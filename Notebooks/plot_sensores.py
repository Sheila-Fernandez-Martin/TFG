import matplotlib.pyplot as plt
import pandas as pd
from funciones import *
days = ['2017-10-31', '2017-11-02', '2017-11-03', '2017-11-08', '2017-11-10', '2017-11-15', '2017-11-20']   
# Guardamos en un diccionario que debe tener un sensor para activarse y desactivarse.

sensor_open_close = {
    'C01': {'open': 'Open', 'close': 'Close'}, 
    'C02': {'open': 'Open', 'close': 'Close'}, 
    'C04': {'open': 'Open', 'close': 'Close'}, 
    'C05': {'open': 'Open', 'close': 'Close'}, 
    'C07': {'open': 'No present', 'close': 'Present'}, 
    'C08': {'open': 'Open', 'close': 'Close'}, 
    'C09': {'open': 'Open', 'close': 'Close'}, 
    'C10': {'open': 'Open', 'close': 'Close'}, 
    'C12': {'open': 'No present', 'close': 'Present'}, 
    'C13': {'open': 'Open', 'close': 'Close'}, 
    'C14': {'open': 'Pressure', 'close': 'No Pressure'}, 
    'D01': {'open': 'Open', 'close': 'Close'}, 
    'D02': {'open': 'Open', 'close': 'Close'}, 
    'D03': {'open': 'Open', 'close': 'Close'}, 
    'D04': {'open': 'Open', 'close': 'Close'}, 
    'D05': {'open': 'Open', 'close': 'Close'}, 
    'D07': {'open': 'Open', 'close': 'Close'}, 
    'D08': {'open': 'Open', 'close': 'Close'}, 
    'D09': {'open': 'Open', 'close': 'Close'}, 
    'D10': {'open': 'Open', 'close': 'Close'}, 
    'H01': {'open': 'Open', 'close': 'Close'}, 
    'M01': {'open': 'Open', 'close': 'Close'}, 
    'S09': {'open': 'Pressure', 'close': 'No Pressure'}, 
    'SM1': {'open': 'Movement', 'close': 'No movement'}, 
    'SM3': {'open': 'Movement', 'close': 'No movement'}, 
    'SM4': {'open': 'Movement', 'close': 'No movement'}, 
    'SM5': {'open': 'Movement', 'close': 'No movement'}, 
    'TV0': {'open': 'Open', 'close': 'Close'}
}

def graf_open_close_sensor(i, letter, sensor, dset = 'Training2'):
    df_sensor = pd.read_csv(f"Data/{dset}/{days[i]}/{days[i]}-{letter}/{days[i]}-{letter}-sensors.csv", sep=";")

    # Filtramos solo el sensor
    df_s = df_sensor[df_sensor['OBJECT'] == sensor].copy()
    abrir, cerrar = sensor_open_close[sensor]['open'], sensor_open_close[sensor]['close']


    # Convertimos TIMESTAMP a datetime
    df_s['TIMESTAMP'] = pd.to_datetime(df_s['TIMESTAMP'], format='%Y/%m/%d %H:%M:%S.%f')

    # Asignamos altura según el estado
    df_s['y'] = df_s['STATE'].apply(lambda x: 1 if x.strip() == abrir else 0)
    plt.figure(figsize=(12, 4))

    # Dibujamos los puntos: verdes arriba (open), rojos abajo (close)
    plt.scatter(df_s.loc[df_s['y'] == 1, 'TIMESTAMP'], df_s.loc[df_s['y'] == 1, 'y'],
                color='green', label=abrir, zorder=3)
    plt.scatter(df_s.loc[df_s['y'] == 0, 'TIMESTAMP'], df_s.loc[df_s['y'] == 0, 'y'],
                color='red', label=cerrar, zorder=3)

    # Dibujamos las líneas negras discontinuas entre cada par open -> close
    last_open_time = None
    for idx, row in df_s.iterrows():
        if row['y'] == 1:
            last_open_time = row['TIMESTAMP']
        elif row['y'] == 0 and last_open_time is not None:
            # Línea negra discontinua
            plt.plot([last_open_time, row['TIMESTAMP']], [1, 1], 'k--', linewidth=2, zorder=2)
            # Círculo hueco en el punto final (No movement)
            plt.scatter(row['TIMESTAMP'], 1, facecolors='none', edgecolors='black', s=20, linewidths=2, zorder=2)
            plt.plot([row['TIMESTAMP'], row['TIMESTAMP']], [0, 1], 'k--', linewidth=1, zorder=2, alpha = 0.5)
            last_open_time = None

    plt.yticks([0, 1], [cerrar, abrir])
    plt.xlabel('Tiempo')
    plt.title(f'Activación y desactivación del sensor {sensor}')
    plt.grid(True, axis='x', linestyle=':')
    plt.tight_layout()
    plt.show()

graf_open_close_sensor(0,'A','C14')