from flask import Flask, render_template, session, redirect, url_for, request
import os
import json


# Flask configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")


# Read products from file
try:
    with open("products/products.json", "r", encoding="utf-8") as file:
        products = json.load(file)
        # Convert to int for processing
        for p in products:
            p["id"] = int(p["id"])
except Exception as e:
    print(f"Error {e}")


# Routs
@app.route('/')
def index():
    cart = session.get('cart', {})
    cart_items = [] # For cart
    total = 0 # Total cart sum

    for pid, qty in cart.items():
        # search first product by generator + next
        product = next((p for p in products if p['id'] == int(pid)), None)
        if product:
            subtotal = product['price'] * qty
            total += subtotal
            cart_items.append({
                **product,
                'quantity': qty,
                'subtotal': round(subtotal, 2)
            })

    return render_template('index.html', products=products, cart_items=cart_items,
                           total=round(total, 2), total_products_in_cart=len(products))



@app.route("/add_to_card/<int:product_id>", methods=["GET", "POST"])
def add_to_card(product_id):
    quantity = int(request.form.get("quantity"))
    cart = session.get('cart', {})
    product_id = str(product_id)
    cart[product_id] = cart.get(product_id, 0) + quantity
    session['cart'] = cart

    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, port=5005)