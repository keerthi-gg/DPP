from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.routers import lifecycle, products, regulator, transactions
from app.services.errors import (
    InvalidTransactionError,
    InvalidTransitionError,
    NotFoundError,
    UnauthorizedRoleError,
)

app = FastAPI(title="Plastic DPP API", version="0.1.0")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.exception_handler(NotFoundError)
def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(UnauthorizedRoleError)
def handle_unauthorized_role(request: Request, exc: UnauthorizedRoleError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": str(exc)})


@app.exception_handler(InvalidTransitionError)
def handle_invalid_transition(request: Request, exc: InvalidTransitionError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(InvalidTransactionError)
def handle_invalid_transaction(request: Request, exc: InvalidTransactionError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "plastic-dpp-api"}


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/ui/")


app.include_router(products.router)
app.include_router(transactions.router)
app.include_router(lifecycle.router)
app.include_router(regulator.router)

app.mount("/ui", StaticFiles(directory=STATIC_DIR, html=True), name="ui")
