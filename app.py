from typing import List
from typing import Optional

from faker import Faker
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str]
    email: Mapped[Optional[str]]
    address: Mapped[Optional[str]]
    country_code: Mapped[Optional[str]] = mapped_column(String(2))
    credit_card: Mapped["CreditCard"] = relationship(
        "CreditCard", back_populates="customer"
    )
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="customer")

    def __repr__(self) -> str:
        return f"<Customer {self.id} {self.fullname}>"


class CreditCard(Base):
    __tablename__ = "credit_card"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(19))
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    customer: Mapped[Customer] = relationship(Customer, back_populates="credit_card")

    def __repr__(self) -> str:
        return f"<CreditCard {self.id} {self.number}>"


class Product(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    price: Mapped[float]
    description: Mapped[Optional[str]]
    category: Mapped[str] = mapped_column(String(30))
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="product")

    def __repr__(self) -> str:
        return f"<Product {self.id} {self.name}>"


class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    customer: Mapped[Customer] = relationship(Customer, back_populates="orders")
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    product: Mapped[Product] = relationship(Product, back_populates="orders")
    quantity: Mapped[Optional[int]]

    def __repr__(self) -> str:
        return f"<Order {self.id} {self.customer_id} {self.product_id}>"


# Connect to SQLite db
DATABASE_URI = "sqlite:///db.sqlite3"

engine = create_engine(DATABASE_URI, echo=True)

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

with Session(engine) as session:
    # insert 10 products
    for i in range(10):
        product = Product(
            name=f"Product {i}",
            price=9.99,
            description=f"Description {i}",
            category="category",
        )
        session.add(product)
    session.commit()

    # insert 10 customers
    fake = Faker(["en_US", "es_ES", "pt_BR", "en_GB"])
    for i in range(100):
        customer = Customer(
            fullname=fake.name(),
            email=fake.email(),
            address=fake.address(),
            country_code=fake.country_code(),
        )
        session.add(customer)
        # insert a credit card for each customer
        credit_card = CreditCard(number=fake.credit_card_number(), customer=customer)
        session.add(credit_card)
        # insert an order of a random product using their credit card
        # insert a random number of orders for each customer
        for _ in range(fake.random_int(1, 5)):
            order = Order(
                customer=customer,
                product=session.query(Product).order_by(Product.id.desc()).first(),
                quantity=1,
            )
            session.add(order)

    session.commit()

    # query all customers
    query = select(Customer)
    customers = session.execute(query).scalars().all()
    print(customers)
    # select customers from the US
    query = select(Customer).where(Customer.country_code == "US")
    customers = session.execute(query).scalars().all()
    print(customers)
    # select a list of countries grouped by country code
    query = select(Customer.country_code).group_by(Customer.country_code)
    countries = session.execute(query).scalars().all()
    print(countries)
    # select customer name, address, and credit card number
    query = select(Customer.fullname, Customer.address, CreditCard.number).join(
        Customer.credit_card
    )
    customers = session.execute(query).all()
    print(customers)
    # sellect customer id with number of orders per customer
    query = (
        select(Customer.id, func.count(Order.id))
        .join(Customer.orders)
        .group_by(Customer.id)
        .order_by(func.count(Order.id).desc())
    )
    result = session.execute(query).all()
    print(result)
