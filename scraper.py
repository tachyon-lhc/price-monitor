import requests
from datetime import datetime
import pandas as pd
import os


class PreciosClarosScraper:
    """Scraper para Precios Claros (Argentina)"""

    def __init__(self, lat=-34.6037, lng=-58.3816):
        """
        lat, lng: Coordenadas (por defecto CABA)
        Para Mar del Plata: lat=-38.0055, lng=-57.5426
        """
        self.base_url = "https://d3e6htiiul5ek9.cloudfront.net/prod"
        self.lat = lat
        self.lng = lng
        self.nombre = "PreciosClaros"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Referer": "https://www.preciosclaros.gob.ar/",
        }

    def buscar_productos(self, terminos=["leche", "arroz", "aceite"], limit=20):
        """Busca múltiples productos"""
        todos_productos = []

        for termino in terminos:
            print(f"🔍 Buscando: {termino}...")
            productos = self._buscar_un_producto(termino, limit)
            todos_productos.extend(productos)

        print(f"✓ Total de productos obtenidos: {len(todos_productos)}")
        return todos_productos

    def _buscar_un_producto(self, termino, limit=20):
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
                url, params=params, headers=self.headers, timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                productos = data.get("productos", [])

                # Transformar a formato estándar
                productos_limpios = []
                for prod in productos:
                    # Usar precioMin como precio principal
                    precio_min = prod.get("precioMin", 0)
                    precio_max = prod.get("precioMax", 0)

                    # Solo agregar si tiene precio válido
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
                                "precio": float(precio_min),  # Para compatibilidad
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
                print(f"  ✗ Error HTTP {response.status_code}")
                return []

        except Exception as e:
            print(f"  ✗ Error: {e}")
            return []

    def guardar_csv_backup(self, datos):
        """Guarda backup en CSV"""
        if datos:
            os.makedirs("data", exist_ok=True)
            df = pd.DataFrame(datos)
            filename = (
                f"data/precios_claros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            df.to_csv(filename, index=False)
            print(f"✓ Backup guardado: {filename}")


class DolarScraper:
    """Scraper para cotizaciones de dólar"""

    def __init__(self):
        self.base_url = "https://dolarapi.com/v1"
        self.nombre = "DolarAPI"

    def obtener_cotizaciones(self):
        """Obtiene todas las cotizaciones de dólar"""
        try:
            response = requests.get(f"{self.base_url}/dolares", timeout=10)

            if response.status_code == 200:
                data = response.json()

                cotizaciones = []
                for dolar in data:
                    cotizaciones.append(
                        {
                            "timestamp": datetime.now(),
                            "fuente": self.nombre,
                            "nombre": dolar["nombre"],
                            "precio_compra": float(dolar["compra"]),
                            "precio_venta": float(dolar["venta"]),
                            "moneda": "USD",
                            "fecha_actualizacion": dolar.get("fechaActualizacion", ""),
                        }
                    )

                print(f"✓ Obtenidas {len(cotizaciones)} cotizaciones de dólar")
                return cotizaciones
            else:
                print(f"✗ Error HTTP: {response.status_code}")
                return []

        except Exception as e:
            print(f"✗ Error scrapeando dólar: {e}")
            return []

    def guardar_csv_backup(self, datos):
        """Guarda backup en CSV"""
        if datos:
            os.makedirs("data", exist_ok=True)
            df = pd.DataFrame(datos)
            filename = f"data/dolar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            print(f"✓ Backup guardado: {filename}")


class MercadoLibreScraper:
    """Scraper para MercadoLibre Argentina vía API oficial"""

    def __init__(self):
        self.base_url = "https://api.mercadolibre.com"
        self.nombre = "MercadoLibre"

    def buscar_productos(self, terminos=["aceite", "arroz"], limit=10):
        """Busca productos en MercadoLibre"""
        todos_productos = []

        for termino in terminos:
            print(f"🔍 Buscando en ML: {termino}...")
            productos = self._buscar_un_producto(termino, limit)
            todos_productos.extend(productos)

        print(f"✓ Total obtenidos de ML: {len(todos_productos)}")
        return todos_productos

    def _buscar_un_producto(self, termino, limit=10):
        """Busca usando la API oficial de MercadoLibre"""
        url = f"{self.base_url}/sites/MLA/search"

        params = {
            "q": termino,
            "limit": limit,
            "category": "MLA1403",  # Alimentos y Bebidas
        }

        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                productos = data.get("results", [])

                productos_limpios = []
                for prod in productos:
                    precio = prod.get("price", 0)

                    if precio > 0:
                        productos_limpios.append(
                            {
                                "timestamp": datetime.now(),
                                "fuente": self.nombre,
                                "categoria": termino,
                                "nombre": prod.get("title", ""),
                                "precio": float(precio),
                                "moneda": prod.get("currency_id", "ARS"),
                                "vendedor": prod.get("seller", {}).get("nickname", ""),
                                "link": prod.get("permalink", ""),
                                "condicion": prod.get("condition", ""),
                                "stock": prod.get("available_quantity", 0),
                            }
                        )

                return productos_limpios
            else:
                print(f"  ✗ Error: {response.status_code}")
                return []

        except Exception as e:
            print(f"  ✗ Error: {e}")
            return []

    def guardar_csv_backup(self, datos):
        """Guarda backup en CSV"""
        if datos:
            os.makedirs("data", exist_ok=True)
            df = pd.DataFrame(datos)
            filename = (
                f"data/mercadolibre_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            df.to_csv(filename, index=False)
            print(f"✓ Backup guardado: {filename}")


# TESTS
if __name__ == "__main__":
    print("=" * 70)
    print(" PRICE MONITOR - TEST DE SCRAPERS ".center(70))
    print("=" * 70)

    # Test 1: Precios Claros
    print("\n### TEST 1: PRECIOS CLAROS ###\n")
    pc_scraper = PreciosClarosScraper(lat=-34.6037, lng=-58.3816)
    productos_pc = pc_scraper.buscar_productos(["leche", "arroz", "aceite"], limit=10)

    if productos_pc:
        print(f"\n📊 Muestra de productos (primeros 5 de {len(productos_pc)}):")
        for prod in productos_pc[:5]:
            print(f"\n• {prod['nombre']}")
            print(f"  Marca: {prod['marca']}")
            print(
                f"  Precio Min: ${prod['precio_min']:.2f} | Max: ${prod['precio_max']:.2f}"
            )
            print(f"  Presentación: {prod['presentacion']}")
            print(f"  Sucursales: {prod['sucursales_disponibles']}")

        pc_scraper.guardar_csv_backup(productos_pc)

    # Test 2: Dólar
    print("\n\n### TEST 2: COTIZACIONES DÓLAR ###\n")
    dolar_scraper = DolarScraper()
    cotizaciones = dolar_scraper.obtener_cotizaciones()

    if cotizaciones:
        print("\n💵 Cotizaciones actuales:")
        for cot in cotizaciones:
            spread = cot["precio_venta"] - cot["precio_compra"]
            print(
                f"  {cot['nombre']:15} | Compra: ${cot['precio_compra']:7.2f} | Venta: ${cot['precio_venta']:7.2f} | Spread: ${spread:.2f}"
            )

        dolar_scraper.guardar_csv_backup(cotizaciones)

    # Test 3: MercadoLibre
    print("\n\n### TEST 3: MERCADOLIBRE ###\n")
    ml_scraper = MercadoLibreScraper()
    productos_ml = ml_scraper.buscar_productos(["aceite comestible", "arroz"], limit=5)

    if productos_ml:
        print(f"\n📦 Productos en ML (primeros 5 de {len(productos_ml)}):")
        for prod in productos_ml[:5]:
            print(f"\n• {prod['nombre'][:60]}...")
            print(f"  Precio: ${prod['precio']:.2f}")
            print(f"  Vendedor: {prod['vendedor']}")
            print(f"  Stock: {prod['stock']}")

        ml_scraper.guardar_csv_backup(productos_ml)

    # Resumen
    print("\n\n" + "=" * 70)
    print(" RESUMEN ".center(70))
    print("=" * 70)
    print(f"✓ Precios Claros: {len(productos_pc)} productos")
    print(f"✓ Dólar: {len(cotizaciones)} cotizaciones")
    print(f"✓ MercadoLibre: {len(productos_ml)} productos")
    print(
        f"✓ TOTAL: {len(productos_pc) + len(cotizaciones) + len(productos_ml)} registros"
    )
    print("=" * 70)

