import smtplib
import ssl

def test_gmail_smtp(email, app_password):
    """Test Gmail SMTP specifically"""
    
    print(f"Testing Gmail SMTP for: {email}")
    
    try:
        # Gmail SMTP settings
        smtp_server = "smtp.gmail.com"
        port = 587
        
        # Create SMTP session
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()  # Enable security
        server.login(email, app_password)
        
        # Send test email
        subject = "Gmail SMTP Test - Dev Digest"
        body = "If you receive this, your Gmail SMTP is working!"
        message = f"Subject: {subject}\n\n{body}"
        
        server.sendmail(email, email, message)
        server.quit()
        
        print("✅ Gmail SMTP test successful!")
        print("📧 Check your Gmail inbox")
        return True
        
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed!")
        print("💡 Check your app password")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# Replace with your credentials
email = "gupta.sanat24@gmail.com"
app_password = "edvxlpruyyksndrs"

if __name__ == "__main__":
    test_gmail_smtp(email, app_password)