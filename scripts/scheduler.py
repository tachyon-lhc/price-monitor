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
    # Crear scheduler
    scheduler = BlockingScheduler()

    # Configurar ejecución diaria a las 8:00 AM
    scheduler.add_job(
        job_diario,
        CronTrigger(hour="0,12", minute=0),
        id="recoleccion_12hs",
    )

    # Mostrar info
    logger.info("Scheduler iniciado")
    jobs = scheduler.get_jobs()
    if jobs:
        logger.info(f"Jobs programados: {len(jobs)}")
        logger.info(f"  - {jobs[0].name}")
    logger.info("Frecuencia: Diaria a las 8:00 AM")

    job_diario()

    # Iniciar scheduler
    scheduler.start()


if __name__ == "__main__":
    main()
