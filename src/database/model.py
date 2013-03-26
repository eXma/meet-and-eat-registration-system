import hashlib
import datetime
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, validates

Base = declarative_base()


class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    token = Column(String, unique=True, index=True)
    allergies = Column(String)
    vegetarians = Column(Integer, default=0)
    confirmed = Column(Boolean, default=False)
    phone = Column(String)
    email = Column(String)

    @validates("name")
    def validate_name(self, _, value):
        if self.name != value and self.token is None:
            self._update_token(value)
        return value

    def _update_token(self, payload):
        token_hash = hashlib.sha1()
        token_hash.update(payload)
        token_hash.update(str(datetime.datetime.now()))
        self.token = token_hash.hexdigest()


class Members(Base):
    __tablename__ = "members"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    team = relationship(Team,
                        backref=backref("members", cascade="all, delete-orphan", lazy="joined"),
                        cascade="all",
                        lazy="joined")


class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True)
    street = Column(String)
    zip_no = Column(String(5))
    extra = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    center_distance = Column(Float)

    team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    team = relationship(Team,
                        backref=backref("location", cascade="all, delete-orphan", lazy="joined", uselist=False),
                        cascade="all",
                        lazy="joined")
