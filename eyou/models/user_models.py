
from sqlalchemy import (
    Column,
    Index,
    Integer,
    Float,
    Text,
    Boolean,
    ForeignKey,
Table

)

from sqlalchemy.orm import relationship
from .meta import Base
import bcrypt

user_role = Table('user_role', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('role_id', Integer, ForeignKey('role.id'))
)

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(Text)
    password = Column(Text)
    roles = relationship("Role", secondary=user_role)
    profile = relationship("Profile", uselist=False, back_populates="user")

    def set_password(self, pw):
        pwhash = bcrypt.hashpw(pw.encode('utf8'), bcrypt.gensalt())
        self.password = pwhash.decode('utf8')

    def check_password(self, pw):
        if self.password is not None:
            expected_hash = self.password.encode('utf8')
            return bcrypt.checkpw(pw.encode('utf8'), expected_hash)
        return False


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    name = Column(Text)

