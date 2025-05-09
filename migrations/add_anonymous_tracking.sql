-- Migration script to add anonymous tracking columns

-- Add anonymous_id and ip_address columns to blog_likes table
ALTER TABLE blog_likes ADD COLUMN anonymous_id TEXT;
ALTER TABLE blog_likes ADD COLUMN ip_address TEXT;

-- Create indexes for the new columns
CREATE INDEX IF NOT EXISTS idx_blog_likes_anonymous_id ON blog_likes(anonymous_id);
CREATE INDEX IF NOT EXISTS idx_blog_likes_ip_address ON blog_likes(ip_address); 