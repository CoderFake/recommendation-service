from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI


def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Music Recommendation API",
        version="1.0.0",
        description="""
        API for music recommendation service with Neural Collaborative Filtering and Content-based Filtering.

        ## Authentication

        This API uses Firebase Authentication. To access protected endpoints, you need to include
        an Authorization header with a Firebase ID token:

        ```
        Authorization: Bearer <your-firebase-token>
        ```

        ## Features

        - User authentication and profile management
        - Song search and management
        - User-song interaction tracking
        - Personalized music recommendations
        - Similar song discovery
        - User taste profiling

        ## Models

        The recommendation system uses multiple models:

        - **Neural Collaborative Filtering (NCF)**: Combines matrix factorization and neural networks
        - **Content-based Filtering**: Uses song features for similarity calculations
        - **Hybrid Recommender**: Combines both approaches for better recommendations

        ## Real-time Learning

        The system features real-time incremental learning to adapt to user preferences on the fly.
        Each interaction is processed immediately to update recommendations.
        """,
        routes=app.routes,
    )

    openapi_schema["servers"] = [
        {"url": "/", "description": "Current server"},
        {"url": "https://api.music-recommendation.example.com", "description": "Production server"},
    ]

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Firebase Authentication token."
        }
    }

    openapi_schema["security"] = [{"BearerAuth": []}]

    openapi_schema["tags"] = [
        {
            "name": "authentication",
            "description": "Operations related to user authentication and profiles"
        },
        {
            "name": "songs",
            "description": "Operations for searching, retrieving, and managing songs"
        },
        {
            "name": "interactions",
            "description": "Operations for tracking user-song interactions"
        },
        {
            "name": "recommendations",
            "description": "Operations for retrieving personalized recommendations"
        },
    ]

    openapi_schema["x-api-status"] = "beta"

    app.openapi_schema = openapi_schema
    return app.openapi_schema