# Recipe API 🍳

A production-ready REST API for recipe management, built with Django REST Framework and Docker. Features secure authentication, dynamic filtering, image uploads, and OpenAPI documentation.

[![CI/CD](https://github.com/yourusername/recipe-api/actions/workflows/main.yml/badge.svg)](https://github.com/yourusername/recipe-api/actions)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)](https://docs.docker.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-API-red)](https://www.django-rest-framework.org/)

## Features ✨

- **Secure Authentication**: Token-based (Bearer) auth with custom user model.
- **Recipe Management**: CRUD operations with:
  - Dynamic filtering (tags, ingredients, assigned recipes).
  - Image uploads (UUID-based storage).
- **Auto-Documented API**: OpenAPI 3.0 via `drf-spectacular`.
- **DevOps Ready**:
  - Dockerized (Django + PostgreSQL + Nginx).
  - CI/CD pipelines (GitHub Actions).
  - TDD approach (unit/integration tests).

## Tech Stack 🛠️

- **Backend**: Django REST Framework
- **Database**: PostgreSQL
- **Infrastructure**: Docker, Docker Compose, Nginx (unprivileged)
- **Documentation**: drf-spectacular (OpenAPI 3.0)
- **Testing**: pytest, DRF test client

## Quick Start 🚀

### Prerequisites
- Docker & Docker Compose
- Python 3.9+

### Running Locally
```bash
# Clone the repo
git clone https://github.com/yourusername/recipe-api.git
cd recipe-api

# Start services (Django + PostgreSQL + Nginx)
docker-compose up -d

# Run migrations
docker-compose exec app python manage.py migrate

# Access API docs at:
http://localhost:8000/api/schema/swagger-ui/
