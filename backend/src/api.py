import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink, db
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
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks",methods=["GET"])
def drinks():
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)
    return jsonify({
        'success': True,
        "drinks":[drink.short() for drink in drinks]
    })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail",methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    return jsonify({"success": True, "drinks": [drink.long() for drink in drinks]})
'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(jwt):

    form   = request.get_json()
    if request.form:
        title  = request.form.get("title")
        recipe = request.form.get('recipe')

        if "title" and "recipe" not in request.form:
            return abort(422)
        elif "title" and "recipe" in form:
            drink=Drink(title=title, recipe=json.dumps(recipe))
            drink.insert()
            return jsonify({
                'success':True,
                "drinks":[drink.long()],
            })
    else:
        return abort(401)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def edit_drink(jwt,drink_id):

    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    if request.form:
        info = request.get_json()
        title = request.form["title"]
        recipe = json.dumps(info.get('recipe'))
        if "title" not in info:
            return abort(422)
        try:
            drink.info=info
            drink.title=title
            drink.recipe=recipe
            drink.update()
        except:
            db.session.rollback()
        finally:
            db.session.close()
        
        return jsonify({
            "success":True,
            "drinks":[drink.long()]
        })
    else:
        return abort(400)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>",methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(jwt,id):
    if jwt:
        drink = Drink.query.filter(Drink.id == id).first_or_404()
        drink.delete()
        return jsonify({
            'success': True,
            "delete": id
        })

## Error Handling
'''
Example error handling for unprocessable entity
'''
# @app.errorhandler(422)
# def unprocessable(error):
#     return jsonify({
#                     "success": False, 
#                     "error": 422,
#                     "message": "unprocessable"
#                     }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(AuthError)
def handle_auth_errors(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error
    },401)

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }, 422)

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }, 404)

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal server error!'
    }, 500)

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
