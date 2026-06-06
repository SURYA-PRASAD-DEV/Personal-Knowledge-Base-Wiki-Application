"""Tests for Whoosh full-text search integration."""
import models


def test_search_finds_article(app, sample_article):
    """Search by title keyword returns the article."""
    results = models.search_articles('Test')
    assert len(results) >= 1
    assert any(r['id'] == sample_article['id'] for r in results)


def test_search_by_content(app, sample_article):
    """Search by content keyword returns the article."""
    results = models.search_articles('keywords')
    assert len(results) >= 1


def test_search_no_results(app):
    """Search for non-matching term returns empty list."""
    results = models.search_articles('xyznonexistent')
    assert results == []
