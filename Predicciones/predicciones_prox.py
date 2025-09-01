# Cargamos las dependencias
import pandas as pd
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

def round_prox_ts_with_date(series: pd.Series) -> pd.Series:
    """
    Convierte TIMESTAMP a datetime, redondea al segundo y devuelve
    'YYYY/MM/DD HH:MM:SS' (manteniendo la fecha).
    Soporta entradas como:
      - '2017/11/09 16:52:31.761'
      - '2017-11-09 16:52:31.761'
      - Timestamp ya parseado
    """
    s = series.astype(str).str.strip()

    # Normaliza casos raros tipo 'HH:MM:SS:ms' -> 'HH:MM:SS.ms' (por si aparecen)
    s = s.str.replace(r":(?=\d{1,6}$)", ".", regex=True)

    # Intento general
    dt = pd.to_datetime(s, errors="coerce")

    # Fallback con formato más estricto si hiciera falta
    mask_nat = dt.isna()
    if mask_nat.any():
        try:
            dt.loc[mask_nat] = pd.to_datetime(
                s[mask_nat],
                format="%Y/%m/%d %H:%M:%S.%f",
                errors="coerce"
            )
        except Exception:
            pass  # si no encaja, se queda NaT

    # Redondeo a segundo y formateo con fecha
    return dt.dt.round("s").dt.strftime("%Y/%m/%d %H:%M:%S")


for i in range(3):
    for letter in ['A', 'B', 'C']:
        src_base = f"Data\\Test\\{days[i]}\\{days[i]}-{letter}"
        dst_base = f"Data\\Test2\\{days[i]}\\{days[i]}-{letter}"
        os.makedirs(dst_base, exist_ok=True)

        # --- sensors (tu lógica existente) ---
        DF = pd.read_csv(f"{src_base}\\{days[i]}-{letter}-sensors.csv", sep=';')
        sensores = sensors(DF)
        EC = estados_consecutivos(DF, sensores)
        for k, tiempos_erroneos in EC.items():
            for t in tiempos_erroneos:
                DF = DF[~((DF['TIMESTAMP'] == t[0]) & (DF['OBJECT'] == k) & (DF['STATE'] == t[1]))]
        DF.to_csv(f"{dst_base}\\{days[i]}-{letter}-sensors.csv", sep=';', index=False)

        # --- acceleration y floor: copiar tal cual ---
        shutil.copy(f"{src_base}\\{days[i]}-{letter}-acceleration.csv",
                    f"{dst_base}\\{days[i]}-{letter}-acceleration.csv")
        shutil.copy(f"{src_base}\\{days[i]}-{letter}-floor.csv",
                    f"{dst_base}\\{days[i]}-{letter}-floor.csv")

        # --- PROXIMITY: leer, redondear a segundo conservando FECHA, guardar ---
        df_prox = pd.read_csv(f"{src_base}\\{days[i]}-{letter}-proximity.csv", sep=';')
        df_prox["TIMESTAMP"] = round_prox_ts_with_date(df_prox["TIMESTAMP"])
        df_prox.to_csv(f"{dst_base}\\{days[i]}-{letter}-proximity.csv", sep=';', index=False)



# ---------------------------------
# PREPARACIÓN DE LOS DATOS DE TEST
# ---------------------------------

for letter in ["A", "B", "C"]:
    # Lista global de sensores detectados para esta letra
    all_sensors = []
    all_floors = []
    all_objects_prox = []
    
    # Creamos una lista para almacenar los sensores detectados
    global_sensors = set()
    global_sensors_prox = set()
    devices = [ f"0{i+1},0{j+1}" for i in range(5) for j in range(10) ]
    for day in days:
        try:
            sen_path = f"Data/Test2/{day}/{day}-{letter}/{day}-{letter}-sensors.csv"
            floor_path = f"Data/Test2/{day}/{day}-{letter}/{day}-{letter}-floor.csv"
            prox_path = f"Data/Test2/{day}/{day}-{letter}/{day}-{letter}-proximity.csv"

            df_sen = pd.read_csv(sen_path, sep=";")
            df_floor = pd.read_csv(floor_path, sep=";")
            df_prox = pd.read_csv(prox_path, sep=";")

            # Quitamos dispositivos no deseados
            df_floor = df_floor[~df_floor['DEVICE'].isin(['01,0A', '02,0A', '01,0B'])]

            # Añadimos columna de día 
            df_sen["DAY"] = day
            df_floor["DAY"] = day
            df_prox["DAY"] = day

            all_sensors.append(df_sen)
            all_floors.append(df_floor)
            all_objects_prox.append(df_prox)
            global_sensors_prox.update(df_sen["OBJECT"].unique())
            global_sensors.update(df_sen["OBJECT"].unique())

            # Procesar datos
            dic1, dic3, dic4, timestamps, timestamps_floor, timestamps_prox, objects = dicts_s_a_prox(df_sen, df_floor, df_prox)
            df = sensor_activity_prox(dic1, dic3, dic4, timestamps, timestamps_floor,  timestamps_prox, objects, global_sensors)
            #df = clean_repeats(df)
            df = clean_repeats_activity0(df)
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
        
        


# --------
# MODELO
# --------

i,letter= 0,'A'

with open(f"modelo_k2_{letter}.pkl", "rb") as f:
    bn = pickle.load(f)

# Cargamos el conjunto de datos de test 

df_test = pd.read_csv(f'Predicciones\\Data_test\\{days[i]}\\{days[i]}-{letter}.csv', sep=',')
df_test = df_test.drop(columns=['DAY'])
#df_test = df_test.drop(columns=['SM3', 'SM4', '01,07', 'D02', 'SM1', 'SM5', 'C14', 'C13'])

# -------------
# PREDICCIONES
# -------------

# Variables del modelo (nodos de la BN)
model_vars = list(bn.nodes())
model_vars.remove('Activity')           # objetivo
#PREV_VAR = 'ACTIVITY_ANTERIOR'          # ajusta si se llama distinto

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

for _, row in df_test.iterrows():
    # Filtrar solo columnas que están en el modelo
    evidence = row[model_vars].to_dict()
    prediction = infer.map_query(['Activity'], evidence=evidence)
    predictions.append({
        #"TIME_BEGIN": row["TIME_BEGIN"],
        #"TIME_END": row["TIME_END"],
        "TIMESTAMP": row["TIMESTAMP"],
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
