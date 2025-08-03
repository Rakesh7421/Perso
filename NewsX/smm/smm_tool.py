#!/usr/bin/env python3
"""
Social Media Management Tool
A comprehensive tool for managing multiple social media platforms
"""

import sqlite3
import json
import os
import hashlib
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import argparse
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PlatformType(Enum):
    TWITTER = "twitter"
    INSTAGRAM = "instagram" 
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"

class PostStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

@dataclass
class SocialAccount:
    id: str
    platform: PlatformType
    username: str
    display_name: str
    access_token: str
    is_active: bool = True
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()

@dataclass
class MediaContent:
    id: str
    file_path: str
    media_type: str  # image, video, gif
    file_size: int
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()

@dataclass
class Post:
    id: str
    account_id: str
    content: str
    media_ids: List[str]
    scheduled_time: Optional[str]
    status: PostStatus
    platform_post_id: Optional[str] = None
    created_at: str = None
    published_at: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.datetime.now().isoformat()

@dataclass
class Analytics:
    id: str
    post_id: str
    platform: PlatformType
    likes: int = 0
    shares: int = 0
    comments: int = 0
    views: int = 0
    reach: int = 0
    engagement_rate: float = 0.0
    collected_at: str = None
    
    def __post_init__(self):
        if self.collected_at is None:
            self.collected_at = datetime.datetime.now().isoformat()

class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self, db_path: str = "smm_tool.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                username TEXT NOT NULL,
                display_name TEXT NOT NULL,
                access_token TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)
        
        # Media content table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media_content (
                id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                media_type TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        # Posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                content TEXT NOT NULL,
                media_ids TEXT, -- JSON array
                scheduled_time TEXT,
                status TEXT NOT NULL,
                platform_post_id TEXT,
                created_at TEXT NOT NULL,
                published_at TEXT,
                FOREIGN KEY (account_id) REFERENCES accounts (id)
            )
        """)
        
        # Analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id TEXT PRIMARY KEY,
                post_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                likes INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                views INTEGER DEFAULT 0,
                reach INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0,
                collected_at TEXT NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def execute_query(self, query: str, params: tuple = None):
        """Execute a query and return results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        return results
    
    def save_account(self, account: SocialAccount):
        """Save a social media account"""
        query = """
            INSERT OR REPLACE INTO accounts 
            (id, platform, username, display_name, access_token, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            account.id, account.platform.value, account.username,
            account.display_name, account.access_token, account.is_active,
            account.created_at
        )
        self.execute_query(query, params)
        logger.info(f"Account saved: {account.username} on {account.platform.value}")
    
    def get_accounts(self, platform: Optional[PlatformType] = None) -> List[SocialAccount]:
        """Get all accounts or accounts for specific platform"""
        if platform:
            query = "SELECT * FROM accounts WHERE platform = ? AND is_active = 1"
            results = self.execute_query(query, (platform.value,))
        else:
            query = "SELECT * FROM accounts WHERE is_active = 1"
            results = self.execute_query(query)
        
        accounts = []
        for row in results:
            accounts.append(SocialAccount(
                id=row[0], platform=PlatformType(row[1]), username=row[2],
                display_name=row[3], access_token=row[4], is_active=bool(row[5]),
                created_at=row[6]
            ))
        return accounts
    
    def save_post(self, post: Post):
        """Save a post"""
        query = """
            INSERT OR REPLACE INTO posts 
            (id, account_id, content, media_ids, scheduled_time, status, 
             platform_post_id, created_at, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            post.id, post.account_id, post.content, json.dumps(post.media_ids),
            post.scheduled_time, post.status.value, post.platform_post_id,
            post.created_at, post.published_at
        )
        self.execute_query(query, params)
        logger.info(f"Post saved: {post.id}")
    
    def get_posts(self, status: Optional[PostStatus] = None) -> List[Post]:
        """Get posts by status"""
        if status:
            query = "SELECT * FROM posts WHERE status = ?"
            results = self.execute_query(query, (status.value,))
        else:
            query = "SELECT * FROM posts"
            results = self.execute_query(query)
        
        posts = []
        for row in results:
            posts.append(Post(
                id=row[0], account_id=row[1], content=row[2],
                media_ids=json.loads(row[3]) if row[3] else [],
                scheduled_time=row[4], status=PostStatus(row[5]),
                platform_post_id=row[6], created_at=row[7], published_at=row[8]
            ))
        return posts

