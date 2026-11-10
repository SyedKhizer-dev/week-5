from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductCreate(BaseModel):

    product_code: str | None = Field(default=None, max_length=25)

    product_name: str | None = Field(default=None, max_length=50)

    description: str | None = None

    standard_cost: Decimal | None = Field(default=None, ge=0)

    list_price: Decimal = Field(ge=0)

    reorder_level: int | None = None

    target_level: int | None = None

    quantity_per_unit: str | None = Field(default=None, max_length=50)

    discontinued: bool = False

    category: str | None = Field(default=None, max_length=50)


class ProductUpdate(BaseModel):

    product_code: str | None = Field(default=None, max_length=25)

    product_name: str | None = Field(default=None, max_length=50)

    description: str | None = None

    standard_cost: Decimal | None = Field(default=None, ge=0)

    list_price: Decimal | None = Field(default=None, ge=0)

    reorder_level: int | None = None

    target_level: int | None = None

    quantity_per_unit: str | None = Field(default=None, max_length=50)

    discontinued: bool | None = None

    category: str | None = Field(default=None, max_length=50)

    @field_validator("list_price")
    @classmethod
    def validate_list_price(cls, value):
        if value is None:
            raise ValueError("List price cannot be null")

        return value


class ProductResponse(BaseModel):

    id: int

    product_code: str | None

    product_name: str | None

    description: str | None

    standard_cost: Decimal | None

    list_price: Decimal

    reorder_level: int | None

    target_level: int | None

    quantity_per_unit: str | None

    discontinued: bool

    category: str | None

    model_config = ConfigDict(from_attributes=True)
