"""
Email service for sending reminders via Gmail SMTP.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

from src.core.config import settings


class EmailService:
    """Service for sending emails via Gmail SMTP."""

    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.gmail_email = getattr(settings, 'gmail_email', None)
        self.gmail_app_password = getattr(settings, 'gmail_app_password', None)

    def send_reminder(
        self,
        to_email: str,
        task_title: str,
        task_description: Optional[str],
        due_date: datetime,
        priority: Optional[str] = None,
        tags: Optional[list] = None,
        task_id: Optional[str] = None
    ) -> bool:
        """
        Send reminder email for task due soon.

        Args:
            to_email: Recipient email address
            task_title: Title of the task
            task_description: Detailed description of the task
            due_date: When the task is due
            priority: Task priority (low, medium, high)
            tags: Task tags
            task_id: Unique task identifier

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.gmail_email or not self.gmail_app_password:
            print("Email service not configured: Gmail credentials missing")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f'🔔 Reminder: Task Due Tomorrow - {task_title}'
            msg['From'] = self.gmail_email
            msg['To'] = to_email

            # Format priority for display
            priority_display = {
                'low': '🟢 Low',
                'medium': '🟡 Medium',
                'high': '🔴 High'
            }.get(priority or 'medium', '⚪ Medium')

            # Format tags for display
            tags_display = ''
            if tags:
                tags_display = '<p style="color: #666;"><strong>🏷️ Tags:</strong> ' + ', '.join(tags) + '</p>'

            # Calculate time until due
            now = datetime.utcnow()
            time_until_due = due_date - now
            hours_remaining = int(time_until_due.total_seconds() / 3600)

            # Email body with full task details
            html = f"""
            <html>
              <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                  <h2 style="color: #667eea; margin-bottom: 10px;">🔔 Task Reminder</h2>
                  <p style="color: #666; font-size: 16px;">Your task is due <strong>tomorrow</strong>:</p>

                  <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px; margin: 25px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="color: #ffffff; margin-top: 0; font-size: 24px;">{task_title}</h3>

                    {f'<p style="color: #e0e7ff; font-size: 16px; margin: 15px 0; line-height: 1.8;">{task_description}</p>' if task_description else ''}

                    <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 8px; margin-top: 20px;">
                      <p style="color: #ffffff; margin: 8px 0; font-size: 15px;">
                        <strong>📅 Due Date:</strong> {due_date.strftime('%B %d, %Y at %I:%M %p')}
                      </p>
                      <p style="color: #ffffff; margin: 8px 0; font-size: 15px;">
                        <strong>⏰ Time Remaining:</strong> {hours_remaining} hours
                      </p>
                      <p style="color: #ffffff; margin: 8px 0; font-size: 15px;">
                        <strong>🎯 Priority:</strong> {priority_display}
                      </p>
                      {f'{tags_display}' if tags_display else ''}
                    </div>
                  </div>

                  <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea; margin: 20px 0;">
                    <p style="margin: 0; color: #495057; font-size: 15px;">
                      <strong>💡 Tip:</strong> Make sure to complete your task on time to stay productive!
                    </p>
                  </div>

                  <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                  <p style="color: #6c757d; font-size: 12px; text-align: center;">
                    This is an automated reminder from your <strong>Todo App</strong>.<br>
                    You received this because you created this task with a due date.<br>
                    Task ID: {task_id or 'N/A'}
                  </p>
                </div>
              </body>
            </html>
            """

            part = MIMEText(html, 'html')
            msg.attach(part)

            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.gmail_email, self.gmail_app_password)
            server.send_message(msg)
            server.quit()

            print(f"✅ Reminder email sent to {to_email} for task: {task_title}")
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False


# Singleton instance
email_service = EmailService()
