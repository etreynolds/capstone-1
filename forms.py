from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, HiddenField, BooleanField, IntegerRangeField, DateField
from wtforms.validators import DataRequired, Email, Length, NumberRange


class UserAddForm(FlaskForm):
    """Form for adding users."""

    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class AddEntryForm(FlaskForm):
    """Add entry form."""

    date = DateField('Date Watched:', format='%Y-%m-%d',
                     validators=[DataRequired()])
    rating = IntegerRangeField('Rating (0-10)', validators=[
        NumberRange(min=0, max=10)])
    movie_id = HiddenField('Movie ID')
