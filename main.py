from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie-collection.db'
db = SQLAlchemy(app)

##CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    ranking = db.Column(db.Integer,nullable=False)
    review = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String, nullable=False)

    #Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'<Book {self.title}>'

db.create_all()

all_movies = db.session.query(Movie).all()

def createRecord(title, year, description,rating,ranking, review, img_url):
    new_movie = Movie(title=title, year=year, description=description, rating=rating, ranking=ranking, review=review, img_url=img_url)
    db.session.add(new_movie)
    db.session.commit()

#CREATE EDIT FORM
class EditForm(FlaskForm):
    rating = StringField("Your Rating out of 10 e.g 7.5", validators=[DataRequired()])
    review = StringField("Your Review", validators=[DataRequired()])
    submit = SubmitField("Done")

@app.route("/")
def home():
    global all_movies
    all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=all_movies)

@app.route("/edit/<num>")
def edit(num):
    global all_movies
    movie_to_edit = Movie.query.get(num)
    form = EditForm()
    if form.validate_on_submit():
        movie_to_edit.rating = form.rating
        movie_to_edit.review = form.review
        db.session.commit()
        all_movies = db.session.query(Movie).all()
        return redirect("home")
    return render_template("edit.html", form=form)

if __name__ == '__main__':
    app.run(debug=True)
