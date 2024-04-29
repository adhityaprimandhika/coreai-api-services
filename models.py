from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, TIMESTAMP, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean)


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    sub_name = Column(String(255))
    merchant_code = Column(String(50))
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category")
    logo = Column(String(255))
    website = Column(String(255))
    latitude = Column(Numeric(10, 8))  # Assuming latitude with precision 10 and scale 8
    longitude = Column(Numeric(11, 8))  # Assuming longitude with precision 11 and scale 8
    address = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class MerchantGarage(Base):
    __tablename__ = "merchants_garage"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    category = Column(String(255))
    address = Column(String(255))
    website = Column(String(255))
    logo = Column(String(255))
    latitude = Column(Numeric(10, 8))  # Assuming latitude with precision 10 and scale 8
    longitude = Column(Numeric(11, 8))  # Assuming longitude with precision 11 and scale 8
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())