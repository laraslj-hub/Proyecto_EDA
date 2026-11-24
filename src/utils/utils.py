"""
Módulo: utils.py
Propósito: Proporcionar funciones auxiliares de infraestructura (creación de carpetas,
descarga resiliente de datos desde APIs e inyección de datos sintéticos de respaldo).
Por qué se diseña así: Aísla las operaciones de Entrada/Salida (I/O) y llamadas de red
del análisis matemático. Si falla la conexión a Internet durante una presentación en vivo,
el sistema conmuta automáticamente a un generador determinista o al archivo CSV local.
"""

from pathlib import Path
from typing import Dict
import numpy as np
import pandas as pd

try:
    import yfinance as yf
    YFINANCE_DISPONIBLE = True
except ImportError:
    YFINANCE_DISPONIBLE = False


def inicializar_directorios(rutas: list[Path]) -> None:
    """
    Verifica y crea las carpetas necesarias del proyecto si no existen.
    
    POR QUÉ: Evita errores 'FileNotFoundError' cuando el script intenta guardar
    archivos CSV o imágenes PNG en un entorno recién clonado desde GitHub.
    """
    for ruta in rutas:
        ruta.mkdir(parents=True, exist_ok=True)


def generar_datos_respaldo(
    tickers: Dict[str, str],
    fecha_inicio: str,
    fecha_fin: str
) -> pd.DataFrame:
    """
    Genera series temporales financieras realistas mediante Movimiento Browniano Geométrico
    en caso de no disponer de conexión a Internet o fallo en la API externa.
    
    POR QUÉ: Garantiza un 100% de reproducibilidad (principio de resiliencia en demos).
    Se fija una semilla aleatoria (seed=42) para que cualquier desarrollador obtenga
    exactamente los mismos resultados estadísticos si trabaja sin conexión.
    """
    np.random.seed(42)
    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq="B")  # 'B' = Días hábiles
    n_dias = len(fechas)

    # Parámetros realistas diarios (media de retorno diario, volatilidad diaria, precio inicial)
    parametros_simulados = {
        "SPY": (0.00045, 0.0095, 470.0),
        "QQQ": (0.00060, 0.0130, 400.0),
        "^IBEX": (0.00038, 0.0090, 10100.0),
        "GC=F": (0.00035, 0.0075, 2050.0),
        "SHY": (0.00014, 0.0015, 82.0),
        "BTC-USD": (0.00120, 0.0340, 42000.0),
    }

    datos = {}
    for ticker in tickers.keys():
        mu, sigma, precio_inicial = parametros_simulados.get(ticker, (0.0003, 0.01, 100.0))
        # Simulación vectorizada de retornos logarítmicos con colas pesadas (distribución t-Student)
        choques = np.random.standard_t(df=5, size=n_dias) * (sigma / np.sqrt(5 / 3))
        retornos = mu + choques
        precios = precio_inicial * np.exp(np.cumsum(retornos))
        datos[ticker] = precios

    df = pd.DataFrame(datos, index=fechas)
    df.index.name = "Date"

    # Introducimos intencionadamente un 1% de valores nulos y 2 filas duplicadas
    # POR QUÉ: Permite demostrar de forma transparente la eficacia del módulo de limpieza de datos.
    mascara_nulos = np.random.rand(*df.shape) < 0.01
    df = df.mask(mascara_nulos)
    df = pd.concat([df, df.iloc[:2]])  # Duplicados artificiales para validación de limpieza

    return df


def obtener_datos_financieros(
    tickers: Dict[str, str],
    fecha_inicio: str,
    fecha_fin: str,
    ruta_guardado: Path
) -> pd.DataFrame:
    """
    Descarga los precios de cierre ajustados desde Yahoo Finance o carga el respaldo local.
    
    POR QUÉ: Implementa un patrón de caché local ('Cache-Aside'). Si el archivo bruto ya
    fue descargado previamente, lo lee del disco en milisegundos en lugar de saturar la API.
    """
    if ruta_guardado.exists():
        print(f"[INFO] Cargando datos brutos desde almacenamiento local: {ruta_guardado.name}")
        return pd.read_csv(ruta_guardado, index_col="Date", parse_dates=True)

    df_bruto = pd.DataFrame()

    if YFINANCE_DISPONIBLE:
        try:
            print("[INFO] Conectando con la API de Yahoo Finance para descargar series históricas...")
            lista_tickers = list(tickers.keys())
            descarga = yf.download(
                lista_tickers,
                start=fecha_inicio,
                end=fecha_fin,
                auto_adjust=True,
                progress=False
            )
            if not descarga.empty and "Close" in descarga:
                df_bruto = descarga["Close"].copy()
        except Exception as error:
            print(f"[ADVERTENCIA] Fallo en la descarga desde API ({error}). Activando respaldo...")

    if df_bruto.empty:
        print("[INFO] Generando dataset financiero de respaldo para ejecución determinista...")
        df_bruto = generar_datos_respaldo(tickers, fecha_inicio, fecha_fin)

    df_bruto.to_csv(ruta_guardado)
    print(f"[INFO] Datos brutos guardados exitosamente en: {ruta_guardado}")
    return df_bruto