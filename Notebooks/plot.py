import matplotlib.pyplot as plt
import pandas as pd
from funciones import *

devices = [ f"0{i+1},0{j+1}" for i in range(5) for j in range(10) ]  # Asumiendo 5 filas y 9 columnas

days = ['2017-10-31', '2017-11-02', '2017-11-03', '2017-11-08', '2017-11-10', '2017-11-15', '2017-11-20']   
sorted_activities = ['Act01', 'Act02', 'Act03', 'Act04', 'Act05', 'Act06', 'Act07', 'Act08', 'Act09', 'Act10', 'Act11', 'Act12', 'Act13', 'Act14', 'Act15', 'Act16', 'Act17', 'Act18', 'Act19', 'Act20', 'Act21', 'Act22', 'Act23', 'Act24']
freq = {act: {dev: 0 for dev in devices} for act in sorted_activities}
# Contar la frecuencia de cada dispositivo por actividad
for day in days:
    for letter in ['A', 'B', 'C']:
        df_floor = pd.read_csv(f"Data/Training2/{day}/{day}-{letter}/{day}-{letter}-floor.csv", sep=";")
        actividades = pd.read_csv(f"Data/Training2/{day}/{day}-{letter}/{day}-{letter}-activity.csv", sep=";")

        # Convertir TIMESTAMP a datetime
        df_floor['TIMESTAMP'] = pd.to_datetime(df_floor['TIMESTAMP'], errors='coerce')
        actividades['DATE BEGIN'] = pd.to_datetime(actividades['DATE BEGIN'], errors='coerce')
        actividades['DATE END'] = pd.to_datetime(actividades['DATE END'], errors='coerce')

        # Eliminamos las filas de floor con DEVICE '02,0A' o '01,0A'
        df_floor = df_floor[~df_floor['DEVICE'].isin(['02,0A', '01,0A'])]

        devic_day = list(df_floor['DEVICE'])
        timestamp_day = list(df_floor['TIMESTAMP'])

        activ_day = actividades['ACTIVITY'].unique()
        # Creamos un diccionario para almacenar los intervalos de cada actividad
        dic2 = {act: [] for act in activ_day}
        # Iteramos sobre las actividades y sus intervalos
        for i in range(len(actividades)):
            act = actividades.loc[i, 'ACTIVITY']
            start = actividades.loc[i, 'DATE BEGIN']
            end = actividades.loc[i, 'DATE END']
            dic2[act].append((start, end))

        # Iteramos sobre el data frame de floor
        for i in range(len(df_floor)):
            # Miramos que device esta y que actividad esta
            device = devic_day[i]
            timestamp = timestamp_day[i]
            
            # Comprobamos si el timestamp está dentro de algún intervalo de actividad
            for act, intervals in dic2.items():
                for start, end in intervals:
                    if start <= timestamp <= end:
                        freq[act][device] += 1

# Normalizamos las frecuencias
max_freq = max(max(freq[act].values()) for act in freq)
for act in freq:
    for dev in freq[act]:
        freq[act][dev] = 100*freq[act][dev]/max_freq
# Definimos el dataframe conteo de frecuencias
# Definimos el DataFrame con 3 variables: 'Activity', 'DEVICE' y 'Count'
conteo = pd.DataFrame([(act, dev, freq[act][dev]) for act in sorted_activities for dev in devices],
                      columns=['Activity', 'DEVICE', 'Count'])
# Asegurar que DEVICE se separa en dos coordenadas X,Y (asumiendo "02,05" significa x=2, y=5)
# conteo[['X', 'Y']] = conteo['DEVICE'].str.split(',', expand=True).astype(int)
# Extraer solo dígitos en X y Y (por ejemplo "0A" -> "0")
conteo[['X_raw', 'Y_raw']] = conteo['DEVICE'].str.split(',', expand=True)

# Extraer solo los dígitos (remover letras)
conteo['X'] = conteo['X_raw'].str.extract('(\d+)').astype(int)
conteo['Y'] = conteo['Y_raw'].str.extract('(\d+)').astype(int)


actividades_filtradas = ['Act02', 'Act03', 'Act04', 'Act22']
conteo_filtrado = conteo[conteo['Activity'].isin(actividades_filtradas)]

# Número de actividades para definir el grid de subplots
acts = conteo_filtrado['Activity'].unique()
n_acts = len(acts)
cols = 2  # número de columnas en el grid
rows = (n_acts + cols - 1) // cols

fig, axes = plt.subplots(rows, cols, figsize=(cols*4, rows*4))
axes = axes.flatten()
colores = {
    'Act02': 'red',
    'Act03': 'green',
    'Act04': 'orange',
    'Act22': 'purple'
}

for idx, act in enumerate(sorted(acts)):
    ax = axes[idx]
    df_act = conteo_filtrado[conteo_filtrado['Activity'] == act]
    ax.scatter(df_act['X'], df_act['Y'], s=df_act['Count']*8, alpha=0.6, color=colores[act])
    ax.set_title(act, fontsize=12)
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 10.5)
    ax.set_xticks(range(1, 6))
    ax.set_yticks(range(1, 11))

# Quitar ejes vacíos si los hay
for i in range(idx+1, len(axes)):
    fig.delaxes(axes[i])

plt.tight_layout()
plt.show()