class PlatformConnector:
    """Base class for platform-specific connectors"""
    
    def __init__(self, account: SocialAccount):
        self.account = account
    
    def publish_post(self, post: Post) -> Dict[str, Any]:
        """Publish a post to the platform"""
        raise NotImplementedError("Subclasses must implement publish_post")
    
    def get_analytics(self, platform_post_id: str) -> Analytics:
        """Get analytics for a specific post"""
        raise NotImplementedError("Subclasses must implement get_analytics")

class TwitterConnector(PlatformConnector):
    """Twitter/X platform connector"""
    
    def publish_post(self, post: Post) -> Dict[str, Any]:
        # Simulate Twitter API call
        logger.info(f"Publishing to Twitter: {post.content[:50]}...")
        
        # In real implementation, use Twitter API v2
        # Example: tweepy.Client().create_tweet(text=post.content)
        
        return {
            "success": True,
            "platform_post_id": f"twitter_{hashlib.md5(post.content.encode()).hexdigest()[:10]}",
            "published_at": datetime.datetime.now().isoformat()
        }
    
    def get_analytics(self, platform_post_id: str) -> Analytics:
        # Simulate analytics collection
        return Analytics(
            id=f"analytics_{platform_post_id}",
            post_id=platform_post_id,
            platform=PlatformType.TWITTER,
            likes=42, shares=12, comments=8, views=1250, reach=980
        )

class InstagramConnector(PlatformConnector):
    """Instagram platform connector"""
    
    def publish_post(self, post: Post) -> Dict[str, Any]:
        logger.info(f"Publishing to Instagram: {post.content[:50]}...")
        
        # In real implementation, use Instagram Basic Display API
        # or Instagram Graph API
        
        return {
            "success": True,
            "platform_post_id": f"ig_{hashlib.md5(post.content.encode()).hexdigest()[:10]}",
            "published_at": datetime.datetime.now().isoformat()
        }
    
    def get_analytics(self, platform_post_id: str) -> Analytics:
        return Analytics(
            id=f"analytics_{platform_post_id}",
            post_id=platform_post_id,
            platform=PlatformType.INSTAGRAM,
            likes=156, shares=23, comments=34, views=2840, reach=2100
        )

class SocialMediaManager:
    """Main SMM tool class"""
    
    def __init__(self, db_path: str = "smm_tool.db"):
        self.db = DatabaseManager(db_path)
        self.connectors = {
            PlatformType.TWITTER: TwitterConnector,
            PlatformType.INSTAGRAM: InstagramConnector,
            # Add other platforms as needed
        }
    
    def add_account(self, platform: PlatformType, username: str, 
                   display_name: str, access_token: str) -> str:
        """Add a new social media account"""
        account_id = f"{platform.value}_{username}_{hashlib.md5(username.encode()).hexdigest()[:8]}"
        account = SocialAccount(
            id=account_id,
            platform=platform,
            username=username,
            display_name=display_name,
            access_token=access_token
        )
        self.db.save_account(account)
        return account_id
    
    def create_post(self, account_id: str, content: str, 
                   media_ids: List[str] = None, 
                   scheduled_time: str = None) -> str:
        """Create a new post"""
        post_id = f"post_{hashlib.md5(f'{account_id}{content}'.encode()).hexdigest()[:12]}"
        
        status = PostStatus.SCHEDULED if scheduled_time else PostStatus.DRAFT
        
        post = Post(
            id=post_id,
            account_id=account_id,
            content=content,
            media_ids=media_ids or [],
            scheduled_time=scheduled_time,
            status=status
        )
        
        self.db.save_post(post)
        return post_id
    
    def publish_post(self, post_id: str) -> bool:
        """Publish a post immediately"""
        posts = [p for p in self.db.get_posts() if p.id == post_id]
        if not posts:
            logger.error(f"Post not found: {post_id}")
            return False
        
        post = posts[0]
        accounts = [a for a in self.db.get_accounts() if a.id == post.account_id]
        if not accounts:
            logger.error(f"Account not found: {post.account_id}")
            return False
        
        account = accounts[0]
        
        if account.platform not in self.connectors:
            logger.error(f"Platform not supported: {account.platform}")
            return False
        
        connector = self.connectors[account.platform](account)
        result = connector.publish_post(post)
        
        if result.get("success"):
            post.status = PostStatus.PUBLISHED
            post.platform_post_id = result.get("platform_post_id")
            post.published_at = result.get("published_at")
            self.db.save_post(post)
            logger.info(f"Post published successfully: {post_id}")
            return True
        else:
            post.status = PostStatus.FAILED
            self.db.save_post(post)
            logger.error(f"Failed to publish post: {post_id}")
            return False
    
    def get_analytics_report(self, account_id: str = None) -> Dict[str, Any]:
        """Generate analytics report"""
        posts = self.db.get_posts(PostStatus.PUBLISHED)
        
        if account_id:
            posts = [p for p in posts if p.account_id == account_id]
        
        total_posts = len(posts)
        platforms = {}
        
        for post in posts:
            account = [a for a in self.db.get_accounts() if a.id == post.account_id][0]
            platform = account.platform.value
            
            if platform not in platforms:
                platforms[platform] = {"posts": 0, "engagement": 0}
            
            platforms[platform]["posts"] += 1
            # Simulate engagement calculation
            platforms[platform]["engagement"] += 42  # Mock data
        
        return {
            "total_posts": total_posts,
            "platforms": platforms,
            "generated_at": datetime.datetime.now().isoformat()
        }
    
    def list_accounts(self) -> List[Dict[str, Any]]:
        """List all accounts"""
        accounts = self.db.get_accounts()
        return [
            {
                "id": acc.id,
                "platform": acc.platform.value,
                "username": acc.username,
                "display_name": acc.display_name,
                "is_active": acc.is_active,
                "created_at": acc.created_at
            }
            for acc in accounts
        ]
    
    def list_posts(self, status: str = None) -> List[Dict[str, Any]]:
        """List posts by status"""
        post_status = PostStatus(status) if status else None
        posts = self.db.get_posts(post_status)
        
        return [
            {
                "id": post.id,
                "account_id": post.account_id,
                "content": post.content[:100] + "..." if len(post.content) > 100 else post.content,
                "status": post.status.value,
                "scheduled_time": post.scheduled_time,
                "created_at": post.created_at,
                "published_at": post.published_at
            }
            for post in posts
        ]

