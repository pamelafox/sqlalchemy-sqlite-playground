from typing import List

from faker import Faker
from sqlalchemy import ForeignKey, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class Customer(Base):
    __tablename__ = "customer"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email_address: Mapped[str]
    address: Mapped[str]
    country_code: Mapped[str] = mapped_column(String(2))
    # add a 1-to-1 relationship to CreditCard
    credit_card: Mapped["CreditCard"] = relationship("CreditCard", uselist=False,
                                                     back_populates="customer")
    # add a 1-to-many relationship to Order
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="customer")
    def __repr__(self):
        return f"<Customer(name={self.name!r})>"
    
class CreditCard(Base):
    __tablename__ = "credit_card"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    customer: Mapped[Customer] = relationship("Customer", back_populates="credit_card")
    number: Mapped[str] = mapped_column(String(19))

    def __repr__(self):
        return f"<CreditCard(number={self.number!r})>"
    
# Add a Product with name, price, description, and category
class Product(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float]
    description: Mapped[str]
    category: Mapped[str] = mapped_column(String(100))
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="product")

    def __repr__(self):
        return f"<Product(name={self.name!r})>"
    
# Add an Order with a customer_id, product_id, and quantity
class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.id"))
    customer: Mapped[Customer] = relationship("Customer", back_populates="orders")
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"))
    product: Mapped[Product] = relationship("Product", back_populates="orders")
    quantity: Mapped[int]

    def __repr__(self):
        return f"<Order(quantity={self.quantity!r})>"

# Set up a database connection and create tables
engine = create_engine("sqlite:///my_database.db", echo=True)
Base.metadata.create_all(engine)

fake = Faker(["en_US", "en_GB", "en_CA", "es_MX", "de_DE", "fr_FR", "ja_JP"])

with Session(engine) as session:
    # insert 10 products
    for i in range(10):
        product = Product(name=f"Product {i}", price=9.99, description="ABC", category="XYZ")
        session.add(product)
    # create 100 customers
    for i in range(100):
        customer = Customer(name=fake.name(), email_address=fake.email(),
                            address=fake.address(), country_code=fake.country_code())
        session.add(customer)
        # create a credit card for each customer
        credit_card = CreditCard(number=fake.credit_card_number(), customer=customer)
        session.add(credit_card)
        # insert random amount of orders of random product IDs using their credit card
        for _ in range(fake.random_int(min=1, max=5)):
            order = Order(customer=customer, product_id=fake.random_int(min=1, max=10),
                        quantity=fake.random_int(min=1, max=5))
            session.add(order)
    # commit the session to the database
    session.commit()

    # Query the database
    # Get all customers
    query = select(Customer)
    results = session.execute(query).scalars().all()
    print(results)

    # Get all customers from the US
    query = select(Customer).where(Customer.country_code == "US")
    results = session.execute(query).scalars().all()
    print(results)

    # Select a list of countries grouped by country code
    from sqlalchemy import func
    query = select(Customer.country_code, func.count(Customer.country_code)).group_by(Customer.country_code)
    results = session.execute(query).all()
    print(results)

    # Select customer name with credit card number
    query = select(Customer.name, CreditCard.number).join(CreditCard)
    results = session.execute(query).all()
    print(results)

    # Select customer name with their number of orders
    query = select(Customer.id, func.count(Order.id)).join(Order).group_by(Customer.id)
    results = session.execute(query).all()
    print(results)