from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker
from decouple import config

# Membuat URL koneksi dengan driver mysql+pymysql
url = URL.create(
    drivername="mysql+pymysql",  # Menggunakan 'mysql+pymysql'
    username=config("DB_USER"),   # Username dari environment variable
    password=config("DB_PASSWORD"),  # Password dari environment variable
    host="localhost",  # Host database
    database="mydb",   # Nama database
    port=3306           # Port database, default MySQL adalah 3306
)

# Membuat engine dan session maker
engine = create_engine(url)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Definisi model Conversation dengan panjang untuk kolom VARCHAR
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String(255))  # Menambahkan panjang untuk VARCHAR
    message = Column(String(255))  # Menambahkan panjang untuk VARCHAR
    response = Column(String(255))  # Menambahkan panjang untuk VARCHAR

# Membuat semua tabel yang belum ada di database
Base.metadata.create_all(engine)
