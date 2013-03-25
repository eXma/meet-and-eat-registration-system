from sqlalchemy import Column, String, Integer, Float, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

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
