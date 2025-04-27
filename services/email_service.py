import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Any
import logging
from config import get_settings
import uuid

logger = logging.getLogger(__name__)
settings = get_settings()

async def send_followup_email_job(user_email: str, subject: str, body: str):
    """Standalone function for sending follow-up emails that can be serialized by APScheduler"""
    service = EmailService()  # Create a new instance for the job
    await service.send_email(user_email, subject, body)

class EmailService:
    def __init__(self, scheduler=None):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME.strip()
        self.smtp_password = settings.SMTP_PASSWORD.strip()
        self.from_email = settings.EMAIL_FROM.strip()
        self.scheduler = scheduler
        logger.info(f"EmailService initialized with SMTP server: {self.smtp_server}:{self.smtp_port}")

    async def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send an email"""
        try:
            logger.info(f"Attempting to send email to {to_email} with subject: {subject}")
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))
            logger.debug("Email message created successfully")

            logger.info("Establishing SMTP connection...")
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
            try:
                logger.debug("SMTP connection established")
                logger.debug("Starting TLS...")
                server.starttls()
                logger.debug("TLS started successfully")
                
                logger.debug(f"Attempting login with username: {self.smtp_username}")
                server.login(self.smtp_username, self.smtp_password)
                logger.debug("SMTP login successful")
                
                logger.info("Sending email message...")
                server.send_message(msg)
                logger.info(f"Email sent successfully to {to_email}")
                return True
            finally:
                server.quit()  # Ensure connection is closed even if an error occurs
            
        except smtplib.SMTPAuthenticationError as auth_error:
            logger.error(f"SMTP Authentication failed: {str(auth_error)}")
            logger.error(f"SMTP Configuration: server={self.smtp_server}, port={self.smtp_port}, username={self.smtp_username}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}")
            logger.error(f"Error details: {str(e)}")
            logger.error(f"SMTP Configuration: server={self.smtp_server}, port={self.smtp_port}, username={self.smtp_username}")
            return False

    def get_welcome_email_content(self, user_data: Dict[str, Any]) -> tuple:
        """Generate welcome email content"""
        subject = "Welcome to Kratom AI - Your Personalized Recommendation"
        body = f"""
Hello!

Thank you for using Kratom AI to get your personalized recommendation. We're excited to help you on your wellness journey.

Important Reminders:
- Start with a lower dose than recommended if you're new to Kratom
- Stay hydrated throughout the day
- Take on an empty stomach for best results
- Store your Kratom in a cool, dry place

Best regards,
The Kratom AI Team
"""
        return subject, body

    def get_followup_email_content(self, user_data: Dict[str, Any]) -> tuple:
        """Generate follow-up email content"""
        subject = "How's Your Kratom Experience Going?"
        body = f"""
Hello again!

It's been a week since you received your personalized Kratom recommendation from us. We'd love to hear about your experience.

Please take a moment to:
1. Rate your experience (1-5 stars)
2. Share any feedback or concerns
3. Let us know if you'd like to adjust your recommendation

Simply reply to this email with your feedback.

Your input helps us improve our recommendations for everyone.

Best regards,
The Kratom AI Team
"""
        return subject, body

    async def send_welcome_email(self, user_data: Dict[str, Any]) -> bool:
        """Send welcome email to new user"""
        logger.info(f"Preparing welcome email for user: {user_data.get('email', 'email not found')}")
        subject, body = self.get_welcome_email_content(user_data)
        success = await self.send_email(user_data['email'], subject, body)
        if success:
            logger.info("Welcome email sent successfully")
        else:
            logger.error("Failed to send welcome email")
        return success

    async def schedule_followup_email(self, user_data: Dict[str, Any]) -> None:
        """Schedule follow-up email for 7 days later"""
        if not self.scheduler:
            logger.error("Scheduler not initialized. Cannot schedule follow-up email.")
            return

        try:
            # Create a unique job ID using the user's email
            job_id = f"followup_email_{user_data['email']}_{uuid.uuid4().hex[:8]}"
            
            # Prepare email content
            subject, body = self.get_followup_email_content(user_data)
            
            # Schedule the follow-up email using the static method
            send_time = datetime.utcnow() + timedelta(days=7)
            success = await self.scheduler.schedule_email(
                job_id=job_id,
                func='services.email_service:send_followup_email_job',  # Updated function reference
                args=[user_data['email'], subject, body],
                run_date=send_time
            )
            
            if success:
                logger.info(f"Follow-up email scheduled for {user_data['email']} at {send_time}")
            else:
                logger.error(f"Failed to schedule follow-up email for {user_data['email']}")
                
        except Exception as e:
            logger.error(f"Error scheduling follow-up email: {str(e)}")