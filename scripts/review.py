import subprocess
import os
import smtplib
from email.message import EmailMessage
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


# 🔍 Get latest git diff
def get_diff():
    try:
        diff = subprocess.check_output(
            ["git", "diff", "HEAD~1"], text=True
        )
        return diff if diff.strip() else "No changes found."
    except Exception as e:
        return f"Error getting diff: {e}"


# 🤖 Initialize Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# 📧 Send email using Brevo SMTP
def send_email(html_content):
    sender = os.getenv("BREVO_EMAIL")
    smtp_key = os.getenv("EMAIL_SERVICE")

    msg = EmailMessage()
    msg["Subject"] = "🚀 Code Review Feedback"
    msg["From"] = sender
    msg["To"] = sender  # send to yourself (change if needed)

    msg.set_content("Your email client does not support HTML.")
    msg.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP("smtp-relay.brevo.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender, smtp_key)
            smtp.send_message(msg)
        print("✅ Email sent via Brevo!")
    except Exception as e:
        print("❌ Email failed:", e)


# 🧠 Generate AI review
def generate_review(diff):
    prompt = f"""
You are a senior code reviewer.

Review the following git diff and provide feedback.

Mandatory:
- Output must be clean HTML
- Use headings, bullet points, and code blocks
- Highlight issues, improvements, and suggestions

DIFF:
{diff}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        return response.text if response and response.text else "<p>No review generated.</p>"
    except Exception as e:
        return f"<p>Error generating review: {e}</p>"


# 🚀 Main flow
def main():
    print("🔍 Getting git diff...")
    diff = get_diff()

    print("🤖 Generating review...")
    html = generate_review(diff)

    print("📧 Sending email...")
    send_email(html)


if __name__ == "__main__":
    main()