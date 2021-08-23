from contextlib import contextmanager
from typing import Generator, Union, Tuple, Any

from flask import Flask, jsonify, request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from taxi_db import Base, Driver, Client, Order
from taxi_validation_tools import (
    post_drivers_schema,
    post_clients_schema,
    post_orders_schema,
    put_orders_schema,
    validate_json,
    validate_url_variable,
)

engine = create_engine("postgresql://postgres:mirniy@localhost:5432/postgres")

Session = scoped_session(sessionmaker(autoflush=True, autocommit=False, bind=engine))


@contextmanager
def session_scope() -> Generator:
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


with session_scope() as session:
    # Создание таблиц, если они не существуют
    Base.metadata.create_all(engine)

app = Flask(__name__)


@app.post("/drivers")
@validate_json(post_drivers_schema)
def post_driver() -> Tuple[Response, int]:
    """Отправляем данные о новом водителе и сохранеям их в базу данных сервиса заказа такси."""
    content: Any = request.get_json()
    with session_scope() as ses:
        new_driver = Driver(name=content["name"], car=content["car"])
        ses.add(new_driver)
        new_driver_info = ses.query(Driver).order_by(Driver.id.desc()).first()
        return (
            jsonify(
                id=new_driver_info.id,
                name=new_driver_info.name,
                car=new_driver_info.car,
            ),
            201,
        )


@app.get("/drivers")
@validate_url_variable(variable="driver_id")
def get_driver() -> Union[Response, Tuple[Response, int]]:
    """Получаем информацию о водителе, имеющемуся в базе данных сервиса заказа такси."""
    with session_scope() as ses:
        id_from_query = request.args.get("driver_id")
        driver_data = ses.query(Driver).get(id_from_query)
        if driver_data is not None:
            return (
                jsonify(id=driver_data.id, name=driver_data.name, car=driver_data.car),
                200,
            )
        else:
            return Response("Object not found", 404)


@app.delete("/drivers/<int:driver_id>")
@validate_url_variable(variable="driver_id")
def delete_driver(driver_id: int) -> Union[Response, Tuple[Response, int]]:
    """Удаляем водителя из базы данных сервиса заказа такси."""
    with session_scope() as ses:
        driver_data = ses.query(Driver).get(driver_id)
        if driver_data is not None:
            ses.query(Driver).filter(Driver.id == driver_id).delete()
            return (
                jsonify(id=driver_data.id, name=driver_data.name, car=driver_data.car),
                200,
            )
        else:
            return Response("Object not found", 404)


@app.post("/clients")
@validate_json(post_clients_schema)
def post_client() -> Tuple[Response, int]:
    """Отправляем данные о новом клиенте и сохраняем их в базу данных сервиса заказа такси."""
    content: Any = request.get_json()
    with session_scope() as ses:
        new_client = Client(name=content["name"], is_vip=content["is_vip"])
        ses.add(new_client)
        new_client_info = ses.query(Client).order_by(Client.id.desc()).first()
        return (
            jsonify(
                id=new_client_info.id,
                name=new_client_info.name,
                is_vip=new_client_info.is_vip,
            ),
            201,
        )


@app.get("/clients")
@validate_url_variable(variable="client_id")
def get_client() -> Union[Response, Tuple[Response, int]]:
    """Получаем информацию о клиенте, имеющемуся в базе данных сервиса заказа такси."""
    with session_scope() as ses:
        id_from_query = request.args.get("client_id")
        client_data = ses.query(Client).get(id_from_query)
        if client_data is not None:
            return (
                jsonify(
                    id=client_data.id, name=client_data.name, is_vip=client_data.is_vip
                ),
                200,
            )
        else:
            return Response("Object not found", 404)


