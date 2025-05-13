"""
Setup Environment Variables Script

This script generates a .env file with the proper configuration for your app.
Run this script and follow the instructions to create your .env file.
"""
import os
import getpass
import secrets

def generate_secret_key():
    """Generate a secure random secret key"""
    return secrets.token_hex(32)

def main():
    print("Setting up environment variables")
    print("===============================")
    print("\nThis script will help you configure your application's .env file.\n")
    
    # Check if .env already exists
    if os.path.exists('.env'):
        overwrite = input("A .env file already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print("Operation cancelled.")
            return
    
    config = {}
    
    # Flask secret key (generate one if not provided)
    secret_key = generate_secret_key()
    config['SECRET_KEY'] = secret_key
    
    # Email settings
    print("\nMail Server Configuration:")
    print("------------------------")
    
    config['MAIL_SERVER'] = input("Mail server [smtp.gmail.com]: ") or "smtp.gmail.com"
    config['MAIL_PORT'] = input("Mail port [587]: ") or "587"
    config['MAIL_USE_TLS'] = input("Use TLS (True/False) [True]: ") or "True"
    config['MAIL_USE_SSL'] = input("Use SSL (True/False) [False]: ") or "False"
    
    print("\nFor Gmail users, you must use an App Password. To create one:")
    print("1. Enable 2-Step Verification at https://myaccount.google.com/security")
    print("2. Create an App Password at https://myaccount.google.com/apppasswords")
    print("   (Select 'App' and 'Other', name it 'Portfolio')")
    print("3. Copy the 16-character password it generates\n")
    
    config['MAIL_USERNAME'] = input("Email address: ")
    config['MAIL_PASSWORD'] = getpass.getpass("App Password (will not be displayed): ")
    config['MAIL_DEFAULT_SENDER'] = input(f"Default sender [{config['MAIL_USERNAME']}]: ") or config['MAIL_USERNAME']
    
    # Write config to .env file
    with open('.env', 'w') as f:
        f.write("# Flask Application Settings\n")
        f.write(f"SECRET_KEY={config['SECRET_KEY']}\n\n")
        
        f.write("# Mail Settings\n")
        f.write(f"MAIL_SERVER={config['MAIL_SERVER']}\n")
        f.write(f"MAIL_PORT={config['MAIL_PORT']}\n")
        f.write(f"MAIL_USE_TLS={config['MAIL_USE_TLS']}\n")
        f.write(f"MAIL_USE_SSL={config['MAIL_USE_SSL']}\n")
        f.write(f"MAIL_USERNAME={config['MAIL_USERNAME']}\n")
        f.write(f"MAIL_PASSWORD={config['MAIL_PASSWORD']}\n")
        f.write(f"MAIL_DEFAULT_SENDER={config['MAIL_DEFAULT_SENDER']}\n")
    
    print("\n.env file created successfully!")
    print("This file contains sensitive information and should not be committed to version control.")

if __name__ == "__main__":
    main() 