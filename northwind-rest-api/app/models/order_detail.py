from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, Numeric, Float
from sqlalchemy import DateTime
from datetime import datetime
from decimal import Decimal
from app.extensions import db


class OrderDetail(db.Model):

    __tablename__ = "order_details"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id"), nullable=False
    )

    product_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("products.id"), nullable=True
    )

    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)

    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(19, 4), nullable=True)

    discount: Mapped[float] = mapped_column(Float, nullable=False)

    date_allocated: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    order: Mapped["Order"] = relationship(back_populates="order_details")

    product: Mapped["Product | None"] = relationship(back_populates="order_details")
