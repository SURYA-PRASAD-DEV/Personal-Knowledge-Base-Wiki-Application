import re
from urllib.parse import quote_plus

LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

def parse_internal_links(content: str) -> str:
    """Replace occurrences of [[Article Title]] with links to the view route.

    For simplicity, links will use the title query param: /articles/view?title=Title
    This function does not validate existence of the target article.
    """
    def repl(m):
        title = m.group(1).strip()
        url = f"/articles/view?title={quote_plus(title)}"
        return f'<a class="internal-link" href="{url}">{title}</a>'

    return LINK_RE.sub(repl, content)
import re
from urllib.parse import quote_plus

LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

def parse_internal_links(content: str) -> str:
    """Replace occurrences of [[Article Title]] with links to the view route.

    For simplicity, links will use the title query param: /articles/view?title=Title
    This function does not validate existence of the target article.
    """
    def repl(m):
        title = m.group(1).strip()
        url = f"/articles/view?title={quote_plus(title)}"
        return f'<a class="internal-link" href="{url}">{title}</a>'

    return LINK_RE.sub(repl, content)
