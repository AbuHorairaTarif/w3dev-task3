from datetime import datetime, timedelta
from functools import wraps
import secrets
import os
import jwt
import re
from flask import Flask, g
from flask_restx import Api, Resource, reqparse
import psycopg2

app = Flask(__name__)
api = Api(app, title='flask-app')

# Load configurations from environment variables or a configuration file
app.config['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'postgresql://myuser:mypassword@localhost:5432/testDB')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'secretkey')
app.config['JWT_EXPIRATION_DELTA'] = timedelta(minutes=10)

# Postgres Database Connection
def get_db_connection():
    if not hasattr(g, 'db_connection'):
        g.db_connection = psycopg2.connect(app.config['DATABASE_URL'])
    return g.db_connection

# Helper function to generate JWT token
def generate_token(username):
    payload = {
        'username': username,
        'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA']
    }
    token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token

# Define a parser for the authorization header
auth_parser = reqparse.RequestParser()
auth_parser.add_argument('Authorization', type=str, location='headers')

# JWT authentication decorator
def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        args = auth_parser.parse_args()
        token = args.get('Authorization', '')

        if not token:
            return {'message': 'Unauthorized access'}, 401

        try:
            decoded_token = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            g.user = decoded_token
        except jwt.ExpiredSignatureError:
            return {'message': 'Session expired, please login again'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401
        
        return f(*args, **kwargs)

# Create a namespace
user_namespace = api.namespace('user', description='Operations about user login')
user_info_namespace = api.namespace('my', description='Operations about sign up new user')

# Create a parser for the login data
login_parser = api.parser()
login_parser.add_argument("username", type=str, required=True)
login_parser.add_argument("password", type=str, required=True)

# Create a parser for the signup data
signup_parser = api.parser()
signup_parser.add_argument("email", type=str, required=True)
signup_parser.add_argument("username", type=str, required=True)
signup_parser.add_argument("password", type=str, required=True)

# Controller
@user_namespace.route('/login')
class LoginResource(Resource):
    @api.doc(
        parser=login_parser, 
        description='User Login',
        params={
            'username': 'Enter Your Username',
            'password': 'Enter Password'
        },
        responses={
            200: 'User login successful',
            404: 'User not found',
            500: 'Internal server error'
        }
    )

    def post(self):
        """Logs user into the system"""
        
        try:
            args = login_parser.parse_args()
            username = args["username"]
            password = args["password"]

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_name = %s AND user_password = %s", (username, password))
            user = cursor.fetchone()

            if user:
                user_data = {
                    "email": user[1],
                    "username": user[2]
                }
                return {"message": "User login successful", "user_info": user_data}, 200
            else:
                return {"message": "User not found"}, 404
            
        except Exception as e:
            return {'message': 'Internal server error'}, 500

@user_namespace.route('/signup')
class SignupResource(Resource):
    @api.doc(
        parser=signup_parser, 
        description='User Registration',
        params={
            'email': 'Enter Your Email',
            'username': 'Enter Your Username',
            'password': 'Enter Password'
        },
        responses={
            201: 'User created successful',
            400: 'Invalid format',
            409: 'User already exists',
            500: 'Internal server error'
        }
    )

    def post(self):
        """Create a new user"""

        try:
            args = signup_parser.parse_args()
            email = args["email"]
            username = args["username"]
            password = args["password"]

            # Check if the email or username already exists
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_email = %s OR user_name = %s", (email, username))

            existing_user = cursor.fetchone()
            if existing_user:
                if existing_user[1] == email:
                    return {'message': 'User already exists'}, 409
                if existing_user[2] == username:
                    return {'message': 'Username already taken'}, 409
            
            # Validate input fields
            if not email.endswith('@gmail.com'):
                return {'message': 'Invalid email format. Email must end with @gmail.com'}, 400
 
            if not re.match(r'^[a-z]+[0-9]', username):
                return {'message': 'Invalid username format. Username should start with a small letter, followed by other small letters and a number.'}, 400
            
            if not re.match(r'^(?=.*[0-9])(?=.*[!@#$%^&*(),.?":{}|<>])[a-zA-Z0-9!@#$%^&*(),.?":{}|<>]{6}$', password):
                return {'message': 'Invalid password format. Password must be 6 characters long and contain at least 1 number and 1 special character.'}, 400

            # Insert the new user into the database
            cursor.execute("INSERT INTO users (user_email, user_name, user_password) VALUES (%s, %s, %s)", (email, username, password))
            conn.commit()
            return {'message': 'User created successfully'}, 201

        except Exception as e:
            return {'message': 'Internal server error'}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0')

