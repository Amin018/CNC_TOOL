from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
def get_my_profile():
    # placeholder; will return the authenticated user once we add auth
    return {"detail": "Current user profile will appear here after auth is added."}
