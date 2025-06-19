#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_cors import CORS # Added CORS import

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' # Changed to app.db for consistency
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app) # Initialize CORS
migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class Home(Resource):
    def get(self):
        response_dict = {
            "message": "Welcome to the Plant Store RESTful API!",
        }
        return make_response(response_dict, 200)

api.add_resource(Home, '/')

class Plants(Resource):
    def get(self):
        plants_list = Plant.query.all()
        plants_data = [plant.to_dict() for plant in plants_list]
        return make_response(jsonify(plants_data), 200)

    def post(self):
        data = request.get_json()
        if not data:
            return make_response(jsonify({"errors": ["No data provided"]}), 400)

        name = data.get('name')
        image = data.get('image')
        price = data.get('price')
        is_in_stock = data.get('is_in_stock', True) # Default to True if not provided

        if not all([name, image, price is not None]):
            return make_response(jsonify({"errors": ["Missing required fields: name, image, price"]}), 400)
        
        if not isinstance(name, str) or not isinstance(image, str) or not isinstance(price, (int, float)) or not isinstance(is_in_stock, bool):
            return make_response(jsonify({"errors": ["Invalid data types for name, image, price, or is_in_stock"]}), 400)

        try:
            new_plant = Plant(name=name, image=image, price=price, is_in_stock=is_in_stock)
            db.session.add(new_plant)
            db.session.commit()
            return make_response(jsonify(new_plant.to_dict()), 201)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 400)

api.add_resource(Plants, '/plants')

class PlantByID(Resource):
    def get(self, id):
        plant = Plant.query.filter_by(id=id).first()
        if plant:
            return make_response(jsonify(plant.to_dict()), 200)
        else:
            return make_response(jsonify({"error": "Plant not found"}), 404)

    def patch(self, id):
        plant = Plant.query.filter_by(id=id).first()
        if not plant:
            return make_response(jsonify({"error": "Plant not found"}), 404)

        data = request.get_json()
        if not data:
            return make_response(jsonify({"errors": ["No data provided for update"]}), 400)

        try:
            for key, value in data.items():
                if hasattr(plant, key) and key != 'id': # Prevent updating the ID
                    setattr(plant, key, value)
            db.session.commit()
            return make_response(jsonify(plant.to_dict()), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 400)

    def delete(self, id):
        plant = Plant.query.filter_by(id=id).first()
        if not plant:
            return make_response(jsonify({"error": "Plant not found"}), 404)
        
        try:
            db.session.delete(plant)
            db.session.commit()
            return make_response('', 204) # 204 No Content for successful deletion
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 500)

api.add_resource(PlantByID, '/plants/<int:id>')
     
if __name__ == '__main__':
    app.run(port=5555, debug=True)
