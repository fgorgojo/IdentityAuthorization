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


# ROUTES/ENDPOINTS   
@app.route('/drinks', methods=['GET'])
def get_drinks():
    """A public endpoint to get drinks"""
    try:
        drinks = Drink.query.all()
        return jsonify({
            "success": True,
            "drinks": [drink.short() for drink in drinks]
        }), 200
    except Exception:
        abort(500)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    """A restricted endpoint to get drinks detail for roles with 
       'get:drinks-detail' permission
    """
    try:
        drinks = Drink.query.all()
        return jsonify({
            "success": True,
            "drinks": [drink.long() for drink in drinks]
        }), 200
    except Exception:
        abort(500)

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    """A restricted endpoint to create a new drink for roles with
       'post:drinks' permission"""
    try:
        body = request.get_json()
        print(body)
        new_drink = Drink(
            title=body.get('title'),
            recipe=json.dumps(body.get('recipe'))
        )
        new_drink.insert()
        return jsonify({
            "success": True,
            "drinks": [new_drink.long()]
        }), 200
    except Exception:
        abort(400)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')  
def update_drink(payload, id):
    """A restricted endpoint to update an existing drink for roles with
       'patch:drinks' permission
    """
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)

        body = request.get_json()
        drink.title = body.get('title', drink.title)
        drink.recipe = json.dumps(body.get('recipe', json.loads(drink.recipe)))
        drink.update()

        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        }), 200
    except Exception:
        abort(400)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
    """A restricted endpoint to delete an existing drink for roles with
       'delete:drinks' permission
    """
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        }), 200
    except Exception:
        abort(400)

# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    """A error handler for unprocessable entity (422) errors"""
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(400)
def bad_request(error):
    """A error handler for bad request (400) errors"""
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


@app.errorhandler(404)
def not_found(error):
    """A error handler for resource not found (404) errors"""
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """A error handler for internal server error (500) errors"""
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error"
    }), 500


@app.errorhandler(AuthError)
def handle_auth_error(error):
    """A error handler for authentication errors"""
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error["description"]
    }), error.status_code







