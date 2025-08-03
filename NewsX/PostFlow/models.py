from app import db
from datetime import datetime
from sqlalchemy import func

class Post(db.Model):
    """Model for LinkedIn posts"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, published, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    source_file = db.Column(db.String(255), nullable=True)  # Track which file the post came from
    post_tags = db.Column(db.String(500), nullable=True)  # Store hashtags and mentions
    media_url = db.Column(db.String(500), nullable=True)  # Optional media attachment
    
    def __repr__(self):
        return f'<Post {self.id}: {self.content[:50]}...>'
    
    def to_dict(self):
        """Convert post to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'content': self.content,
            'scheduled_time': self.scheduled_time.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'source_file': self.source_file,
            'post_tags': self.post_tags,
            'media_url': self.media_url
        }

class UploadLog(db.Model):
    """Model to track file uploads and imports"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # csv, json
    posts_imported = db.Column(db.Integer, default=0)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='success')  # success, failed, partial
    error_message = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<UploadLog {self.filename}: {self.posts_imported} posts>'
