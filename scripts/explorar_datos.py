import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import Database
import pandas as pd


def explorar_datos():
    """Exploración interactiva de los datos"""

    db = Database("price_monitor.db")

    print("=" * 80)
    print("EXPLORACIÓN DE DATOS - PRICE MONITOR")
    print("=" * 80)

    # 1. Resumen general
    stats = db.obtener_estadisticas_generales()
    print(f"\nTotal de productos: {stats['total_productos']}")
    print(f"Categorías: {len(stats['categorias'])}")
    print(f"Período: {stats['primera_fecha']} → {stats['ultima_fecha']}")

    # 2. Estadísticas por categoría
    print("\n" + "=" * 80)
    print("ESTADÍSTICAS POR CATEGORÍA")
    print("=" * 80)

    stats_cat = db.obtener_estadisticas_por_categoria()

    df = pd.DataFrame(stats_cat)
    df = df.sort_values("cantidad", ascending=False)

    print(df.to_string(index=False))

    # 3. Detectar categorías problemáticas
    print("\n" + "=" * 80)
    print("CATEGORÍAS CON POSIBLES PROBLEMAS")
    print("=" * 80)

    # Categorías con muy pocos productos
    pocos_productos = df[df["cantidad"] < 5]
    if not pocos_productos.empty:
        print("\nCategorías con < 5 productos (puede necesitar mejor búsqueda):")
        for _, row in pocos_productos.iterrows():
            print(f"  - {row['categoria']}: {row['cantidad']} productos")

    # Categorías con rango de precios muy amplio (puede indicar productos mezclados)
    df["rango"] = df["precio_max"] - df["precio_min"]
    df["rango_relativo"] = (df["rango"] / df["precio_min"] * 100).round(1)

    rango_alto = df[df["rango_relativo"] > 500]  # Más de 500% de diferencia
    if not rango_alto.empty:
        print(
            "\nCategorías con rango de precios muy amplio (puede tener productos incorrectos):"
        )
        for _, row in rango_alto.iterrows():
            print(
                f"  - {row['categoria']}: ${row['precio_min']:.2f} → ${row['precio_max']:.2f} ({row['rango_relativo']}%)"
            )

    # 4. Menú interactivo
    while True:
        print("\n" + "=" * 80)
        print("OPCIONES:")
        print("  1. Ver productos de una categoría específica")
        print("  2. Buscar productos por nombre")
        print("  3. Ver top 10 más caros")
        print("  4. Ver top 10 más baratos")
        print("  5. Exportar todo a CSV")
        print("  0. Salir")
        print("=" * 80)

        opcion = input("\nElige opción: ").strip()

        if opcion == "1":
            print("\nCategorías disponibles:")
            for i, cat in enumerate(stats["categorias"], 1):
                print(f"  {i}. {cat}")

            cat_input = input("\nEscribe el nombre de la categoría: ").strip()

            from src.database.models import Producto

            productos = (
                db.session.query(Producto)
                .filter(Producto.categoria == cat_input)
                .order_by(Producto.precio.asc())
                .all()
            )

            if productos:
                print(f"\n{len(productos)} productos en '{cat_input}':\n")
                for p in productos[:20]:  # Primeros 20
                    print(f"  ${p.precio:7.2f} | {p.marca:15} | {p.nombre[:50]}")
                if len(productos) > 20:
                    print(f"\n  ... y {len(productos) - 20} más")
            else:
                print(f"\nNo hay productos en '{cat_input}'")

        elif opcion == "2":
            busqueda = input("\nBuscar productos por nombre: ").strip().lower()

            from src.database.models import Producto

            productos = (
                db.session.query(Producto)
                .filter(Producto.nombre.ilike(f"%{busqueda}%"))
                .order_by(Producto.precio.asc())
                .all()
            )

            if productos:
                print(f"\n{len(productos)} productos encontrados:\n")
                for p in productos[:20]:
                    print(f"  {p.categoria:20} | ${p.precio:7.2f} | {p.nombre[:40]}")
            else:
                print("\nNo se encontraron productos")

        elif opcion == "3":
            from src.database.models import Producto

            caros = (
                db.session.query(Producto)
                .order_by(Producto.precio.desc())
                .limit(10)
                .all()
            )

            print("\nTOP 10 MÁS CAROS:\n")
            for i, p in enumerate(caros, 1):
                print(f"  {i:2}. ${p.precio:8.2f} | {p.categoria:20} | {p.nombre[:40]}")

        elif opcion == "4":
            from src.database.models import Producto

            baratos = (
                db.session.query(Producto)
                .order_by(Producto.precio.asc())
                .limit(10)
                .all()
            )

            print("\nTOP 10 MÁS BARATOS:\n")
            for i, p in enumerate(baratos, 1):
                print(f"  {i:2}. ${p.precio:7.2f} | {p.categoria:20} | {p.nombre[:40]}")

        elif opcion == "5":
            from src.database.models import Producto

            todos = db.session.query(Producto).all()

            data = [
                {
                    "timestamp": p.timestamp,
                    "categoria": p.categoria,
                    "nombre": p.nombre,
                    "marca": p.marca,
                    "precio": p.precio,
                    "precio_min": p.precio_min,
                    "precio_max": p.precio_max,
                    "presentacion": p.presentacion,
                    "sucursales": p.sucursales_disponibles,
                }
                for p in todos
            ]

            df_export = pd.DataFrame(data)
            filename = (
                f"productos_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            df_export.to_csv(filename, index=False)
            print(f"\nExportado a: {filename}")

        elif opcion == "0":
            print("\nHasta luego!")
            break

        else:
            print("\nOpción inválida")


if __name__ == "__main__":
    explorar_datos()
