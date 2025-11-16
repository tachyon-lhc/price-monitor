from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import os

from scraper import PreciosClarosScraper, DolarScraper
from database import Database

# Configurar logging
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"logs/monitor_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def job_recolectar_datos():
    """Job principal que se ejecuta periódicamente"""
    logger.info("=" * 70)
    logger.info("🚀 INICIANDO RECOLECCIÓN DE DATOS")
    logger.info("=" * 70)

    inicio = datetime.now()

    try:
        # Inicializar base de datos
        db = Database("price_monitor.db")

        # === PARTE 1: Cotizaciones de Dólar ===
        logger.info("\n📊 Obteniendo cotizaciones de dólar...")
        dolar_scraper = DolarScraper()
        cotizaciones = dolar_scraper.obtener_cotizaciones()

        if cotizaciones:
            db.guardar_cotizaciones(cotizaciones)
            dolar_scraper.guardar_csv_backup(cotizaciones)
            logger.info(f"✓ Dólar: {len(cotizaciones)} cotizaciones guardadas")
        else:
            logger.warning("⚠ No se obtuvieron cotizaciones de dólar")

        # === PARTE 2: Productos de Supermercados ===
        logger.info("\n🛒 Obteniendo productos de supermercados...")

        # Productos básicos a monitorear
        categorias = [
            "leche",
            "arroz",
            "aceite",
            "azucar",
            "harina",
            "fideos",
            "yerba",
            "cafe",
        ]

        pc_scraper = PreciosClarosScraper(lat=-34.6037, lng=-58.3816)
        productos = pc_scraper.buscar_productos(categorias, limit=15)

        if productos:
            db.guardar_productos(productos)
            pc_scraper.guardar_csv_backup(productos)
            logger.info(f"✓ Productos: {len(productos)} items guardados")
        else:
            logger.warning("⚠ No se obtuvieron productos")

        # === RESUMEN ===
        duracion = (datetime.now() - inicio).total_seconds()
        total_registros = len(cotizaciones) + len(productos)

        logger.info("\n" + "=" * 70)
        logger.info("📈 RESUMEN DE RECOLECCIÓN")
        logger.info("=" * 70)
        logger.info(f"  • Cotizaciones: {len(cotizaciones)}")
        logger.info(f"  • Productos: {len(productos)}")
        logger.info(f"  • Total: {total_registros} registros")
        logger.info(f"  • Duración: {duracion:.2f} segundos")
        logger.info("=" * 70)

        # Mostrar estadísticas de la DB
        stats = db.obtener_estadisticas_generales()
        logger.info("\n📊 ESTADÍSTICAS GENERALES DE LA BASE DE DATOS")
        logger.info(f"  • Total productos históricos: {stats['total_productos']}")
        logger.info(f"  • Total cotizaciones históricas: {stats['total_cotizaciones']}")
        if stats["primera_fecha"]:
            logger.info(
                f"  • Primera fecha de datos: {stats['primera_fecha'].strftime('%Y-%m-%d %H:%M')}"
            )
        if stats["ultima_fecha"]:
            logger.info(
                f"  • Última actualización: {stats['ultima_fecha'].strftime('%Y-%m-%d %H:%M')}"
            )

        logger.info("\n✅ Recolección completada exitosamente")

    except Exception as e:
        logger.error(f"\n❌ ERROR durante la recolección: {e}", exc_info=True)

    logger.info("=" * 70 + "\n")


def ejecutar_una_vez():
    """Ejecuta el job una sola vez (útil para testing)"""
    logger.info("🔧 MODO TEST: Ejecutando una sola vez")
    job_recolectar_datos()
    logger.info(
        "\n✓ Ejecución única completada. Para ejecutar automáticamente, usa: python scheduler.py"
    )


