from models import User

def create_admin_account(username, email, password):
    """Create a new admin account"""
    user_id = User.create(username, email, password, role='admin')
    if user_id:
        print(f"Admin account created successfully! ID: {user_id}")
        print(f"Username: {username}")
        print(f"Email: {email}")
    else:
        print("Failed to create admin account. Email or username might already exist.")

if __name__ == "__main__":
    print("Create new admin account")
    print("-" * 20)
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")
    
    create_admin_account(username, email, password) 