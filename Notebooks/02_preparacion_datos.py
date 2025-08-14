import pandas as pd
from funciones import *

r"""
Este script se encarga de crear una red base de datos sencilla y legible para el modelo a partir de los datos de actividades y sensores.

Esta base de datos se realiza a partir de los datos de entrenamiento, que se encuentran en la carpeta `../Data/Training2/`. Guardara en cada fila un vector de sensores binarios y la actividad que se realiza en ese momento. Además, esta base de datos no contiene redundancias y tampoco da prioridad a actividades que se repiten en el tiempo, ya que se considera que todas las actividades son igualmente importantes. 

Los datos los guardaremos en 3 archivos CSV en la carpeta `../Model/Data/`. Estos archivos serán:
`data_A.csv`, `data_B.csv`, y `data_C.csv`, donde cada uno corresponde a un momento del día (A, B, C) y contiene las actividades y sensores correspondientes a ese momento.
"""
# Tomamos el training
days = ['2017-10-31', '2017-11-02', '2017-11-03', '2017-11-08', '2017-11-10', '2017-11-15', '2017-11-20']

for letter in ["A", "B", "C"]:
    # Creamos dos listas para almacenar los DataFrames de actividades y sensores
    all_activities = []
    all_sensors = []
    all_floors = []
    
    # Creamos una lista para almacenar los sensores detectados
    global_sensors = set()
    devices = [ f"0{i+1},0{j+1}" for i in range(5) for j in range(10) ]  # Asumiendo 5 filas y 9 columnas

    for day in days:
        try:
            act_path = f"Data/Training2/{day}/{day}-{letter}/{day}-{letter}-activity.csv"
            sen_path = f"Data/Training2/{day}/{day}-{letter}/{day}-{letter}-sensors.csv"
            floor_path = f"Data/Training2/{day}/{day}-{letter}/{day}-{letter}-floor.csv"

            df_act = pd.read_csv(act_path, sep=";")
            df_sen = pd.read_csv(sen_path, sep=";")
            df_floor = pd.read_csv(floor_path, sep=";")

            # Eliminamos las filas de floor con device '01,'0A' y '02,0A'
            df_floor = df_floor[~df_floor['DEVICE'].isin(['01,0A', '02,0A', '01,0B'])]

            # Añadimos columna de día por si queremos rastrear luego
            df_act["DAY"] = day
            df_sen["DAY"] = day
            df_floor["DAY"] = day

            all_activities.append(df_act)
            all_sensors.append(df_sen)
            all_floors.append(df_floor)
            global_sensors.update(df_sen["OBJECT"].unique())
        except FileNotFoundError:
            print(f"Archivos no encontrados para el día {day} - {letter}. Saltando.")
            continue
    
    # Creamos una lista de df que estarán en el formato correcto
    DATA = []
    for i in range(len(days)):
        activities = all_activities[i]
        sensors = all_sensors[i]
        floor = all_floors[i]
        
        dic1, dic2, dic3, timestamps, timestamps_floor, t1, t2, objects = dicts_s_a(sensors, activities, floor)
        # Creamos un DataFrame con los datos
        df = sensor_activity(dic1, dic2,dic3, timestamps, timestamps_floor, t1, t2, objects, global_sensors)
        df= clean_repeats(df)
        
        # Eliminamos las filas tales que tiene un valor 0 en la columna 'Activity'
        # df = df[df['Activity'] != 0]
        # Añadimos el DataFrame a la lista
        DATA.append(df)

        # Añadimos la columna de día al DataFrame
        df["DAY"] = days[i]
    
    # Unimos todos los DataFrames por filas en uno solo
    final_df = pd.concat(DATA, ignore_index=True)
    # Guardamos el DataFrame en un archivo CSV
    final_df.to_csv(f'Red Bayesiana/Data/data_{letter}.csv', index=False)
