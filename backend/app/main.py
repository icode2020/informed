"""Public foundation endpoints. No voter profiles are persisted yet."""
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="Informed API", version="0.1.0")


class HealthResponse(BaseModel):
    status: str = "ok"


class ProfileInput(BaseModel):
    interests: list[dict] = Field(default_factory=list)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.get("/v1/status")
def status_info() -> dict[str, str]:
    return {"stage": "foundation", "authentication": "not_configured"}


@app.post("/v1/profiles", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def create_profile(_: ProfileInput) -> None:
    # Fail closed: never persist or accept a sensitive profile until
    # identity, consent, authorization, KMS and ZeroDB are configured.
    raise HTTPException(
        status_code=501,
        detail="Profile storage requires authenticated identity, explicit consent and encryption",
    )
