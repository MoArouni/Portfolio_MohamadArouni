from db_init import get_db_connection
from datetime import datetime

def create_backdated_post(title, content, user_id, timestamp_str):
    """
    Create a blog post with a custom timestamp
    timestamp_str format: 'YYYY-MM-DD HH:MM:SS'
    Example: '2023-12-25 14:30:00'
    """
    try:
        # Validate timestamp format
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        
        # Connect to database
        conn = get_db_connection()
        
        # Insert post with custom timestamp
        cursor = conn.execute(
            'INSERT INTO posts (title, content, user_id, created_at) VALUES (?, ?, ?, ?)',
            (title, content, user_id, timestamp_str)
        )
        post_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"\nPost created successfully!")
        print(f"Post ID: {post_id}")
        print(f"Title: {title}")
        print(f"Timestamp: {timestamp_str}")
        return post_id
        
    except ValueError:
        print("\nError: Invalid timestamp format. Use 'YYYY-MM-DD HH:MM:SS'")
        return None
    except Exception as e:
        print(f"\nError creating post: {str(e)}")
        return None

if __name__ == "__main__":
    print("Create Backdated Blog Post")
    print("-" * 25)
    
    # Get post details
    title = input("Enter post title: ")
    print("\nEnter post content (press Enter twice to finish):")
    content_lines = []
    while True:
        line = input()
        if line == "":
            break
        content_lines.append(line)
    content = "\n".join(content_lines)
    
    # Get user ID
    while True:
        try:
            user_id = int(input("\nEnter user ID (must be an existing user): "))
            break
        except ValueError:
            print("Please enter a valid number")
    
    # Get timestamp
    print("\nEnter timestamp in format 'YYYY-MM-DD HH:MM:SS'")
    print("Example: 2023-12-25 14:30:00")
    timestamp = input("Timestamp: ")
    
    # Create the post
    create_backdated_post(title, content, user_id, timestamp) 