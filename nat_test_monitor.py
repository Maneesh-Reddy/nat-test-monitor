import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ============================================================
#  CONFIGURATION — loaded from GitHub Secrets
# ============================================================

SENDER_EMAIL     = os.environ["SENDER_EMAIL"]       # Gmail used to SEND the alert
SENDER_PASSWORD  = os.environ["SENDER_PASSWORD"]    # Gmail App Password
RECIPIENT_EMAIL  = os.environ["RECIPIENT_EMAIL"]    # Email where you RECEIVE the alert

ROLL_NUMBERS = [
    "26030048240111",
    "26030048240161",
    "26030048240113",
    "26030048240167",
    "26030048240090",
    "26030048240068",
]

URL = "http://www.nat-test.com/contents/result/result-id26-03-4Q-gs.html"

# ============================================================
#  EMAIL FUNCTION
# ============================================================

def send_email(found_numbers):
    subject = "🎉 NAT-TEST Results Alert — Your Roll Number is Listed!"

    body = f"""
Congratulations! The following roll number(s) have appeared on the NAT-TEST March 2026 results page:

{chr(10).join(f"  ✅  {n}" for n in found_numbers)}

Check your results here:
{URL}

Alert sent at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC

頑張ってください！
"""

    msg = MIMEMultipart()
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = RECIPIENT_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

    print(f"✅ Alert email sent to {RECIPIENT_EMAIL} for: {found_numbers}")

# ============================================================
#  MAIN — runs once per GitHub Actions trigger
# ============================================================

print(f"[{datetime.now()}] 🔍 Checking NAT-TEST results page...")

try:
    response = requests.get(URL, timeout=30)
    response.raise_for_status()
    page_text = response.text
except Exception as e:
    print(f"❌ Failed to fetch page: {e}")
    exit(1)

found = [num for num in ROLL_NUMBERS if num in page_text]

if found:
    print(f"🎉 Found roll numbers: {found}")
    send_email(found)
else:
    print(f"⏳ None of the roll numbers found yet. Will check again in 10 minutes.")
