from flask import Blueprint, render_template, request, redirect, url_for
from .models import Plant
import os
import urllib.parse
from dotenv import load_dotenv
import requests
import pprint
from . import db

load_dotenv()
PLANT_API_KEY = os.getenv("PLANT_API_KEY")
API_URL = "https://perenual.com/api/v2/species-list"


# Define routes on it, like @main.route("/")
# Register it in __init__.py with app.register_blueprint(main)
main = Blueprint('main', __name__)


@main.route("/", methods=["GET", "POST"])
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 8

    if request.method == "POST":
        query = request.form.get("query")
        plants = Plant.query.filter(Plant.common_name.ilike(f"%{query}%")).paginate(page=page, per_page=per_page)
        if not plants.items:
            return "Plant Not Found", 404
        return render_template("index.html", saved_plants=plants)

    plants_data = Plant.query.paginate(page=page, per_page=per_page)
    return render_template("index.html", saved_plants=plants_data)


@main.route("/plant/<int:plant_id>", methods=["GET", "POST"])
def plant_details(plant_id):
    existing_plant = Plant.query.get(plant_id)
    if existing_plant:
        return render_template("plant_details.html", plant=existing_plant)


@main.route("/search_new_plant", methods=["GET"])
def search_new_plant():
    return render_template("search_new_plant.html")


@main.route("/select_new_plant", methods=["POST"])
def select_new_plant():
    new_plant_query = request.form.get('new_plant_name')
    url = f"{API_URL}?key={PLANT_API_KEY}&q={urllib.parse.quote(new_plant_query)}"
    response = requests.get(url)
    if response.status_code == 200:
        new_plants = response.json().get('data', [])
        return render_template("select_new_plant.html", new_plants=new_plants)
    else:
        return "Plant Not Found from API", 404


@main.route("/add/<int:plant_id>", methods=["GET", "POST"])
def add_plant(plant_id):
    page = request.args.get('page', 1, type=int)
    per_page = 8

    existing_plant = Plant.query.get(plant_id)
    if existing_plant:
        # Simulate a paginated object with a single item
        pagination = Plant.query.filter(Plant.id == plant_id).paginate(page=page, per_page=per_page)
        return render_template("index.html", saved_plants=pagination)

    plant_details_url = f"https://perenual.com/api/v2/species/details/{plant_id}?key={PLANT_API_KEY}"
    response = requests.get(plant_details_url)

    if response.status_code == 200:
        data = response.json()

        new_plant = Plant(
            id=data.get("id"),
            common_name=data.get("common_name", "Unknown"),
            scientific_name=", ".join(data.get("scientific_name", ["Unknown"])),
            pruning_month=", ".join(data.get("pruning_month", [])),
            pruning_count=(
                {} if isinstance(data.get("pruning_count", {}), list) else data.get("pruning_count", {})).get("amount",
                                                                                                              "N/A"),
            flowering_season=data.get("flowering_season"),
            cycle=data.get("cycle", "N/A"),
            plant_image=data.get("default_image").get("medium_url", "")
        )
        db.session.add(new_plant)
        db.session.commit()
        # Get the updated pagination after adding
        pagination = Plant.query.paginate(page=page, per_page=per_page)
        return render_template('index.html', saved_plants=pagination)

    return "Plant Not Found", 404


@main.route("/delete/<int:plant_id>", methods=['POST'])
def delete_plant(plant_id):
    plant_to_delete = db.get_or_404(Plant, plant_id)
    db.session.delete(plant_to_delete)
    db.session.commit()
    return redirect(url_for('main.index'))


@main.route("/saved_plants")
def show_saved_plants():
    plants = Plant.query.all()  # Fetch all data from DB
    return render_template('plant_details.html', plants=plants)


@main.route('/spring')
def spring():
    page = request.args.get('page', 1, type=int)
    per_page = 8
    spring_query = Plant.query.filter(Plant.flowering_season == 'Spring')
    spring_plants = spring_query.paginate(page=page, per_page=per_page)
    return render_template('spring.html', saved_plants=spring_plants)


@main.route('/summer')
def summer():
    page = request.args.get('page', 1, type=int)
    per_page = 8
    summer_query = Plant.query.filter(Plant.flowering_season == 'Summer')
    summer_plants = summer_query.paginate(page=page, per_page=per_page)
    return render_template('summer.html', saved_plants=summer_plants)


@main.route('/autumn')
def autumn():
    page = request.args.get('page', 1, type=int)
    per_page = 8
    autumn_query = Plant.query.filter(Plant.flowering_season == 'Autumn')
    autumn_plants = autumn_query.paginate(page=page, per_page=per_page)
    return render_template('autumn.html', saved_plants=autumn_plants)


@main.route('/winter')
def winter():
    page = request.args.get('page', 1, type=int)
    per_page = 8
    winter_query = Plant.query.filter(Plant.flowering_season == 'Winter')
    winter_plants = winter_query.paginate(page=page, per_page=per_page)
    return render_template('winter.html', saved_plants=winter_plants)
