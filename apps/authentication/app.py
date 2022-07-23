from crypt import methods
from email import message
from flask import Flask, request, Response, jsonify
from sqlalchemy import and_
from  configuration import Configuration
from models import database, User, Role
from email.utils import parseaddr
from helper_functions import password_check
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

@application.route("/register", methods = ["POST"])
def register():
    # Get all data from request body and check if data is valid
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    is_customer = request.json.get("isCustimer", None)

    # Empty or missing fields errors
    if not forename:
        return jsonify(message="Field forename is missing."), 400
    elif len(forename) > 256:
        return jsonify(message="Invalid forename."), 400

    if not surname:
        return jsonify(message="Field surname is missing."), 400 
    elif len(surname) > 256:
        return jsonify(message="Invalid surname."), 400
    
    if not email:
        return jsonify(message="Field email is missing."), 400
    
    if not password:
        return jsonify(message="Field password is missing."), 400

    if is_customer == "":
        return jsonify(message="Field isCustomer is missing."), 400
    elif not isinstance(is_customer, bool):
        return jsonify(message="Invalid isCustomer."), 400

    # Invalid email
    if len(email) > 256:
        return jsonify(message="Invalid email."), 400
    if len(parseaddr(email)[1]) == 0:
        return jsonify(message="Invalid email."), 400

    # Invalid password
    if not password_check["password_ok"]:
        return jsonify(message="Invalid password."), 400

    # Check if email is taken
    if User.query.filter_by(email=email).first():
        return jsonify(message="Email already exists."), 400

    # Check which role is selected
    role_id : int
    if is_customer:
        role_id = 2
    else:
        role_id = 3

    # Add new user
    user = User(
        forename = forename,
        surname = surname,
        password = password,
        email = email,
        role_id = role_id
    )

    database.session.add(user)
    database.session.commit()

    # Default statis is 200 ok
    return Response()
    
@application.route("/login", methods = ["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    # Check for missing fileds
    if not email:
        return jsonify(message="Field email is missing."), 400
    
    if not password:
        return jsonify(message="Field password is missing."), 400

    # Invalid email
    if len(email) > 256:
        return jsonify(message="Invalid email."), 400
    if len(parseaddr(email)[1]) == 0:
        return jsonify(message="Invalid email."), 400
    
    # Check if user exists with given credentials
    user = User.query.filter(and_ (User.email == email, User.password == password)).first()
    if not user:
        return jsonify(message="Invalid credentials."), 400


    # Create JWT token 
    additional_claims = {
        "forename": user.forename,
        "surname": user.surname,
        "role": Role.query.filter_by(id=user.role_id).first().role_name
    }

    access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.email, additional_claims=additional_claims)

    return jsonify(accessToken = access_token, refreshToken = refresh_token)

# Returns new access token if one is expired; can only be accessed with refresh token
@application.route("/refresh", methods = ["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    refresh_claims = get_jwt()

    # Creates new additional_claims from old
    additional_claims = {
        "forename": refresh_claims["forename"],
        "surname": refresh_claims["surname"],
        "role": refresh_claims["role"]
    }

    return create_access_token(identity=identity, additional_claims=additional_claims), 200




if __name__ == "__main__":
    database.init_app(application)
    application.run(debug=True)
 