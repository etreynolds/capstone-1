from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):
    """User model."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)

    # entries = db.relationship('Entry')

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, password, email):
        """Sign up user. Hashes password and adds user to system."""

        hashed_pw = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username, email=email, password=hashed_pw)

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
    runtime = db.Column(db.Integer)
    poster_path = db.Column(db.Text)

    def __init__(self, movie_id, title, release_date, runtime, poster_path):
        self.movie_id = movie_id
        self.title = title
        self.release_date = release_date
        self.runtime = runtime
        self.poster_path = poster_path


class TV(db.Model):
    """TV show model."""

    __tablename__ = "shows"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)


class Entry(db.Model):
    """User log of movies and tv episodes watched."""

    __tablename__ = "entries"

    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey(
    #     'users.id'), nullable=False)
    media_type = db.Column(db.Text, nullable=False)
    media_name = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    # movie_theater = db.Column(db.Text, default=False)
    # movie_with_people = db.Column(db.Text, default=False)
    # movie_new = db.Column(db.Text, default=False)
    # tv_episodes = db.Column(db.Integer)

    # user = db.relationship('User')

    def __init__(self, media_type, media_name, date):
        self.date = date
        self.media_type = media_type
        self.media_name = media_name
        # self.movie_theater = movie_theater
        # self.movie_with_people = movie_with_people
        # self.movie_new = movie_new
        # self.tv_episodes = tv_episodes
