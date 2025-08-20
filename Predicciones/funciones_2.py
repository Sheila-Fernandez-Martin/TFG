from datetime import datetime, timedelta
import pandas as pd
import os

def enumerate_seconds(start_time_str, end_time_str):
    r"""
    Enumerates all seconds in the interval between two timestamps.
    Arguments:
        start_time_str -- Start time in the format 'HH:MM:SS.ssssss'.
        end_time_str -- End time in the format 'HH:MM:SS.ssssss'.
    Returns:
        output -- A list of strings representing each second in the interval, formatted as 'HH:MM:SS'.
    """
    output = []
    # Define the format of the input timestamps
    time_format1 = "%H:%M:%S"
    time_format2 = "%H:%M:%S.%f"

    try:
        # Try to parse the input strings with microseconds
        start_time = datetime.strptime(start_time_str, time_format2)
        end_time = datetime.strptime(end_time_str, time_format2)
    except ValueError:
        # If it fails, parse without microseconds
        start_time = datetime.strptime(start_time_str, time_format1)
        end_time = datetime.strptime(end_time_str, time_format1)
    
    # Generate all seconds in the interval
    current_time = start_time
    while current_time <= end_time:
        output.append(current_time.strftime("%H:%M:%S"))
        current_time += timedelta(seconds=1)
    return(output)

def create_bit_vector(sorted_list,elements):
    r"""
    Creates a bit vector from a sorted list and a set of elements.
    Arguments:
        sorted_list -- A sorted list of elements.
        elements -- A set of elements to check against the sorted list.
    Returns:
        output -- A list of 1s and 0s, where 1 indicates the element is in the sorted list and 0 indicates it is not.
    """
    output = []
    for i in sorted_list:
        if i in elements:
            output.append(1)
        else:
            output.append(0)
    return output

def load_file(day, letter, file_type='acceleration', dset='Training'):
    """
    Loads a file from the specified day and letter.
    Arguments:
        day -- The day of the data to load.
        letter -- The letter associated with the data.
        file_type -- The type of file to load (default is 'acceleration').
        dset -- The dataset to use (default is 'Training').
    Returns:
        df -- A DataFrame containing the loaded data.
    """
    # Construct the file path
    file_path = f'../Data/{dset}/{day}/{day}-{letter}/{day}-{letter}-{file_type}.csv'
    
    if os.path.exists(file_path):
        return pd.read_csv(file_path, sep=';', encoding='utf-8')
    else:
        raise FileNotFoundError(f"El archivo {file_path} no existe.")

def dicts_s_a(sensors, floor):
    """
    Creates a dictionary with keys the timestamps and values the activity and sensors at that time.
    Arguments:
        sensors -- A DataFrame containing sensor data with columns 'TIMESTAMP', 'OBJECT', and 'STATE'.
        activities -- A DataFrame containing activity data with columns 'DATE BEGIN', 'DATE END', and 'ACTIVITY'.
    Returns:
        data -- A dictionary with timestamps as keys and a list of sensor states and activities as values.
    """
    
    timestamps = [x.split(" ")[1] for x in sensors["TIMESTAMP"].to_list()]
    # Crea una lista con los sensores del df sensors
    objects = sensors["OBJECT"].to_list()
    # Crea una lista con los estados del df sensors
    states = sensors["STATE"].to_list()

    timestamps_floor = [x.split(" ")[1] for x in floor["TIMESTAMP"].to_list()]

    # Ponemos ambos timestamps en el mismo formato: 'HH:MM:SS'
    timestamps = [x.split(".")[0] for x in timestamps]
    timestamps_floor = [x.split(".")[0] for x in timestamps_floor]

    suelos = floor["DEVICE"].to_list()
    # Crea una lista con los dispositivos del df floor
    devices = [f"{i+1:02d},{j+1:02d}" for i in range(5) for j in range(10)]  # Asumiendo 5 filas y 9 columnas
    
    # Crea dic1 para los sensores y dic2 para actividades 
    dic1,dic3 = {},{}

    for s in set(objects):
        dic1[s] = []

    for d in set(devices):
        dic3[d] = set()

    # A dic1 le asocia como claves los sensores y como valores una lista de tuplas (estado, hora)
    for i in range(len(timestamps)):
        dic1[objects[i]].append((states[i],timestamps[i]))

    # A dic3 le asocia como claves los dispositivos y como valores una lista de tuplas (hora)
    for i in range(len(timestamps_floor)):
        dic3[suelos[i]].add(timestamps_floor[i])

    #for d in devices:
    #    dic3[d] = sorted(list(dic3[d]))

    return dic1, dic3, timestamps, timestamps_floor, objects

