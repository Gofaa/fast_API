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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()
    new_order = Order(
        quantity=order.quantity,
        product_id=order.product_id
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
            "product": {
                "id": new_order.product_id,
                "name": new_order.product.name,
                "price": new_order.product.price
            },
            'quantity': new_order.quantity,
            'order_status': new_order.order_statuses.value,
            "total_price": new_order.quantity * new_order.product.price
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
                "product": {
                    "id": order.product_id,
                    "name": order.product.name,
                    "price": order.product.price,
                    "total_price": order.quantity * order.product.price
                },
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
                'order_user': {
                    "id": order.user.id,
                    "name": order.user.username,
                    "email": order.user.email
                },
                "product": {
                    "id": order.product_id,
                    "name": order.product.name,
                    "price": order.product.price,
                    "total_price": order.quantity * order.product.price
                },
                'order_status': order.order_statuses.value
            }
            return jsonable_encoder(response)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Order with {id} ID is not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only SuperAdmin is allowed to this request")


@order_urls.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
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


@order_urls.get('/user/orders', status_code=status.HTTP_200_OK)
async def get_user_orders(Authorize: AuthJWT = Depends()):
    """
    get a requested user's orders
    :param Authorize:
    :return:
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='enter valid access token')
    username = Authorize.get_jwt_subject()
    print(username)
    current_user = session.query(User).filter(User.username == username).first()
    orders = current_user.orders

    custom_data = [
        {
            "id": order.id,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product": {
                'id': order.product.id,
                "name": order.product.name,
                "price": order.product.price
            },
            "quantity": order.quantity,
            "order_statuses": order.order_statuses.value,
            "total_price": order.quantity * order.product.price
        }
        for order in orders
    ]
    return jsonable_encoder(custom_data)


@order_urls.get('/user/order/{id}', status_code=status.HTTP_200_OK)
async def get_user_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    """
    get user order by id
    :param id:
    :param Authorize:
    :return:
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='enter valid access token')
    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()
    orders = current_user.orders
    for order in orders:
        if order.id == id:
            order_data = {
                "id": order.product.id,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email
                },
                "product": {
                    "id": order.product.id,
                    'name': order.product.name,
                    'price': order.product.price,
                },
                'quantity': order.quantity,
                'order_statuses': order.order_statuses.value,
                'total_price': order.quantity * order.product.price
            }
            return jsonable_encoder(order_data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"No order with this ID {id}")


@order_urls.put('{id}/update', status_code=status.HTTP_200_OK)
async def update_order(id: int, order: OrderModel, Authorize: AuthJWT = Depends()):
    """
    Updating user order by fields: quantity and product id
    :param id:
    :param order:
    :param Authorize:
    :return:
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="enter valid access token")
    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username)

    order_to_update = session.query(Order).filter(Order.id == id).first()
    if order_to_update.username != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="you can't update other user's order")
    order_to_update.quantity = order.quantity
    order_to_update.product_id = order.product_id
    session.commit()

    data = {
        "success": True,
        "code": 200,
        "message": "your order successfully edited",
        'data': {
            'id': order.id,
            'quantity': order.quantity,
            "product": order.product_id,
            "order_status": order.order_statuses

        }
    }
    return jsonable_encoder(data)


@order_urls.patch('/{id}/update-status', status_code=status.HTTP_200_OK)
async def update_order_status(id: int, update_status: OrderStatusModel, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="enter valid access token")
    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()
    if user.is_staff:
        order_to_update = session.query(Order).filter(Order.id == id).first()
        if (update_status.order_statuses == "PENDING") or (update_status.order_statuses == "IN_TRANSIT") or (
                update_status.order_statuses == "DELIVERED"):
            order_to_update.order_statuses = update_status.order_statuses
            session.commit()

            custom_response = {
                "success": True,
                'code': 200,
                'message': 'user order is successfully updated',
                'data': {
                    'id': order_to_update.id,
                    'order_status': order_to_update.order_statuses
                }
            }

            return jsonable_encoder(custom_response)

        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="invalid order statuses")


@order_urls.delete('/{id}/delete', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(id: int, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="enter valid access token")
    username = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == username).first()
    order = session.query(Order).filter(Order.id == id).first()
    if order.user != user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Kechirasiz siz boshqa foydalanuvchilarning buyurtmasini o'chira olmaysiz!")
    if order.order_statuses != "PENDING":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Kechirasiz siz yo'lga chiqgan va yetkazib berilgan buyurtmalarni o'chira olmaysiz!")
    session.delete(order)
    session.commit()

    custom_response = {
        "success": True,
        "code": 200,
        "message": "User order is successfully deleted",
        "data": None
    }
    return jsonable_encoder(custom_response)
