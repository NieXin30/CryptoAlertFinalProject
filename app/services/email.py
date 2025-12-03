"""Email service for sending notifications."""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    """Service for sending email notifications via 163 Mail SMTP."""
    
    SMTP_SERVER = "smtp.163.com"
    SMTP_PORT = 465  # SSL port
    
    def __init__(self):
        self.username = os.getenv('MAIL_USERNAME')
        self.password = os.getenv('MAIL_PASSWORD')
        self.admin_email = os.getenv('ADMIN_EMAIL')
    
    def _create_connection(self):
        """Create SMTP connection."""
        server = smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT)
        server.login(self.username, self.password)
        return server
    
    def send_alert_email(self, to_email: str, currency: str, condition: str, 
                         threshold: float, current_price: float) -> bool:
        """Send price alert notification email.
        
        Args:
            to_email: Recipient email address.
            currency: Currency symbol (e.g., 'BTC').
            condition: Alert condition ('>' or '<').
            threshold: Price threshold that was set.
            current_price: Current price that triggered the alert.
            
        Returns:
            True if email was sent successfully.
        """
        try:
            condition_text = "above" if condition == '>' else "below"
            
            subject = f"[CryptoAlert] {currency} Price Alert"
            
            body = f"""
Hello!

Your cryptocurrency price alert has been triggered:

Currency: {currency}
Condition: Price {condition_text} ${threshold:,.2f}
Current Price: ${current_price:,.2f}

This is an automated notification. Please do not reply directly.

---
CryptoAlert Price Monitoring System
            """.strip()
            
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = self._create_connection()
            server.sendmail(self.username, to_email, msg.as_string())
            server.quit()
            
            return True
        except Exception as e:
            print(f"Failed to send alert email: {e}")
            return False
    
    def send_admin_alert(self, error_message: str, task_name: str = "Background Task") -> bool:
        """Send error alert to admin.
        
        Args:
            error_message: Error message to include.
            task_name: Name of the failed task.
            
        Returns:
            True if email was sent successfully.
        """
        if not self.admin_email:
            print("Admin email not configured")
            return False
        
        try:
            subject = f"[CryptoAlert Alert] {task_name} Failed"
            
            body = f"""
Administrator,

A system background task has failed. Please investigate:

Task Name: {task_name}
Error Message: {error_message}

---
CryptoAlert System Alert
            """.strip()
            
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = self.admin_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = self._create_connection()
            server.sendmail(self.username, self.admin_email, msg.as_string())
            server.quit()
            
            return True
        except Exception as e:
            print(f"Failed to send admin alert: {e}")
            return False
