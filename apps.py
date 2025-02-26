
"""
Copyright (c) 2025 Hank Lenham, Ryan McPhee, Lawrence Stephenson
This code is licensed under MIT license (see LICENSE for details)

@author: Burnout


This python file is used in and is part of the Burnout project.

For more information about the Burnout project, visit:
https://github.com/S25-CSC510-Group10/FitnessApp

"""

"""Importing flask to connect to the database"""
from flask import Flask
from flask_pymongo import PyMongo
from flask_mail import Mail


class App:
    """Initialize Flask app with MongoDB and Mail configuration"""
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'secret'
        self.app.config['MONGO_URI'] = 'mongodb://localhost:27017/test'
        self.mongo = PyMongo(self.app)

        self.app.config['MAIL_SERVER'] = 'smtp.gmail.com'
        self.app.config['MAIL_PORT'] = 465
        self.app.config['MAIL_USE_SSL'] = True
        self.app.config['MAIL_USERNAME'] = "bogusdummy123@gmail.com"
        self.app.config['MAIL_PASSWORD'] = "helloworld123!"
        self.mail = Mail(self.app)


    def get_app(self):
        """Returns the Flask app instance"""
        return self.app

    def get_mongo(self):
        """Returns the MongoDB instance"""
        return self.mongo

    def get_mail(self):
        """Returns the Mail instance"""
        return self.mail
