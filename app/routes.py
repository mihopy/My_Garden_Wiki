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
    if request.method == "POST":
        query = request.form.get("query")
        plants = Plant.query.filter(Plant.common_name.ilike(f"%{query}%")).all()
        if not plants:
            return "Plant Not Found", 404
        return render_template("index.html", saved_plants=plants)

    #     url = f"{API_URL}?key={PLANT_API_KEY}&q={urllib.parse.quote(query)}"
    #     response = requests.get(url)
    #     pprint.pprint(response.status_code)
    #     if response.status_code == 200:
    #         plants = response.json().get('data', [])
    #         pprint.pprint(response.json())
    plants_data = Plant.query.all()
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
    existing_plant = Plant.query.get(plant_id)
    if existing_plant:
        return render_template("index.html", saved_plants=[existing_plant])

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
        return render_template('index.html', saved_plants=[new_plant])

    return "Plant Not Found", 404


@main.route("/saved_plants")
def show_saved_plants():
    plants = Plant.query.all()  # Fetch all data from DB
    return render_template('plant_details.html', plants=plants)


@main.route('/spring')
def spring():
    plants = Plant.query.all()
    spring_plants = [plant for plant in plants if plant.flowering_season == 'Spring']
    return render_template('spring.html', saved_plants=spring_plants)


@main.route('/summer')
def summer():
    plants = Plant.query.all()
    summer_plants = [plant for plant in plants if plant.flowering_season == 'Summer']
    return render_template('summer.html', saved_plants=summer_plants)


@main.route('/autumn')
def autumn():
    plants = Plant.query.all()
    autumn_plants = [plant for plant in plants if plant.flowering_season == 'Autumn']
    return render_template('autumn.html', saved_plants=autumn_plants)


@main.route('/winter')
def winter():
    plants = Plant.query.all()
    winter_plants = [plant for plant in plants if plant.flowering_season == 'Winter']
    return render_template('winter.html', saved_plants=winter_plants)
