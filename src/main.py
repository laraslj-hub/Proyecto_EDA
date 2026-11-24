"""
Módulo: main.py
Propósito: Orquestar de principio a fin el flujo del Análisis Exploratorio de Datos (EDA).
Por qué se diseña así: Mantiene un punto de entrada limpio y legible. Cualquier desarrollador
que abra 'main.py' comprende en 10 segundos las 4 fases del pipeline: Inicialización,
Ingesta, Preprocesamiento/Limpieza y Análisis/Visualización.
"""

from variables import (
    RUTA_DATOS,
    RUTA_DOCS,
    RUTA_GRAFICOS,
    ARCHIVO_DATOS_BRUTOS,
    ARCHIVO_DATOS_LIMPIOS,
    ARCHIVO_ESTADISTICOS,
    TICKERS_ACTIVOS,
    FECHA_INICIO,
    FECHA_FIN,
    VENTANA_CORTO_PLAZO,
    TASA_LIBRE_RIESGO_ANUAL,
    DIAS_BURSATILES_ANIO,
    NIVEL_CONFIANZA_VAR,
    RESOLUCION_DPI,
)
from utils.utils import inicializar_directorios, obtener_datos_financieros
from funciones import (
    limpiar_y_preprocesar_datos,
    calcular_retornos,
    obtener_estadisticos_descriptivos,
    generar_visualizaciones,
)


def ejecutar_pipeline_eda() -> None:
    """Ejecuta secuencialmente todas las etapas del Análisis Exploratorio de Datos."""
    print("=" * 75)
    print("INICIANDO ANÁLISIS EXPLORATORIO DE DATOS: INVERSIÓN A CORTO PLAZO")
    print("=" * 75)

    # Paso 1: Asegurar que la estructura de carpetas exista
    inicializar_directorios([RUTA_DATOS, RUTA_DOCS, RUTA_GRAFICOS])

    # Paso 2: Obtención de datos (API Yahoo Finance o Respaldo Determinista)
    df_bruto = obtener_datos_financieros(
        tickers=TICKERS_ACTIVOS,
        fecha_inicio=FECHA_INICIO,
        fecha_fin=FECHA_FIN,
        ruta_guardado=ARCHIVO_DATOS_BRUTOS,
    )

    # Paso 3: Limpieza y preprocesado de la serie temporal
    df_limpio = limpiar_y_preprocesar_datos(
        df_bruto=df_bruto,
        ruta_salida=ARCHIVO_DATOS_LIMPIOS,
    )

    # Paso 4: Transformación matemática (cálculo de rentabilidades diarias y a 21 días)
    retornos_diarios, retornos_corto_plazo = calcular_retornos(
        df_precios=df_limpio,
        ventana_corto_plazo=VENTANA_CORTO_PLAZO,
    )

    # Paso 5: Obtención de estadísticos descriptivos y métricas de riesgo
    df_resumen = obtener_estadisticos_descriptivos(
        retornos_diarios=retornos_diarios,
        retornos_corto_plazo=retornos_corto_plazo,
        tasa_libre_riesgo=TASA_LIBRE_RIESGO_ANUAL,
        dias_anio=DIAS_BURSATILES_ANIO,
        nivel_var=NIVEL_CONFIANZA_VAR,
        ruta_salida=ARCHIVO_ESTADISTICOS,
    )

    print("\n--- RESUMEN ESTADÍSTICO DESCRIPTIVO (ORDENADO POR EFICIENCIA SHARPE) ---")
    print(df_resumen.to_string())

    # Paso 6: Creación de visualizaciones ejecutivas
    generar_visualizaciones(
        df_precios=df_limpio,
        retornos_diarios=retornos_diarios,
        retornos_corto_plazo=retornos_corto_plazo,
        df_resumen=df_resumen,
        ruta_graficos=RUTA_GRAFICOS,
        dpi=RESOLUCION_DPI,
    )

    print("\n" + "=" * 75)
    print("PIPELINE COMPLETADO CON ÉXITO. RESULTADOS DISPONIBLES EN 'src/data/'")
    print("=" * 75)


if __name__ == "__main__":
    # POR QUÉ: El bloque 'if __name__ == "__main__":' garantiza que el pipeline solo
    # se ejecute cuando se invoca este archivo directamente, evitando ejecuciones
    # accidentales si otro módulo importa 'main.py'.
    ejecutar_pipeline_eda()