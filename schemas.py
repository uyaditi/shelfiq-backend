from pydantic import BaseModel
from typing import Optional
from datetime import date



class StockBase(BaseModel):
    date:             Optional[date]   = None
    store:            Optional[str]    = None
    product_name:     Optional[str]    = None
    category:         Optional[str]    = None
    price:            Optional[float]  = None
    cost:             Optional[float]  = None
    sales_qty:        Optional[int]    = None
    revenue:          Optional[float]  = None
    roi_percent:      Optional[float]  = None
    remaining_stock:  Optional[int]    = None
    shelf_section:    Optional[str]    = None
    visibility_score: Optional[float]  = None
    rating:           Optional[float]  = None
    product_id:       Optional[str]    = None

class StockCreate(StockBase):
    pass

class StockUpdate(StockBase):
    pass

class StockResponse(StockBase):
    id: int
    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    transaction_id: Optional[str]   = None
    date:           Optional[date]  = None
    store:          Optional[str]   = None
    customer_id:    Optional[str]   = None
    products:       Optional[str]   = None
    categories:     Optional[str]   = None
    review_ratings: Optional[str]   = None
    total_amount:   Optional[float] = None
    product_ids:    Optional[str]   = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    id: int
    class Config:
        from_attributes = True