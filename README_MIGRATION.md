# Migration from SQLite to PostgreSQL

This project has been updated to use PostgreSQL instead of SQLite. Below are the instructions for setting up and migrating your data.

## Requirements

- PostgreSQL server (version 12 or higher)
- Python packages: `psycopg2-binary` and `flask-sqlalchemy`

## Setup Instructions

1. **Install and Configure PostgreSQL**

   - [Download and install PostgreSQL](https://www.postgresql.org/download/)
   - Create a new database for your portfolio:
     ```sql
     CREATE DATABASE portfolio_db;
     ```
   - Create a user with appropriate permissions:
     ```sql
     CREATE USER myuser WITH PASSWORD 'mypassword';
     GRANT ALL PRIVILEGES ON DATABASE portfolio_db TO myuser;
     ```

2. **Update Environment Variables**

   Create a `.env` file with the following variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/portfolio_db
   SECRET_KEY=your_secret_key_here
   USERNAME=admin
   EMAIL=admin@example.com
   PASSWORD=securepassword
   ```

   Replace the connection string components with your PostgreSQL credentials.

3. **Install Required Python Packages**

   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**

   Run the application once to create the tables:
   ```bash
   python app.py
   ```

## Migrating Data from SQLite

If you have existing data in SQLite that you want to migrate:

1. **Export data from your existing SQLite database**

   You can use the `sqlite3` command-line tool to export data as CSV:
   ```bash
   sqlite3 blog.db
   sqlite> .headers on
   sqlite> .mode csv
   sqlite> .output users.csv
   sqlite> SELECT * FROM users;
   sqlite> .output posts.csv
   sqlite> SELECT * FROM posts;
   # Repeat for other tables
   sqlite> .exit
   ```

2. **Import data into PostgreSQL**

   Use PostgreSQL's `COPY` command to import the CSV files:
   ```sql
   COPY users(id, username, email, password, role, created_at) 
   FROM '/path/to/users.csv' DELIMITER ',' CSV HEADER;
   
   -- Update sequence to start after the highest ID
   SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
   
   -- Repeat for other tables
   ```

## Important Changes

The migration included several key changes:

1. SQLite-specific SQL functions have been replaced with PostgreSQL equivalents
   - `strftime()` -> `TO_CHAR()`
   - Boolean values: `0/1` -> `false/true`

2. Query parameters now use named parameters (`:param`) instead of placeholders (`?`)

3. Transaction management uses SQLAlchemy's session instead of SQLite connection

4. Database schema has been updated to use PostgreSQL data types (e.g., SERIAL for auto-incrementing IDs)

## Verification

After migration, verify that all functionality works by:
1. Logging in with admin credentials
2. Creating a new blog post
3. Viewing analytics
4. Testing like/comment functionality

## Troubleshooting

If you encounter issues:

- Check PostgreSQL logs for errors
- Verify connection string format in `.env` file
- Ensure the PostgreSQL service is running
- Check that your database user has sufficient privileges

## Database Configuration

The application is now configured to use:

1. **PostgreSQL** in production (when `DATABASE_URL` environment variable is set)
2. **SQLite** for development/testing (when `DATABASE_URL` is not set)

This dual database support allows you to:
- Deploy to production with PostgreSQL for better performance and scalability
- Develop locally with SQLite without requiring a PostgreSQL server installation

When using SQLite for development, the application will:
1. Create a `blog.db` file in the project root directory
2. Apply SQLite-specific schema adaptations automatically
3. Log a warning message indicating that SQLite is being used for development only 