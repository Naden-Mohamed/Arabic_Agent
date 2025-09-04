from fastapi import FastAPI, APIRouter


base_router = APIRouter(
    # prefix="/api1",
    # tags=["Base"],
)

@base_router.get("/welcome")
async def read_root():
    return {"Good": "World"}