from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from app.extensions import db


class Customer(db.Model):

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    company: Mapped[str | None] = mapped_column(String(50), nullable=True)

    first_name: Mapped[str | None] = mapped_column(String(50), nullable=True)

    last_name: Mapped[str | None] = mapped_column(String(50), nullable=True)

    email_address: Mapped[str | None] = mapped_column(String(50), nullable=True)

    job_title: Mapped[str | None] = mapped_column(String(50), nullable=True)

    business_phone: Mapped[str | None] = mapped_column(String(25), nullable=True)

    city: Mapped[str | None] = mapped_column(String(50), nullable=True)

    country_region: Mapped[str | None] = mapped_column(String(50), nullable=True)

    orders: Mapped[list["Order"]] = relationship(back_populates="customer")
