-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Drop tables if they exist to avoid conflicts
DROP TABLE IF EXISTS visitor_stats;
DROP TABLE IF EXISTS cv_downloads;
DROP TABLE IF EXISTS comment_likes;
DROP TABLE IF EXISTS blog_likes;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'subscriber' CHECK (role IN ('admin', 'subscriber'))
);

-- Posts table
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    user_id INTEGER,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Comments table
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER,
    user_id INTEGER,
    author_name TEXT,
    content TEXT NOT NULL,
    liked_by_author BOOLEAN DEFAULT 0,
    is_anonymous BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Blog Likes table
CREATE TABLE blog_likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER,
    username TEXT,
    is_anonymous BOOLEAN DEFAULT 0,
    anonymous_id TEXT,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Comment Likes table
CREATE TABLE comment_likes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id INTEGER NOT NULL,
    user_id INTEGER,
    is_anonymous BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- CV Downloads table
CREATE TABLE cv_downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    reason TEXT NOT NULL,
    is_anonymous BOOLEAN DEFAULT 1,
    ip_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Visitor Statistics table
CREATE TABLE visitor_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip_address TEXT NOT NULL,
    country TEXT,
    page_visited TEXT NOT NULL,
    is_unique BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster queries
CREATE INDEX idx_posts_user_id ON posts(user_id);
CREATE INDEX idx_comments_post_id ON comments(post_id);
CREATE INDEX idx_comments_user_id ON comments(user_id);
CREATE INDEX idx_blog_likes_post_id ON blog_likes(post_id);
CREATE INDEX idx_blog_likes_user_id ON blog_likes(user_id);
CREATE INDEX idx_comment_likes_comment_id ON comment_likes(comment_id);
CREATE INDEX idx_comment_likes_user_id ON comment_likes(user_id);
CREATE INDEX idx_cv_downloads_user_id ON cv_downloads(user_id);
CREATE INDEX idx_visitor_stats_ip_address ON visitor_stats(ip_address);
CREATE INDEX idx_visitor_stats_page_visited ON visitor_stats(page_visited);

-- Optional: Insert a default admin user (password should be hashed in production)
-- INSERT INTO users (username, email, password, role) 
-- VALUES ('admin', 'admin@example.com', 'admin_password_hash', 'admin'); 