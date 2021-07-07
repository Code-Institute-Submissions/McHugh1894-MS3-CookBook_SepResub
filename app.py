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


