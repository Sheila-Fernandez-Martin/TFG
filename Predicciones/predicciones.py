# Cargamos las dependencias
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import seaborn as sns
import datetime
import shutil
import os
from datetime import datetime, timedelta
import networkx as nx
from pgmpy.estimators import HillClimbSearch
from pgmpy.models import BayesianNetwork as DiscreteBayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination
from sklearn.model_selection import train_test_split
import pickle
from funciones_2 import *
from pathlib import Path
import re


days = ['2017-11-09', '2017-11-13', '2017-11-21']


# FUNCIONES AUXILIARES
for i in range(3):
    for letter in ['A', 'B', 'C']:
        DF = pd.read_csv(f'Data\\Test\\{days[i]}\\{days[i]}-{letter}\\{days[i]}-{letter}-sensors.csv', sep=';') 
        sensores = sensors(DF)
        EC = estados_consecutivos(DF,sensores)
        keys = EC.keys()
        for k in keys:
            tiempos_erroneos = EC[k]
            for t in tiempos_erroneos:
                DF = DF[~((DF['TIMESTAMP'] == t[0]) & (DF['OBJECT'] == k) & (DF['STATE'] == t[1]))]
            
        if not os.path.exists(f'Data\\Test2\\{days[i]}\\{days[i]}-{letter}'): 
            os.makedirs(f'Data\\Test2\\{days[i]}\\{days[i]}-{letter}')
            
        DF.to_csv(f'Data\\Test2\\{days[i]}\\{days[i]}-{letter}\\{days[i]}-{letter}-sensors.csv',sep=';', index=False)
        shutil.copy(f'Data\\Test\\{days[i]}\\{days[i]}-{letter}\\{days[i]}-{letter}-acceleration.csv', f'Data\\Test2\\{days[i]}\\{days[i]}-{letter}\\{days[i]}-{letter}-acceleration.csv')
        shutil.copy(f'Data\\Test\\{days[i]}\\{days[i]}-{letter}\\{days[i]}-{letter}-floor.csv', f'Data\\Test2\\{days[i]}\\{days[i]}-{letter}\\{days[i]}-{letter}-floor.csv')
        shutil.copy(f'Data\\Test\\{days[i]}\\{days[i]}-{letter}\\{days[i]}-{letter}-proximity.csv', f'Data\\Test2\\{days[i]}\\{days[i]}-{letter}\\{days[i]}-{letter}-proximity.csv')


# ---------------------------------
# PREPARACIÓN DE LOS DATOS DE TEST
# ---------------------------------

for letter in ["A", "B", "C"]:
    # Lista global de sensores detectados para esta letra
    global_sensors = set()

    for day in days:
        try:
            sen_path = f"Data/Test2/{day}/{day}-{letter}/{day}-{letter}-sensors.csv"
            floor_path = f"Data/Test2/{day}/{day}-{letter}/{day}-{letter}-floor.csv"

            df_sen = pd.read_csv(sen_path, sep=";")
            df_floor = pd.read_csv(floor_path, sep=";")

            # Quitamos dispositivos no deseados
            df_floor = df_floor[~df_floor['DEVICE'].isin(['01,0A', '02,0A', '01,0B'])]

            # Añadimos columna de día 
            df_sen["DAY"] = day
            df_floor["DAY"] = day


            global_sensors.update(df_sen["OBJECT"].unique())

        except FileNotFoundError:
            print(f"Archivos no encontrados para el día {day} - {letter}. Saltando.")
            continue
        
        # Procesar datos
        dic1, dic3, timestamps, timestamps_floor, objects = dicts_s_a(df_sen, df_floor)
        df = sensor_activity(dic1, dic3, timestamps, timestamps_floor, objects, global_sensors)
        df = clean_repeats(df)
        df["DAY"] = day  # mantener día

        # Guardar **cada día y letra** como CSV independiente
        out_dir = f"Predicciones/Data_test/{day}"
        os.makedirs(out_dir, exist_ok=True)

        # Guardar CSV dentro de la carpeta del día
        out_path = f"{out_dir}/{day}-{letter}.csv"
        df.to_csv(out_path, index=False)


# --------
# MODELO
# --------

i,letter= 2,'A'

with open(f"modelo_k2_{letter}.pkl", "rb") as f:
    bn = pickle.load(f)

# Cargamos el conjunto de datos de test 

df_test = pd.read_csv(f'Predicciones\\Data_test\\{days[i]}\\{days[i]}-{letter}.csv', sep=',', index_col=0)
df_test = df_test.drop(columns=['DAY'])


# -------------
# PREDICCIONES
# -------------

model_vars = list(bn.nodes())  # Variables que el modelo sí conoce
model_vars.remove('Activity')  # Queremos predecir esta

infer = VariableElimination(bn)

predictions = []

