from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from models import User, Product, Order
from schemas import OrderStatusModel, OrderModel
from database import session, engine
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException

order_urls = APIRouter(
    prefix='/order'
)
session = session(bind=engine)


@order_urls.get('/')
async def welcome_page(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        pass
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="enter valid access token")
    return {'message': 'Bu order route sahifasi'}


@order_urls.post('/make', status_code=status.HTTP_201_CREATED)
async def make_order(order: OrderModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
        pass
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    new_order = Order(
        quantity=order.quantity
    )

    new_order.user = user
    session.add(new_order)
    session.commit()

    data = {
        'success': True,
        'code': 201,
        'message': 'Order is successfully created',
        'data': {
            'id': new_order.id,
            'quantity': new_order.quantity,
            'order_status': new_order.order_statuses
        }
    }

    return jsonable_encoder(data)


@order_urls.get('/list')
async def list_all_order(Authorize: AuthJWT = Depends()):
    """Bu barcha buyurtmalar royxatini qaytaradi"""
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Enter valid access token')

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        orders = session.query(Order).all()
        custom_data = [

            {
                'id': order.id,
                'username': order.user.username,
                'user_id': order.user_id,
                'product_id': order.product_id,
                'quantity': order.quantity,
                'order_status': order.order_statuses.value,
            }
            for order in orders
        ]
        return jsonable_encoder(custom_data)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only SuperAdmin can see all orders')


@order_urls.get('/{id}', status_code=status.HTTP_200_OK)
async def get_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    """buyurtmani ID bo'yicha Polish """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="enter valid access token")
    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        if order:
            response = {
                'order_id': order.id,
                'order_quantity': order.quantity,
                'order_user_id': order.user_id,
                'product_id': order.product_id,
                'order_status': order.order_statuses.value
            }
            return jsonable_encoder(response)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Order with {id} ID is not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only SuperAdmin is allowed to this request")


# @order_urls.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
# async def delete_product_by_id(id: int, Authorize: AuthJWT = Depends()):
#     try:
#         Authorize.jwt_required()
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
#                             detail='enter valid access token')
#     user = Authorize.get_jwt_subject()
#     current_user = session.query(User).filter(User.username == user).first()
#     if current_user.is_staff:
#         product = session.query(Product).filter(Product.id == id).first()
#         if product:
#             session.delete(product)
#             session.commit()
#             data = {
#                 "success": True,
#                 'code': 200,
#                 'message': f'product with ID {id} has been deleted',
#                 'data': None
#             }
#             return jsonable_encoder(data)
#         else:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                                 detail=f"Product with ID {id} is not found")
#     else:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
#                             detail='Only SuperAdmin is allowed to delete product')