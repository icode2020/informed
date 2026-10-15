"""Informed API: public endpoints and fail-closed identity boundary."""
from fastapi import Depends, FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.auth import Identity, require_identity

app = FastAPI(title="Informed API", version="0.2.0")


class HealthResponse(BaseModel):
    status: str = "ok"


class ProfileInput(BaseModel):
    interests: list[dict] = Field(default_factory=list)


class MeResponse(BaseModel):
    subject: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.get("/v1/status")
def status_info() -> dict[str, str]:
    return {"stage": "auth_boundary", "authentication": "oidc_configuration_required"}


@app.get("/v1/me", response_model=MeResponse)
def me(response: Response, identity: Identity = Depends(require_identity)) -> MeResponse:
    response.headers["Cache-Control"] = "no-store"
    return MeResponse(subject=identity.subject)


@app.post("/v1/profiles", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def create_profile(_: ProfileInput) -> None:
    # Never persist sensitive profiles before consent, authorization, KMS and ZeroDB.
    raise HTTPException(
        status_code=501,
        detail="Profile storage requires authenticated identity, explicit consent and encryption",
    )
