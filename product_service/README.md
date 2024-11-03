# Online Mart - Product Service

**Search Specific Data**

```bash
def search_product_by_name(name: str, session: Session) -> List[Product]:
    products = session.exec(
        select(Product).where(Product.product_name.ilike(f"%{name}%"))
    ).all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found with this name.")
    
    return products

@app.get("/api/search_product_by_name/{product_name}", response_model=List[Product])
def search_product(name: str, session: DB_Session):
    return search_product_by_name(name, session)
```

**Detail of Retrive, Add, Upadate, Delete Data**

[Retrive, Add, Upadate, Delete Data](https://github.com/raheelam98/online_mart_class/tree/main/user_service)