from decimal import Decimal
from pydantic import BaseModel, Field

class SaleLine(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)

class SaleCreate(BaseModel):
    customer_name: str | None = Field(default=None, max_length=160)
    payment_method: str = Field(default="Efectivo", max_length=30)
    discount: Decimal = Field(default=Decimal("0"), ge=0)
    items: list[SaleLine] = Field(min_length=1)
