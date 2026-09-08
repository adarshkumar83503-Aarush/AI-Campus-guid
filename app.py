from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Valid Student Admission Numbers List (College DB)
# Aap isme apne college ke admission numbers format ke hisab se aur add kar sakte hain
VALID_STUDENTS = {
    "25116CN001": "Adarsh dubey",
    "25116CN407": "Akansha Singh",
    "25116CN091": "Aisha pandey",
    "25116cn029": "Aditya yadav:",
}

# Campus Places Database (GL Bajaj Campus)
CAMPUS_DATA = {
    "library": {
        "name": "Central Library (GL Bajaj)",
        "block": "Main Academic Block",
        "floor": "Ground / 1st Floor",
        "lat": 28.4728,
        "lng": 77.4897,
        "indoor": "Main entrance se enter karein -> Right wing corridor -> Central Library.",
        "keywords": ["library", "book", "padhne", "study", "kitab", "reading room"]
    },
    "canteen": {
        "name": "Campus Cafeteria & Food Court",
        "block": "Near PGDM / Hostel Area",
        "floor": "Ground Floor",
        "lat": 28.4722,
        "lng": 77.4892,
        "indoor": "Academic block ke piche garden area cross karke seedha Canteen entrance hai.",
        "keywords": ["canteen", "food", "khana", "lunch", "cafeteria", "chai", "nescafe"]
    },
    "lab": {
        "name": "IT & CSE Computer Labs",
        "block": "Academic Block",
        "floor": "2nd & 3rd Floor",
        "lat": 28.4730,
        "lng": 77.4896,
        "indoor": "Staircase/Lift se 2nd floor jayein -> Lab complex right wing me hai.",
        "keywords": ["lab", "computer", "coding", "it lab", "cs lab", "practical", "programming"]
    },
    "placement": {
        "name": "Training & Placement Cell (T&P)",
        "block": "Admin / Main Block",
        "floor": "Ground Floor",
        "lat": 28.4726,
        "lng": 77.4899,
        "indoor": "Admin building reception ke paas T&P executive block.",
        "keywords": ["placement", "job", "interview", "t&p", "internship", "crc"]
    },
    "admin": {
        "name": "Registrar Office & Accounts",
        "block": "Admin Block",
        "floor": "Ground Floor",
        "lat": 28.4725,
        "lng": 77.4898,
        "indoor": "Main reception gate se enter karte hi saamne fee counter aur registrar desk hai.",
        "keywords": ["admin", "office", "fee", "fees", "admit card", "exam cell", "registrar"]
    }
}

@app.route("/")
def home():
    formatted_locations = {
        k: {"name": v["name"], "lat": v["lat"], "lng": v["lng"], "desc": f"{v['block']} ({v['floor']})"}
        for k, v in CAMPUS_DATA.items()
    }
    return render_template("index.html", locations=formatted_locations)

@app.route("/login", methods=["POST"])
def student_login():
    data = request.json or {}
    admission_no = data.get("admission_no", "").strip().upper()
    
    # Check if exists in valid list OR starts with college prefix pattern (e.g., GLB or 20)
    if admission_no in VALID_STUDENTS:
        student_name = VALID_STUDENTS[admission_no]
        return jsonify({"success": True, "message": f"Welcome, {student_name}!", "admission_no": admission_no})
    
    # Generic rule-based fallback check (e.g. GLB followed by numbers or 10-digit admission number)
    if admission_no.startswith("GLB") and len(admission_no) >= 6:
        return jsonify({"success": True, "message": f"Welcome Student ({admission_no})!", "admission_no": admission_no})

    return jsonify({"success": False, "message": "Invalid Admission Number! Kripya sahi Admission No. darj karein."})

@app.route("/chat", methods=["POST"])
def chat():
    user_query = request.json.get("message", "").lower().strip()
    
    matched = None
    for key, data in CAMPUS_DATA.items():
        if any(word in user_query for word in data["keywords"]) or key in user_query:
            matched = data
            break

    if matched:
        reply_text = (
            f"📍 {matched['name']}\n"
            f"🏢 Location: {matched['block']} - {matched['floor']}\n"
            f"🚶 Route: {matched['indoor']}"
        )
        return jsonify({
            "reply": reply_text,
            "lat": matched["lat"],
            "lng": matched["lng"]
        })

    return jsonify({
        "reply": "Maaf kijiye, ye jagah campus database me nahi mili. Aap Library, Canteen, Computer Lab, ya Placement Cell try kar sakte hain.",
        "lat": None,
        "lng": None
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
