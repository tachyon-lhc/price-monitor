import requests
from datetime import datetime
import pandas as pd
from pathlib import Path

# Imports del proyecto
try:
    from ..utils.paths import BACKUPS_DIR, init_directories
    import config
except ImportError:
    import sys

    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from src.utils.paths import BACKUPS_DIR, init_directories
    import config

# Extraer configuración
COORDENADAS = config.COORDENADAS
CATEGORIAS_PRODUCTOS = config.CATEGORIAS_PRODUCTOS
LIMITE_PRODUCTOS_POR_CATEGORIA = config.LIMITE_PRODUCTOS_POR_CATEGORIA
API_TIMEOUT = config.API_TIMEOUT

init_directories()


class PreciosClarosScraper:
    """Scraper para Precios Claros (Argentina)"""

    def __init__(self, ubicacion="CABA"):
        """
        ubicacion: Clave en COORDENADAS ('CABA', 'MAR_DEL_PLATA')
        """
        if ubicacion not in COORDENADAS:
            raise ValueError(
                f"Ubicación '{ubicacion}' no válida. Opciones: {list(COORDENADAS.keys())}"
            )

        coords = COORDENADAS[ubicacion]
        self.lat = coords["lat"]
        self.lng = coords["lng"]
        self.base_url = "https://d3e6htiiul5ek9.cloudfront.net/prod"
        self.nombre = "PreciosClaros"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://www.preciosclaros.gob.ar/",
        }

    def buscar_productos(self, terminos=None, limit=None):
        """Busca múltiples productos"""
        if terminos is None:
            terminos = CATEGORIAS_PRODUCTOS
        if limit is None:
            limit = LIMITE_PRODUCTOS_POR_CATEGORIA

        todos_productos = []

        for termino in terminos:
            print(f"Buscando: {termino}...")
            productos = self._buscar_un_producto(termino, limit)
            todos_productos.extend(productos)

        print(f"Total de productos obtenidos: {len(todos_productos)}")
        return todos_productos

    def _buscar_un_producto(self, termino, limit):
        """Busca un solo término"""
        url = f"{self.base_url}/productos"

        params = {
            "limit": limit,
            "offset": 0,
            "string": termino,
            "lat": self.lat,
            "lng": self.lng,
        }

        try:
            response = requests.get(
                url, params=params, headers=self.headers, timeout=API_TIMEOUT
            )

            if response.status_code == 200:
                data = response.json()
                productos = data.get("productos", [])

                productos_limpios = []
                for prod in productos:
                    precio_min = prod.get("precioMin", 0)
                    precio_max = prod.get("precioMax", 0)

                    if precio_min > 0:
                        productos_limpios.append(
                            {
                                "timestamp": datetime.now(),
                                "fuente": self.nombre,
                                "categoria": termino,
                                "nombre": prod.get("nombre", ""),
                                "marca": prod.get("marca", ""),
                                "precio_min": float(precio_min),
                                "precio_max": float(precio_max),
                                "precio": float(precio_min),
                                "presentacion": prod.get("presentacion", ""),
                                "ean": prod.get("id", ""),
                                "sucursales_disponibles": prod.get(
                                    "cantSucursalesDisponible", 0
                                ),
                                "lat": self.lat,
                                "lng": self.lng,
                            }
                        )

                return productos_limpios
            else:
                print(f"Error HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"Error: {e}")
            return []

    def guardar_csv_backup(self, datos):
        """Guarda backup en CSV"""
        if datos:
            df = pd.DataFrame(datos)
            filename = (
                BACKUPS_DIR
                / f"precios_claros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            df.to_csv(filename, index=False)
            print(f"Backup guardado: {filename}")


if __name__ == "__main__":
    print("=" * 70)
    print("PRICE MONITOR - TEST DE SCRAPER")
    print("=" * 70)

    scraper = PreciosClarosScraper(ubicacion="MAR_DEL_PLATA")
    productos = scraper.buscar_productos(["leche", "arroz"], limit=5)

    if productos:
        print(f"\nProductos obtenidos: {len(productos)}")
        for prod in productos[:3]:
            print(f"\n- {prod['nombre']}")
            print(f"  Precio: ${prod['precio']:.2f}")

        scraper.guardar_csv_backup(productos)

