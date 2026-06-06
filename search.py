"""
Whoosh full-text search module.
Falls back to simple substring search if Whoosh is not available.
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from whoosh.index import create_in, open_dir, exists_in
    from whoosh.fields import Schema, TEXT, ID, KEYWORD
    from whoosh.qparser import MultifieldParser, OrGroup
    WHOOSH_AVAILABLE = True
except ImportError:
    WHOOSH_AVAILABLE = False
    logger.warning('Whoosh not installed; full-text search disabled, falling back to substring search')

_index = None
_index_dir = None


def get_schema():
    """Define the Whoosh schema for articles."""
    return Schema(
        id=ID(stored=True, unique=True),
        title=TEXT(stored=True),
        content=TEXT(stored=True),
        tags=KEYWORD(stored=True, commas=True, lowercase=True),
    )


def init_search(app):
    """Initialize or open the Whoosh index. Call after app creation."""
    global _index, _index_dir

    if not WHOOSH_AVAILABLE:
        return

    _index_dir = Path(app.config.get('SEARCH_INDEX_DIR',
                      Path(__file__).parent / 'data' / 'search_index'))
    _index_dir.mkdir(parents=True, exist_ok=True)

    index_dir_str = str(_index_dir)

    if exists_in(index_dir_str):
        _index = open_dir(index_dir_str)
        logger.info('Opened existing Whoosh index at %s', index_dir_str)
    else:
        _index = create_in(index_dir_str, get_schema())
        logger.info('Created new Whoosh index at %s', index_dir_str)


def rebuild_index(articles):
    """Rebuild the index from scratch with all articles."""
    if not WHOOSH_AVAILABLE or _index is None:
        return

    try:
        writer = _index.writer(timeout=10.0)
        for article in articles:
            writer.update_document(
                id=str(article['id']),
                title=article.get('title', ''),
                content=article.get('content', ''),
                tags=','.join(article.get('tags', [])),
            )
        writer.commit()
        logger.info('Rebuilt Whoosh index with %d articles', len(articles))
    except Exception as e:
        logger.warning('Failed to rebuild index: %s', e)


def add_to_index(article):
    """Add or update a single article in the index."""
    if not WHOOSH_AVAILABLE or _index is None:
        return

    try:
        writer = _index.writer(timeout=10.0)
        writer.update_document(
            id=str(article['id']),
            title=article.get('title', ''),
            content=article.get('content', ''),
            tags=','.join(article.get('tags', [])),
        )
        writer.commit()
    except Exception as e:
        logger.warning('Failed to add article %s to index: %s', article['id'], e)


def remove_from_index(article_id):
    """Remove an article from the index by ID."""
    if not WHOOSH_AVAILABLE or _index is None:
        return

    try:
        writer = _index.writer(timeout=10.0)
        writer.delete_by_term('id', str(article_id))
        writer.commit()
    except Exception as e:
        logger.warning('Failed to remove article %s from index: %s', article_id, e)


def search(query_string, limit=50):
    """Search the index. Returns list of dicts or None if unavailable."""
    if not WHOOSH_AVAILABLE or _index is None:
        return None

    if not query_string or not query_string.strip():
        return []

    results_list = []
    with _index.searcher() as searcher:
        parser = MultifieldParser(
            ['title', 'content', 'tags'],
            schema=_index.schema,
            group=OrGroup,
        )
        query = parser.parse(query_string)
        results = searcher.search(query, limit=limit)

        for hit in results:
            results_list.append({
                'id': hit['id'],
                'title': hit['title'],
                'content': hit['content'],
                'tags': [t.strip() for t in hit.get('tags', '').split(',') if t.strip()],
            })

    return results_list
