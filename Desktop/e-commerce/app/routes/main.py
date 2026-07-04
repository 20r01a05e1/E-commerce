from app import db
from flask import Blueprint, render_template,request,flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import RegisterForm, LoginForm, ProductForm
from app.models import Product, Order, User, Cart
from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename
from flask import current_app

main = Blueprint("main", __name__)


@main.route("/")
def home():

    featured_products = Product.query.limit(8).all()

    return render_template(
        "home.html",
        featured_products=featured_products
    )

@main.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()

        if existing_user:
            return "Email already registered!"

        hashed_password = generate_password_hash(form.password.data)

        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return "Registration Successful!"

    return render_template(
        "register.html",
        form=form
    )
    
@main.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and check_password_hash(
                user.password,
                form.password.data):

            login_user(user)

            return redirect(url_for("main.home"))

        flash("Invalid Email or Password", "danger")

    return render_template(
        "login.html",
        form=form
    )
    
@main.route("/admin")
def admin():

    total_products = Product.query.count()

    total_users = User.query.count()

    total_orders = Order.query.count()

    return render_template(
        "admin_dashboard.html",
        total_products=total_products,
        total_users=total_users,
        total_orders=total_orders
    )
    
@main.route("/add-product", methods=["GET", "POST"])
def add_product():

    form = ProductForm()

    if form.validate_on_submit():

        filename = ""

        if form.image.data:
            image = form.image.data
            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    current_app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock=form.stock.data,
            category=form.category.data,
            image=filename
        )

        db.session.add(product)
        db.session.commit()

        flash("Product Added Successfully!", "success")

        return redirect(url_for("main.admin_products"))

    if request.method == "POST":
        print("VALID:", form.validate_on_submit())
        print("ERRORS:", form.errors)

    return render_template("add_product.html", form=form)

@main.route("/products")
def products():

    search = request.args.get("search")

    category = request.args.get("category")

    query = Product.query

    if search:

        query = query.filter(
            Product.name.ilike(f"%{search}%")
        )

    if category:

        query = query.filter_by(
            category=category
        )

    products = query.all()

    return render_template(
        "products.html",
        products=products
    )
    
@main.route("/product/<int:id>")
def product_details(id):

    product = Product.query.get_or_404(id)

    return render_template(
        "product_details.html",
        product=product
    )
    
@main.route("/add-to-cart/<int:id>")
@login_required
def add_to_cart(id):

    product = Product.query.get_or_404(id)

    cart_item = Cart(
        user_id=current_user.id,
        product_id=product.id,
        quantity=1
    )

    db.session.add(cart_item)
    db.session.commit()

    flash("Product added to cart!")

    return redirect(url_for("main.products"))

@main.route("/cart")
@login_required
def cart():

    cart_items = Cart.query.filter_by(
        user_id=current_user.id
    ).all()

    total = 0

    for item in cart_items:
        total += item.product.price * item.quantity

    return render_template(
        "cart.html",
        cart_items=cart_items,
        total=total
    )
    
@main.route("/checkout")
@login_required
def checkout():

    cart_items = Cart.query.filter_by(
        user_id=current_user.id
    ).all()

    total = 0

    for item in cart_items:
        total += item.product.price * item.quantity

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        total=total
    )
    
@main.route("/place-order")
@login_required
def place_order():

    cart_items = Cart.query.filter_by(
        user_id=current_user.id
    ).all()

    if not cart_items:
        flash("Your cart is empty!")
        return redirect(url_for("main.cart"))

    total = 0

    for item in cart_items:
        total += item.product.price * item.quantity

    order = Order(
        user_id=current_user.id,
        total_price=total,
        status="Pending"
    )

    db.session.add(order)

    for item in cart_items:
        db.session.delete(item)

    db.session.commit()

    flash("Order Placed Successfully!")

    return redirect(url_for("main.orders"))

@main.route("/orders")
@login_required
def orders():

    orders = Order.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "orders.html",
        orders=orders
    )
    
@main.route("/increase/<int:id>")
@login_required
def increase_quantity(id):

    cart_item = Cart.query.get_or_404(id)

    cart_item.quantity += 1

    db.session.commit()

    return redirect(url_for("main.cart"))

@main.route("/decrease/<int:id>")
@login_required
def decrease_quantity(id):

    cart_item = Cart.query.get_or_404(id)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        db.session.commit()

    return redirect(url_for("main.cart"))


@main.route("/remove/<int:id>")
@login_required
def remove_from_cart(id):

    cart_item = Cart.query.get_or_404(id)

    db.session.delete(cart_item)

    db.session.commit()

    flash("Item removed from cart.", "success")

    return redirect(url_for("main.cart"))

@main.route("/admin/products")
def admin_products():

    products = Product.query.all()

    return render_template(
        "admin_products.html",
        products=products
    )
    
@main.route("/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):

    product = Product.query.get_or_404(id)

    form = ProductForm(obj=product)

    if form.validate_on_submit():

        product.name = form.name.data
        product.description = form.description.data
        product.price = form.price.data
        product.stock = form.stock.data
        product.category = form.category.data
        product.image = form.image.data

        db.session.commit()

        flash("Product Updated Successfully!", "success")

        return redirect(url_for("main.admin_products"))

    return render_template(
        "edit_product.html",
        form=form
    )


@main.route("/delete-product/<int:id>")
def delete_product(id):

    product = Product.query.get_or_404(id)

    db.session.delete(product)

    db.session.commit()

    flash("Product Deleted Successfully!", "success")

    return redirect(url_for("main.admin_products"))


@main.route("/admin/orders")
def admin_orders():

    orders = Order.query.all()

    return render_template(
        "admin_orders.html",
        orders=orders
    )
    
@main.route("/update-order/<int:id>")
def update_order_status(id):

    order = Order.query.get_or_404(id)

    if order.status == "Pending":
        order.status = "Processing"

    elif order.status == "Processing":
        order.status = "Shipped"

    elif order.status == "Shipped":
        order.status = "Delivered"

    db.session.commit()

    flash("Order status updated successfully!", "success")

    return redirect(url_for("main.admin_orders"))

@main.route("/logout")
@login_required
def logout():

    logout_user()

    flash("Logged out successfully!", "success")

    return redirect(url_for("main.home"))