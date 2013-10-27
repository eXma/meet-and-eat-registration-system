from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import StaticPool


# The global database session.
session = None


def init_session(connection_string=None, drop=False):
    """Initialize the database session and create the schema if it
    does not exist.

    The connection string describes the database connection.
    Documentation on this can be found on [1]. If its omitted
    a temporary in-memory sqlite database will be used. This
    is useful for unittesting where you need a fresh database
    on every run.

    The schema can also be dropped before initialization by
    setting the drop parameter to true.

    The session can be accessed by the session variable of the
    database module.

    [1] http://docs.sqlalchemy.org/en/rel_0_8/core/engines.html

    :param connection_string: The connection description for the
                              engine. See above for details
    :param drop: Drop the schema and recreate it in init. All
                 data will be lost!
    """
    if connection_string is None:
        engine =  create_engine('sqlite://',
                                echo=False,
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

