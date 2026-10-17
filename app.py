import os
import random
import time
import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ==========================================
# 📍 CAMPUS LOCATIONS
# ==========================================
CAMPUS_DATA = {
    "ab1": {
        "name": "Academic Block 1 (AB-1)",
        "category": "academic",
        "lat": 28.4725,
        "lng": 77.4891,
        "desc": "First Year Classes, Dean Office & Lecture Halls"
    },
    "ab2": {
        "name": "Academic Block 2 (AB-2)",
        "category": "academic",
        "lat": 28.4728,
        "lng": 77.4896,
        "desc": "CSE, IT, AI & Data Science Departments & High-Tech Labs"
    },
    "library": {
        "name": "Central Knowledge Park Library",
        "category": "facilities",
        "lat": 28.4730,
        "lng": 77.4894,
        "desc": "Over 70,000+ Books, Digital Research Wing & Reading Halls"
    },
    "audi": {
        "name": "Mahatma Gandhi Central Auditorium",
        "category": "facilities",
        "lat": 28.4735,
        "lng": 77.4889,
        "desc": "Air-conditioned 1000+ Capacity Hall for Convocations & Fests"
    },
    "cafeteria": {
        "name": "Student Cafeteria & Food Court",
        "category": "facilities",
        "lat": 28.4721,
        "lng": 77.4890,
        "desc": "Cafeteria, Nescafe Corner & Open Green Dining Courtyard"
    },
    "sports": {
        "name": "Sports Complex & Main Playground",
        "category": "sports",
        "lat": 28.4732,
        "lng": 77.4884,
        "desc": "Cricket Pitch, Basketball Court, Badminton & Volleyball"
    }
}

# ==========================================
# 👥 AUTH & MEMORY DATABASES
# ==========================================
STUDENTS_DB = {
    "25116CN001": {"name": "Adarsh", "email": "adarshkumar83503@gmail.com"},
    "25116CN407": {"name": "Akansha", "email": "akanshasingh16806@gmail.com"},
    "25116CN091": {"name": "Aisha", "email": "pandeyaisha829@gmail.com"},
    "25116CN029": {"name": "Aditya", "email": "aditya33322@gmail.com"}
}

OTP_STORE = {}

COMPLAINTS_DB = [
    {
        "ticket_id": "GLB-1024",
        "admission_no": "25116CN001",
        "category": "Lab / Hardware",
        "location": "AB-2, IoT Lab 4",
        "description": "Ethernet switch not functioning at bench 3.",
        "status": "In Progress",
        "created_at": "17 Oct 2026, 11:20 AM"
    }
]

LOST_FOUND_DB = [
    {
        "id": 1,
        "type": "Lost",
        "title": "Titan Black Chrono Watch",
        "location": "AB-1 Cafeteria",
        "contact": "adarshkumar83503@gmail.com",
        "date": "17 Oct 2026",
        "status": "Active"
    },
    {
        "id": 2,
        "type": "Found",
        "title": "College ID Card (CSE 2nd Year)",
        "location": "Central Library Desk",
        "contact": "Library Helpdesk Counter 2",
        "date": "16 Oct 2026",
        "status": "Handed to Security"
    }
]

CLUBS_EVENTS_DB = [
    {
        "name": "Google Developer Student Clubs (GDSC)",
        "tag": "Tech Club",
        "desc": "Web, Android, Cloud, AI/ML Workshops and Hackathons.",
        "badge": "Active",
        "color": "blue"
    },
    {
        "name": "Rotaract Club of GL Bajaj",
        "tag": "Social & Cultural",
        "desc": "Community drives, youth leadership, blood donations and annual fests.",
        "badge": "Community",
        "color": "amber"
    },
    {
        "name": "Zenith - Annual Cultural Fest",
        "tag": "Flagship Fest",
        "desc": "3 days of celebrity pro-nights, dance battles, dramatics, and rock shows.",
        "badge": "Upcoming",
        "color": "emerald"
    },
    {
        "name": "E-Cell (Entrepreneurship Cell)",
        "tag": "Innovation & Startups",
        "desc": "Incubation funding, Shark Tank campus pitches, and mentor connects.",
        "badge": "Incubation",
        "color": "purple"
    }
]

# ==========================================
# 🌐 MAIN & API ROUTES
# ==========================================
@app.route("/")
def index():
    return render_template("index.html", 
                           locations=CAMPUS_DATA, 
                           lost_items=reversed(LOST_FOUND_DB), 
                           clubs=CLUBS_EVENTS_DB)

