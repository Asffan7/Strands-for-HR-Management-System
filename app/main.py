

from fastapi import FastAPI

from app.api import api_router

app = FastAPI(
  title="Strands HR Management System",
  description="HR management APIs with leave management as the current scope.",
  version="1.0.0",
)
app.include_router(api_router)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
  """Return a lightweight process health response without contacting dependencies."""
  return {"status": "ok"}