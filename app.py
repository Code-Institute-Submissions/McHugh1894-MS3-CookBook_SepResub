# Import files
import os
from flask import Flask, flash, render_template, redirect, request, session, url_for
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
ADMIN_USER = "admin@gmail.com"
mongo = PyMongo(app)


# Home Page


@app.route("/")
@app.route("/home")
def home():
    is_logged_in = True if "username" in session else False
    return render_template("home.html", is_logged_in=is_logged_in)


# Recipes Page
@app.route("/recipes")
def recipe():
    category = request.args.get("categories")
    recipes = []
    if category and category != "All":
        recipes = list(mongo.db.recipes.find({"recipe_category": category}))
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
            {"username": request.form.get("username").lower()}
        )
        if existing_user:
            if check_password_hash(
                existing_user["password"], request.form.get("password")
            ):
                session["user"] = request.form.get("username").lower()
                return redirect(url_for("mypage", username=session["user"]))
            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))
    return render_template("users/login.html")


# Profile
@app.route("/profile", methods=["GET", "POST"])
def mypage():
    if not session.get("user"):
        return render_template("error_handlers/404.html")
    username = mongo.db.users.find_one({"username": session["user"]})["username"]
    if session["user"]:
        if session["user"] == ADMIN_USER:
            user_recipes = list(mongo.db.recipes.find())
        else:
            user_recipes = list(mongo.db.recipes.find({"username": session["user"]}))
        return render_template(
            "users/mypage.html", username=username, user_recipes=user_recipes
        )
    return redirect(url_for("login"))


# Logout
@app.route("/logout")
def logout():
    """Remove user from session cookie"""
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


# Contact Page
@app.route("/contact")
def contact():
    return render_template("users/contact.html")


# Recipes Description
@app.route("/recipes/<recipe_id>/view")
def recipes(recipe_id):
    try:
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        if not recipe:
            return render_template("error_handlers/404.html")
        return render_template("recipe/recipe-info.html", recipes=recipe)
    except:
        return render_template("error_handlers/404.html")


# Add New Recipe To DB
@app.route("/recipe/add", methods=["GET", "POST"])
def add_recipe():
    if not session.get("user"):
        return render_template("error_handlers/404.html")
    if request.method == "POST":
        recipe = {
            "category_name": request.form.get("category_name"),
            "recipe_name": request.form.get("recipe_name"),
            "chef": request.form.get("chef"),
            "image": request.form.get("image"),
            "serving": request.form.get("serving"),
            "prep_time": request.form.get("prep_time"),
            "cook_time": request.form.get("cook_time"),
            "total_time": request.form.get("total_time"),
            "ingredients": request.form.get("ingredients"),
            "directions": request.form.get("directions"),
                        
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe is successfully added")
        return redirect(url_for("mypage", username=session["user"]))
    categories = list(mongo.db.recipe_categories.find())
    return render_template("recipe/add_recipe.html", categories=categories)


# Edit Recipe From DB
@app.route("/recipe/<recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if not session.get("user"):
        return render_template("error_handlers/404.html")
    if request.method == "POST":
        submit = {
            "category_name": request.form.get("category_name"),
            "recipe_name": request.form.get("recipe_name"),
            "chef": request.form.get("chef"),
            "image": request.form.get("image"),
            "serving": request.form.get("serving"),
            "prep_time": request.form.get("prep_time"),
            "cook_time": request.form.get("cook_time"),
            "total_time": request.form.get("total_time"),
            "ingredients": request.form.get("ingredients"),
            "directions": request.form.get("directions"),
            
        }
        mongo.db.recipes.update({"_id": ObjectId(recipe_id)}, submit)
        flash("Recipe Successfully Updated")
        return redirect(url_for("mypage", username=session["user"]))
    try:
        recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
        categories = mongo.db.categories.find().sort("category_name", 1)
        return render_template(
            "recipe/edit_recipe.html", recipe=recipe, categories=categories
        )
    except:
        return render_template("error_handlers/404.html")
        

# Show 404 page


# Delete Recipe From DB
@app.route("/recipe/<recipe_id>/delete")
def delete_recipe(recipe_id):
    # Fetch recipe and check if it exists, if recipe doesn't exist, throw some error, else proceed
    mongo.db.recipes.remove({"_id": ObjectId(recipe_id)})
    flash("Recipe Successfully Deleted")
    return redirect(url_for("mypage"))


def is_user_admin():
    if not session.get("user") == "admin@gmail.com":
        return True
    else:
        return False


# Get Category from DB
@app.route("/categories")
def get_categories():
    if is_user_admin():
        return render_template("category/categories.html")
    categories = list(mongo.db.recipe_categories.find())
    return render_template("category/categories.html", categories=categories)


# Add Category to DB
@app.route("/category/add", methods=["GET", "POST"])
def add_category():
    if is_user_admin():
        return render_template("error_handlers/403.html")
    if request.method == "POST":
        category = {"category_name": request.form.get("category_name")}
        mongo.db.recipe_categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("get_categories"))
    return render_template("category/add_category.html")


# Edit Category from DB
@app.route("/category/<category_id>/edit", methods=["GET", "POST"])
def edit_category(category_id):
    if is_user_admin():
        return render_template("category/categories.html")
    if request.method == "POST":
        submit = {"category_name": request.form.get("category_name")}
        mongo.db.recipe_categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category Successfully Updated")
        return redirect(url_for("get_categories"))
    category = mongo.db.recipe_categories.find_one({"_id": ObjectId(category_id)})
    return render_template("category/edit_category.html", category=category)


# Delete Category from DB
@app.route("/category/<category_id>/delete")
def delete_category(category_id):
    if is_user_admin():
        return render_template("error_handlers/403.html")
    mongo.db.recipe_categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("get_categories"))


# Subscribe Newsletter
@app.route("/newsletter", methods=["GET", "POST"])
def newsletter():
    if request.method == "POST":
        existing_user = mongo.db.newsletter.find_one(
            {"email_id": request.form.get("email_id").lower()}
        )
        if existing_user:
            flash("Already Subscribed")
            return redirect(url_for("contact"))
        newsletter = {"email_id": request.form.get("email_id").lower()}
        flash("Successfully subscribed")
        mongo.db.newsletter.insert_one(newsletter)
    return render_template("users/contact.html")


# App Run
if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), port=int(os.environ.get("PORT")), 
    debug=False)




