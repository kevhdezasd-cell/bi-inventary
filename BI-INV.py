import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Inventario",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Dashboard Inteligente de Inventario")
st.markdown("### Analiza tu inventario cargando un archivo Excel o CSV")

# ---------------------------------------------------------
# CARGA DEL ARCHIVO
# ---------------------------------------------------------
file = st.file_uploader("Sube tu archivo de inventario", type=["xlsx", "csv"])

if file:
    # Lectura automática
    df = pd.read_excel(file) if file.name.endswith("xlsx") else pd.read_csv(file)

    st.success("Archivo cargado correctamente.")

    # ---------------------------------------------------------
    # PREPROCESAMIENTO
    # ---------------------------------------------------------
    df["ValorInventario"] = df["Stock Actual"] * df["Costo Unitario"]
    df["BajoStock"] = df["Stock Actual"] < df["Stock Mínimo"]
    df["SobreStock"] = df["Stock Actual"] > df["Stock Máximo"]

    df["Rotación"] = df["Venta Mensual"] / (df["Stock Actual"] + 1)
    df["Cobertura (días)"] = (df["Stock Actual"] / (df["Venta Mensual"] + 1)) * 30

    # ---------------------------------------------------------
    # KPIs
    # ---------------------------------------------------------
    total_valor = df["ValorInventario"].sum()
    bajo_stock = df["BajoStock"].sum()
    sobre_stock = df["SobreStock"].sum()
    rot_prom = df["Rotación"].mean()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("💰 Valor Total de Inventario", f"${total_valor:,.2f}")
    c2.metric("⚠ Productos en Bajo Stock", bajo_stock)
    c3.metric("📦 Productos en Sobrestock", sobre_stock)
    c4.metric("🔄 Rotación Promedio", f"{rot_prom:.2f}")

    st.markdown("---")

    # ---------------------------------------------------------
    # GRÁFICOS
    # ---------------------------------------------------------
    st.subheader("📊 Visualizaciones del Inventario")

    col1, col2 = st.columns(2)

    # Valor por categoría
    with col1:
        fig1 = px.bar(
            df.groupby("Categoría")["ValorInventario"].sum().reset_index(),
            x="Categoría",
            y="ValorInventario",
            title="Valor del Inventario por Categoría",
            text_auto=True
        )
        st.plotly_chart(fig1, use_container_width=True)

    # Stock actual por producto
    with col2:
        fig2 = px.bar(
            df.sort_values("Stock Actual", ascending=False),
            x="Producto",
            y="Stock Actual",
            title="Stock Actual por Producto"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ---------------------------------------------------------
    # PRODUCTOS EN RIESGO
    # ---------------------------------------------------------
    st.subheader("🚨 Productos en Riesgo de Quiebre de Stock")
    df_bajo = df[df["BajoStock"] == True]

    st.dataframe(
        df_bajo.style.apply(
            lambda x: ["background-color: #ffcccc" if v else "" for v in x], subset=["BajoStock"]
        )
    )

    st.subheader("📦 Productos con Sobrestock")
    df_sobre = df[df["SobreStock"] == True]
    st.dataframe(
        df_sobre.style.apply(
            lambda x: ["background-color: #fff3cd" if v else "" for v in x], subset=["SobreStock"]
        )
    )

    # ---------------------------------------------------------
    # COBERTURA
    # ---------------------------------------------------------
    st.subheader("⏳ Cobertura de Inventario (Días)")
    fig3 = px.scatter(
        df,
        x="Producto",
        y="Cobertura (días)",
        color="Categoría",
        size="Stock Actual",
        title="Cobertura del Inventario por Producto"
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ---------------------------------------------------------
    # RECOMENDACIONES
    # ---------------------------------------------------------
    st.markdown("## 🧠 Recomendaciones Inteligentes")

    st.info("""
    **Sugerencias basadas en los datos cargados:**

    - Reabastecer de inmediato los productos marcados en **rojo**.
    - Revisar estrategia de compra para productos con sobrestock.
    - Priorizar ventas de productos con rotación baja.
    - Mejorar predicciones de demanda para mantener niveles óptimos de inventario.
    - Revisar costos unitarios altos para reducir el valor total del inventario.
    """)

else:
    st.warning("Por favor sube un archivo para generar el dashboard.")
