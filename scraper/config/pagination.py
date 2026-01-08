from pydantic import BaseModel


class PaginationConfig(BaseModel):
    selector: str
