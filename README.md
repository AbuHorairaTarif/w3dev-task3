# w3dev-task3
Python assignment and build an JSON Restful OpenAPI standard API based on flask

## Table of Contents

- [Prerequisites](#prerequisites)
- [How To Run](#How-to-run)
  - [PostgreSQL Setup](#postgresql-setup)
  - [Elasticsearch and Kibana Setup](#elasticsearch-and-kibana-setup)
- [API Endpoints](#api-endpoints)
  - [User Login](#user-login)
  - [User Registration](#user-registration)

## Prerequisites

- Python 
- Flask
- Flask-RESTx
- PyJWT
- Docker
- PostgreSQL / PGAdmin
- Elasticsearch / Kibana

## How-to-run

<li>First Create Virtual Environment</li>
<li>Run in terminal: pip install virtualenv</li>
<li>Go to project directory and type in 'virtualenv venv' and after then 'venv/bin/activate'</li>
<li>Now Install flask by typing ' pip install flask'</li>
<li>Run all required dependencies from terminal 'pip install -r requirement.txt'</li>
<li>Complete postgres setup</li>
<li>'docker-compose up -d'</li>


### User Login

**Endpoint:** `/user/login`

- **Method:** `POST`
- **Description:** Logs a user into the system using their username and password.
- **Request Body:**
  - `username`: User's username
  - `password`: User's password


### User Registration

**Endpoint:** `/user/signup`

- **Method:** `POST`
- **Description:** Creates a new user account.
- **Request Body:**
  - `email`: User's email
  - `username`: User's desired username
  - `password`: User's desired password

