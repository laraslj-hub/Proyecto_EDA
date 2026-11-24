"""
Módulo: funciones.py
Propósito: Contener toda la lógica analítica del proyecto: preprocesado, limpieza,
cálculo vectorizado de métricas descriptivas de inversión y generación de gráficos.
Por qué se diseña así: Todas las funciones son 'puras' o modulares (reciben DataFrames
y devuelven DataFrames), facilitando la realización de pruebas unitarias y su
reutilización directa dentro de los Jupyter Notebooks.
"""

from pathlib import Path
from typing import Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def limpiar_y_preprocesar_datos(df_bruto: pd.DataFrame, ruta_salida: Path) -> pd.DataFrame:
    """
    Realiza la limpieza integral del dataset: eliminación de duplicados, ordenación
    cronológica e imputación de valores faltantes (missings).
    
    POR QUÉ SE HACE ASÍ:
    1. Eliminar duplicados en el índice temporal evita distorsiones al calcular rentabilidades.
    2. En series temporales financieras, NUNCA se debe imputar con la media global porque
       introduce 'sesgo de anticipación' (look-ahead bias: usar precios del futuro para
       rellenar el pasado). Por ello, se usa 'ffill' (Forward Fill: propagar el último precio
       de cierre conocido, que es exactamente lo que ocurre en días festivos bursátiles) y
       'bfill' únicamente para el primer día de la serie si estuviera vacío.
    """
    df = df_bruto.copy()

    # 1. Auditoría inicial
    nulos_iniciales = int(df.isna().sum().sum())
    duplicados_iniciales = int(df.index.duplicated().sum())
    print(f"[LIMPIEZA] Estado inicial -> Nulos: {nulos_iniciales} | Fechas duplicadas: {duplicados_iniciales}")

    # 2. Eliminación de índices duplicados conservando la primera aparición
    df = df[~df.index.duplicated(keep="first")]

    # 3. Ordenación cronológica estricta
    df = df.sort_index(ascending=True)

    # 4. Eliminación de columnas completamente vacías (si algún ticker falló por completo)
    df = df.dropna(axis=1, how="all")

    # 5. Imputación financiera sin sesgo de futuro (Forward Fill + Backward Fill inicial)
    df = df.ffill().bfill()

    # 6. Verificación de calidad post-limpieza
    nulos_finales = int(df.isna().sum().sum())
    print(f"[LIMPIEZA] Estado final   -> Nulos: {nulos_finales} | Filas válidas: {len(df)}")

    df.to_csv(ruta_salida)
    return df


