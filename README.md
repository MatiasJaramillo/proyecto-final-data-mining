# Estructura del proyecto:

```bash
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