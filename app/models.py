from . import db


class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    common_name = db.Column(db.String(100), nullable=False)
    scientific_name = db.Column(db.String(150))
    pruning_month = db.Column(db.String(300))
    pruning_count = db.Column(db.String(200))
    flowering_season = db.Column(db.String(300))
    cycle = db.Column(db.String(100))
    plant_image = db.Column(db.String(500))
    