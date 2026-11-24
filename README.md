# Proyecto_EDA
Proyecto Análisis Exploratorio del Dato (EDA)

# EDA Financiero: Optimización del Capital a Muy Corto Plazo

## Descripción del Proyecto
Este proyecto desarrolla un **Análisis Exploratorio de Datos (EDA)** aplicado al mercado financiero con un propósito social: **determinar en qué activos se debe invertir a muy corto plazo para incrementar el capital de las personas sin exponerlas a la ruina financiera**. 

El estudio contrasta la creencia popular de perseguir activos hipervolátiles frente a la eficiencia real medida por el **Ratio de Sharpe**, el **Valor en Riesgo (VaR al 95%)** y el **Maximum Drawdown**, sentando las bases analíticas para futuros modelos predictivos de gestión inteligente de inversiones.

## Tecnologías Utilizadas
* **Lenguaje:** Python 3.11 (Tipado estático y programación modular).
* **Manipulación y Cálculo Vectorizado:** `pandas`, `numpy`.
* **Visualización de Datos:** `matplotlib`, `seaborn`.
* **Ingesta de Datos:** `yfinance` (API de Yahoo Finance) + datos macroeconómicos de referencia (Banco de España / Tesoro Público).
* **Entorno de Desarrollo:** Visual Studio Code y Jupyter Notebooks.

## Estructura del Repositorio
* `src/main.py`: Script orquestador del pipeline completo.
* `src/variables.py`: Configuración centralizada de constantes y parámetros financieros.
* `src/funciones.py`: Funciones modulares de limpieza, estadística descriptiva y visualización.
* `src/utils/utils.py`: Ingesta resiliente de datos con sistema de caché y respaldo offline.
* `src/data/`: Datasets brutos, limpios, tabla estadística exportada y gráficos en alta resolución.
* `src/docs/guia_proyecto.md`: Documentación detallada de uso y metodología.
* `src/notebooks/explicacion_codigo.ipynb`: Desglose técnico paso a paso del código desarrollado.
* `src/memoria.ipynb`: Memoria ejecutiva completa del Análisis Exploratorio de Datos.

## Ejecución Rápida
```bash
# Ejecutar el análisis completo
python src/main.py
```