# 1. OTP Routes
@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json or {}
    adm = data.get("admission_no", "").strip().upper()
    if adm not in STUDENTS_DB:
        return jsonify({"success": False, "message": "Admission ID nahi mili! (Try: 25116CN001)"}), 404
    
    otp = str(random.randint(100000, 999999))
    OTP_STORE[adm] = {"otp": otp, "expires": time.time() + 300}
    return jsonify({"success": True, "message": f"Verification OTP: {otp}", "otp": otp})

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json or {}
    adm = data.get("admission_no", "").strip().upper()
    otp = data.get("otp", "").strip()
    if adm in OTP_STORE and OTP_STORE[adm]["otp"] == otp:
        del OTP_STORE[adm]
        return jsonify({"success": True, "message": "Login successful!", "user": STUDENTS_DB[adm]})
    return jsonify({"success": False, "message": "Galat ya Expired OTP!"}), 400

# 2. Admission & Cutoff Predictor API
@app.route("/api/predict-admission", methods=["POST"])
def predict_admission():
    data = request.json or {}
    try:
        rank = int(data.get("rank", 0))
    except ValueError:
        return jsonify({"success": False, "message": "Valid rank daalein."})
    
    category = data.get("category", "General")
    quota = data.get("quota", "UP-State")

    # GL Bajaj Cutoff benchmarks (Simulated JEE Main / UPTAC Ranks)
    branches = []
    if rank <= 85000:
        branches.append({"branch": "Computer Science & Engineering (Core)", "chance": "Very High", "color": "emerald"})
    if rank <= 125000:
        branches.append({"branch": "CSE (Artificial Intelligence & ML)", "chance": "High", "color": "emerald"})
    if rank <= 165000:
        branches.append({"branch": "CSE (Data Science)", "chance": "Good", "color": "blue"})
    if rank <= 210000:
        branches.append({"branch": "Information Technology (IT)", "chance": "Moderate", "color": "sky"})
    if rank <= 350000:
        branches.append({"branch": "Electronics & Communication (ECE)", "chance": "Safe", "color": "amber"})
    
    if not branches:
        branches.append({"branch": "Management / Institutional Round Quota", "chance": "Contact Admission Cell", "color": "purple"})

    return jsonify({
        "success": True,
        "eligible_branches": branches,
        "summary": f"Rank {rank} ({category} / {quota}) ke aadhar par eligible branches:"
    })

# 3. Complaint Submission
@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():
    data = request.json or {}
    desc = data.get("description", "").strip()
    if not desc:
        return jsonify({"success": False, "message": "Vivaran likhna anivarya hai."}), 400
    
    tid = f"GLB-{random.randint(1000, 9999)}"
    record = {
        "ticket_id": tid,
        "admission_no": data.get("admission_no", "Guest Student"),
        "category": data.get("category", "General"),
        "location": data.get("location", "Campus"),
        "description": desc,
        "status": "Pending",
        "created_at": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    }
    COMPLAINTS_DB.append(record)
    return jsonify({"success": True, "message": "Complaint safaltapoorvak darj hui!", "ticket_id": tid})

# 4. Lost & Found Post
@app.route("/api/lost-found/add", methods=["POST"])
def add_lost_found():
    data = request.json or {}
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"success": False, "message": "Item name daalein."})
    
    new_item = {
        "id": len(LOST_FOUND_DB) + 1,
        "type": data.get("type", "Lost"),
        "title": title,
        "location": data.get("location", "Campus"),
        "contact": data.get("contact", "Helpdesk"),
        "date": datetime.datetime.now().strftime("%d %b %Y"),
        "status": "Active"
    }
    LOST_FOUND_DB.append(new_item)
    return jsonify({"success": True, "message": "Item safaltapoorvak add ho gaya!"})

@app.route("/admin")
def admin_page():
    return render_template("admin.html", complaints=list(reversed(COMPLAINTS_DB)))

@app.route("/api/complaints/update-status", methods=["POST"])
def update_complaint_status():
    data = request.json or {}
    tid = data.get("ticket_id")
    st = data.get("status")
    for c in COMPLAINTS_DB:
        if c["ticket_id"] == tid:
            c["status"] = st
            return jsonify({"success": True})
    return jsonify({"success": False, "message": "Ticket nahi mila"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
    
