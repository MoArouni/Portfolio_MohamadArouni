# Portfolio Website

A modern, responsive portfolio website built with Flask, featuring a blog system, project showcase, and professional CV presentation.

## Features

### 1. Modern UI/UX
- Responsive design that adapts to all screen sizes
- Smooth animations and transitions for an engaging user experience
- Interactive elements with visual feedback

### 2. Enhanced Blog System
- Full-featured blog with posts, comments, and likes
- Support for both authenticated and anonymous users
- Advanced commenting system with author interactions
- Like/unlike functionality with tracking for anonymous users

### 3. Professional Presentation
- Customized timeline for education and experience
- Interactive project cards with filtering by category
- Skill display with visual progress indicators
- Downloadable CV with analytics tracking

### 4. User Authentication
- Secure login and registration system
- Role-based permissions (admin, subscriber)
- Profile management

### 5. Admin Dashboard
- Blog post management (create, edit, delete)
- Comment moderation
- Analytics tracking for posts, downloads, and site traffic

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

## Setup Instructions

### 1. Install required packages

```bash
pip install -r requirements.txt
```

### 2. Initialize the database

```bash
python db_init.py
```

### 3. Run the application

```bash
python app.py
```

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

## Database Relationships

- A user can have multiple posts and comments
- A post belongs to a user and can have multiple comments
- A comment belongs to a post and optionally to a user 