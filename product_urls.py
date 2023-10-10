from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from models import User, Product
from schemas import ProductModel
from database import session, engine
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException

product_urls = APIRouter(
    prefix='/product'
)
session = session(bind=engine)


@product_urls.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductModel, Authorize: AuthJWT = Depends()):
    """yangi product yaratish"""
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='enter valid access token')

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()
    if current_user.is_staff:
        new_product = Product(
            name=product.name,
            price=product.price
        )
        session.add(new_product)
        session.commit()
        data = {
            'success': True,
            'code': 201,
            'message': 'product is created',
            'data': {
                'id': new_product.id,
                'name': new_product.name,
                'price': new_product.price
            }

        }
        return jsonable_encoder(data)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail='only admin can add new product ')


@product_urls.get('/list')
async def product_list(Authorize: AuthJWT = Depends()):
    """productlar ro'yxatini ko'rish"""
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='enter valid access token')

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        products = session.query(Product).all()
        custom_data = [
            {
                'id': product.id,
                'product_name': product.name,
                'product_price': product.price
            }
            for product in products
        ]
        return jsonable_encoder(custom_data)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                             detail='Only SuperAdmin can see all products')


@product_urls.get('/{id}')
async def get_product_by_id(id: int, Authorize: AuthJWT = Depends()):
    """productlar ro'yxatini ko'rish"""
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='enter valid access token')

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        product = session.query(Product).filter(Product.id == id).first()
        if product:
            response = {
                'product_id': product.id,
                'product_name': product.name,
                'product_price': product.price
            }
            return jsonable_encoder(response)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Product with {id} ID is not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only SuperAdmin is allowed to this request")


@product_urls.delete('/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_by_id(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='enter valid access token')
    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()
    if current_user.is_staff:
        product = session.query(Product).filter(Product.id == id).first()
        if product:
            session.delete(product)
            session.commit()
            data = {
                "success": True,
                'code': 200,
                'message': f'product with ID {id} has been deleted',
                'data': None
            }
            return jsonable_encoder(data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Product with ID {id} is not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='Only SuperAdmin is allowed to delete product')


@product_urls.put('/update/{id}', status_code=status.HTTP_200_OK)
async def update_product_by_id(id: int, update_data: ProductModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='enter valid access token')
    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()
    if current_user.is_staff:
        product = session.query(Product).filter(Product.id == id).first()
        if product:
            for key, value in update_data.dict(
                    exclude_unset=True).items():  # exclude_unset=True bu partial update qilish uchun, yani qisman:
                setattr(product, key, value)
            session.commit()
            data = {
                'success': True,
                'code': 200,
                'message': f"Product with ID {id} has been updated",
                'data': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price
                }
            }
            return jsonable_encoder(data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Product with ID {id} is not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only SuperAdmin is allowed to update product")

