
# Lichtblick – Social Media Prototype

**A Python-based social media prototype featuring a FastAPI backend, Streamlit frontend, JWT authentication, and cloud-based media storage.**

Lichtblick is a social media application prototype developed to explore full-stack development with Python.

The project combines a REST API built with FastAPI, a Streamlit user interface, asynchronous database operations with SQLAlchemy, and ImageKit integration for media uploads.

Users can register, sign in, publish image or video posts, browse a shared feed, interact through comments, and delete their own posts.

The focus of this project is on connecting authentication, persistent data storage, external services, and a frontend into a working application architecture.

## Key Features

### User Authentication
- User registration and login
- JWT-based authentication using `fastapi-users`
- Protected API endpoints
- User account management
- Authentication-based access to application features

### Posts and Media
- Image and video uploads through ImageKit
- Optional captions for uploaded media
- Persistent post storage with SQLite
- Chronological feed displaying recent posts
- Post deletion restricted to the respective owner

### Social Interactions
- Comments associated with individual posts
- Display of comments and their authors
- Like and dislike controls in the frontend
- Local UI fallback for reactions without backend persistence

### User Interface
- Interactive frontend built with Streamlit
- Login and registration views
- Shared post feed
- Media upload interface
- Light and dark mode

## Tech Stack

| Category | Technologies |
|----------|--------------|
| Language | Python |
| Backend | FastAPI, Uvicorn |
| Frontend | Streamlit |
| Authentication | fastapi-users, JWT |
| Database | SQLite |
| ORM | SQLAlchemy (Async) |
| Database Driver | aiosqlite |
| Media Storage | ImageKit |
| Data Validation | Pydantic |
| Environment Configuration | python-dotenv |
| Dependency Management | uv |

## Architecture

Lichtblick follows a frontend-backend architecture.

```text
                 Streamlit Frontend
                         |
                         |
                HTTP / REST API
                  JWT Bearer Token
                         |
                         v
                  FastAPI Backend
                         |
             +-----------+-----------+
             |                       |
             v                       v
       SQLAlchemy Async          ImageKit SDK
             |                       |
             v                       v
        SQLite Database       Cloud Media Storage
             |
       +-----+------+
       |     |      |
      Users Posts Comments
```

### Architecture Overview

**Frontend**

The Streamlit application provides the user interface for authentication, publishing posts, browsing the feed, and interacting with comments.

**Backend**

FastAPI handles HTTP requests, authentication, media uploads, post management, and database interactions.

**Authentication**

The application uses `fastapi-users` with JWT Bearer tokens. Protected endpoints require an authenticated, active user.

**Database**

SQLAlchemy provides asynchronous database access, while SQLite stores user accounts, posts, and comments.

**Media Storage**

ImageKit handles uploaded media. The application stores media URLs and related metadata in the database rather than maintaining a separate local media library.

## Project Structure

```text
lichtblick/
|
|-- backend/
|   |-- api.py
|   |-- users.py
|   |-- database.py
|   |-- schemas.py
|   |-- storage_imagekit.py
|
|-- frontend_app.py
|-- run_backend.py
|
|-- pyproject.toml
|-- uv.lock
|-- .gitignore
|-- .python-version
|-- LICENSE
|-- README.md
```

### Important Files

| File | Purpose |
|------|---------|
| `backend/api.py` | FastAPI application and API endpoints |
| `backend/users.py` | JWT authentication and user management |
| `backend/database.py` | Database models and asynchronous sessions |
| `backend/schemas.py` | Pydantic request and response schemas |
| `backend/storage_imagekit.py` | ImageKit client configuration |
| `frontend_app.py` | Streamlit user interface |
| `run_backend.py` | Backend startup script |
| `pyproject.toml` | Project dependencies and configuration |
| `uv.lock` | Locked dependency versions |

## Getting Started

The application can be run locally using Python and the `uv` package manager.

### Prerequisites

