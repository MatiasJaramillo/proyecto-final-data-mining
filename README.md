# Estructura del proyecto:

'''bash
project-root/
│
├── README.md
├── requirements.txt
├── .gitignore
├── .env.example
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── external/
│
├── notebooks/
│   ├── 01_eda.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_feature_engineering.ipynb
│   ├── 04_model_experimentation.ipynb
│   └── 05_final_evaluation.ipynb
│
├── src/
│   ├── __init__.py
│   │
│   ├── data/
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   ├── load_data.py
│   │   └── sql/
│   │       ├── 00_create_schema.sql
│   │       ├── 01_create_obt.sql
│   │       ├── 02_clean_data.sql
│   │       ├── 03_feature_engineering.sql
│   │       └── 04_time_split.sql
│   │
│   ├── features/
│   │   ├── __init__.py
│   │   ├── build_features.py
│   │   ├── transformers.py
│   │   └── preprocessing_pipeline.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train_model.py
│   │   ├── evaluate_model.py
│   │   ├── predict_model.py
│   │   └── model_registry.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── schemas.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       ├── database.py
│       └── metrics.py
│
├── app/
│   ├── __init__.py
│   └── frontend.py
│
├── models/
│   ├── final_model.pkl
│   ├── preprocessing_pipeline.pkl
│   └── model_metrics.json
│
├── reports/
│   ├── figures/
│   ├── tables/
│   └── final_report.md
│
└── tests/
    ├── test_features.py
    ├── test_model.py
    └── test_api.py
''' 