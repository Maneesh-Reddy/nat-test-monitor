import requests
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ============================================================
#  CONFIGURATION — Fill in your details here
# ============================================================

# Your Gmail address and App Password
# (See setup instructions below for how to get App Password)
SENDER_EMAIL    = "your_gmail@gmail.com"
SENDER_PASSWORD = "xxxx xxxx xxxx xxxx"   # Gmail App Password (16 chars)

# Email(s) to receive alerts — add more if needed
RECIPIENT_EMAILS = [
    "your_gmail@gmail.com",
]

# Roll numbers to watch for
ROLL_NUMBERS = [
    "26030048240111",
    "26030048240161",
    "26030048240113",
    "26030048240167",
    "26030048240090",
    "26030048240068",
]

# URL to monitor
URL = "http://www.nat-test.com/contents/result/result-id26-03-4Q-gs.html"

# Check every N seconds (600 = 10 minutes)
CHECK_INTERVAL = 600

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

This alert was sent at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Good luck! 頑張ってください！
"""

    msg = MIMEMultipart()
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = ", ".join(RECIPIENT_EMAILS)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAILS, msg.as_string())
        print(f"[{datetime.now()}] ✅ Alert email sent for: {found_numbers}")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Failed to send email: {e}")


# ============================================================
#  MONITOR FUNCTION
# ============================================================

def check_results():
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        page_text = response.text

        found = [num for num in ROLL_NUMBERS if num in page_text]
        return found

    except Exception as e:
        print(f"[{datetime.now()}] ⚠️  Error fetching page: {e}")
        return []


# ============================================================
#  MAIN LOOP
# ============================================================

alerted_numbers = set()  # Track already-alerted numbers to avoid duplicate emails

print(f"[{datetime.now()}] 🚀 NAT-TEST Monitor started.")
print(f"Watching for {len(ROLL_NUMBERS)} roll numbers on:")
print(f"  {URL}")
print(f"Checking every {CHECK_INTERVAL // 60} minutes.\n")

while True:
    print(f"[{datetime.now()}] 🔍 Checking page...")
    found = check_results()

    # Filter out numbers we've already alerted about
    new_found = [n for n in found if n not in alerted_numbers]

    if new_found:
        print(f"[{datetime.now()}] 🎉 Found new roll numbers: {new_found}")
        send_email(new_found)
        alerted_numbers.update(new_found)

        # If all numbers found, stop monitoring
        if alerted_numbers >= set(ROLL_NUMBERS):
            print(f"[{datetime.now()}] ✅ All roll numbers found. Stopping monitor.")
            break
    else:
        print(f"[{datetime.now()}] ⏳ Not found yet. Next check in {CHECK_INTERVAL // 60} minutes.")

    time.sleep(CHECK_INTERVAL)
