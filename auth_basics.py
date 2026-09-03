from fastapi import FastAPI, HTTPException, Depends, Header
from jose import jwt
from datetime import timezone, datetime, timedelta

app = FastAPI()

# jwt token has 3 parts header, payload, signature

SECRET_KEY = "mysecret"
ALGORITHM = "HS256"

# Create token
def create_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=30)
    to_encode.update({
        "exp":expire
    })
    token = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return token

# Login API (Token generate)
@app.post("/login")
def login(username:str, password:str):
    if username!="maha" or password!="1234":
        raise HTTPException (
            status_code=401,
            detail="Invalid Username and password"
        )
    token = create_token({
        "sub":username
    })
    return {
        "access_token":token
    }
    
# Verify Token
def verify_token(token:str = Header(None)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        return payload
    except:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expire token"
        )
        
# protected route
@app.get("/secure")
def secure_data(user = Depends(verify_token)):
    return{
        "message": "Secure Data Accessed",
        "user": user
    }