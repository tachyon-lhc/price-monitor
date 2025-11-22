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
    "fideos",
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
    # Panificados
    "pan lactal",
    "pan rallado",
    # Conservas
    "tomate triturado",
    "atun",
    # Proteínas
    "huevos",
    "pollo entero",
    "pollo pechuga",
    "pollo pata entera",
    # Limpieza
    "detergente",
    "lavandina",
    "jabon tocador",
    "jabon liquido",
]

# Límites de scraping
LIMITE_PRODUCTOS_POR_CATEGORIA = 20

# Configuración de la API
API_TIMEOUT = 15  # segundos

# === NUEVA SECCIÓN: Configuración de análisis ===

# Canasta básica para análisis
CANASTA_BASICA = [
    "leche entera",
    "arroz blanco",
    "aceite girasol",
    "azucar",
    "yerba mate",
    "pan lactal",
    "fideos secos",
    "harina 0000",
]

# Categorías por tipo (para agrupación en análisis)
CATEGORIAS_AGRUPADAS = {
    "Lácteos": ["leche entera", "leche descremada", "yogur", "queso cremoso"],
    "Almacén": [
        "arroz blanco",
        "fideos secos",
        "aceite girasol",
        "azucar",
        "harina 0000",
        "sal fina",
    ],
    "Infusiones": ["yerba mate", "cafe molido", "te negro"],
    "Panificados": ["pan lactal", "pan rallado"],
    "Conservas": ["tomate triturado", "atun lata"],
    "Proteínas": ["huevos", "pollo"],
    "Limpieza": ["detergente", "lavandina"],
}
