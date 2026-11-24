"""
Módulo: variables.py
Propósito: Centralizar todas las constantes, configuraciones de rutas y parámetros
financieros del proyecto.
Por qué se diseña así: Evita el antipatrón de 'números mágicos' (hardcoding) dispersos
en el código. Si en el futuro cambia la tasa libre de riesgo o se añade un nuevo activo,
solo se modifica este archivo sin tocar la lógica de negocio.
"""

from pathlib import Path
from typing import Dict

# -------------------------------------------------------------------------
# 1. GESTIÓN DE RUTAS CON PATHLIB
# -------------------------------------------------------------------------
# POR QUÉ: Se utiliza 'pathlib.Path' en lugar de concatenar cadenas con '/' o '\'
# porque garantiza compatibilidad multiplataforma (macOS, Linux y Windows) de forma nativa.
RUTA_BASE: Path = Path(__file__).resolve().parent
RUTA_DATOS: Path = RUTA_BASE / "data"
RUTA_DOCS: Path = RUTA_BASE / "docs"
RUTA_GRAFICOS: Path = RUTA_BASE / "data" / "graficos"

# Archivos de salida estáticos
ARCHIVO_DATOS_BRUTOS: Path = RUTA_DATOS / "activos_brutos.csv"
ARCHIVO_DATOS_LIMPIOS: Path = RUTA_DATOS / "activos_limpios.csv"
ARCHIVO_ESTADISTICOS: Path = RUTA_DATOS / "resumen_estadistico.csv"

# -------------------------------------------------------------------------
# 2. UNIVERSO DE INVERSIÓN Y PARÁMETROS TEMPORALES
# -------------------------------------------------------------------------
# POR QUÉ: Se seleccionan activos líquidos que representan distintos perfiles de
# riesgo/beneficio para poder contrastar empíricamente la hipótesis de corto plazo.
TICKERS_ACTIVOS: Dict[str, str] = {
    "SPY": "S&P 500 (Renta Variable EE.UU.)",
    "QQQ": "Nasdaq 100 (Tecnología EE.UU.)",
    "^IBEX": "IBEX 35 (Renta Variable España)",
    "GC=F": "Oro (Valor Refugio)",
    "SHY": "Bonos Corto Plazo 1-3 Años (Bajo Riesgo)",
    "BTC-USD": "Bitcoin (Criptoactivo Alta Volatilidad)"
}

# Rango temporal de estudio (2 años de histórico diario para capturar distintos ciclos de corto plazo)
FECHA_INICIO: str = "2024-01-01"
FECHA_FIN: str = "2026-01-01"

# -------------------------------------------------------------------------
# 3. PARÁMETROS FINANCIEROS Y ESTADÍSTICOS
# -------------------------------------------------------------------------
# POR QUÉ: En finanzas cuantitativas, un año bursátil estándar tiene 252 días de negociación.
# Para evaluar el "muy corto plazo", definimos una ventana móvil de 21 días hábiles (~1 mes natural).
DIAS_BURSATILES_ANIO: int = 252
VENTANA_CORTO_PLAZO: int = 21

# Tasa libre de riesgo anual (basada en Letras del Tesoro Público / BCE: ~3.25%)
TASA_LIBRE_RIESGO_ANUAL: float = 0.0325

# Nivel de confianza para el cálculo del Valor en Riesgo (VaR al 95%)
NIVEL_CONFIANZA_VAR: float = 0.05

# -------------------------------------------------------------------------
# 4. CONFIGURACIÓN ESTÉTICA DE VISUALIZACIÓN
# -------------------------------------------------------------------------
# POR QUÉ: Definir una paleta corporativa y accesible mejora la legibilidad en presentaciones
# ejecutivas ante públicos no técnicos.
ESTILO_GRAFICOS: str = "whitegrid"
PALETA_COLORES: str = "viridis"
RESOLUCION_DPI: int = 300