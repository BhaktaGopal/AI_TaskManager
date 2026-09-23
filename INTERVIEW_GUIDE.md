# AI Task Manager — Interview Revision Guide

Project-specific revision guide for a 2–3 year Python/FastAPI backend interview.

## 1. 30-Second Explanation
> AI Task Manager is a FastAPI backend foundation for a task-management application. The current implementation focuses on authentication and user management using PostgreSQL, SQLAlchemy, Pydantic, Passlib/bcrypt, OAuth2 password-form login, and JWT bearer tokens. The code is separated into API, service, core, database, model, and schema layers.

**Important:** task CRUD and AI functionality are not implemented in the current repository.

## 2. Architecture
```text
Client
  -> FastAPI Routes
      -> Auth Service / User API
          -> Security/Auth Dependencies
              -> SQLAlchemy
                  -> PostgreSQL
```

## 3. Registration Flow
```text
POST /auth/register
 -> Pydantic validates UserCreate
 -> get_db() provides Session
 -> query by email
 -> duplicate? HTTP 400
 -> hash password
 -> create User
 -> db.add()
 -> db.commit()
 -> db.refresh()
 -> return user
```

**Q: Why Pydantic?**

It validates and parses request data. `EmailStr` validates the email field, and the schema also contributes to OpenAPI documentation.

## 4. Login Flow
```text
POST /auth/login
 -> OAuth2PasswordRequestForm
 -> authenticate_user()
 -> query by email
 -> verify_password()
 -> create_access_token()
 -> return JWT
```

The OAuth2 form field is `username`, but the project treats it as email.

## 5. Protected Endpoint Flow
```text
GET /users/me
 -> Depends(get_current_user)
 -> OAuth2PasswordBearer
 -> extract bearer token
 -> verify_token()
 -> jwt.decode()
 -> read sub
 -> query User by email
 -> return User
```

## 6. JWT
JWT structure:
```text
header.payload.signature
```
Current claims:
```json
{"sub":"user@example.com","exp":"<expiration>"}
```
- `sub`: authenticated subject; this project stores the email.
- `exp`: expiration time.
- Current expiration: 60 minutes.
- JWT is signed, not inherently encrypted.

**Q: What if someone tampers with the payload?**

The signature no longer matches; server-side decoding should reject the token.

**Q: How would you implement logout?**

Use short-lived access tokens plus refresh tokens and revoke the refresh token; use a denylist only where strong immediate revocation is required.

## 7. Password Security
Current flow:
```text
password -> SHA-256 -> bcrypt -> stored hash
```
Passwords are not stored in plaintext. bcrypt is designed for password hashing and is intentionally expensive.

**Do not call this encryption.** Say password hashing.

## 8. FastAPI Dependency Injection
Examples:
```python
db: Session = Depends(get_db)
current_user: User = Depends(get_current_user)
```

Dependency injection centralizes reusable concerns such as DB sessions and authentication and improves testability.

**Q: Why `yield` in `get_db()`?**

It lets FastAPI supply a request-scoped dependency and perform cleanup after the endpoint finishes.

## 9. Database Session Lifecycle
```text
request -> get_db() -> SessionLocal() -> yield db -> endpoint -> finally: db.close()
```
The `finally` block ensures cleanup even when an exception occurs.

## 10. SQLAlchemy
Know:
- Engine
- Session
- Declarative Base
- ORM model
- Transactions
- Commit
- Refresh
- Connection pooling

**Engine vs Session:**
> The engine manages connectivity and pooling; the session represents the unit of work used to query and modify records.

**add / commit / refresh:**
- `add()`: attaches an object to the session.
- `commit()`: persists the transaction.
- `refresh()`: reloads the object, including DB-generated values.

## 11. Model vs Schema
**SQLAlchemy model:** database representation.

**Pydantic schema:** API contract and validation.

Keep them separate because persistence and API concerns evolve independently.

