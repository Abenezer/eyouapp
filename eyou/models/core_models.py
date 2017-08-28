from sqlalchemy import (
    Column,
    Index,
    Integer,
    Float,
    Text,
    Boolean,
    ForeignKey

)
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Table

from sqlalchemy.orm import relationship

from .meta import Base

place_image_point = Table('place_image_point', Base.metadata,
                          Column('place_image_id', Integer, ForeignKey('place_image.id')),
                          Column('user_id', Integer, ForeignKey('user.id'))
                          )

profile_place = Table('profile_place', Base.metadata,
                      Column('place_id', Integer, ForeignKey('place.id')),
                      Column('profile_id', Integer, ForeignKey('profile.id'))
                      )


class Place(Base):
    __tablename__ = 'place'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)
    lat = Column(Integer)
    lon = Column(Integer)
    type_id = Column(Integer, ForeignKey('type.id'))
    area_id = Column(Integer, ForeignKey('area.id'))
    featured = Column(Boolean(create_constraint=False), default=False)
    type = relationship("Type")
    area = relationship("Area")
    date_added = Column(DateTime)
    feedbacks = relationship("Feedback", back_populates="place")
    menus = relationship("Menu", back_populates="place")
    user_id = Column(Integer, ForeignKey('user.id'))
    parent_id = Column(Integer, ForeignKey('place.id'))
    parent = relationship("Place")
    profiles = relationship(
        "Profile",
        secondary=profile_place,
        back_populates="places")


# Index('place_name_index', Place.name, unique=True, mysql_length=255)

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)
    popularity = Column(Integer)
    types = relationship("Type", back_populates="category")


class Type(Base):
    __tablename__ = 'type'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)
    popularity = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", back_populates="types")


# Index('type_name_index', Type.name, unique=True, mysql_length=255)

class Area(Base):
    __tablename__ = 'area'
    id = Column(Integer, primary_key=True)
    lon = Column(Float)
    lat = Column(Float)
    country = Column(Text)
    city = Column(Text)
    localName = Column(Text)
    displayName = Column(Text)
    description = Column(Text)
    boundingBox = Column(Text)
    OSM_id = Column(Integer)
    nom_place_id = Column(Integer)


class Feedback(Base):
    __tablename__ = 'feedback'
    id = Column(Integer, primary_key=True)
    point = Column(Integer)
    comment = Column(Text)
    date_added = Column(DateTime)
    place_id = Column(Integer, ForeignKey('place.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User")
    place = relationship("Place", back_populates="feedbacks")


class PlaceTag(Base):
    __tablename__ = 'place_tag'
    id = Column(Integer, primary_key=True)
    tag = Column(Text)
    place_id = Column(Integer, ForeignKey('place.id'))
    user_id = Column(Integer, ForeignKey('user.id'))


class Menu(Base):
    __tablename__ = 'menu'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)
    cost = Column(Float)
    place_id = Column(Integer, ForeignKey('place.id'))
    type_id = Column(Integer, ForeignKey('menu_type.id'))
    subtype = Column(Text)
    date_added = Column(DateTime)
    feedbacks = relationship("MenuFeedback", back_populates="menu")
    image_path = Column(Text)
    user_id = Column(Integer, ForeignKey('user.id'))
    place = relationship("Place", back_populates="menus")
    user = relationship("User")


class MenuType(Base):
    __tablename__ = 'menu_type'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    description = Column(Text)


class MenuFeedback(Base):
    __tablename__ = 'menu_feedback'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    menu_id = Column(Integer, ForeignKey('menu.id'))
    tag = Column(Text)
    comment = Column(Text)
    date_added = Column(DateTime)
    rating = Column(Float)
    image_path = Column(Text)
    user = relationship("User")
    menu = relationship("Menu", back_populates="feedbacks")


class PlaceImage(Base):
    __tablename__ = 'place_image'
    id = Column(Integer, primary_key=True)
    place_id = Column(Integer, ForeignKey('place.id'))
    image_path = Column(Text)
    url = Column(Text)
    tag = Column(Text)
    date_added = Column(DateTime)
    users = relationship("User",
                         secondary=place_image_point)


class Profile(Base):
    __tablename__ = 'profile'
    id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    places = relationship("Place", secondary=profile_place, back_populates="profiles")
    picture_path = Column(Text)
    score = Column(Integer)
    gender = Column(Text)
    dob = Column(Date)
    full_name = Column(Text)
    date_added = Column(DateTime)
    work_status_id = Column(Integer, ForeignKey('work_status.id'))
    user = relationship("User", back_populates="profile")
    work_status = relationship("WorkStatus")



class WorkStatus(Base):
    __tablename__ = 'work_status'
    id = Column(Integer, primary_key=True)
    name = Column(Text)

class TestStatus(Base):
    __tablename__ = 'test_status'
    id = Column(Integer, primary_key=True)
    name = Column(Text)