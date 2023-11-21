#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods = ['GET', 'POST'])
def route_campers():
    if request.method =='GET':
        campers = [
            camper.to_dict()
            for camper
            in Camper.query.all()
        ]
        return make_response(campers, 200)
    
    if request.method == 'POST':
        params = request.json
        if not params["name"] or not params ["age"]:
            return make_response({'errors': ["validation errors"]}, 400)
        if params["age"] < 8 or params["age"] > 18:
            return make_response({'errors': ["validation errors"]}, 400)
        
        new_camper = Camper(name = params['name'],
                            age = params['age'])
        db.session.add(new_camper)
        db.session.commit()
        
        camper_dict = {'id': new_camper.id, 
                       'name': new_camper.name, 
                       'age': new_camper.age}
        
        return make_response(camper_dict, 201)
        
@app.route('/campers/<int:id>', methods = ['GET', 'PATCH', 'DELETE'])
def route_campers_by_id(id):
    camper = Camper.query.get(id)
    if not camper:
        return make_response({'error': "Camper not found"}, 404)
    
    if request.method == 'GET':
        return make_response(camper.to_dict(rules=('signups', 'activities')), 200)
    
    if request.method == 'PATCH':
        params = request.json
        if not params["name"] or not params ["age"]:
            return make_response({'errors':["validation errors"]}, 400)
        if params["age"] < 8 or params["age"] > 18:
            return make_response({'errors': ["validation errors"]}, 400)
        
        for attr in params:
            setattr(camper, attr, params[attr])
        db.session.commit()
        return make_response(camper.to_dict(), 202)
    
    
    
@app.route('/activities')
def route_activities():
    activities = Activity.query.all()
    return make_response([activity.to_dict() for activity in activities], 200)

@app.route('/activities/<int:id>', methods=["DELETE"])
def route_delete_activities(id):
    if request.method == 'DELETE':
        activity = Activity.query.get(id)
        if not activity:
            return make_response({
                "error": "Activity not found"
                }, 404)
        db.session.delete(activity)
        db.session.commit()
        return make_response({}, 204)
    return make_response({}, 200)

@app.route('/signups', methods=['POST'])
def route_signup():
    params = request.json
    if not params["camper_id"] or not params ['activity_id'] or not params ['time']:
        return make_response(
            {"errors": ["validation errors"]}, 400)
    if params["time"] < 0 and params["time"] > 23:
        return make_response(
            {"errors": ["validation errors"]}, 400)
    try:
        signup = Signup(
            camper_id = params["camper_id"],
            activity_id = params["activity_id"],
            time = params["time"]
        )
    except:
        return make_response(
            {"errors": ["validation errors"]}, 400)    
    
    db.session.add(signup)
    db.session.commit()
    return make_response(signup.to_dict(rules=('activity', 'camper')), 201)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