- Python 3.11
- Git
- [uv](https://docs.astral.sh/uv/)
- An [ImageKit](https://imagekit.io/) account

An ImageKit account is required to configure media uploads.

### 1. Clone the Repository

```bash
git clone https://github.com/waistarek/lichtblick.git
cd lichtblick
```

### 2. Install Dependencies

Install the project dependencies using `uv`:

```bash
uv sync
```

This creates a virtual environment and installs the dependencies defined in `pyproject.toml` and `uv.lock`.

### 3. Configure Environment Variables

Create a `.env` file in the project root.

Use the following configuration as a reference:

```dotenv
# ImageKit Configuration
IMAGEKIT_PRIVATE_KEY=your_private_key
IMAGEKIT_PUBLIC_KEY=your_public_key
IMAGEKIT_URL=https://ik.imagekit.io/your_endpoint

# JWT Authentication
JWT_SECRET=your_secure_random_secret
JWT_LIFETIME_SECONDS=3600

# Backend Configuration
BACKEND_URL=http://localhost:8000
```

Replace the example values with your own configuration.

Generate a cryptographically secure JWT secret locally with:

```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the generated value into your local `.env` file.

**Security:** Never commit `.env` files, private API keys, passwords, or authentication secrets to version control.

### 4. Start the Backend

Run the backend from the project root:

```bash
uv run python run_backend.py
```

Alternatively, start FastAPI directly for local development:

```bash
uv run uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
```

The backend should be accessible at:

- API: http://localhost:8000
- Interactive API documentation: http://localhost:8000/docs

The application initializes its database tables during startup.

### 5. Start the Frontend

Open a second terminal in the project directory.

Start Streamlit:

```bash
uv run streamlit run frontend_app.py
```

The frontend is typically available at:

http://localhost:8501

Ensure that the backend is running before using features that communicate with the API.

## Using the Application

### 1. Create an Account

Open the Streamlit interface and navigate to the registration view.

Enter an email address and password to create a user account.

### 2. Sign In

Log in using your registered credentials.

The backend provides JWT-based authentication for protected operations.

### 3. Create a Post

Navigate to the post creation interface.

1. Select an image or video.
2. Enter an optional caption.
3. Submit the post.

The application uploads the media through ImageKit and stores the post information in SQLite.

### 4. Explore the Feed

The feed displays stored posts ordered by creation time, with the newest posts first.

Each post contains media information and associated metadata.

### 5. Interact with Posts

Authenticated users can:

- View comments
- Add comments
- Use the frontend's reaction controls
- Delete their own posts

Reaction controls currently use local frontend state when backend reaction endpoints are unavailable.

## REST API

The backend exposes endpoints for authentication, posts, media uploads, and comments.

FastAPI automatically generates interactive API documentation at `/docs`.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/jwt/login` | Authenticate and obtain a JWT |
| POST | `/auth/jwt/logout` | JWT authentication logout endpoint |
| GET | `/users/me` | Retrieve the current user |

Additional password reset and verification routes are registered through `fastapi-users`. Their use in a deployed application requires the corresponding notification and verification workflows.

### Posts and Media

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/upload` | Upload media and create a post |
| GET | `/feed` | Retrieve the shared post feed |
| DELETE | `/post/{post_id}` | Delete a post owned by the authenticated user |

### Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/post/{post_id}/comments` | Retrieve comments for a post |
| POST | `/post/{post_id}/comments` | Add a comment to a post |

The application's post and comment endpoints require authentication.

## Database

Lichtblick uses SQLite with asynchronous SQLAlchemy sessions.

The application includes three main data models.

### User

Stores account and authentication-related information, including:

- Unique user ID
- Email address
- Hashed password
- Account status

### Post

Stores information about published media:

- Unique post ID
- Author ID
- Caption
- Media URL
- Media type and filename
- Creation timestamp

### Comment

Stores comments associated with posts:

- Unique comment ID
- Post ID
- Author ID
- Comment text
- Creation timestamp

The application uses relationships between users, posts, and comments to associate content with its respective author.

## Technical Highlights

This project explores several practical software development concepts:

**REST API Development**

Implementation of application endpoints using FastAPI, including request handling, authentication dependencies, and database operations.

**Authentication and Authorization**

Integration of JWT-based authentication and ownership checks for operations such as deleting posts.

**Asynchronous Database Access**

Use of SQLAlchemy asynchronous sessions for querying and modifying persistent application data.

**External Service Integration**

Integration of the ImageKit SDK to upload media and retrieve hosted media URLs.

**Frontend-Backend Communication**

Connection between an interactive Streamlit interface and a FastAPI backend through HTTP requests.

**Configuration Management**

Use of environment variables to separate application configuration and API credentials from source code.

## Current Limitations

Lichtblick is a development prototype, not a production-ready social media platform.

The current implementation has several limitations:

- Likes and dislikes are not consistently persisted through backend endpoints.
- SQLite is used as the local database.
- Automated test coverage has not been established.
- Server-side media validation and upload limits require additional hardening.
- Feed and comment API responses currently include author email information.
- Additional security and deployment measures would be required for public production use.

These limitations are documented to distinguish implemented functionality from potential future improvements.

## Potential Future Improvements

Possible extensions include:

- Persistent backend support for reactions
- Pagination and search functionality
- Enhanced user profiles
- More comprehensive media upload validation
- Automated backend and API tests
- Continuous integration
- Expanded moderation and authorization features

These items are future possibilities and are not presented as implemented features.

## License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for details.
