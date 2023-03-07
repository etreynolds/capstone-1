from flask import Flask, redirect, render_template, flash, session, g, request
import requests
from flask_debugtoolbar import DebugToolbarExtension
from api import API_SECRET_KEY
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User
from forms import UserAddForm, LoginForm
from datetime import datetime

CURR_USER_KEY = "curr_user"

API_BASE_URL = "https://api.themoviedb.org/3"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///media-memoir'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "keepitsecret"

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

debug = DebugToolbarExtension(app)


@app.template_filter('datetimeformat')
def datetimeformat(value, format='%B'):
    return value.strftime(format)


@app.route("/")
def homepage():
    """Homepage."""

    if g.user:
        return render_template('home.html')

    else:
        return redirect('/signup')

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If logged in add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Log out user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.
    Create new user and add to DB. Redirect to homepage.
    If form not valid, present form.
    If username already exists, flash message and present form again.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                email=form.email.data,
                username=form.username.data,
                password=form.password.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template('/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template("/signup.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", "danger")

    return render_template('/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle user log out."""

    do_logout()

    flash("You have logged out.", "success")
    return redirect("/login")


##############################################################################
# API routes


def request_movie(movie):
    """Return movie info from API."""

    res = requests.get(f"{API_BASE_URL}/movie",
                       params={'api_key': API_SECRET_KEY,
                               'query': movie})

    data = res.json()

    for result in data['results']:
        print(result['original_title'])
        print(result['release_date'])

    # print(data['results'][0])


@app.route("/movie")
def get_movie_info():
    """Return page about movie."""

    movie = request.args["movie"]

    res = requests.get(f"{API_BASE_URL}/search/movie",
                       params={'api_key': API_SECRET_KEY,
                               'query': movie})

    data = res.json()
    title = data["results"][0]['title']
    id = data["results"][0]['id']
    release_date = datetime_obj = datetime.strptime(
        (data["results"][0]['release_date']), '%Y-%m-%d')
    user_score = data["results"][0]['vote_average']
    poster_path = data["results"][0]['poster_path']
    poster_url = f"https://image.tmdb.org/t/p/w300{poster_path}"

    movie_info = {"title": title,
                  "release_date": release_date, "poster_url": poster_url, "user_score": user_score}

    return render_template('home.html', movie_info=movie_info)


@app.route("/show")
def get_show_info():
    """Return page about show."""

    show = request.args["show"]

    res = requests.get(f"{API_BASE_URL}/search/tv",
                       params={'api_key': API_SECRET_KEY,
                               'query': show})

    data = res.json()
    title = data["results"][0]['name']
    id = data["results"][0]['id']
    first_air_date = datetime_obj = datetime.strptime(
        (data["results"][0]['first_air_date']), '%Y-%m-%d')
    user_score = data["results"][0]['vote_average']
    poster_path = data["results"][0]['poster_path']
    poster_url = f"https://image.tmdb.org/t/p/w300{poster_path}"

    show_info = {"title": title,
                 "first_air_date": first_air_date, "poster_url": poster_url, "user_score": user_score}

    return render_template('home.html', show_info=show_info)
