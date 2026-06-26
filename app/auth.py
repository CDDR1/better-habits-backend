from typing import Annotated

from fastapi import Depends

# TODO: Replace this stub with real Clerk JWT verification before going to production.
# Plan: install `clerk-backend-api`, validate the bearer token from the Authorization
# header against Clerk's JWKS, and return the `sub` claim (the Clerk user ID).
def get_current_user_id() -> str:
    return "user_dev"

CurrentUser = Annotated[str, Depends(get_current_user_id)]
