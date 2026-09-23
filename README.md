## AI Task Manager

A FastAPI backend implementing user registration, JWT authentication, password hashing, PostgreSQL persistence, and protected user APIs.

> Current scope: the repository currently provides the authentication/user-management foundation. Task CRUD and AI functionality are not implemented yet.

### Features
- User registration with email validation
- Duplicate-email protection
- SHA-256 + bcrypt password hashing
- OAuth2 password-form login
- JWT access-token generation and validation
- Protected `/users/me` endpoint
- PostgreSQL + SQLAlchemy ORM
- FastAPI dependency injection
- Swagger/OpenAPI documentation

### Tech Stack
| Technology | Purpose |
|---|---|
| Python 3.13+ | Backend language |
| FastAPI | REST API framework |
| PostgreSQL | Relational database |
| SQLAlchemy 2.x | ORM/database access |
| Pydantic 2.x | Request validation |
| python-jose | JWT |
| Passlib + bcrypt | Password hashing |
| Uvicorn | ASGI server |

### Architecture
```text
Client
  -> FastAPI Routes
      -> Auth Service / User API
          -> Security/Auth Dependencies
              -> SQLAlchemy
                  -> PostgreSQL
```

### Project Structure
```text
AI_TaskManager/
├── app/
│   ├── api/
│   │   ├── auth.py
│   │   └── user.py
│   ├── core/
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   └── security.py
│   ├── db/
│   │   ├── deps.py
│   │   └── session.py
│   ├── models/
│   │   └── user.py
│   ├── schemas/
│   │   └── user.py
│   ├── services/
│   │   └── auth_services.py
│   └── main.py
├── requirements.txt
├── PROJECT.md
└── test.py
```

### Getting Started

Prerequisites: Python 3.13+, PostgreSQL, Git.

```bash
git clone https://github.com/BhaktaGopal/AI_TaskManager.git
cd AI_TaskManager
python -m venv venv
```

Windows:
```bash
venv\\Scripts\\activate
```

Linux/macOS:
```bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Create PostgreSQL database `ai_task_manager`. The current `app/core/config.py` expects a local PostgreSQL connection on port `5433`; adjust configuration for your environment.

Run:
```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### API

`GET /`
```json
{"message":"Auth system running"}
```

`POST /auth/register`
```json
{"email":"user@example.com","password":"password123"}
```

`POST /auth/login` uses OAuth2 form fields:
```text
username=user@example.com
password=password123
```
Response:
```json
{"access_token":"<JWT_TOKEN>","token_type":"bearer"}
```

`GET /users/me`
```http
Authorization: Bearer <JWT_TOKEN>
```
Response:
```json
{"id":1,"email":"user@example.com","role":"user"}
```

### Authentication Flow
```text
Register -> validate -> duplicate check -> hash -> save
Login    -> authenticate -> verify password -> create JWT
Request  -> extract bearer token -> verify JWT -> load user -> endpoint
```

### Database Model
```text
users
├── id        INTEGER PRIMARY KEY
├── email     STRING UNIQUE + INDEXED
├── password  STRING
└── role      STRING DEFAULT 'user'
```

The app currently creates tables with `Base.metadata.create_all()`. For production, use Alembic migrations.

### Security Notes
- Passlib + bcrypt for password hashing
- JWT bearer authentication
- HS256 signing
- 60-minute token expiration

> Production note: the current source contains DB/JWT configuration values directly in `app/core/config.py`. Move secrets to environment variables or a secret manager before production use. Do not commit real credentials in `.env`.

### Testing
The repository does not yet contain a structured Pytest suite. `test.py` currently checks the Passlib bcrypt backend.

Recommended future testing: Pytest, FastAPI TestClient, authentication tests, and database integration tests.

### Roadmap
- Task CRUD
- Task ownership/relationships
- Task status, priority, due dates
- Role-based access control
- Refresh tokens and revocation
- Alembic migrations
- Centralized exception handling
- Structured logging
- Pytest
- Docker / Compose
- CI/CD
- AI-assisted task creation/prioritization

### Production Checklist
- [ ] Externalize secrets
- [ ] Remove credential-bearing `.env` files from Git
- [ ] Add Alembic
- [ ] Add automated tests
- [ ] Standardize API errors
- [ ] Add observability
- [ ] Add Docker/CI/CD
- [ ] Add health checks
- [ ] Add a license

## Author
**Bhakta Gopal**

GitHub: https://github.com/BhaktaGopal