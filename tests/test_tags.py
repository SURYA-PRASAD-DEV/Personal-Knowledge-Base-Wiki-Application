"""Tests for tag cloud and tag filtering."""
import models


def test_tag_cloud(app, sample_article):
    """Tag cloud includes tags from sample article."""
    cloud = models.get_tag_cloud()
    tag_names = [t['tag'] for t in cloud]
    assert 'test' in tag_names
    assert 'sample' in tag_names


def test_filter_by_tag(client, sample_article):
    """GET /?tag=test filters articles to those with the 'test' tag."""
    resp = client.get('/?tag=test')
    assert resp.status_code == 200
    assert b'Test Article' in resp.data
