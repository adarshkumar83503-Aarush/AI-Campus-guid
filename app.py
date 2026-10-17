import os
import random
import time
import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Campus Data
CAMPUS_DATA = {
    "library": {
        "name": "Central Library (GL Bajaj)",
        "block": "Main Academic Block",
        "floor": "Ground / 1st Floor",
        "lat": 28.4728,
        "lng": 77.4897,
        "desc": "Main Academic Block (Ground / 1st Floor)"
    },
    "canteen": {
        "name": "Campus Cafeteria & Food Court",
        "block": "Near PGDM / Hostel Area",
        "floor": "Ground Floor",
        "lat": 28.4722,
        "lng": 77.4892,
        "desc": "Near PGDM / Hostel Area (Ground Floor)"
    },
    "audi": {
        "name": "Main Auditorium",
        "block": "Block A",
        "floor": "Ground Floor",
        "lat": 28.4735,
        "lng": 77.4889,
        "desc": "Block A (Ground Floor)"
    },
    "admin": {
        "name": "Registrar & Accounts Office",
        "block": "Administrative Block",
        "floor": "Ground Floor",
        "lat": 28.4730,
        "lng": 77.4895,
        "desc": "Administrative Block (Ground Floor)"
    }
}

STUDENTS_DB = {
    "25116CN001": {"name": "Adarsh", "email": "adarshkumar83503@gmail.com"},
    "25116CN407": {"name": "AKANSHA", "email": "akanshasingh16806@gmail.com"},
    "25116CN091": {"name": "Aisha", "email": "pandeyaisha829@gmail.com"},
    "25116CN029": {"name": "Aditya", "email": "aditya33322@gmail.com"}
}

OTP_STORE = {}
COMPLAINTS_DB = []

@app.route("/")
def home():
    return render_template("index.html", locations=CAMPUS_DATA)

@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json or {}
    adm = data.get("admission_no", "").strip().upper()
    if adm not in STUDENTS_DB:
        return jsonify({"success": False, "message": "Admission ID nahi mili!"}), 404
    
    otp = str(random.randint(100000, 999999))
    OTP_STORE[adm] = {"otp": otp, "expires": time.time() + 300}
    print(f"\n[OTP GENERATED] {adm} -> {otp}\n", flush=True)
    return jsonify({"success": True, "message": f"Verification OTP: {otp}", "fallback_otp": otp})

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json or {}
    adm = data.get("admission_no", "").strip().upper()
    otp = data.get("otp", "").strip()
    if adm in OTP_STORE and OTP_STORE[adm]["otp"] == otp:
        del OTP_STORE[adm]
        return jsonify({"success": True, "user": STUDENTS_DB[adm]})
    return jsonify({"success": False, "message": "Galat OTP!"}), 400

@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():
    data = request.json or {}
    desc = data.get("description", "").strip()
    if not desc:
        return jsonify({"success": False, "message": "Vivaran likhein."})
    tid = f"GLB-{random.randint(1000, 9999)}"
    COMPLAINTS_DB.append({
        "ticket_id": tid,
        "admission_no": data.get("admission_no", "Guest"),
        "category": data.get("category", "General"),
        "location": data.get("location", "-"),
        "description": desc,
        "status": "Pending",
        "created_at": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    })
    return jsonify({"success": True, "message": "Grievance Darj!", "ticket_id": tid})

@app.route("/admin")
def admin():
    return render_template("admin.html", complaints=list(reversed(COMPLAINTS_DB)))

@app.route("/api/complaints/update-status", methods=["POST"])
def update_status():
    data = request.json or {}
    for c in COMPLAINTS_DB:
        if c["ticket_id"] == data.get("ticket_id"):
            c["status"] = data.get("status")
            return jsonify({"success": True})
    return jsonify({"success": False}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
    
