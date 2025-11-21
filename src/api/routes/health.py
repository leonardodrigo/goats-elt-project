from fastapi import APIRouter, status

router = APIRouter()


@router.get(
    "/health", status_code=status.HTTP_200_OK, description="Health check endpoint"
)
def health_check():
    return {"status": "ok"}
