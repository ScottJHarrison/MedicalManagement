from urllib.parse import urlencode

from flask import Flask, render_template, url_for, request, redirect, jsonify, session, redirect, send_from_directory
import pymongo
from bson import ObjectId, json_util
import json
from flask_mail import Mail, Message
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import csv
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = '123654'
app.config['SECRET_KEY'] = '123654'

bcrypt = Bcrypt(app)


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["medical_management"]
timetable_collection = db["timetable"]
requests_collection = db["requests"]
users_collection = db["users"]
patients_collection = db["patients"]
staff_collection = db["staff"]
reviews_collection = db["reviews"]


######################################################################################################
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # Specify the name of the login view


class User(UserMixin):
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def get_id(self):
        return self.email


# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({'email': user_id})
    if user:
        return User(user['email'], user['password'])
    return None


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            return 'This email address is already registered.'

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users_collection.insert_one({'email': email, 'password': hashed_password})
        user = load_user(email)
        login_user(user)

        send_confirmation_email2(email)

        return redirect(url_for('requests_page'))
    return render_template('register.html')

def send_confirmation_email2(user_email):
    # Send confirmation email to user
    msg = Message(
        'Welcome to our application!',
        recipients=["scott.j.harrison18@gmail.com"]  # Use the user's email as the recipient
    )
    msg.body = f'Hi, thank you for registering with us! Your registered email address is {user_email}.'

    mail.send(msg)

    return jsonify({"status": "success", "message": "Request submitted"}), 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = load_user(email)

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('requests_page'))

        return 'Invalid email or password.'

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


####################################################################################################

@app.route("/timetable_page", methods=["GET"])
@login_required
def timetable_page():
    return render_template("timetable.html")


@app.route("/requests", methods=["GET"])
@login_required
def requests_page():
    return render_template("requests.html")


@app.route("/patientrec", methods=["GET"])
@login_required
def patientrec_page():
    return render_template("records.html")


@app.route("/home", methods=["GET"])
def home():
    return render_template("home.html")


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")

@app.route("/feedback", methods=["GET"])
def feedback():
    return render_template("feedback.html")


# Helper function to convert ObjectId to str
def convert_objectid_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    return obj


# Route to add a new time slot
@app.route('/timetable/add', methods=['POST'])
def add_time_slot():
    data = request.get_json()
    timetable_collection.insert_one(data)
    return jsonify({"status": "success", "message": "Time slot added"}), 201


# Route to modify an existing time slot
@app.route('/timetable/update/<slot_id>', methods=['PUT'])
def update_time_slot(slot_id):
    data = request.get_json()
    timetable_collection.update_one({"_id": ObjectId(slot_id)}, {"$set": data})
    return jsonify({"status": "success", "message": "Time slot updated"}), 200


# Route to get all time slots
@app.route('/timetable', methods=['GET'])
def get_time_slots():
    time_slots = list(timetable_collection.find())
    for slot in time_slots:
        slot["_id"] = convert_objectid_to_str(slot["_id"])
    return jsonify(time_slots), 200


# Route to get a specific time slot
@app.route('/timetable/<slot_id>', methods=['GET'])
def get_time_slot(slot_id):
    slot = timetable_collection.find_one({"_id": ObjectId(slot_id)})
    if slot:
        slot["_id"] = convert_objectid_to_str(slot["_id"])
        return jsonify(slot), 200
    return jsonify({"status": "error", "message": "Time slot not found"}), 404


# Route to delete a specific time slot
@app.route('/timetable/delete/<slot_id>', methods=['DELETE'])
def delete_time_slot(slot_id):
    result = timetable_collection.delete_one({"_id": ObjectId(slot_id)})
    if result.deleted_count > 0:
        return jsonify({"status": "success", "message": "Time slot deleted"}), 200
    return jsonify({"status": "error", "message": "Time slot not found"}), 404


# Configure email settings
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = "scott.j.harrison18@gmail.com"
app.config["MAIL_PASSWORD"] = "agewlsdflzznegwz"
app.config["MAIL_DEFAULT_SENDER"] = "scott.j.harrison18@gmail.com"

mail = Mail(app)


# New route to handle request form submission
@app.route('/submit_request', methods=['POST'])
def submit_request():
    name = request.form.get("name")
    request_type = request.form.get("request_type")
    request_details = request.form.get("request_details")

    # Save request data to MongoDB
    request_data = {
        'name': name,
        'request_type': request_type,
        'request_details': request_details
    }
    requests_collection.insert_one(request_data)

    msg = Message(
        f"New {request_type.capitalize()} Request",
        recipients=["scott.j.harrison18@gmail.com"]
    )
    msg.body = f"Name: {name}\n\nRequest type: {request_type}\n\nRequest details:\n{request_details}"

    mail.send(msg)

    return jsonify({"status": "success", "message": "Request submitted"}), 200


##########################################################################################
def load_csv_data():
    with open(r'C:\Users\Scott Harrison\PycharmProjects\pythonProject3\static\patients.csv', newline='',
              encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    return data


@app.route('/records')
@login_required
def records():
    csv_data = load_csv_data()
    return render_template('records.html', data=csv_data)

@app.route('/get_patient_records')
def get_patient_records():
    try:
        patients = patients_collection.find()
        patient_list = [json.loads(json_util.dumps(patient)) for patient in patients]
        return jsonify(patient_list)
    except Exception as e:
        print("Error: ", e)
        return jsonify({"error": "An internal server error occurred"}), 500


@app.route('/images/<filename>')
def images(filename):
    return send_from_directory('images', filename)


@app.route('/send_confirmation_email', methods=['POST'])
def send_confirmation_email():
    user_email = request.form['email']
    user_name = request.form['name']

    # Send confirmation email to user
    msg = Message(
        'Welcome to our application!',
        recipients=["scott.j.harrison18@gmail.com"]
    )
    msg.body = f'Hi {user_name}, thank you for registering with us!'

    mail.send(msg)

    return jsonify({"status": "success", "message": "Confirmation email sent"}), 200

@app.route('/submit_review', methods=['POST'])
def submit_review():
    data = request.get_json()
    name = data.get("name")
    stars = data.get("stars")
    review = data.get("review")

    review_data = {
        "name": name,
        "stars": int(stars),
        "review": review,
    }

    reviews_collection.insert_one(review_data)

    return jsonify({"status": "success", "message": "Review submitted"}), 200

@app.route('/load_reviews', methods=['GET'])
def load_reviews():
    reviews = list(reviews_collection.find())
    for review in reviews:
        review["_id"] = convert_objectid_to_str(review["_id"])
    return jsonify(reviews), 200

#####################################################



if __name__ == '__main__':
    app.run(debug=True)
