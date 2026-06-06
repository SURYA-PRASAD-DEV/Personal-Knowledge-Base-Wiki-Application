"""
Simple Firestore data access layer for Articles and Versions.
This keeps logic separate from routes for clarity.
"""
from firebase_module import db
import logging
try:
    import bleach
except Exception:
    bleach = None
logger = logging.getLogger(__name__)
import json
from pathlib import Path
from datetime import datetime
import uuid

DATA_DIR = Path(__file__).parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
ART_FILE = DATA_DIR / 'articles.json'
VER_FILE = DATA_DIR / 'versions.json'

ART_COL = 'articles'
VER_COL = 'versions'

USE_FIRESTORE = db is not None
logger.info('USE_FIRESTORE=%s', USE_FIRESTORE)


def _load_json(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _save_json(path, data):
    path.write_text(json.dumps(data, default=str, indent=2), encoding='utf-8')


# In-memory / file fallback when Firestore isn't configured
if not USE_FIRESTORE:
    _ART_STORE = _load_json(ART_FILE)
    _VER_STORE = _load_json(VER_FILE)
else:
    _ART_STORE = {}
    _VER_STORE = {}


def init_models(app):
    """Re-initialize model stores using app config. Call after app is created."""
    global DATA_DIR, ART_FILE, VER_FILE, _ART_STORE, _VER_STORE, USE_FIRESTORE

    if app.config.get('USE_FIRESTORE') is False:
        USE_FIRESTORE = False

    DATA_DIR = Path(app.config.get('DATA_DIR', Path(__file__).parent / 'data'))
    DATA_DIR.mkdir(exist_ok=True)
    ART_FILE = DATA_DIR / 'articles.json'
    VER_FILE = DATA_DIR / 'versions.json'

    if not USE_FIRESTORE:
        _ART_STORE.clear()
        _ART_STORE.update(_load_json(ART_FILE))
        _VER_STORE.clear()
        _VER_STORE.update(_load_json(VER_FILE))


def _now():
    return datetime.utcnow()


def sanitize_html(content: str) -> str:
    """Sanitize HTML content using bleach."""
    if not content:
        return ''
    if bleach is None:
        logger.warning('bleach not installed; skipping HTML sanitization')
        return content
    allowed_tags = [
        'a', 'b', 'strong', 'i', 'em', 'u', 'p', 'br', 'ul', 'ol', 'li',
        'h1', 'h2', 'h3', 'h4', 'pre', 'code', 'blockquote',
    ]
    allowed_attrs = {
        'a': ['href', 'title', 'target', 'rel'],
    }
    cleaned = bleach.clean(content, tags=allowed_tags, attributes=allowed_attrs, strip=True)
    return cleaned


def create_article(title, content, tags, created_by='Anonymous'):
    doc_id = str(uuid.uuid4())
    safe_content = sanitize_html(content)
    data = {
        'title': title,
        'content': safe_content,
        'tags': tags,
        'created_by': created_by,
        'created_at': _now(),
        'updated_at': _now(),
    }
    if USE_FIRESTORE:
        db.collection(ART_COL).document(doc_id).set(data)
    else:
        _ART_STORE[doc_id] = data
        _save_json(ART_FILE, _ART_STORE)

    # Update search index
    try:
        from search import add_to_index
        add_to_index({'id': doc_id, **data})
    except Exception as e:
        logger.warning('Failed to add article %s to search index: %s', doc_id, e)

    return {'id': doc_id, **data}


def get_article(article_id):
    if USE_FIRESTORE:
        doc = db.collection(ART_COL).document(article_id).get()
        if not doc.exists:
            return None
        data = doc.to_dict()
        data['id'] = doc.id
        return data
    else:
        d = _ART_STORE.get(article_id)
        if not d:
            return None
        return {'id': article_id, **d}


def get_article_by_title(title):
    if USE_FIRESTORE:
        q = db.collection(ART_COL).where('title', '==', title).limit(1).get()
        for doc in q:
            d = doc.to_dict()
            d['id'] = doc.id
            return d
        return None
    else:
        for k, v in _ART_STORE.items():
            if v.get('title') == title:
                return {'id': k, **v}
        return None


def update_article(article_id, title, content, tags, edited_by='Anonymous'):
    # Save current to versions
    current = get_article(article_id)
    if current:
        add_version(article_id, current['content'], edited_by=edited_by)
    # Sanitize incoming HTML
    safe_content = sanitize_html(content)
    data = {
        'title': title,
        'content': safe_content,
        'tags': tags,
        'updated_by': edited_by,
        'updated_at': _now(),
    }
    if USE_FIRESTORE:
        db.collection(ART_COL).document(article_id).update(data)
    else:
        if article_id in _ART_STORE:
            _ART_STORE[article_id].update(data)
            _save_json(ART_FILE, _ART_STORE)

    # Update search index
    try:
        from search import add_to_index
        updated = get_article(article_id)
        if updated:
            add_to_index(updated)
    except Exception as e:
        logger.warning('Failed to update article %s in search index: %s', article_id, e)


def delete_article(article_id):
    if USE_FIRESTORE:
        vers = db.collection(VER_COL).where('article_id', '==', article_id).get()
        for v in vers:
            db.collection(VER_COL).document(v.id).delete()
        db.collection(ART_COL).document(article_id).delete()
    else:
        to_del = [k for k, v in _VER_STORE.items() if v.get('article_id') == article_id]
        for k in to_del:
            _VER_STORE.pop(k, None)
        if _VER_STORE:
            _save_json(VER_FILE, _VER_STORE)
        _ART_STORE.pop(article_id, None)
        _save_json(ART_FILE, _ART_STORE)

    # Remove from search index
    try:
        from search import remove_from_index
        remove_from_index(article_id)
    except Exception as e:
        logger.warning('Failed to remove article %s from search index: %s', article_id, e)


def list_articles(limit=100):
    if USE_FIRESTORE:
        docs = db.collection(ART_COL).order_by('updated_at', direction='DESCENDING').limit(limit).stream()
        out = []
        for d in docs:
            item = d.to_dict()
            item['id'] = d.id
            out.append(item)
        return out
    else:
        items = []
        for k, v in _ART_STORE.items():
            itm = dict(v)
            itm['id'] = k
            items.append(itm)
        items.sort(key=lambda x: str(x.get('updated_at', '')), reverse=True)
        return items[:limit]


def list_articles_by_tag(tag):
    if USE_FIRESTORE:
        docs = db.collection(ART_COL).where('tags', 'array_contains', tag).stream()
        out = []
        for d in docs:
            item = d.to_dict()
            item['id'] = d.id
            out.append(item)
        return out
    else:
        out = []
        for k, v in _ART_STORE.items():
            if tag in v.get('tags', []):
                item = dict(v)
                item['id'] = k
                out.append(item)
        return out


def search_articles(q):
    """Search articles using Whoosh full-text search, with fallback to substring matching."""
    # Try Whoosh first
    try:
        from search import search as whoosh_search
        results = whoosh_search(q)
        if results is not None:
            return results
    except Exception as e:
        logger.warning('Whoosh search failed, falling back to substring: %s', e)

    # Fallback: original substring search
    all_docs = list_articles(limit=500)
    qlow = q.lower()
    results = []
    for a in all_docs:
        if (qlow in a.get('title', '').lower() or
                qlow in a.get('content', '').lower() or
                any(qlow in t.lower() for t in a.get('tags', []))):
            results.append(a)
    return results


def add_version(article_id, content, edited_by='System'):
    safe_content = sanitize_html(content)
    if USE_FIRESTORE:
        vs = db.collection(VER_COL).where('article_id', '==', article_id).order_by('version_no', direction='DESCENDING').limit(1).get()
        if vs:
            last = vs[0].to_dict()
            next_no = last.get('version_no', 0) + 1
        else:
            next_no = 1
        vid = str(uuid.uuid4())
        data = {
            'article_id': article_id,
            'version_no': next_no,
            'content': safe_content,
            'edited_at': _now(),
            'edited_by': edited_by,
        }
        db.collection(VER_COL).document(vid).set(data)
        return {'id': vid, **data}
    else:
        last_no = 0
        for v in _VER_STORE.values():
            if v.get('article_id') == article_id:
                last_no = max(last_no, v.get('version_no', 0))
        next_no = last_no + 1
        vid = str(uuid.uuid4())
        data = {
            'article_id': article_id,
            'version_no': next_no,
            'content': safe_content,
            'edited_at': _now(),
            'edited_by': edited_by,
        }
        _VER_STORE[vid] = data
        _save_json(VER_FILE, _VER_STORE)
        return {'id': vid, **data}


def get_versions(article_id):
    if USE_FIRESTORE:
        docs = db.collection(VER_COL).where('article_id', '==', article_id).order_by('version_no', direction='DESCENDING').stream()
        out = []
        for d in docs:
            item = d.to_dict()
            item['id'] = d.id
            out.append(item)
        return out
    else:
        out = []
        for k, v in _VER_STORE.items():
            if v.get('article_id') == article_id:
                itm = dict(v)
                itm['id'] = k
                out.append(itm)
        out.sort(key=lambda x: x.get('version_no', 0), reverse=True)
        return out


def restore_version(article_id, version_id):
    if USE_FIRESTORE:
        vdoc = db.collection(VER_COL).document(version_id).get()
        if not vdoc.exists:
            return False
        v = vdoc.to_dict()
        current = get_article(article_id)
        if current:
            add_version(article_id, current['content'])
        db.collection(ART_COL).document(article_id).update({'content': v['content'], 'updated_at': _now()})
        return True
    else:
        v = _VER_STORE.get(version_id)
        if not v:
            return False
        current = get_article(article_id)
        if current:
            add_version(article_id, current['content'])
        if article_id in _ART_STORE:
            _ART_STORE[article_id]['content'] = v['content']
            _ART_STORE[article_id]['updated_at'] = _now()
            _save_json(ART_FILE, _ART_STORE)
            return True
        return False


def list_all_tags():
    tags = set()
    if USE_FIRESTORE:
        docs = db.collection(ART_COL).stream()
        for d in docs:
            for t in d.to_dict().get('tags', []):
                tags.add(t)
    else:
        for v in _ART_STORE.values():
            for t in v.get('tags', []):
                tags.add(t)
    return sorted(tags)


def get_tag_cloud():
    """Get all tags with usage counts, sorted by frequency."""
    tag_counts = {}
    if USE_FIRESTORE:
        docs = db.collection(ART_COL).stream()
        for d in docs:
            for t in d.to_dict().get('tags', []):
                tag_counts[t] = tag_counts.get(t, 0) + 1
    else:
        for v in _ART_STORE.values():
            for t in v.get('tags', []):
                tag_counts[t] = tag_counts.get(t, 0) + 1

    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2']
    tag_list = []
    for tag in sorted(tag_counts.keys()):
        color = colors[hash(tag) % len(colors)]
        tag_list.append({
            'tag': tag,
            'count': tag_counts[tag],
            'color': color,
            'size_class': _get_tag_size_class(tag_counts[tag], tag_counts),
        })
    return sorted(tag_list, key=lambda x: x['count'], reverse=True)


def _get_tag_size_class(count, all_counts):
    """Determine CSS size class based on usage frequency."""
    if not all_counts:
        return 'md'
    max_count = max(all_counts.values())
    min_count = min(all_counts.values())
    if max_count == min_count:
        return 'md'
    range_count = max_count - min_count
    normalized = (count - min_count) / range_count
    if normalized >= 0.75:
        return 'xl'
    elif normalized >= 0.5:
        return 'lg'
    elif normalized >= 0.25:
        return 'md'
    else:
        return 'sm'
