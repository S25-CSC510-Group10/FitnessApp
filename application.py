
"""
Copyright (c) 2023 Rajat Chandak, Shubham Saboo, Vibhav Deo, Chinmay Nayak
This code is licensed under MIT license (see LICENSE for details)

@author: Burnout


This python file is used in and is part of the Burnout project.

For more information about the Burnout project, visit:
https://github.com/VibhavDeo/FitnessApp

"""
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import smtplib
from flask import json,jsonify,Flask
from flask import render_template, session, url_for, flash, redirect, request, Flask
from flask_mail import Mail
from flask_pymongo import PyMongo
from tabulate import tabulate
from achievements import updateAchievments, getAchievements
from forms import HistoryForm, RegistrationForm, LoginForm, CalorieForm, UnenrollForm, UserProfileForm, EnrollForm,ReviewForm
from insert_db_data import insertfooddata,insertexercisedata
import schedule
from threading import Thread
import time
from datetime import date

app = Flask(__name__, template_folder='templates')
app.secret_key = 'secret'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/test'
app.config['MONGO_CONNECT'] = True
mongo = PyMongo(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "burnoutapp2023@gmail.com"
app.config['MAIL_PASSWORD'] = "jgny mtda gguq shnw"
mail = Mail(app)

insertfooddata()
insertexercisedata()

def reminder_email():
    """
    reminder_email() will send a reminder to users for doing their workout.
    """
    with app.app_context():
        try:
            time.sleep(10)
            print('in send mail')
            recipientlst = list(mongo.db.user.distinct('email'))
            print(recipientlst)
            
            server = smtplib.SMTP_SSL("smtp.gmail.com",465)
            sender_email = "burnoutapp2023@gmail.com"
            sender_password = "jgny mtda gguq shnw"

            server.login(sender_email,sender_password)
            message = 'Subject: Daily Reminder to Exercise'
            for e in recipientlst:
                print(e)
                server.sendmail(sender_email,e,message)                
            server.quit()        
        except KeyboardInterrupt:
            print("Thread interrupted")

schedule.every().day.at("08:00").do(reminder_email)

# Run the scheduler
def schedule_process():
    while True:
        schedule.run_pending()
        time.sleep(10)

Thread(target=schedule_process).start()
  

@app.route("/", methods=["GET", "POST"])
@app.route("/home")
def home():
    """
    home() function displays the homepage of our website.
    route "/home" will redirect to home() function.
    input: The function takes session as the input
    Output: Out function will redirect to the login page
    """
    if session.get('email'):
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    """"
    login() function displays the Login form (login.html) template
    route "/login" will redirect to login() function.
    LoginForm() called and if the form is submitted then various values are fetched and verified from the database entries
    Input: Email, Password, Login Type
    Output: Account Authentication and redirecting to Dashboard
    """
    if not session.get('email'):
        form = LoginForm()
        if form.validate_on_submit():
            temp = mongo.db.user.find_one({'email': form.email.data}, {
                'email', 'pwd','name'})
            if temp is not None and temp['email'] == form.email.data and temp['pwd'] == form.password.data:
                flash('You have been logged in!', 'success')
                print(temp)
                session['email'] = temp['email']
                session['name']=temp['name']
                #session['login_type'] = form.type.data
                return redirect(url_for('dashboard'))
            else:
                flash(
                    'Login Unsuccessful. Please check username and password',
                    'danger')
    else:
        return redirect(url_for('home'))
    return render_template(
        'login.html',
        title='Login',
        form=form)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    """
    logout() function just clears out the session and returns success
    route "/logout" will redirect to logout() function.
    Output: session clear
    """
    session.clear()
    return "success"


@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    register() function displays the Registration portal (register.html) template
    route "/register" will redirect to register() function.
    RegistrationForm() called and if the form is submitted then various values are fetched and updated into database
    Input: Username, Email, Password, Confirm Password
    Output: Value update in database and redirected to home login page
    """
    now = datetime.now()
    now = now.strftime('%Y-%m-%d')

    if not session.get('email'):
        form = RegistrationForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')

                mongo.db.user.insert_one({'name': username, 'email': email, 'pwd': password})
                
                weight = request.form.get('weight')
                height = request.form.get('height')
                goal = request.form.get('goal')
                target_weight = request.form.get('target_weight')
                temp = mongo.db.profile.find_one({'email': email, 'date': now}, {'height', 'weight', 'goal', 'target_weight'})
                mongo.db.profile.insert_one({'email': email,
                                             'date': now,
                                             'height': height,
                                             'weight': weight,
                                             'goal': goal,
                                             'target_weight': target_weight})
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route("/calories", methods=['GET', 'POST'])
def calories():
    """
    calorie() function displays the Calorieform (calories.html) template
    route "/calories" will redirect to calories() function.
    CalorieForm() called and if the form is submitted then various values are fetched and updated into the database entries
    Input: Email, date, food, burnout
    Output: Value update in database and redirected to home page
    """
    now = datetime.now()
    now = now.strftime('%Y-%m-%d')

    get_session = session.get('email')
    if get_session is not None:
        form = CalorieForm()
        if form.validate_on_submit():
            if request.method == 'POST':
                email = session.get('email')
                food = request.form.get('food')
                cals = food.split(" ")
                cals = int(cals[-1][1:-1])
                burn = request.form.get('burnout')

                temp = mongo.db.calories.find_one({'email': email}, {'email', 'calories', 'burnout', 'date'})
                if temp is not None and temp['date']==str(now):
                    mongo.db.calories.update_many({'email': email}, {'$set': {'calories': temp['calories'] + cals, 'burnout': temp['burnout'] + int(burn)}})
                else:
                    mongo.db.calories.insert({'date': now, 'email': email, 'calories': cals, 'burnout': int(burn)})
                flash(f'Successfully updated the data', 'success')
                return redirect(url_for('calories'))
    else:
        return redirect(url_for('home'))
    return render_template('calories.html', form=form, time=now)


@app.route("/display_profile", methods=['GET', 'POST'])
def display_profile():
    """
    Display user profile and graph
    """
    now = datetime.now()
    now = now.strftime('%Y-%m-%d')

    if session.get('email'):
        email = session.get('email')
        user_data = mongo.db.profile.find_one({'email': email})
        target_weight=float(user_data['target_weight'])
        user_data_hist = list(mongo.db.profile.find({'email': email}))

        for entry in user_data_hist:
            entry['date'] = datetime.strptime(entry['date'], '%Y-%m-%d').date()

        sorted_user_data_hist = sorted(user_data_hist, key=lambda x: x['date'])
        # Extracting data for the graph
        dates = [entry['date'] for entry in sorted_user_data_hist]
        weights = [float(entry['weight']) for entry in sorted_user_data_hist]

        # Plotting Graph 
        fig = px.line(x=dates, y=weights, labels={'x': 'Date', 'y': 'Weight'}, title='Progress',markers=True,line_shape='spline')
        fig.add_trace(go.Scatter(x=dates, y=[target_weight] * len(dates),mode='lines', line=dict(color='green', width=1, dash='dot'), name='Target Weight'))
        fig.update_yaxes(range=[min(min(weights),target_weight) - 5, max(max(weights),target_weight) + 5])
        fig.update_xaxes(range=[min(dates),now]) 
        # Converting to JSON
        graph_html = fig.to_html(full_html=False)

        last_10_entries = sorted_user_data_hist[-10:]

        return render_template('display_profile.html', status=True, user_data=user_data, graph_html=graph_html, last_10_entries=last_10_entries)
    else:
        return redirect(url_for('login'))
    #return render_template('user_profile.html', status=True, form=form)#

@app.route("/activities", methods=['GET', 'POST'])
def activities():
    """
    Display the list of activities which a user has or had previously enrolled under with their current status
    """
    now = datetime.now()
    now = now.strftime('%Y-%m-%d')

    if session.get('email'):
        email = session.get('email')
        activity_cursor = findActivities(email)
        activities = [
            {"name": activity.get("Activity", "Unknown"), 
            "status": activity.get("Status", "Unknown"), 
            "date": activity.get("Date", "Unknown")}
            for activity in activity_cursor
        ]
        return render_template('new_dashboard.html', activities=activities)
    else:
        return redirect(url_for('login'))
    #return render_template('user_profile.html', status=True, form=form)#

@app.route("/achievements", methods=['GET', 'POST'])
def achievements():
    """
    Display the list of achievements which a user has earned
    """

    if session.get('email'):
        email = session.get('email')
        achievements = getAchievements(email, mongo.db)
        return render_template('achievements.html', achievements=achievements)
    else:
        return redirect(url_for('login'))
    #return render_template('user_profile.html', status=True, form=form)#


@app.route("/user_profile", methods=['GET', 'POST'])
def user_profile():
    """
    user_profile() function displays the UserProfileForm (user_profile.html) template
    route "/user_profile" will redirect to user_profile() function.
    user_profile() called and if the form is submitted then various values are fetched and updated into the database entries
    Input: Email, height, weight, goal, Target weight
    Output: Value update in database and redirected to home login page.
    """
    now = datetime.now()
    now = now.strftime('%Y-%m-%d')

    if session.get('email'):
        form = UserProfileForm()
        if form.validate_on_submit():
            print('validated')
            if request.method == 'POST':
                print('post')
                email = session.get('email')
                weight = request.form.get('weight')
                height = request.form.get('height')
                goal = request.form.get('goal')
                target_weight = request.form.get('target_weight')
                temp = mongo.db.profile.find_one({'email': email, 'date': now}, {'height', 'weight', 'goal', 'target_weight'})
                if temp is not None:
                    mongo.db.profile.update_one({'email': email, 'date': now},
                                            {'$set': {
                                                'weight': weight,
                                                'height': height,
                                                'goal': goal,
                                                'target_weight':target_weight}})
                else:
                    mongo.db.profile.insert({'email': email,
                                             'date': now,
                                             'height': height,
                                             'weight': weight,
                                             'goal': goal,
                                             'target_weight': target_weight})

                flash(f'User Profile Updated', 'success')

                return redirect(url_for('display_profile'))
    else:
        return redirect(url_for('login'))
    return render_template('user_profile.html', status=True, form=form)


@app.route("/history", methods=['GET'])
def history():
    # ############################
    # history() function displays the Historyform (history.html) template
    # route "/history" will redirect to history() function.
    # HistoryForm() called and if the form is submitted then various values are fetched and update into the database entries
    # Input: Email, date
    # Output: Value fetched and displayed
    # ##########################
    if session.get('email'):
        get_session = session.get('email')
        form = None
        if get_session is not None:
            form = HistoryForm()
        return render_template('history.html', form=form)
    else:
        return redirect(url_for('login'))
    

@app.route('/water', methods=['GET','POST'])
def water():
    if session.get('email'):
        email = session.get('email')
        intake = request.form.get('intake')
        if request.method == 'POST':

            current_time = datetime.now()
            # Insert the new record
            mongo.db.intake_collection.insert_one({'intake': intake, 'time': current_time, 'email': email})

        # Retrieving records for the logged-in user
        records = mongo.db.intake_collection.find({"email": email}).sort("time", -1)

        # IMPORTANT: We need to convert the cursor to a list to iterate over it multiple times
        records_list = list(records)
        if records_list:
            average_intake = sum(int(record['intake']) for record in records_list) / len(records_list)
        else:
            average_intake = 0
        # Calculate total intake
        total_intake = sum(int(record['intake']) for record in records_list)

        # Render template with records and total intake
        return render_template('water_intake.html', records=records_list, total_intake=total_intake,average_intake=average_intake)
    else:
        return redirect(url_for('login'))


@app.route('/clear-intake', methods=['POST'])
def clear_intake():
    if session.get('email'):
        email = session.get('email')
        mongo.db.intake_collection.delete_many({"email": email})

        return redirect(url_for('water'))
    else:
        return redirect(url_for('login'))
    

@app.route('/shop')
def shop():
    if session.get('email'):
        return render_template('shop.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/mind')
def mind():
    if session.get('email'):
        return render_template('mind.html')
    else:
        return redirect(url_for('login'))

@app.route("/ajaxhistory", methods=['POST'])
def ajaxhistory():
    # ############################
    # ajaxhistory() is a POST function displays the fetches the various information from database
    # route "/ajaxhistory" will redirect to ajaxhistory() function.
    # Details corresponding to given email address are fetched from the database entries
    # Input: Email, date
    # Output: date, email, calories, burnout
    # ##########################
    email = get_session = session.get('email')
    print(email)
    if get_session is not None:
        if request.method == "POST":
            date = request.form.get('date')
            res = mongo.db.calories.find_one({'email': email, 'date': date}, {
                                             'date', 'email', 'calories', 'burnout'})
            if res:
                return json.dumps({'date': res['date'], 'email': res['email'], 'burnout': res['burnout'], 'calories': res['calories']}), 200, {
                    'ContentType': 'application/json'}
            else:
                return json.dumps({'date': "", 'email': "", 'burnout': "", 'calories': ""}), 200, {
                    'ContentType': 'application/json'}


@app.route("/friends", methods=['GET'])
def friends():
    # ############################
    # friends() function displays the list of friends corrsponding to given email
    # route "/friends" will redirect to friends() function which redirects to friends.html page.
    # friends() function will show a list of "My friends", "Add Friends" functionality, "send Request" and Pending Approvals" functionality
    # Details corresponding to given email address are fetched from the database entries
    # Input: Email
    # Output: My friends, Pending Approvals, Sent Requests and Add new friends
    # ##########################
    email = session.get('email')

    myFriends = list(mongo.db.friends.find(
        {'sender': email, 'accept': True}, {'sender', 'receiver', 'accept'}))
    myFriendsList = list()

    for f in myFriends:
        myFriendsList.append(f['receiver'])

    print(myFriends)
    allUsers = list(mongo.db.user.find({}, {'name', 'email'}))

    pendingRequests = list(mongo.db.friends.find(
        {'sender': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    pendingReceivers = list()
    for p in pendingRequests:
        pendingReceivers.append(p['receiver'])

    pendingApproves = list()
    pendingApprovals = list(mongo.db.friends.find(
        {'receiver': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    for p in pendingApprovals:
        pendingApproves.append(p['sender'])

    print(pendingApproves)

    # print(pendingRequests)
    return render_template('friends.html', allUsers=allUsers, pendingRequests=pendingRequests, active=email,
                           pendingReceivers=pendingReceivers, pendingApproves=pendingApproves, myFriends=myFriends, myFriendsList=myFriendsList)

@app.route('/bmi_calc', methods=['GET', 'POST'])
def bmi_calci():
    bmi = ''
    bmi_category = ''
    
    if request.method == 'POST' and 'weight' in request.form:
        weight = float(request.form.get('weight'))
        height = float(request.form.get('height'))
        bmi = calc_bmi(weight, height)
        bmi_category = get_bmi_category(bmi)
    
    return render_template("bmi_cal.html", bmi=bmi, bmi_category=bmi_category)

def calc_bmi(weight, height):
    return round((weight / ((height / 100) ** 2)), 2)

def get_bmi_category(bmi):
    if bmi < 18.5:
        return 'Underweight'
    elif bmi < 24.9:
        return 'Normal Weight'
    elif bmi < 29.9:
        return 'Overweight'
    else:
        return 'Obese'


@app.route('/guided_meditation', methods=['GET'])
def render_guided_meditation():
    return render_template("guided_medication.html")

@app.route("/send_email", methods=['GET','POST'])
def send_email():
    # ############################
    # send_email() function shares Calorie History with friend's email
    # route "/send_email" will redirect to send_email() function which redirects to friends.html page.
    # Input: Email
    # Output: Calorie History Received on specified email
    # ##########################
    email = session.get('email')
    temp = mongo.db.user.find_one({'email': email}, {'name'})
    data = list(mongo.db.calories.find({'email': email}, {'date','email','calories','burnout'}))
    table = [['Date','Email ID','Calories','Burnout']]
    for a in data:
        tmp = [a['date'],a['email'],a['calories'],a['burnout']] 
        table.append(tmp) 
    
    friend_email = str(request.form.get('share')).strip()
    friend_email = str(friend_email).split(',')
    server = smtplib.SMTP_SSL("smtp.gmail.com",465)
    #Storing sender's email address and password
    sender_email = "burnoutapp2023@gmail.com"
    sender_password = "jgny mtda gguq shnw"
    
    #Logging in with sender details
    server.login(sender_email,sender_password)
    message = 'Subject: Calorie History\n\n Your Friend '+str(temp['name'])+' has shared their calorie history with you!\n {}'.format(tabulate(table))
    for e in friend_email:
        print(e)
        server.sendmail(sender_email,e,message)
        
    server.quit()
    
    myFriends = list(mongo.db.friends.find(
        {'sender': email, 'accept': True}, {'sender', 'receiver', 'accept'}))
    myFriendsList = list()
    
    for f in myFriends:
        myFriendsList.append(f['receiver'])

    allUsers = list(mongo.db.user.find({}, {'name', 'email'}))
    
    pendingRequests = list(mongo.db.friends.find(
        {'sender': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    pendingReceivers = list()
    for p in pendingRequests:
        pendingReceivers.append(p['receiver'])

    pendingApproves = list()
    pendingApprovals = list(mongo.db.friends.find(
        {'receiver': email, 'accept': False}, {'sender', 'receiver', 'accept'}))
    for p in pendingApprovals:
        pendingApproves.append(p['sender'])
        
    return render_template('friends.html', allUsers=allUsers, pendingRequests=pendingRequests, active=email,
                           pendingReceivers=pendingReceivers, pendingApproves=pendingApproves, myFriends=myFriends, myFriendsList=myFriendsList)



@app.route("/ajaxsendrequest", methods=['POST'])
def ajaxsendrequest():
    # ############################
    # ajaxsendrequest() is a function that updates friend request information into database
    # route "/ajaxsendrequest" will redirect to ajaxsendrequest() function.
    # Details corresponding to given email address are fetched from the database entries and send request details updated
    # Input: Email, receiver
    # Output: DB entry of receiver info into database and return TRUE if success and FALSE otherwise
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        receiver = request.form.get('receiver')
        res = mongo.db.friends.insert_one(
            {'sender': email, 'receiver': receiver, 'accept': False})
        if res:
            return json.dumps({'status': True}), 200, {
                'ContentType': 'application/json'}
    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'}


@app.route("/ajaxcancelrequest", methods=['POST'])
def ajaxcancelrequest():
    # ############################
    # ajaxcancelrequest() is a function that updates friend request information into database
    # route "/ajaxcancelrequest" will redirect to ajaxcancelrequest() function.
    # Details corresponding to given email address are fetched from the database entries and cancel request details updated
    # Input: Email, receiver
    # Output: DB deletion of receiver info into database and return TRUE if success and FALSE otherwise
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        receiver = request.form.get('receiver')
        res = mongo.db.friends.delete_one(
            {'sender': email, 'receiver': receiver})
        if res:
            return json.dumps({'status': True}), 200, {
                'ContentType': 'application/json'}
    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'}


@app.route("/ajaxapproverequest", methods=['POST'])
def ajaxapproverequest():
    # ############################
    # ajaxapproverequest() is a function that updates friend request information into database
    # route "/ajaxapproverequest" will redirect to ajaxapproverequest() function.
    # Details corresponding to given email address are fetched from the database entries and approve request details updated
    # Input: Email, receiver
    # Output: DB updation of accept as TRUE info into database and return TRUE if success and FALSE otherwise
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        receiver = request.form.get('receiver')
        print(email, receiver)
        res = mongo.db.friends.update_one({'sender': receiver, 'receiver': email}, {
                                          "$set": {'sender': receiver, 'receiver': email, 'accept': True}})
        mongo.db.friends.insert_one(
            {'sender': email, 'receiver': receiver, 'accept': True})
        if res:
            return json.dumps({'status': True}), 200, {
                'ContentType': 'application/json'}
    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'}


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    # ############################
    # dashboard() function displays the dashboard.html template
    # route "/dashboard" will redirect to dashboard() function.
    # dashboard() called and displays the list of activities
    # Output: redirected to dashboard.html
    # ##########################
    exercises = [
        {"id": 1, "name": "Yoga"},
        {"id": 2, "name": "Swimming"},
        ]
    email = get_session = session.get('email')
    if session.get('email'):
        return render_template('dashboard.html', title='Dashboard', exercises=exercises)
    else:
        return redirect(url_for('login'))

@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    email = get_session = session.get('email')
    if session.get('email'):
        data = request.get_json()
        exercise_id = data.get('exercise_id')
        print(exercise_id)
        action = data.get('action')
        exercise = mongo.db.your_exercise_collection.find_one({"exercise_id": exercise_id})
        print(exercise)
        if exercise:
            if action=="add":
            # Create a new document in the favorites schema (you can customize this schema)
                favorite = {
                    "exercise_id":exercise.get("exercise_id"),
                    "email": email,
                    "image": exercise.get("image"),
                    "video_link": exercise.get("video_link"),
                    "name": exercise.get("name"),
                    "description": exercise.get("description"),
                    "href": exercise.get("href")
                }

            # Insert the exercise into the favorites collection
                mongo.db.favorites.insert_one(favorite)
                return jsonify({"status": "success"})
            elif action=="remove":
                print(exercise.get("exercise_id"))
                print("iamhere1")
                mongo.db.favorites.delete_one({"email": email, "exercise_id": exercise.get("exercise_id")})
                return jsonify({"status": "success"})


        else:
            return jsonify({"status": "error", "message": "Exercise not found"})
    else:
        return redirect(url_for('login'))

    return json.dumps({'status': False}), 500, {
        'ContentType:': 'application/json'
    }

@app.route('/favorites')
def favorites():
    email = session.get('email')
    if not email:
        # Redirect the user to the login page or show an error message
        return redirect(url_for('login'))

    # Query MongoDB to get the user's favorite exercises
    favorite_exercises = mongo.db.favorites.find({"email": email})

    return render_template('favorites.html', favorite_exercises=favorite_exercises)
    

@app.route("/yoga", methods=['GET', 'POST'])
def yoga():
    # ############################
    # yoga() function displays the yoga.html template
    # route "/yoga" will redirect to yoga() function.
    # A page showing details about yoga is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        activity = "yoga"
        userEnrolledStatus = mongo.db.user_activity.find_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
        if userEnrolledStatus is None: 
            enrolled = False
            form = EnrollForm()
            if form.validate_on_submit():
                if request.method == 'POST':
                    mongo.db.user_activity.insert({'Email': email, 'Activity': activity, 'Status': "Enrolled", 'Date': date.today().strftime('%Y-%m-%d')})
                flash(
                    f' You have succesfully enrolled in our {activity} plan!',
                    'success')
                activity_cursor = findActivities(email)
                activities = [
                    {"name": activity.get("Activity", "Unknown"), 
                    "status": activity.get("Status", "Unknown"), 
                    "date": activity.get("Date", "Unknown")}
                    for activity in activity_cursor
                ]

                    
                return render_template('new_dashboard.html', form=form, activities=activities)
                # return redirect(url_for('dashboard'))
        else :
            enrolled = True
            form = UnenrollForm()
            if form.validate_on_submit():
                if form.submit.data : 
                    if request.method == 'POST':
                        mongo.db.user_activity.remove({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
                    flash(
                        f' You have succesfully unenrolled in our {activity} plan!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)
                elif form.completed.data:
                    achievment = None
                    if request.method == 'POST':
                        achievment = updateAchievments(activity, email, mongo.db)
                        mongo.db.user_activity.update_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"}, 
                                                        {'$set': {'Status': 'Completed', 'Date': date.today().strftime('%Y-%m-%d')}})
                    flash(
                        f' You have succesfully completed the {activity} plan!',
                        'success')
                    if achievment is not None:
                        flash(
                        f' Woohoooo!!!! You have earned {achievment["name"]} achievement! Go to your Achievements Page to view all your Achievements!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)

        return render_template('yoga.html', title='Yoga', form=form, enrolled=enrolled)
    else:
        return redirect(url_for('dashboard'))


@app.route("/headspace", methods=['GET', 'POST'])
def headspace():
    # ############################
    # headspace() function displays the headspace.html template
    # route "/headspace" will redirect to headspace() function.
    # A page showing details about headspace is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        activity = "headspace"
        userEnrolledStatus = mongo.db.user_activity.find_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
        if userEnrolledStatus is None: 
            enrolled = False
            form = EnrollForm()
            if form.validate_on_submit():
                if request.method == 'POST':
                    mongo.db.user_activity.insert({'Email': email, 'Activity': activity, 'Status': "Enrolled", 'Date': date.today().strftime('%Y-%m-%d')})
                flash(
                    f' You have succesfully enrolled in our {activity} plan!',
                    'success')
                activity_cursor = findActivities(email)
                activities = [
                    {"name": activity.get("Activity", "Unknown"), 
                    "status": activity.get("Status", "Unknown"), 
                    "date": activity.get("Date", "Unknown")}
                    for activity in activity_cursor
                ]
                return render_template('new_dashboard.html', form=form, activities=activities)
                # return redirect(url_for('dashboard'))
        else :
            enrolled = True
            form = UnenrollForm()
            if form.validate_on_submit():
                if form.submit.data : 
                    if request.method == 'POST':
                        mongo.db.user_activity.remove({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
                    flash(
                        f' You have succesfully unenrolled in our {activity} plan!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)
                elif form.completed.data:
                    achievment = None
                    if request.method == 'POST':
                        achievment = updateAchievments(activity, email, mongo.db)
                        mongo.db.user_activity.update_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"}, 
                                                        {'$set': {'Status': 'Completed', 'Date': date.today().strftime('%Y-%m-%d')}})
                    flash(
                        f' You have succesfully completed the {activity} plan!',
                        'success')
                    if achievment is not None:
                        flash(
                        f' Woohoooo!!!! You have earned {achievment["name"]} achievement! Go to your Achievements Page to view all your Achievements!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)

        return render_template('Headspace.html', title='Headspace', form=form, enrolled=enrolled)
    else:
        return redirect(url_for('dashboard'))


@app.route("/mbsr", methods=['GET', 'POST'])
def mbsr():
    # ############################
    # headspace() function displays the headspace.html template
    # route "/headspace" will redirect to headspace() function.
    # A page showing details about headspace is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        activity = "msbr"
        userEnrolledStatus = mongo.db.user_activity.find_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
        if userEnrolledStatus is None: 
            enrolled = False
            form = EnrollForm()
            if form.validate_on_submit():
                if request.method == 'POST':
                    mongo.db.user_activity.insert({'Email': email, 'Activity': activity, 'Status': "Enrolled", 'Date': date.today().strftime('%Y-%m-%d')})
                flash(
                    f' You have succesfully enrolled in our {activity} plan!',
                    'success')
                activity_cursor = findActivities(email)
                activities = [
                    {"name": activity.get("Activity", "Unknown"), 
                    "status": activity.get("Status", "Unknown"), 
                    "date": activity.get("Date", "Unknown")}
                    for activity in activity_cursor
                ]
                return render_template('new_dashboard.html', form=form, activities=activities)
                # return redirect(url_for('dashboard'))
        else :
            enrolled = True
            form = UnenrollForm()
            if form.validate_on_submit():
                if form.submit.data : 
                    if request.method == 'POST':
                        mongo.db.user_activity.remove({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
                    flash(
                        f' You have succesfully unenrolled in our {activity} plan!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)
                elif form.completed.data:
                    achievment = None
                    if request.method == 'POST':
                        achievment = updateAchievments(activity, email, mongo.db)
                        mongo.db.user_activity.update_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"}, 
                                                        {'$set': {'Status': 'Completed', 'Date': date.today().strftime('%Y-%m-%d')}})
                    flash(
                        f' You have succesfully completed the {activity} plan!',
                        'success')
                    if achievment is not None:
                        flash(
                        f' Woohoooo!!!! You have earned {achievment["name"]} achievement! Go to your Achievements Page to view all your Achievements!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)

        return render_template('mbsr.html', title='mbsr', form=form, enrolled=enrolled)
    else:
        return redirect(url_for('dashboard'))


@app.route("/swim", methods=['GET', 'POST'])
def swim():
    # ############################
    # swim() function displays the swim.html template
    # route "/swim" will redirect to swim() function.
    # A page showing details about swimming is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        activity = "swimming"
        userEnrolledStatus = mongo.db.user_activity.find_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
        if userEnrolledStatus is None: 
            enrolled = False
            form = EnrollForm()
            if form.validate_on_submit():
                if request.method == 'POST':
                    mongo.db.user_activity.insert({'Email': email, 'Activity': activity, 'Status': "Enrolled", 'Date': date.today().strftime('%Y-%m-%d')})
                flash(
                    f' You have succesfully enrolled in our {activity} plan!',
                    'success')
                activity_cursor = findActivities(email)
                activities = [
                    {"name": activity.get("Activity", "Unknown"), 
                    "status": activity.get("Status", "Unknown"), 
                    "date": activity.get("Date", "Unknown")}
                    for activity in activity_cursor
                ]
                return render_template('new_dashboard.html', form=form, activities=activities)
                # return redirect(url_for('dashboard'))
        else :
            enrolled = True
            form = UnenrollForm()
            if form.validate_on_submit():
                if form.submit.data : 
                    if request.method == 'POST':
                        mongo.db.user_activity.remove({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
                    flash(
                        f' You have succesfully unenrolled in our {activity} plan!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)
                elif form.completed.data:
                    achievment = None
                    if request.method == 'POST':
                        achievment = updateAchievments(activity, email, mongo.db)
                        mongo.db.user_activity.update_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"}, 
                                                        {'$set': {'Status': 'Completed', 'Date': date.today().strftime('%Y-%m-%d')}})
                    flash(
                        f' You have succesfully completed the {activity} plan!',
                        'success')
                    if achievment is not None:
                        flash(
                        f' Woohoooo!!!! You have earned {achievment["name"]} achievement! Go to your Achievements Page to view all your Achievements!',
                        'success')     
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)

        return render_template('swim.html', title='Swim', form=form, enrolled=enrolled)
    else:
        return redirect(url_for('dashboard'))


@app.route("/abbs", methods=['GET', 'POST'])
def abbs():
    # ############################
    # abbs() function displays the abbs.html template
    # route "/abbs" will redirect to abbs() function.
    # A page showing details about abbs workout is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        activity = "abbs"
        userEnrolledStatus = mongo.db.user_activity.find_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
        if userEnrolledStatus is None: 
            enrolled = False
            form = EnrollForm()
            if form.validate_on_submit():
                if request.method == 'POST':
                    mongo.db.user_activity.insert({'Email': email, 'Activity': activity, 'Status': "Enrolled", 'Date': date.today().strftime('%Y-%m-%d')})
                flash(
                    f' You have succesfully enrolled in our {activity} plan!',
                    'success')
                activity_cursor = findActivities(email)
                activities = [
                    {"name": activity.get("Activity", "Unknown"), 
                    "status": activity.get("Status", "Unknown"), 
                    "date": activity.get("Date", "Unknown")}
                    for activity in activity_cursor
                ]
                return render_template('new_dashboard.html', form=form, activities=activities)
                # return redirect(url_for('dashboard'))
        else :
            enrolled = True
            form = UnenrollForm()
            if form.validate_on_submit():
                if form.submit.data : 
                    if request.method == 'POST':
                        mongo.db.user_activity.remove({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
                    flash(
                        f' You have succesfully unenrolled in our {activity} plan!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)
                elif form.completed.data:
                    achievment = None
                    if request.method == 'POST':
                        achievment = updateAchievments(activity, email, mongo.db)
                        mongo.db.user_activity.update_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"}, 
                                                        {'$set': {'Status': 'Completed', 'Date': date.today().strftime('%Y-%m-%d')}})
                    flash(
                        f' You have succesfully completed the {activity} plan!',
                        'success')
                    if achievment is not None:
                        flash(
                        f' Woohoooo!!!! You have earned {achievment["name"]} achievement! Go to your Achievements Page to view all your Achievements!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)

        return render_template('abbs.html', title='Abbs Smash!', form=form, enrolled=enrolled)
    else:
        return redirect(url_for('dashboard'))


@app.route("/belly", methods=['GET', 'POST'])
def belly():
    # ############################
    # belly() function displays the belly.html template
    # route "/belly" will redirect to belly() function.
    # A page showing details about belly workout is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        activity = "belly"
        userEnrolledStatus = mongo.db.user_activity.find_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
        if userEnrolledStatus is None: 
            enrolled = False
            form = EnrollForm()
            if form.validate_on_submit():
                if request.method == 'POST':
                    mongo.db.user_activity.insert({'Email': email, 'Activity': activity, 'Status': "Enrolled", 'Date': date.today().strftime('%Y-%m-%d')})
                flash(
                    f' You have succesfully enrolled in our {activity} plan!',
                    'success')
                activity_cursor = findActivities(email)
                activities = [
                    {"name": activity.get("Activity", "Unknown"), 
                    "status": activity.get("Status", "Unknown"), 
                    "date": activity.get("Date", "Unknown")}
                    for activity in activity_cursor
                ]
                return render_template('new_dashboard.html', form=form, activities=activities)
                # return redirect(url_for('dashboard'))
        else :
            enrolled = True
            form = UnenrollForm()
            if form.validate_on_submit():
                if form.submit.data : 
                    if request.method == 'POST':
                        mongo.db.user_activity.remove({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
                    flash(
                        f' You have succesfully unenrolled in our {activity} plan!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)
                elif form.completed.data:
                    achievment = None
                    if request.method == 'POST':
                        achievment = updateAchievments(activity, email, mongo.db)
                        mongo.db.user_activity.update_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"}, 
                                                        {'$set': {'Status': 'Completed', 'Date': date.today().strftime('%Y-%m-%d')}})
                    flash(
                        f' You have succesfully completed the {activity} plan!',
                        'success')
                    if achievment is not None:
                        flash(
                        f' Woohoooo!!!! You have earned {achievment["name"]} achievement! Go to your Achievements Page to view all your Achievements!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)

        return render_template('belly.html', title='Belly Burner', form=form, enrolled=enrolled)
        
    else:
        return redirect(url_for('dashboard'))


@app.route("/core", methods=['GET', 'POST'])
def core():
    # ############################
    # core() function displays the belly.html template
    # route "/core" will redirect to core() function.
    # A page showing details about core workout is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        activity = "core"
        userEnrolledStatus = mongo.db.user_activity.find_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
        if userEnrolledStatus is None: 
            enrolled = False
            form = EnrollForm()
            if form.validate_on_submit():
                if request.method == 'POST':
                    mongo.db.user_activity.insert({'Email': email, 'Activity': activity, 'Status': "Enrolled", 'Date': date.today().strftime('%Y-%m-%d')})
                flash(
                    f' You have succesfully enrolled in our {activity} plan!',
                    'success')
                activity_cursor = findActivities(email)
                activities = [
                    {"name": activity.get("Activity", "Unknown"), 
                    "status": activity.get("Status", "Unknown"), 
                    "date": activity.get("Date", "Unknown")}
                    for activity in activity_cursor
                ]
                return render_template('new_dashboard.html', form=form, activities=activities)
                # return redirect(url_for('dashboard'))
        else :
            enrolled = True
            form = UnenrollForm()
            if form.validate_on_submit():
                if form.submit.data : 
                    if request.method == 'POST':
                        mongo.db.user_activity.remove({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
                    flash(
                        f' You have succesfully unenrolled in our {activity} plan!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)
                elif form.completed.data:
                    achievment = None
                    if request.method == 'POST':
                        achievment = updateAchievments(activity, email, mongo.db)
                        mongo.db.user_activity.update_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"}, 
                                                        {'$set': {'Status': 'Completed', 'Date': date.today().strftime('%Y-%m-%d')}})
                    flash(
                        f' You have succesfully completed the {activity} plan!',
                        'success')
                    if achievment is not None:
                        flash(
                        f' Woohoooo!!!! You have earned {achievment["name"]} achievement! Go to your Achievements Page to view all your Achievements!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)

        return render_template('core.html', title='Core Conditioning', form=form, enrolled=enrolled)
    else:
        return redirect(url_for('dashboard'))


@app.route("/gym", methods=['GET', 'POST'])
def gym():
    # ############################
    # gym() function displays the gym.html template
    # route "/gym" will redirect to gym() function.
    # A page showing details about gym plan is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        activity = "gym"
        userEnrolledStatus = mongo.db.user_activity.find_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
        if userEnrolledStatus is None: 
            enrolled = False
            form = EnrollForm()
            if form.validate_on_submit():
                if request.method == 'POST':
                    mongo.db.user_activity.insert({'Email': email, 'Activity': activity, 'Status': "Enrolled", 'Date': date.today().strftime('%Y-%m-%d')})
                flash(
                    f' You have succesfully enrolled in our {activity} plan!',
                    'success')
                activity_cursor = findActivities(email)
                activities = [
                    {"name": activity.get("Activity", "Unknown"), 
                    "status": activity.get("Status", "Unknown"), 
                    "date": activity.get("Date", "Unknown")}
                    for activity in activity_cursor
                ]
                return render_template('new_dashboard.html', form=form, activities=activities)
                # return redirect(url_for('dashboard'))
        else :
            enrolled = True
            form = UnenrollForm()
            if form.validate_on_submit():
                if form.submit.data : 
                    if request.method == 'POST':
                        mongo.db.user_activity.remove({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
                    flash(
                        f' You have succesfully unenrolled in our {activity} plan!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)
                elif form.completed.data:
                    achievment = None
                    if request.method == 'POST':
                        achievment = updateAchievments(activity, email, mongo.db)
                        mongo.db.user_activity.update_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"}, 
                                                        {'$set': {'Status': 'Completed', 'Date': date.today().strftime('%Y-%m-%d')}})
                    flash(
                        f' You have succesfully completed the {activity} plan!',
                        'success')
                    if achievment is not None:
                        flash(
                        f' Woohoooo!!!! You have earned {achievment["name"]} achievement! Go to your Achievements Page to view all your Achievements!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)

        return render_template('gym.html', title='Gym', form=form, enrolled=enrolled)
    else:
        return redirect(url_for('dashboard'))

@app.route("/walk", methods=['GET', 'POST'])
def walk():
    # ############################
    # walk() function displays the walk.html template
    # route "/walk" will redirect to walk() function.
    # A page showing details about walk plan is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        activity = "walk"
        userEnrolledStatus = mongo.db.user_activity.find_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
        if userEnrolledStatus is None: 
            enrolled = False
            form = EnrollForm()
            if form.validate_on_submit():
                if request.method == 'POST':
                    mongo.db.user_activity.insert({'Email': email, 'Activity': activity, 'Status': "Enrolled", 'Date': date.today().strftime('%Y-%m-%d')})
                flash(
                    f' You have succesfully enrolled in our {activity} plan!',
                    'success')
                activity_cursor = findActivities(email)
                activities = [
                    {"name": activity.get("Activity", "Unknown"), 
                    "status": activity.get("Status", "Unknown"), 
                    "date": activity.get("Date", "Unknown")}
                    for activity in activity_cursor
                ]
                return render_template('new_dashboard.html', form=form, activities=activities)
                # return redirect(url_for('dashboard'))
        else :
            enrolled = True
            form = UnenrollForm()
            if form.validate_on_submit():
                if form.submit.data : 
                    if request.method == 'POST':
                        mongo.db.user_activity.remove({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
                    flash(
                        f' You have succesfully unenrolled in our {activity} plan!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)
                elif form.completed.data:
                    achievment = None
                    if request.method == 'POST':
                        achievment = updateAchievments(activity, email, mongo.db)
                        mongo.db.user_activity.update_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"}, 
                                                        {'$set': {'Status': 'Completed', 'Date': date.today().strftime('%Y-%m-%d')}})
                    flash(
                        f' You have succesfully completed the {activity} plan!',
                        'success')
                    if achievment is not None:
                        flash(
                        f' Woohoooo!!!! You have earned {achievment["name"]} achievement! Go to your Achievements Page to view all your Achievements!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)

        return render_template('walk.html', title='Walk', form=form, enrolled=enrolled)
    else:
        return redirect(url_for('dashboard'))

@app.route("/dance", methods=['GET', 'POST'])
def dance():
    # ############################
    # dance() function displays the dance.html template
    # route "/dance" will redirect to dance() function.
    # A page showing details about dance plan is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        activity = "dance"
        userEnrolledStatus = mongo.db.user_activity.find_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
        if userEnrolledStatus is None: 
            enrolled = False
            form = EnrollForm()
            if form.validate_on_submit():
                if request.method == 'POST':
                    mongo.db.user_activity.insert({'Email': email, 'Activity': activity, 'Status': "Enrolled", 'Date': date.today().strftime('%Y-%m-%d')})
                flash(
                    f' You have succesfully enrolled in our {activity} plan!',
                    'success')
                activity_cursor = findActivities(email)
                activities = [
                    {"name": activity.get("Activity", "Unknown"), 
                    "status": activity.get("Status", "Unknown"), 
                    "date": activity.get("Date", "Unknown")}
                    for activity in activity_cursor
                ]
                return render_template('new_dashboard.html', form=form, activities=activities)
                # return redirect(url_for('dashboard'))
        else :
            enrolled = True
            form = UnenrollForm()
            if form.validate_on_submit():
                if form.submit.data : 
                    if request.method == 'POST':
                        mongo.db.user_activity.remove({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
                    flash(
                        f' You have succesfully unenrolled in our {activity} plan!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)
                elif form.completed.data:
                    achievment = None
                    if request.method == 'POST':
                        achievment = updateAchievments(activity, email, mongo.db)
                        mongo.db.user_activity.update_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"}, 
                                                        {'$set': {'Status': 'Completed', 'Date': date.today().strftime('%Y-%m-%d')}})
                    flash(
                        f' You have succesfully completed the {activity} plan!',
                        'success')
                    if achievment is not None:
                        flash(
                        f' Woohoooo!!!! You have earned {achievment["name"]} achievement! Go to your Achievements Page to view all your Achievements!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)

        return render_template('dance.html', title='Dance', form=form, enrolled=enrolled)
    else:
        return redirect(url_for('dashboard'))

@app.route("/hrx", methods=['GET', 'POST'])
def hrx():
    # ############################
    # hrx() function displays the hrx.html template
    # route "/hrx" will redirect to hrx() function.
    # A page showing details about hrx plan is shown and if clicked on enroll then DB updation done and redirected to new_dashboard
    # Input: Email
    # Output: DB entry about enrollment and redirected to new dashboard
    # ##########################
    email = get_session = session.get('email')
    if get_session is not None:
        activity = "hrx"
        userEnrolledStatus = mongo.db.user_activity.find_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
        if userEnrolledStatus is None: 
            enrolled = False
            form = EnrollForm()
            if form.validate_on_submit():
                if request.method == 'POST':
                    mongo.db.user_activity.insert({'Email': email, 'Activity': activity, 'Status': "Enrolled", 'Date': date.today().strftime('%Y-%m-%d')})
                flash(
                    f' You have succesfully enrolled in our {activity} plan!',
                    'success')
                activity_cursor = findActivities(email)
                activities = [
                    {"name": activity.get("Activity", "Unknown"), 
                    "status": activity.get("Status", "Unknown"), 
                    "date": activity.get("Date", "Unknown")}
                    for activity in activity_cursor
                ]
                return render_template('new_dashboard.html', form=form, activities=activities)
                # return redirect(url_for('dashboard'))
        else :
            enrolled = True
            form = UnenrollForm()
            if form.validate_on_submit():
                if form.submit.data : 
                    if request.method == 'POST':
                        mongo.db.user_activity.remove({'Email': email, 'Activity': activity, 'Status': "Enrolled"})
                    flash(
                        f' You have succesfully unenrolled in our {activity} plan!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)
                elif form.completed.data:
                    achievment = None
                    if request.method == 'POST':
                        achievment = updateAchievments(activity, email, mongo.db)
                        mongo.db.user_activity.update_one({'Email': email, 'Activity': activity, 'Status': "Enrolled"}, 
                                                        {'$set': {'Status': 'Completed', 'Date': date.today().strftime('%Y-%m-%d')}})
                    flash(
                        f' You have succesfully completed the {activity} plan!',
                        'success')
                    if achievment is not None:
                        flash(
                        f' Woohoooo!!!! You have earned {achievment["name"]} achievement! Go to your Achievements Page to view all your Achievements!',
                        'success')
                    activity_cursor = findActivities(email)
                    activities = [
                        {"name": activity.get("Activity", "Unknown"), 
                        "status": activity.get("Status", "Unknown"), 
                        "date": activity.get("Date", "Unknown")}
                        for activity in activity_cursor
                    ]
                    return render_template('new_dashboard.html', form=form, activities=activities)

        return render_template('hrx.html', title='HRX', form=form, enrolled=enrolled)
    else:
        return redirect(url_for('dashboard'))

# @app.route("/ajaxdashboard", methods=['POST'])
# def ajaxdashboard():
#     # ############################
#     # login() function displays the Login form (login.html) template
#     # route "/login" will redirect to login() function.
#     # LoginForm() called and if the form is submitted then various values are fetched and verified from the database entries
#     # Input: Email, Password, Login Type
#     # Output: Account Authentication and redirecting to Dashboard
#     # ##########################
#     email = get_session = session.get('email')
#     print(email)
#     if get_session is not None:
#         if request.method == "POST":
#             result = mongo.db.user.find_one(
#                 {'email': email}, {'email', 'Status'})
#             if result:
#                 return json.dumps({'email': result['email'], 'Status': result['result']}), 200, {
#                     'ContentType': 'application/json'}
#             else:
#                 return json.dumps({'email': "", 'Status': ""}), 200, {
#                     'ContentType': 'application/json'}

@app.route("/review", methods=['GET', 'POST'])
def submit_reviews():
    # ############################
    # submit_reviews() function collects and displays the reviews submitted by different users
    # route "/review" will redirect to submit_review() function which redirects to review.html page.
    # Reviews are stored into a MongoDB collection and then retrieved immediately
    # Input: Email
    # Output: Name, Review
    # ##########################
    existing_reviews = mongo.db.reviews.find()
    if session.get('email'):
        print("Imhere2")
        if request.method == 'POST':  # Check if it's a POST request
            form = ReviewForm(request.form)  # Initialize the form with form data
            if form.validate_on_submit():
                print("imehere1")
                email = session.get('email')
                user = mongo.db.user.find_one({'email': email})
                name = request.form.get('name')
                review = request.form.get('review')  # Correct the field name
                mongo.db.reviews.insert_one({'name': name, 'review': review})
                return render_template("review.html", form=form, existing_reviews=existing_reviews)
        else:
            form = ReviewForm()  # Create an empty form for GET requests
        return render_template('review.html', form=form, existing_reviews=existing_reviews)
    else:
        return "User not logged in"

@app.route('/blog')
def blog():
    # 处理 "blog" 页面的逻辑
    return render_template('blog.html')

def findActivities(email):
    activities = mongo.db.user_activity.find({'Email': email})
    return activities

if __name__ == '__main__':
    app.run(debug=True)