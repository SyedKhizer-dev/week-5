from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Numeric, ForeignKey
from sqlalchemy import text
from datetime import datetime
from decimal import Decimal
from app.extensions import db


class Order(db.Model):

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    customer_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("customers.id"), nullable=True
    )

    order_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    shipped_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    ship_name: Mapped[str | None] = mapped_column(String(50), nullable=True)

    shipping_fee: Mapped[Decimal | None] = mapped_column(Numeric(19, 4), nullable=True)

    taxes: Mapped[Decimal | None] = mapped_column(Numeric(19, 4), nullable=True)

    payment_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    status_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    customer: Mapped["Customer | None"] = relationship(back_populates="orders")

    order_details: Mapped[list["OrderDetail"]] = relationship(back_populates="order")
