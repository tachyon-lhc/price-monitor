import sys
from pathlib import Path

# Agregar la raíz del proyecto al PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Ahora sí importar
from src.scrapers.precios_claro import PreciosClarosScraper
from src.utils.paths import init_directories

if __name__ == "__main__":
    print("=" * 70)
    print("TEST DE SCRAPER")
    print("=" * 70)

    # Inicializar directorios
    init_directories()

    # Crear scraper - CAMBIADO ACÁ
    scraper = PreciosClarosScraper(ubicacion="MAR_DEL_PLATA")  # <-- Ahora usa ubicacion

    # Buscar productos
    productos = scraper.buscar_productos(["leche", "arroz"], limit=5)

    if productos:
        print(f"\nTotal: {len(productos)} productos")
        for prod in productos[:3]:
            print(f"\n- {prod['nombre']}")
            print(f"  Precio: ${prod['precio']:.2f}")

        scraper.guardar_csv_backup(productos)

    print("\nTest completado")