for _, row in df_test.iterrows():
    # Filtrar solo columnas que están en el modelo
    evidence = row[model_vars].to_dict()
    prediction = infer.map_query(['Activity'], evidence=evidence)
    predictions.append({
        "TIME_BEGIN": row["TIME_BEGIN"],
        "TIME_END": row["TIME_END"],
        "PREDICCION": prediction["Activity"]
    })

# Convertimos a DataFrame
df_predicciones = pd.DataFrame(predictions)

def to_act2(v):
    s = str(v).strip()
    if s == "" or s == "0" or s.lower() == "idle":
        return "Idle"

    # 'Act3', 'act 3', 'ACT03', etc.
    m = re.match(r'(?i)^act\s*(\d+)$', s)  # <- flag (?i) al inicio
    if m:
        return f"Act{int(m.group(1)):02d}"

    # solo número: '3', 3, '22.0', etc.
    try:
        n = int(float(s))
        return f"Act{n:02d}"
    except Exception:
        return s
    
df_predicciones["PREDICCION"] = df_predicciones["PREDICCION"].apply(to_act2)
 
# Calculamos las frecuencias de las predicciones
frecuencias = df_predicciones["PREDICCION"].value_counts().to_dict()

print(f"\033[1;34mPredicciones\033[0m:")
for pred, freq in frecuencias.items():
    print(f"{pred}: {freq} veces")

# asegurar directorio
out_dir = Path("Predicciones") / "Data_predicciones" /str(days[i])
out_dir.mkdir(parents=True, exist_ok=True)

# ruta final del CSV
out_path = out_dir / f"{days[i]}-{letter}-predicciones.csv"
df_predicciones.to_csv(out_path, index=False)


# Ruta del GT: Data\Test2\2017-11-21\2017-11-21-B\2017-11-21-B-activity.csv
gt = pd.read_csv(f'Data\\Test2\\{days[i]}\\{days[i]}-{letter}\\{days[i]}-{letter}-activity.csv', sep=',')

# 1) Cargar GT y tomar el primer timestamp y el número de ventanas (N)

gt["TIMESTAMP"] = pd.to_datetime(gt["TIMESTAMP"], errors="coerce")

gt = gt.dropna(subset=["TIMESTAMP"]).sort_values("TIMESTAMP").reset_index(drop=True)

gt_start = gt["TIMESTAMP"].iloc[0]   # ancla
N        = len(gt)              # nº de ventanas de 30 s en el GT

# 2) Preparar predicciones (df_predicciones): llevar TIME_BEGIN al mismo día del GT
df = df_predicciones.copy()
base_date = gt_start.normalize()  # fecha del GT (00:00)
df["TIME_BEGIN_dt"] = pd.to_datetime(
    base_date.strftime("%Y-%m-%d") + " " + df["TIME_BEGIN"].astype(str),
    errors="coerce"
)
df = df.dropna(subset=["TIME_BEGIN_dt"]).sort_values("TIME_BEGIN_dt").reset_index(drop=True)

# Opcional: descartar predicciones anteriores al inicio del GT
df = df[df["TIME_BEGIN_dt"] >= gt_start].copy()

