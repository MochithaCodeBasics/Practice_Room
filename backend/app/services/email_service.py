"""
Email service for sending password reset tokens via Gmail SMTP.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


class EmailService:
    """Gmail SMTP email service for password reset."""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")  # Gmail App Password
        self.from_email = os.getenv("SMTP_FROM_EMAIL", self.smtp_user)
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(self.smtp_user and self.smtp_password)
    
    def send_password_reset_email(self, to_email: str, username: str, reset_token: str) -> bool:
        """Send password reset email with token link."""
        if not self.is_configured():
            print(f"[EMAIL SERVICE] Not configured. Token for {username}: {reset_token}")
            return False
        
        reset_link = f"{self.frontend_url}/reset-password?token={reset_token}"
        
        subject = "Practice Room - Password Reset Request"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #405c68; color: #ffffff !important; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .warning {{ color: #856404; background: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Password Reset</h1>
                </div>
                <div class="content">
                    <p>Hello <strong>{username}</strong>,</p>
                    <p>We received a request to reset your password for your Practice Room account.</p>
                    <p>Click the button below to reset your password:</p>
                    <p style="text-align: center;">
                        <a href="{reset_link}" class="button" style="color: #ffffff; text-decoration: none;">Reset Password</a>
                    </p>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #666;">{reset_link}</p>
                    <div class="warning">
                        ⚠️ This link will expire in <strong>1 hour</strong>.<br>
                        If you didn't request this reset, you can safely ignore this email.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Hello {username},
        
        We received a request to reset your password for your Practice Room account.
        
        Click here to reset your password: {reset_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this reset, you can safely ignore this email.
        """
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            print(f"[EMAIL SERVICE] Password reset email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"[EMAIL SERVICE] Failed to send email: {e}")
            # Fallback: print token to console for development
            print(f"[EMAIL SERVICE] Token for {username}: {reset_token}")
            return False

    def send_welcome_email(self, to_email: str, username: str) -> bool:
        """Send welcome email to new users."""
        if not self.is_configured():
            print(f"[EMAIL SERVICE] Not configured. Welcome email for {username}")
            return False
        
        subject = "Welcome to Practice Room! \U0001f389"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #405c68; color: #ffffff !important; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>\U0001f44b Welcome Aboard!</h1>
                </div>
                <div class="content">
                    <p>Hello <strong>{username}</strong>,</p>
                    <p>Welcome to <strong>Practice Room</strong>! We are thrilled to have you join our community.</p>
                    <p>Get started by exploring our practice modules and solving some challenges.</p>
                    <p style="text-align: center;">
                        <a href="{self.frontend_url}" class="button" style="color: #ffffff; text-decoration: none;">Start Practicing</a>
                    </p>
                    <p>If you have any questions, feel free to reply to this email.</p>
                    <p>Happy Coding!<br>Codebasics Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Hello {username},
        
        Welcome to Practice Room! We are thrilled to have you join our community.
        
        Get started by exploring our practice modules and solving some challenges:
        {self.frontend_url}
        
        Happy Coding!
        The Codebasics Team
        """
        
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())
            
            print(f"[EMAIL SERVICE] Welcome email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"[EMAIL SERVICE] Failed to send welcome email: {e}")
            return False


# Singleton instance
email_service = EmailService()
