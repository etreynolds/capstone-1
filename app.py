from flask import Flask, redirect, render_template, flash, session, g, request, url_for, abort
import requests
import pdb
from flask_debugtoolbar import DebugToolbarExtension
from api import API_SECRET_KEY
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import exists, func
from models import db, connect_db, User, Entry, Movie
from forms import UserAddForm, LoginForm, AddEntryForm
from datetime import datetime
import os
# from collections.abc import Container, Iterable, MutableSet

CURR_USER_KEY = "curr_user"

API_BASE_URL = "https://api.themoviedb.org/3"
API_POSTER_URL = "https://image.tmdb.org/t/p/w185"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgres:///media_memoir')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'keepitsecret')
print(app.config['SECRET_KEY'])

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
db.create_all()

debug = DebugToolbarExtension(app)


# Function to convert runtime minutes into 'hour minutes'
# example: 129 minutes will show as '2h 9m'
def convert(min):
    min = min % (24 * 1440)
    hour = min // 1440
    min %= 1440
    hour = min // 60
    min %= 60
    return (f"{hour}h {min}m")


@app.template_filter('datetimeformat')
def datetimeformat(value, format='%B'):
    return value.strftime(format)


@app.route("/")
def homepage():
    """Homepage."""

    session['count'] = session.get('count', 0) + 1

    if g.user:
        return render_template('home.html')

    else:
        return redirect('/signup')

##############################################################################
# User signup/login/logout routes


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
                name=form.name.data,
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

def search_movie(movie):
    res = requests.get(f"{API_BASE_URL}/search/movie",
                       params={'api_key': API_SECRET_KEY,
                               'query': movie})
    return res.json()["results"]


def get_movie_details(id):
    res = requests.get(f"{API_BASE_URL}/movie/{id}",
                       params={'api_key': API_SECRET_KEY,
                               'movie_id': id})
    return res.json()


@app.route("/movie", methods=["GET"])
def get_movie_info():
    """Return page about movie."""

    movie = request.args["movie"]

    data = search_movie(movie)

    movie_list = []

    # if searched movie doesn't exist, show 404 page
    for data1 in data[0:5]:
        try:
            id = data1['id']
        except (IndexError, KeyError):
            abort(404)

        title = data1['title']
        release_date = datetime_obj = datetime.strptime(
            (data1['release_date']), '%Y-%m-%d')
        user_score = data1['vote_average']
        poster_path = data1['poster_path']
        poster_url = f"{API_POSTER_URL}{poster_path}"

        data2 = get_movie_details(id)
        runtime = data2['runtime']
        if len(data2['genres']) > 0:
            genre = data2['genres'][0]['name']

        tagline = data2['tagline']

        formatted_runtime = convert(runtime)

        movie_info = {"title": title,
                      "id": id,
                      "formatted_runtime": formatted_runtime,
                      "release_date": release_date,
                      "genre": genre,
                      "poster_url": poster_url,
                      "user_score": user_score,
                      "tagline": tagline}

        movie_list.append(movie_info)

        # Check to see if movie exists in db. if not, add it.
        exists = db.session.query(db.exists().where(Movie.id == id)).scalar()

        if not exists:
            movie_to_db = Movie(id, title, release_date, genre,
                                runtime, poster_path, user_score)
            db.session.add(movie_to_db)
            db.session.commit()

    form = AddEntryForm()

    # if exists:
    #     return render_template('home.html', movie_info=movie_info, form=form)

    # else:
    #     movie_to_db = Movie(id, title, release_date, genre,
    #                         runtime, poster_path, user_score)
    #     db.session.add(movie_to_db)
    #     db.session.commit()

    return render_template('home.html', movie_list=movie_list, form=form)


##############################################################################
# Entries routes

@app.route("/add-entry", methods=["GET", "POST"])
def add_entry():
    """Add an entry. Show form if GET."""

    if not g.user:
        flash("Must be signed in!", "danger")
        return redirect("/")

    form = AddEntryForm()

    if form.validate_on_submit():
        user_id = g.user.id
        date = form.date.data
        movie_id = form.movie_id.data
        rating = request.form.get('rating')
        entry = Entry(date=date, user_id=user_id,
                      movie_id=movie_id, rating=rating)
        db.session.add(entry)
        db.session.commit()
        flash(f"Added movie entry for {date}", "success")
        return redirect(url_for('show_user_summary', user_id=user_id))

    else:
        return render_template('home.html', form=form)


##############################################################################
# Summary routes

@app.route("/user/<int:user_id>/summary")
def show_user_summary(user_id):
    """Show details about user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    if user != g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    entries = (db.session.query(Entry.id, Entry.date, Entry.rating, Movie.title, Movie.runtime, Movie.genre, Movie.user_score)
               .order_by(Entry.date.desc())
               .filter(Entry.user_id == g.user.id)
               .join(Movie)
               .all())

    movie_count = (db.session.query(Entry.user_id)
                   .filter(Entry.user_id == g.user.id)
                   .count())

    total_watch_time = (db.session.query(db.func.sum(Movie.runtime))
                        .join(Entry, Entry.movie_id == Movie.id)
                        .filter(Entry.user_id == g.user.id)
                        .group_by(Entry.user_id).scalar())

    formatted_watch_time = convert(total_watch_time)

    return render_template('summary.html', user=user, entries=entries, movie_count=movie_count, formatted_watch_time=formatted_watch_time)


@app.route("/summary/<int:entry_id>/delete", methods=["POST"])
def delete_entry(entry_id):
    """Delete entry when X clicked on summary page."""

    entry = Entry.query.get_or_404(entry_id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(f"/user/{g.user.id}/summary")


##############################################################################
# Error routes

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


##############################################################################
# Test routes
