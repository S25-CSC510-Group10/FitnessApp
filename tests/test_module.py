"""
Copyright (c) 2023 Rajat Chandak, Shubham Saboo, Vibhav Deo, Chinmay Nayak
This code is licensed under MIT license (see LICENSE for details)

@author: Burnout


This python file is used in and is part of the Burnout project.

For more information about the Burnout project, visit:
https://github.com/VibhavDeo/FitnessApp

"""

import unittest
import os, sys, inspect
from application import app
from flask import session


class TestApplication(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_home_route(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 302)

    def test_login_route(self):
        response = self.app.get("/login")
        self.assertEqual(response.status_code, 200)

    def test_register_route(self):
        response = self.app.get("/register")
        self.assertEqual(response.status_code, 200)

    def test_calories_route(self):

        response = self.app.get("/calories")
        self.assertEqual(response.status_code, 302)

    def test_user_profile_route(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.get("/user_profile")
            self.assertEqual(response.status_code, 200)

    def test_history_route_unauthenticated(self):

        response = self.app.get("/history")
        self.assertEqual(response.status_code, 302)

    def test_history_route(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.get("/history")

            self.assertEqual(response.status_code, 200)

    def test_bmi_calci_post(self):
        response = self.app.post("/bmi_calc", data={"weight": 70, "height": 175})
        self.assertEqual(response.status_code, 200)

    def test_ajaxsendrequest_route(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.post(
                "/ajaxsendrequest", data={"receiver": "friend@example.com"}
            )
            self.assertEqual(response.status_code, 200)

    def test_ajaxcancelrequest_route(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.post(
                "/ajaxcancelrequest", data={"receiver": "friend@example.com"}
            )
            self.assertEqual(response.status_code, 200)

    def test_ajaxapproverequest_route(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.post(
                "/ajaxapproverequest", data={"receiver": "friend@example.com"}
            )
            self.assertEqual(response.status_code, 200)

    def test_dashboard_route(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.get("/dashboard")
            self.assertEqual(response.status_code, 200)

    def test_favorites_route(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.get("/favorites")
            self.assertEqual(response.status_code, 200)

    def test_exercise_routes(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"

            exercise_routes = [
                "/yoga",
                "/swimming",
                "/abs",
                "/belly",
                "/core",
                "/gym",
                "/walk",
                "/dance",
                "/hrx",
            ]

            for route in exercise_routes:
                response = client.get(route)
                self.assertEqual(response.status_code, 200)

    def test_clear_water_intake(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"

            response = client.post("/clear-intake")
            self.assertEqual(response.status_code, 302)

    def test_water_unauthenticated(self):
        response = self.app.post("/water")
        self.assertEqual(response.status_code, 302)

    def test_my_activities_unauthenticated(self):
        response = self.app.get("/activities")
        self.assertEqual(response.status_code, 302)

    def test_my_activities(self):
        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.get("/activities")
            self.assertEqual(response.status_code, 200)

    def test_achievements_unauthenticated(self):
        response = self.app.get("/achievements")
        self.assertEqual(response.status_code, 302)

    def test_achievements(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.get("/achievements")
            self.assertEqual(response.status_code, 200)

    def test_shop_unauthenticated(self):
        response = self.app.get("/shop")
        self.assertEqual(response.status_code, 302)

    def test_shop(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.get("/shop")
            self.assertEqual(response.status_code, 200)

    def test_mind_unauthenticated(self):
        response = self.app.get("/mind")
        self.assertEqual(response.status_code, 302)

    def test_mind(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.get("/mind")
            self.assertEqual(response.status_code, 200)

    def test_submit_reviews_route(self):

        with self.app as client:
            with client.session_transaction() as sess:
                sess["email"] = "testuser@example.com"
            response = client.get("/review")
            self.assertEqual(response.status_code, 200)  #

    ### CSC 510 Spring 2025 - Team 10 Tests
    #


if __name__ == "__main__":
    unittest.main()
