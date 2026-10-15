from flask import Flask, jsonify

app = Flask(__name__)

products = [
    {"id": 1, "name": "Laptop", "price": 45000, "emoji": "💻", "category": "Computers",
     "description": "14-inch, 16 GB RAM, all-day battery."},
    {"id": 2, "name": "Headphones", "price": 1500, "emoji": "🎧", "category": "Audio",
     "description": "Over-ear, deep bass, 30-hour playtime."},
    {"id": 3, "name": "Smart Watch", "price": 2500, "emoji": "⌚", "category": "Wearables",
     "description": "Heart-rate, sleep and step tracking."},
    {"id": 4, "name": "Keyboard", "price": 900, "emoji": "⌨️", "category": "Accessories",
     "description": "Compact mechanical keyboard, quiet switches."},
]


@app.route("/")
def home():
    return "<h1>E-commerce Product Service</h1><p>Product Service is running!</p>"


@app.route("/products")
def get_products():
    return jsonify(products)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
