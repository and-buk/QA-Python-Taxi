from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Integer, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Construct a base class for declarative class definitions
Base: Any = declarative_base()


class Driver(Base):
    """Таблица базы данных сервиса заказа такси для работы с водителями сервиса."""

    __tablename__ = "drivers"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="Идентификатор водителя"
    )
    name = Column(String(25), nullable=False, comment="Имя водителя")
    car = Column(String(25), nullable=False, comment="Автомобиль водителя")


class Client(Base):
    """Таблица базы данных сервиса заказа такси для работы с клиентами сервиса."""

    __tablename__ = "clients"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="Идентификатор клиента"
    )
    name = Column(String(25), nullable=False, comment="Имя клиента")
    is_vip = Column(
        Boolean, default=False, nullable=False, comment="Наличие VIP статуса"
    )


class Order(Base):
    """Таблица базы данных сервиса заказа такси для работы с заказами."""

    __tablename__ = "orders"

    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="Идентификатор заказа"
    )
    address_from = Column(String(50), nullable=False, comment="Адрес посадки")
    address_to = Column(String(50), nullable=False, comment="Адрес высадки")
    client_id = Column(
        Integer,
        ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
        comment="Идентификатор клиента",
    )
    driver_id = Column(
        Integer,
        ForeignKey("drivers.id", ondelete="CASCADE"),
        nullable=False,
        comment="Идентификатор водителя",
    )
    date_created = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        comment="Дата и время создания заказа",
    )
    status = Column(
        String(20), nullable=False, default="not_accepted", comment="Статус заказа"
    )
    client = relationship("Client")
    driver = relationship("Driver")
