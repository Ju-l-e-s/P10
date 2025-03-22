# SoftDesk Support API

This project is a **Django REST Framework** application for managing software projects, issues, and comments. It offers the following features:

- **User Management**: Create and manage user accounts (with RGPD compliance such as `age >= 15`).
- **Project Management**: Create and manage software projects.
- **Contributor Management**: Add and list contributors for each project.
- **Issue Management**: Create and manage issues (tasks/bugs) within a project.
- **Comment Management**: Post comments on issues to facilitate communication.
- **Permissions**: Only project contributors can access a project’s issues/comments, and only the resource author can update/delete them.

---

## Prerequisites

- **Python 3.9 or higher** installed on your machine.
- **Poetry** for dependency management.
- (Optional) A virtual environment tool (such as `venv`).

---

## Installation

1. **Clone the project repository**:
    ```bash
    git clone <REPOSITORY_URL>
    cd <REPOSITORY_FOLDER>
    ```

2. **Create and activate a virtual environment** (optional but recommended):

   **On Linux/macOS**:
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

   **On Windows**:
   ```bash
   python -m venv env
   env\Scripts\activate
   ```

3. **Install the dependencies with Poetry**:
   ```bash
   poetry install
   ```

4. **Run migrations to set up the database (SQLite by default)**:
   ```bash
   poetry run python manage.py migrate
   ```

5. **Create a superuser (optional, for Django admin)**:
   ```bash
   poetry run python manage.py createsuperuser
   ```

---

## Usage

Start the development server:
```bash
poetry run python manage.py runserver
```

The API will be accessible at [http://127.0.0.1:8000/](http://127.0.0.1:8000/) by default.

### Authentication:
- Obtain a JWT token via the `/api/token/` endpoint (if you implemented JWT).
- Include the token in the `Authorization: Bearer <token>` header for subsequent requests.

### Endpoints :
- `POST /api/projects/` : Create a project.
- `GET /api/projects/` : List all projects (paginated).
- `GET /api/projects/{id}/` : Retrieve a specific project if you are a contributor or author.
- `POST /api/issues/` : Create an issue within a project (must specify project field).
- `GET /api/issues/` : List issues of contributed projects.
- `POST /api/comments/` : Post a comment on an issue.
#### User Endpoints
- `POST /api/users/` : Create a new user.
- `GET /api/users/` : Retrieve your user details.
- `PATCH /api/users/{id}/` : Update user data.
- `DELETE /api/users/{id}/` : Delete a user.

#### Project Endpoints
- `POST /api/projects/` : Create a project.
- `GET /api/projects/` : List all projects (paginated).
- `GET /api/projects/{id}/` : Retrieve a specific project if you are a contributor or author.
- `PUT /api/projects/{id}/` : Update a project (only the author).
- `DELETE /api/projects/{id}/` : Delete a project (only the author).

#### Contributor Endpoints
- `POST /api/projects/{id}/contributors/` : Add a contributor.
- `GET /api/projects/{id}/contributors/` : List project contributors.
- `DELETE /api/projects/{id}/contributors/{user_id}/` : Remove a contributor.

#### Issue Endpoints
- `POST /api/projects/{id}/issues/` : Create an issue within a project (must specify project field).
- `GET /api/projects/{id}/issues/` : List issues of contributed projects.
- `PUT /api/issues/{id}/` : Update an issue (only the author).
- `DELETE /api/issues/{id}/` : Delete an issue (only the author).

#### Comment Endpoints
- `POST /api/issues/{id}/comments/` : Post a comment on an issue.
- `GET /api/issues/{id}/comments/` : List comments for an issue.
- `PUT /api/comments/{id}/` : Update a comment (only the author).
- `DELETE /api/comments/{id}/` : Delete a comment (only the author).

---
## Caching Mechanism

To improve performance and reduce unnecessary database queries, SoftDesk API implements caching using Django’s LocMemCache.

### Cache Configuration:

The caching system is configured in config/settings.py as follows:

```bash
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}
```
### How It Works:
SoftDesk API uses caching to improve response times for list endpoints.  
- Implemented via the `CacheListMixin`, which caches list responses using an explicit cache key.  
- Cached data is stored for `CACHE_TIMEOUT` seconds (configured in `settings.py`).  
- Automatically retrieves cached data if available, reducing database queries.

---
## General Instructions

- **Menu navigation**: Not applicable here; this is a REST API. Use tools like Postman or cURL.
- **Entering data**: Send JSON in your request body when creating/updating resources.
- **Authentication**: Provide the JWT token in your headers for secured endpoints.

---

## Project Structure

```
softdesk/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── logs/
│   ├── django.log
├── support/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── factories.py
│   ├── mixins.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   ├── tests/
├── db.sqlite3
├── manage.py
├── poetry.lock
├── pyproject.toml
├── pytest.ini
├── README.md

```

- `config/` : Django project configuration.
- `support/` : Main app containing models, views, serializers, permissions, and tests.
- `manage.py` : Django’s command-line utility file.
- `pyproject.toml / poetry.lock` : Poetry configuration for dependencies.
- `requirements.txt` : Alternative listing of required Python packages (if using pip).

---

## Run Tests

```bash
poetry run pytest
```

All functional and unit tests are located in `support/tests/`.

- `test_models.py` : Model tests.
- `test_views.py`, `test_comments.py`, etc. : Endpoint tests with DRF’s APIClient.

When all tests are green, you’re good to go!

---

## Contributing

1. Fork the repository.
2. Create a new branch: `git checkout -b my-feature`.
3. Commit your changes: `git commit -am 'Add new feature'`.
4. Push to your branch: `git push origin my-feature`.
5. Create a Pull Request.

Feel free to submit issues or suggestions for improvement.

---

## License

You can choose an appropriate license for your project (MIT, Apache 2.0, etc.). Include a `LICENSE` file for details.

---