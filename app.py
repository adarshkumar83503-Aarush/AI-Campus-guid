import os
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ==========================================================
# 📧 GMAIL CONFIGURATION (Yahan apna email & app password daalein)
# ==========================================================
SENDER_EMAIL = sfrl khsi gaso roni
SENDER_APP_PASSWORD = sfrl khsi gaso roni

# Registered Students Database (Test karne ke liye apna email yahan dalein)
STUDENTS_DB = {
"25116CN001": {"name": "Adarsh", "email": "adarshkumar83503@gmail.com"},
    "25116CN407": {"name": "AKANSHA", "email": "akanshasingh16806@gmail.com"},
    "25116CN091": {"name": "Aisha", "email": "pandeyaisha829@gmail.com"}    
}

OTP_STORE = {}

# GL Bajaj Campus Locations
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

def send_real_email_otp(recipient_email, student_name, otp):
    """Port 587 (TLS) use karke Gmail se live OTP bhejna"""
    subject = f"Campus Navigator OTP: {otp}"
    body = f"""Namaste {student_name},

GL Bajaj Campus Guide & Navigator me login karne ke liye aapka OTP hai:

👉  {otp}  👈

Yeh OTP agle 5 minute tak valid hai. Kisi ke sath share na karein.

- AI Campus Guide Team
"""
    msg = MIMEMultipart()
    msg['From'] = f"GL Bajaj Navigator <{SENDER_EMAIL}>"
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Clean password from spaces
    clean_password = SENDER_APP_PASSWORD.replace(" ", "")

    server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
    server.starttls()
    server.login(SENDER_EMAIL, clean_password)
    server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
    server.quit()

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
        return jsonify({"success": False, "message": "Admission No. record me nahi mila! (Try: GLB2023001)"})

    student = STUDENTS_DB[admission_no]
    recipient_email = student["email"]

    # 6-Digit Secure OTP
    otp = str(random.randint(100000, 999999))
    OTP_STORE[admission_no] = {
        "otp": otp,
        "expires": time.time() + 300
    }

    # Backup Log: Terminal aur Render logs me hamesha dikhega
    print(f"\n==========================================", flush=True)
    print(f"🔐 [OTP GENERATED] Admission: {admission_no} | OTP: {otp}", flush=True)
    print(f"==========================================\n", flush=True)

    user_part, domain = recipient_email.split('@')
    masked_email = user_part[:2] + "***@" + domain

    try:
        send_real_email_otp(recipient_email, student["name"], otp)
        return jsonify({
            "success": True,
            "message": f"OTP aapke registered email ({masked_email}) par bhej diya gaya hai!"
        })
    except Exception as e:
        print(f"[SMTP Error]: {e}", flush=True)
        # Fail-safe message: Agar SMTP block hua toh testing rukegi nahi
        return jsonify({
            "success": True,
            "message": f"Email bhejne me issue aaya. Terminal/Render logs me OTP aa gaya hai: {otp}"
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
        return jsonify({"success": False, "message": "OTP expire ho gaya. Kripya naya OTP generate karein."})

    if user_otp == record["otp"]:
        del OTP_STORE[admission_no]
        student_name = STUDENTS_DB[admission_no]["name"]
        return jsonify({
            "success": True,
            "message": f"Welcome, {student_name}!",
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

    return jsonify({"reply": "Location nahi mili. Library, Canteen ya CS Lab try karein.", "lat": None, "lng": None})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
