from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


session = None


def init_session(connection_string=None, drop=False):
    if connection_string is None:
        connection_string = 'sqlite://'

    from database.model import Base

    global session

    if drop:
        try:
            old_session = session
            Base.metadata.drop_all(bind=old_session.bind)
        except:
            pass

    engine = create_engine(connection_string, echo=True)
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    Base.metadata.create_all(bind=engine)

    session = db_session