# 3) Índice de ventana de 30 s respecto al inicio del GT
df["win_idx"] = ((df["TIME_BEGIN_dt"] - gt_start).dt.total_seconds() // 30).astype(int)

# === 4) y 5) y 6) → TOP-2 por duración dentro de cada ventana de 30s ===

# A) Parsear TIME_END al mismo día del GT y asegurar duración mínima
df["TIME_END_dt"] = pd.to_datetime(
    base_date.strftime("%Y-%m-%d") + " " + df["TIME_END"].astype(str),
    errors="coerce"
)
# si TIME_END_dt es NaT, usa TIME_BEGIN_dt
df["TIME_END_dt"] = df["TIME_END_dt"].fillna(df["TIME_BEGIN_dt"])
# si END <= BEGIN, forzamos 1s para que compute duración
mask_bad = df["TIME_END_dt"] <= df["TIME_BEGIN_dt"]
df.loc[mask_bad, "TIME_END_dt"] = df.loc[mask_bad, "TIME_BEGIN_dt"] + pd.to_timedelta(1, unit="s")

# B) Construir rejilla de ventanas [start, end) ancladas al GT
wins = pd.DataFrame({"win_idx": range(N)})
wins["win_start"] = gt_start + pd.to_timedelta(wins["win_idx"] * 30, unit="s")
wins["win_end"]   = wins["win_start"] + pd.Timedelta(seconds=30)

# C) Para cada ventana, sumar duración por etiqueta y quedarnos con el TOP-2
rows = []
for _, w in wins.iterrows():
    w_start, w_end = w["win_start"], w["win_end"]

    # filas que solapan con la ventana
    mask = (df["TIME_END_dt"] > w_start) & (df["TIME_BEGIN_dt"] < w_end)
    sub = df.loc[mask, ["TIME_BEGIN_dt", "TIME_END_dt", "PREDICCION"]].copy()

    if sub.empty:
        rows.append({"TIMESTAPMP": w_start, "Activity_1": "0", "Activity_2": "0"})
        continue

    # recortar a los límites de la ventana
    sub["overlap_start"] = sub["TIME_BEGIN_dt"].clip(lower=w_start)
    sub["overlap_end"]   = sub["TIME_END_dt"].clip(upper=w_end)
    sub["dur"] = (sub["overlap_end"] - sub["overlap_start"]).dt.total_seconds()
    sub.loc[sub["dur"] < 0, "dur"] = 0  # seguridad numérica

    # duración total por actividad
    dur = sub.groupby("PREDICCION", sort=False)["dur"].sum()
    # desempate por aparición más temprana en la ventana
    first_seen = sub.groupby("PREDICCION")["overlap_start"].min()

    # ordenar: mayor duración, y si empatan el que apareció antes
    order = sorted(dur.index, key=lambda k: (-dur[k], first_seen[k]))

    top1 = str(order[0]) if len(order) >= 1 and dur[order[0]] > 0 else "0"
    top2 = str(order[1]) if len(order) >= 2 and dur[order[1]] > 0 else "0"

    rows.append({"TIMESTAPMP": w_start, "Activity_1": top1, "Activity_2": top2})

# D) DataFrame final por ventanas de 30s
df_30s = pd.DataFrame(rows)[["TIMESTAPMP", "Activity_1", "Activity_2"]]

# (Opcional) si quieres solo la hora:
# df_30s["TIMESTAPMP"] = df_30s["TIMESTAPMP"].dt.strftime("%H:%M:%S")

print(df_30s.head(20))

# asegurar directorio
out_dir = Path("Predicciones") / "Data_predicciones" /str(days[i])
out_dir.mkdir(parents=True, exist_ok=True)

# ruta final del CSV
out_path = out_dir / f"{days[i]}-{letter}-predicciones_30s.csv"
df_30s.to_csv(out_path, index=False)

print(f"\n\033[1m=================\033[0m")
print(f"\033[1;32m    Predicciones del modelo\033[0m")
print(f"\033[1m=================\033[0m")
print(df_predicciones.head())
print(df_30s.head(20))


# -----------------------
# EVALUACIÓN DEL MODELO
# -----------------------

# 0) Asegurar tiempos y ordenar
gt["TIMESTAMP"] = pd.to_datetime(gt["TIMESTAMP"], errors="coerce")
df_30s["TIMESTAPMP"] = pd.to_datetime(df_30s["TIMESTAPMP"], errors="coerce")

gt = gt.dropna(subset=["TIMESTAMP"]).sort_values("TIMESTAMP").reset_index(drop=True)
df_30s = df_30s.dropna(subset=["TIMESTAPMP"]).sort_values("TIMESTAPMP").reset_index(drop=True)

# 1) Normalizador de etiquetas: 0/NaN -> 'Idle', números -> 'ActN', resto se deja igual
def norm_label(v):
    if pd.isna(v):
        return "Idle"
    s = str(v).strip()
    if s == "" or s == "0":
        return "Idle"
    try:
        n = int(float(s))
        return f"Act{n}"
    except Exception:
        return s

# 2) Predicciones: mapea tus dos columnas
pred = df_30s.rename(columns={"TIMESTAPMP": "TIMESTAMP"}).copy()
pred["Pred1"] = pred["Activity_1"].apply(norm_label)
pred["Pred2"] = pred["Activity_2"].apply(norm_label)

# 3) Ground truth: toma sus dos columnas
gt_ref = gt.copy()
gt_ref["GT1"] = gt_ref["Activity_1"].apply(norm_label)
gt_ref["GT2"] = gt_ref["Activity_2"].apply(norm_label)

# 4) Unir por TIMESTAMP
comp = pd.merge(
    gt_ref[["TIMESTAMP", "GT1", "GT2"]],
    pred[["TIMESTAMP", "Pred1", "Pred2"]],
    on="TIMESTAMP",
    how="left"
)

# Completar predicciones faltantes con Idle
comp["Pred1"] = comp["Pred1"].fillna("Idle")
comp["Pred2"] = comp["Pred2"].fillna("Idle")

# 5) Acierto si cualquiera coincide
comp["correct"] = (
    (comp["Pred1"] == comp["GT1"]) |
    (comp["Pred1"] == comp["GT2"]) |
    (comp["Pred2"] == comp["GT1"]) |
    (comp["Pred2"] == comp["GT2"])
)

acc = comp["correct"].mean()
print(f"Accuracy 30s (match en cualquiera de las dos): {acc:.2%}")

# (Opcional) primeras discrepancias
errores = comp[~comp["correct"]][["TIMESTAMP", "GT1", "GT2", "Pred1", "Pred2"]]
print("\nPrimeras discrepancias:")
print(errores.head(10))




