reminder_email()
- This function sends an automated email to all the users as a daily reminder to exercise

login()
- This function is used for login by the user
- Using email ID and passoword is validated and the user is directed to home

logout()
- This function is used for logout by the user
- logout() function just clears the session

register()
- This function is used for registering new users
- Details of new users are stored in the database and the user is redirected to login page

homePage()
- This function renders the home page

send_email()
- This function is used to send an email to user's friends containing calorie history of user
- The user will fill a textarea with their friends email IDs (comma seperated if multiple)

calories()
- This function will add calories consumed/burned for the data selected.

profile()
- This function is used to store/display user's profile details such as height, weight and goal weight

history()
- This function displays user's historical calorie consumption and burnout at date level

friends()
- This function allows user to accept friend requests and display all friends

bmi_calci()
- This function returns the Body Mass Index of the user whenever they enter their height and weight

submit_reviews()
- This function returns the exiting reviews and also insert the new reviews submitted by user

calc_bmi()
- This function calculates the BMI mathematically which is returned to the the bmi_calci() function

get_bmi_category()
- This function will designate the BMI category of the user based on the calculated BMI value

send_email()
- This function shares the calorie details of the user to their friends via email.

add_favorite()
- This function allows the user to record and store their favourite exercises

favorites()
- This function displays the favourite exercises of the users

yoga()/swim()/abbs()/belly()/core()/gym()/walk()/dance()/hrx()
- This function allows user to enroll in different plans

activities()
- This function display the list of activities which a user has or had previously enrolled under with their current status.

find_activities()
- This function seaches the list of activities of a user based on an email search.

achievements()
- This function displays the list of achievements that a user has earned in his fitness journey.

render_guided_meditation()
- This function is used to display the different meditation exercises available throughout the internet.
