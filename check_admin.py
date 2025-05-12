import sqlite3

def check_admin():
    conn = sqlite3.connect('blog.db')
    conn.row_factory = sqlite3.Row
    
    # Get all users with admin role
    cursor = conn.execute('SELECT id, username, email, role FROM users WHERE role = ?', ('admin',))
    admin_users = cursor.fetchall()
    
    print("\nCurrent admin users in database:")
    for user in admin_users:
        print(f"ID: {user['id']}")
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        print(f"Role: {user['role']}")
        print("---")
    
    conn.close()

if __name__ == '__main__':
    check_admin() 