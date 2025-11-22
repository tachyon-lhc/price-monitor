from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from datetime import datetime

# Import relativo del modelo
try:
    from .models import Base, Producto
except ImportError:
    # Fallback para testing directo
    import sys

    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from src.database.models import Base, Producto


class Database:
    """Maneja la conexión y operaciones de base de datos"""

    def __init__(self, db_path="price_monitor.db"):
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        print(f"Base de datos inicializada: {db_path}")

    def guardar_productos(self, lista_productos):
        """Guarda una lista de productos"""
        try:
            contador = 0
            for prod_dict in lista_productos:
                producto = Producto(**prod_dict)
                self.session.add(producto)
                contador += 1

            self.session.commit()
            print(f"Guardados {contador} productos en DB")
            return True

        except Exception as e:
            self.session.rollback()
            print(f"Error guardando productos: {e}")
            return False

    def obtener_ultimos_productos(self, limit=10, fuente=None):
        """Obtiene los últimos productos scrapeados"""
        query = self.session.query(Producto)

        if fuente:
            query = query.filter(Producto.fuente == fuente)

        return query.order_by(Producto.timestamp.desc()).limit(limit).all()

    def obtener_productos_por_categoria(self, categoria, limit=50):
        """Obtiene productos de una categoría específica"""
        return (
            self.session.query(Producto)
            .filter(Producto.categoria == categoria)
            .order_by(Producto.precio.asc())
            .limit(limit)
            .all()
        )

    def obtener_estadisticas_generales(self):
        """Obtiene estadísticas generales de la base de datos"""
        total_productos = self.session.query(func.count(Producto.id)).scalar()
        primera_fecha = self.session.query(func.min(Producto.timestamp)).scalar()
        ultima_fecha = self.session.query(func.max(Producto.timestamp)).scalar()

        return {
            "total_productos": total_productos,
            "primera_fecha": primera_fecha,
            "ultima_fecha": ultima_fecha,
            "fuentes_productos": [
                f[0] for f in self.session.query(Producto.fuente).distinct().all()
            ],
            "categorias": [
                c[0] for c in self.session.query(Producto.categoria).distinct().all()
            ],
        }

    def obtener_estadisticas_por_categoria(self):
        """Obtiene estadísticas agrupadas por categoría"""
        resultado = (
            self.session.query(
                Producto.categoria,
                func.count(Producto.id).label("cantidad"),
                func.avg(Producto.precio).label("precio_promedio"),
                func.min(Producto.precio).label("precio_min"),
                func.max(Producto.precio).label("precio_max"),
            )
            .group_by(Producto.categoria)
            .all()
        )

        return [
            {
                "categoria": r.categoria,
                "cantidad": r.cantidad,
                "precio_promedio": round(r.precio_promedio, 2)
                if r.precio_promedio
                else 0,
                "precio_min": r.precio_min,
                "precio_max": r.precio_max,
            }
            for r in resultado
        ]


# TEST del módulo
if __name__ == "__main__":
    print("=" * 60)
    print("TEST DATABASE OPERATIONS")
    print("=" * 60)

    # Crear base de datos de prueba
    db = Database("test_database.db")

    # Test 1: Insertar productos
    print("\n1. Insertando productos de prueba...")
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
        },
        {
            "timestamp": datetime.now(),
            "fuente": "PreciosClaros",
            "categoria": "arroz",
            "nombre": "Arroz Gallo Oro 1kg",
            "marca": "Gallo Oro",
            "precio": 1200.0,
            "precio_min": 1200.0,
            "precio_max": 1250.0,
            "presentacion": "1 kg",
            "ean": "7790123456789",
            "sucursales_disponibles": 8,
            "lat": -34.6037,
            "lng": -58.3816,
        },
    ]

    from datetime import datetime

    db.guardar_productos(productos_prueba)

    # Test 2: Obtener últimos productos
    print("\n2. Obteniendo últimos productos...")
    ultimos = db.obtener_ultimos_productos(5)
    for prod in ultimos:
        print(f"   - {prod.nombre[:40]} | ${prod.precio}")

    # Test 3: Estadísticas generales
    print("\n3. Estadísticas generales:")
    stats = db.obtener_estadisticas_generales()
    print(f"   Total productos: {stats['total_productos']}")
    print(f"   Categorías: {stats['categorias']}")

    # Test 4: Estadísticas por categoría
    print("\n4. Estadísticas por categoría:")
    stats_cat = db.obtener_estadisticas_por_categoria()
    for cat in stats_cat:
        print(
            f"   {cat['categoria']}: {cat['cantidad']} productos, promedio ${cat['precio_promedio']}"
        )

    print("\n" + "=" * 60)
    print("Tests completados")