## 12. OAuth2
The project uses `OAuth2PasswordBearer(tokenUrl="auth/login")` and `OAuth2PasswordRequestForm`.

**Q: Is OAuth2 the same as JWT?**
No. OAuth2 is an authorization framework; JWT is a token format. This project uses JWT in an OAuth2-compatible bearer-token flow.

## 13. APIRouter
Routes are split into `auth.py` and `user.py`, keeping endpoint groups modular.

## 14. 401 vs 403
**401 Unauthorized:** authentication is missing or invalid.

**403 Forbidden:** authentication succeeded, but the user lacks permission.

Example: valid JWT + role=user + admin-only route = 403.

## 15. Authentication vs Authorization
**Authentication:** Who are you?
```text
JWT -> email -> User
```
**Authorization:** What are you allowed to do?

The current role field is only a foundation; full RBAC is not implemented.

## 16. RBAC
Conceptual flow:
```text
JWT -> Current User -> Role -> Permission Dependency -> Endpoint
```
Possible dependency:
```python
def require_admin(current_user = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403)
    return current_user
```

## 17. User Model
```text
User
├── id
├── email
├── password
└── role
```
`email` is unique and indexed.

**Q: Is the application-level duplicate check enough?**
No. Concurrent requests can pass that check, so the database unique constraint is essential.

## 18. Configuration Issues
The current source defines the DB URL and JWT secret directly in `app/core/config.py`.

Production solution:
```env
DATABASE_URL=...
SECRET_KEY=...
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
Use environment variables or a secret manager.

The repo has `app/.env`, but the hard-coded values are what the application actually uses.

## 19. create_all vs Alembic
Current:
```python
Base.metadata.create_all(bind=engine)
```
This is convenient for a prototype but not a versioned migration system.

Production:
```text
model change -> Alembic migration -> review -> apply migration
```

## 20. Error Handling
The current current-user dependency raises a generic exception when a user cannot be found.

Production improvement: use explicit HTTP exceptions and a consistent API error format.

## 21. Service Layer
Current services include:
```text
create_user()
authenticate_user()
login_user()
```

The service layer keeps business logic out of route handlers. There is some duplication because the route already orchestrates authentication and JWT creation while `login_user()` contains similar logic. Refactor to one clear path.

## 22. Task CRUD Extension
Natural future model:
```text
Task
├── id
├── title
├── description
├── status
├── priority
├── due_date
├── created_at
├── updated_at
└── owner_id -> users.id
```
Authorize by checking `current_user.id == task.owner_id`.

## 23. Pagination
Example:
```text
GET /tasks?page=1&page_size=20
offset = (page - 1) * page_size
```
Cursor pagination can be preferable for very large datasets.

## 24. Scaling
```text
             Load Balancer
              /    |    \\
          API-1   API-2   API-3
              \\    |    /
               PostgreSQL
```
JWT can support horizontal API scaling because normal authentication does not require local server-side session state.

## 25. Redis
Possible cache-aside flow:
```text
Client -> FastAPI -> Redis
                  |-- HIT  -> return
                  |-- MISS -> PostgreSQL -> cache
