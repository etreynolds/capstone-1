from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User model."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)

    entries = db.relationship('Entry')

    def __repr__(self):
        return f"<User #{self.id}: {self.name}, {self.username}, {self.email}>"

    @classmethod
    def signup(cls, name, username, password, email):
        """Sign up user. Hashes password and adds user to system."""

        hashed_pw = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(name=name, username=username,
                    email=email, password=hashed_pw)

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with 'username' and 'password'.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class Movie(db.Model):
    """Movie model."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    release_date = db.Column(db.Date)
    genre = db.Column(db.Text)
    runtime = db.Column(db.Integer)
    poster_path = db.Column(db.Text)

    def __init__(self, movie_id, title, release_date, genre, runtime, poster_path):
        self.movie_id = movie_id
        self.title = title
        self.release_date = release_date
        self.genre = genre
        self.runtime = runtime
        self.poster_path = poster_path


class Entry(db.Model):
    """User log of movies and tv episodes watched."""

    __tablename__ = "entries"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)

    user = db.relationship('User')

    # def __init__(self, date):
    #     self.date = date
