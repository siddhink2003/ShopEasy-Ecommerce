from datetime import datetime, timezone
from flask import Flask, request, jsonify

app = Flask(__name__)

orders = []
next_order_id = 1


@app.route("/")
def home():
    return "<h1>E-commerce Order Service</h1><p>Order Service is running!</p>"


@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify(list(reversed(orders)))  # newest first


@app.route("/orders", methods=["POST"])
def create_order():
    global next_order_id

    data = request.get_json(silent=True) or {}

    if not data.get("items"):
        return jsonify({"error": "Order must contain items"}), 400

    order = {
        "order_id": next_order_id,
        "items": data["items"],
        "total": data.get("total", 0),
        "status": "Placed",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    orders.append(order)
    next_order_id += 1

    return jsonify(order), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
