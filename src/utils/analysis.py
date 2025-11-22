"""
Utilidades para análisis de productos
"""

from pathlib import Path
import sys

# Setup imports
try:
    import config
except ImportError:
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    import config

from src.database import Database


def filtrar_productos_invalidos(productos):
    """
    Filtra productos que no coincidan con lo esperado para cada categoría
    """
    # Palabras a excluir POR CATEGORÍA
    filtros_por_categoria = {
        "arroz blanco": [
            "alfajor",
            "chocolate",
            "barra",
            "snack",
            "cereal",
            "galletita",
        ],
        "arroz grano largo": [
            "alfajor",
            "chocolate",
            "barra",
            "snack",
            "cereal",
            "galletita",
        ],
        "leche entera": ["acondicionador", "shampoo", "dulce de leche", "crema"],
        "leche descremada": ["acondicionador", "shampoo", "dulce de leche", "crema"],
        "aceite girasol": ["aceite esencial", "aceite motor"],
        "yogur": ["yogurisimo"],  # Si querés excluir bebidas lácteas
        # Agregar más según necesites
    }

    productos_validos = []
    productos_filtrados = []

    for prod in productos:
        categoria = prod["categoria"]
        nombre_lower = prod["nombre"].lower()

        # Obtener palabras a excluir para esta categoría
        palabras_excluir = filtros_por_categoria.get(categoria, [])

        # Verificar si contiene palabras a excluir
        es_valido = True
        for palabra in palabras_excluir:
            if palabra in nombre_lower:
                es_valido = False
                productos_filtrados.append(
                    {
                        "categoria": categoria,
                        "nombre": prod["nombre"],
                        "razon": f"Contiene '{palabra}'",
                    }
                )
                break

        if es_valido:
            productos_validos.append(prod)

    # Mostrar resumen de filtrado
    if productos_filtrados:
        print(f"\nProductos filtrados: {len(productos_filtrados)}")
        # Agrupar por categoría
        from collections import Counter

        por_categoria = Counter(p["categoria"] for p in productos_filtrados)
        for cat, count in por_categoria.items():
            print(f"  {cat}: {count} productos")

    return productos_validos


def calcular_costo_canasta_basica(db):
    """
    Calcula el costo de la canasta básica usando el producto más barato de cada categoría
    """
    from sqlalchemy import func
    from src.database.models import Producto

    print("\nCANASTA BÁSICA")
    print("-" * 70)

    costo_total = 0
    productos_canasta = []

    for categoria in config.CANASTA_BASICA:
        # Obtener el producto más barato de esta categoría
        producto = (
            db.session.query(Producto)
            .filter(Producto.categoria == categoria)
            .order_by(Producto.precio.asc())
            .first()
        )

        if producto:
            productos_canasta.append(
                {
                    "categoria": categoria,
                    "nombre": producto.nombre,
                    "marca": producto.marca,
                    "precio": producto.precio,
                    "presentacion": producto.presentacion,
                }
            )
            costo_total += producto.precio
        else:
            print(f"  ADVERTENCIA: No hay datos para '{categoria}'")

    # Mostrar resultados
    print(f"\nProductos en canasta ({len(productos_canasta)} items):\n")
    for item in productos_canasta:
        print(
            f"  {item['categoria']:20} | {item['nombre'][:35]:35} | ${item['precio']:7.2f}"
        )

    print(f"\n{'COSTO TOTAL':56} | ${costo_total:7.2f}")
    print("-" * 70)

    return {"productos": productos_canasta, "costo_total": costo_total}


def estadisticas_por_grupo(db):
    """
    Agrupa estadísticas por los grupos definidos en CATEGORIAS_AGRUPADAS
    """
    from sqlalchemy import func
    from src.database.models import Producto

    print("\nESTADÍSTICAS POR GRUPO")
    print("-" * 70)

    resultados = {}

    for grupo, categorias in config.CATEGORIAS_AGRUPADAS.items():
        # Obtener productos de este grupo
        stats = (
            db.session.query(
                func.count(Producto.id).label("cantidad"),
                func.avg(Producto.precio).label("promedio"),
                func.min(Producto.precio).label("minimo"),
                func.max(Producto.precio).label("maximo"),
            )
            .filter(Producto.categoria.in_(categorias))
            .first()
        )

        if stats and stats.cantidad > 0:
            resultados[grupo] = {
                "cantidad": stats.cantidad,
                "promedio": round(stats.promedio, 2),
                "minimo": stats.minimo,
                "maximo": stats.maximo,
            }

            print(f"\n{grupo}:")
            print(f"  Productos: {stats.cantidad}")
            print(f"  Promedio: ${stats.promedio:.2f}")
            print(f"  Rango: ${stats.minimo:.2f} - ${stats.maximo:.2f}")

    return resultados


def productos_mas_baratos_por_categoria(db, categorias=None):
    """
    Muestra el producto más barato de cada categoría
    Útil para armar la "lista de compras inteligente"
    """
    from src.database.models import Producto

    if categorias is None:
        categorias = config.CATEGORIAS_PRODUCTOS

    print("\nPRODUCTOS MÁS BARATOS POR CATEGORÍA")
    print("-" * 70)

    resultados = []

    for categoria in categorias:
        producto = (
            db.session.query(Producto)
            .filter(Producto.categoria == categoria)
            .order_by(Producto.precio.asc())
            .first()
        )

        if producto:
            resultados.append(
                {
                    "categoria": categoria,
                    "nombre": producto.nombre,
                    "marca": producto.marca,
                    "precio": producto.precio,
                    "sucursales": producto.sucursales_disponibles,
                }
            )
            print(
                f"{categoria:20} | {producto.nombre[:30]:30} | ${producto.precio:7.2f} | {producto.sucursales_disponibles} sucursales"
            )

    return resultados


# TEST
if __name__ == "__main__":
    print("=" * 70)
    print("TEST DE ANÁLISIS")
    print("=" * 70)

    db = Database("price_monitor.db")

    # Test 1: Canasta básica
    canasta = calcular_costo_canasta_basica(db)

    # Test 2: Estadísticas por grupo
    stats_grupos = estadisticas_por_grupo(db)

    # Test 3: Productos más baratos
    mas_baratos = productos_mas_baratos_por_categoria(db, config.CANASTA_BASICA)

    print("\n" + "=" * 70)
    print("Tests completados")
