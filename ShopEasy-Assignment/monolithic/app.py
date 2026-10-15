from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

# Product data
products = [
    {"id": 1, "name": "Laptop", "price": 45000, "emoji": "💻"},
    {"id": 2, "name": "Headphones", "price": 1500, "emoji": "🎧"},
    {"id": 3, "name": "Smart Watch", "price": 2500, "emoji": "⌚"},
    {"id": 4, "name": "Keyboard", "price": 900, "emoji": "⌨️"}
]

# Orders are managed by the same application
orders = []
next_order_id = 1

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>ShopEasy - Monolithic E-commerce</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            background: #f4f6f9;
            color: #222;
        }
        header {
            background: #173b57;
            color: white;
            padding: 22px;
            text-align: center;
        }
        main {
            max-width: 950px;
            margin: 30px auto;
            padding: 15px;
        }
        .products {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 18px;
        }
        .card {
            background: white;
            padding: 22px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 3px 12px #0001;
        }
        .emoji { font-size: 48px; }
        .price { font-size: 20px; font-weight: bold; }
        button {
            background: #176b50;
            color: white;
            border: 0;
            padding: 11px 16px;
            border-radius: 6px;
            cursor: pointer;
        }
        .section {
            background: white;
            padding: 22px;
            margin-top: 25px;
            border-radius: 12px;
        }
        input {
            padding: 10px;
            width: 65px;
            margin: 8px;
        }
        li { margin: 10px 0; }
        footer { text-align: center; padding: 25px; color: #666; }
    </style>
</head>
<body>
<header>
    <h1>ShopEasy</h1>
    <p>Monolithic E-commerce Application</p>
</header>

<main>
    <h2>Our Products</h2>
    <div class="products">
        {% for p in products %}
        <div class="card">
            <div class="emoji">{{ p.emoji }}</div>
            <h3>{{ p.name }}</h3>
            <p class="price">₹{{ "{:,}".format(p.price) }}</p>
            <form action="/order" method="post">
                <input type="hidden" name="product_id" value="{{ p.id }}">
                <label>Qty:
                    <input type="number" name="quantity"
                           value="1" min="1" max="10" required>
                </label>
                <br>
                <button type="submit">Buy Now</button>
            </form>
        </div>
        {% endfor %}
    </div>

    <div class="section">
        <h2>Order Status</h2>
        {% if message %}
            <p>{{ message }}</p>
        {% else %}
            <p>Select a product and click Buy Now to place an order.</p>
        {% endif %}
        <p><strong>Total orders:</strong> {{ orders|length }}</p>
    </div>

    <div class="section">
        <h2>Recent Orders</h2>
        {% if orders %}
        <ul>
            {% for order in orders|reverse %}
            <li>
                Order #{{ order.id }} —
                {{ order.product }} × {{ order.quantity }} —
                ₹{{ "{:,}".format(order.total) }} —
                {{ order.status }}
            </li>
            {% endfor %}
        </ul>
        {% else %}
        <p>No orders placed yet.</p>
        {% endif %}
    </div>
</main>

<footer>ShopEasy | Monolithic Architecture Demo</footer>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(
        HTML, products=products, orders=orders,
        message=request.args.get("message", "")
    )

@app.route("/order", methods=["POST"])
def place_order():
    global next_order_id

    try:
        product_id = int(request.form.get("product_id", 0))
        quantity = int(request.form.get("quantity", 1))
    except ValueError:
        return redirect(url_for("home", message="Invalid order details."))

    product = next((p for p in products if p["id"] == product_id), None)

    if product is None or not 1 <= quantity <= 10:
        return redirect(url_for("home", message="Invalid product or quantity."))

    order = {
        "id": next_order_id,
        "product": product["name"],
        "quantity": quantity,
        "total": product["price"] * quantity,
        "status": "Placed"
    }

    orders.append(order)
    next_order_id += 1

    return redirect(url_for(
        "home",
        message=f"Order #{order['id']} placed successfully!"
    ))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5003, debug=False)