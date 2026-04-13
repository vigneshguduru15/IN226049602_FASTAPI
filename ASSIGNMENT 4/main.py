from fastapi import FastAPI
from fastapi import HTTPException

app = FastAPI()


products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True}
]

cart = []
orders = []
order_id_counter = 1

def find_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


@app.get("/products")
def get_products():
    return {
        "total": len(products),
        "products": products
    }

@app.get("/products/audit")
def product_audit():
    in_stock_list = [p for p in products if p["in_stock"]]
    out_stock_list = [p for p in products if not p["in_stock"]]

    total_value = sum(p["price"] * 10 for p in in_stock_list)

    most_expensive = max(products, key=lambda x: x["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock_list),
        "out_of_stock_names": [p["name"] for p in out_stock_list],
        "total_stock_value": total_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }

@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):
    updated = []

    for product in products:
        if product["category"].lower() == category.lower():
            new_price = int(product["price"] * (1 - discount_percent / 100))
            product["price"] = new_price
            updated.append(product)

    if not updated:
        return {"message": "No products found in this category"}

    return {
        "updated_count": len(updated),
        "products": updated
    }



@app.post("/products")
def add_product(product: dict):
    for p in products:
        if p["name"].lower() == product["name"].lower():
            return {"error": "Product already exists"}

    product["id"] = len(products) + 1
    products.append(product)

    return {
        "message": "Product added",
        "product": product
    }

@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/products/{product_id}")
def update_product(product_id: int, price: int = None, in_stock: bool = None):
    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if price is not None:
        product["price"] = price

    if in_stock is not None:
        product["in_stock"] = in_stock

    return product

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    products.remove(product)

    return {"message": f"Product '{product['name']}' deleted"}

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):
    product = find_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")
    

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * item["unit_price"]
            return {
                "message": "Cart updated",
                "cart_item": item
            }

    new_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": product["price"] * quantity
    }

    cart.append(new_item)

    return {
        "message": "Added to cart",
        "cart_item": new_item
    }
    
@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }
    
@app.delete("/cart/{product_id}")
def remove_from_cart(product_id: int):
    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "Item removed from cart"}

    raise HTTPException(status_code=404, detail="Item not found in cart")

@app.post("/cart/checkout")
def checkout(customer_name: str, address: str):
    global order_id_counter

    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    grand_total = sum(item["subtotal"] for item in cart)

    new_orders = []
    for item in cart:
        order = {
            "order_id": order_id_counter,
            "customer_name": customer_name,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total": item["subtotal"]
        }
        orders.append(order)
        new_orders.append(order)
        order_id_counter += 1

    cart.clear()

    return {
        "message": "Order placed",
        "orders_placed": new_orders,
        "grand_total": grand_total
    }
    
@app.get("/orders")
def get_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }