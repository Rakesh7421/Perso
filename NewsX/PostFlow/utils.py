import csv
import json
import pandas as pd
from datetime import datetime
from io import StringIO, TextIOWrapper

def validate_post_data(data):
    """Validate post data structure and content"""
    errors = []
    
    if not isinstance(data, dict):
        errors.append("Post data must be a dictionary")
        return errors
    
    # Check required fields
    if 'content' not in data or not data['content'].strip():
        errors.append("Post content is required")
    
    if 'scheduled_time' not in data:
        errors.append("Scheduled time is required")
    
    # Validate content length
    if 'content' in data and len(data['content']) > 3000:
        errors.append("Post content exceeds LinkedIn character limit (3000 characters)")
    
    # Validate scheduled time
    if 'scheduled_time' in data:
        try:
            if isinstance(data['scheduled_time'], str):
                # Try to parse the datetime string
                scheduled_time = datetime.fromisoformat(data['scheduled_time'].replace('Z', '+00:00'))
            elif isinstance(data['scheduled_time'], datetime):
                scheduled_time = data['scheduled_time']
            else:
                errors.append("Invalid scheduled time format")
                return errors
            
            # Check if the time is in the future
            if scheduled_time <= datetime.now():
                errors.append("Scheduled time must be in the future")
                
        except (ValueError, TypeError):
            errors.append("Invalid scheduled time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
    
    return errors

def process_csv_file(file):
    """Process uploaded CSV file and extract post data"""
    posts_data = []
    errors = []
    
    try:
        # Read file content
        file_content = file.read()
        
        # Try to decode as UTF-8, fallback to latin-1
        try:
            content_str = file_content.decode('utf-8')
        except UnicodeDecodeError:
            content_str = file_content.decode('latin-1')
        
        # Use pandas to read CSV for better handling
        df = pd.read_csv(StringIO(content_str))
        
        # Check required columns
        required_columns = ['content', 'scheduled_time']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            errors.append(f"Missing required columns: {', '.join(missing_columns)}")
            return posts_data, errors
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Prepare post data
                scheduled_time = pd.to_datetime(row['scheduled_time'])
                if hasattr(scheduled_time, 'to_pydatetime'):
                    scheduled_datetime = scheduled_time.to_pydatetime()
                else:
                    scheduled_datetime = scheduled_time
                
                post_data = {
                    'content': str(row['content']).strip(),
                    'scheduled_time': scheduled_datetime,
                    'post_tags': str(row.get('post_tags', '')).strip() if pd.notna(row.get('post_tags', '')) else ''
                }
                
                # Validate the post data
                validation_errors = validate_post_data(post_data)
                row_num = index + 2  # Add 2 to account for 0-based index and header row
                if validation_errors:
                    errors.extend([f"Row {row_num}: {error}" for error in validation_errors])
                    continue
                
                posts_data.append(post_data)
                
            except Exception as e:
                row_num = index + 2  # Add 2 to account for 0-based index and header row
                errors.append(f"Error processing row {row_num}: {str(e)}")
        
    except Exception as e:
        errors.append(f"Error reading CSV file: {str(e)}")
    
    return posts_data, errors

def process_json_file(file):
    """Process uploaded JSON file and extract post data"""
    posts_data = []
    errors = []
    
    try:
        # Read file content
        file_content = file.read()
        
        # Try to decode as UTF-8
        try:
            content_str = file_content.decode('utf-8')
        except UnicodeDecodeError:
            content_str = file_content.decode('latin-1')
        
        # Parse JSON
        data = json.loads(content_str)
        
        # Handle different JSON structures
        if isinstance(data, list):
            # Array of posts
            posts_list = data
        elif isinstance(data, dict) and 'posts' in data:
            # Object with posts array
            posts_list = data['posts']
        elif isinstance(data, dict):
            # Single post object
            posts_list = [data]
        else:
            errors.append("Invalid JSON structure. Expected array of posts or object with 'posts' field")
            return posts_data, errors
        
        # Process each post
        for index, post_item in enumerate(posts_list):
            try:
                if not isinstance(post_item, dict):
                    errors.append(f"Post {index + 1}: Post data must be an object")
                    continue
                
                # Prepare post data
                post_data = {
                    'content': str(post_item.get('content', '')).strip(),
                    'scheduled_time': post_item.get('scheduled_time'),
                    'post_tags': str(post_item.get('post_tags', '')).strip()
                }
                
                # Convert scheduled_time to datetime if it's a string
                if isinstance(post_data['scheduled_time'], str):
                    try:
                        post_data['scheduled_time'] = datetime.fromisoformat(
                            post_data['scheduled_time'].replace('Z', '+00:00')
                        )
                    except ValueError:
                        # Try other common formats
                        try:
                            post_data['scheduled_time'] = datetime.strptime(
                                post_data['scheduled_time'], '%Y-%m-%d %H:%M:%S'
                            )
                        except ValueError:
                            errors.append(f"Post {index + 1}: Invalid scheduled_time format")
                            continue
                
                # Validate the post data
                validation_errors = validate_post_data(post_data)
                if validation_errors:
                    errors.extend([f"Post {index + 1}: {error}" for error in validation_errors])
                    continue
                
                posts_data.append(post_data)
                
            except Exception as e:
                errors.append(f"Error processing post {index + 1}: {str(e)}")
        
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        errors.append(f"Error reading JSON file: {str(e)}")
    
    return posts_data, errors

def format_datetime_for_display(dt):
    """Format datetime for display in templates"""
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M')
    return ''

def get_time_until_post(scheduled_time):
    """Calculate time until post is scheduled"""
    if scheduled_time > datetime.now():
        delta = scheduled_time - datetime.now()
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    else:
        return "Overdue"
