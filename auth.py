# JWT authentication 
# BEARER token le kr jata h 
from data import CustomerData, predictionResponse,predict,app



# configuratins
SECRET_KEY = 'sample key' #will be changed in production
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# security Scheme
from fastapi.security import HTTPBearer
from pydantic import BaseModel
security = HTTPBearer()
# user authenticatiom 
class UserRegister(BaseModel):
    username: str
    password: str
class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type : str  #bearer
    expires_in: int

fake_user_db ={
    'admin': {
        'username':'harsha',
        'paasword': "12345",
        'disable': False
    },
    'user1':{
        'username': 'user1',
        'password':'user01',
        "disabled": False
    },
    'user2':{
        'name': 'user2',
        'password': "user02",
        'disabled': False 
    } 
}
from datetime import timedelta,datetime
from typing import Optional
# import jwt
from jose import jwt
# JWT access token
def create_access_token(data:dict,expires_delta:Optional[timedelta]=None):#timedelta means token kitni der m expire ho jaega
    # we will create copy of date aviod mution
    to_encode = data.copy()
    # we will check if expire_delta is provideed othwise we wioo make default expiration time
    if expires_delta:
        expire =  datetime.utcnow()+ expires_delta
    else:
        expire = datetime.utcnow()+ timedelta(minutes=15)
    # daata  = expiration time add karenge
    to_encode.update({'exp': expire})

    # encode copy the data,secret key,aglorithim
    encode_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    # returm encode token
    return encode_jwt
from fastapi import HTTPException
def verify_token(token:str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    username :str= payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401,detail = "invalid token")
    return username
def auth_user(username:str,password:str):
    user = fake_user_db.get(username)
    if not user or user['password' ] != password:
        return None
    return user
# endpoint for user register
@app.post('/register',response_model=TokenResponse)
async def register_user(user:UserRegister):
    if user.username in fake_user_db:
        raise HTTPException(status_code=400,detail='username already exists')
    # register new user 
    fake_user_db[user.username] = {
        'username': user.username,
        'password': user.password,
        'disabled': False
    }
    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub':user.username},expires_delta=access_token_expire)
    return {
        'access_token': access_token,
        "token_type":'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRE_MINUTES*60
    }


@app.post('/login',response_model = TokenResponse)
async def user_login(user_cred:UserLogin):
    if auth_user(user_cred.username ,user_cred.password) is None:
        raise HTTPException(status_code= 401,detail = "invaild user")
    
    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub':user_cred.username},expires_delta=access_token_expire)
    return {
        'access_token': access_token,
        "token_type":'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRE_MINUTES*60
    }
    
# 3. prediction endpoint with jwt authentication




# 4. log authized ACCESS
# 5.call original prediction function
from typing import ClassVar

class AuthenticaticatedPredictionRequest(BaseModel):
    customer: CustomerData


from fastapi import Depends
# 1.post end point
@app.post ("/predict/auth",response_model = predictionResponse,dependencies=[Depends(security)]) #depends extracts the authorization checks is tha format of bearer token
# 2.response model
async def predict_auth(request:AuthenticaticatedPredictionRequest,credentials=Depends(security)):
# 3. verify Token
    username = verify_token(credentials.credentials)
    
# 4. log authized ACCESS
    print(f"user{username} access he prediction endpoint")
    
# 5.call original prediction function
    return predict(request.customer)#we extract data from function 


    




















