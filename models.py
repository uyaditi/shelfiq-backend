from sqlalchemy import Column, Integer, String, Float, Date
from db import Base

class RetailStock(Base):
    __tablename__ = "retail_stock"

    id               = Column(Integer, primary_key=True, index=True)
    date             = Column(Date)
    store            = Column(String(50))
    product_name     = Column(String(100))
    category         = Column(String(100))
    price            = Column(Float)
    cost             = Column(Float)
    sales_qty        = Column(Integer)
    revenue          = Column(Float)
    roi_percent      = Column(Float)
    remaining_stock  = Column(Integer)
    shelf_section    = Column(String(50))
    visibility_score = Column(Float)
    rating           = Column(Float)
    product_id       = Column(String(20))


class RetailCustomer(Base):
    __tablename__ = "retail_customer"

    id             = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(20))
    date           = Column(Date)
    store          = Column(String(50))
    customer_id    = Column(String(20))
    products       = Column(String)
    categories     = Column(String)
    review_ratings = Column(String)
    total_amount   = Column(Float)
    product_ids    = Column(String)