```
Use caching when measurement shows it is needed; invalidation and consistency add complexity.

## 26. Testing Strategy
### Unit
- `hash_password`
- `verify_password`
- `create_access_token`
- `verify_token`

### API
- registration
- duplicate registration
- login
- invalid credentials
- authenticated endpoint
- missing token
- invalid token

### Integration
Use an isolated test database and test real DB interactions.

## 27. Priority Test Cases
1. Register valid user
2. Reject duplicate email
3. Successful login
4. Reject invalid password
5. Reject invalid JWT
6. Allow `/users/me` with valid JWT
7. Reject `/users/me` without JWT

## 28. Common FastAPI Questions
**Why FastAPI?** Type-hint-driven validation, dependency injection, automatic OpenAPI documentation, and async support.

**What is `Depends()`?** FastAPI dependency injection.

**What is `APIRouter`?** A way to modularize endpoint groups.

**What is `OAuth2PasswordBearer`?** A dependency for extracting bearer tokens from the Authorization header.

## 29. Common Python Questions
**Why functions in services?** Current operations are stateless; classes become useful if state or interchangeable strategies are required.

**Why `yield` in get_db()?** Request-scoped dependency setup and cleanup.

**What does finally do?** Ensures cleanup even if an exception occurs.

## 30. Common Database Questions
**Why unique email?** Database-level integrity.

**Why index email?** Login and current-user lookup query by email.

**What is a transaction?** A unit of work committed or rolled back as a whole.

## 31. Common Security Questions
**Can JWT payload be decoded without the secret?** Usually yes; encoding is not encryption.

**Can it be modified and remain valid?** Not without a valid signature.

**Where should the secret live?** Environment variables or secret management.

**Why bcrypt?** It is designed for password hashing and is computationally expensive.

## 32. Strong “What Would You Improve?” Answer
> “I would externalize secrets and database configuration, add Alembic migrations, build a Pytest suite, introduce explicit response schemas, standardize exception handling, implement refresh-token authentication, add authorization around the existing role field, and then containerize the service with CI/CD, observability, and health checks.”

## 33. Honest Project Limitations
1. Task CRUD is not implemented.
2. AI functionality is not implemented.
3. Full RBAC is not implemented.
4. The role field is not enforced.
5. Secrets are hard-coded.
6. The `.env` file is not the source of truth for those values.
7. No migration framework yet.
8. No structured Pytest suite yet.
9. Some authentication service logic is duplicated.
10. Generic exception handling can be improved.
11. Tables are created with `create_all()` during startup.

## 34. 60-Second Interview Answer
> “I built a FastAPI backend as the foundation for an AI task-management application. The current implementation focuses on authentication and user management. FastAPI handles routing and dependency injection, Pydantic handles validation, SQLAlchemy manages PostgreSQL persistence, and Passlib with bcrypt handles password hashing. Users register with an email and password, the password is hashed before storage, and successful login issues a JWT access token using the email as the subject. Protected endpoints use OAuth2PasswordBearer to extract the bearer token, validate the JWT, resolve the current user from PostgreSQL, and execute the endpoint. I separated routes, services, security utilities, database dependencies, models, and schemas so the project can later grow into task CRUD, RBAC, migrations, testing, and AI functionality.”

## 35. Interview Traps
- **Does JWT encrypt the password?** No. Password hashing is separate.
- **Does OAuth2 mean JWT?** No. OAuth2 is an authorization framework; JWT is a token format.
- **Does the role field mean RBAC exists?** No. Permission checks are still needed.
- **Is `create_all()` a migration system?** No. It does not provide versioned schema migrations.
- **Does `.env` control the DB URL?** Not currently; the app uses values defined in `config.py`.

## 36. Final Checklist
- [ ] FastAPI
- [ ] APIRouter
- [ ] Depends
- [ ] Pydantic
- [ ] OAuth2 password flow
- [ ] Bearer tokens
- [ ] JWT structure
- [ ] sub / exp
- [ ] HS256
- [ ] bcrypt
- [ ] SQLAlchemy Engine
- [ ] SQLAlchemy Session
- [ ] ORM
- [ ] Transactions
- [ ] commit / refresh
- [ ] PostgreSQL
- [ ] Indexes
- [ ] Unique constraints
- [ ] Dependency lifecycle
- [ ] Authentication vs authorization
- [ ] 401 vs 403
- [ ] RBAC
- [ ] Environment variables
- [ ] Alembic
- [ ] Unit vs integration testing
- [ ] Logout/revocation
- [ ] Horizontal scaling

### One-line summary
> **FastAPI routes → service layer → security/auth dependencies → SQLAlchemy → PostgreSQL, with JWT bearer authentication protecting user endpoints.**