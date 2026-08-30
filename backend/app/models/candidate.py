from pydantic import BaseModel


class ProductCandidate(BaseModel):
    product_id: str
    product_name: str
    price: float
    rating: float
    margin_percent: float
    available_quantity: int
    fastest_delivery_days: int
    valid: bool