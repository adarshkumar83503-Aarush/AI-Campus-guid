import random
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Valid Student Database
STUDENTS_DB = {
    "25116cn001": {"name": "Adarsh", "email": "adarshkumar83503@gmail.com"},
    "2023BT0101": {"name": "Student 2", "email": "student2@glbajaj.org"},
    "GLB001": {"name": "Adarsh", "email": "adarsh@glbajaj.org"}
}

# Temporary OTP Store
OTP_STORE = {}

# GL Bajaj Campus Coordinates & Data
CAMPUS_DATA = {
    "library": {
        "name": "Central Library (GL Bajaj)",
        "block": "Main Academic Block",
        "floor": "Ground / 1st Floor",
        "lat": 28.4728,
        "lng": 77.4897,
        "indoor": "Main entrance se enter karein -> Right wing corridor -> Central Library.",
        "keywords": ["library", "book", "padhne", "study", "kitab"]
    },
    "canteen": {
        "name": "Campus Cafeteria & Food Court",
        "block": "Near PGDM / Hostel Area",
        "floor": "Ground Floor",
        "lat": 28.4722,
        "lng": 77.4892,
        "indoor": "Academic block ke piche garden cross karke seedha Canteen entrance.",
        "keywords": ["canteen", "food", "khana", "lunch", "cafeteria", "chai"]
    },
    "lab": {
        "name": "IT & CSE Computer Labs",
        "block": "Academic Block",
        "floor": "2nd & 3rd Floor",
        "lat": 28.4730,
        "lng": 77.4896,
        "indoor": "Staircase/Lift se 2nd floor -> Lab complex right wing me hai.",
        "keywords": ["lab", "computer", "coding", "it lab", "cs lab", "practical"]
    },
    "placement": {
        "name": "Training & Placement Cell (T&P)",
        "block": "Admin / Main Block",
        "floor": "Ground Floor",
        "lat": 28.4726,
        "lng": 77.4899,
        "indoor": "Admin building reception ke paas T&P executive block.",
        "keywords": ["placement", "job", "interview", "t&p", "internship"]
    }
}

@app.route("/")
def home():
    formatted_locations = {
        k: {"name": v["name"], "lat": v["lat"], "lng": v["lng"], "desc": f"{v['block']} ({v['floor']})"}
        for k, v in CAMPUS_DATA.items()
    }
    return render_template("index.html", locations=formatted_locations)

@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json or {}
    admission_no = data.get("admission_no", "").strip().upper()

    # Agar list me nahi hai par GLB se start hota hai tab bhi allow karein testing ke liye
    if admission_no not in STUDENTS_DB:
        if admission_no.startswith("GLB") and len(admission_no) >= 5:
            STUDENTS_DB[admission_no] = {"name": f"Student ({admission_no})", "email": "student@glbajaj.org"}
        else:
            return jsonify({"success": False, "message": "Galat Admission No! (Demo ID: GLB2023001)"})

    # 6-digit OTP
    otp = str(random.randint(100000, 999999))
    OTP_STORE[admission_no] = {
        "otp": otp,
        "expires": time.time() + 300
    }

    return jsonify({
        "success": True,
        "message": "OTP generated successfully!",
        "otp": otp
    })

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json or {}
    admission_no = data.get("admission_no", "").strip().upper()
    user_otp = data.get("otp", "").strip()

    if admission_no not in OTP_STORE:
        return jsonify({"success": False, "message": "Pehle OTP request karein."})

    record = OTP_STORE[admission_no]

    if time.time() > record["expires"]:
        del OTP_STORE[admission_no]
        return jsonify({"success": False, "message": "OTP expire ho gaya. Dobara bhejein."})

    if user_otp == record["otp"]:
        del OTP_STORE[admission_no]
        student_name = STUDENTS_DB[admission_no]["name"]
        return jsonify({
            "success": True, 
            "message": f"Welcome, {student_name}!",
            "student_name": student_name
        })

    return jsonify({"success": False, "message": "Galat OTP! Kripya sahi 6-digit OTP dalein."})

@app.route("/chat", methods=["POST"])
def chat():
    user_query = request.json.get("message", "").lower().strip()
    matched = None
    for key, data in CAMPUS_DATA.items():
        if any(word in user_query for word in data["keywords"]) or key in user_query:
            matched = data
            break

    if matched:
        reply_text = f"📍 {matched['name']}\n🏢 {matched['block']} - {matched['floor']}\n🚶 {matched['indoor']}"
        return jsonify({"reply": reply_text, "lat": matched["lat"], "lng": matched["lng"]})

    return jsonify({"reply": "Jagah nahi mili. Library, Canteen ya CS Lab try karein.", "lat": None, "lng": None})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
