
from datetime import date

achievements = {
    "yoga": [
        {"name": "Zen Beginner", "required_count": 1, "description": "Attend 1 yoga sessions."},
        {"name": "Flexible Enthusiast", "required_count": 10, "description": "Complete 10 yoga sessions."},
        {"name": "Pose Perfectionist", "required_count": 20, "description": "Complete 20 yoga sessions."},
        {"name": "Flow Champion", "required_count": 30, "description": "Complete 30 yoga sessions."}
    ],
    "swimming": [
        {"name": "Splash Starter", "required_count": 1, "description": "Attend 1 swimming sessions."},
        {"name": "Aqua Adventurer", "required_count": 10, "description": "Attend 10 swimming sessions."},
        {"name": "Water Warrior", "required_count": 20, "description": "Attend 20 swimming sessions."},
        {"name": "Deep Diver", "required_count": 25, "description": "Attend 25 swimming sessions."}
    ],
    "abbs": [
        {"name": "Core Explorer", "required_count": 1, "description": "Attend 1 abs-focused sessions."},
        {"name": "Six-Pack Seeker", "required_count": 20, "description": "Attend 20 abs-focused sessions."},
        {"name": "Iron Core", "required_count": 30, "description": "Attend 30 abs-focused sessions."},
        {"name": "Ab Machine", "required_count": 40, "description": "Attend 40 abs-focused sessions."}
    ],
    "walk": [
        {"name": "Trail Trotter", "required_count": 1, "description": "Attend 1 walk sessions."},
        {"name": "Daily Strider", "required_count": 10, "description": "Attend 10 walk sessions."},
        {"name": "Marathon Mindset", "required_count": 30, "description": "Attend 30 walk sessions."},
    ],
    "belly": [
        {"name": "Burn It Up", "required_count": 1, "description": "Complete 1 belly workout sessions."},
        {"name": "Toned and Strong ", "required_count": 10, "description": "Complete 10 belly workout sessions."},
        {"name": "Routine Regular", "required_count": 20, "description": "Complete 20 belly workout sessions."},
        {"name": "Shred Legend", "required_count": 30, "description": "Complete 30 belly workout sessions."}
    ],
    "dance": [
        {"name": "Groove Beginner", "required_count": 1, "description": "Complete 1 dance sessions."},
        {"name": "Rhythm Master", "required_count": 10, "description": "Complete 10 dance sessions."},
        {"name": "Choreography Ace", "required_count": 20, "description": "Complete 20 dance sessions."},
        {"name": "Stage Ready", "required_count": 30, "description": "Complete 30 dance sessions."}
    ],
    "hrx": [
        {"name": "HIIT Newbie", "required_count": 1, "description": "Complete your first HRX session."},
        {"name": "Calorie Crusher", "required_count": 15, "description": "Complete 15 HRX sessions."},
        {"name": "Endurance Expert", "required_count": 25, "description": "Attend 25 HRX sessions."},
        {"name": "Beast Mode", "required_count": 50, "description": "Complete 50 HRX sessions."}
    ],
    "core": [
        {"name": "Foundation Builder", "required_count": 1, "description": "Complete 1 Core sessions."},
        {"name": "Core Contender", "required_count": 10, "description": "Complete 10 Core sessions."},
        {"name": "Strength Specialist", "required_count": 20, "description": "Complete 20 Core sessions."},
        {"name": "Champion Core", "required_count": 30, "description": "Complete 30 Core sessions."}
    ],
    "gym": [
        {"name": "Lift Beginner", "required_count": 1, "description": "Complete 1 gym workouts."},
        {"name": "Weight Warrior", "required_count": 20, "description": "Complete 20 gym workouts."},
        {"name": "Routine Regular", "required_count": 30, "description": "Complete 30 gym workouts."},
        {"name": "Max Out", "required_count": 50, "description": "Complete 50 gym workouts."}
    ],
    "headspace": [
        {"name": "Mindful Beginner", "required_count": 1, "description": "Attend your first Meditation session."},
        {"name": "Focused Achiever", "required_count": 10, "description": "Complete 10 meditation sessions."},
        {"name": "Clarity Seeker", "required_count": 20, "description": "Complete 20 meditation sessions."},
        {"name": "Zen Master", "required_count": 30, "description": "Complete 30 meditation sessions."}
    ],
    "mbsr": [
        {"name": "Stress Reliever", "required_count": 1, "description": "Complete your first session."},
        {"name": "Calm Practitioner", "required_count": 10, "description": "Complete 10 MSBR sessions."},
        {"name": "Resilient Thinker", "required_count": 20, "description": "Complete 20 MSBR sessions."},
        {"name": "Inner Peace Guru", "required_count": 30, "description": "Complete 30 MSBR sessions."}
    ]
}

def updateAchievments(activity, email, db):
    """
    This function accepts activity name and email address of the user as input and 
    then checks and updates any achievements related to the activity in MongoDB.
    """
    activities = db.user_activity.find({'Email': email, 'Activity': activity, 'Status': "Completed"})
    count = activities.count() + 1

    latest_achievement = None

    for achievement in achievements[activity]:
        if count >= achievement["required_count"]:
            if latest_achievement is None or achievement["required_count"] > latest_achievement["required_count"]:
                latest_achievement = achievement

    if latest_achievement is not None:
        achievementExists = db.achievements.find_one({"Name": latest_achievement["name"], "Email": email})
        
        if achievementExists is None:
            db.achievements.insert({"Name": latest_achievement["name"], "Email": email, "Description": latest_achievement["description"], "Date": date.today().strftime('%Y-%m-%d')})
            return latest_achievement
        
    return None

def getAchievements(email, db):
    """
    This function accepts email address of the user as input and 
    then returns all the achievements earned by the user from MongoDB.
    """

    achievements_cursor = db.achievements.find({"Email": email})
    achievements = [
        {"name": achievement.get("Name", "Unknown"), 
        "date": achievement.get("Date", "Unknown"), 
        "description": achievement.get("Description", "Unknown")}
        for achievement in achievements_cursor
    ]
    
    return achievements