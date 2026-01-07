"""
API routes for Blog service.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from flask import Blueprint, request, jsonify, current_app
from time import time
from shared.schemas import APIResponse, generate_request_id
from shared.supabase_db import SupabaseManager
from Blog.config import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from typing import Dict, Any

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "blog",
        "timestamp": int(time())
    }), 200


@blog_bp.route('/posts', methods=['GET'])
def get_posts():
    """
    Get latest blog posts from Supabase.
    
    Query parameters:
        - page: Page number (default: 1)
        - limit: Posts per page (default: 10, max: 50)
        - category: Filter by category (optional)
        - search: Search in title and content (optional)
    
    Returns:
        JSON response with posts and pagination info
    """
    request_id = generate_request_id()
    start_time = time()
    
    try:
        # Parse query parameters
        page = max(1, int(request.args.get('page', 1)))
        limit = min(MAX_PAGE_SIZE, max(1, int(request.args.get('limit', DEFAULT_PAGE_SIZE))))
        category = request.args.get('category', '').strip()
        search = request.args.get('search', '').strip()
        
        # Initialize Supabase manager
        db = SupabaseManager(table_name='blog_posts')
        
        # Build filters
        filters = {}
        ilike_filters = {}
        
        if category:
            filters['category'] = category
        
        if search:
            # For search, we'll need to fetch and filter manually since Supabase REST doesn't support OR
            ilike_filters['title'] = f'%{search}%'
        
        # Calculate offset
        offset = (page - 1) * limit
        
        # Fetch posts with pagination
        posts = db.select(
            columns='*',
            filters=filters if filters else None,
            ilike_filters=ilike_filters if ilike_filters else None,
            order_by='created_at',
            order_desc=True,
            limit=limit
        )
        
        # Get total count (simplified - actual implementation might need a separate count query)
        total_posts = len(posts)
        
        # Prepare response
        response_data = {
            'posts': posts,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_posts,
                'has_more': len(posts) == limit
            }
        }
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint='/posts',
            status='success',
            status_code=200,
            latency_ms=latency_ms
        )
        
        return jsonify(APIResponse.success(
            data=response_data,
            request_id=request_id
        ).to_dict()), 200
        
    except ValueError as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint='/posts',
            status='error',
            status_code=400,
            latency_ms=latency_ms,
            error=str(e),
            error_type='ValueError'
        )
        return jsonify(APIResponse.error(
            error_message=f"Invalid parameters: {str(e)}",
            request_id=request_id
        ).to_dict()), 400
        
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint='/posts',
            status='error',
            status_code=500,
            latency_ms=latency_ms,
            error=str(e),
            error_type=type(e).__name__
        )
        return jsonify(APIResponse.error(
            error_message="Failed to fetch blog posts",
            request_id=request_id
        ).to_dict()), 500


@blog_bp.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    """
    Get a specific blog post by ID.
    
    Args:
        post_id: ID of the post to retrieve
    
    Returns:
        JSON response with post details
    """
    request_id = generate_request_id()
    start_time = time()
    
    try:
        # Initialize Supabase manager
        db = SupabaseManager(table_name='blog_posts')
        
        # Fetch post by ID
        posts = db.select(
            columns='*',
            filters={'id': post_id}
        )
        
        if not posts or len(posts) == 0:
            return jsonify(APIResponse.error(
                error_message="Post not found",
                request_id=request_id
            ).to_dict()), 404
        
        post = posts[0]
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint=f'/posts/{post_id}',
            status='success',
            status_code=200,
            latency_ms=latency_ms
        )
        
        return jsonify(APIResponse.success(
            data={'post': post},
            request_id=request_id
        ).to_dict()), 200
        
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint=f'/posts/{post_id}',
            status='error',
            status_code=500,
            latency_ms=latency_ms,
            error=str(e),
            error_type=type(e).__name__
        )
        return jsonify(APIResponse.error(
            error_message="Failed to fetch blog post",
            request_id=request_id
        ).to_dict()), 500


@blog_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Get all available blog post categories.
    
    Returns:
        JSON response with list of categories
    """
    request_id = generate_request_id()
    start_time = time()
    
    try:
        # Initialize Supabase manager
        db = SupabaseManager(table_name='blog_posts')
        
        # Fetch all posts to get unique categories
        # Note: In production, this should be optimized with a proper distinct query
        posts = db.select(columns='category')
        
        # Get unique categories
        categories = list(set(post.get('category', '') for post in posts if post.get('category')))
        categories.sort()
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint='/categories',
            status='success',
            status_code=200,
            latency_ms=latency_ms
        )
        
        return jsonify(APIResponse.success(
            data={'categories': categories},
            request_id=request_id
        ).to_dict()), 200
        
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint='/categories',
            status='error',
            status_code=500,
            latency_ms=latency_ms,
            error=str(e),
            error_type=type(e).__name__
        )
        return jsonify(APIResponse.error(
            error_message="Failed to fetch categories",
            request_id=request_id
        ).to_dict()), 500
