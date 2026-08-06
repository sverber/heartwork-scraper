"""
Radius HDD Custom Sub Builder scraper.

Navigates directly to the sub-builder iframe app, iterates all valid
End 1 × End 2 combinations, and writes a CSV.

Target: https://apps2.radiushdd.com/SubBuilder/Selector.aspx

Architecture:
- Discover End 1 brands once from a single page.
- Fan out: one worker thread per (End1 brand × gender) combination.
  Each thread owns its own Playwright instance (Playwright is not thread-safe).
- Results are collected into a shared list guarded by a Lock.
- A checkpoint CSV is written every 50 rows.
"""
import csv
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from playwright.sync_api import sync_playwright, Page

IFRAME_URL = "https://apps2.radiushdd.com/SubBuilder/Selector.aspx"

SEL_BRAND1 = "#ctl00_cphMain_drpBrandID1"
SEL_GENDER1 = "#ctl00_cphMain_drpGender1"
SEL_ITEM1 = "#ctl00_cphMain_drpEnd1"
SEL_BRAND2 = "#ctl00_cphMain_drpBrandID2"
SEL_GENDER2 = "#ctl00_cphMain_drpGender2"
SEL_ITEM2 = "#ctl00_cphMain_drpEnd2"

_SKIP_VALUES = {"0", ""}

CSV_COLUMNS = [
    "end1_brand",
    "end1_gender",
    "end1_item",
    "end2_brand",
    "end2_gender",
    "end2_item",
    "overall_length_inches",
    "shoulder_to_shoulder_inches",
    "material_diameter",
    "hardness",
    "price_ship_same_day",
    "price_ship_next_day",
    "price_standard_2_4_weeks",
]

# Max parallel workers — one per End1 brand+gender combo (at most 12).
# Keep at ≤6 to avoid hammering the server.
MAX_WORKERS = 6


def _get_options(page: Page, selector: str) -> list[tuple[str, str]]:
    """Return [(value, label)] for all real (non-placeholder, non-separator) options."""
    raw = page.evaluate(f"""
        () => {{
            const sel = document.querySelector('{selector}');
            if (!sel) return [];
            return Array.from(sel.options).map(o => [o.value, o.text.trim()]);
        }}
    """)
    return [
        (val, text) for val, text in raw
        if val not in _SKIP_VALUES
        and not val.startswith("─")
        and not text.startswith("─")
    ]


def _select_and_wait(page: Page, selector: str, value: str):
    """
    Select a value and wait for the ASP.NET postback response.
    expect_response is more reliable than wait_for_load_state because
    WebForms postbacks don't trigger a navigation event.
    """
    try:
        with page.expect_response(
            lambda r: "Selector.aspx" in r.url and r.request.method == "POST",
            timeout=15000,
        ):
            page.select_option(selector, value)
        page.wait_for_timeout(300)
    except Exception:
        # Fallback if no postback fires (e.g. value already selected, or timeout)
        page.wait_for_timeout(2000)


def _read_attrs(page: Page) -> dict:
    """Extract specs and prices from the result section."""
    return page.evaluate("""
        () => {
            const byId = id => { const el = document.getElementById(id); return el ? el.innerText.trim() : ''; };

            let hardness = '';
            for (const el of document.querySelectorAll('span, td')) {
                if (el.innerText.includes('Rockwell')) { hardness = el.innerText.trim(); break; }
            }

            const ship = document.getElementById('ctl00_cphMain_drpShipping');
            let priceSameDay = '', priceNextDay = '', priceStd = '';
            if (ship) {
                for (const opt of ship.options) {
                    if (opt.text.includes('same day'))        priceSameDay = opt.value;
                    else if (opt.text.includes('next day'))   priceNextDay = opt.value;
                    else if (opt.text.includes('Standard') || opt.text.includes('2-4')) priceStd = opt.value;
                }
            }

            // Material diameter lives in lblMaterialDiameter1 when End1 supplies it,
            // and in lblMaterialDiameter2 when End2 supplies it — never both at once.
            const d1el = document.getElementById('ctl00_cphMain_lblMaterialDiameter1');
            const d2el = document.getElementById('ctl00_cphMain_lblMaterialDiameter2');
            const materialDiam = (d1el ? d1el.innerText.trim() : '') || (d2el ? d2el.innerText.trim() : '');

            return {
                overall_length:       byId('ctl00_cphMain_lblOverallLength2'),
                shoulder_to_shoulder: byId('ctl00_cphMain_lblShoulderToShoulder'),
                material_diameter:    materialDiam,
                hardness,
                price_same_day:  priceSameDay,
                price_next_day:  priceNextDay,
                price_standard:  priceStd,
            };
        }
    """)


