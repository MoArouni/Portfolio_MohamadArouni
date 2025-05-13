import sqlite3

# Connect to the database
conn = sqlite3.connect('blog.db')

# SQL script to create the cv_verifications table
sql = '''
-- CV Verification Links table
CREATE TABLE IF NOT EXISTS cv_verifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    reason TEXT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    is_used BOOLEAN DEFAULT 0,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster token lookups
CREATE INDEX IF NOT EXISTS idx_cv_verifications_token ON cv_verifications(token);
'''

# Execute the SQL
conn.executescript(sql)

# Commit changes and close connection
conn.commit()
conn.close()

print("CV verifications table created successfully!") 