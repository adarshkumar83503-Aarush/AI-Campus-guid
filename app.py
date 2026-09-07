from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Campus Places Database
CAMPUS_DATA = {
    "library": {
        "name": "Central Library",
        "block": "Block 1 (Academic)",
        "floor": "3rd Floor",
        "lat": 28.4728,
        "lng": 77.4897,
        "indoor": "Main gate se enter karein  sidha jake left len fir right len-> Stairs se 3rd floor -> right turn and left turn ->>> AAP KYA DEKHTE HAIN AAP KI MANJIL 😀 .",
        "keywords": ["library", "book", "padhne", "study", "kitab"]
    },
    "canteen": {
        "name": "Campus Canteen & Cafeteria",
        "block": "Near Sports Ground",
        "floor": "2nd Floor",
        "lat": 28.4722,
        "lng": 77.4892,
        "indoor": "Basketball court ke saamne seedha entrance hai.",
        "keywords": ["canteen", "food", "khana", "lunch", "cafeteria", "chai", "coffee"]
    },
    "lab": {
        "name": "Computer Labs (IT & CSE)",
        "block": "Block B",
        "floor": "3rd Floor",
        "lat": 28.4730,
        "lng": 77.4896,
        "indoor": "Block B lift se 3rd floor jayein -> Lab 304 seedhe hallway me hai.",
        "keywords": ["lab", "computer", "coding", "it lab", "cs lab", "practical"]
    },
    "placement": {
        "name": "Training & Placement Cell (T&P)",
        "block": "Admin Block",
        "floor": "1st Floor",
        "lat": 28.4726,
        "lng": 77.4899,
        "indoor": "Admin porch se 1st floor stairwell -> Right hand side room 105.",
        "keywords": ["placement", "job", "interview", "t&p", "internship"]
    },
    "admin": {
        "name": "Admin Office & Registrar (Exam Cell)",
        "block": "Admin Block 1",
        "floor": "Ground Floor",
        "lat": 28.4725,
        "lng": 77.4898,
        "indoor": "Main reception ke bagal me room 004.",
        "keywords": ["admin", "office", "fee", "fees", "admit card", "exam cell", "registrar"]
    }
}

@app.route("/")
def home():
    # Pass locations so map pins load on start
    formatted_locations = {
        k: {"name": v["name"], "lat": v["lat"], "lng": v["lng"], "desc": f"{v['block']} ({v['floor']})"}
        for k, v in CAMPUS_DATA.items()
    }
    return render_template("index.html", locations=formatted_locations)

@app.route("/chat", methods=["POST"])
def chat():
    user_query = request.json.get("message", "").lower().strip()
    
    # Keyword search engine
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
        "reply": "Maaf kijiye, ye location database me nahi mili. Aap Library, Canteen, Computer Lab, Admin Office, ya Placement Cell search kar sakte hain.",
        "lat": None,
        "lng": None
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)