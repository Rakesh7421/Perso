#!/usr/bin/env python3
"""
SMM Tool Web Interface
A Flask-based web interface for the Social Media Management Tool
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
import json
import os
from smm_tool import SocialMediaManager, PlatformType, PostStatus
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'smm_tool_secret_key_change_in_production'
CORS(app)

# Initialize SMM manager
smm = SocialMediaManager()

@app.route('/')
def dashboard():
    """Main dashboard"""
    try:
        accounts = smm.list_accounts()
        posts = smm.list_posts()
        analytics = smm.get_analytics_report()
        
        return render_template('dashboard.html', 
                             accounts=accounts, 
                             posts=posts[:10],  # Show latest 10 posts
                             analytics=analytics)
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        flash(f"Error loading dashboard: {e}", 'error')
        return render_template('dashboard.html', accounts=[], posts=[], analytics={})

@app.route('/accounts')
def accounts():
    """Accounts management page"""
    try:
        accounts_list = smm.list_accounts()
        return render_template('accounts.html', accounts=accounts_list)
    except Exception as e:
        logger.error(f"Accounts page error: {e}")
        flash(f"Error loading accounts: {e}", 'error')
        return render_template('accounts.html', accounts=[])

@app.route('/add_account', methods=['GET', 'POST'])
def add_account():
    """Add new account page"""
    if request.method == 'POST':
        try:
            platform = request.form['platform']
            username = request.form['username']
            display_name = request.form['display_name']
            access_token = request.form['access_token']
            
            account_id = smm.add_account(
                PlatformType(platform),
                username,
                display_name,
                access_token
            )
            
            flash(f"Account added successfully! ID: {account_id}", 'success')
            return redirect(url_for('accounts'))
        
        except Exception as e:
            logger.error(f"Add account error: {e}")
            flash(f"Error adding account: {e}", 'error')
    
    platforms = [p.value for p in PlatformType]
    return render_template('add_account.html', platforms=platforms)

@app.route('/posts')
def posts():
    """Posts management page"""
    try:
        status_filter = request.args.get('status')
        posts_list = smm.list_posts(status_filter)
        return render_template('posts.html', posts=posts_list, current_status=status_filter)
    except Exception as e:
        logger.error(f"Posts page error: {e}")
        flash(f"Error loading posts: {e}", 'error')
        return render_template('posts.html', posts=[], current_status=None)

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    """Create new post page"""
    if request.method == 'POST':
        try:
            account_id = request.form['account_id']
            content = request.form['content']
            scheduled_time = request.form.get('scheduled_time') or None
            
            post_id = smm.create_post(account_id, content, scheduled_time=scheduled_time)
            
            # Auto-publish if not scheduled
            if not scheduled_time:
                publish_success = smm.publish_post(post_id)
                if publish_success:
                    flash(f"Post created and published successfully! ID: {post_id}", 'success')
                else:
                    flash(f"Post created but failed to publish. ID: {post_id}", 'warning')
            else:
                flash(f"Post scheduled successfully! ID: {post_id}", 'success')
            
            return redirect(url_for('posts'))
        
        except Exception as e:
            logger.error(f"Create post error: {e}")
            flash(f"Error creating post: {e}", 'error')
    
    try:
        accounts_list = smm.list_accounts()
        return render_template('create_post.html', accounts=accounts_list)
    except Exception as e:
        logger.error(f"Create post page error: {e}")
        flash(f"Error loading create post page: {e}", 'error')
        return render_template('create_post.html', accounts=[])

@app.route('/analytics')
def analytics():
    """Analytics page"""
    try:
        account_id = request.args.get('account_id')
        analytics_data = smm.get_analytics_report(account_id)
        accounts_list = smm.list_accounts()
        
        return render_template('analytics.html', 
                             analytics=analytics_data, 
                             accounts=accounts_list,
                             selected_account=account_id)
    except Exception as e:
        logger.error(f"Analytics page error: {e}")
        flash(f"Error loading analytics: {e}", 'error')
        return render_template('analytics.html', analytics={}, accounts=[], selected_account=None)

# API endpoints
@app.route('/api/publish/<post_id>', methods=['POST'])
def api_publish_post(post_id):
    """API endpoint to publish a post"""
    try:
        success = smm.publish_post(post_id)
        return jsonify({'success': success, 'message': 'Post published' if success else 'Failed to publish'})
    except Exception as e:
        logger.error(f"API publish error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/accounts')
def api_accounts():
    """API endpoint to get all accounts"""
    try:
        accounts_list = smm.list_accounts()
        return jsonify(accounts_list)
    except Exception as e:
        logger.error(f"API accounts error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/posts')
def api_posts():
    """API endpoint to get all posts"""
    try:
        status = request.args.get('status')
        posts_list = smm.list_posts(status)
        return jsonify(posts_list)
    except Exception as e:
        logger.error(f"API posts error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics')
def api_analytics():
    """API endpoint to get analytics"""
    try:
        account_id = request.args.get('account_id')
        analytics_data = smm.get_analytics_report(account_id)
        return jsonify(analytics_data)
    except Exception as e:
        logger.error(f"API analytics error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(host='0.0.0.0', port=5000, debug=True)