import sys
from pathlib import Path
from datetime import datetime

# Setup path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.scrapers.precios_claro import PreciosClarosScraper
from src.utils.paths import init_directories
from src.database import Database
import config


def ejecutar_pipeline(categorias=None, limit=None):
    """Ejecuta el pipeline completo: scraping + guardado en DB"""

    print("=" * 70)
    print("PRICE MONITOR - PIPELINE DE RECOLECCIÓN")
    print("=" * 70)
    print(f"Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Inicializar
    init_directories()

    # 1. Scraping
    print("1. SCRAPING DE DATOS")
    print("-" * 70)

    scraper = PreciosClarosScraper(ubicacion="CABA")

    # Usar valores por defecto del config
    if categorias is None:
        categorias = config.CATEGORIAS_PRODUCTOS
    if limit is None:
        limit = config.LIMITE_PRODUCTOS_POR_CATEGORIA

    print(f"Categorías a buscar ({len(categorias)}): {', '.join(categorias[:5])}...")
    if len(categorias) > 5:
        print(f"  ... y {len(categorias) - 5} más")
    print(f"Límite por categoría: {limit}\n")

    productos = scraper.buscar_productos(categorias, limit=limit)

    # Filtrar productos con precios absurdos Y palabras problemáticas
    productos_antes = len(productos)

    productos_filtrados = []
    for p in productos:
        # Filtro 1: Precio máximo
        if p["precio"] >= 50000:
            continue

        # Filtro 2: Palabras contradictorias por categoría
        nombre_lower = p["nombre"].lower()

        # Si es categoría azúcar, excluir "sin azúcar"
        if p["categoria"] in ["azucar", "azucar comun", "azucar blanca"]:
            if (
                "sin azucar" in nombre_lower
                or "sin azúcar" in nombre_lower
                or "0%" in nombre_lower
            ):
                continue

        productos_filtrados.append(p)

    productos = productos_filtrados
    productos_despues = len(productos)

    if productos_antes != productos_despues:
        print(
            f"\nFiltrados {productos_antes - productos_despues} productos no relevantes"
        )
        print(f"\nTotal obtenido: {len(productos)} productos")

    # 2. Guardar en base de datos
    print("\n2. GUARDANDO EN BASE DE DATOS")
    print("-" * 70)

    db = Database("price_monitor.db")
    exito = db.guardar_productos(productos)

    if not exito:
        print("Error guardando en base de datos")
        return

    # 3. Backup en CSV
    print("\n3. BACKUP EN CSV")
    print("-" * 70)
    scraper.guardar_csv_backup(productos)

    # 4. Mostrar estadísticas
    print("\n4. ESTADÍSTICAS ACTUALES")
    print("-" * 70)

    stats = db.obtener_estadisticas_generales()
    print(f"Total productos en DB: {stats['total_productos']}")
    print(f"Categorías únicas: {len(stats['categorias'])}")
    print(f"Fuentes: {', '.join(stats['fuentes_productos'])}")

    if stats["primera_fecha"]:
        print(
            f"Primera recolección: {stats['primera_fecha'].strftime('%Y-%m-%d %H:%M')}"
        )
    if stats["ultima_fecha"]:
        print(f"Última recolección: {stats['ultima_fecha'].strftime('%Y-%m-%d %H:%M')}")

    # Estadísticas por categoría
    print("\nEstadísticas por categoría:")
    stats_cat = db.obtener_estadisticas_por_categoria()
    for cat in stats_cat:
        print(
            f"  {cat['categoria']:20} | "
            f"Cantidad: {cat['cantidad']:3} | "
            f"Promedio: ${cat['precio_promedio']:7.2f} | "
            f"Min: ${cat['precio_min']:7.2f} | "
            f"Max: ${cat['precio_max']:7.2f}"
        )

    # 5. Análisis avanzado (DENTRO de la función)
    print("\n5. ANÁLISIS AVANZADO")
    print("-" * 70)

    from src.utils.analysis import calcular_costo_canasta_basica, estadisticas_por_grupo

    # Canasta básica
    canasta = calcular_costo_canasta_basica(db)

    # Estadísticas por grupo
    stats_grupos = estadisticas_por_grupo(db)

    # FIN - esto cierra la función
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETADO EXITOSAMENTE")
    print(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    try:
        """
        ejecutar_pipeline(
            categorias=[
                "leche entera",
                "arroz largo fino",
                "arroz blanco 0000",
                "arroz grano largo",
            ],
            limit=10,
        )
        """
        ejecutar_pipeline()
    except KeyboardInterrupt:
        print("\n\nPipeline interrumpido por el usuario.")
    except Exception as e:
        print(f"\n\nERROR FATAL: {e}")
        import traceback

        traceback.print_exc()
