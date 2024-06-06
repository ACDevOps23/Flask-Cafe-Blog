from flask import Flask, render_template, request, url_for, redirect, flash, abort
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from functools import wraps
from form import AddCafe, RegisterForm, LoginForm
import base64
import hashlib
import bcrypt
import datetime
import os


app = Flask(__name__)
bootstrap = Bootstrap5(app)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLite_DB", 'sqlite:///cafes.db')
app.config["SECRET_KEY"] = os.environ.get("FLASK_KEY")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Flask-login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(cafe_user_id):
    return db.get_or_404(Cafe_User, cafe_user_id)

# Cafe Database
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[str] = mapped_column(String(250), nullable=False)
    has_wifi: Mapped[str] = mapped_column(String(250), nullable=False)
    has_sockets: Mapped[str] = mapped_column(String(250), nullable=False)
    can_take_calls: Mapped[str] = mapped_column(String(250), nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

# Cafe User Database
class Cafe_User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=False, nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)


with app.app_context():
    db.create_all()

# custom decorator
def logged_in(user):
    @wraps(user)
    def only_logged_in(*args, **kwargs):
        if current_user.is_authenticated:
            return user(*args, **kwargs)
        else:
            return abort(403)
    return only_logged_in



@app.route("/")
def home():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    cafe = result.scalars().all()
    return render_template("index.html", cafes=cafe)

# Create an account
@app.route("/register", methods=["GET", "POST"])
def create_account():
    register_user = RegisterForm()

    if register_user.validate_on_submit():
        email = register_user.email.data
        result = db.session.execute(db.select(Cafe_User).where(Cafe_User.email == email))

        check_email = result.scalar()

        if check_email:
            flash("You already have an account, Log in")
            return redirect(url_for("login"))
        else:
            password = register_user.password.data
            p_byte = password.encode("utf-8")

            hash_password = bcrypt.hashpw(base64.b64encode(hashlib.sha256(p_byte).digest()), bcrypt.gensalt())

            user = Cafe_User(name=register_user.name.data,
                         email=register_user.email.data,
                         password=hash_password)

            db.session.add(user)
            db.session.commit()
            return redirect(url_for("login"))
    return render_template("register.html", form=register_user, current_user=current_user)


# login user
@app.route("/login", methods=["GET", "POST"])
def login():

    user_login = LoginForm()

    if user_login.validate_on_submit():

        email = user_login.email.data
        result = db.session.execute(db.select(Cafe_User).where(Cafe_User.email == email))
        user_email = result.scalar()

        password = user_login.password.data.encode("utf-8")
        p_word = base64.b64encode(hashlib.sha256(password).digest())

        if user_email and bcrypt.checkpw(p_word, user_email.password):
            login_user(user_email)
            return redirect(url_for("home"))
        else:
            flash("Email or password does not exist")
            return redirect(url_for("login"))

    return render_template("login.html", form=user_login, current_user=current_user)

# logout user
@app.route("/logout")
@logged_in
def logout():
    logout_user()
    return redirect(url_for("home"))


# Add a Cafe
@app.route("/add", methods=["GET", "POST"])
@logged_in
def add_cafe():
    cafe_form = AddCafe()

    if cafe_form.validate_on_submit():
        new_cafe = Cafe(name=cafe_form.name.data,
                        map_url=cafe_form.map_url.data,
                        img_url=cafe_form.img_url.data,
                        description=cafe_form.description.data,
                        location=cafe_form.location.data,
                        seats=cafe_form.seats.data,
                        has_toilet=cafe_form.has_toilet.data,
                        has_wifi=cafe_form.has_wifi.data,
                        has_sockets=cafe_form.has_sockets.data,
                        can_take_calls=cafe_form.can_take_calls.data,
                        coffee_price=cafe_form.coffee_price.data)

        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("add.html", form=cafe_form, current_user=current_user)

# search cafe by city
@app.route("/search", methods=["GET", "POST"])
def search_cafe():

    if request.method == "POST":
        cafe_search = request.form["search"].title()
        result = db.session.execute(db.select(Cafe).where(Cafe.location == cafe_search).order_by(Cafe.name))
        cafes = result.scalars().all()
        if not cafes:
            flash(f"No cafes in {cafe_search}")

        return render_template("search.html", search=cafes, current_user=current_user)


# Edit a Cafe
@app.route("/update/<int:cafe_id>", methods=["GET", "POST"])
@logged_in
def edit_cafes(cafe_id):
    find_cafe = db.get_or_404(Cafe, cafe_id)

    edit_cafe = AddCafe(
        name=find_cafe.name,
        map_url=find_cafe.map_url,
        img_url=find_cafe.img_url,
        description=find_cafe.description,
        location=find_cafe.location,
        seats=find_cafe.seats,
        has_toilet=find_cafe.has_toilet,
        has_wifi=find_cafe.has_wifi,
        has_sockets=find_cafe.has_sockets,
        can_take_calls=find_cafe.can_take_calls,
        coffee_price=find_cafe.coffee_price)

    if edit_cafe.validate_on_submit():
        find_cafe.name = edit_cafe.name.data
        find_cafe.map_url = edit_cafe.map_url.data
        find_cafe.img_url = edit_cafe.img_url.data
        find_cafe.description = edit_cafe.description.data
        find_cafe.location = edit_cafe.location.data
        find_cafe.seats = edit_cafe.seats.data
        find_cafe.has_toilet = edit_cafe.has_toilet.data
        find_cafe.has_wifi = edit_cafe.has_wifi.data
        find_cafe.has_sockets = edit_cafe.has_sockets.data
        find_cafe.can_take_calls = edit_cafe.can_take_calls.data
        find_cafe.coffee_price = edit_cafe.coffee_price.data
        db.session.commit()
        return redirect(url_for("home", cafe_id=find_cafe.id))

    return render_template("add.html", form=edit_cafe, edit=True, current_user=current_user)


# Delete a Cafe
@app.route("/delete/<int:cafe_id>")
@logged_in
def delete_cafe(cafe_id):

    remove_cafe = db.get_or_404(Cafe, cafe_id)
    db.session.delete(remove_cafe)
    db.session.commit()
    return redirect(url_for("home", current_user=current_user))

# about the website
@app.route("/about")
def about():
    return render_template("about.html")


if __name__ == '__main__':
    app.run(debug=False)