def sensor_activity(dic1, dic3, timestamps, timestamps_floor, objects, global_sensors):
    """
    Creates a dictionary with keys the timestamps and values the activity and sensors at that time.
    Arguments:
        sensors -- A dictionari.
        activities -- A DataFrame containing activity data with columns 'DATE BEGIN', 'DATE END', and 'ACTIVITY'.
    """

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
    tbegin,tend = min(timestamps[0],timestamps_floor[0]),max(timestamps[-1],timestamps_floor[-1])
    # Convertimos 
    data = {}

    for t in enumerate_seconds(tbegin,tend):
        active_devices = []
        for device in dic3:
            if t in dic3[device]:
                active_devices.append(device)
        data[t] = active_devices


    for elem in dic1:
        events = dic1[elem]

        if len(events) > 1:
                for i in range(len(events)-1):
                    if i==0: 
                        if events[i][0] == sensor_open_close[elem]['close']:
                            start_time = tbegin
                            end_time = events[i][1]
                            for t in enumerate_seconds(start_time, end_time):
                                if t in data:
                                    data[t].append(elem) 

                    elif events[i][0] == sensor_open_close[elem]['open']:
                        start_time = events[i][1]
                        end_time = events[i + 1][1]
                        for t in enumerate_seconds(start_time, end_time):
                            if t in data:
                                data[t].append(elem)

                if events[-1][0] == sensor_open_close[elem]['open']:
                    start_time = events[i][1]
                    end_time = tend
                    for t in enumerate_seconds(start_time, end_time):
                        if t in data:
                            data[t].append(elem)


    data_pd = []
    all_s = [
        'C01', 'C02', 'C04', 'C05', 'C07', 'C08', 'C09', 'C10',
        'C12', 'C13', 'C14', 'D01', 'D02', 'D03', 'D04', 'D05',
        'D07', 'D08', 'D09', 'D10', 'H01', 'M01', 'S09',
        'SM1', 'SM3', 'SM4', 'SM5', 'TV0'
    ]
    sorted_list_of_sensors = sorted(all_s)
    devices = [f"{i+1:02d},{j+1:02d}" for i in range(5) for j in range(10)]  # Asumiendo 5 filas y 9 columnas
    for t in enumerate_seconds(tbegin,tend):
        # Crea una lista binaria + número de actividad
        data_pd.append(create_bit_vector(sorted_list_of_sensors+devices,data[t][:])+[t])
    df = pd.DataFrame(data_pd, columns=sorted_list_of_sensors+devices+['TIMESTAMP'])
    return df

