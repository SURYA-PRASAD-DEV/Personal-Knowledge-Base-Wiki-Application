import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import config_by_name
import models
from utils.parser import parse_internal_links
from utils.diff import generate_html_diff
from auth import init_auth, get_user_by_id, get_user_by_username, create_user
from search import init_search, rebuild_index


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.secret_key = app.config['SECRET_KEY']

    # Logging
    logging.basicConfig(
        level=app.config.get('LOG_LEVEL', logging.INFO),
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    )
    logger = logging.getLogger(__name__)
    logger.info('Starting PKB Flask app [config=%s]', config_name)

    if not app.config.get('TESTING') and app.config['SECRET_KEY'] == 'dev-secret-key':
     logger.warning('SECRET_KEY is set to the default dev value. Set a proper SECRET_KEY for production.')

    # Initialize models
    models.init_models(app)

    #.;;;''''bvbbbbbbbb///////////////////////////............................../ mm
    # 
    # .......ze auth
    init_auth(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return get_user_by_id(user_id)

    # Custom Jinja2 filters
    def format_date(fmt, value):
        """Format a datetime value using strftime. Usage: {{ "%Y-%m-%d"|format_date(dt) }}"""
        if hasattr(value, 'strftime'):
            return value.strftime(fmt)
        return str(value)

    app.jinja_env.filters['format_date'] = format_date

    # Initialize search
    init_search(app)
    try:
        all_articles = models.list_articles(limit=10000)
        rebuild_index(all_articles)
    except Exception as e:
        logger.warning('Failed to rebuild search index on startup: %s', e)

    # ── Auth Routes ──────────────────────────────────────────────

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            confirm = request.form.get('confirm_password', '').strip()

            if not username or not email or not password:
                flash('All fields are required', 'danger')
                return render_template('register.html')
            if password != confirm:
                flash('Passwords do not match', 'danger')
                return render_template('register.html')
            if len(password) < 6:
                flash('Password must be at least 6 characters', 'danger')
                return render_template('register.html')

            user = create_user(username, email, password)
            if not user:
                flash('Username or email already taken', 'danger')
                return render_template('register.html')

            login_user(user)
            flash('Registration successful!', 'success')
            return redirect(url_for('index'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()

            user = get_user_by_username(username)
            if user and user.check_password(password):
                login_user(user)
                flash('Logged in successfully', 'success')
                next_page = request.args.get('next')
                return redirect(next_page or url_for('index'))

            flash('Invalid username or password', 'danger')
            return render_template('login.html')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged out', 'success')
        return redirect(url_for('login'))

    # ── Article Routes ───────────────────────────────────────────

    @app.route('/')
    def index():
        q = request.args.get('q', '')
        tag = request.args.get('tag')
        if q:
            articles = models.search_articles(q)
        elif tag:
            articles = models.list_articles_by_tag(tag)
        else:
            articles = models.list_articles()
        tag_cloud = models.get_tag_cloud()
        return render_template('index.html', articles=articles, tag_cloud=tag_cloud, q=q, selected_tag=tag)

    @app.route('/articles/new', methods=['GET', 'POST'])
    @login_required
    def create_article():
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            tags = [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()]
            if not title:
                flash('Title is required', 'danger')
                tag_cloud = models.get_tag_cloud()
                return render_template('article_form.html', article={}, action='Create', tag_cloud=tag_cloud)
            article = models.create_article(title, content, tags,
                                            created_by=current_user.username if current_user.is_authenticated else 'Anonymous')
            flash('Article created', 'success')
            return redirect(url_for('view_article') + f"?article_id={article['id']}")
        tag_cloud = models.get_tag_cloud()
        return render_template('article_form.html', article={}, action='Create', tag_cloud=tag_cloud)

    @app.route('/articles/edit/<article_id>', methods=['GET', 'POST'])
    @login_required
    def edit_article(article_id):
        article = models.get_article(article_id)
        if not article:
            return render_template('404.html'), 404
        if request.method == 'POST':
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            tags = [t.strip() for t in request.form.get('tags', '').split(',') if t.strip()]
            if not title:
                flash('Title is required', 'danger')
                tag_cloud = models.get_tag_cloud()
                return render_template('article_form.html', article=article, action='Edit', tag_cloud=tag_cloud)
            models.update_article(article_id, title, content, tags,
                                  edited_by=current_user.username if current_user.is_authenticated else 'Anonymous')
            flash('Article updated', 'success')
            return redirect(url_for('view_article') + f"?article_id={article_id}")
        tag_cloud = models.get_tag_cloud()
        return render_template('article_form.html', article=article, action='Edit', tag_cloud=tag_cloud)

    @app.route('/articles/delete/<article_id>', methods=['POST'])
    @login_required
    def delete_article(article_id):
        models.delete_article(article_id)
        flash('Article deleted', 'success')
        return redirect(url_for('index'))

    @app.route('/articles/view')
    def view_article():
        article_id = request.args.get('article_id')
        title = request.args.get('title')
        article = None
        if article_id:
            article = models.get_article(article_id)
        elif title:
            article = models.get_article_by_title(title)
        if not article:
            return render_template('404.html'), 404
        rendered = parse_internal_links(article['content'])
        versions = models.get_versions(article['id'])
        return render_template('article_view.html', article=article, rendered_content=rendered, versions=versions)

    @app.route('/articles/<article_id>/versions')
    def versions(article_id):
        article = models.get_article(article_id)
        if not article:
            return render_template('404.html'), 404
        vers = models.get_versions(article_id)
        return render_template('versions.html', article=article, versions=vers)

    @app.route('/articles/<article_id>/restore/<version_id>', methods=['POST'])
    @login_required
    def restore_version(article_id, version_id):
        models.restore_version(article_id, version_id)
        flash('Version restored', 'success')
        return redirect(url_for('view_article') + f"?article_id={article_id}")

    @app.route('/articles/<article_id>/compare')
    def compare_versions(article_id):
        article = models.get_article(article_id)
        if not article:
            return render_template('404.html'), 404

        v1_id = request.args.get('v1')
        v2_id = request.args.get('v2')
        vers = models.get_versions(article_id)
        v1 = None
        v2 = None

        if v1_id:
            v1 = next((v for v in vers if v['id'] == v1_id), None)
        if v2_id:
            v2 = next((v for v in vers if v['id'] == v2_id), None)

        if not v1 or not v2:
            flash('Invalid versions selected', 'warning')
            return redirect(url_for('versions', article_id=article_id))

        diff_html = generate_html_diff(v1.get('content', ''), v2.get('content', ''))
        return render_template('compare_versions.html', article=article, v1=v1, v2=v2, diff_html=diff_html, all_versions=vers)

    # ── API Endpoints ────────────────────────────────────────────

    @app.route('/api/articles/autocomplete')
    def articles_autocomplete():
        q = request.args.get('q', '').lower()
        limit = request.args.get('limit', 10, type=int)
        all_articles = models.list_articles(limit=100)
        matches = [a['title'] for a in all_articles if q in a['title'].lower()][:limit]
        return {'suggestions': matches}

    @app.route('/api/links/validate', methods=['POST'])
    def validate_links():
        import re
        content = request.json.get('content', '')
        links = re.findall(r'\[\[([^\[\]]+)\]\]', content)
        missing = []
        valid = []
        for link_title in links:
            article = models.get_article_by_title(link_title.strip())
            if article:
                valid.append(link_title)
            else:
                if link_title not in missing:
                    missing.append(link_title)
        return {
            'valid': valid,
            'missing': missing,
            'total': len(links),
            'has_missing': len(missing) > 0,
        }

    @app.route('/api/articles/exists')
    def article_exists():
        title = request.args.get('title', '').strip()
        if not title:
            return {'exists': False}
        article = models.get_article_by_title(title)
        return {'exists': article is not None, 'title': title}

    @app.route('/api/tags/suggestions')
    def tag_suggestions():
        q = request.args.get('q', '').strip().lower()
        limit = request.args.get('limit', 10, type=int)
        tag_cloud = models.get_tag_cloud()
        suggestions = []
        for tag_info in tag_cloud:
            tag = tag_info['tag']
            if q in tag.lower():
                suggestions.append({
                    'tag': tag,
                    'count': tag_info['count'],
                    'color': tag_info['color'],
                })
                if len(suggestions) >= limit:
                    break
        return {'suggestions': suggestions}

    # ── Error Handlers ───────────────────────────────────────────

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    return app


# Module-level app for Gunicorn (`gunicorn app:app`)
app = create_app()


if __name__ == '__main__':
    app.run(
        host=os.environ.get('FLASK_HOST', '127.0.0.1'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        debug=app.config.get('DEBUG', False),
    )
