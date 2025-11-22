from pathlib import Path

# Obtener la raíz del proyecto (donde está el README)
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BACKUPS_DIR = DATA_DIR / "backups"
EXPORTS_DIR = DATA_DIR / "exports"
LOGS_DIR = PROJECT_ROOT / "logs"


# Crear directorios si no existen
def init_directories():
    """Inicializa la estructura de directorios"""
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
