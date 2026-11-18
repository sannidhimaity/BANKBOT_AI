
from database.db import engine, Base
from database import models


def initialize_database():

    print("Initializing BankBot AI database...")

    Base.metadata.create_all(bind=engine)

    print("Database created successfully!")

    print("Tables created:")

    for table_name in Base.metadata.tables:
        print(f"- {table_name}")


if __name__ == "__main__":
    initialize_database()
