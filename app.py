import os
from typing import List
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, String, select, ForeignKey, func
from sqlalchemy.orm import Session, DeclarativeBase, Mapped, mapped_column, relationship
from faker import Faker

# Using SQLAlchemy 2.0 with Declarative Base and Mapped classes


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[Optional[str]]
    email_address: Mapped[Optional[str]]
    address: Mapped[Optional[str]]
    country_code: Mapped[Optional[str]] = mapped_column(String(2))
    credit_card: Mapped["CreditCard"] = relationship(back_populates="customer")
    orders: Mapped[List["Order"]] = relationship(back_populates="customer")

    def __repr__(self) -> str:
        return (
            f"User(id={self.id!r}, name={self.fullname!r}, fullname={self.fullname!r})"
        )


class CreditCard(Base):
    __tablename__ = "credit_card"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(19))
    customer_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    customer: Mapped["Customer"] = relationship(back_populates="credit_card")

    def __repr__(self) -> str:
        return f"CreditCard(id={self.id!r}, number={self.number!r})"


class Product(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    price: Mapped[int]
    category: Mapped[str] = mapped_column(String(30))
    orders: Mapped[List["Order"]] = relationship(back_populates="product")

    def __repr__(self) -> str:
        return f"Product(id={self.id!r}, name={self.name!r}, price={self.price!r})"


# add this in the demo video
class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    customer: Mapped["Customer"] = relationship(back_populates="orders")
    product: Mapped["Product"] = relationship(back_populates="orders")

    def __repr__(self) -> str:
        return f"Order(id={self.id!r}, customer_id={self.customer_id!r}, product_id={self.product_id!r})"


# load in .env file using python-dotenv
load_dotenv()
DATABASE_URI = "postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}".format(
    dbuser=os.environ["DBUSER"],
    dbpass=os.environ["DBPASS"],
    dbhost=os.environ["DBHOST"],
    dbname=os.environ["DBNAME"],
)
# connect to a postgres database, echo SQL queries
engine = create_engine(DATABASE_URI, echo=True)

# drop any existing tables - add with copilot
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# Create a session - all this with Copilot!
with Session(engine) as session:
    # insert a product
    session.add(Product(name="Widget", price=10, category="Widgets"))
    # insert 10 products, different kinds of toys
    for i in range(10):
        session.add(Product(name=f"Toy {i}", price=10, category="Toys"))

    # insert a customer
    customer = Customer(
        fullname="John Doe",
        address="123 Main St",
        country_code="US",
        email_address="jd@gmail.com",
    )
    session.add(customer)

    # insert 10 customers
    for i in range(10):
        session.add(
            Customer(
                fullname=f"John Doe {i}", address=f"{i} Main St", country_code="US"
            )
        )
    # use faker to insert customers
    # first use Faker with no locale, examine data in SQLTools
    # then use Faker with locales, examine data in SQLTools
    fake = Faker(["en_US", "es_MX", "en_GB", "pt_BR"])
    for _ in range(100):
        customer = Customer(
            fullname=fake.name(),
            address=fake.address(),
            country_code=fake.country_code(),
            email_address=fake.email(),
        )
        session.add(customer)
        # insert a credit card for each customer
        session.add(CreditCard(number=fake.credit_card_number(), customer=customer))
        # insert an order for each customer, for a random product
        # for a random amount between 1 and 5
        for _ in range(fake.random_int(1, 5)):
            product = session.execute(
                select(Product).order_by(func.random()).limit(1)
            ).scalar_one()
            session.add(Order(customer=customer, product=product))

    session.commit()

    # now do some queries
    # select all customers
    query = select(Customer)
    customers = session.execute(query).scalars().all()
    print(customers)
    # select customers from the US
    query = select(Customer).where(Customer.country_code == "US")
    customers = session.scalars(query).all()
    customers = session.execute(query).scalars().all()
    print(customers)
    # select a list of countries grouped by country code
    query = select(Customer.country_code, func.count(Customer.id)).group_by(
        Customer.country_code
    )
    countries = session.execute(query).all()
    print(countries)
    # select customers joint with their credit cards
    # select customer name, address, and first credit card number
    query = select(Customer.fullname, Customer.address, CreditCard.number).join(
        Customer.credit_card
    )
    result = session.execute(query).first()
    print(result)
    # select customers joint with their orders
    # select customer name, address, and number of orders placed
    query = (
        select(Customer.id, func.count(Order.id))
        .join(Customer.orders)
        .group_by(Customer.id)
        .order_by(func.count(Order.id).desc())
    )
    result = session.execute(query).all()
    print(result)
    # find all customers with 5 orders placed in the US
