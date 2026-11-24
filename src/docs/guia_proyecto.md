# Guía Técnica y Funcional del Proyecto (Documentación de Usuario y Desarrollador)

## 1. En qué consiste el proyecto
El presente proyecto aborda el problema de la vulnerabilidad financiera mediante datos empíricos. Muchas personas con bajo capital buscan rentabilidades explosivas a muy corto plazo (semanas o un mes) atraídas por activos especulativos. Este análisis descriptivo evalúa matemáticamente seis clases de activos (`SPY`, `QQQ`, `^IBEX`, `GC=F`, `SHY` y `BTC-USD`) en ventanas móviles de **21 sesiones bursátiles (1 mes natural)** para descubrir qué activos incrementan realmente el patrimonio protegiendo al ciudadano de pérdidas irreversibles.

## 2. Origen y Codificación de los Datasets (`src/data/`)
Todos los archivos están codificados en estándar **UTF-8** separados por comas (`.csv`):
1. `activos_brutos.csv`: Precios de cierre ajustados por dividendos y *splits* descargados de Yahoo Finance (`yfinance`). Índice temporal en formato ISO `YYYY-MM-DD`.
2. `activos_limpios.csv`: Serie temporal depurada sin fechas duplicadas, ordenada cronológicamente y con valores ausentes imputados mediante *Forward Fill* (`ffill`) para evitar el sesgo de anticipación (*look-ahead bias*).
3. `resumen_estadistico.csv`: Matriz de resultados descriptivos con 11 indicadores clave por activo (Retorno medio y mediano mensual, Probabilidad de ganancia mensual, VaR 95%, Volatilidad anualizada, Ratio de Sharpe, Maximum Drawdown, Asimetría y Curtosis).

## 3. Instrucciones de Uso en Visual Studio Code
1. Abra la carpeta raíz del proyecto en **Visual Studio Code**.
2. Para regenerar todos los datos y gráficos desde la terminal integrada, ejecute:
   `python src/main.py`
3. Para explorar la narrativa analítica interactiva, abra `src/memoria.ipynb` y pulse **Run All** en la barra superior de VS Code.
4. Para revisar la arquitectura interna del código bloque por bloque, abra `src/notebooks/explicacion_codigo.ipynb`.