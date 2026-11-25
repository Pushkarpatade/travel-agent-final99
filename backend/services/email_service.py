import os
import smtplib
import json
import urllib.request
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from backend.config import settings

logger = logging.getLogger("travelpilot.email")

def send_real_otp_email(to_email: str, otp: str) -> dict:
    """
    Sends a real 6-digit OTP code to the recipient email.
    Supports:
    1. Resend API (free tier: 3,000 emails/month) via RESEND_API_KEY
    2. Gmail SMTP / Custom SMTP via SMTP_USER and SMTP_PASSWORD
    3. Fallback: logs OTP to server console
    """
    resend_key = (settings.RESEND_API_KEY or os.getenv("RESEND_API_KEY", "")).strip()
    smtp_user = os.getenv("SMTP_USER", "").strip()
    smtp_pass = os.getenv("SMTP_PASSWORD", "").strip()
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    subject = f"Your TravelPilot Verification Code: {otp}"
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 16px; background-color: #ffffff;">
      <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #0891b2; margin: 0; font-size: 24px;">TravelPilot AI</h2>
        <p style="color: #64748b; font-size: 13px; margin-top: 4px;">Autonomous Travel Planning & Security</p>
      </div>
      <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; text-align: center;">
        <p style="color: #334155; font-size: 14px; margin-bottom: 8px;">Your 2-Step Verification One-Time Password (OTP) is:</p>
        <div style="font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #0891b2; padding: 12px; background: #ecfeff; border-radius: 8px; display: inline-block;">
          {otp}
        </div>
        <p style="color: #94a3b8; font-size: 12px; margin-top: 12px;">This code is valid for 10 minutes. Never share this code with anyone.</p>
      </div>
    </div>
    """

    # 1. Try Resend if configured
    if resend_key:
        try:
            req_data = json.dumps({
                "from": "TravelPilot AI <onboarding@resend.dev>",
                "to": [to_email],
                "subject": subject,
                "html": html_content
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.resend.com/emails",
                data=req_data,
                headers={
                    "Authorization": f"Bearer {resend_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "TravelPilot/1.0"
                },
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                logger.info(f"Resend email dispatched to {to_email}: status {resp.status}")
                return {"success": True, "provider": "resend", "status": resp.status}
        except Exception as e:
            logger.error(f"Resend dispatch error: {e}")

    # 2. Try SMTP (e.g. Gmail) if configured
    if smtp_user and smtp_pass:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = smtp_user
            msg["To"] = to_email
            msg.attach(MIMEText(f"Your TravelPilot OTP is: {otp}. Valid for 10 minutes.", "plain"))
            msg.attach(MIMEText(html_content, "html"))

            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [to_email], msg.as_string())
            server.quit()
            logger.info(f"SMTP email dispatched to {to_email} via {smtp_host}")
            return {"success": True, "provider": "smtp"}
        except Exception as e:
            logger.error(f"SMTP dispatch error: {e}")

    # 3. Fallback: Log to console
    logger.info(f"[DEV OTP] 2-Step OTP for {to_email} is: {otp}")
    return {"success": True, "provider": "local_dev", "logged_otp": otp}
