from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    safe_password = password[:72]  # bcrypt limit
    return pwd_context.hash(safe_password)

def verify_password(plain_password: str, password_hash: str) -> bool:
    safe_password = plain_password[:72]
    return pwd_context.verify(safe_password, password_hash)
