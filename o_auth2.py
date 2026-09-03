from fastapi import FastAPI, HTTPException, Depends
from jose import jwt, JWTError
from datetime import timezone, datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pwdlib import PasswordHash

app = FastAPI()

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# password hashing setup
pwd_context = PasswordHash.recommended()

# OAuth Setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Dummy user 
fake_user_db = {
    "admin": {
        "username":"admin",
        "hashed_password":pwd_context.hash("1234")
    }
}

# Hash Password
def hash_password(password:str):
    return pwd_context.hash(password)

# Verify Password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Create token
def create_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({
        "exp":expire
    })
    token = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token

# Login API (OAuth2 Form)
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_user_db.get(form_data.username)
    if not user or not verify_password(form_data.password,user["hashed_password"]):
        raise HTTPException(
            status_code=400,
            detail="Invalid username or password"
        )
    access_token = create_token({"sub":form_data.username})
    return {
        "access_token":access_token,
        "token_type":"bearer"
    }
    
# Verify Token
def verify_token(token:str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        return username
    
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail = "Invalid token"
        )
        
# protected route
@app.get("/secure")
def secure_data(user:str = Depends(verify_token)):
    return{
        "message": "You have access to this route!",
        "user": user
    }