from flask import Flask, request, Response, jsonify
from sqlalchemy import and_
from decoraters import role_check
from email_validator import validate_email, EmailNotValidError
from  configuration import Configuration
from models import database, User, Role
from password_utils import password_check
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
    is_customer = request.json.get("isCustomer", "")

    # Empty or missing fields errors
    if len(forename) == 0:
        return jsonify(message="Field forename is missing."), 400
    elif len(forename) > 256:
        return jsonify(message="Invalid forename."), 400

    if len(surname) == 0:
        return jsonify(message="Field surname is missing."), 400 
    elif len(surname) > 256:
        return jsonify(message="Invalid surname."), 400
    
    if len(email) == 0:
        return jsonify(message="Field email is missing."), 400

    if len(password) == 0:
        return jsonify(message="Field password is missing."), 400
    
    if is_customer == "":
        return jsonify(message="Field isCustomer is missing."), 400
    elif not isinstance(is_customer, bool):
        return jsonify(message="Invalid isCustomer."), 400


    # Invalid email
    if len(email) > 256:
        return jsonify(message="Invalid email."), 400
    try:
        validate_email(email)
    except:
        return jsonify(message="Invalid email."), 400

    # Check if email is taken
    if User.query.filter_by(email=email).first():
        return jsonify(message="Email already exists."), 400

    # Invalid password
    if not password_check(password):
        return jsonify(message="Invalid password."), 400

    # Check which role is selected
    role_id = None
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
    if len(email) == 0:
        return jsonify(message="Field email is missing."), 400
    
    if len(password) == 0:
        return jsonify(message="Field password is missing."), 400

    # Invalid email
    if len(email) > 256:
        return jsonify(message="Invalid email."), 400
    try:
        validate_email(email)
    except:
        return jsonify(message="Invalid email."), 400
    
    # Check if user exists with given credentials
    user = User.query.filter(and_ (User.email == email, User.password == password)).first()
    if not user:
        return jsonify(message="Invalid credentials."), 400

    role_name = "admin"
    if user.role_id == 2:
        role_name = "customer"
    elif user.role_id == 3:
        role_name = "worker"

    # Create JWT token 
    additional_claims = {
        "forename": user.forename,
        "surname": user.surname,
        "role": role_name
    }

    access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.email, additional_claims=additional_claims)

    return jsonify(accessToken = access_token, refreshToken = refresh_token), 200

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

    return jsonify(accessToken=create_access_token(identity=identity, additional_claims=additional_claims)), 200

# Delete user; can only be accesed as admin
@application.route("/delete", methods = ["POST"])
@role_check(role = "admin")
def delete():
    email = request.json.get("email", "")
    
    # Missing email
    if len(email) == 0:
        return jsonify(message="Field email is missing."), 400

    # Invalid email
    if len(email) > 256:
        return jsonify(message="Invalid email."), 400
    try:
        validate_email(email)
    except:
        return jsonify(message="Invalid email."), 400

    # User doesn't exist
    user = User.query.filter(User.email==email).first()
    if not user:
        return jsonify(message="Unknown user."), 400
    
    # User exists and can be deleted
    database.session.delete(user)
    database.session.commit()
    return Response()


if __name__ == "__main__":
    database.init_app(application)
    application.run(port=5002, host='0.0.0.0', debug=True)
    