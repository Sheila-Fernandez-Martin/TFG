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

FLOOR_SOFA = {
    # Sofá en la parte superior izquierda (filas 01–02, cols 01–04)
    "01,01","01,02","01,03","01,04",
    "02,01","02,02","02,03","02,04","WATER BOTTLE","BOOK","SM5"
}

FLOOR_TABLE = {
    # Mesa/zona de trabajo hacia el centro-superior (filas 01–02, cols 05–06)
    "01,05","01,06","01,07",
    "02,05","02,06","02,07","WATER BOTTLE","BOOK","SM5"
}

FLOOR_ENTRANCE = {
    # Entrada arriba a la derecha (aprox. 01,10)
    "01,10","01,08","01,09",
    "02,10","02,08","ENTRANCE DOOR","02,09"
}

FLOOR_BED = {
    # Cama parte inferior izquierda (filas 03–04, cols 01–03)
    "03,01","03,02","03,03","03,04",
    "04,01","04,02","04,03","04,04","WATER BOTTLE","BOOK","SM4"
}

FLOOR_BATHROOM = {
    # Baño en la franja inferior-central (filas 03–04, cols 05–06)
    "03,05","03,06",
    "04,05","04,06","WATER BOTTLE","SM3"
}

FLOOR_KITCHEN = {
    # Cocina a la derecha (filas 02–03, cols 08–10)
    #"02,09","02,10",
    "03,07","03,08","03,09","03,10",
    "04,07","04,08","04,09","04,10","SM1","WATER BOTTLE"
}

# ----------------------------
# DICCIONARIO ACTIVIDAD -> SENSORES (objetos + suelo)
# ----------------------------
ACTIVITY_SENSORS = {
    0 : {'C01', 'C02', 'C04', 'C05', 'C07', 'C08', 'C09', 'C10',
        'C12', 'C13', 'C14', 'D01', 'D02', 'D03', 'D04', 'D05',
        'D07', 'D08', 'D09', 'D10', 'H01', 'M01', 'S09',
        'TV0',"ACTIVITY_ANTERIOR"} | FLOOR_TABLE | FLOOR_SOFA | FLOOR_BED | FLOOR_BATHROOM | FLOOR_ENTRANCE | FLOOR_KITCHEN,
    1: {"C01", "C14","D04","MEDICINE BOX","BED","FRIDGE","ACTIVITY_ANTERIOR","04,09", '04,08', '04,07', '03,09',"WATER BOTTLE", "SM1","SM3","SM4","SM5"}, # Take medication TODAS LAS ESTANCIAS MENOS ENTRADA                                                        # Take medication
    2: {"D01","D02","D10","C04","H01","POT DRAWER","FRIDGE","FOOD CUPBOARD","SM3",'04,09', '04,08', '03,09',"WATER BOTTLE","SM1"},            # Prepare breakfast COCINA
    3: {"D01","D02","D10","C04","POT DRAWER","FRIDGE","FOOD CUPBOARD",'03,09', '04,09', '03,08', '04,08',"WATER BOTTLE","SM1"},                  # Prepare lunch COCINA
    4: {"D01","D02","D10","C04","C09","02,08","POT DRAWER","FRIDGE","FOOD CUPBOARD",'03,09', '04,09', '04,08','01,07',"WATER BOTTLE","SM1"},                  # Prepare dinner COCINA
    5: {"C02","C05", "POT DRAWER","FRIDGE","FOOD CUPBOARD", '04,06', '04,07', '04,08','01,07',"WATER BOTTLE","SM1","D10"}, # Breakfast COCINA/TABLE/SALON/DORMITORIO
    6: {"C02","C05","POT DRAWER","FRIDGE","FOOD CUPBOARD",'01,07', '04,07', '04,06', '04,08',"WATER BOTTLE","SM1"}, # Lunch COCINA/TABLE/SALON/DORMITORIO
    7: {"C02","C05","POT DRAWER","FRIDGE","FOOD CUPBOARD",'04,07', '01,07', '04,08', '04,06',"WATER BOTTLE","SM1"}, # Dinner COCINA/TABLE/SALON/DORMITORIO
    8: {"C02","C05","POT DRAWER","FRIDGE","FOOD CUPBOARD",'04,09', '04,08', '04,07', '02,02',"WATER BOTTLE","SM1","SM4","SM5"}, # Eat a snack 
    9: {"TV0","S09","TV CONTROLLER",'01,03', '01,04', '01,07', '02,03',"WATER BOTTLE","SM5"},                   # Watch TV SOFA/TABLE
    10: {"M01","01,10","01,08","01,09","02,10","02,08","02,09","02,07","BED",'01,09', '01,08', '01,07', '02,08',"WATER BOTTLE"},   # Enter the SmartLab ENTRADA
    11: {"C07","S09","TV CONTROLLER","04,04",'01,07', '01,03', '02,03', '01,04',"WATER BOTTLE","SM5"},                  # Play a videogame 
    12: {"TV CONTROLLER","S09",'01,07', '01,03', '01,04', '01,05',"WATER BOTTLE","SM5"},                                      # Relax on the sofa
    13: {"M01",'01,09', '01,08', '01,07', '02,08',"WATER BOTTLE"},                                  # Leave the SmartLab
    14: {"M01","S09", "C14","BED",'01,08', '01,09', '01,03', '01,04',"WATER BOTTLE"}, # Visit in the SmartLab
    15: {"C08","GARBAGE CAN",'03,07', '03,08', '01,09', '01,08',"WATER BOTTLE","SM1","SM3","SM4","SM5"},# | FLOOR_BATHROOM | FLOOR_BED | FLOOR_TABLE, # Put waste in the bin
    16: {"C09",'04,04', '03,04', '04,05', '03,05',"WATER BOTTLE","SM3"},                  # Wash hands 
    17: {"C09","BATHROOM TAP","TOOTHBRUSH",'04,04', '03,04', '04,05', '03,05',"WATER BOTTLE","SM3"},  # Brush teeth
    18: {"C10","BATHROOM TAP","D07",'04,04', '04,05', '01,07', '03,04',"WATER BOTTLE","SM3"} ,                            # Use the toilet
    19: {"D05","POT DRAWER","FRIDGE","FOOD CUPBOARD",'04,09', '04,08', '01,07', '04,06',"WATER BOTTLE","SM1"} ,                                   # Wash dishes
    20: {"D09","LAUNDRY BASKET",'04,08', '04,07', '04,09', '01,07',"WATER BOTTLE","SM1","D03"},                  # Put washing into the washing machine
    21: {'01,07', '01,05', '01,06',"WATER BOTTLE","SM5"},                                     # Work at the table
    22: {"C12","C13","D03","D08","WARDROBE DOOR","C14","PYJAMA DRAWER","BED","LAUNDRY BASKET",'03,02', '03,03', '03,01', '04,08',"WATER BOTTLE","SM4","SM3"},     # Dressing
    23: {"C14","SM3","C13","04,05","03,06","WARDROBE DOOR","PYJAMA DRAWER","03,05","BED",'04,02', '01,07', '04,01', '03,02',"WATER BOTTLE","SM4"},     # Go to the bed
    24: {"C14","BED","SM3",'04,02', '01,07', '04,01', '04,03',"SM4","SM1","SM3"},                                       # Wake up
}

