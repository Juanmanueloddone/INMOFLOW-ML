import os, hashlib
import numpy as np, pandas as pd
from datetime import datetime, timezone
from sqlalchemy import create_engine

DB_URL = os.environ["DATABASE_URL"]
engine = create_engine(DB_URL)

# ---------- Cargar dataset ----------
df = pd.read_sql("SELECT * FROM public.ml7_dataset_v1 WHERE label IS NOT NULL", engine)
train = df[df.split_bucket=='train'].copy()
valid = df[df.split_bucket=='valid'].copy()
test  = df[df.split_bucket=='test'].copy()

target = "label"

cat_cols_all = [
  'operacion','periodicidad',
  'prov_prop','muni_prop','barrio_prop','tipo_prop',
  'prov_dem','muni_dem','barrio_dem','tipo_dem',
  'moneda_prop','moneda_dem','tier'
]
num_cols_all = [
  'precio_prop','precio_min','precio_max',
  'm2_prop','metros_min','amb_prop','ambientes_min',
  'gap_precio_centro','gap_precio_min','gap_precicio_max','gap_precio_max','ratio_m2',
  'amenities_deseadas_cnt','amenities_prop_cnt','amenities_match_cnt','amenities_match_pct',
  'score_reglas','pos_reglas'
]
# dedup typo si existe
num_cols_all = list(dict.fromkeys(num_cols_all))

cat_cols = [c for c in cat_cols_all if c in train.columns]
num_cols = [c for c in num_cols_all if c in train.columns]

# ---------- Preprocesamiento simple ----------
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

num_tf = Pipeline([("imputer", SimpleImputer(strategy="constant", fill_value=0.0))])
cat_tf = Pipeline([
  ("imputer", SimpleImputer(strategy="most_frequent")),
  ("onehot", OneHotEncoder(handle_unknown="ignore"))
])

pre = ColumnTransformer(
  [("num", num_tf, num_cols), ("cat", cat_tf, cat_cols)],
  remainder="drop"
)

clf = LogisticRegression(max_iter=300, class_weight="balanced")
pipe = Pipeline([("pre", pre), ("clf", clf)])

# Manejar caso extremo sin datos en train
if len(train) == 0 or train[target].nunique() < 2:
    raise RuntimeError("Train vacío o con una sola clase. Necesitamos más datos etiquetados.")

pipe.fit(train, train[target])

def rank_metrics(df_split, scores, k_values=(5,10), group_col='demanda_id'):
    g = df_split.copy()
    g['score'] = scores
    out = {}
    for k in k_values:
        precs, ndcgs = [], []
        for _, grp in g.groupby(group_col):
            grp = grp.sort_values('score', ascending=False)
            labels = grp['label'].tolist()
            top = labels[:k]
            if len(top)==0: 
                continue
            precs.append(np.mean(top))
            # NDCG@K binario
            gains = (2**np.array(top) - 1)
            discounts = 1/np.log2(np.arange(2, 2+len(top)))
            dcg = float(np.sum(gains*discounts))
            ideal_top = sorted(labels, reverse=True)[:k]
            gains_i = (2**np.array(ideal_top) - 1)
            dcg_i = float(np.sum(gains_i*discounts))
            ndcgs.append(dcg/dcg_i if dcg_i>0 else 0.0)
        out[f'P@{k}'] = float(np.mean(precs)) if precs else 0.0
        out[f'NDCG@{k}'] = float(np.mean(ndcgs)) if ndcgs else 0.0
    return out

# AUC defensivo
def safe_auc(y_true, y_score):
    if len(np.unique(y_true)) < 2:
        return float("nan")
    return float(roc_auc_score(y_true, y_score))

p_valid = pipe.predict_proba(valid)[:,1] if len(valid) else np.array([])
p_test  = pipe.predict_proba(test)[:,1]  if len(test)  else np.array([])

auc_valid = safe_auc(valid[target], p_valid) if len(valid) else float("nan")
auc_test  = safe_auc(test[target],  p_test)  if len(test)  else float("nan")
m_valid   = rank_metrics(valid, p_valid) if len(valid) else {}
m_test    = rank_metrics(test,  p_test)  if len(test)  else {}

