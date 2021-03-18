from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .auth_handler import decodeJWT
from main import r


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token.")
            token = credentials.credentials
            r.delete(token)
            return token
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str):
        is_valid = False
        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            is_valid = True
        return is_valid


class LibrarianBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(LibrarianBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(LibrarianBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or access denied.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str):
        is_valid = False
        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            if payload['role'] == 'librarian':
                is_valid = True
        return is_valid


class MemberBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(MemberBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(MemberBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or access denied.")
            token = credentials.credentials
            user_id = r.get(token)
            return int(user_id)
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str):
        is_valid = False
        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            if payload['role'] == 'member':
                is_valid = True
        return is_valid
