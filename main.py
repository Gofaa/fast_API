from fastapi import FastAPI
from auth_urls import auth_urls
from order_urls import order_urls
from fastapi_jwt_auth import AuthJWT

from product_urls import product_urls
from schemas import Settings

app = FastAPI()


@AuthJWT.load_config
def get_config():
    return Settings()


app.include_router(auth_urls)
app.include_router(order_urls)
app.include_router(product_urls)


@app.get('/')
async def root():
    return {'message': "Bu asosiy sahifa"}
