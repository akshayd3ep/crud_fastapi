from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.items import router as items_router
from routes.clock_in import router as clock_in_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(clock_in_router, prefix="/api/v1")
app.include_router(items_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hello, ASGI World!"}
