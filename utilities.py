
"""
Copyright (c) 2025 Hank Lenham, Ryan McPhee, Lawrence Stephenson
This code is licensed under MIT license (see LICENSE for details)

@author: Burnout


This python file is used in and is part of the Burnout project.

For more information about the Burnout project, visit:
https://github.com/S25-CSC510-Group10/FitnessApp

"""

"""Importing modules to check the send_email functions""" 
import random
import string
from flask_mail import Message
from apps import App

class Utilities:
    """Class to chech the send_email functionality"""
    app = App()
    mail = app.mail
    mongo = app.mongo
    def send_email(self, email):
        """Validates the send email function"""
        msg = Message()
        msg.subject = "BURNOUT - Reset Password Request"
        msg.sender = 'bogusdummy123@gmail.com'
        msg.recipients = [email]
        random_str = str(self.get_random_string(8))
        msg.body = 'Please use the following password to login to your account: ' + random_str
        self.mongo.db.ath.update({'email': email}, {'$set': {'temp': random_str}})
        if self.mail.send(msg):
            return "success"
        return "failed"

    def get_random_string(self, length):
        """choose from all lowercase letter"""
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        print("Random string of length", length, "is:", result_str)
        return result_str
