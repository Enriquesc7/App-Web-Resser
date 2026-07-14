# FastAPI
from fastapi import APIRouter, Depends, status

# Schemas
from schemas.user import UserPublicProfile

# Auth
from managers.auth import get_current_active_user


router = APIRouter(
    prefix="/api",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)


@router.get(
    path="/me",
    response_model=UserPublicProfile,
    status_code=status.HTTP_200_OK,
    summary="Profil de l'utilisateur connecté",
)
async def get_me(
    current_user=Depends(get_current_active_user),
):
    """
    Retourne le profil de l'utilisateur authentifié.
    - 200 avec UserPublicProfile si la session est valide.
    - 401 si aucun cookie access_token ou token invalide.
    """
    return current_user
