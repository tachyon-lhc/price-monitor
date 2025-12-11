# config.py
"""
Configuración del proyecto Price Monitor
"""

# Coordenadas para búsqueda
COORDENADAS = {
    "CABA": {"lat": -34.6037, "lng": -58.3816},
    "MAR_DEL_PLATA": {"lat": -38.0055, "lng": -57.5426},
}

# Categorías ESPECÍFICAS para evitar ruido
CATEGORIAS_PRODUCTOS = [
    # Lácteos
    "leche entera",
    "leche descremada",
    "yogur",
    "queso cremoso",
    # Almacén básico
    "arroz grano largo 1kg",
    "arroz doble carolina",
    "arroz blanco 0000",
    "arroz largo fino",
    "fideos guiseros",
    "aceite girasol 900",
    "aceite girasol",
    "azucar",
    "harina 0000",
    "harina 000",
    "sal fina",
    "sal gruesa",
    # Infusiones
    "yerba mate",
    "cafe molido",
    "te saquitos",
    "te hebras",
    # Conservas
    "tomate triturado",
    "atun",
    # Proteínas
    "hamburguesas carne",
    # Limpieza
    "detergente",
    "lavandina",
    "jabon tocador",
    "jabon liquido",
]

# Límites de scraping
LIMITE_PRODUCTOS_POR_CATEGORIA = 30

# Configuración de la API
API_TIMEOUT = 15  # segundos

# === NUEVA SECCIÓN: Configuración de análisis ===

# Canasta básica para análisis
CANASTA_BASICA = [
    "leche entera",
    "arroz largo fino",
    "aceite girasol",
    "azucar",
    "yerba mate",
    "fideos guiseros",
    "harina 0000",
    "hamburguesas carne",
]

CANTIDADES_CANASTA = {
    "leche entera": 3,
    "arroz largo fino": 4,
    "aceite girasol": 1,
    "azucar": 2,
    "yerba mate": 1,
    "fideos guiseros": 3,
    "harina 0000": 2,
    "hamburguesas carne": 1,
}

# Categorías por tipo (para agrupación en análisis)
CATEGORIAS_AGRUPADAS = {
    "Lácteos": ["leche entera", "leche descremada", "yogur", "queso cremoso"],
    "Almacén": [
        "arroz largo fino",
        "fideos guiseros",
        "aceite girasol",
        "azucar",
        "harina 0000",
        "sal fina",
    ],
    "Infusiones": ["yerba mate", "cafe molido", "te negro"],
    "Conservas": ["tomate triturado", "atun lata"],
    "Proteínas": ["huevos", "pollo entero"],
    "Limpieza": ["detergente", "lavandina"],
}
