import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database import Database

# Configuración de la página
st.set_page_config(page_title="Price Monitor Dashboard", page_icon="📊", layout="wide")


# Inicializar base de datos
@st.cache_resource
def get_database():
    return Database("price_monitor.db")


db = get_database()

# Título principal
st.title("📊 Price Monitor - Dashboard de Análisis")
st.markdown("---")

# === SIDEBAR ===
with st.sidebar:
    st.header("⚙️ Configuración")

    # Selector de vista
    vista = st.radio(
        "Selecciona vista:",
        ["📈 Overview", "💵 Cotizaciones", "🛒 Productos", "📊 Análisis"],
    )

    st.markdown("---")

    # Estadísticas generales
    stats = db.obtener_estadisticas_generales()

    st.subheader("📋 Estadísticas Generales")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Productos", stats["total_productos"])
    with col2:
        st.metric("Cotizaciones", stats["total_cotizaciones"])

    if stats["ultima_fecha"]:
        st.info(
            f"🕐 Última actualización:\n{stats['ultima_fecha'].strftime('%Y-%m-%d %H:%M')}"
        )

# === VISTA: OVERVIEW ===
if vista == "📈 Overview":
    st.header("📈 Vista General del Sistema")

    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)

    # Obtener datos
    ultimas_cotizaciones = db.obtener_comparacion_cotizaciones()
    ultimos_productos = db.obtener_ultimos_productos(10)

    with col1:
        if ultimas_cotizaciones:
            dolar_blue = next(
                (c for c in ultimas_cotizaciones if c.nombre == "Blue"), None
            )
            if dolar_blue:
                st.metric(
                    "Dólar Blue",
                    f"${dolar_blue.precio_venta:.2f}",
                    f"Spread: ${dolar_blue.precio_venta - dolar_blue.precio_compra:.2f}",
                )

    with col2:
        if ultimas_cotizaciones:
            dolar_oficial = next(
                (c for c in ultimas_cotizaciones if c.nombre == "Oficial"), None
            )
            if dolar_oficial:
                st.metric(
                    "Dólar Oficial",
                    f"${dolar_oficial.precio_venta:.2f}",
                    f"Spread: ${dolar_oficial.precio_venta - dolar_oficial.precio_compra:.2f}",
                )

    with col3:
        if ultimos_productos:
            precio_promedio = sum(
                p.precio for p in ultimos_productos if p.precio
            ) / len(ultimos_productos)
            st.metric(
                "Precio Promedio", f"${precio_promedio:.2f}", "últimos 10 productos"
            )

    with col4:
        categorias_distintas = len(
            set(p.categoria for p in ultimos_productos if p.categoria)
        )
        st.metric("Categorías", categorias_distintas, "monitoreadas")

    st.markdown("---")

    # Dos columnas para cotizaciones y productos
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💵 Últimas Cotizaciones")
        if ultimas_cotizaciones:
            df_cotizaciones = pd.DataFrame(
                [
                    {
                        "Tipo": c.nombre,
                        "Compra": f"${c.precio_compra:.2f}",
                        "Venta": f"${c.precio_venta:.2f}",
                        "Spread": f"${c.precio_venta - c.precio_compra:.2f}",
                    }
                    for c in ultimas_cotizaciones
                ]
            )
            st.dataframe(df_cotizaciones, use_container_width=True, hide_index=True)

    with col2:
        st.subheader("🛒 Últimos Productos")
        if ultimos_productos:
            df_productos = pd.DataFrame(
                [
                    {
                        "Producto": p.nombre[:40] + "..."
                        if len(p.nombre) > 40
                        else p.nombre,
                        "Precio": f"${p.precio:.2f}",
                        "Categoría": p.categoria,
                    }
                    for p in ultimos_productos
                ]
            )
            st.dataframe(df_productos, use_container_width=True, hide_index=True)