@app.delete("/clients/<int:client_id>")
@validate_url_variable(variable="client_id")
def delete_client(client_id: int) -> Union[Response, Tuple[Response, int]]:
    """Удаляем клиента из базы данных сервиса заказа такси."""
    with session_scope() as ses:
        client_data = ses.query(Client).get(client_id)
        if client_data is not None:
            ses.query(Client).filter(Client.id == client_id).delete()
            return (
                jsonify(
                    id=client_data.id, name=client_data.name, is_vip=client_data.is_vip
                ),
                200,
            )
        else:
            return Response("Object not found", 404)


@app.post("/orders")
@validate_json(post_orders_schema)
def post_order() -> Tuple[Response, int]:
    """Отправляем данные о новом заказе и сохраняем их в базу данных сервиса заказа такси."""
    content: Any = request.get_json()
    with session_scope() as ses:
        new_order = Order(
            client_id=content["client_id"],
            driver_id=content["driver_id"],
            date_created=content["date_created"],
            status=content["status"],
            address_from=content["address_from"],
            address_to=content["address_to"],
        )
        ses.add(new_order)
        new_order_info = ses.query(Order).order_by(Order.id.desc()).first()
        return (
            jsonify(
                id=new_order_info.id,
                client_id=new_order_info.client_id,
                driver_id=new_order_info.driver_id,
                date_created=new_order_info.date_created,
                status=new_order_info.status,
                address_from=new_order_info.address_from,
                address_to=new_order_info.address_to,
            ),
            201,
        )


@app.get("/orders")
@validate_url_variable(variable="order_id")
def get_order() -> Union[Response, Tuple[Response, int]]:
    """Получаем информацию о заказе, из базы данных сервиса заказа такси."""
    with session_scope() as ses:
        id_from_request = request.args.get("order_id")
        order_data = ses.query(Order).get(id_from_request)
        if order_data is not None:
            return (
                jsonify(
                    id=order_data.id,
                    client_id=order_data.client_id,
                    driver_id=order_data.driver_id,
                    date_created=order_data.date_created,
                    status=order_data.status,
                    address_from=order_data.address_from,
                    address_to=order_data.address_to,
                ),
                200,
            )
        else:
            return Response("Object not found", 404)


@app.put("/orders/<int:order_id>")
@validate_url_variable(variable="order_id")
@validate_json(put_orders_schema)
def change_order(order_id: int) -> Union[Response, Tuple[Response, int]]:
    """Отправляем информацию в базу данных сервиса заказа такси о параметрах заказа, которые необходимо поменять."""
    content: Any = request.get_json()
    with session_scope() as ses:
        order_data = ses.query(Order).get(order_id)
        if order_data is not None:
            if order_data.status == "done" or order_data.status == "cancelled":
                return Response(
                    "Unable to change the order with completed or cancelled status",
                    status=400,
                )
            elif (
                order_data.status == "in_progress"
                and content["status"] == "not_accepted"
            ):
                return Response(
                    "Unable to change the status of an order in progress to not accepted",
                    status=400,
                )
            elif (
                order_data.status == "in_progress"
                and order_data.client_id != content["client_id"]
                and order_data.driver_id != content["driver_id"]
                and order_data.date_created != content["date_created"]
            ):
                return Response(
                    "Unable to change some details of an order in progress", status=400
                )
            elif order_data.status == "not_accepted" and content["status"] == "done":
                return Response(
                    "Unable to change an unaccepted order to done status", status=400
                )
            else:
                order_data.driver_id = content["driver_id"]
                order_data.client_id = content["client_id"]
                order_data.date_created = content["date_created"]
                order_data.status = content["status"]
                order_data.address_from = content["address_from"]
                order_data.address_to = content["address_to"]
                new_order_data = ses.query(Order).get(order_id)
                return (
                    jsonify(
                        id=new_order_data.id,
                        client_id=new_order_data.client_id,
                        driver_id=new_order_data.driver_id,
                        date_created=new_order_data.date_created,
                        status=new_order_data.status,
                        address_from=new_order_data.address_from,
                        address_to=new_order_data.address_to,
                    ),
                    200,
                )
        else:
            return Response("Object not found", 404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
