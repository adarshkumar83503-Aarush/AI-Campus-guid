import random
import time
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Yahan apna Gmail aur 16-digit App Password daalein (Bina space ke ya space ke sath chalega)
SENDER_EMAIL = "adarshkumar83503@gmail.com "
SENDER_APP_PASSWORD = "sfrl khsi gaso roni" 

STUDENTS_DB = {
    "25116CN001": {"name": "Adarsh", "email": "adarshkumar83503@gmail.com"},
    "25116CN407": {"name": "AKANSHA", "email": "akanshasingh16806@gmail.com"},
    "25116CN091": {"name": "Aisha", "email": "pandeyaisha829@gmail.com"},
    "25116CN029": {"name": "Aditya", "email": "aditya33322@gmail.com"}
}

OTP_STORE = {}
COMPLAINTS_DB = []

CAMPUS_DATA = {
    # Existing default entries
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
    },
    "placement": {
        "name": "Training & Placement Cell (T&P)",
        "block": "Admin / Main Block",
        "floor": "Ground Floor",
        "lat": 28.4726,
        "lng": 77.4899,
        "indoor": "Admin building reception ke paas T&P block.",
        "keywords": ["placement", "job", "interview", "t&p"]
    },

    
    "gate_1": {
        "name": "Gate Number 1",
        "block": "Main Entrance",
        "floor": "Ground Level",
        "lat": 28.472365,
        "lng": 77.488155,
        "indoor": "Main gate 1 entrance.",
        "keywords": ["gate 1", "gate no 1", "entry 1", "main gate"]
    },
    "gate_2": {
        "name": "Gate Number 2",
        "block": "Side Entrance",
        "floor": "Ground Level",
        "lat": 28.472077,
        "lng": 77.489820,
        "indoor": "Gate 2 entrance.",
        "keywords": ["gate 2", "gate no 2", "entry 2"]
    },
    "gate_3": {
        "name": "Gate Number 3",
        "block": "Back/Side Entrance",
        "floor": "Ground Level",
        "lat": 28.474170,
        "lng": 77.489113,
        "indoor": "Gate 3 entrance.",
        "keywords": ["gate 3", "gate no 3", "entry 3"]
    },
    "ab1_entry_1": {
        "name": "AB1 Building Entry 1",
        "block": "Academic Block 1",
        "floor": "Ground Floor",
        "lat": 28.472107,
        "lng": 77.488729,
        "indoor": "AB1 main front entrance.",
        "keywords": ["ab1 entry 1", "ab1 gate 1", "ab1 main gate"]
    },
    "ab1_entry_2": {
        "name": "AB1 Building Entry 2",
        "block": "Academic Block 1",
        "floor": "Ground Floor",
        "lat": 28.471987,
        "lng": 77.489280,
        "indoor": "AB1 side entrance 2.",
        "keywords": ["ab1 entry 2", "ab1 gate 2"]
    },
    "ab1_entry_3": {
        "name": "AB1 Building Entry 3",
        "block": "Academic Block 1",
        "floor": "Ground Floor",
        "lat": 28.472489,
        "lng": 77.489287,
        "indoor": "AB1 entrance 3.",
        "keywords": ["ab1 entry 3", "ab1 gate 3"]
    },
    "ab1_entry_4": {
        "name": "AB1 Building Entry 4",
        "block": "Academic Block 1",
        "floor": "Ground Floor",
        "lat": 28.472640,
        "lng": 77.488723,
        "indoor": "AB1 entrance 4.",
        "keywords": ["ab1 entry 4", "ab1 gate 4"]
    },
    "ab2_entry_1": {
        "name": "AB2 Building Entry 1",
        "block": "Academic Block 2",
        "floor": "Ground Floor",
        "lat": 28.472710,
        "lng": 77.489538,
        "indoor": "AB2 main entrance.",
        "keywords": ["ab2 entry 1", "ab2 main gate", "ab2"]
    },
    "ab2_entry_2": {
        "name": "AB2 Building Entry 2",
        "block": "Academic Block 2",
        "floor": "Ground Floor",
        "lat": 28.472826,
        "lng": 77.488981,
        "indoor": "AB2 secondary entrance.",
        "keywords": ["ab2 entry 2", "ab2 gate 2"]
    },
    "registrar_office": {
        "name": "Registrar Office",
        "block": "Admin Block",
        "floor": "Ground Floor",
        "lat": 28.472850,
        "lng": 77.488639,
        "indoor": "Admin building central wing -> Registrar Office.",
        "keywords": ["registrar", "registrar office", "registration", "admin office"]
    },
    "bca_building": {
        "name": "BCA Building",
        "block": "BCA Academic Block",
        "floor": "Ground Floor",
        "lat": 28.473911,
        "lng": 77.489368,
        "indoor": "BCA department main block entrance.",
        "keywords": ["bca", "bca building", "bca block"]
    },
    "pgdm_block": {
        "name": "PGDM Block",
        "block": "PGDM Management Block",
        "floor": "Ground Floor",
        "lat": 28.473085,
        "lng": 77.488308,
        "indoor": "PGDM management building entrance.",
        "keywords": ["pgdm", "pgdm block", "pgdm building", "mba block"]
    },
    "shd_auditorium": {
        "name": "SHD Auditorium",
        "block": "Auditorium Block",
        "floor": "Ground / Lower Ground",
        "lat": 28.472369,
        "lng": 77.489740,
        "indoor": "Main SHD Auditorium entry.",
        "keywords": ["auditorium", "shd", "audi", "shd auditorium", "hall"]
    },
    "sports_ground": {
        "name": "Sports Ground",
        "block": "Outdoor Sports Complex",
        "floor": "Ground Level",
        "lat": 28.472979,
        "lng": 77.488991,
        "indoor": "Main sports ground area.",
        "keywords": ["sports ground", "ground", "play ground", "cricket ground"]
    },
    "futshell_area": {
        "name": "Futshell Area",
        "block": "Sports Complex",
        "floor": "Ground Level",
        "lat": 28.473088,
        "lng": 77.489353,
        "indoor": "Futshell turf area near sports ground.",
        "keywords": ["futshell", "football", "turf", "futsal"]
    },
    "boys_hostel_2_ground": {
        "name": "Boys Hostel 2 Ground",
        "block": "Hostel Zone",
        "floor": "Ground Level",
        "lat": 28.473011,
        "lng": 77.489544,
        "indoor": "Play area in front of BH-2.",
        "keywords": ["bh2 ground", "boys hostel 2 ground", "hostel ground"]
    },
    "basketball_court": {
        "name": "Basketball Court",
        "block": "Sports Area",
        "floor": "Ground Level",
        "lat": 28.472871,
        "lng": 77.489839,
        "indoor": "Outdoor Basketball Court.",
        "keywords": ["basketball", "basketball court", "bb court"]
    },
    "badminton_court": {
        "name": "Badminton Court",
        "block": "Sports Area",
        "floor": "Ground Level",
        "lat": 28.472683,
        "lng": 77.490026,
        "indoor": "Outdoor Badminton Court.",
        "keywords": ["badminton", "badminton court"]
    },
    "volleyball_court": {
        "name": "Volleyball Court",
        "block": "Sports Area",
        "floor": "Ground Level",
        "lat": 28.472498,
        "lng": 77.490222,
        "indoor": "Outdoor Volleyball Court.",
        "keywords": ["volleyball", "volleyball court"]
    },
    "mba_canteen": {
        "name": "MBA Canteen",
        "block": "Near PGDM / MBA Block",
        "floor": "Ground Floor",
        "lat": 28.473173,
        "lng": 77.488335,
        "indoor": "MBA block adjacent canteen entrance.",
        "keywords": ["mba canteen", "management canteen", "pgdm canteen"]
    },
    "girls_hostel_block_c": {
        "name": "Girls Hostel Block C",
        "block": "Hostel Zone",
        "floor": "Ground Floor Entrance",
        "lat": 28.473374,
        "lng": 77.489921,
        "indoor": "Girls Hostel Block C reception/gate.",
        "keywords": ["girls hostel c", "girls hostel block c", "gh block c"]
    },
    "girls_hostel": {
        "name": "Girls Hostel Main",
        "block": "Hostel Zone",
        "floor": "Ground Floor Entrance",
        "lat": 28.473453,
        "lng": 77.489782,
        "indoor": "Girls Hostel main gate.",
        "keywords": ["girls hostel", "gh", "girls hostel main"]
    },
    "boys_hostel_1": {
        "name": "Boys Hostel 1 (BH1)",
        "block": "Hostel Zone",
        "floor": "Ground Floor Entrance",
        "lat": 28.473438,
        "lng": 77.488423,
        "indoor": "BH1 main entrance gate.",
        "keywords": ["boys hostel 1", "bh1", "boys hostel block 1"]
    },
    "boys_hostel_2": {
        "name": "Boys Hostel 2 (BH2)",
        "block": "Hostel Zone",
        "floor": "Ground Floor Entrance",
        "lat": 28.472612,
        "lng": 77.489399,
        "indoor": "BH2 main entrance gate.",
        "keywords": ["boys hostel 2", "bh2", "boys hostel block 2"]
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

    if admission_no not in STUDENTS_DB:
        return jsonify({"success": False, "message": "Admission Number record me nahi mila! (Use: GLB2023001)"})

    student = STUDENTS_DB[admission_no]
    recipient_email = student["email"]

    otp = str(random.randint(100000, 999999))
    OTP_STORE[admission_no] = {
        "otp": otp,
        "expires": time.time() + 300
    }

    # Backup print: taaki terminal/render logs me hamesha OTP dikhe
    print(f"\n>>> [OTP GENERATED] Admission: {admission_no} | OTP: {otp} <<<\n", flush=True)

    # Email bhejne ki koshish (Fail-safe wrapper)
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Campus Navigator <{SENDER_EMAIL}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"Your Campus Guide OTP: {otp}"
        body = f"Hello {student['name']},\n\nYour OTP for Campus Guide login is: {otp}\nValid for 5 minutes."
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=5)
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()
        email_sent = True
    except Exception as e:
        print(f"[Email Warning] Mail send nahi hui: {e}", flush=True)
        email_sent = False

    user_part, domain = recipient_email.split('@')
    masked_email = user_part[:2] + "***@" + domain

    if email_sent:
        return jsonify({"success": True, "message": f"OTP aapke email ({masked_email}) par bhej diya gaya hai!"})
    else:
        # Email fail hone par bhi viva/test ke liye popup me hint de dega taaki project ruke na
        return jsonify({
            "success": True, 
            "message": f"Email connect nahi hua, par Testing OTP Console me aa gaya: {otp}"
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
        return jsonify({"success": False, "message": "OTP expire ho gaya."})

    if user_otp == record["otp"]:
        del OTP_STORE[admission_no]
        student_name = STUDENTS_DB[admission_no]["name"]
        return jsonify({"success": True, "message": f"Welcome {student_name}!", "student_name": student_name})

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
# -----------------------------------------------------------
# ⚠️ COMPLAINT & ADMIN ROUTES
# -----------------------------------------------------------

@app.route("/submit-complaint", methods=["POST"])
def submit_complaint():
    data = request.json or {}
    admission_no = data.get("admission_no", "Guest Student")
    category = data.get("category", "General")
    location = data.get("location", "Not Specified")
    description = data.get("description", "").strip()

    if not description:
        return jsonify({"success": False, "message": "Kripya samasya ka vivaran likhein."})

    ticket_id = f"GLB-CMP-{random.randint(1000, 9999)}"
    timestamp = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

    new_record = {
        "ticket_id": ticket_id,
        "admission_no": admission_no,
        "category": category,
        "location": location,
        "description": description,
        "status": "Pending Review",
        "created_at": timestamp
    }
    COMPLAINTS_DB.append(new_record)

    print(f"\n🚨 [COMPLAINT LOGGED] {ticket_id} by {admission_no}: {description}\n", flush=True)

    return jsonify({
        "success": True,
        "message": "Aapki complaint safaltapoorvak darj kar li gayi hai!",
        "ticket_id": ticket_id
    })

@app.route("/admin")
def admin_dashboard():
    return render_template("admin.html", complaints=reversed(COMPLAINTS_DB))

@app.route("/api/complaints/update-status", methods=["POST"])
def update_complaint_status():
    data = request.json or {}
    ticket_id = data.get("ticket_id")
    new_status = data.get("status")

    for cmp in COMPLAINTS_DB:
        if cmp["ticket_id"] == ticket_id:
            cmp["status"] = new_status
            return jsonify({"success": True})

    return jsonify({"success": False, "message": "Ticket nahi mila"}), 404
if __name__ == "__main__":
    app.run(debug=True, port=5000)
