from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    user_name = StringField("UserName", validators = [DataRequired()])
    password = PasswordField("Password",validators = [DataRequired()])
    submit = SubmitField("Sign In")

class SignupForm(FlaskForm):
    user_name = StringField("UserName", validators = [DataRequired()])
    email = EmailField("Email",validators = [DataRequired()])
    password = PasswordField("Password",validators = [DataRequired()])
    vpassword = PasswordField("Validate Password", validators = [DataRequired()])
    submit = SubmitField("Sign Up")

class PasswordResetForm(FlaskForm):
    current_password = PasswordField("Current Password", validators = [DataRequired()])
    new_password = PasswordField("New Password", validators = [DataRequired()])
    confirm_new_password = PasswordField("Confirm New Password", validators = [DataRequired()])
    submit = SubmitField("Reset Password")

class PasswordRecovery(FlaskForm):
    email = EmailField("Email", validators = [DataRequired()])
    submit = SubmitField("Recover Password")