# Media Memoir

<font size="4">**_Media Memoir_**</font> is an application that allows users to register, login, keep a log of the movies they watch, see information about the movies they watch, and view watch summaries and statistics.

Check out [Media Memoir](https://media-memoir.herokuapp.com/)!

## Features

### Movie Search

Users can quickly search for any movie and cards will appear showing the top 5 results. Information included for each movie is **runtime**, **release date**, **genre(s)**, and **TMDB user score**.

### Watched Movie

Registered users will be able to log a movie they've watched by searching for a movie and selecting a date in the _**Date Watched**_ field of the movie card.

### Summary

Users can visit the **Summary** page to see a quick snapshot of all movies they've marked as *watched*.

## User Flow

![User Flow](/proposal/user-flow.png "User Flow")

## Database



![DB Schema](/proposal/db-schema.png "DB Schema")

## API

<a href="https://www.themoviedb.org/documentation/api">
  <img src="https://www.themoviedb.org/assets/2/v4/logos/v2/blue_short-8e7b30f73a4020692ccca9c88bafe5dcb6f8a62a4c6bc55cd9ba82bb2cd95f6c.svg" width="40%" />
</a>

TMDB API provides a wealth of information and data points on movies that are utilized.

## Tech Stack

HTML, CSS, JavaScript, Jinja, Python, Flask, PostgreSQL, SQLAlchemy