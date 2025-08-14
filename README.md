# Reconocimiento de Actividades Humanas con Redes Bayesianas

Este proyecto forma parte del Trabajo de Fin de Grado en Matemáticas y tiene como objetivo **identificar actividades humanas** en un entorno inteligente utilizando **redes Bayesianas**.  
Se trabaja con datos reales recogidos por sensores, un suelo inteligente, balizas BLE y un reloj inteligente, registrando 24 actividades distintas.


## 📂 Estructura del proyecto

├── 01_analisis_limpieza.ipynb # Análisis exploratorio y limpieza de datos
├── 02_preparacion_datos.py # Generación de datasets limpios y equilibrados
├── funciones.py # Funciones auxiliares para el preprocesado
├── 03_model.py # Modelo con Hill Climbing + BIC
├── 03_modelo_K2.py # Modelo Hill Climbing + K2 score
├── 03_modelo_TreeSearch.py # Modelo TreeSearch
├── 04_Model.ipynb # Análisis y resultados del mejor modelo
├── /Red Bayesiana/Data/ # Datos preparados (data_A.csv, data_B.csv, data_C.csv)
└── README.md # Este documento


## 📊 Flujo de trabajo

1. **Análisis y limpieza de datos**  (`01_analisis_limpieza.ipynb`)
   - Carga de datos sensoriales (*sensors.csv* y *floor.csv*) y de actividad *activity.csv*.   
   - Eliminación de redundancias y ruido.  
   - Homogeneización de formatos de tiempo y dispositivos.

2. **Preparación de datasets** (`02_preparacion_datos.py`)  
   - Generación de tres conjuntos (`data_A.csv`, `data_B.csv`, `data_C.csv`), cada uno correspondiente a un tramo del día y guardados dentro de la carpeta `Red Bayesiana`.
   - Balanceo para evitar sobre-representación de actividades frecuentes.
   - Conversión de lecturas a vectores binarios de los sensores y a un número entre 0-24 en el caso de las actividades.

3. **Modelado con Redes Bayesianas**  
   Se han probado tres aproximaciones:
   - **Hill Climbing + BIC** (`03_model.py`)
   - **Hill Climbing + K2** (`03_modelo_K2.py`)
   - **TreeSearch** (`03_modelo_TreeSearch.py`)

   Los modelos se entrenan con `MaximumLikelihoodEstimator` y se evalúan con *Variable Elimination* para predicción.

4. **Selección del mejor modelo**  
   El notebook `04_Model.ipynb` analiza las métricas y selecciona el modelo con mejor rendimiento.