def clean_repeats2(df):
    df = df.copy()

    # Convertir TIMESTAMP a datetime si no lo es
    if not pd.api.types.is_datetime64_any_dtype(df['TIMESTAMP']):
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])

    grouped_rows = []
    start_idx = 0

    for i in range(1, len(df)):
        # Comparar fila actual con la anterior (excepto TIMESTAMP)
        if not df.iloc[i].drop(labels='TIMESTAMP').equals(df.iloc[i-1].drop(labels='TIMESTAMP')):
            row_data = df.iloc[start_idx].drop(labels='TIMESTAMP').to_dict()
            row_data['TIME_BEGIN'] = df.iloc[start_idx]['TIMESTAMP'].strftime("%H:%M:%S")
            row_data['TIME_END'] = df.iloc[i-1]['TIMESTAMP'].strftime("%H:%M:%S")
            row_data['DAY'] = df.iloc[start_idx]['TIMESTAMP'].strftime("%Y-%m-%d")
            grouped_rows.append(row_data)
            start_idx = i

    # Guardar el último bloque
    row_data = df.iloc[start_idx].drop(labels='TIMESTAMP').to_dict()
    row_data['TIME_BEGIN'] = df.iloc[start_idx]['TIMESTAMP'].strftime("%H:%M:%S")
    row_data['TIME_END'] = df.iloc[len(df)-1]['TIMESTAMP'].strftime("%H:%M:%S")
    row_data['DAY'] = df.iloc[start_idx]['TIMESTAMP'].strftime("%Y-%m-%d")
    grouped_rows.append(row_data)

    return pd.DataFrame(grouped_rows).reset_index(drop=True)

# Miramos los sensores que tenemos
def sensors(DF):
    return list(set(DF['OBJECT']))

# Para cada sensor analizamos si se activan y dejan de activar correctamente
def estados_consecutivos(DF, sensors):
    # Para cada sensor, creamos un diccionario que almacena los sensores con lecturas erróneas.
    EC = {sensor: [] for sensor in sensors}
    for sensor in sensors:
        object, state, time = list(DF['OBJECT']), list(DF['STATE']), list(DF['TIMESTAMP'])

        last_state = -1
        for i in range(len(object)):
            # Si el objeto es el sensor que estamos analizando
            if object[i] == sensor:

                if last_state == -1: 
                    last_state = i

                elif state[last_state] != state[i]:
                    # Si el estado ha cambiado nos situamos en el siguiente intervalo
                    last_state = i

                elif state[last_state] == state[i]:
                    # Si el estado no ha cambiado --> hay un error en la lectura
                    EC[sensor].append((time[i], state[i]))

    
    for sensor in sensors:
        # Eliminamos los sensores que no tienen errores de lectura
        if len(EC[sensor]) == 0: del EC[sensor]
    return EC

def clean_repeats(df):
    """
    Cleans the DataFrame by removing repeated following rows. Moreover, it adds two new columns:
    'TIME_BEGIN' and 'TIME_END', which represent the start and end times of the activity.
    Arguments:
        df -- A DataFrame with sensor states.
    Returns:
        df_cleaned -- A cleaned DataFrame with no repeated following rows.
    """
    df_cleaned = df.copy()
    # Iterate through the DataFrame and remove repeated rows
    remove_indices = []
    time_begin = []
    time_end = []
    t0 = df_cleaned.iloc[0]['TIMESTAMP']
    t1 = t0
    # We get the TIMESTAMP column as a list
    timestamps = df_cleaned['TIMESTAMP'].tolist()
    # We remove the TIMESTAMP column from the DataFrame
    df_cleaned = df_cleaned.drop(columns=['TIMESTAMP'])

    for i in range(len(df_cleaned) - 1):

        # Check if the current row is equal to the next row
        if df_cleaned.iloc[i].equals(df_cleaned.iloc[i + 1]):
            remove_indices.append(i + 1)
            t1 = timestamps[i + 1]

        else:
            # If they are not equal, store the time_begin and time_end
            time_begin.append(t0)
            time_end.append(t1)
            t0 = timestamps[i + 1]
            t1 = t0
            
    # Add the last time_begin and time_end
    time_begin.append(t0)
    time_end.append(timestamps[-1])
    # Remove the repeated rows
    df_cleaned.drop(index=remove_indices, inplace=True)
    # Add time_begin and time_end columns
    df_cleaned['TIME_BEGIN'] = time_begin
    df_cleaned['TIME_END'] = time_end
    
    return df_cleaned.reset_index(drop=True)