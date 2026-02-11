# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import PlainTextResponse
# from app.api.v1.endpoints import meridian
# from app.api.v1.endpoints import auth
# from app.api.v1.endpoints import chat

# from app.core.config import settings
# from app.api.v1.endpoints import shared, harper, oakfield

# app = FastAPI(
#     title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
# )

# if settings.BACKEND_CORS_ORIGINS:
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=settings.BACKEND_CORS_ORIGINS,
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

# # Routers
# app.include_router(
#     shared.companies_router,
#     prefix=f"{settings.API_V1_STR}/companies",
#     tags=["companies"],
# )
# app.include_router(
#     shared.decisions_router,
#     prefix=f"{settings.API_V1_STR}/decisions",
#     tags=["decisions"],
# )
# app.include_router(
#     harper.router, prefix=f"{settings.API_V1_STR}/harper", tags=["harper"]
# )
# app.include_router(
#     oakfield.router, prefix=f"{settings.API_V1_STR}/oakfield", tags=["oakfield"]
# )
# app.include_router(
#     meridian.router, prefix=f"{settings.API_V1_STR}/meridian", tags=["meridian"]
# )
# app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
# app.include_router(chat.router, prefix=settings.API_V1_STR, tags=["chat"])


# @app.get("/", response_class=PlainTextResponse)
# def root():
#     return "UnloqAI Backend API is live"




# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.core.config import settings
# from app.api.v1.endpoints import shared, harper, oakfield

# app = FastAPI(
#     title=settings.PROJECT_NAME,
#     openapi_url=f"{settings.API_V1_STR}/openapi.json"
# )

# if settings.BACKEND_CORS_ORIGINS:
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=settings.BACKEND_CORS_ORIGINS,
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

# app.include_router(
#     shared.companies_router,
#     prefix=f"{settings.API_V1_STR}/companies",
#     tags=["companies"]
# )
# app.include_router(
#     shared.decisions_router,
#     prefix=f"{settings.API_V1_STR}/decisions",
#     tags=["decisions"]
# )
# app.include_router(
#     harper.router,
#     prefix=f"{settings.API_V1_STR}/harper",
#     tags=["harper"]
# )
# app.include_router(
#     oakfield.router,
#     prefix=f"{settings.API_V1_STR}/oakfield",
#     tags=["oakfield"]
# )

# @app.get("/")
# def root():
#     return {"message": "Welcome to UnloqAI Backend"}



from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
# from app.api.v1.api import api_router
from app.core.config import settings
from .api.v1.endpoints import shared, harper, oakfield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Routers
app.include_router(
    shared.companies_router,
    prefix=f"{settings.API_V1_STR}/companies",
    tags=["companies"]
)

app.include_router(
    shared.decisions_router,
    prefix=f"{settings.API_V1_STR}/decisions",
    tags=["decisions"]
)

app.include_router(
    harper.router,
    prefix=f"{settings.API_V1_STR}/harper",
    tags=["harper"]
)

app.include_router(
    oakfield.router,
    prefix=f"{settings.API_V1_STR}/oakfield",
    tags=["oakfield"]
)

from app.api.v1.endpoints import meridian

app.include_router(
    meridian.router,
    prefix=f"{settings.API_V1_STR}/meridian",
    tags=["meridian"]
)


from app.api.v1.endpoints import auth
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["auth"]
)

from app.api.v1.endpoints import chat
app.include_router(
    chat.router,
    prefix=f"{settings.API_V1_STR}/chat",
    tags=["chat"]
)
# Analysis router removed - module missing

# API V1 ROOT ENDPOINT
@app.get("/api/v1", response_class=PlainTextResponse)
def api_v1_root():
    return "UnloqAI API v1 is live"

# DEBUG ENDPOINT
@app.get("/api/v1/debug")
def debug_info():
    return {
        "status": "alive",
        "api_v1_str": settings.API_V1_STR,
        "cors_origins": settings.BACKEND_CORS_ORIGINS,
    }

# ROUTE LISTING
@app.get("/api/v1/routes")
def list_routes():
    routes = []
    for route in app.routes:
        path = getattr(route, "path", None)
        name = getattr(route, "name", None)
        methods = list(getattr(route, "methods", []))
        routes.append({"path": path, "name": name, "methods": methods})
    return routes

# ROOT ENDPOINT (FIXED)
@app.get("/", response_class=PlainTextResponse)
def root():
    return "UnloqAI Backend API is live"

# CATCH-ALL FOR DEBUGGING 404s
@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])
async def catch_all(request: Request, path_name: str):
    from fastapi.responses import JSONResponse
    
    # If it's an OPTIONS request, return 200 to allow CORS preflight to pass
    if request.method == "OPTIONS":
        return JSONResponse(
            status_code=200,
            content={"message": "OPTIONS preflight handled in catch-all"},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    return JSONResponse(
        status_code=404,
        content={
            "message": "Caught in final catch-all. This path is not defined.",
            "requested_path": path_name,
            "method": request.method,
            "headers": dict(request.headers)
        }
    )

