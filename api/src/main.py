import litellm
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from .chat_completion import conversation_router
from .dependencies import shutdown, startup
from .middleware import setup_middleware

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title='Prompt Alchemy',
    description='Transforming Simple Prompts into Gold',
    version='0.1.0',
    redoc_url=None,
    openapi_url='/api/v1/openapi.json',
)

# Set up rate limiter middleware
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Event handlers for startup and shutdown
app.add_event_handler('startup', startup)
app.add_event_handler('shutdown', shutdown)

# Middleware setup
setup_middleware(app)


# Exception handler for rate limiting
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(status_code=429, content={'detail': 'Rate Limited!'})


# Set up callbacks for litellm
litellm.success_callback = ['langfuse']
litellm.failure_callback = ['langfuse']

# Include application router(s)
app.include_router(conversation_router)

# Entry point for the application
if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
