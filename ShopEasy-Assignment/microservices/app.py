from flask import Flask, Response, request, jsonify
import urllib.request
import urllib.error
import json
import os

app = Flask(__name__)

PRODUCT_SERVICE_URL = os.environ.get("PRODUCT_SERVICE_URL", "http://127.0.0.1:5001")
ORDER_SERVICE_URL = os.environ.get("ORDER_SERVICE_URL", "http://127.0.0.1:5002")

# Used only if the Product Service is down, so the storefront still loads.
FALLBACK_PRODUCTS = [
    {"id": 1, "name": "Laptop", "price": 45000, "emoji": "💻", "category": "Computers",
     "description": "14-inch, 16 GB RAM, all-day battery."},
    {"id": 2, "name": "Headphones", "price": 1500, "emoji": "🎧", "category": "Audio",
     "description": "Over-ear, deep bass, 30-hour playtime."},
    {"id": 3, "name": "Smart Watch", "price": 2500, "emoji": "⌚", "category": "Wearables",
     "description": "Heart-rate, sleep and step tracking."},
    {"id": 4, "name": "Keyboard", "price": 900, "emoji": "⌨️", "category": "Accessories",
     "description": "Compact mechanical keyboard, quiet switches."},
]


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ShopEasy | Everyday tech, delivered</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#F1F3F8; --surface:#fff; --ink:#12172B; --muted:#5E6785; --line:#E1E5EF;
  --brand:#3B3FE0; --brand-d:#2C2FB8; --ok:#0E9F6E; --err:#C8302B;
  --display:'Bricolage Grotesque','Segoe UI',sans-serif; --body:'DM Sans','Segoe UI',sans-serif;
}
*{box-sizing:border-box}
body{margin:0;font-family:var(--body);background:var(--bg);color:var(--ink);line-height:1.5}
button,input{font:inherit}
:focus-visible{outline:3px solid var(--brand);outline-offset:2px}
.wrap{max-width:1120px;margin:0 auto;padding:0 24px}

