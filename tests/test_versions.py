"""Tests for version history and restore functionality."""
import models


def test_version_created_on_edit(app, sample_article):
    """Editing an article creates a version snapshot."""
    aid = sample_article['id']
    models.update_article(aid, 'New Title', '<p>New content</p>', ['newtag'])
    versions = models.get_versions(aid)
    assert len(versions) >= 1


def test_restore_version(app, sample_article):
    """Restoring a version reverts article content."""
    aid = sample_article['id']

    # Edit to create a version
    models.update_article(aid, 'New Title', '<p>New content</p>', ['newtag'])

    versions = models.get_versions(aid)
    assert len(versions) >= 1

    # Restore the first version (which has the original content)
    models.restore_version(aid, versions[-1]['id'])

    restored = models.get_article(aid)
    assert 'test content' in restored['content'].lower()


def test_versions_page_loads(client, sample_article):
    """GET /articles/<id>/versions returns 200."""
    resp = client.get(f'/articles/{sample_article["id"]}/versions')
    assert resp.status_code == 200
