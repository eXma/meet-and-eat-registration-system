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
    deleted = Column(Boolean, default=False)
    backup = Column(Boolean, default=False)
    want_information = Column(Boolean, default=False)
    groups = Column(Integer, default=0)

    @validates("name")
    def validate_name(self, _, value):
        if self.name != value and self.token is None:
            self._update_token(value)
        return value

    def _update_token(self, payload):
        token_hash = hashlib.sha1()
        if isinstance(payload, unicode):
            token_hash.update(payload.encode("utf8"))
        else:
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


class RouteDistance(Base):
    __tablename__ = "route_distances"
    id = Column(Integer, primary_key=True)
    location_from_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    location_from = relationship(Location, foreign_keys=[location_from_id])

    location_to_id = Column(Integer, ForeignKey("locations.id", ondelete="CASCADE"), nullable=False)
    location_to = relationship(Location, foreign_keys=[location_to_id])

    distance = Column(Float, nullable=False)


class MeetingEntry(Base):
    __tablename__ = "meeting_entry"
    id = Column(Integer, primary_key=True)
    host_team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    host = relationship(Team, foreign_keys=[host_team_id])

    plan_round = Column(Integer, nullable=False)
    participant_team_id = Column(Integer, ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    participant = relationship(Team, foreign_keys=[participant_team_id])


    def __cmp__(self, other):
        assert isinstance(other, MeetingEntry)

        if self.__eq__(other):
            return 0

        return (self.host_team_id - other.host_team_id << 16) + \
               (self.plan_round - other.plan_round << 8) + \
               (self.participant_team_id - other.participant_team_id)

    def __eq__(self, other):
        if not isinstance(other, MeetingEntry):
            return False
        return (self.plan_round == other.plan_round and
                self.host_team_id == other.host_team_id and
                self.participant_team_id == other.participant_team_id)

    def __repr__(self):
        return "MeetingEntry(host=%d, round=%d, participant=%d)" % (self.host_team_id,
                                                                    self.plan_round,
                                                                    self.participant_team_id)
