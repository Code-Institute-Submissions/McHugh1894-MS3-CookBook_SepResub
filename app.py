# Import files
import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env
app = Flask(__name__)

# Configuration
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")
ADMIN_USER =  "admin@gmail.com"
mongo = PyMongo(app)
"""
checks if user is logged in. 
if not logged in displays flash 
message. 
"""


# Home Page
@app.route('/')
@app.route('/home')
def home():
    is_logged_in = True if 'username' in session else False    
    return render_template('home.html', is_logged_in=is_logged_in)


# Recipes Page
@app.route("/recipes")
def recipe():
    category = request.args.get("category")
    recipes = []
    if category: 
        recipes = list(mongo.db.recipes.find({"recipe_category":category}))
    else:
        recipes = list(mongo.db.recipes.find())
    return render_template("recipes.html", recipes=recipes)


# Search Recipe
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    recipes = list(mongo.db.recipes.find({"$text": {"$search": query}}))
    return render_template("recipe/recipe.html", recipes=recipes)


# User SignUp
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("signup"))
        signup = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(signup)
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("mypage", username=session["user"]))
    return render_template("users/signup.html")


# Users Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                return redirect(url_for(
                    "mypage", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))
    return render_template("users/login.html")    


# App Run
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)


