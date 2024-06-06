from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, URL


class AddCafe(FlaskForm):
    name = StringField("Cafe Name", validators=[DataRequired()])
    map_url = StringField("Maps Location", validators=[DataRequired(), URL()])
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    description = StringField("Cafe Description", validators=[DataRequired()])
    location = StringField("Location of Cafe", validators=[DataRequired()])
    seats = StringField("Amount of Seats", validators=[DataRequired()])
    has_toilet = StringField("Toilets", validators=[DataRequired(), ])
    has_wifi = StringField("Wifi", validators=[DataRequired()])
    has_sockets = StringField("Sockets", validators=[DataRequired()])
    can_take_calls = StringField("Take Calls", validators=[DataRequired()])
    coffee_price = StringField("Coffee Price", validators=[DataRequired()])
    submit = SubmitField("Submit Cafe")


class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Create")


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")

