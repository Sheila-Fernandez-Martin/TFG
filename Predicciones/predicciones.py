# Cargamos las dependencias
import pandas as pd
import shutil
import os
from pgmpy.inference import VariableElimination
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


            global_sensors.update(df_sen["OBJECT"].unique())

            # Procesar datos
            dic1, dic3, timestamps, timestamps_floor, objects = dicts_s_a(df_sen, df_floor)
            df = sensor_activity(dic1, dic3, timestamps, timestamps_floor, objects, global_sensors)
            #df = clean_repeats(df)
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

i,letter= 0,'C'

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







