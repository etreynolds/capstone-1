from flask import Flask, redirect, render_template, flash, session, g, request
import requests
from flask_debugtoolbar import DebugToolbarExtension
from api import API_SECRET_KEY
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import exists
from models import db, connect_db, User, Entry, Movie
from forms import UserAddForm, LoginForm, AddEntryForm
from datetime import datetime

CURR_USER_KEY = "curr_user"

API_BASE_URL = "https://api.themoviedb.org/3"
API_POSTER_URL = "https://image.tmdb.org/t/p/w185"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///media_memoir'
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


@app.route("/movie", methods=["GET", "POST"])
def get_movie_info():
    """Return page about movie."""

    movie = request.args["movie"]

    res1 = requests.get(f"{API_BASE_URL}/search/movie",
                        params={'api_key': API_SECRET_KEY,
                                'query': movie})

    data1 = res1.json()
    movie_id = data1["results"][0]['id']
    title = data1["results"][0]['title']
    release_date = datetime_obj = datetime.strptime(
        (data1["results"][0]['release_date']), '%Y-%m-%d')
    user_score = data1["results"][0]['vote_average']
    poster_path = data1["results"][0]['poster_path']
    poster_url = f"{API_POSTER_URL}{poster_path}"

    res2 = requests.get(f"{API_BASE_URL}/movie/{movie_id}",
                        params={'api_key': API_SECRET_KEY,
                                'movie_id': movie_id})

    data2 = res2.json()
    runtime = data2['runtime']
    genre = data2['genres'][0]['name']

    # Function to convert runtime minutes into 'hour minutes'
    # example: 129 minutes will show as '2h 9m'
    def convert(min):
        min = min % (24 * 1440)
        hour = min // 1440
        min %= 1440
        hour = min // 60
        min %= 60
        return (f"{hour}h {min}m")

    formatted_runtime = convert(runtime)

    movie_info = {"title": title,
                  "formatted_runtime": formatted_runtime,
                  "release_date": release_date,
                  "genre": genre,
                  "poster_url": poster_url,
                  "user_score": user_score}

    form = AddEntryForm()

    # Check to see if movie exists in db. if not, add it.
    exists = db.session.query(db.exists().where(
        Movie.movie_id == movie_id)).scalar()

    if exists:
        print("******************")
        print("Already in DB")

        if form.validate_on_submit():
            date = form.date.data
            entry = Entry(date=date)
            db.session.add(entry)
            db.session.commit()
            flash("Entry logged.", "success")
            return redirect('/')
        else:
            return render_template('home.html', movie_info=movie_info, form=form)

    else:
        movie_to_db = Movie(movie_id, title, release_date, genre,
                            runtime, poster_path)
        db.session.add(movie_to_db)
        db.session.commit()
        print("********************")
        print("Added to DB")

        if form.validate_on_submit():
            date = form.date.data
            entry = Entry(date=date)
            db.session.add(entry)
            db.session.commit()
            flash("Entry logged.", "success")
            return redirect('/')
        else:
            return render_template('home.html', movie_info=movie_info, form=form)


# @app.route("/show")
# def get_show_info():
#     """Return page about show."""

#     show = request.args["show"]

#     res = requests.get(f"{API_BASE_URL}/search/tv",
#                        params={'api_key': API_SECRET_KEY,
#                                'query': show})

#     data = res.json()
#     title = data["results"][0]['name']
#     first_air_date = datetime_obj = datetime.strptime(
#         (data["results"][0]['first_air_date']), '%Y-%m-%d')
#     user_score = data["results"][0]['vote_average']
#     poster_path = data["results"][0]['poster_path']
#     poster_url = f"{API_POSTER_URL}{poster_path}"

#     show_info = {"title": title,
#                  "first_air_date": first_air_date,
#                  "poster_url": poster_url,
#                  "user_score": user_score}

#     return render_template('home.html', show_info=show_info)


##############################################################################
# Entries routes

@app.route("/add-entry", methods=["GET", "POST"])
def add_entry():
    """Add an entry. Show form if GET."""

    if not g.user:
        flash("Must be signed in!", "danger")
        return redirect("/")

    user = g.user
    form = AddEntryForm()

    if form.validate_on_submit():
        user_id = user.id
        date = form.date.data
        entry = Entry(date=date, user_id=user_id)
        db.session.add(entry)
        db.session.commit()
        flash(f"Added movie entry for {date}", "success")
        return redirect("/add-entry")

    return render_template('add-entry.html', form=form)

# @app.route("/add-entry", methods=["POST"])
# def add_entry():
#     """Handle adding entries."""
#     if request.method == 'POST':
#         date = request.form['date']
#         entry = Entry(date=date)
#         db.session.add(entry)
#         db.session.commit()
#         flash("Entry logged.", "success")
#         return redirect("/")
#     else:
#         return render_template("home.html")
##############################################################################
# Summary routes


@app.route("/summary")
def show_user_summary():
    """Show summary of user's entries."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    # user = User.query.get_or_404(user_id)

    users = User.query.all()

    return render_template('summary.html', users=users)


@app.route("/user/<int:user_id>/summary")
def show_user(user_id):
    """Show details about user."""
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('summary.html', user=user)
