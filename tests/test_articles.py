"""Tests for article CRUD operations."""


def test_index_page(client):
    """GET / returns 200 and shows dashboard."""
    resp = client.get('/')
    assert resp.status_code == 200


def test_create_article(logged_in_client):
    """POST /articles/new creates an article and redirects to view."""
    resp = logged_in_client.post('/articles/new', data={
        'title': 'My New Article',
        'content': '<p>Content here</p>',
        'tags': 'python, flask',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Article created' in resp.data
    assert b'My New Article' in resp.data


def test_create_article_missing_title(logged_in_client):
    """POST /articles/new without title shows error."""
    resp = logged_in_client.post('/articles/new', data={
        'title': '',
        'content': 'some content',
        'tags': '',
    }, follow_redirects=True)
    assert b'Title is required' in resp.data


def test_view_article(client, sample_article):
    """GET /articles/view?article_id=<id> shows article content."""
    resp = client.get(f'/articles/view?article_id={sample_article["id"]}')
    assert resp.status_code == 200
    assert b'Test Article' in resp.data


def test_edit_article(logged_in_client, sample_article):
    """POST /articles/edit/<id> updates the article."""
    aid = sample_article['id']
    resp = logged_in_client.post(f'/articles/edit/{aid}', data={
        'title': 'Updated Title',
        'content': '<p>Updated content</p>',
        'tags': 'updated',
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Article updated' in resp.data


def test_delete_article(logged_in_client, sample_article):
    """POST /articles/delete/<id> removes the article."""
    aid = sample_article['id']
    resp = logged_in_client.post(f'/articles/delete/{aid}', follow_redirects=True)
    assert resp.status_code == 200
    assert b'Article deleted' in resp.data


def test_view_nonexistent_article(client):
    """Viewing a non-existent article returns 404."""
    resp = client.get('/articles/view?article_id=nonexistent-uuid')
    assert resp.status_code == 404
