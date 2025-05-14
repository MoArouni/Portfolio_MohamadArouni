-- PostgreSQL schema for Portfolio app

-- Drop tables if they exist to avoid conflicts
DROP TABLE IF EXISTS cv_verifications CASCADE;
DROP TABLE IF EXISTS visitor_stats CASCADE;
DROP TABLE IF EXISTS cv_downloads CASCADE;
DROP TABLE IF EXISTS comment_likes CASCADE;
DROP TABLE IF EXISTS blog_likes CASCADE;
DROP TABLE IF EXISTS comments CASCADE;
DROP TABLE IF EXISTS posts CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'subscriber' CHECK (role IN ('admin', 'subscriber')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Posts table
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    user_id INTEGER,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Comments table
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER,
    user_id INTEGER,
    author_name VARCHAR(255),
    content TEXT NOT NULL,
    liked_by_author BOOLEAN DEFAULT false,
    is_anonymous BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Blog Likes table
CREATE TABLE blog_likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER,
    username VARCHAR(255),
    is_anonymous BOOLEAN DEFAULT false,
    anonymous_id VARCHAR(255),
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Comment Likes table
CREATE TABLE comment_likes (
    id SERIAL PRIMARY KEY,
    comment_id INTEGER NOT NULL,
    user_id INTEGER,
    is_anonymous BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- CV Downloads table
CREATE TABLE cv_downloads (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    reason TEXT NOT NULL,
    is_anonymous BOOLEAN DEFAULT true,
    ip_address VARCHAR(45),
    email VARCHAR(255),
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- Visitor Statistics table
CREATE TABLE visitor_stats (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    country VARCHAR(100),
    page_visited TEXT NOT NULL,
    is_unique BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notifications table
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    user_id INTEGER,
    username VARCHAR(255),
    is_anonymous BOOLEAN DEFAULT true,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- CV Verification Links table
CREATE TABLE cv_verifications (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    is_used BOOLEAN DEFAULT false,
    expires_at TIMESTAMP NOT NULL,
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
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_created_at ON notifications(created_at); 