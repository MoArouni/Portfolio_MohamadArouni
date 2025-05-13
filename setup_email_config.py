"""
Email Configuration Setup Script

This script helps you configure the email settings for your portfolio application.
It will create a .env file with your email credentials.

Instructions for Gmail:
1. Enable 2-factor authentication on your Google account
2. Generate an "App Password" at https://myaccount.google.com/apppasswords
3. Use that App Password here instead of your regular Gmail password
"""

import os
import getpass

def main():
    print("Email Configuration Setup")
    print("========================")
    print("\nThis script will help you set up your email settings for the CV download feature.")
    print("For Gmail users: You'll need to create an App Password in your Google Account settings.")
    print("See: https://myaccount.google.com/apppasswords\n")
    
    # Get existing .env file content if it exists
    env_vars = {}
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # Get Secret Key
    secret_key = env_vars.get('SECRET_KEY', '')
    if not secret_key:
        import random
        import string
        # Generate a random secret key if one doesn't exist
        chars = string.ascii_letters + string.digits + '!@#$%^&*()_-+=[]{}|;:,.<>?'
        secret_key = ''.join(random.choice(chars) for _ in range(32))
    
    # Get Email Settings
    mail_server = input(f"Mail Server [{env_vars.get('MAIL_SERVER', 'smtp.gmail.com')}]: ") or env_vars.get('MAIL_SERVER', 'smtp.gmail.com')
    mail_port = input(f"Mail Port [{env_vars.get('MAIL_PORT', '587')}]: ") or env_vars.get('MAIL_PORT', '587')
    mail_use_tls = input(f"Use TLS (True/False) [{env_vars.get('MAIL_USE_TLS', 'True')}]: ") or env_vars.get('MAIL_USE_TLS', 'True')
    mail_use_ssl = input(f"Use SSL (True/False) [{env_vars.get('MAIL_USE_SSL', 'False')}]: ") or env_vars.get('MAIL_USE_SSL', 'False')
    
    mail_username = input(f"Email Username/Address [{env_vars.get('MAIL_USERNAME', '')}]: ") or env_vars.get('MAIL_USERNAME', '')
    mail_password = getpass.getpass(f"Email Password/App Password (leave empty to keep existing): ")
    if not mail_password and 'MAIL_PASSWORD' in env_vars:
        mail_password = env_vars['MAIL_PASSWORD']
    
    mail_default_sender = input(f"Default Sender Email [{env_vars.get('MAIL_DEFAULT_SENDER', mail_username)}]: ") or env_vars.get('MAIL_DEFAULT_SENDER', mail_username)
    
    # Create .env file
    with open('.env', 'w') as f:
        f.write(f"# Flask app settings\n")
        f.write(f"SECRET_KEY={secret_key}\n\n")
        
        f.write(f"# Email configuration\n")
        f.write(f"MAIL_SERVER={mail_server}\n")
        f.write(f"MAIL_PORT={mail_port}\n")
        f.write(f"MAIL_USE_TLS={mail_use_tls}\n")
        f.write(f"MAIL_USE_SSL={mail_use_ssl}\n")
        f.write(f"MAIL_USERNAME={mail_username}\n")
        f.write(f"MAIL_PASSWORD={mail_password}\n")
        f.write(f"MAIL_DEFAULT_SENDER={mail_default_sender}\n")
    
    print("\nEmail configuration saved to .env file!")
    print("Your application should now be able to send emails for CV download verification.")
    print("\nIMPORTANT: If you're using Gmail, make sure you've created an App Password in your Google Account.")
    print("The .env file contains sensitive information and should not be committed to version control.")

if __name__ == "__main__":
    main() 