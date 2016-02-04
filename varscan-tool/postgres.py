from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import exc
from sqlalchemy.dialects.postgresql import ARRAY
from contextlib import contextmanager

Base = declarative_base()

class ToolTypeMixin(object):
    """ Gather the timing metrics for different datasets """

    id = Column(Integer, primary_key=True)
    case_id = Column(String)
    tool = Column(String)
    files = Column(ARRAY(String))
    systime = Column(Float)
    usertime = Column(Float)
    elapsed = Column(String)
    cpu = Column(Float)
    max_resident_time = Column(Float)

    def __repr__(self):
        return "<ToolTypeMixin(systime='%d', usertime='%d', elapsed='%s', cpu='%d', max_resident_time='%d'>" %(self.systime,
                self.usertime, self.elapsed, self.cpu, self.max_resident_time)

class Metrics(ToolTypeMixin, Base):

    __tablename__ = 'metrics_table'

@contextmanager
def session_scope():
    """ Provide a transactional scope around a series of transactions """

    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def db_connect(database):
    """performs database connection"""

    return create_engine(URL(**database))

def create_table(engine, tool):
    """ checks if a table for metrics exists and create one if it doesn't """

    inspector = Inspector.from_engine(engine)
    tables = set(inspector.get_table_names())
    print(inspector.get_table_names())
    if tool.__tablename__ not in tables:
        Base.metadata.create_all(engine)


def add_metrics(engine, toolname, case_id, file_ids, metrics, logger):
    """ add provided metrics to database """


    #check if metrics has all information
    if 'system_time' not in metrics:
        raise Exception("system_time not found in metrics")
    if 'user_time' not in metrics:
        raise Exception("user_time not found in metrics")
    if 'wall_clock' not in metrics:
        raise Exception("wall_clock not found in metrics")
    if 'percent_of_cpu' not in metrics:
        raise Exception("percent_of_cpu not found in metrics")
    if 'maximum_resident_set_size' not in metrics:
        raise Exception("maximum resident set size not found in metrics")


    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    met = Metrics(case_id = case_id,
                    tool = toolname,
                    files=file_ids,
                    systime=metrics['system_time'],
                    usertime=metrics['user_time'],
                    elapsed=metrics['wall_clock'],
                    cpu=metrics['percent_of_cpu'],
                    max_resident_time=metrics['maximum_resident_set_size'])

    create_table(engine, met)


    session.add(met)
    session.commit()

    logger.info("Added entry for case id: %s in table %s." %(met.case_id, met.__tablename__))

