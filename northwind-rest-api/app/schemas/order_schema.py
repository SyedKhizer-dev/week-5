from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):

    customer_id: int | None = None

    order_date: datetime | None = None

    shipped_date: datetime | None = None

    ship_name: str | None = Field(default=None, max_length=50)

    shipping_fee: Decimal | None = Field(default=None, ge=0)

    taxes: Decimal | None = Field(default=None, ge=0)

    payment_type: str | None = Field(default=None, max_length=50)

    status_id: int | None = None


class OrderUpdate(BaseModel):

    customer_id: int | None = None

    order_date: datetime | None = None

    shipped_date: datetime | None = None

    ship_name: str | None = Field(default=None, max_length=50)

    shipping_fee: Decimal | None = Field(default=None, ge=0)

    taxes: Decimal | None = Field(default=None, ge=0)

    payment_type: str | None = Field(default=None, max_length=50)

    status_id: int | None = None


class OrderDetailResponse(BaseModel):

    id: int

    order_id: int

    product_id: int | None

    quantity: Decimal

    unit_price: Decimal | None

    discount: float

    date_allocated: datetime | None

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):

    id: int

    customer_id: int | None

    order_date: datetime | None

    shipped_date: datetime | None

    ship_name: str | None

    shipping_fee: Decimal | None

    taxes: Decimal | None

    payment_type: str | None

    status_id: int | None

    order_details: list[OrderDetailResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
