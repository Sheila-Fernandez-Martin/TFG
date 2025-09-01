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

def dicts_s_a_prox(sensors, floor, proximity):
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
    #if states[0] == sensor_open_close[objects[0]]['close']:
    #    timestamps.pop(0)  # Remove the first timestamp if the first state is 'close'
    #    objects.pop(0)  # Remove the first object if the first state is 'close'
    #    states.pop(0)  # Remove the first state if the first state is 'close'
    #if states[-1] == sensor_open_close[objects[-1]]['open']:
    #    timestamps.pop(-1)
    #    objects.pop(-1)  # Remove the last object if the last state is 'open'
    #    states.pop(-1)  # Remove the last state if the last state is 'open'
    timestamps_floor = [x.split(" ")[1] for x in floor["TIMESTAMP"].to_list()]
    # Redondear al segundo más cercano
    timestamps_prox = [x.split(" ")[1] for x in proximity["TIMESTAMP"].to_list()]

    # Ponemos ambos timestamps en el mismo formato: 'HH:MM:SS'
    timestamps = [x.split(".")[0] for x in timestamps]
    timestamps_floor = [x.split(".")[0] for x in timestamps_floor]
    timestamps_prox = [x.split(".")[0] for x in timestamps_prox]


    suelos = floor["DEVICE"].to_list()
    objects_prox = proximity["OBJECT"].to_list()
    # Crea una lista con los dispositivos del df floor
    devices = [f"{i+1:02d},{j+1:02d}" for i in range(5) for j in range(10)]  # Asumiendo 5 filas y 9 columnas
    
    # Crea dic1 para los sensores y dic2 para actividades 
    dic1,dic3,dic4 = {},{},{}

    for s in set(objects):
        dic1[s] = []

    for d in set(devices):
        dic3[d] = []

    for p in set(objects_prox):
        dic4[p] = []

    # A dic1 le asocia como claves los sensores y como valores una lista de tuplas (estado, hora)
    for i in range(len(timestamps)):
        dic1[objects[i]].append((states[i],timestamps[i]))
        
    # A dic3 le asocia como claves los dispositivos y como valores una lista de tuplas (hora)
    for i in range(len(timestamps_floor)):
        dic3[suelos[i]].append((timestamps_floor[i]))

    # A dic4 le asocia como claves los dispositivos y como valores una lista de tuplas (hora)
    for i in range(len(timestamps_prox)):
        dic4[objects_prox[i]].append((timestamps_prox[i]))

    return dic1, dic3, dic4, timestamps, timestamps_floor, timestamps_prox, objects

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
    #if states[0] == sensor_open_close[objects[0]]['close']:
    #    timestamps.pop(0)  # Remove the first timestamp if the first state is 'close'
    #    objects.pop(0)  # Remove the first object if the first state is 'close'
    #    states.pop(0)  # Remove the first state if the first state is 'close'
    #if states[-1] == sensor_open_close[objects[-1]]['open']:
    #    timestamps.pop(-1)
    #    objects.pop(-1)  # Remove the last object if the last state is 'open'
    #    states.pop(-1)  # Remove the last state if the last state is 'open'
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
        dic3[d] = []

    # A dic1 le asocia como claves los sensores y como valores una lista de tuplas (estado, hora)
    for i in range(len(timestamps)):
        dic1[objects[i]].append((states[i],timestamps[i]))
        
    # A dic3 le asocia como claves los dispositivos y como valores una lista de tuplas (hora)
    for i in range(len(timestamps_floor)):
        dic3[suelos[i]].append((timestamps_floor[i]))

    return dic1, dic3, timestamps, timestamps_floor, objects