def _open_page(headless: bool = True) -> tuple:
    """Start a fresh Playwright instance + page at the sub-builder URL. Returns (playwright, browser, page)."""
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=headless)
    page = browser.new_page()
    page.goto(IFRAME_URL, wait_until="networkidle")
    page.wait_for_timeout(2000)
    return pw, browser, page


def _scrape_combo(
    b1_val: str,
    b1_text: str,
    g1_text: str,
    counter: list,
    lock: threading.Lock,
    headless: bool = True,
) -> list[dict]:
    """
    Worker: scrape all End2 combinations for a given End1 (brand, gender).
    Returns the list of row dicts for this combo.
    """
    combo_rows: list[dict] = []
    label = f"{b1_text}/{g1_text}"

    pw, browser, page = _open_page(headless=headless)
    try:
        _select_and_wait(page, SEL_BRAND1, b1_val)
        _select_and_wait(page, SEL_GENDER1, g1_text)

        end1_items = _get_options(page, SEL_ITEM1)
        if not end1_items:
            print(f"  [{label}] no items, skipping.")
            return combo_rows

        print(f"  [{label}] {len(end1_items)} End1 items")

        for i1_val, i1_text in end1_items:
            _select_and_wait(page, SEL_ITEM1, i1_val)

            end2_brands = _get_options(page, SEL_BRAND2)

            for b2_val, b2_text in end2_brands:
                _select_and_wait(page, SEL_BRAND2, b2_val)

                end2_genders = _get_options(page, SEL_GENDER2)

                for g2_val, g2_text in end2_genders:
                    _select_and_wait(page, SEL_GENDER2, g2_val)

                    end2_items = _get_options(page, SEL_ITEM2)

                    for i2_val, i2_text in end2_items:
                        _select_and_wait(page, SEL_ITEM2, i2_val)

                        attrs = _read_attrs(page)
                        row = {
                            "end1_brand":                  b1_text,
                            "end1_gender":                 g1_text,
                            "end1_item":                   i1_text,
                            "end2_brand":                  b2_text,
                            "end2_gender":                 g2_text,
                            "end2_item":                   i2_text,
                            "overall_length_inches":       attrs["overall_length"],
                            "shoulder_to_shoulder_inches": attrs["shoulder_to_shoulder"],
                            "material_diameter":           attrs["material_diameter"],
                            "hardness":                    attrs["hardness"],
                            "price_ship_same_day":         attrs["price_same_day"],
                            "price_ship_next_day":         attrs["price_next_day"],
                            "price_standard_2_4_weeks":    attrs["price_standard"],
                        }
                        combo_rows.append(row)

                        with lock:
                            counter[0] += 1
                            n = counter[0]
                        print(
                            f"    [{label}][{n:>5}] {i1_text!r} × {i2_text!r}"
                            f" | len={attrs['overall_length']}"
                            f" | s2s={attrs['shoulder_to_shoulder']}"
                        )

    except Exception as e:
        print(f"  [{label}] ERROR: {e}")
    finally:
        browser.close()
        pw.stop()

    return combo_rows


def scrape(output_path: Path, headless: bool = True, max_workers: int = MAX_WORKERS):
    """
    Scrape all End1 × End2 combinations from the Radius HDD sub builder.

    Parallelises by End1 brand+gender combo. Writes checkpoint CSV every 50 new rows.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Discover brands from a one-off page
    pw, browser, page = _open_page(headless=headless)
    end1_brands = _get_options(page, SEL_BRAND1)
    browser.close()
    pw.stop()
    print(f"End 1 brands ({len(end1_brands)}): {[t for _, t in end1_brands]}")

    # Build work items: all (brand, gender) combos for End 1
    combos = [
        (val, text, gender)
        for val, text in end1_brands
        for gender in ("Box", "Pin")
    ]
    print(f"Launching {len(combos)} combos across {max_workers} workers ...\n")

    all_rows: list[dict] = []
    counter = [0]
    lock = threading.Lock()
    last_checkpoint = [0]

    def checkpoint_if_needed():
        with lock:
            n = counter[0]
            if n - last_checkpoint[0] >= 50:
                last_checkpoint[0] = n
                _write_csv(output_path, list(all_rows))
                print(f"  [checkpoint] {n} rows written to {output_path}")

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_scrape_combo, val, text, gender, counter, lock, headless): (text, gender)
            for val, text, gender in combos
        }
        for future in as_completed(futures):
            label = futures[future]
            try:
                combo_rows = future.result()
                with lock:
                    all_rows.extend(combo_rows)
                print(f"  Combo {label} done: {len(combo_rows)} rows")
                checkpoint_if_needed()
            except Exception as e:
                print(f"  Combo {label} FAILED: {e}")

    _write_csv(output_path, all_rows)
    print(f"\nFinished. {len(all_rows)} rows → {output_path}")
    return all_rows


def _write_csv(path: Path, rows: list[dict]):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
