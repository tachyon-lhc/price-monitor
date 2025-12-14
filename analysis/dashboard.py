import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# setup path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database import Database
from src.database.models import Producto
import config

# Configuración de la pagina
st.set_page_config(page_title="Price Monitor Dashboard", page_icon="📊", layout="wide")


# Cache de la base de datos
@st.cache_resource
def get_database():
    return Database("price_monitor.db")


db = get_database()


# Cache de datos
@st.cache_data(ttl=300)
def load_all_products():
    productos = db.session.query(Producto).all()
    return pd.DataFrame(
        [
            {
                "id": p.id,
                "fecha": p.timestamp.date(),
                "hora": p.timestamp.time(),
                "categoria": p.categoria,
                "nombre": p.nombre,
                "marca": p.marca,
                "precio": p.precio,
                "precio_min": p.precio_min,
                "precio_max": p.precio_max,
                "presentacion": p.presentacion,
                "sucursales": p.sucursales_disponibles,
            }
            for p in productos
        ]
    )


# Cargar datos
df = load_all_products()

# Sidebar
with st.sidebar:
    st.header("Filtros")

    # Filtro de fecha
    fechas_disponibles = sorted(df["fecha"].unique())
    fecha_seleccionada = st.selectbox(
        "Fecha", options=["Todas"] + [str(f) for f in fechas_disponibles], index=0
    )

    # Filtro de categoría
    categorias = ["Todas"] + sorted(df["categoria"].unique().tolist())
    categoria_seleccionada = st.selectbox("Categoría", categorias)

    st.markdown("---")

    # Estadísticas generales
    st.subheader("Estadísticas Generales")
    stats = db.obtener_estadisticas_generales()
    st.metric("Total Productos", stats["total_productos"])
    st.metric("Categorías", len(stats["categorias"]))
    st.metric("Días con Datos", len(fechas_disponibles))

    if stats["ultima_fecha"]:
        st.info(
            f"Última actualización:\n{stats['ultima_fecha'].strftime('%Y-%m-%d %H:%M')}"
        )

# Aplicar filtros
df_filtered = df.copy()
if fecha_seleccionada != "Todas":
    df_filtered = df_filtered[
        df_filtered["fecha"] == pd.to_datetime(fecha_seleccionada).date()
    ]
if categoria_seleccionada != "Todas":
    df_filtered = df_filtered[df_filtered["categoria"] == categoria_seleccionada]

# Título principal
st.title("📊 Supermarket Price Tracker - Dashboard")
st.markdown("---")

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Productos", "Canasta Básica", "Evolución Temporal"]
)