for letter in ["A", "B", "C"]:
    # Creamos dos listas para almacenar los DataFrames de actividades y sensores
    all_activities = []
    all_sensores = []
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
            all_sensores.append(df_sen)
            all_floors.append(df_floor)
            global_sensors.update(df_sen["OBJECT"].unique())

        except FileNotFoundError:
            print(f"Archivos no encontrados para el día {day} - {letter}. Saltando.")
            continue
    
    # Creamos una lista de df que estarán en el formato correcto
    DATA = []
    for i in range(len(days)):
        activities = all_activities[i]
        sensors = all_sensores[i]
        floor = all_floors[i]
        
        dic1, dic2, dic3, timestamps, timestamps_floor, t1, t2, objects = dicts_s_a(sensors, activities, floor)
        # Creamos un DataFrame con los datos
        df = sensor_activity(dic1, dic2, dic3, timestamps, timestamps_floor, t1, t2, objects, global_sensors)
        #df, error_counter, error_by_activity, bad_rows = check_errors(df, ACTIVITY_SENSORS, fix=True)
        df= clean_repeats(df) 
        #df = clean_repeats_activity0(df) #comprime solo las 0

        # Añadimos el DataFrame a la lista
        DATA.append(df)

        # Añadimos la columna de día al DataFrame
        df["DAY"] = days[i]
    
    # Unimos todos los DataFrames por filas en uno solo
    final_df = pd.concat(DATA, ignore_index=True)
    #final_df["Activity"] = pd.to_numeric(final_df["Activity"], errors="coerce").fillna(0).astype(int)
    #final_df["ACTIVITY_ANTERIOR"] = final_df["Activity"].shift(1, fill_value=0).astype(int)
    #cols = list(final_df.columns)
    #cols.insert(cols.index("Activity")+1, cols.pop(cols.index("ACTIVITY_ANTERIOR")))
    #final_df = final_df[cols]   
    # Guardamos el DataFrame en un archivo CSV
    final_df.to_csv(f'Red Bayesiana/Data/data_{letter}.csv', index=False)



