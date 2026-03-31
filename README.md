# Chapbook

A multi-author article publishing platform API — think Medium. Authors publish articles, follow each other, clap and rate posts, bookmark content, and comment.

Built with Django REST Framework, fully containerised with Docker.

---

## Features

- **Auth** — Email-based registration with JWT (cookie-based access + refresh tokens)
- **Articles** — Create, edit, delete articles with rich content, tags, banners, and auto-generated slugs
- **Engagement** — Claps, ratings (1–5), and threaded comments/responses
- **Social** — Follow/unfollow authors, view follower/following lists
- **Bookmarks** — Save articles for later
- **Search** — Full-text search via Elasticsearch (Bonsai.io in production)
- **Reading time** — Auto-calculated estimated reading time per article
- **Admin** — Customised Django admin at `/supersecret/`
- **API docs** — Interactive ReDoc documentation at `/redoc/`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.1.7 + Django REST Framework 3.14.0 |
| Database | PostgreSQL 15 |
| Cache / Broker | Redis 7 |
| Search | Elasticsearch 7.17.9 (local) / Bonsai.io (production) |
| Async tasks | Celery 5.2.7 |
| Task monitoring | Flower |
| Media storage | Cloudinary (production) |
| Static files | WhiteNoise (production) |
| Auth | dj-rest-auth + django-allauth + SimpleJWT |
| Containerisation | Docker + Docker Compose |
| Reverse proxy | Nginx (local) |

---

## Local Development

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [GNU Make](https://www.gnu.org/software/make/) (`scoop install make` on Windows)

### First run

```bash
cd src/
make build       # builds images and starts all services
make superuser   # create an admin user
```

### Subsequent sessions

```bash
make up          # start services
make down        # stop services
```

### Local URLs

| URL | Service |
|---|---|
| http://localhost:8080/api/v1/ | REST API |
| http://localhost:8080/redoc/ | API docs |
| http://localhost:8080/supersecret/ | Django admin |
| http://localhost:8025 | MailHog (captured emails) |
| http://localhost:5555 | Flower (Celery monitoring) |
| http://localhost:9200 | Elasticsearch |

### Useful commands

```bash
make migrate            # run migrations
make makemigrations     # create new migrations
make show-logs-api      # stream Django logs
make elastic-rebuild    # rebuild Elasticsearch index
make test-cov           # run tests with coverage
make black              # format code
make flake8             # lint
```

---

## API Endpoints

All endpoints under `/api/v1/`.

### Auth
| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/registration/` | Public | Register new user |
| POST | `/auth/login/` | Public | Login — sets JWT cookies |
| POST | `/auth/logout/` | Auth | Logout |
| GET/PUT | `/auth/user/` | Auth | Current user details |
| POST | `/auth/password/reset/` | Public | Request password reset |

### Profiles
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/profiles/` | Public | List all profiles |
| GET | `/profiles/me/` | Auth | Own profile |
| PATCH | `/profiles/update/` | Auth | Update profile |
| GET | `/profiles/{id}/followers/` | Auth | Follower list |
| POST | `/profiles/{id}/follow/` | Auth | Follow a user |
| POST | `/profiles/{id}/unfollow/` | Auth | Unfollow a user |

### Articles
| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/articles/` | Public | List articles |
| POST | `/articles/` | Auth | Create article |
| GET | `/articles/{slug}/` | Public | Article detail |
| PUT/PATCH | `/articles/{slug}/` | Auth (author) | Update article |
| DELETE | `/articles/{slug}/` | Auth (author) | Delete article |
| POST | `/articles/{slug}/clap/` | Auth | Clap on article |

### Other
| Method | Path | Auth | Description |
|---|---|---|---|
| GET/POST | `/ratings/` | Auth | Rate an article |
| GET/POST | `/bookmarks/` | Auth | Bookmark an article |
| GET/POST | `/responses/` | Auth | Comment on an article |
| GET | `/elastic/search/?search=query` | Public | Full-text search |

---

## Production Deployment (Railway)

### Prerequisites

- [Railway](https://railway.app) account
- [Bonsai.io](https://bonsai.io) account (free Elasticsearch)
- [Cloudinary](https://cloudinary.com) account (free media storage)

### Steps

1. Push `main` branch to GitHub
2. Create a new Railway project → **Deploy from GitHub repo** → select `chapbook`
3. Add **PostgreSQL** plugin — Railway auto-injects `DATABASE_URL`
4. Add **Redis** plugin — Railway auto-injects `REDIS_URL`
5. Set environment variables (see below)
6. Deploy

### Required Environment Variables

| Variable | Description |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `chapbook.settings.production` |
| `DJANGO_SECRET_KEY` | Random 50-char string |
| `ALLOWED_HOSTS` | `your-app.up.railway.app` |
| `CSRF_TRUSTED_ORIGINS` | `https://your-app.up.railway.app` |
| `SIGNING_KEY` | Random string for JWT signing |
| `DOMAIN` | `your-app.up.railway.app` |
| `DEFAULT_FROM_EMAIL` | Your email address |
| `CLOUDINARY_CLOUD_NAME` | From Cloudinary dashboard |
| `CLOUDINARY_API_KEY` | From Cloudinary dashboard |
| `CLOUDINARY_API_SECRET` | From Cloudinary dashboard |
| `ELASTICSEARCH_URL` | From Bonsai.io dashboard |
| `DATABASE_URL` | Auto-injected by Railway PostgreSQL |
| `REDIS_URL` | Auto-injected by Railway Redis |

Generate a secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Post-deploy checklist

```
[ ] GET  /redoc/                           → API docs load
[ ] POST /api/v1/auth/registration/        → user created
[ ] POST /api/v1/auth/login/               → JWT cookies returned
[ ] GET  /api/v1/articles/                 → 200 OK
[ ] POST /api/v1/articles/ (with banner)   → tests Cloudinary
[ ] GET  /api/v1/elastic/search/?search=x  → tests Bonsai
[ ] GET  /supersecret/                     → admin loads
```

---

## Environment Files (local only)

Local env files live in `src/.envs/.local/` and are gitignored. They are checked in for dev convenience but **never commit production credentials**.

---

## Project Structure

```
src/
├── chapbook/               # Django project module
│   └── settings/
│       ├── base.py         # Shared settings
│       ├── local.py        # Development settings
│       └── production.py   # Production settings
├── core_apps/
│   ├── users/              # Custom user model, registration
│   ├── profiles/           # User profiles, follow/unfollow
│   ├── articles/           # Article CRUD, claps, views
│   ├── ratings/            # Article ratings
│   ├── bookmarks/          # Bookmarks
│   ├── responses/          # Comments/responses
│   └── search/             # Elasticsearch integration
├── docker/local/           # Local Docker config
├── requirements/
│   ├── base.txt
│   ├── local.txt
│   └── production.txt
├── Dockerfile.prod         # Production Docker image
├── railway.toml            # Railway deployment config
├── local.yml               # Docker Compose (development)
└── Makefile                # Development shortcuts
```

---

## License

MIT
