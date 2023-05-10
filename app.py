from flask import Flask, render_template, redirect, request, url_for, session
from flask_session import Session
from cs50 import SQL

app = Flask(__name__)
db = SQL('sqlite:///store.db')

app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"
Session(app)

@app.route("/")
def index(scrollTo = None):
    books = db.execute('SELECT * FROM books')

    if scrollTo:
        return render_template('index.html', stylesheet = url_for('static', filename='styles/index.css'), books = books, scrollTo = scrollTo)
    return render_template('index.html', stylesheet = url_for('static', filename='styles/index.css'), books = books)

@app.route("/cart", methods=["GET", "POST"])
def cart():
    if "cart" not in session:
        session["cart"] = {}

    if request.method == "POST":
        id, quantity = int(request.form.get("id")), int(request.form.get("quantity"))

        if id:
            session_quantity = session["cart"].get(id, {"quantity": 0})["quantity"]
            quantity = min(quantity, 10 - session_quantity)
            session["cart"][id] = {"quantity": session_quantity + quantity}
        return index(id)
    
    cart = db.execute("SELECT * FROM books WHERE id IN(?)", list(session["cart"].keys()))

    for item in cart:
        item['quantity'] = session["cart"][int(item['id'])]["quantity"]
    return render_template('cart.html', stylesheet = url_for('static', filename='styles/cart.css'), cart=cart)

@app.route("/remove", methods=["POST"])
def remove():
    id = int(request.form.get("id"))

    if id:
        session["cart"][id]["quantity"] -= 1 if "decrease-quantity" in request.form else 0
        if session["cart"][id]["quantity"] <= 0 or "remove-item" in request.form:
            del session["cart"][id]
    return redirect("/cart")