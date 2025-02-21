"""
Copyright (c) 2024 Devesh Ajay Vaidya, Ashwin Ramesh, Aditi Reddy, Bhuvan Chandra Kurra
This code is licensed under MIT license (see LICENSE for details)

@author: Burnout


This python file is used in and is part of the Burnout project.

For more information about the Burnout project, visit:
https://github.com/CS510-001-HW/FitnessApp

"""

""""Importing app from apps.py"""
from apps import App

app = App()
mongo = app.mongo


def insertfooddata():
    """
    Function to insert food data from a CSV file into MongoDB.
    Reads calorie data for various foods and inserts or updates each food's calorie count in the database.
    """

    # Open the CSV file containing food calorie data
    f = open("food_data/calories.csv", "r", encoding="ISO-8859-1")
    l = f.readlines()  # Read all lines in the file into a list

    # Adjust each line to remove unwanted characters (trimming edges)
    for i in range(1, len(l)):
        l[i] = l[i][1 : len(l[i]) - 2]

    # Process each line (food item) and update calorie data in MongoDB
    for i in range(1, len(l)):
        temp = l[i].split(
            ","
        )  # Split line by commas to separate food and calorie count
        mongo.db.food.update_one(
            {"food": temp[0]},  # Filter by food name
            {"$set": {"calories": temp[1]}},  # Set or update calorie data
            upsert=True,  # If food item doesn't exist, insert it
        )


def insertexercisedata():
    """Define exercise data for all 9 exercises"""
    exercise_data = [
        {
            "email": "email",
            "exercise_id": 1,
            "image": "../static/img/yoga.jpg",
            "video_link": "https://www.youtube.com/watch?v=c8hjhRqIwHE",
            "name": "Yoga for Beginners",
            "description": "New to Yoga? You are at the right place! Learn easy yoga poses to build strength, flexibility, and mental clarity.",
            "href": "yoga",
        },
        {
            "email": "email",
            "exercise_id": 2,
            "image": "../static/img/swim.jpeg",
            "video_link": "https://www.youtube.com/watch?v=oM4sHl1hTEE",
            "name": "Swimming",
            "description": "Swimming is an activity that burns lots of calories, is easy on the joints, supports your weight, builds muscular strength and endurance.",
            "href": "swimming",
        },
        {
            "email": "email",
            "exercise_id": 3,
            "image": "../static/img/R31.jpg",
            "video_link": "https://www.youtube.com/watch?v=z6GxFSsx84E",
            "name": "Abs Smash",
            "description": "Whether your goal is a six-pack or just a little more definition around your midsection, we will help get you there!",
            "href": "abs",
        },
        {
            "email": "email",
            "exercise_id": 4,
            "image": "../static/img/walk.jpg",
            "video_link": "https://www.youtube.com/watch?v=3hlUMzWh8jY",
            "name": "Walk Fitness",
            "description": "Join us to get the best of the walk workouts to burn more calories than a stroll around the park.",
            "href": "walk",
        },
        {
            "email": "email",
            "exercise_id": 5,
            "image": "../static/img/R21.jpg",
            "video_link": "https://www.youtube.com/watch?v=8MAtXXXUvqo",
            "name": "Belly Burner",
            "description": "Join Sasha for a 30-minute no-equipment workout that will work on that stubborn belly fat.",
            "href": "belly",
        },
        {
            "email": "email",
            "exercise_id": 6,
            "image": "../static/img/R22.jpg",
            "video_link": "https://www.youtube.com/watch?v=Qf0L-xtMUjg",
            "name": "Dance Fitness",
            "description": "Shake it off and groove to some fun tracks with Tom and his squad in this dance fitness session!",
            "href": "dance",
        },
        {
            "email": "email",
            "exercise_id": 7,
            "image": "../static/img/R23.jpg",
            "video_link": "https://www.youtube.com/watch?v=Ze7zzMgCdko",
            "name": "HRX Fitness",
            "description": "It's time to push yourself to the limit! Join us for some intense workout sessions.",
            "href": "hrx",
        },
        {
            "email": "email",
            "exercise_id": 8,
            "image": "../static/img/R32.jpg",
            "video_link": "https://www.youtube.com/watch?v=XH7mBWRG9q0",
            "name": "Core Conditioning",
            "description": "Develop core muscle strength that improves posture and contributes to a trimmer appearance.",
            "href": "core",
        },
        {
            "email": "email",
            "exercise_id": 9,
            "image": "../static/img/R11.jpg",
            "video_link": "https://www.youtube.com/watch?v=8IjCdiweJQo",
            "name": "Gym",
            "description": "A collection of Dumbbells workouts by skilled trainers specific to a particular muscle group.",
            "href": "gym",
        },
        {
            "email": "email",
            "exercise_id": 10,
            "image": "../static/img/headspace.PNG",
            "video_link": "https://www.youtube.com/watch?v=5LMRrYqAAZI",
            "name": "Headspace",
            "description": "Headspace's mission is to provide every person access to lifelong mental health support.",
            "href": "headspace",
        },
        {
            "email": "email",
            "exercise_id": 11,
            "image": "../static/img/mbsr.jpg",
            "video_link": "https://www.youtube.com/watch?v=507zwibbfRs",
            "name": "MBSR",
            "description": "Mindfulness-Based Stress Reduction (MBSR) is a structured program designed to help individuals manage stress, reduce anxiety, and improve overall well-being through mindfulness meditation and awareness.",
            "href": "mbsr",
        },
    ]

    # Connect to MongoDB

    # Connect to MongoDB collection designated for storing exercise data
    collection = mongo.db["your_exercise_collection"]

    # Insert each exercise into MongoDB
    for exercise in exercise_data:
        query = {"exercise_id": exercise["exercise_id"]}  # Query by unique exercise ID
        update = {
            "$set": exercise
        }  # Update exercise details if exercise already exists
        collection.update_one(
            query, update, upsert=True
        )  # Insert exercise if it doesn't exist