def calcular_retornos(
    df_precios: pd.DataFrame,
    ventana_corto_plazo: int = 21
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Calcula las rentabilidades porcentuales diarias y las rentabilidades acumuladas
    en ventanas móviles de muy corto plazo (por defecto, 21 sesiones = 1 mes).
    
    POR QUÉ: Usamos operaciones vectorizadas de Pandas (pct_change) en lugar de bucles 'for'
    porque se ejecutan en código C subyacente, siendo hasta 100 veces más rápidas.
    """
    # Retorno simple diario: R_t = (P_t - P_{t-1}) / P_{t-1}
    retornos_diarios = df_precios.pct_change().dropna()

    # Retorno en ventana móvil de corto plazo (ej. qué gana una persona que entra hoy y sale en 21 días)
    retornos_corto_plazo = df_precios.pct_change(periods=ventana_corto_plazo).dropna()

    return retornos_diarios, retornos_corto_plazo


def obtener_estadisticos_descriptivos(
    retornos_diarios: pd.DataFrame,
    retornos_corto_plazo: pd.DataFrame,
    tasa_libre_riesgo: float,
    dias_anio: int,
    nivel_var: float,
    ruta_salida: Path
) -> pd.DataFrame:
    """
    Calcula una batería completa de estadísticos descriptivos centrados en la relación
    riesgo-beneficio para responder con rigor a la pregunta de investigación.
    
    POR QUÉ SE INCLUYEN ESTAS MÉTRICAS:
    - Media y Mediana a Corto Plazo: La mediana es robusta frente a valores atípicos (outliers).
    - Volatilidad y Rango Intercuartílico: Miden la incertidumbre.
    - Valor en Riesgo (VaR 95%): Indica cuánto puede perder una familia en el 5% de los peores meses.
    - Maximum Drawdown (Caída Máxima): Mide la peor pérdida acumulada desde un máximo previo.
    - Ratio de Sharpe: Evalúa el beneficio obtenido por cada unidad de riesgo asumido.
    """
    resumen = pd.DataFrame(index=retornos_diarios.columns)

    # 1. Métricas de Muy Corto Plazo (Ventana de 21 días hábiles / 1 mes)
    resumen["Retorno_Medio_Mensual_%"] = retornos_corto_plazo.mean() * 100
    resumen["Retorno_Mediano_Mensual_%"] = retornos_corto_plazo.median() * 100
    resumen["Mejor_Mes_%"] = retornos_corto_plazo.max() * 100
    resumen["Peor_Mes_%"] = retornos_corto_plazo.min() * 100

    # Probabilidad empírica de ganar dinero en un mes cualquiera
    resumen["Probabilidad_Ganancia_Mensual_%"] = (retornos_corto_plazo > 0).mean() * 100

    # Valor en Riesgo Histórico Mensual al 95% de confianza (Percentil 5)
    resumen["VaR_95_Mensual_%"] = np.percentile(retornos_corto_plazo, nivel_var * 100, axis=0) * 100

    # 2. Métricas Anualizadas y de Eficiencia (Ratio de Sharpe)
    retorno_anualizado = retornos_diarios.mean() * dias_anio
    volatilidad_anualizada = retornos_diarios.std() * np.sqrt(dias_anio)

    resumen["Retorno_Anualizado_%"] = retorno_anualizado * 100
    resumen["Volatilidad_Anualizada_%"] = volatilidad_anualizada * 100
    resumen["Ratio_Sharpe"] = (retorno_anualizado - tasa_libre_riesgo) / volatilidad_anualizada

    # 3. Cálculo del Maximum Drawdown (Caída máxima desde el pico)
    # POR QUÉ: Se calcula reconstruyendo el índice de riqueza acumulada y comparándolo con su máximo histórico.
    riqueza_acumulada = (1 + retornos_diarios).cumprod()
    pico_historico = riqueza_acumulada.cummax()
    drawdown = (riqueza_acumulada - pico_historico) / pico_historico
    resumen["Max_Drawdown_%"] = drawdown.min() * 100

    # 4. Forma de la distribución (Asimetría y Curtosis)
    resumen["Asimetria_Skewness"] = retornos_diarios.skew()
    resumen["Curtosis"] = retornos_diarios.kurtosis()

    # Ordenamos por Ratio de Sharpe descendente (el criterio profesional de eficiencia financiera)
    resumen = resumen.sort_values(by="Ratio_Sharpe", ascending=False).round(2)
    resumen.to_csv(ruta_salida)
    return resumen


def generar_visualizaciones(
    df_precios: pd.DataFrame,
    retornos_diarios: pd.DataFrame,
    retornos_corto_plazo: pd.DataFrame,
    df_resumen: pd.DataFrame,
    ruta_graficos: Path,
    dpi: int = 300
) -> None:
    """
    Genera y exporta los 4 gráficos clave para la memoria y la presentación ejecutiva.
    
    POR QUÉ: Cada gráfico responde a una pregunta específica de la narrativa:
    1. Evolución Base 100 -> ¿Cuánto habrían crecido 100 € en cada activo?
    2. Boxplot de Corto Plazo -> ¿Qué dispersión y riesgo de pérdida mensual sufre el inversor?
    3. Mapa de Riesgo vs Beneficio -> ¿Qué activo es realmente más eficiente (Sharpe)?
    4. Matriz de Correlación -> ¿Cómo combinamos activos para no perderlo todo a la vez?
    """
    sns.set_theme(style="whitegrid")

    # ---------------------------------------------------------------------
    # GRÁFICO 1: Evolución del Capital Normalizado (Base 100 €)
    # ---------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 6))
    precios_base_100 = (df_precios / df_precios.iloc[0]) * 100
    for columna in precios_base_100.columns:
        ax.plot(precios_base_100.index, precios_base_100[columna], label=columna, linewidth=2)

    ax.axhline(100, color="black", linestyle="--", alpha=0.6, label="Capital Inicial (100 €)")
    ax.set_title("Evolución de 100 € Invertidos: Comparativa de Clases de Activos", fontsize=14, fontweight="bold")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Valor del Capital (€)")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(ruta_graficos / "01_evolucion_capital_base100.png", dpi=dpi)
    plt.close(fig)

    # ---------------------------------------------------------------------
    # GRÁFICO 2: Distribución de Rentabilidades a Muy Corto Plazo (21 días)
    # ---------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(11, 6))
    datos_melted = retornos_corto_plazo.melt(var_name="Activo", value_name="Retorno_Mensual")
    datos_melted["Retorno_Mensual"] = datos_melted["Retorno_Mensual"] * 100

    sns.boxplot(
        data=datos_melted,
        x="Activo",
        y="Retorno_Mensual",
        palette="viridis",
        ax=ax,
        showfliers=True
    )
    ax.axhline(0, color="red", linestyle="--", linewidth=1.5, label="Umbral de Pérdida (0%)")
    ax.set_title("Distribución de Beneficios y Pérdidas a Muy Corto Plazo (Ventanas de 21 Días)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Activo Financiero")
    ax.set_ylabel("Rentabilidad Mensual (%)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(ruta_graficos / "02_boxplot_corto_plazo.png", dpi=dpi)
    plt.close(fig)

    # ---------------------------------------------------------------------
    # GRÁFICO 3: Mapa Estratégico Riesgo vs. Beneficio (Frontera de Eficiencia)
    # ---------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 6))
    scatter = ax.scatter(
        df_resumen["Volatilidad_Anualizada_%"],
        df_resumen["Retorno_Anualizado_%"],
        c=df_resumen["Ratio_Sharpe"],
        cmap="viridis",
        s=250,
        edgecolors="black",
        zorder=4
    )
    for activo, fila in df_resumen.iterrows():
        ax.annotate(
            f"{activo}\n(Sharpe: {fila['Ratio_Sharpe']})",
            (fila["Volatilidad_Anualizada_%"], fila["Retorno_Anualizado_%"]),
            xytext=(8, 5),
            textcoords="offset points",
            fontsize=9,
            fontweight="bold"
        )

    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("Eficiencia (Ratio de Sharpe)")
    ax.set_title("Relación Riesgo vs. Beneficio: ¿Dónde es más eficiente el capital?", fontsize=14, fontweight="bold")
    ax.set_xlabel("Riesgo / Volatilidad Anualizada (%)")
    ax.set_ylabel("Retorno Anualizado Esperado (%)")
    fig.tight_layout()
    fig.savefig(ruta_graficos / "03_riesgo_vs_beneficio.png", dpi=dpi)
    plt.close(fig)

    # ---------------------------------------------------------------------
    # GRÁFICO 4: Matriz de Correlación de Pearson (Diversificación)
    # ---------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    matriz_corr = retornos_diarios.corr()
    sns.heatmap(
        matriz_corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        linewidths=0.8,
        ax=ax
    )
    ax.set_title("Matriz de Correlación entre Activos (Diversificación del Riesgo)", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(ruta_graficos / "04_matriz_correlacion.png", dpi=dpi)
    plt.close(fig)
    print(f"[GRÁFICOS] Las 4 visualizaciones se han exportado correctamente en: {ruta_graficos}")