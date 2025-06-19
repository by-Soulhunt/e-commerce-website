from flask import (Flask, render_template, session, redirect, url_for, request, jsonify,
                   flash)
import os
import json
import stripe

# Stripe configuration
stripe.api_key = os.getenv("SECRET_KEY")
STRIPE_PUBLISH_KEY = os.getenv("PUBLISH_KEY")

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
    """
    Main page. Show products. Processing products in cart.
    :return:
    """
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
                           total=round(total, 2), total_products_in_cart=len(products),
                           stripe_publishable_key=STRIPE_PUBLISH_KEY)


@app.route("/add_to_card/<int:product_id>", methods=["GET", "POST"])
def add_to_card(product_id):
    """
    Add products to cart
    :param product_id:
    :return: redirect index
    """
    quantity = int(request.form.get("quantity"))
    cart = session.get('cart', {})
    product_id = str(product_id)
    cart[product_id] = cart.get(product_id, 0) + quantity
    session['cart'] = cart

    return redirect(url_for('index'))


@app.route("/delete-item-from-cart", methods=["GET", "POST"])
def delete_item_from_cart():
    item_to_delete = request.form.get("cart_product_id")
    cart = session.get('cart', {})
    if item_to_delete in cart:
        del cart[item_to_delete]
        session["cart"] = cart

    return redirect(url_for('index'))


@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    cart = session.get('cart', {})
    if not cart:
        return jsonify({"error": "Cart is empty"}), 400

    line_items = []
    for product_id, quantity in cart.items():
        product = next((p for p in products if str(p['id']) == product_id), None)
        if product:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product['name'],
                    },
                    'unit_amount': int(product['price'] * 100),
                },
                'quantity': quantity,
            })

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('cancel', _external=True),
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 500


@app.route('/success')
def success():
    session.pop('cart', None)
    flash("Payment was successful! Thank you for your purchase.", "success")
    return redirect(url_for('index'))

@app.route('/cancel')
def cancel():
    flash("The payment was canceled or failed.", "danger")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True, port=5005)