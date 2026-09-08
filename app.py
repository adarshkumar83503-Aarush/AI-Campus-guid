import random
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Student Database with Registered Email / Phone
STUDENTS_DB = {
    "25116CN001": {"name": "Adarsh", "email": "adarshkumar83503@gmail.com", "phone": "9696082530"},
    "25116CN407": {"name": "Akansha", "email": "akanshasingh16806@gmail.com", "phone": "8445446575"},
    "25116CN091": {"name": "Aisha", "email": "pandeyaisha829@gmail.com", "phone": "8840047689"},
    "25116CN029": {" name": "Aditya","email":"aditya33322@gmail.com", " phone": "7307360489"}
}

# Temporary OTP Store: { "GLB2023001": {"otp": "482910", "expires": timestamp} }
OTP_STORE = {}

CAMPUS_DATA = {
    "library": {
        "name": "Central Library (GL Bajaj)",
        "block": "Main Academic Block",
        "floor": "Ground / 1st Floor",
        "lat": 28.4728,
        "lng": 77.4897,
        "indoor": "Main entrance -> Right wing corridor -> Central Library.",
        "keywords": ["library", "book", "padhne", "study", "kitab"]
    },
    "canteen": {
        "name": "Campus Cafeteria & Food Court",
        "block": "Near PGDM / Hostel Area",
        "floor": "Ground Floor",
        "lat": 28.4722,
        "lng": 77.4892,
        "indoor": "Academic block ke piche garden area cross karke seedha Canteen.",
        "keywords": ["canteen", "food", "khana", "lunch", "cafeteria"]
    },
    "lab": {
        "name": "IT & CSE Computer Labs",
        "block": "Academic Block",
        "floor": "2nd & 3rd Floor",
        "lat": 28.4730,
        "lng": 77.4896,
        "indoor": "Staircase/Lift se 2nd floor -> Lab complex right wing.",
        "keywords": ["lab", "computer", "coding", "it lab", "cs lab"]
    }
}

@app.route("/")
def home():
    formatted_locations = {
        k: {"name": v["name"], "lat": v["lat"], "lng": v["lng"], "desc": f"{v['block']} ({v['floor']})"}
        for k, v in CAMPUS_DATA.items()
    }
    return render_template("index.html", locations=formatted_locations)

# Step 1: Send OTP Endpoint
@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json or {}
    admission_no = data.get("admission_no", "").strip().upper()

    if admission_no not in STUDENTS_DB:
        return jsonify({"success": False, "message": "Admission Number college record me nahi mila!"})

    # 6-Digit Random OTP Generate karein
    otp = str(random.randint(100000, 999999))
    OTP_STORE[admission_no] = {
        "otp": otp,
        "expires": time.time() + 300  # 5 minute valid
    }

    student_info = STUDENTS_DB[admission_no]

    # Console me print karein (testing ke liye)
    print(f"\n==========================================")
    print(f"🔐 OTP for {student_info['name']} ({admission_no}): {otp}")
    print(f"==========================================\n")

    # Real implementation me yahan email send hota hai.
    # Demo ke liye hum masked email aur OTP response me bhej rahe hain taaki test karna aasan ho.
    masked_email = student_info["email"][:3] + "****@" + student_info["email"].split("@")[1]
    
    return jsonify({
        "success": True,
        "message": f"OTP successfully sent to {masked_email}",
        "demo_otp": otp  # Testing/Viva me turant use karne ke liye
    })

# Step 2: Verify OTP Endpoint
@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json or {}
    admission_no = data.get("admission_no", "").strip().upper()
    user_otp = data.get("otp", "").strip()

    if admission_no not in OTP_STORE:
        return jsonify({"success": False, "message": "Pehle OTP request karein!"})

    record = OTP_STORE[admission_no]

    if time.time() > record["expires"]:
        del OTP_STORE[admission_no]
        return jsonify({"success": False, "message": "OTP expire ho gaya! Dobara bhejein."})

    if user_otp == record["otp"]:
        del OTP_STORE[admission_no]
        student_name = STUDENTS_DB[admission_no]["name"]
        return jsonify({
            "success": True, 
            "message": f"Verification Successful! Welcome {student_name}",
            "student_name": student_name
        })

    return jsonify({"success": False, "message": "Galat OTP! Kripya sahi OTP dalein."})

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

    return jsonify({"reply": "Location nahi mili. Library, Canteen ya Lab try karein.", "lat": None, "lng": None})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
