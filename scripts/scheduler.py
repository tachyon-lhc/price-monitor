import sys
from pathlib import Path
from datetime import datetime
import time

# Setup path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

# Importar el pipeline
from run_pipeline import ejecutar_pipeline

# Configurar logging
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            log_dir / f"scheduler_{datetime.now().strftime('%Y%m')}.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def job_diario():
    """Job que se ejecuta automáticamente cada día"""
    logger.info("=" * 80)
    logger.info("INICIANDO RECOLECCIÓN PROGRAMADA")
    logger.info("=" * 80)

    try:
        ejecutar_pipeline()
        logger.info("Recolección completada exitosamente")
    except Exception as e:
        logger.error(f"Error durante la recolección: {e}", exc_info=True)

    logger.info("=" * 80 + "\n")


def main():
    """Inicia el scheduler"""
    print("=" * 80)
    print("PRICE MONITOR - SCHEDULER AUTOMÁTICO")
    print("=" * 80)
    print("\nEl sistema recolectará datos automáticamente todos los días.")
    print("Logs guardados en: logs/")
    print("\nPresiona Ctrl+C para detener\n")
    print("=" * 80)

    # Crear scheduler
    scheduler = BlockingScheduler()

    # Configurar ejecución diaria a las 8:00 AM
    scheduler.add_job(
        job_diario,
        CronTrigger(hour=8, minute=0),
        id="recoleccion_diaria",
        name="Recolección diaria de precios",
        replace_existing=True,
    )

    # Mostrar info
    # DESPUÉS:
    logger.info("Scheduler iniciado")
    jobs = scheduler.get_jobs()
    if jobs:
        logger.info(f"Jobs programados: {len(jobs)}")
        logger.info(f"  - {jobs[0].name}")
    logger.info("Frecuencia: Diaria a las 8:00 AM")

    # Preguntar si ejecutar ahora
    respuesta = input(
        "\n¿Ejecutar recolección AHORA antes de iniciar el scheduler? (s/n): "
    ).lower()
    if respuesta == "s":
        logger.info("\nEjecutando recolección inmediata...")
        job_diario()

    print("\n" + "=" * 80)
    print("Scheduler activo. Esperando próxima ejecución...")
    print("=" * 80 + "\n")

    # Iniciar scheduler
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("\n\nScheduler detenido por el usuario")
        print("\n" + "=" * 80)
        print("SCHEDULER DETENIDO")
        print("=" * 80)


if __name__ == "__main__":
    main()

