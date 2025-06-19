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
except Exception as e:
    print(f"Error {e}")


# Routs
@app.route("/")
def index():
    return render_template("index.html", products=products)

if __name__ == "__main__":
    app.run(debug=True, port=5005)