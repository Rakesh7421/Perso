# Overview

This is a LinkedIn Post Scheduler web application built with Flask that allows users to create, schedule, and manage LinkedIn posts. The application supports both manual post creation and bulk data import via CSV/JSON files. It features a dashboard for post management, file upload capabilities, and a clean user interface styled with Bootstrap and LinkedIn branding.

**Status**: Production ready and fully configured for Vercel deployment with Python runtime support.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with a base template inheritance structure
- **UI Framework**: Bootstrap 5.3.0 for responsive design and components
- **Styling**: Custom CSS with LinkedIn-inspired color scheme and branding
- **JavaScript**: Vanilla JavaScript for client-side interactions, form validation, and UI enhancements
- **Icon System**: Bootstrap Icons for consistent iconography

## Backend Architecture
- **Web Framework**: Flask with SQLAlchemy ORM for database operations
- **Database Abstraction**: SQLAlchemy with DeclarativeBase for model definitions
- **File Processing**: Custom utilities for CSV and JSON file parsing using pandas
- **Configuration Management**: Environment-based configuration for development (SQLite) and production (PostgreSQL)
- **Middleware**: ProxyFix for proper header handling in production deployments

## Database Design
- **Post Model**: Stores post content, scheduling information, status tracking, and metadata
- **UploadLog Model**: Tracks file upload history and import statistics
- **Database Strategy**: SQLite for local development, PostgreSQL for production via environment variable detection

## Application Structure
- **Modular Design**: Separated concerns with dedicated files for models, routes, utilities, and configuration
- **Template Organization**: Base template with extending child templates for consistent layout
- **Static Assets**: Organized CSS and JavaScript files for styling and client-side functionality

## Data Processing
- **File Upload**: Support for CSV and JSON formats with validation and error handling
- **Content Validation**: Character limits, required field validation, and scheduling time validation
- **Bulk Import**: Batch processing capabilities for multiple posts from uploaded files

# External Dependencies

## Python Libraries
- **Flask**: Core web framework
- **Flask-SQLAlchemy**: Database ORM and management
- **pandas**: Data processing for CSV/JSON file handling
- **Werkzeug**: WSGI utilities and middleware

## Frontend Libraries
- **Bootstrap 5.3.0**: CSS framework and UI components (CDN)
- **Bootstrap Icons**: Icon library (CDN)

## Database Systems
- **SQLite**: Development database (local file-based)
- **PostgreSQL**: Production database (via DATABASE_URL environment variable)

## Deployment Platform
- **Vercel**: Production hosting platform with Python runtime support
- **Environment Variables**: Session secrets and database configuration via Vercel environment management
- **Deployment Configuration**: Optimized vercel.json with 15MB lambda size and 30s timeout for file processing
- **Database Strategy**: Automatic PostgreSQL detection via DATABASE_URL environment variable

## File Storage
- **Local File System**: Temporary file processing during upload
- **Memory Processing**: In-memory file handling for CSV/JSON parsing without persistent storage