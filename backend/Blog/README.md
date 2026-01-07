# Blog Service

The Blog service provides REST API endpoints for fetching and displaying blog posts about substance use recovery, harm reduction, and related topics.

## Features

- Fetch latest blog posts with pagination
- Filter posts by category
- Search posts by title and content
- Get individual post details
- List all available categories
- Full-text search support

## Setup

### Prerequisites

- Python 3.8+
- Supabase account with database access
- Environment variables configured (see below)

### Environment Variables

Required in `.env` file:
```
DB_URL=your_supabase_url
SERVICE_ROLE_KEY=your_service_role_key
DEBUG=false
```

### Database Schema

Run the SQL schema file to create the necessary tables:

```bash
# Execute blog_schema.sql in your Supabase SQL editor
```

This creates:
- `blog_posts` table with sample data
- Indexes for optimized queries
- Full-text search support
- Auto-updating timestamps

### Installation

```bash
cd backend/Blog
pip install -r requirements.txt
```

### Running the Service

```bash
python run.py
```

The service will start on port 5003 by default.

## API Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "service": "blog",
  "timestamp": 1704633600
}
```

### Get All Posts

```
GET /posts
```

Query parameters:
- `page` (optional): Page number (default: 1)
- `limit` (optional): Posts per page (default: 10, max: 50)
- `category` (optional): Filter by category
- `search` (optional): Search in title and content

Response:
```json
{
  "success": true,
  "data": {
    "posts": [
      {
        "id": "uuid",
        "title": "Post Title",
        "content": "Full content...",
        "excerpt": "Brief summary...",
        "author": "Author Name",
        "category": "Recovery",
        "tags": ["recovery", "support"],
        "image_url": null,
        "published": true,
        "created_at": "2024-01-07T12:00:00Z",
        "updated_at": "2024-01-07T12:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 5,
      "has_more": false
    }
  },
  "request_id": "req_xxx"
}
```

### Get Single Post

```
GET /posts/<post_id>
```

Response:
```json
{
  "success": true,
  "data": {
    "post": {
      "id": "uuid",
      "title": "Post Title",
      "content": "Full content...",
      ...
    }
  },
  "request_id": "req_xxx"
}
```

### Get Categories

```
GET /categories
```

Response:
```json
{
  "success": true,
  "data": {
    "categories": [
      "Recovery",
      "Education",
      "Support",
      "Harm Reduction",
      "Mental Health"
    ]
  },
  "request_id": "req_xxx"
}
```

## Testing

Run the test script to verify all endpoints:

```bash
# Make sure the service is running first
python test_blog.py
```

## Configuration

Edit `config.py` to customize:
- `SERVICE_PORT`: Port number (default: 5003)
- `DEFAULT_PAGE_SIZE`: Default posts per page (default: 10)
- `MAX_PAGE_SIZE`: Maximum posts per page (default: 50)
- `DEBUG`: Enable debug mode (default: false)

## Sample Categories

The default schema includes these categories:
- Recovery
- Education
- Support
- Harm Reduction
- Mental Health

## Architecture

The Blog service follows the same structure as other services in the project:

```
Blog/
├── __init__.py
├── app.py              # Flask app factory
├── config.py           # Configuration constants
├── run.py              # Entry point
├── requirements.txt    # Dependencies
├── blog_schema.sql     # Database schema
├── test_blog.py        # Test script
└── api/
    ├── __init__.py
    └── routes.py       # API route handlers
```

## Integration

The Blog service can be integrated with the frontend by making HTTP requests to the endpoints. It uses the shared `APIResponse` schema for consistency with other services.

## Notes

- All posts are stored in Supabase PostgreSQL database
- Posts support full-text search on title and content
- Timestamps are automatically managed with triggers
- CORS is enabled for cross-origin requests
- All responses follow the standard APIResponse format