# === VISTA: COTIZACIONES ===
elif vista == "💵 Cotizaciones":
    st.header("💵 Análisis de Cotizaciones")

    # Comparación de cotizaciones actuales
    st.subheader("📊 Comparación de Tipos de Cambio")

    cotizaciones = db.obtener_comparacion_cotizaciones()

    if cotizaciones:
        # Preparar datos para gráfico
        df_cot = pd.DataFrame(
            [
                {
                    "Tipo": c.nombre,
                    "Compra": c.precio_compra,
                    "Venta": c.precio_venta,
                    "Spread": c.precio_venta - c.precio_compra,
                }
                for c in cotizaciones
            ]
        )

        # Gráfico de barras comparativo
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                name="Compra",
                x=df_cot["Tipo"],
                y=df_cot["Compra"],
                marker_color="lightblue",
            )
        )
        fig.add_trace(
            go.Bar(
                name="Venta",
                x=df_cot["Tipo"],
                y=df_cot["Venta"],
                marker_color="darkblue",
            )
        )

        fig.update_layout(
            title="Precios de Compra y Venta por Tipo de Cambio",
            xaxis_title="Tipo de Cambio",
            yaxis_title="Precio (ARS)",
            barmode="group",
            height=400,
        )

        st.plotly_chart(fig, use_container_width=True)

        # Tabla detallada
        st.subheader("📋 Detalle de Cotizaciones")

        df_detalle = pd.DataFrame(
            [
                {
                    "Tipo": c.nombre,
                    "Compra": f"${c.precio_compra:.2f}",
                    "Venta": f"${c.precio_venta:.2f}",
                    "Spread": f"${c.precio_venta - c.precio_compra:.2f}",
                    "Spread %": f"{((c.precio_venta - c.precio_compra) / c.precio_compra * 100):.2f}%",
                    "Actualizado": c.timestamp.strftime("%Y-%m-%d %H:%M"),
                }
                for c in cotizaciones
            ]
        )

        st.dataframe(df_detalle, use_container_width=True, hide_index=True)

        # Gráfico de spread
        st.subheader("📈 Spreads por Tipo de Cambio")
        fig_spread = px.bar(
            df_cot.sort_values("Spread", ascending=False),
            x="Tipo",
            y="Spread",
            title="Diferencia entre Precio de Venta y Compra",
            labels={"Spread": "Spread (ARS)", "Tipo": "Tipo de Cambio"},
            color="Spread",
            color_continuous_scale="Blues",
        )
        fig_spread.update_layout(height=400)
        st.plotly_chart(fig_spread, use_container_width=True)

# === VISTA: PRODUCTOS ===
elif vista == "🛒 Productos":
    st.header("🛒 Análisis de Productos")

    # Filtros
    col1, col2 = st.columns([1, 3])

    with col1:
        # Obtener categorías disponibles
        from sqlalchemy import distinct

        categorias_disponibles = [
            c[0]
            for c in db.session.query(
                distinct(
                    db.session.query(Database)
                    .from_statement("SELECT DISTINCT categoria FROM productos")
                    .statement
                )
            ).all()
            if c[0]
        ]

        if not categorias_disponibles:
            # Fallback si la query falla
            categorias_disponibles = [
                "leche",
                "arroz",
                "aceite",
                "azucar",
                "harina",
                "fideos",
                "yerba",
                "cafe",
            ]

        categoria_filtro = st.selectbox(
            "Filtrar por categoría:", ["Todas"] + sorted(categorias_disponibles)
        )

    # Obtener productos
    if categoria_filtro == "Todas":
        productos = db.obtener_ultimos_productos(100)
    else:
        from database import Producto

        productos = (
            db.session.query(Producto)
            .filter(Producto.categoria == categoria_filtro)
            .order_by(Producto.timestamp.desc())
            .limit(100)
            .all()
        )

    if productos:
        # Convertir a DataFrame
        df_productos = pd.DataFrame(
            [
                {
                    "Nombre": p.nombre,
                    "Marca": p.marca,
                    "Precio": p.precio,
                    "Precio Min": p.precio_min,
                    "Precio Max": p.precio_max,
                    "Categoría": p.categoria,
                    "Presentación": p.presentacion,
                    "Sucursales": p.sucursales_disponibles,
                    "Fecha": p.timestamp.strftime("%Y-%m-%d %H:%M"),
                }
                for p in productos
            ]
        )

        # Métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Productos", len(df_productos))
        with col2:
            st.metric("Precio Promedio", f"${df_productos['Precio'].mean():.2f}")
        with col3:
            st.metric("Precio Mínimo", f"${df_productos['Precio'].min():.2f}")
        with col4:
            st.metric("Precio Máximo", f"${df_productos['Precio'].max():.2f}")

        st.markdown("---")

        # Gráfico de distribución de precios
        st.subheader("📊 Distribución de Precios")
        fig_dist = px.histogram(
            df_productos,
            x="Precio",
            nbins=30,
            title=f"Distribución de Precios - {categoria_filtro}",
            labels={"Precio": "Precio (ARS)", "count": "Cantidad"},
            color_discrete_sequence=["#1f77b4"],
        )
        fig_dist.update_layout(height=400)
        st.plotly_chart(fig_dist, use_container_width=True)

        # Top 10 más baratos
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💰 Top 10 Más Baratos")
            df_baratos = df_productos.nsmallest(10, "Precio")[
                ["Nombre", "Marca", "Precio"]
            ]
            df_baratos["Precio"] = df_baratos["Precio"].apply(lambda x: f"${x:.2f}")
            st.dataframe(df_baratos, use_container_width=True, hide_index=True)

        with col2:
            st.subheader("💸 Top 10 Más Caros")
            df_caros = df_productos.nlargest(10, "Precio")[
                ["Nombre", "Marca", "Precio"]
            ]
            df_caros["Precio"] = df_caros["Precio"].apply(lambda x: f"${x:.2f}")
            st.dataframe(df_caros, use_container_width=True, hide_index=True)

        # Tabla completa con búsqueda
        st.subheader("🔍 Todos los Productos")
        busqueda = st.text_input("Buscar producto por nombre:", "")

        if busqueda:
            df_filtrado = df_productos[
                df_productos["Nombre"].str.contains(busqueda, case=False, na=False)
            ]
        else:
            df_filtrado = df_productos

        st.dataframe(df_filtrado, use_container_width=True, hide_index=True)

