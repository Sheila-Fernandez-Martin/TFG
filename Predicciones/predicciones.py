# Cargamos las dependencias
import pandas as pd
import numpy as np 
import shutil
import os
from pgmpy.inference import VariableElimination
import pickle
from funciones_2 import *
from pathlib import Path
import re
from pgmpy.factors.discrete import DiscreteFactor
from functools import reduce
import operator


days = ['2017-11-09', '2017-11-13', '2017-11-21']

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
    all_sensors = []
    all_floors = []
    
    # Creamos una lista para almacenar los sensores detectados
    global_sensors = set()
    devices = [ f"0{i+1},0{j+1}" for i in range(5) for j in range(10) ]
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

            all_sensors.append(df_sen)
            all_floors.append(df_floor)
            global_sensors.update(df_sen["OBJECT"].unique())

            # Procesar datos
            dic1, dic3, timestamps, timestamps_floor, objects = dicts_s_a(df_sen, df_floor)
            df = sensor_activity(dic1, dic3, timestamps, timestamps_floor,  objects, global_sensors)
            #df = clean_repeats(df)
            #df = clean_repeats_activity0(df)
            df["DAY"] = day  # mantener día
            # Guardar **cada día y letra** como CSV independiente
            out_dir = f"Predicciones/Data_test/{day}"
            os.makedirs(out_dir, exist_ok=True)

            # Guardar CSV dentro de la carpeta del día
            out_path = f"{out_dir}/{day}-{letter}.csv"
            df.to_csv(out_path, index=False)

        except FileNotFoundError:
            print(f"Archivos no encontrados para el día {day} - {letter}. Saltando.")
            continue
        
        


# MODELO
# --------

i,letter= 2,'A'

with open(f"modelo_k2_{letter}.pkl", "rb") as f:
    bn = pickle.load(f)

# Cargamos el conjunto de datos de test 

df_test = pd.read_csv(f'Predicciones\\Data_test\\{days[i]}\\{days[i]}-{letter}.csv', sep=',')
df_test = df_test.drop(columns=['DAY'])
#df_test = df_test.drop(columns=['SM3', 'SM4', '01,07', 'D02', 'SM1', 'SM5', 'C14', 'C13'])
#DEVICES = [ f"0{i+1},0{j+1}" for i in range(5) for j in range(9) ]

#df_test = df_test.drop(columns=DEVICES)
#df_test = df_test.drop(columns=['01,10','02,10','03,10','04,10','05,10'])

# -------------
# PREDICCIONES
# -------------
import time
# Variables del modelo (nodos de la BN)
model_vars = list(bn.nodes())
model_vars.remove('Activity')           # objetivo
#PREV_VAR = 'ACTIVITY_ANTERIOR'          # ajusta si se llama distinto
t1 = time.time()
infer = VariableElimination(bn)
#prev_act = 0

# Usaremos solo columnas que existen en el df + no el PREV_VAR (lo ponemos nosotros)
#cols_in_df = [c for c in model_vars if c != PREV_VAR and c in df_test.columns]

def to_int01(x):
    # fuerza 0/1 enteros; trata NaN como 0
    try:
        return int(round(float(x)))
    except Exception:
        return 0

predictions = []

#for _, row in df_test.iterrows():
    # Evidencia base: SOLO variables del modelo presentes en el df, convertidas a int
    #evidence = {c: to_int01(row[c]) for c in cols_in_df}

    # Insertamos la actividad anterior (predicha)
    #evidence[PREV_VAR] = int(prev_act)

    # (Debug opcional) ¿cuánta evidencia activa llevamos?
    # if sum(evidence.values()) == 0:
    #     print("Fila sin evidencia activa, dependerá del prior/transición")

    #pred = infer.map_query(['Activity'], evidence=evidence)
    #act_pred = int(pred['Activity'])

    #predictions.append({
    #    "TIMESTAMP": row["TIMESTAMP"],
    #    "PREDICCION": act_pred
    #})

    #prev_act = act_pred

cpd_act = bn.get_cpds('Activity')
try:
    activity_states = list(cpd_act.state_names['Activity'])
except Exception:
    # Fallback si no hay state_names en el CPD
    if 'Activity' in df_test.columns:
        activity_states = sorted(pd.unique(df_test['Activity'].dropna()))
    else:
        activity_states = list(range(int(cpd_act.variable_card)))

predictions = []

for _, row in df_test.iterrows():
    # Evidencia = todas las variables del modelo salvo 'Activity'
    evidence = row[model_vars].to_dict()

    # Distribución posterior P(Activity | evidencia)
    q = infer.query(variables=['Activity'], evidence=evidence, show_progress=False)
    probs = np.asarray(q.values, dtype=float).ravel()

    # Top-1 y Top-2
    order = np.argsort(probs)[::-1]
    top1 = order[0]
    top2 = order[1] if probs.size > 1 else None

    pred1_state = activity_states[top1]
    pred1_prob  = probs[top1]
    if top2 is not None:
        pred2_state = activity_states[top2]
        pred2_prob  = probs[top2]
    else:
        pred2_state, pred2_prob = None, None

    predictions.append({
        "TIMESTAMP": row["TIMESTAMP"],
        "PREDICCION": pred1_state,
        "PROB1": float(pred1_prob),
        "PREDICCION_2": pred2_state,
        "PROB2": float(pred2_prob) if pred2_prob is not None else None
    })
# Convertimos a DataFrame
df_predicciones = pd.DataFrame(predictions)
t2 = time.time()

print(t2-t1)
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
    

# reutiliza tu función to_act2 para ambos campos
df_predicciones["PREDICCION"]   = df_predicciones["PREDICCION"].apply(to_act2)
df_predicciones["PREDICCION_2"] = df_predicciones["PREDICCION_2"].apply(lambda x: to_act2(x) if pd.notna(x) else x)

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







