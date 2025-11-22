from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Producto(Base):
    """Modelo para productos de supermercados"""

    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    fuente = Column(String(50), index=True)
    categoria = Column(String(100))
    nombre = Column(String(300))
    marca = Column(String(100))
    precio = Column(Float)
    precio_min = Column(Float)
    precio_max = Column(Float)
    presentacion = Column(String(100))
    ean = Column(String(50))
    sucursales_disponibles = Column(Integer)
    lat = Column(Float)
    lng = Column(Float)
    # Campos opcionales para e-commerce
    vendedor = Column(String(100))
    link = Column(String(500))
    condicion = Column(String(50))
    stock = Column(Integer)

    __table_args__ = (
        Index("idx_fuente_categoria", "fuente", "categoria"),
        Index("idx_timestamp_fuente", "timestamp", "fuente"),
    )

    def __repr__(self):
        return f"<Producto {self.nombre[:30]}: ${self.precio}>"
