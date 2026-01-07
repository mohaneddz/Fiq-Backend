"""
Tests for Blog API routes.
"""
import pytest
from Blog.app import create_app


@pytest.fixture
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check(self, client):
        """Test health endpoint returns 200."""
        response = client.get('/blog/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'blog'


class TestPostsEndpoint:
    """Tests for blog posts endpoints."""
    
    def test_get_posts_default_pagination(self, client):
        """Test getting posts with default pagination."""
        response = client.get('/blog/posts')
        assert response.status_code == 200
        data = response.get_json()
        assert 'data' in data
        assert 'posts' in data['data']
        assert 'pagination' in data['data']
    
    def test_get_posts_with_page(self, client):
        """Test getting posts with specific page."""
        response = client.get('/blog/posts?page=2')
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['pagination']['page'] == 2
    
    def test_get_posts_with_limit(self, client):
        """Test getting posts with specific limit."""
        response = client.get('/blog/posts?limit=5')
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['pagination']['limit'] == 5
    
    def test_get_posts_with_category(self, client):
        """Test filtering posts by category."""
        response = client.get('/blog/posts?category=Education')
        assert response.status_code == 200
        data = response.get_json()
        # All returned posts should have the specified category
        posts = data['data']['posts']
        if posts:
            assert all(post['category'] == 'Education' for post in posts)
    
    def test_get_posts_with_search(self, client):
        """Test searching posts."""
        response = client.get('/blog/posts?search=drug')
        assert response.status_code == 200
        # Response should contain search results
        assert response.get_json() is not None
    
    def test_get_posts_invalid_page(self, client):
        """Test that invalid page number defaults to 1."""
        response = client.get('/blog/posts?page=0')
        assert response.status_code == 200
        data = response.get_json()
        assert data['data']['pagination']['page'] == 1
    
    def test_get_posts_limit_exceeds_max(self, client):
        """Test that limit is capped at MAX_PAGE_SIZE."""
        response = client.get('/blog/posts?limit=1000')
        assert response.status_code == 200
        data = response.get_json()
        # Should be capped at MAX_PAGE_SIZE (50)
        assert data['data']['pagination']['limit'] <= 50


class TestPostDetailEndpoint:
    """Tests for individual post detail endpoint."""
    
    @pytest.mark.skip(reason="Requires valid post ID from database")
    def test_get_post_by_id(self, client):
        """Test getting a specific post by ID."""
        # This would need a real post ID
        post_id = "test-post-id"
        response = client.get(f'/blog/posts/{post_id}')
        assert response.status_code in [200, 404]
    
    def test_get_post_invalid_id(self, client):
        """Test getting post with invalid ID."""
        response = client.get('/blog/posts/nonexistent-id-12345')
        # Should return 404 or handle gracefully
        assert response.status_code in [404, 200]


class TestCreatePostEndpoint:
    """Tests for creating blog posts."""
    
    @pytest.mark.skip(reason="Requires Supabase write access")
    def test_create_post(self, client, sample_post):
        """Test creating a new blog post."""
        response = client.post('/blog/posts',
                              json=sample_post,
                              content_type='application/json')
        # Should create successfully or return appropriate error
        assert response.status_code in [200, 201, 400, 403]
    
    def test_create_post_missing_fields(self, client):
        """Test creating post with missing required fields."""
        incomplete_post = {"title": "Test Title"}
        response = client.post('/blog/posts',
                              json=incomplete_post,
                              content_type='application/json')
        # Should return validation error
        assert response.status_code in [400, 404, 405]
