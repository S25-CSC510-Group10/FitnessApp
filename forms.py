
"""
Copyright (c) 2024 Devesh Ajay Vaidya, Ashwin Ramesh, Aditi Reddy, Bhuvan Chandra Kurra
This code is licensed under MIT license (see LICENSE for details)

@author: Burnout


This python file is used in and is part of the Burnout project.

For more information about the Burnout project, visit:
https://github.com/CS510-001-HW/FitnessApp
"""

# from datetime import date
# from re import sub
# from flask import app
"""Importing modules to create forms"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.core import DateField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from apps import App


class RegistrationForm(FlaskForm):
    """Form to collect the registration data of the user"""
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[
            DataRequired(), EqualTo('password')])
    weight = StringField(
        'Weight (in kilograms)', validators=[
            DataRequired(), Length(
                min=2, max=20)])
    height = StringField(
        'Height (in centimeters)', validators=[
            DataRequired(), Length(
                min=2, max=20)])
    goal = SelectField('Select Goal', choices=['Weight Loss', 'Muscle Gain'])
    target_weight = StringField(
        'Target Weight (in kilograms)', validators=[
            DataRequired(), Length(
                min=2, max=20)])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        """Function to validate the entered email"""
        app_object = App()
        mongo = app_object.mongo

        temp = mongo.db.user.find_one({'email': email.data}, {'email', 'pwd'})
        if temp:
            raise ValidationError('Email already exists!')


class LoginForm(FlaskForm):
    """Login form to log in to the application"""
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class CalorieForm(FlaskForm):
    """Form to rcord the calorie intake details of the user"""
    app = App()
    mongo = app.mongo

    cursor = mongo.db.food.find()
    get_docs = []
    for record in cursor:
        get_docs.append(record)

    result = []
    temp = ""
    for i in get_docs:
        temp = i['food'] + ' (' + i['calories'] + ')'
        result.append((temp, temp))

    food = SelectField(
        'Select Food', choices=result)

    burnout = StringField('Burn Out', validators=[DataRequired()])
    submit = SubmitField('Save')


class UserProfileForm(FlaskForm):
    """Form to input user details to store their height, weight, goal and target weight"""
    weight = StringField(
        'Weight (in kilograms)', validators=[
            DataRequired(), Length(
                min=2, max=20)])
    height = StringField(
        'Height (in centimeters)', validators=[
            DataRequired(), Length(
                min=2, max=20)])
    goal = SelectField('Select Goal', choices=['Weight Loss', 'Muscle Gain'])
    target_weight = StringField(
        'Target Weight (in kilograms)', validators=[
            DataRequired(), Length(
                min=2, max=20)])
    submit = SubmitField('Update')


class HistoryForm(FlaskForm):
    """Form to input the date for which the history needs to be displayed"""
    app = App()
    mongo = app.mongo
    date = DateField()
    submit = SubmitField('Fetch')


class EnrollForm(FlaskForm):
    """Form to enroll into a particular exercise/event"""
    app = App()
    mongo = app.mongo
    submit = SubmitField('Enroll')

class UnenrollForm(FlaskForm):
    """Form to enroll into a particular exercise/event"""
    app = App()
    mongo = app.mongo
    completed = SubmitField(label='Completed')
    submit = SubmitField(label='Unenroll')

class ResetPasswordForm(FlaskForm):
    """Form to reset the account password"""
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField(
        'Confirm Password', validators=[
            DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset')

class ReviewForm(FlaskForm):
    """Form to input the different reviews about the application"""
    review = StringField(
        'Review', validators=[
            DataRequired(), Length(
                min=2, max=200)])
    name = StringField(
        'Name', validators=[
            DataRequired(), Length(
                min=2, max=200)])
    submit = SubmitField('Submit')