# === VISTA: ANÁLISIS ===
elif vista == "📊 Análisis":
    st.header("📊 Análisis Avanzado")

    st.subheader("💡 Insights y Estadísticas")

    # Análisis por categoría
    from database import Producto
    from sqlalchemy import func

    resultado = (
        db.session.query(
            Producto.categoria,
            func.count(Producto.id).label("cantidad"),
            func.avg(Producto.precio).label("precio_promedio"),
            func.min(Producto.precio).label("precio_min"),
            func.max(Producto.precio).label("precio_max"),
        )
        .group_by(Producto.categoria)
        .all()
    )

    if resultado:
        df_stats = pd.DataFrame(
            [
                {
                    "Categoría": r.categoria,
                    "Cantidad": r.cantidad,
                    "Precio Promedio": r.precio_promedio,
                    "Precio Mínimo": r.precio_min,
                    "Precio Máximo": r.precio_max,
                    "Rango": r.precio_max - r.precio_min,
                }
                for r in resultado
                if r.categoria
            ]
        )

        # Gráfico de precio promedio por categoría
        fig_cat = px.bar(
            df_stats.sort_values("Precio Promedio", ascending=False),
            x="Categoría",
            y="Precio Promedio",
            title="Precio Promedio por Categoría",
            labels={"Precio Promedio": "Precio (ARS)", "Categoría": "Categoría"},
            color="Precio Promedio",
            color_continuous_scale="Viridis",
        )
        fig_cat.update_layout(height=400)
        st.plotly_chart(fig_cat, use_container_width=True)

        # Tabla de estadísticas
        st.subheader("📋 Estadísticas por Categoría")
        df_stats_display = df_stats.copy()
        df_stats_display["Precio Promedio"] = df_stats_display["Precio Promedio"].apply(
            lambda x: f"${x:.2f}"
        )
        df_stats_display["Precio Mínimo"] = df_stats_display["Precio Mínimo"].apply(
            lambda x: f"${x:.2f}"
        )
        df_stats_display["Precio Máximo"] = df_stats_display["Precio Máximo"].apply(
            lambda x: f"${x:.2f}"
        )
        df_stats_display["Rango"] = df_stats_display["Rango"].apply(
            lambda x: f"${x:.2f}"
        )

        st.dataframe(df_stats_display, use_container_width=True, hide_index=True)

        # Análisis de variabilidad de precios
        st.subheader("📈 Variabilidad de Precios")
        fig_rango = px.bar(
            df_stats.sort_values("Rango", ascending=False),
            x="Categoría",
            y="Rango",
            title="Rango de Precios por Categoría (Diferencia entre Máximo y Mínimo)",
            labels={"Rango": "Rango (ARS)", "Categoría": "Categoría"},
            color="Rango",
            color_continuous_scale="Reds",
        )
        fig_rango.update_layout(height=400)
        st.plotly_chart(fig_rango, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "**Price Monitor** - Sistema de monitoreo de precios y cotizaciones | Datos actualizados automáticamente"
)
