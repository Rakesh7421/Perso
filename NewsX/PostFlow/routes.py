from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app, db
from models import Post, UploadLog
from utils import process_csv_file, process_json_file, validate_post_data
from datetime import datetime, timedelta
import os
import json

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard showing all posts"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    
    # Build query
    query = Post.query
    if status_filter != 'all':
        query = query.filter(Post.status == status_filter)
    
    # Get posts ordered by scheduled time
    posts = query.order_by(Post.scheduled_time.desc()).all()
    
    # Get statistics
    total_posts = Post.query.count()
    scheduled_posts = Post.query.filter(Post.status == 'scheduled').count()
    published_posts = Post.query.filter(Post.status == 'published').count()
    
    # Get recent uploads
    recent_uploads = UploadLog.query.order_by(UploadLog.upload_time.desc()).limit(5).all()
    
    return render_template('dashboard.html', 
                         posts=posts, 
                         total_posts=total_posts,
                         scheduled_posts=scheduled_posts,
                         published_posts=published_posts,
                         recent_uploads=recent_uploads,
                         current_filter=status_filter)

@app.route('/create-post', methods=['GET', 'POST'])
def create_post():
    """Create a new post manually"""
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        scheduled_date = request.form.get('scheduled_date')
        scheduled_time = request.form.get('scheduled_time')
        post_tags = request.form.get('post_tags', '').strip()
        
        # Validate input
        if not content:
            flash('Post content is required.', 'error')
            return render_template('create_post.html')
        
        if len(content) > 3000:  # LinkedIn character limit
            flash('Post content exceeds LinkedIn character limit (3000 characters).', 'error')
            return render_template('create_post.html')
        
        if not scheduled_date or not scheduled_time:
            flash('Scheduled date and time are required.', 'error')
            return render_template('create_post.html')
        
        try:
            # Combine date and time
            scheduled_datetime = datetime.strptime(f"{scheduled_date} {scheduled_time}", "%Y-%m-%d %H:%M")
            
            # Check if the scheduled time is in the future
            if scheduled_datetime <= datetime.now():
                flash('Scheduled time must be in the future.', 'error')
                return render_template('create_post.html')
            
            # Create new post
            post = Post(
                content=content,
                scheduled_time=scheduled_datetime,
                post_tags=post_tags,
                status='scheduled'
            )
            
            db.session.add(post)
            db.session.commit()
            
            flash('Post scheduled successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except ValueError:
            flash('Invalid date or time format.', 'error')
            return render_template('create_post.html')
        except Exception as e:
            flash(f'Error creating post: {str(e)}', 'error')
            return render_template('create_post.html')
    
    # Set default values for the form
    default_date = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d")
    default_time = (datetime.now() + timedelta(hours=1)).strftime("%H:%M")
    
    return render_template('create_post.html', default_date=default_date, default_time=default_time)

@app.route('/upload', methods=['GET', 'POST'])
def upload_data():
    """Handle file uploads for bulk post import"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'error')
            return render_template('upload.html')
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return render_template('upload.html')
        
        filename = file.filename
        if not filename or not filename.lower().endswith(('.csv', '.json')):
            flash('Only CSV and JSON files are supported.', 'error')
            return render_template('upload.html')
        
        try:
            file_type = 'csv' if filename.lower().endswith('.csv') else 'json'
            
            # Process the file
            if file_type == 'csv':
                posts_data, errors = process_csv_file(file)
            else:
                posts_data, errors = process_json_file(file)
            
            if errors and not posts_data:
                # Complete failure
                log = UploadLog(
                    filename=filename,
                    file_type=file_type,
                    posts_imported=0,
                    status='failed',
                    error_message='; '.join(errors)
                )
                db.session.add(log)
                db.session.commit()
                
                flash(f'File upload failed: {"; ".join(errors)}', 'error')
                return render_template('upload.html')
            
            # Save posts to database
            posts_imported = 0
            for post_data in posts_data:
                try:
                    post = Post(
                        content=post_data['content'],
                        scheduled_time=post_data['scheduled_time'],
                        post_tags=post_data.get('post_tags', ''),
                        source_file=filename,
                        status='scheduled'
                    )
                    db.session.add(post)
                    posts_imported += 1
                except Exception as e:
                    errors.append(f"Error saving post: {str(e)}")
            
            db.session.commit()
            
            # Log the upload
            log = UploadLog(
                filename=filename,
                file_type=file_type,
                posts_imported=posts_imported,
                status='partial' if errors else 'success',
                error_message='; '.join(errors) if errors else None
            )
            db.session.add(log)
            db.session.commit()
            
            if errors:
                flash(f'Upload completed with {posts_imported} posts imported. Errors: {"; ".join(errors)}', 'warning')
            else:
                flash(f'Successfully imported {posts_imported} posts!', 'success')
            
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}', 'error')
            return render_template('upload.html')
    
    return render_template('upload.html')

@app.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    """Edit an existing post"""
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        scheduled_date = request.form.get('scheduled_date')
        scheduled_time = request.form.get('scheduled_time')
        post_tags = request.form.get('post_tags', '').strip()
        
        # Validate input
        if not content:
            flash('Post content is required.', 'error')
            return render_template('create_post.html', post=post, edit_mode=True)
        
        if len(content) > 3000:
            flash('Post content exceeds LinkedIn character limit (3000 characters).', 'error')
            return render_template('create_post.html', post=post, edit_mode=True)
        
        try:
            # Combine date and time
            scheduled_datetime = datetime.strptime(f"{scheduled_date} {scheduled_time}", "%Y-%m-%d %H:%M")
            
            # Update post
            post.content = content
            post.scheduled_time = scheduled_datetime
            post.post_tags = post_tags
            post.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Post updated successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except ValueError:
            flash('Invalid date or time format.', 'error')
            return render_template('create_post.html', post=post, edit_mode=True)
        except Exception as e:
            flash(f'Error updating post: {str(e)}', 'error')
            return render_template('create_post.html', post=post, edit_mode=True)
    
    return render_template('create_post.html', post=post, edit_mode=True)

@app.route('/delete-post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    """Delete a post"""
    post = Post.query.get_or_404(post_id)
    
    try:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting post: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/api/posts')
def api_posts():
    """API endpoint to get posts as JSON"""
    posts = Post.query.order_by(Post.scheduled_time.asc()).all()
    return jsonify([post.to_dict() for post in posts])

@app.route('/api/analytics')
def api_analytics():
    """API endpoint for analytics data"""
    total_posts = Post.query.count()
    scheduled_posts = Post.query.filter(Post.status == 'scheduled').count()
    published_posts = Post.query.filter(Post.status == 'published').count()
    failed_posts = Post.query.filter(Post.status == 'failed').count()
    
    return jsonify({
        'total_posts': total_posts,
        'scheduled_posts': scheduled_posts,
        'published_posts': published_posts,
        'failed_posts': failed_posts
    })

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