def ejecutar_automatico():
    """Ejecuta el scheduler en modo automático"""
    logger.info("=" * 70)
    logger.info("🚀 PRICE MONITOR - MODO AUTOMÁTICO".center(70))
    logger.info("=" * 70)
    logger.info("\nPresiona Ctrl+C para detener\n")

    # Crear carpetas necesarias
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Ejecutar inmediatamente la primera vez
    logger.info("⏳ Ejecutando primera recolección...")
    job_recolectar_datos()

    # Configurar scheduler
    scheduler = BlockingScheduler()

    # OPCIÓN 1: Ejecutar cada 6 horas (4 veces al día)
    scheduler.add_job(
        job_recolectar_datos,
        CronTrigger(hour="6,12,18,23", minute=0),
        id="recolectar_datos",
        name="Recolección de precios y cotizaciones",
        replace_existing=True,
    )

    # OPCIÓN 2: Para testing, ejecutar cada 30 minutos
    # Descomenta esto si querés probar más seguido:
    # scheduler.add_job(
    #     job_recolectar_datos,
    #     'interval',
    #     minutes=30,
    #     id='recolectar_datos',
    #     name='Recolección de prueba cada 30 min'
    # )

    logger.info("\n⏰ SCHEDULER CONFIGURADO:")
    logger.info("  • Frecuencia: 6am, 12pm, 6pm, 11pm")
    logger.info("  • Próxima ejecución: " + str(scheduler.get_jobs()[0].next_run_time))
    logger.info("  • Logs guardados en: logs/")
    logger.info("  • Base de datos: price_monitor.db")
    logger.info("  • Backups CSV: data/")
    logger.info("\n" + "=" * 70 + "\n")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n\n" + "=" * 70)
        logger.info("👋 DETENIENDO PRICE MONITOR")
        logger.info("=" * 70)
        logger.info("  • Scheduler detenido correctamente")
        logger.info("  • Todos los datos han sido guardados")
        logger.info("=" * 70 + "\n")


def mostrar_menu():
    """Muestra menú de opciones"""
    print("\n" + "=" * 70)
    print("PRICE MONITOR - Sistema de Monitoreo de Precios".center(70))
    print("=" * 70)
    print("\n¿Qué deseas hacer?\n")
    print("  1. Ejecutar UNA VEZ (para testing)")
    print("  2. Ejecutar AUTOMÁTICAMENTE (cada 6 horas)")
    print("  3. Ver estadísticas de la base de datos")
    print("  4. Salir")
    print("\n" + "=" * 70)

    opcion = input("\nElige una opción (1-4): ").strip()
    return opcion


def ver_estadisticas():
    """Muestra estadísticas de la base de datos"""
    try:
        db = Database("price_monitor.db")
        stats = db.obtener_estadisticas_generales()

        print("\n" + "=" * 70)
        print("📊 ESTADÍSTICAS DE LA BASE DE DATOS".center(70))
        print("=" * 70)
        print(f"\n  📦 Total de productos: {stats['total_productos']}")
        print(f"  💵 Total de cotizaciones: {stats['total_cotizaciones']}")

        if stats["primera_fecha"]:
            print(
                f"\n  📅 Primera recolección: {stats['primera_fecha'].strftime('%Y-%m-%d %H:%M')}"
            )
        if stats["ultima_fecha"]:
            print(
                f"  📅 Última recolección: {stats['ultima_fecha'].strftime('%Y-%m-%d %H:%M')}"
            )

        print("\n  🏪 Fuentes de productos:")
        for fuente in stats["fuentes_productos"]:
            print(f"    • {fuente[0]}")

        print("\n  📋 Categorías monitoreadas:")
        categorias = list(set([cat[0] for cat in stats["categorias"] if cat[0]]))
        for cat in sorted(categorias)[:10]:  # Mostrar primeras 10
            print(f"    • {cat}")

        # Últimas cotizaciones
        print("\n  💰 Últimas cotizaciones del dólar:")
        cotizaciones = db.obtener_comparacion_cotizaciones()
        for cot in cotizaciones[:5]:
            spread = cot.precio_venta - cot.precio_compra
            print(
                f"    • {cot.nombre:20} Venta: ${cot.precio_venta:8.2f}  Spread: ${spread:6.2f}"
            )

        print("\n" + "=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error al obtener estadísticas: {e}\n")


def main():
    """Función principal con menú interactivo"""
    while True:
        opcion = mostrar_menu()

        if opcion == "1":
            ejecutar_una_vez()
            input("\nPresiona Enter para continuar...")

        elif opcion == "2":
            ejecutar_automatico()
            break

        elif opcion == "3":
            ver_estadisticas()
            input("\nPresiona Enter para continuar...")

        elif opcion == "4":
            print("\n👋 ¡Hasta luego!\n")
            break

        else:
            print("\n❌ Opción inválida. Por favor elige 1, 2, 3 o 4.\n")
            input("Presiona Enter para continuar...")


if __name__ == "__main__":
    # Si se ejecuta con argumento --once, ejecutar una vez
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        ejecutar_una_vez()
    else:
        main()
