from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class Producto(Base):
    """Modelo para productos (supermercados, e-commerce)"""

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


class Cotizacion(Base):
    """Modelo para cotizaciones (dólar, crypto)"""

    __tablename__ = "cotizaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)
    fuente = Column(String(50))
    nombre = Column(String(100), index=True)
    precio_compra = Column(Float)
    precio_venta = Column(Float)
    moneda = Column(String(10))
    fecha_actualizacion = Column(String(50))

    __table_args__ = (Index("idx_nombre_timestamp", "nombre", "timestamp"),)

    def __repr__(self):
        return f"<Cotizacion {self.nombre}: ${self.precio_venta}>"


class Database:
    """Maneja la conexión y operaciones de base de datos"""

    def __init__(self, db_path="price_monitor.db"):
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        print(f"✓ Base de datos inicializada: {db_path}")

    def guardar_productos(self, lista_productos):
        """Guarda una lista de productos"""
        try:
            contador = 0
            for prod_dict in lista_productos:
                producto = Producto(**prod_dict)
                self.session.add(producto)
                contador += 1

            self.session.commit()
            print(f"✓ Guardados {contador} productos en DB")
            return True

        except Exception as e:
            self.session.rollback()
            print(f"✗ Error guardando productos: {e}")
            return False

    def guardar_cotizaciones(self, lista_cotizaciones):
        """Guarda una lista de cotizaciones"""
        try:
            contador = 0
            for cot_dict in lista_cotizaciones:
                cotizacion = Cotizacion(**cot_dict)
                self.session.add(cotizacion)
                contador += 1

            self.session.commit()
            print(f"✓ Guardadas {contador} cotizaciones en DB")
            return True

        except Exception as e:
            self.session.rollback()
            print(f"✗ Error guardando cotizaciones: {e}")
            return False

    def obtener_ultimos_productos(self, limit=10, fuente=None):
        """Obtiene los últimos productos scrapeados"""
        query = self.session.query(Producto)

        if fuente:
            query = query.filter(Producto.fuente == fuente)

        return query.order_by(Producto.timestamp.desc()).limit(limit).all()

    def obtener_ultimas_cotizaciones(self, limit=10):
        """Obtiene las últimas cotizaciones"""
        return (
            self.session.query(Cotizacion)
            .order_by(Cotizacion.timestamp.desc())
            .limit(limit)
            .all()
        )

    def obtener_comparacion_cotizaciones(self):
        """Obtiene la última cotización de cada tipo para comparar"""
        from sqlalchemy import func

        subq = (
            self.session.query(
                Cotizacion.nombre, func.max(Cotizacion.timestamp).label("max_timestamp")
            )
            .group_by(Cotizacion.nombre)
            .subquery()
        )

        return (
            self.session.query(Cotizacion)
            .join(
                subq,
                (Cotizacion.nombre == subq.c.nombre)
                & (Cotizacion.timestamp == subq.c.max_timestamp),
            )
            .order_by(Cotizacion.precio_venta.desc())
            .all()
        )

    def obtener_estadisticas_generales(self):
        """Obtiene estadísticas generales de la base de datos"""
        from sqlalchemy import func

        total_productos = self.session.query(func.count(Producto.id)).scalar()
        total_cotizaciones = self.session.query(func.count(Cotizacion.id)).scalar()

        primera_fecha_producto = self.session.query(
            func.min(Producto.timestamp)
        ).scalar()
        ultima_fecha_producto = self.session.query(
            func.max(Producto.timestamp)
        ).scalar()

        return {
            "total_productos": total_productos,
            "total_cotizaciones": total_cotizaciones,
            "primera_fecha": primera_fecha_producto,
            "ultima_fecha": ultima_fecha_producto,
            "fuentes_productos": self.session.query(Producto.fuente).distinct().all(),
            "categorias": self.session.query(Producto.categoria).distinct().all(),
        }


if __name__ == "__main__":
    print("=" * 60)
    print(" TEST DATABASE ".center(60))
    print("=" * 60)

    db = Database("test_monitor.db")

    productos_prueba = [
        {
            "timestamp": datetime.now(),
            "fuente": "PreciosClaros",
            "categoria": "leche",
            "nombre": "Leche Entera La Serenísima 1L",
            "marca": "La Serenísima",
            "precio": 850.0,
            "precio_min": 850.0,
            "precio_max": 850.0,
            "presentacion": "1 L",
            "ean": "7790070000001",
            "sucursales_disponibles": 5,
            "lat": -34.6037,
            "lng": -58.3816,
        }
    ]

    db.guardar_productos(productos_prueba)

    cotizaciones_prueba = [
        {
            "timestamp": datetime.now(),
            "fuente": "DolarAPI",
            "nombre": "Blue",
            "precio_compra": 1400.0,
            "precio_venta": 1420.0,
            "moneda": "USD",
            "fecha_actualizacion": datetime.now().isoformat(),
        }
    ]

    db.guardar_cotizaciones(cotizaciones_prueba)

    print("\n--- Últimos productos ---")
    ultimos = db.obtener_ultimos_productos(5)
    for prod in ultimos:
        print(f"  {prod.nombre[:50]} - ${prod.precio}")

    print("\n--- Últimas cotizaciones ---")
    cotizaciones = db.obtener_ultimas_cotizaciones(5)
    for cot in cotizaciones:
        print(f"  {cot.nombre}: ${cot.precio_venta}")

    print("\n✓ Tests completados\n")
