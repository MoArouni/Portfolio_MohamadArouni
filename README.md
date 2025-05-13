# Portfolio Website with CV Download Verification

This is a Flask-based portfolio website with blog functionality and email verification for CV downloads.

## Setup Instructions

1. Clone the repository
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```
3. Set up your environment variables by creating a `.env` file with the following:
   ```
   # Secret key for Flask sessions and token generation
   SECRET_KEY=your_secret_key_here

   # Admin user credentials
   USERNAME=admin
   EMAIL=admin@example.com
   PASSWORD=admin_password

   # Email settings (for verification links)
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USE_SSL=False
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   MAIL_DEFAULT_SENDER=your_email@gmail.com
   ```

4. For Gmail, you need to use an App Password:
   - Go to your Google Account at [https://myaccount.google.com/](https://myaccount.google.com/)
   - Navigate to Security > 2-Step Verification > App passwords
   - Create a new app password for your application
   - Use this password in your `.env` file

5. Run the application:
   ```
   python app.py
   ```

## Features

- Portfolio showcase
- Blog with comments and likes
- CV download with email verification
- Admin dashboard with analytics
- Responsive design

## CV Download Verification

The website supports two methods for downloading the CV:
1. Direct download (user provides email and download reason)
2. Email verification link (more secure):
   - User provides email and selects a reason for downloading
   - System emails a secure verification link to the user
   - Link is valid for 30 minutes
   - Once verified, the CV downloads automatically

## Database Schema

The application uses SQLite for data storage with tables for:
- Users and authentication
- Blog posts, comments, and likes
- CV download records and verification tokens
- Visitor statistics

## Development

The application is built with:
- Flask for the back-end
- SQLite for the database
- Vanilla JavaScript for front-end interactivity
- HTML/CSS for template rendering

## Technical Details

### Backend
- Flask framework with SQLite database
- Secure password hashing with Werkzeug
- RESTful API endpoints for AJAX interactions
- Jinja2 templating engine

### Frontend
- Custom CSS with variables for theming
- Vanilla JavaScript for interactive features
- FontAwesome icons
- Particles.js for animated backgrounds

### Analytics
- Track CV downloads with reason categorization
- Monitor blog post popularity 
- Analyze user engagement

## Recent Enhancements

### Blog Functionality Improvements
- Fixed anonymous commenting system
- Implemented tracking system for anonymous likes using localStorage
- Added new database models for enhanced analytics

### Authentication System
- Redesigned login and registration pages
- Added password strength indicator
- Improved form validation with meaningful error messages
- Enhanced security features

### CV Download System
- Redesigned download modal with card-style options
- Added analytics tracking for download reasons
- Improved user experience with visual feedback and loading states

### Timeline & Education Section
- Added expandable content sections with "Read More" functionality
- Improved timeline visualization
- Enhanced mobile responsiveness

## Files Structure

- `schema.sql` - SQL schema for creating database tables
- `db_init.py` - Script to initialize the database
- `models.py` - Python classes for database operations
- `app.py` - Flask application
- `templates` - Pages displayed to the User.
- `static`- Styling files for the pages (templates).

## Database Relationships

- A user can have multiple posts and comments
- A post belongs to a user and can have multiple comments
- A comment belongs to a post and optionally to a user 