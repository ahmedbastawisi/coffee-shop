import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def get_drinks():
    try:
        drinks = Drink.query.all()
        drinks_json = [drink.short() for drink in drinks]
        return jsonify({
            'success': True,
            'drinks': drinks_json
        })
    except:
        abort(422)


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    try:
        drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        })
    except:
        abort(422)


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drink():
    body = request.get_json()

    try:
        drink = Drink(title=body['title'], recipe=json.dumps(body['recipe']))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(drink_id):
    body = request.get_json()

    try:
        drink = Drink.query.filter(
            Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        if('title' in body):
             drink.title=body['title']
        if('recipe' in body):
            drink.recipe=json.dumps(body['recipe'])

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })

    except:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    try:
        drink = Drink.query.filter(
            Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()
        return jsonify({
            'success': True,
            'delete': drink_id
        })

    except:
        abort(422)


## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(AuthError)
def handle_auth_errors(error):
    response = error.error, error.status_code
    return response