from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from wtforms import TextAreaField, FloatField, IntegerField
from flask_wtf.file import FileField, FileAllowed

class LoginForm(FlaskForm):
    
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired()]
    )

    submit = SubmitField("Login")
    
class RegisterForm(FlaskForm):

    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=3, max=30)]
    )

    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=6)]
    )

    submit = SubmitField("Register")
    
class ProductForm(FlaskForm):
    
    name = StringField("Product Name", validators=[DataRequired()])

    description = TextAreaField("Description")

    price = FloatField("Price", validators=[DataRequired()])

    stock = IntegerField("Stock", validators=[DataRequired()])

    category = StringField("Category", validators=[DataRequired()])

    image = FileField(
        "Product Image",
        validators=[
            FileAllowed(["jpg", "jpeg", "png"], "Images only!")
        ]
    )

    submit = SubmitField("Save Product")