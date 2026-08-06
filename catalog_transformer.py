import json
from pathlib import Path
from typing import List

from scraper.models.import_product import ImportProduct, ImportProductAttribute
from scraper.models.models import Category, Product


class CatalogTransformer:
    def __init__(self, root_category: Category):
        self.root = root_category
        # Initialize the list to store results
        self.import_products: List[ImportProduct] = []

    def transform(self) -> List[ImportProduct]:
        self.import_products = []
        # Start recursion
        self._traverse(self.root, [])
        return self.import_products

    def _traverse(self, current_category: Category, parents: List[Category]):
        # 1. Update parents list, skipping "Root" so Level 1 is the first real category
        new_parents = parents + [current_category] if current_category.name != "Root" else parents

        # 2. Logging
        depth = len(new_parents)
        parent_names = " > ".join([p.name for p in new_parents]) if new_parents else "None"
        indent = "  " * depth
        print(f"{indent}Category: {current_category.name} (Depth: {depth}, Path: {parent_names})")

        # 3. Map products at this level
        for product in current_category.products:
            print(f"{indent}  - Product: {product.name}")
            # Pass the accumulated new_parents to the mapper
            import_model = self._map_to_import(product, new_parents)
            self.import_products.append(import_model)

        # 4. Recurse into subcategories
        for subcat in current_category.subcategories:
            self._traverse(subcat, new_parents)

    @staticmethod
    def _map_to_import(product: Product, parents: List[Category]) -> ImportProduct:
        """Mapping method to populate the target class based on category depth."""
        # Safely extract up to 3 levels from the parents list
        l1 = parents[0] if len(parents) > 0 else None
        l2 = parents[1] if len(parents) > 1 else None
        l3 = parents[2] if len(parents) > 2 else None

        mapped_attributes = []

        for attr in product.attributes:
            mapped_attributes.append(
                ImportProductAttribute(
                    name=attr.name,
                    value=", ".join(attr.values) if attr.values else ""
                )
            )

        return ImportProduct(
            # Using the end of the URL or the name as a fallback SKU
            sku=str(product.url).rstrip('/').split('/')[-1] if product.url else product.name.replace(" ", "-"),
            product_name=product.name,

            # Category Hierarchy Mapping
            level1_id=str(l1.url) if l1 else None,
            level1_name=l1.name if l1 else None,

            level2_id=str(l2.url) if l2 else None,
            level2_name=l2.name if l2 else None,

            level3_id=str(l3.url) if l3 else None,
            level3_name=l3.name if l3 else None,

            attributes=mapped_attributes
        )


if __name__ == "__main__":
    # 1. Simplified Path Setup
    input_path = Path("output/de-ijssel-coatings.json")
    # input_path = Path("output/epifanes_binnenvaart.json")
    # input_path = Path("output/epifanes_pleziervaart.json")
    # input_path = Path("output/international-pc.json")
    # input_path = Path("output/yachtpaint.json")

    # Just take the name (de-ijssel-coatings) and add _catalog.json
    output_path = input_path.with_name(f"{input_path.stem}_catalog.json")

    if not input_path.exists():
        print(f"Error: {input_path} not found.")
    else:
        print(f"Processing: {input_path.name} -> {output_path.name}")

        with open(input_path, "r") as f:
            data = json.load(f)
            root = Category.model_validate(data)

        transformer = CatalogTransformer(root)
        final_products = transformer.transform()

        print(f"\nSuccessfully mapped {len(final_products)} products.")

        # 2. Save result
        with open(output_path, "w") as f:
            json.dump(
                [p.model_dump(by_alias=True, mode='json') for p in final_products],
                f,
                indent=2
            )
        print(f"Catalog file generated at: {output_path}")