print("AUC valid:", auc_valid, "| AUC test:", auc_test)
print("Valid:", m_valid)
print("Test :", m_test)

# ---------- Guardar predicciones de TEST ----------
model_version = "ml_v0.1.0_logreg"
features_used_hash = hashlib.sha1("|".join(sorted(num_cols + cat_cols)).encode()).hexdigest()
now = datetime.now(timezone.utc)

pred = test[['demanda_id','propiedad_id','split_bucket']].copy()
pred['score_ml'] = p_test
pred['rank_ml']  = pred.groupby('demanda_id')['score_ml'].rank(ascending=False, method='first')
pred['model_version'] = model_version
pred['features_used_hash'] = features_used_hash
pred['created_at'] = now

with engine.begin() as conn:
    conn.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS public.ml7_baseline_predictions(
          demanda_id uuid,
          propiedad_id uuid,
          split_bucket text,
          score_ml double precision,
          rank_ml double precision,
          model_version text,
          features_used_hash text,
          created_at timestamptz
        );
        TRUNCATE public.ml7_baseline_predictions;
    """)
    pred.to_sql("ml7_baseline_predictions", conn, schema="public", if_exists="append", index=False)

# ---------- Log de métricas del run ----------
metrics_row = {
  "model_version": model_version,
  "features_used_hash": features_used_hash,
  "created_at": now,
  "auc_valid": auc_valid,
  "auc_test": auc_test,
  "valid_P@5": m_valid.get("P@5"),
  "valid_NDCG@5": m_valid.get("NDCG@5"),
  "valid_P@10": m_valid.get("P@10"),
  "valid_NDCG@10": m_valid.get("NDCG@10"),
  "test_P@5": m_test.get("P@5"),
  "test_NDCG@5": m_test.get("NDCG@5"),
  "test_P@10": m_test.get("P@10"),
  "test_NDCG@10": m_test.get("NDCG@10"),
}
metrics_df = pd.DataFrame([metrics_row])

with engine.begin() as conn:
    conn.exec_driver_sql("""
      CREATE TABLE IF NOT EXISTS public.ml7_metrics_runs(
        model_version text,
        features_used_hash text,
        created_at timestamptz,
        auc_valid double precision,
        auc_test double precision,
        valid_P@5 double precision,
        valid_NDCG@5 double precision,
        valid_P@10 double precision,
        valid_NDCG@10 double precision,
        test_P@5 double precision,
        test_NDCG@5 double precision,
        test_P@10 double precision,
        test_NDCG@10 double precision
      );
    """)
    metrics_df.to_sql("ml7_metrics_runs", conn, schema="public", if_exists="append", index=False)

# ---------- (Opcional) copiar a tabla de shadow ----------
if os.environ.get("WRITE_TO_SHADOW","false").lower() == "true":
    with engine.begin() as conn:
        conn.exec_driver_sql("""
          CREATE TABLE IF NOT EXISTS public.match_model_scores (
            demanda_id   uuid NOT NULL,
            propiedad_id uuid NOT NULL,
            score_ml     double precision NOT NULL,
            rank_ml      double precision,
            model_version text NOT NULL,
            features_used_hash text,
            created_at   timestamptz DEFAULT now(),
            PRIMARY KEY (demanda_id, propiedad_id, model_version)
          );
          INSERT INTO public.match_model_scores(demanda_id, propiedad_id, score_ml, rank_ml, model_version, features_used_hash, created_at)
          SELECT demanda_id, propiedad_id, score_ml, rank_ml, model_version, features_used_hash, created_at
          FROM public.ml7_baseline_predictions
          ON CONFLICT (demanda_id, propiedad_id, model_version) DO UPDATE
          SET score_ml = EXCLUDED.score_ml,
              rank_ml = EXCLUDED.rank_ml,
              features_used_hash = EXCLUDED.features_used_hash,
              created_at = EXCLUDED.created_at;
        """)
    print("✔ Copiado a match_model_scores (shadow)")