/* header */
header.top{background:var(--surface);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
.bar{display:flex;align-items:center;gap:16px;height:68px}
.logo{font-family:var(--display);font-weight:800;font-size:24px;letter-spacing:-.02em;margin-right:auto}
.logo span{color:var(--brand)}
.btn{border:0;border-radius:10px;padding:11px 18px;font-weight:700;cursor:pointer;transition:background .15s}
.btn-primary{background:var(--brand);color:#fff}
.btn-primary:hover{background:var(--brand-d)}
.btn-primary:disabled{background:#B9BBEF;cursor:not-allowed}
.btn-ghost{background:transparent;color:var(--ink);border:1px solid var(--line)}
.btn-ghost:hover{background:var(--bg)}
.badge{background:#fff;color:var(--brand);border-radius:99px;padding:0 8px;margin-left:6px;font-size:13px}

/* hero */
.hero{padding:56px 0 32px}
.hero h1{font-family:var(--display);font-weight:800;font-size:clamp(34px,6vw,58px);line-height:1.04;letter-spacing:-.03em;margin:0 0 14px;max-width:14ch}
.hero p{color:var(--muted);font-size:18px;margin:0 0 26px;max-width:46ch}
.search{display:flex;align-items:center;gap:10px;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:4px 16px;max-width:520px}
.search input{flex:1;border:0;background:transparent;padding:13px 0;outline:none}
.search:focus-within{border-color:var(--brand);box-shadow:0 0 0 3px #3B3FE033}

/* filters + grid */
.chips{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 22px}
.chip{border:1px solid var(--line);background:var(--surface);border-radius:99px;padding:8px 16px;cursor:pointer;font-weight:500}
.chip[aria-pressed=true]{background:var(--ink);border-color:var(--ink);color:#fff}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:20px;padding-bottom:64px}
.card{background:var(--surface);border-radius:18px;overflow:hidden;border:1px solid var(--line);display:flex;flex-direction:column}
.tile{height:150px;display:grid;place-items:center;font-size:68px}
.card:nth-child(4n+1) .tile{background:#E4E5FB}
.card:nth-child(4n+2) .tile{background:#FDEBD3}
.card:nth-child(4n+3) .tile{background:#D9F2E6}
.card:nth-child(4n+4) .tile{background:#FBE0E4}
.info{padding:18px;display:flex;flex-direction:column;gap:4px;flex:1}
.cat{color:var(--muted);font-size:13px}
.info h3{font-family:var(--display);font-size:21px;margin:0;letter-spacing:-.01em}
.desc{color:var(--muted);font-size:14px;margin:0 0 12px;flex:1}
.row{display:flex;align-items:center;justify-content:space-between;gap:10px}
.price{font-family:var(--display);font-weight:700;font-size:20px}
.empty{grid-column:1/-1;text-align:center;color:var(--muted);padding:48px 0}
.skeleton{height:300px;border-radius:18px;background:linear-gradient(90deg,#E6E9F2 25%,#F3F5FA 50%,#E6E9F2 75%);background-size:200% 100%;animation:sh 1.2s infinite}
@keyframes sh{to{background-position:-200% 0}}
.notice{background:#FFF4E0;border:1px solid #F5D9A6;border-radius:10px;padding:10px 14px;margin-bottom:18px;font-size:14px}

/* cart drawer */
.scrim{position:fixed;inset:0;background:#12172B66;opacity:0;pointer-events:none;transition:opacity .2s;z-index:30}
.scrim.on{opacity:1;pointer-events:auto}
aside.cart{position:fixed;top:0;right:0;height:100%;width:min(420px,100%);background:var(--surface);z-index:40;display:flex;flex-direction:column;transform:translateX(100%);transition:transform .25s ease}
aside.cart.on{transform:none}
.cart-h{display:flex;align-items:center;justify-content:space-between;padding:20px 24px;border-bottom:1px solid var(--line)}
.cart-h h2{font-family:var(--display);margin:0;font-size:22px}
.lines{flex:1;overflow:auto;padding:8px 24px;margin:0;list-style:none}
.line{display:grid;grid-template-columns:48px 1fr auto;gap:12px;align-items:center;padding:14px 0;border-bottom:1px solid var(--line)}
.line .e{font-size:30px;background:var(--bg);border-radius:10px;display:grid;place-items:center;height:48px}
.line b{display:block}
.line small{color:var(--muted)}
.qty{display:inline-flex;align-items:center;border:1px solid var(--line);border-radius:8px;margin-top:6px}
.qty button{width:30px;height:30px;border:0;background:none;cursor:pointer;font-size:18px}
.qty span{min-width:24px;text-align:center;font-weight:700}
.rm{border:0;background:none;color:var(--err);cursor:pointer;font-size:13px;display:block;margin-left:auto}
.cart-f{padding:20px 24px;border-top:1px solid var(--line)}
.total{display:flex;justify-content:space-between;font-family:var(--display);font-size:22px;font-weight:700;margin-bottom:14px}
.msg{min-height:22px;margin:10px 0 0;font-size:14px;color:var(--err)}
.cart-f .btn{width:100%}

/* dialogs */
dialog{border:0;border-radius:20px;padding:0;width:min(520px,92vw);box-shadow:0 24px 60px #12172B40}
dialog::backdrop{background:#12172B66}
.dlg{padding:28px}
.dlg h2{font-family:var(--display);margin:0 0 6px}
.tick{width:56px;height:56px;border-radius:50%;background:var(--ok);color:#fff;display:grid;place-items:center;font-size:28px;margin-bottom:14px}
.order{border:1px solid var(--line);border-radius:12px;padding:14px;margin-top:12px}
.order .row{font-weight:700}
.order small{color:var(--muted)}
.status{background:#D9F2E6;color:#0A6B4A;border-radius:99px;padding:2px 10px;font-size:13px}

@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>

<header class="top">
  <div class="wrap bar">
    <div class="logo">Shop<span>Easy</span></div>
    <button class="btn btn-ghost" id="ordersBtn">My orders</button>
    <button class="btn btn-primary" id="cartBtn" aria-controls="cart">Cart<span class="badge" id="count">0</span></button>
  </div>
</header>

<main class="wrap">
  <section class="hero">
    <h1>Everyday tech, delivered.</h1>
    <p>Laptops, audio and accessories at honest prices. Add what you need and check out in one step.</p>
    <label class="search">
      <span aria-hidden="true">🔍</span>
      <input id="q" type="search" placeholder="Search products" aria-label="Search products" autocomplete="off">
    </label>
  </section>

  <div class="chips" id="chips" role="group" aria-label="Filter by category"></div>
  <div id="notice"></div>
  <section class="grid" id="grid" aria-live="polite"></section>
</main>

<div class="scrim" id="scrim"></div>
<aside class="cart" id="cart" aria-label="Shopping cart">
  <div class="cart-h"><h2>Your cart</h2><button class="btn btn-ghost" id="closeCart">Close</button></div>
  <ul class="lines" id="lines"></ul>
  <div class="cart-f">
    <div class="total"><span>Total</span><span id="total">₹0</span></div>
    <button class="btn btn-primary" id="orderBtn">Place order</button>
    <p class="msg" id="msg" role="alert"></p>
  </div>
</aside>

<dialog id="done"><div class="dlg">
  <div class="tick">✓</div>
  <h2 id="doneTitle">Order placed</h2>
  <p id="doneText" style="color:var(--muted);margin:0 0 18px"></p>
  <button class="btn btn-primary" id="doneClose">Keep shopping</button>
</div></dialog>

<dialog id="ordersDlg"><div class="dlg">
  <h2>My orders</h2>
  <div id="ordersList"></div>
  <button class="btn btn-ghost" id="ordersClose" style="margin-top:18px">Close</button>
</div></dialog>

<script>
const $ = id => document.getElementById(id);
const inr = n => '₹' + n.toLocaleString('en-IN');
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

let products = [], cart = {}, category = 'All', query = '';

/* ---------- products ---------- */
async function loadProducts() {
  $('grid').innerHTML = '<div class="skeleton"></div>'.repeat(4);
  try {
    const res = await fetch('/api/products');
    const data = await res.json();
    products = data.products;
    $('notice').innerHTML = data.live ? '' :
      '<div class="notice">Product Service is offline, so you are seeing the saved catalog.</div>';
  } catch {
    $('grid').innerHTML = '<p class="empty">Could not load products. Refresh the page to try again.</p>';
    return;
  }
  renderChips(); renderGrid();
}

function renderChips() {
  const cats = ['All', ...new Set(products.map(p => p.category).filter(Boolean))];
  $('chips').innerHTML = cats.map(c =>
    `<button class="chip" aria-pressed="${c === category}" data-c="${esc(c)}">${esc(c)}</button>`).join('');
}

function renderGrid() {
  const list = products.filter(p =>
    (category === 'All' || p.category === category) &&
    p.name.toLowerCase().includes(query));
  $('grid').innerHTML = list.length ? list.map(p => `
    <article class="card">
      <div class="tile" aria-hidden="true">${p.emoji || '📦'}</div>
      <div class="info">
        <span class="cat">${esc(p.category || '')}</span>
        <h3>${esc(p.name)}</h3>
        <p class="desc">${esc(p.description || '')}</p>
        <div class="row">
          <span class="price">${inr(p.price)}</span>
          <button class="btn btn-primary" data-add="${p.id}">Add to cart</button>
        </div>
      </div>
    </article>`).join('') :
    '<p class="empty">No products match your search. Try a different word or choose All.</p>';
}

$('chips').onclick = e => {
  const c = e.target.dataset.c; if (!c) return;
  category = c; renderChips(); renderGrid();
};
$('q').oninput = e => { query = e.target.value.trim().toLowerCase(); renderGrid(); };
$('grid').onclick = e => {
  const id = e.target.dataset.add; if (!id) return;
  cart[id] = Math.min((cart[id] || 0) + 1, 20);
  renderCart(); $('msg').textContent = '';
  e.target.textContent = 'Added'; setTimeout(() => e.target.textContent = 'Add to cart', 900);
};

/* ---------- cart ---------- */
const entries = () => Object.entries(cart).map(([id, qty]) => ({p: products.find(x => x.id == id), qty})).filter(x => x.p);

function renderCart() {
  const list = entries();
  $('count').textContent = list.reduce((s, x) => s + x.qty, 0);
  $('total').textContent = inr(list.reduce((s, x) => s + x.p.price * x.qty, 0));
  $('orderBtn').disabled = !list.length;
  $('lines').innerHTML = list.length ? list.map(({p, qty}) => `
    <li class="line">
      <div class="e">${p.emoji || '📦'}</div>
      <div><b>${esc(p.name)}</b><small>${inr(p.price)} each</small>
        <div class="qty">
          <button data-dec="${p.id}" aria-label="Decrease quantity of ${esc(p.name)}">−</button>
          <span>${qty}</span>
          <button data-inc="${p.id}" aria-label="Increase quantity of ${esc(p.name)}">+</button>
        </div></div>
      <div><b>${inr(p.price * qty)}</b><button class="rm" data-rm="${p.id}">Remove</button></div>
    </li>`).join('') :
    '<li class="empty">Your cart is empty. Add a product to get started.</li>';
}

$('lines').onclick = e => {
  const d = e.target.dataset;
  if (d.inc) cart[d.inc] = Math.min(cart[d.inc] + 1, 20);
  if (d.dec && --cart[d.dec] < 1) delete cart[d.dec];
  if (d.rm) delete cart[d.rm];
  renderCart();
};

const openCart = on => { $('cart').classList.toggle('on', on); $('scrim').classList.toggle('on', on); };
$('cartBtn').onclick = () => openCart(true);
$('closeCart').onclick = $('scrim').onclick = () => openCart(false);
document.addEventListener('keydown', e => { if (e.key === 'Escape') openCart(false); });

async function placeOrder() {
  const items = entries().map(({p, qty}) => ({id: p.id, qty}));
  $('msg').textContent = ''; $('orderBtn').disabled = true; $('orderBtn').textContent = 'Placing order…';
  try {
    const res = await fetch('/place-order', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({items})
    });
    const r = await res.json();
    if (!res.ok) throw new Error(r.error || 'Could not place the order. Please try again.');
    cart = {}; renderCart(); openCart(false);
    $('doneTitle').textContent = 'Order #' + r.order_id + ' placed';
    $('doneText').textContent = 'Total ' + inr(r.total) + '. We will start packing it right away.';
    $('done').showModal();
  } catch (err) {
    $('msg').textContent = err.message;
  } finally {
    $('orderBtn').textContent = 'Place order'; renderCart();
  }
}
$('orderBtn').onclick = placeOrder;
$('doneClose').onclick = () => $('done').close();

/* ---------- orders ---------- */
$('ordersBtn').onclick = async () => {
  $('ordersList').innerHTML = '<p class="empty">Loading orders…</p>';
  $('ordersDlg').showModal();
  try {
    const res = await fetch('/api/orders');
    const orders = await res.json();
    if (!res.ok) throw new Error(orders.error);
    $('ordersList').innerHTML = orders.length ? orders.map(o => `
      <div class="order">
        <div class="row"><span>Order #${o.order_id}</span><span class="status">${esc(o.status)}</span></div>
        <small>${o.items.map(i => esc(i.name) + (i.qty ? ' × ' + i.qty : '')).join(', ')}</small>
        <div class="row" style="margin-top:6px"><span>${inr(o.total)}</span></div>
      </div>`).join('') :
      '<p class="empty">No orders yet. Place your first order from the cart.</p>';
  } catch (err) {
    $('ordersList').innerHTML = '<p class="empty">' + esc(err.message || 'Could not load orders.') + '</p>';
  }
};
$('ordersClose').onclick = () => $('ordersDlg').close();

renderCart();
loadProducts();
</script>
</body>
</html>
"""


def call_service(url, payload=None, timeout=5):
    """GET (or POST when payload is given) JSON from another service."""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8")), response.status


def load_products():
    try:
        data, _ = call_service(f"{PRODUCT_SERVICE_URL}/products", timeout=3)
        return data, True
    except (urllib.error.URLError, TimeoutError, ValueError):
        return FALLBACK_PRODUCTS, False


@app.route("/")
def home():
    return Response(HTML, mimetype="text/html")


@app.route("/api/products")
def api_products():
    items, live = load_products()
    return jsonify({"products": items, "live": live})


@app.route("/api/orders")
def api_orders():
    try:
        data, status = call_service(f"{ORDER_SERVICE_URL}/orders")
        return jsonify(data), status
    except (urllib.error.URLError, TimeoutError):
        return jsonify({"error": "Order Service is unavailable."}), 503


@app.route("/place-order", methods=["POST"])
def place_order():
    data = request.get_json(silent=True) or {}
    items = data.get("items", [])

    if not items:
        return jsonify({"error": "Please add a product first."}), 400

    # Prices and names always come from the server, never from the browser.
    catalog, _ = load_products()
    lookup = {p["id"]: p for p in catalog}
    validated = []

    for item in items:
        product = lookup.get(item.get("id"))
        try:
            qty = int(item.get("qty", 1))
        except (TypeError, ValueError):
            qty = 0
        if product is None or not 1 <= qty <= 20:
            return jsonify({"error": "Invalid product or quantity."}), 400
        validated.append({
            "id": product["id"], "name": product["name"],
            "emoji": product.get("emoji", ""), "price": product["price"], "qty": qty,
        })

    total = sum(i["price"] * i["qty"] for i in validated)

    try:
        result, status = call_service(
            f"{ORDER_SERVICE_URL}/orders", {"items": validated, "total": total}
        )
        return jsonify(result), status
    except urllib.error.HTTPError:
        return jsonify({"error": "Order Service rejected the request."}), 502
    except (urllib.error.URLError, TimeoutError):
        return jsonify({"error": "Order Service is unavailable. Please try again."}), 503


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
