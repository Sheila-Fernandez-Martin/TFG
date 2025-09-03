# Cargamos los paquetes necesarios
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pgmpy.estimators import HillClimbSearch
from pgmpy.models import BayesianNetwork as DiscreteBayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
import pickle

# MODELO K2  
# -------------------------
# PREPARACIÓN DE LOS DATOS
# -------------------------

letter = 'A'  # Cambiar según la letra
# Cargamos los datos
df = pd.read_csv(f'Red Bayesiana\\Data\\data_{letter}.csv', sep=',')

# Eliminamos la ultima columna que no contiene información relevante
df = df.drop(columns=['DAY'])
#DEVICES = [ f"0{i+1},0{j+1}" for i in range(5) for j in range(9) ]

#df = df.drop(columns=DEVICES)
#df = df.drop(columns=['01,10','02,10','03,10','04,10','05,10'])
#print(df)

# ----------------------------
# ZONAS DE SUELO
# ----------------------------
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
    1: {"C01", "C14","D04","MEDICINE BOX","BED","FRIDGE","ACTIVITY_ANTERIOR"}|FLOOR_KITCHEN|FLOOR_BED|FLOOR_BATHROOM|FLOOR_SOFA|FLOOR_TABLE, # Take medication TODAS LAS ESTANCIAS MENOS ENTRADA                                                        # Take medication
    2: {"D01","D02","D10","C04","H01","POT DRAWER","FRIDGE","FOOD CUPBOARD"} | FLOOR_KITCHEN,            # Prepare breakfast COCINA
    3: {"D01","D02","D10","C04","POT DRAWER","FRIDGE","FOOD CUPBOARD"} | FLOOR_KITCHEN,                  # Prepare lunch COCINA
    4: {"D01","D02","D10","C04","C09","02,08","POT DRAWER","FRIDGE","FOOD CUPBOARD"} | FLOOR_KITCHEN,                  # Prepare dinner COCINA
    5: {"C02","C05", "POT DRAWER","FRIDGE","FOOD CUPBOARD"} |FLOOR_KITCHEN, # Breakfast COCINA/TABLE/SALON/DORMITORIO
    6: {"C02","C05","POT DRAWER","FRIDGE","FOOD CUPBOARD"} | FLOOR_KITCHEN, # Lunch COCINA/TABLE/SALON/DORMITORIO
    7: {"C02","C05","POT DRAWER","FRIDGE","FOOD CUPBOARD"} | FLOOR_TABLE | FLOOR_KITCHEN, # Dinner COCINA/TABLE/SALON/DORMITORIO
    8: {"C02","C05","POT DRAWER","FRIDGE","FOOD CUPBOARD"} | FLOOR_KITCHEN|FLOOR_SOFA, # Eat a snack 
    9: {"TV0","S09","TV CONTROLLER"} | FLOOR_SOFA | FLOOR_TABLE,                   # Watch TV SOFA/TABLE
    10: {"M01","01,10","01,08","01,09","02,10","02,08","02,09","02,07","BED"} | FLOOR_KITCHEN|FLOOR_BED|FLOOR_BATHROOM|FLOOR_SOFA|FLOOR_TABLE,   # Enter the SmartLab ENTRADA
    11: {"C07","S09","TV CONTROLLER","04,04"} | FLOOR_SOFA,                  # Play a videogame 
    12: {"TV CONTROLLER","S09"} | FLOOR_SOFA,                                      # Relax on the sofa
    13: {"M01"} | FLOOR_ENTRANCE,                                  # Leave the SmartLab
    14: {"M01","S09", "C14","BED"} | FLOOR_TABLE | FLOOR_SOFA | FLOOR_BED | FLOOR_BATHROOM | FLOOR_ENTRANCE | FLOOR_KITCHEN, # Visit in the SmartLab
    15: {"C08","GARBAGE CAN"} | FLOOR_KITCHEN,# | FLOOR_BATHROOM | FLOOR_BED | FLOOR_TABLE, # Put waste in the bin
    16: {"C09"} | FLOOR_BATHROOM,                  # Wash hands 
    17: {"C09","BATHROOM TAP","TOOTHBRUSH"} | FLOOR_BATHROOM,  # Brush teeth
    18: {"C10","BATHROOM TAP","D07"} | FLOOR_BATHROOM,                            # Use the toilet
    19: {"D05","POT DRAWER","FRIDGE","FOOD CUPBOARD"} | FLOOR_KITCHEN,                                   # Wash dishes
    20: {"D09","LAUNDRY BASKET"} | FLOOR_KITCHEN | FLOOR_BATHROOM,                  # Put washing into the washing machine
    21: {"SM1"} | FLOOR_TABLE,                                     # Work at the table
    22: {"C12","C13","D03","D08","WARDROBE DOOR","C14","PYJAMA DRAWER","BED","LAUNDRY BASKET"} | FLOOR_BED | FLOOR_BATHROOM,     # Dressing
    23: {"C14","SM3","C13","04,05","03,06","WARDROBE DOOR","PYJAMA DRAWER","03,05","BED"} | FLOOR_BED,                                       # Go to the bed
    24: {"C14","BED"} | FLOOR_BED,                                       # Wake up
}
from collections import Counter, defaultdict