def main():
    """CLI interface for the SMM tool"""
    parser = argparse.ArgumentParser(description="Social Media Management Tool")
    parser.add_argument("--db", default="smm_tool.db", help="Database file path")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Add account command
    add_account_parser = subparsers.add_parser("add-account", help="Add social media account")
    add_account_parser.add_argument("platform", choices=[p.value for p in PlatformType])
    add_account_parser.add_argument("username")
    add_account_parser.add_argument("display_name")
    add_account_parser.add_argument("access_token")
    
    # Create post command
    create_post_parser = subparsers.add_parser("create-post", help="Create new post")
    create_post_parser.add_argument("account_id")
    create_post_parser.add_argument("content")
    create_post_parser.add_argument("--schedule", help="Schedule time (ISO format)")
    
    # Publish post command
    publish_parser = subparsers.add_parser("publish", help="Publish post")
    publish_parser.add_argument("post_id")
    
    # List commands
    subparsers.add_parser("list-accounts", help="List all accounts")
    
    list_posts_parser = subparsers.add_parser("list-posts", help="List posts")
    list_posts_parser.add_argument("--status", choices=[s.value for s in PostStatus])
    
    # Analytics command
    analytics_parser = subparsers.add_parser("analytics", help="Generate analytics report")
    analytics_parser.add_argument("--account-id", help="Specific account ID")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    smm = SocialMediaManager(args.db)
    
    try:
        if args.command == "add-account":
            account_id = smm.add_account(
                PlatformType(args.platform),
                args.username,
                args.display_name,
                args.access_token
            )
            print(f"Account added with ID: {account_id}")
        
        elif args.command == "create-post":
            post_id = smm.create_post(
                args.account_id,
                args.content,
                scheduled_time=args.schedule
            )
            print(f"Post created with ID: {post_id}")
        
        elif args.command == "publish":
            success = smm.publish_post(args.post_id)
            print("Post published successfully!" if success else "Failed to publish post")
        
        elif args.command == "list-accounts":
            accounts = smm.list_accounts()
            print(json.dumps(accounts, indent=2))
        
        elif args.command == "list-posts":
            posts = smm.list_posts(args.status)
            print(json.dumps(posts, indent=2))
        
        elif args.command == "analytics":
            report = smm.get_analytics_report(args.account_id)
            print(json.dumps(report, indent=2))
    
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()