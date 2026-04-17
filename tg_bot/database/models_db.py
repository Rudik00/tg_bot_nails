from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Master(Base):
    __tablename__ = "masters"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    name = Column(String, nullable=False)
    # Пример хранения: "пн,вт,ср,чт,пт"
    work_days = Column(String, nullable=True)
    # Пример хранения: "01.05,09.05,22.06"
    weekend_days = Column(String, nullable=True)
    list_of_clients = relationship(
        "MasterClient",
        back_populates="master",
        cascade="all, delete-orphan",
    )


class MasterClient(Base):
    __tablename__ = "master_clients"
    __table_args__ = (
        UniqueConstraint(
            "master_id",
            "booking_date",
            "booking_time",
            name="uq_master_booking_slot",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(
        Integer,
        ForeignKey("masters.id", ondelete="CASCADE"),
        nullable=False,
    )
    booking_date = Column(Date, nullable=False)
    booking_time = Column(Time, nullable=False)
    service = Column(String, nullable=False)
    client_telegram_id = Column(BigInteger, nullable=False, index=True)

    master = relationship("Master", back_populates="list_of_clients")


class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(Integer, nullable=True)
    time_services = Column(Integer, nullable=True)  # Время в минутах

    bookings = relationship("Client", back_populates="service")


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    client_telegram_id = Column(BigInteger, nullable=False, index=True)
    client_username = Column(String, nullable=True)
    service_id = Column(
        Integer,
        ForeignKey("services.id", ondelete="RESTRICT"),
        nullable=False,
    )
    booking_date = Column(Date, nullable=False)
    booking_time = Column(Time, nullable=False)
    master_telegram_id = Column(BigInteger, nullable=False, index=True)
    master_username = Column(String, nullable=True)
    master_name = Column(String, nullable=False)

    service = relationship("Service", back_populates="bookings")


# Временный алиас, чтобы не ломать старые импорты.
User = Master
