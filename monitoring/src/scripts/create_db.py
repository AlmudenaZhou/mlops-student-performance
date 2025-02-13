from sqlalchemy import create_engine

from monitoring.config.db_config import DATABASE_URI
from monitoring.src.utils.models import Base

if __name__ == "__main__":
    engine = create_engine(DATABASE_URI)
    Base.metadata.create_all(engine)
    print("Database created")
