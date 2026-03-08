from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from db import get_db
from models.models import RetailStock, RetailCustomer
from schemas.schemas import (
    StockCreate, StockUpdate, StockResponse,
    CustomerCreate, CustomerUpdate, CustomerResponse
)

router = APIRouter(prefix="/data", tags=["Data"])


@router.get("/stock", response_model=List[StockResponse])
def get_all_stock(
    skip: int = 0,
    limit: int = 100,
    store: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    shelf_section: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all stock records with optional filters"""
    query = db.query(RetailStock)
    if store:
        query = query.filter(RetailStock.store == store)
    if category:
        query = query.filter(RetailStock.category == category)
    if shelf_section:
        query = query.filter(RetailStock.shelf_section == shelf_section)
    return query.offset(skip).limit(limit).all()


@router.get("/stock/{id}", response_model=StockResponse)
def get_stock_by_id(id: int, db: Session = Depends(get_db)):
    """Get a single stock record by ID"""
    record = db.query(RetailStock).filter(RetailStock.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Stock record not found")
    return record


@router.post("/stock", response_model=StockResponse)
def create_stock(payload: StockCreate, db: Session = Depends(get_db)):
    """Create a new stock record"""
    record = RetailStock(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/stock/{id}", response_model=StockResponse)
def update_stock(id: int, payload: StockUpdate, db: Session = Depends(get_db)):
    """Update an existing stock record"""
    record = db.query(RetailStock).filter(RetailStock.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Stock record not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/stock/{id}")
def delete_stock(id: int, db: Session = Depends(get_db)):
    """Delete a stock record"""
    record = db.query(RetailStock).filter(RetailStock.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Stock record not found")
    db.delete(record)
    db.commit()
    return {"message": f"Stock record {id} deleted successfully"}



@router.get("/customer", response_model=List[CustomerResponse])
def get_all_customers(
    skip: int = 0,
    limit: int = 100,
    store: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all customer records with optional filters"""
    query = db.query(RetailCustomer)
    if store:
        query = query.filter(RetailCustomer.store == store)
    if customer_id:
        query = query.filter(RetailCustomer.customer_id == customer_id)
    return query.offset(skip).limit(limit).all()


@router.get("/customer/{id}", response_model=CustomerResponse)
def get_customer_by_id(id: int, db: Session = Depends(get_db)):
    """Get a single customer record by ID"""
    record = db.query(RetailCustomer).filter(RetailCustomer.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Customer record not found")
    return record


@router.post("/customer", response_model=CustomerResponse)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer record"""
    record = RetailCustomer(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.put("/customer/{id}", response_model=CustomerResponse)
def update_customer(id: int, payload: CustomerUpdate, db: Session = Depends(get_db)):
    """Update an existing customer record"""
    record = db.query(RetailCustomer).filter(RetailCustomer.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Customer record not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/customer/{id}")
def delete_customer(id: int, db: Session = Depends(get_db)):
    """Delete a customer record"""
    record = db.query(RetailCustomer).filter(RetailCustomer.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Customer record not found")
    db.delete(record)
    db.commit()
    return {"message": f"Customer record {id} deleted successfully"}