# API Route Documentation

This document lists the public routes for the PKB app.

- `GET /` — Dashboard: lists articles, optional `q` (search) or `tag` query.
- `GET /articles/new` — Form to create an article
- `POST /articles/new` — Create article (form fields: `title`, `content`, `tags`)
- `GET /articles/edit/<article_id>` — Form to edit an article
- `POST /articles/edit/<article_id>` — Update article
- `POST /articles/delete/<article_id>` — Delete article
- `GET /articles/view?article_id=<id>` or `GET /articles/view?title=<title>` — View article
- `GET /articles/<article_id>/versions` — List versions for an article
- `POST /articles/<article_id>/restore/<version_id>` — Restore a version

Notes:
- All POST routes are simple and assume the client sends form-encoded data.
