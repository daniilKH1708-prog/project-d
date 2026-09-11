from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "my_secret_key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:/Users/kharc/PyCharmMiscProject/project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    password = db.Column(
        db.String(100),
        nullable=False
    )

class Product(db.Model):
    __tablename__ = "project"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    image = db.Column(
        db.String(255)
    )

    category = db.Column(
        db.String(100)
    )

    description = db.Column(
        db.Text
    )

    rating = db.Column(
        db.Float
    )

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = Users.query.filter_by(
            name=username
        ).first()

        if user and user.password == password:

            session["username"] = user.name

            return redirect("/products")

        return render_template(
            "login.html",
            error="Wrong username or password"
        )

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        existing_user = Users.query.filter_by(
            name=username
        ).first()

        if existing_user:

            return render_template(
                "register.html",
                error="Такой пользователь уже существует"
            )

        new_user = Users(
            name=username,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        session["username"] = username

        return redirect("/products")

    return render_template("register.html")

@app.route("/products")
def products():

    if "username" not in session:
        return redirect("/login")

    search = request.args.get("search", "").strip()

    if search:
        all_products = Product.query.filter(
            db.or_(
                Product.name.ilike(f"%{search}%"),
                Product.category.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        ).all()
    else:
        all_products = Product.query.all()

    return render_template(
        "products.html",
        products=all_products,
        username=session["username"],
        search=search
    )
@app.route("/product/<int:product_id>")
def product_details(product_id):
    product = Product.query.get_or_404(product_id)

    return render_template(
        "product_details.html",
        product=product
    )
@app.route("/add_to_cart/<int:product_id>")
def add_to_cart(product_id):

    product = Product.query.get_or_404(product_id)

    cart = session.get("cart", {})

    product_id = str(product_id)

    cart[product_id] = cart.get(product_id, 0) + 1

    session["cart"] = cart

    return redirect("/products")
@app.route("/cart")
def cart():

    cart = session.get("cart", {})

    products = []
    total = 0
    for product_id, quantity in cart.items():

        product = Product.query.get(int(product_id))

        if product:

            products.append({
                "product": product,
                "quantity": quantity
            })

            total += product.price * quantity
    return render_template(
        "cart.html",
        products=products,
        total=total
    )
@app.route("/add_products", methods=["GET", "POST"])
def get_products():

    if request.method == "POST":

        name = request.form.get("name")
        price = request.form.get("price")
        image = request.form.get("image")
        category = request.form.get("category")
        description = request.form.get("description")
        rating = request.form.get("rating")

        new_product = Product(
            name=name,
            price=float(price),
            image=image,
            category=category,
            description=description,
            rating=float(rating) if rating else 0
        )

        db.session.add(new_product)
        db.session.commit()

        return redirect("/products")

    return render_template("add_products.html")
@app.route("/buy", methods=["GET", "POST"])
def buy():

    if request.method == "POST":

        card_id = request.form.get("card_id")

        if not card_id:
            return "Card ID is missing"

        product = Product.query.get_or_404(int(card_id))

        return render_template(
            "buy.html",
            product=product
        )

    return redirect("/cart")
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    app.run(debug=True)