def sensor_activity_prox(dic1, dic3, dic4, timestamps, timestamps_floor, timestamps_prox, objects, global_sensors):
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

    tbegin,tend = min(timestamps[0],timestamps_floor[0],timestamps_prox[0]),max(timestamps[-1],timestamps_floor[-1],timestamps_prox[-1])
    #tbegin,tend = t1[0],t2[-1] NO GENERA CAMBIOS

    # Convertimos 
    data = {}

    #for t in enumerate_seconds(tbegin,tend):
    #    activity = getActivity(dic2, t)
    #    active_devices = [device for device, times in dic3.items() if t in times]
    #    if len(active_devices) != 0:
    #        data[t] = [activity] + active_devices
    #    else:
    #        data[t] = [activity]

    for t in enumerate_seconds(tbegin, tend):
        active_devices = []
        for dic in (dic3, dic4):
            active_devices.extend([device for device, times in dic.items() if t in times])
        if len(active_devices) != 0:
            data[t] = active_devices
        else:
            data[t] = []

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
    all_objects_prox = all_objects_prox_df()
    sorted_list_of_sensors_prox = sorted(all_objects_prox)
    devices = [f"{i+1:02d},{j+1:02d}" for i in range(5) for j in range(10)]  # Asumiendo 5 filas y 9 columnas
    for t in enumerate_seconds(tbegin,tend):
        # Crea una lista binaria + número de actividad
        data_pd.append(create_bit_vector(sorted_list_of_sensors+devices+sorted_list_of_sensors_prox,data[t][:])+[t])
    df = pd.DataFrame(data_pd, columns=sorted_list_of_sensors+devices+sorted_list_of_sensors_prox+['TIMESTAMP'])
    return df

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
    #tbegin,tend = t1[0],t2[-1] NO GENERA CAMBIOS

    # Convertimos 
    data = {}

    for t in enumerate_seconds(tbegin, tend):
        active_devices = []
        active_devices.extend([device for device, times in dic3.items() if t in times])
        if len(active_devices) != 0:
            data[t] = active_devices
        else:
            data[t] = []

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

def clean_repeats_activity0(df):

    """
    Cleans the DataFrame by removing repeated following rows.
    Only removes when Activity == 0.
    Arguments:
        df -- A DataFrame with sensor states.
    Returns:
        df_cleaned -- A cleaned DataFrame with no repeated following rows (for Activity==0).
    """
    df_cleaned = df.copy()
    remove_indices = []
    for i in range(len(df_cleaned) - 1):
        # Check if the current row is equal to the next row
        if df_cleaned.iloc[i].equals(df_cleaned.iloc[i + 1]):
            act_val = df_cleaned.iloc[i + 1]["Activity"]
            if act_val == 0 or str(act_val).strip() == "0":
                remove_indices.append(i + 1)

    df_cleaned.drop(index=remove_indices, inplace=True)
    return df_cleaned.reset_index(drop=True)
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


def all_objects_prox_df():
    """
    Returns a set of all activities used in the dataset, Training and test.
    Returns:
        activities -- A set of all activities.
    """
    objects_prox = [
        "TV CONTROLLER",
        "BOOK",
        "ENTRANCE DOOR",
        "MEDICINE BOX",
        "FOOD CUPBOARD",
        "FRIDGE",
        "POT DRAWER",
        "WATER BOTTLE",
        "GARBAGE CAN",
        "WARDROBE DOOR",
        "PYJAMA DRAWER",
        "BED",
        "BATHROOM TAP",
        "TOOTHBRUSH",
        "LAUNDRY BASKET"
    ]
    return objects_prox  

def clean_repeats(df):

    """
    Cleans the DataFrame by removing repeated following rows.
    Arguments:
        df -- A DataFrame with sensor states.
    Returns:
        df_cleaned -- A cleaned DataFrame with no repeated following rows.
    """
    df_cleaned = df.copy()
    # Iterate through the DataFrame and remove repeated rows
    remove_indices = []
    for i in range(len(df_cleaned) - 1):
        # Check if the current row is equal to the next row
        if df_cleaned.iloc[i].equals(df_cleaned.iloc[i + 1]):
            remove_indices.append(i + 1)
    df_cleaned.drop(index=remove_indices, inplace=True)

    return df_cleaned.reset_index(drop=True)