def check_errors(df, ACTIVITY_SENSORS):
    error_counter = Counter()
    error_by_activity = defaultdict(Counter)
    bad_rows = set()

    for idx, row in df.iterrows():
        activity = row["Activity"]
        allowed = set(ACTIVITY_SENSORS.get(activity, []))
        active_sensors = [
            col for col in df.columns
            if col not in ["Activity","DAY"] and row[col] == 1
        ]
        for sensor in active_sensors:
            if sensor not in allowed:
                bad_rows.add(idx)
                error_counter[sensor] += 1
                error_by_activity[activity][sensor] += 1

    return error_counter, error_by_activity, bad_rows


# --- 1ª pasada: detectar errores ---
error_counter, error_by_activity, bad_rows = check_errors(df, ACTIVITY_SENSORS)

# --- 4. Resumen general ---
print("\n--- Resumen de sensores mal colocados (ordenados) ---")
for sensor, count in error_counter.most_common():
    print(f"{sensor}: {count}")
    # Mostrar el desglose por actividad
    for activity, counter in error_by_activity.items():
        if sensor in counter:
            print(f"    {activity}: {counter[sensor]}")
print(f"\nFilas con errores: {len(bad_rows)}")
threshold = 40
sensors_to_drop = [sensor for sensor, count in error_counter.items() if count > threshold]
df_clean = df.drop(columns=sensors_to_drop)

print(f"Sensores eliminados: {sensors_to_drop}")

# --- 3ª pasada: comprobar de nuevo ---
error_counter2, error_by_activity2, bad_rows2 = check_errors(df_clean, ACTIVITY_SENSORS)

#for sensor, count in error_counter2.most_common():
#    print(f"{sensor}: {count}")
    # Mostrar el desglose por actividad
#    for activity, counter in error_by_activity2.items():
#        if sensor in counter:
#            print(f"    {activity}: {counter[sensor]}")
print(f"\nFilas con errores: {len(bad_rows2)}")

# Lista de variables en tu dataset
#variables = df.columns.tolist()

# Nodo objetivo
#target_node = 'Activity'

# Crear lista negra de aristas salientes desde el nodo objetivo
#black_list = [(target_node, var) for var in variables if var != target_node]




















df = df_clean
#df = df.drop(columns=['SM1','SM3','SM4','SM5'])
# Eliminamos las filas que tienen un valor 0 en la columna 'Activity'
df = df[df['Activity'] != 0] 
# --------
# MODELO
# --------
import time

# Aprender la estructura de la red bayesiana
hc = HillClimbSearch(df)
t1 = time.time()

model = hc.estimate(scoring_method='k2score', max_indegree=20)
t2 = time.time()

print(t2-t1)


# Visualización de la estructura aprendida
G = nx.DiGraph(model.edges())
plt.figure(figsize=(10, 8))
nx.draw(G, with_labels=True, node_color="#87CEFA", edge_color='gray', node_size=2000, font_size=12)
plt.title("Estructura aprendida (DAG)")
plt.show()

# Ajustar el modelo a los datoss
bn = DiscreteBayesianNetwork(model.edges())
bn.fit(df, estimator=MaximumLikelihoodEstimator)

# Guardar modelo entrenado
with open(f"modelo_k2_{letter}.pkl", "wb") as f:
    pickle.dump(bn, f)

