# Proyecto Final: Predicción de Precios (End-to-End ML con Big Data)

Este repositorio es la plantilla oficial para el proyecto final. 

> [!WARNING]
> **Arquitectura para Grandes Volúmenes (Big Data):** 
> Procesamiento de **~20GB** de información de viajes. Tratar de descargar toda la data e intentar usar un `train_test_split` tradicional en Pandas o Scikit-Learn saturará su memoria RAM al instante. Por tanto, el corazón de la limpieza estructurada, el ensamble de la OBT y la división Train/Test **se ejecutará del lado de Snowflake mediante SQL**. 

El proyecto está segmentado de la siguiente manera para su evaluación:

*   **PSet #4**: Investigación técnica. Creación del documento técnico (monografía) y exposición sobre el algoritmo de Boosting que se le asignó a su equipo. Algoritmos en paralelo.
*   **Proyecto Final (PSet #5)**: Implementación, experimentación y despliegue del modelo punto a punto.

---

## Objetivo General del Proyecto Final

Deberán conectarse a **Snowflake** para consumir la One Big Table (`analytics.obt_trips`), empujando el cómputo primario a la base de datos (Pushdown Computation), realizar el proceso de de exploración en muestras, estructurar el modelado (*Out-of-Core Training* o por *Lotes*), empaquetarlo en código productivo modular Python y servirlo mediante una API base con FastAPI.

---

## Flujo de Trabajo

### 1. Modelado de Datos
En la subcarpeta `src/data/sql/` estructurarán la lógica de cruce masivo.
1. Script para materializar la OBT unificada.
2. Script para separar los datos (`train_set` 2015-2023, `val_set` 2024, `test_set` 2025).

### 2. Preparación y Exploración
No carguen toda la base. Usen directivas SQL como `SAMPLE` o `LIMIT` mientras evalúan.
1.  **`01_eda.ipynb`**: Realicen Análisis Exploratorio en un **sample**. Identifiquen outliers y Data Leakage.
2.  **`02_data_cleaning.ipynb`**: Validen reglas lógicas en pandas y **traspasen su código estructural a sus queries SQL** en la DB.
3.  **`03_feature_engineering.ipynb`**: Creen variables complejas espacio-temporales.

### 3. Experimentación (Out-of-Core)
**`04_model_experimentation.ipynb`**: Entrenen modelos. Para ensambles y boostings, investiguen sobre la iteración por lotes (`batch training`, iteradores en XGBoost/LightGBM) o tomen la mayor submuestra representativa que soporte la memoria de sus máquinas. Seleccionen el mejor según RMSE.

### 4. Refactorización de Produccion
Migrar el Jupyter a los scripts definitivos en `src/`.
1.  Copiar la lógica de recolección de *chunks* a `src/data/ingestion.py`.
2.  Pipeline definitivo en `src/features/`.
3.  Lógica de `partial_fit` / batch en `src/models/train_model.py`.

### 5. API y Front End
El producto no es un Jupyter, es un software que usará un usuario final interactivo.
1. **Back-end de ML**: Levantar la aplicación web que envuelve al `.pkl` ejecutando:  
   `uvicorn src.api.main:app --reload`
2. **Interfaz de Usuario**: Desarrollar en `app/frontend.py` la interfaz gráfica usando **Streamlit**. El usuario final introducirá datos básicos del viaje y este conectará a la API.  
   Para correr el servidor web, asegúrese de estar en la raíz de su terminal y ejecutar:
   `streamlit run app/frontend.py`

---

## Estructura

```text
├── data/               # Archivos prohibidos en Git (.gitignore) y modelos (.pkl)
├── notebooks/          # Exploración interactivo (usar MUESTRAS)
│   ├── 01_eda.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_feature_engineering.ipynb
│   └── 04_model_experimentation.ipynb
├── src/                # Código fuente de Producción
│   ├── data/           
│   │   ├── sql/        # Scripts SQL obligatorios para la DB (Pushdown)
│   │   └── ingestion.py # Iterador de descargas
│   ├── features/       # Transformadores sklearn
│   ├── models/         # Entrenamiento modular y por batch
│   ├── api/            # API del modelo (FastAPI)
│   └── utils/          
├── app/                # Carpeta para el Frontend final
│   └── frontend.py     # Aplicación interactiva en Streamlit
├── tests/              # Pruebas unitarias
├── .env.example        
├── requirements.txt    
└── README.md           
```

---

## Rúbrica de Evaluación

### **PSet #4: Investigación Técnica (100 Puntos Totales)**
Focalizado puramente en la curva teórica y estudio en profundidad del ecosistema de Boosting.

| Criterio | Puntaje | Descripción |
| :------- | :---: | :---------- |
| **Documento Técnico (PDF)** | **50 pts** | Formulación matemática, seudocódigo del algoritmo, manejo de categóricas/nulos nativos, parámetros clave de regularización, pitfalls e impacto de `learning_rate` vs `n_estimators`. Extensión ~4-6 hojas. |
| **Presentación y Defensa** | **50 pts** | Claridad en la exposición grupal, respuestas precisas a la audiencia y capacidad analítica frente al por qué usar su boosting frente a un simple Random Forest. |

### **Proyecto Final: Implementación y Productivización (100 Puntos Totales)**
El cierre del curso. Evalúa la capacidad técnica end-to-end simulando la realidad de MLOps.

| Etapa del Desarrollo (Parte Técnica - 70 Puntos) | Puntaje | Descripción |
| :------- | :---: | :---------- |
| **Data Engineering (SQL)** | 15 pts | Correcta construcción de la OBT en Snowflake, filtros limpios y *Time-Based splits* construidos del lado de la base de datos (0 Leakage). |
| **Experimentación y Ensambles** | 25 pts | Construcción estricta de Voting/Bagging/Pasting, y tuning *Out-of-Core* o en lotes de todos los Boostings (`AdaBoost`, `GradientBoosting`, `XGBoost`, `LightGBM`, `CatBoost`). |
| **Métricas Obtenidas** | 15 pts | Evaluación basada en el RMSE del Test Set. Se otorga puntaje completo a quienes superen la regresión baseline y alcancen el P90 de la clase. |
| **Software y Despliegue** | 15 pts | Código 100% modular en `src/`, FastAPI activa devolviendo predicciones correctas y Frontend de Streamlit amigable consumiendo a la API sin fallos de interfaz. |

| Defensa Final (30 Puntos) | Puntaje | Descripción |
| :------- | :---: | :---------- |
| **Validación de Conceptos** | 30 pts | Los alumnos pueden explicar todo el proyecto |

> [!CAUTION]
> **Penalizaciones Críticas del Proyecto Final**
> - **Data Leakage**: Incluir variables exclusivas del cierre del viaje en el input o usar test para tunear o elegir el modelo. (-50 pts y RMSE invalidado)
> - **No Usar Muestras/Lotes**: Tratar de descargar los 20GB en un DF local de Pandas causando saturación (-50 pts).
> - **Faltante de Algoritmos**: No incluir alguno de los Boostings obligatorios (-10 pts por modelo faltante).