# TAB 1: OVERVIEW
with tab1:
    st.header("Vista General")

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Productos Totales",
            len(df_filtered),
            delta=f"{len(df_filtered) - len(df)}"
            if fecha_seleccionada != "Todas"
            else None,
        )

    with col2:
        st.metric("Precio Promedio", f"${df_filtered['precio'].mean():.2f}")

    with col3:
        st.metric("Precio Mínimo", f"${df_filtered['precio'].min():.2f}")

    with col4:
        st.metric("Precio Máximo", f"${df_filtered['precio'].max():.2f}")

    st.markdown("---")

    # Gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribución de Precios")
        fig = px.histogram(
            df_filtered,
            x="precio",
            nbins=30,
            title="",
            labels={"precio": "Precio (ARS)", "count": "Cantidad"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Productos por Categoría")
        cat_counts = df_filtered["categoria"].value_counts().head(10)
        fig = px.bar(
            x=cat_counts.values,
            y=cat_counts.index,
            orientation="h",
            labels={"x": "Cantidad", "y": "Categoría"},
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Estadísticas por categoría
    st.subheader("Estadísticas por Categoría")

    stats_cat = (
        df_filtered.groupby("categoria")
        .agg({"precio": ["count", "mean", "min", "max"]})
        .round(2)
    )

    stats_cat.columns = ["Cantidad", "Promedio", "Mínimo", "Máximo"]
    stats_cat = stats_cat.sort_values("Promedio", ascending=False)

    st.dataframe(stats_cat, use_container_width=True)

# TAB 2: PRODUCTOS
with tab2:
    st.header("Exploración de Productos")

    # Buscador
    busqueda = st.text_input("Buscar por nombre de producto:", "")

    df_search = df_filtered.copy()
    if busqueda:
        df_search = df_search[
            df_search["nombre"].str.contains(busqueda, case=False, na=False)
        ]

    st.write(f"Mostrando {len(df_search)} productos")

    # Ordenamiento
    col1, col2 = st.columns([3, 1])
    with col1:
        orden = st.selectbox(
            "Ordenar por:",
            ["Precio (menor a mayor)", "Precio (mayor a menor)", "Nombre", "Categoría"],
        )

    if orden == "Precio (menor a mayor)":
        df_search = df_search.sort_values("precio")
    elif orden == "Precio (mayor a menor)":
        df_search = df_search.sort_values("precio", ascending=False)
    elif orden == "Nombre":
        df_search = df_search.sort_values("nombre")
    else:
        df_search = df_search.sort_values("categoria")

    # Tabla de productos
    st.dataframe(
        df_search[
            ["categoria", "nombre", "marca", "precio", "presentacion", "sucursales"]
        ].head(50),
        use_container_width=True,
        hide_index=True,
    )

    # Top más baratos y más caros
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Más Baratos")
        baratos = df_filtered.nsmallest(10, "precio")[
            ["nombre", "marca", "precio", "categoria"]
        ]
        st.dataframe(baratos, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("Top 10 Más Caros")
        caros = df_filtered.nlargest(10, "precio")[
            ["nombre", "marca", "precio", "categoria"]
        ]
        st.dataframe(caros, hide_index=True, use_container_width=True)

# TAB 3: CANASTA BÁSICA
with tab3:
    st.header("Canasta Básica")

    from src.utils.analysis import calcular_costo_canasta_basica

    # CAMBIO: Usar todos los datos, no solo última fecha
    # Para cada categoría, tomar el producto más barato disponible
    canasta_productos = []
    costo_total = 0

    for categoria in config.CANASTA_BASICA:
        # Buscar en TODOS los datos disponibles
        productos_cat = df[df["categoria"] == categoria]

        if not productos_cat.empty:
            # Agrupar por producto (nombre+marca) y tomar precio mínimo
            producto_min = productos_cat.loc[productos_cat["precio"].idxmin()]

            cantidad = config.CANTIDADES_CANASTA.get(categoria, 1)

            subtotal = producto_min["precio"] * cantidad

            canasta_productos.append(
                {
                    "Categoría": categoria,
                    "Producto": producto_min["nombre"],
                    "Marca": producto_min["marca"],
                    "Precio Unitario": producto_min["precio"],
                    "Cantidad": cantidad,
                    "Subtotal": subtotal,
                    "Presentación": producto_min["presentacion"],
                    "Fecha": producto_min["fecha"],
                }
            )

        costo_total += subtotal

    # Mostrar costo total
    col1, col2 = st.columns([2, 1])
    with col1:
        st.metric(
            "Costo Total de Canasta Básica",
            f"${costo_total:,.2f}",
            help="Suma de los productos más baratos de cada categoría (histórico completo)",
        )
    with col2:
        st.metric(
            "Productos en Canasta",
            f"{len(canasta_productos)} / {len(config.CANASTA_BASICA)}",
        )

    st.markdown("---")

    # Tabla de productos
    if canasta_productos:
        df_canasta = pd.DataFrame(canasta_productos)

        # Formatear tabla
        st.subheader("Productos de la Canasta Básica")
        st.dataframe(df_canasta, use_container_width=True, hide_index=True)

        # Gráfico
        fig = px.bar(
            df_canasta,
            x="Categoría",
            y="Subtotal",
            title="Costo por Categoría en Canasta Básica",
            text="Subtotal",
            hover_data=["Producto", "Marca", "Cantidad", "Precio Unitario", "Fecha"],
        )
        fig.update_traces(texttemplate="$%{text:.2f}", textposition="outside")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

# TAB 4: EVOLUCIÓN TEMPORAL
with tab4:
    st.header("Evolución de Precios")

    if len(fechas_disponibles) < 2:
        st.warning("Se necesitan al menos 2 días de datos para análisis temporal")
    else:
        # Selector de categoría para evolución
        categorias_evolucion = st.multiselect(
            "Selecciona categorías para ver evolución:",
            options=sorted(df["categoria"].unique()),
            default=sorted(df["categoria"].unique())[:3],  # Primeras 3 por defecto
        )

        if categorias_evolucion:
            # Evolución del precio promedio por categoría
            df_evolucion = (
                df[df["categoria"].isin(categorias_evolucion)]
                .groupby(["fecha", "categoria"])["precio"]
                .mean()
                .reset_index()
            )

            fig = px.line(
                df_evolucion,
                x="fecha",
                y="precio",
                color="categoria",
                title="Evolución del Precio Promedio por Categoría",
                markers=True,
                labels={
                    "precio": "Precio Promedio (ARS)",
                    "fecha": "Fecha",
                    "categoria": "Categoría",
                },
            )
            st.plotly_chart(fig, use_container_width=True)

            # Variación de precios
            st.subheader("Variación de Precios entre Fechas")

            if len(fechas_disponibles) >= 2:
                fecha_inicial = fechas_disponibles[0]
                fecha_final = fechas_disponibles[-1]

                df_inicial = (
                    df[df["fecha"] == fecha_inicial]
                    .groupby("categoria")["precio"]
                    .mean()
                )
                df_final = (
                    df[df["fecha"] == fecha_final].groupby("categoria")["precio"].mean()
                )

                variacion = pd.DataFrame(
                    {"Precio Inicial": df_inicial, "Precio Final": df_final}
                )
                variacion["Variación (%)"] = (
                    (variacion["Precio Final"] - variacion["Precio Inicial"])
                    / variacion["Precio Inicial"]
                    * 100
                ).round(2)
                variacion["Variación ($)"] = (
                    variacion["Precio Final"] - variacion["Precio Inicial"]
                ).round(2)

                variacion = variacion.sort_values("Variación (%)", ascending=False)

                st.dataframe(variacion, use_container_width=True)

                # Gráfico de variaciones
                fig = px.bar(
                    variacion.reset_index(),
                    x="categoria",
                    y="Variación (%)",
                    title=f"Variación Porcentual de Precios ({fecha_inicial} → {fecha_final})",
                    color="Variación (%)",
                    color_continuous_scale=["green", "yellow", "red"],
                )
                st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**Supermarket Price Tracker** - Dashboard de análisis de precios")
st.markdown("Datos actualizados automáticamente mediante scheduler diario")
