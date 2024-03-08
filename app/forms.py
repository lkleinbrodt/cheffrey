from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    # email = StringField('Email', validators = [DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=5)])
    password2 = PasswordField(
        "Repeat Password",
        validators=[DataRequired(), EqualTo("password", "Passwords do not match.")],
    )
    submit = SubmitField("Register")

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(User.email == email.data))
        if user is not None:
            raise ValidationError("User already exists with that email.")

    # def validate_email(self, email):
    #     user = db.session.scalar(
    #         sa.select(User).where(User.email == email.data)
    #     )
    #     if user is not None:
    #         raise ValidationError('Please use a different email address.')


class SettingsForm(FlaskForm):
    phone_number = StringField("Phone Number", validators=[DataRequired()])
    submit = SubmitField("Save")


# class VerificationForm(FlaskForm):
#     phone_number = StringField('Phone', validators=[DataRequired()])
#     verification_code = StringField('Verification Code', validators=[DataRequired(), Length(min=6, max=6)])
#     submit = SubmitField('Verify')

#     def validate_phone_number(form, field):
#         if len(field.data) > 16:
#             raise ValidationError('Invalid phone number.')
#         try:
#             input_number = phonenumbers.parse(field.data)
#             if not (phonenumbers.is_valid_number(input_number)):
#                 raise ValidationError('Invalid phone number.')
#         except:
#             input_number = phonenumbers.parse("+1"+field.data)
#             if not (phonenumbers.is_valid_number(input_number)):
#                 raise ValidationError('Invalid phone number.')
