# Recipe API 🍳

A production-ready Django REST Framework API for recipe management with secure authentication, advanced filtering, and comprehensive documentation.

[![CI/CD](https://github.com/RamiAdell/recipe-app-api/actions/workflows/main.yml/badge.svg)](https://github.com/RamiAdell/recipe-app-api/actions)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)]
(https://docs.docker.com/)
[![OpenAPI](https://img.shields.io/badge/OpenAPI-3.0-brightgreen?logo=openapi-initiative)](https://swagger.io/specification/)

## Features ✨

- **Secure Authentication**: Token-based (Bearer) auth with custom user model
- **Advanced Recipe Management**:
  - Full CRUD operations with image uploads
  - Dynamic filtering by tags/ingredients (`/api/recipe/recipes/?tags=1,2&ingredients=3`)
  - Bulk operations for tags/ingredients
- **Comprehensive Documentation**: Auto-generated OpenAPI 3.0 docs with `drf-spectacular`
- **Robust Testing**: 100% test coverage with Django TestCase

## API Endpoints 📍

| Endpoint                          | Method | Description                          | Auth Required |
|-----------------------------------|--------|--------------------------------------|---------------|
| `/api/recipe/recipes/`            | GET    | List recipes (filterable)            | Yes           |
| `/api/recipe/recipes/{id}/`       | PUT    | Update full recipe                   | Yes           |
| `/api/recipe/recipes/upload_image/`| POST   | Upload recipe image                  | Yes           |
| `/api/user/token/`                | POST   | Obtain auth token                   | No            |
| `/api/schema/`                    | GET    | OpenAPI schema (YAML/JSON)          | No            |

*[View full API documentation](http://localhost:8000/api/schema/swagger-ui/)*

## Tech Stack 🛠️

**Backend**  
▸ Django REST Framework 3.14  
▸ PostgreSQL (with query optimization)  
▸ Token Authentication  

**Infrastructure**  
▸ Docker + Docker Compose (multi-container)  
▸ Nginx (unprivileged Alpine)  
▸ CI/CD via GitHub Actions  

**Documentation**  
▸ OpenAPI 3.0 (drf-spectacular)  
▸ Interactive Swagger UI  

## Quick Start 🚀

```bash
# Clone and run with Docker
git clone https://github.com/RamiAdell/recipe-app-api.git
cd recipe-app-api
docker-compose up -d

# Apply migrations
docker-compose exec app python manage.py migrate

# Access endpoints:
curl -X GET http://localhost:8000/api/recipe/recipes/ \
  -H "Authorization: Token YOUR_TOKEN"
```
### Project Structure 📂
Copy
recipe-app-api/
├── app/
│   ├── core/               # Custom auth models
│   ├── recipe/             # Recipe logic
│   │   ├── tests/          # 50+ test cases
│   │   ├── views.py        # ViewSets with OpenAPI params
│   │   └── serializers.py  # Nested serializers
├── docker/                 # Nginx configs
├── .github/workflows/      # CI/CD pipelines
└── docker-compose.yml      # 3-service setup


### Testing Approach ✔️
## Test Coverage: 100% for critical paths
## Test Types:

Model validation (Recipe, Tag, Ingredient)
API endpoints (CRUD + filtering)
Authentication flows
Image upload validation
