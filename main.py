from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import json

# Load configuration data
config_path = 'config.json'
with open(config_path) as config_file:
    config = json.load(config_file)

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie-collection.db'
db = SQLAlchemy(app)
API_KEY = config["API_KEY"]

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

#CREATE EDIT FORM
class AddForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Done")

@app.route("/")
def home():
    global all_movies
    all_movies = db.session.query(Movie).all()
    return render_template("index.html", movies=all_movies)

@app.route("/add", methods={"GET", "POST"})
def add():
    form = AddForm()
    if form.validate_on_submit():
        title = form.title.data
        url=f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={title}&include_adult=false"
        print(url)
        response = requests.get(url=url).json()["results"]
        print(response)
        return render_template("select.html", movies=response)
    return render_template("add.html", form=form)

@app.route("/select", methods={"GET", "POST"})
def select():
    url = f"https://api.themoviedb.org/3/movie/{request.args.get('id')}?api_key={API_KEY}&language=en-US"
    movie = requests.get(url=url).json()
    title = movie["original_title"]
    year = movie["release_date"][:3]
    description = movie["overview"]
    rating = movie["vote_average"]
    ranking = 0
    review= "None"
    img_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
    createRecord(title,year, description, rating, ranking, review, img_url)
    created_record = Movie.query.filter_by(title=title).first()
    return redirect(url_for('edit', num=created_record.id))

@app.route("/edit", methods={"GET", "POST"})
def edit():
    num = request.args.get("num")
    movie_to_edit = Movie.query.get(num)
    form = EditForm()
    if form.validate_on_submit():
        movie_to_edit.rating = float(form.rating.data)
        movie_to_edit.review = form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", form=form, movie= movie_to_edit)

@app.route("/delete", methods={"GET", "POST"})
def delete():
    num = request.args.get("num")
    movie_to_delete = Movie.query.get(num)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
