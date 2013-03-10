from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool


session = None


def init_session(connection_string=None, drop=False):
    if connection_string is None:
        engine =  create_engine('sqlite://',
                                echo=True,
                                connect_args={'check_same_thread':False},
                                poolclass=StaticPool)
    else:
        engine = create_engine(connection_string)

    from database.model import Base

    global session

    if drop:
        try:
            old_session = session
            Base.metadata.drop_all(bind=old_session.bind)
        except:
            pass

    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base.metadata.create_all(bind=engine)

    session = db_session

