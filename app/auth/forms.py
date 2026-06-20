import re

from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError,
)

from app.models import User


PASSWORD_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{12,}$"
)


class RegistrationForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=255)],
    )
    first_name = StringField(
        "First Name",
        validators=[Length(max=120)],
    )
    last_name = StringField(
        "Last Name",
        validators=[Length(max=120)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=12, max=128)],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")],
    )

    submit = SubmitField("Register")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError(
                "An account with this email already exists."
            )

    def validate_password(self, password):
        if not PASSWORD_REGEX.match(password.data or ""):
            raise ValidationError(
                "Password must be at least 12 characters and include "
                "uppercase, lowercase, number, and special character."
            )


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=255)],
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
    )
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[DataRequired(), Email(), Length(max=255)],
    )
    submit = SubmitField("Request Password Reset")


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=12, max=128)],
    )
    confirm_password = PasswordField(
        "Confirm New Password",
        validators=[DataRequired(), EqualTo("password")],
    )

    def validate_password(self, password):
        if not PASSWORD_REGEX.match(password.data or ""):
            raise ValidationError(
                "Password must be at least 12 characters and include "
                "uppercase, lowercase, number, and special character."
            )

    submit = SubmitField("Reset Password")
    