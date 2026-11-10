from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, Numeric
from app.extensions import db
from decimal import Decimal


class Product(db.Model):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    product_code: Mapped[str | None] = mapped_column(String(25), nullable=True)

    product_name: Mapped[str | None] = mapped_column(String(50), nullable=True)

    description: Mapped[str | None] = mapped_column(String, nullable=True)

    standard_cost: Mapped[Decimal | None] = mapped_column(Numeric(19, 4), nullable=True)

    list_price: Mapped[Decimal] = mapped_column(Numeric(19, 4), nullable=False)

    reorder_level: Mapped[int | None] = mapped_column(Integer, nullable=True)

    target_level: Mapped[int | None] = mapped_column(Integer, nullable=True)

    quantity_per_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)

    discontinued: Mapped[bool] = mapped_column(Boolean, nullable=False)

    category: Mapped[str | None] = mapped_column(String(50), nullable=True)

    order_details: Mapped[list["OrderDetail"]] = relationship(back_populates="product")
