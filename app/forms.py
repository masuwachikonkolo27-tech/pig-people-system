from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class PigForm(FlaskForm):
    name = StringField('Pig Name', validators=[DataRequired()])
    cost = FloatField('Cost', validators=[DataRequired()])

class SaleForm(FlaskForm):
    amount = FloatField('Sale Amount', validators=[DataRequired()])