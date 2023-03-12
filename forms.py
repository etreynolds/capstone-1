from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class LogActivityForm(FlaskForm):
    """Log activity form."""

    # media_type = SelectField('Media Type', choices=[(
    #     'movie', 'Movie'), ('tv', 'TV Show')], coerce=str, default='movie')
    media_name = StringField('Movie Name', validators=[DataRequired()])
    date = DateField('Date (YYYY-M-D)', format='%Y-%m-%d')
    # movie_theater = BooleanField('Watched movie in theater?', default=False)
    # movie_with_people = BooleanField(
    #     'Watched movie with people?', default=False)
    # movie_new = BooleanField('First time watching this movie?', default=False)
    # tv_episodes = IntegerField('Number of episodes watched')
