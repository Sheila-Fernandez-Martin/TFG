from datetime import datetime, timedelta
import pandas as pd
import os


## First, some methods that I will need
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

def create_act_number(act):
    r"""    Converts an activity string to a numerical representation.
    Arguments:
        act -- Activity string, e.g., 'Act24', 'Idle'.
    Returns:
        act -- Numerical representation of the activity, where 'Idle' is 0 and 'ActX' is X.
    """
    if act=="Idle":
        return 0
    else:
        return int(act.replace("Act",""))
    
def getActivity(dic,time):
    r"""
    Given a dictionary of activities with their time intervals and a specific time returns the activity at that time.
    Arguments:
        dic -- Dictionary with activities as keys and lists of one tuple (start_time, end_time) as value.
                {'Act24': [(start_time1, end_time1), (start_time2, end_time2)], ...}
        time -- Time in the format 'HH:MM:SS' to check the activity at that moment.
    Returns:
        act -- The activity at the specified time, or 'Idle' if no activity is found.
    """
    act = "Idle"
    for a in dic:
        for elem in dic[a]:
            if elem[0]<=time and time<=elem[1]:
                act = a
    return act     

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

def dicts_s_a(sensors, activities, floor):
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

    # Crea una lista con todas las horas de inicio (t1) y de fin (t2) del df activities 
    t1 = [x.split(" ")[1] for x in activities["DATE BEGIN"].to_list()]
    t2 = [x.split(" ")[1] for x in activities["DATE END"].to_list()]

    t1 = [x.split(".")[0] for x in t1]
    t2 = [x.split(".")[0] for x in t2]

    # Crea una lista con SOLO las actividades
    acts = activities["ACTIVITY"].to_list()
    
    # Crea dic1 para los sensores y dic2 para actividades 
    dic1,dic2,dic3 = {},{},{}

    for s in set(objects):
        dic1[s] = []
    for a in set(acts):
        dic2[a] = []
    for d in set(devices):
        dic3[d] = []
    # A dic1 le asocia como claves los sensores y como valores una lista de tuplas (estado, hora)
    for i in range(len(timestamps)):
        dic1[objects[i]].append((states[i],timestamps[i]))
    # A dic2 le asocia como claves las actividades y como valores una lista de tuplas (inicio, fin)
    for i in range(len(t1)):
        dic2[acts[i]].append((t1[i],t2[i]))
    # A dic3 le asocia como claves los dispositivos y como valores una lista de tuplas (hora)
    for i in range(len(timestamps_floor)):
        dic3[suelos[i]].append((timestamps_floor[i]))

    return dic1, dic2, dic3, timestamps, timestamps_floor, t1, t2, objects

def sensor_activity(dic1, dic2, dic3, timestamps, timestamps_floor, t1, t2, objects, global_sensors):
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

    tbegin,tend = min(timestamps[0],t1[0],timestamps_floor[0]),max(timestamps[-1],t2[-1],timestamps_floor[-1])
    # Convertimos 
    data = {}

    for t in enumerate_seconds(tbegin,tend):
        activity = getActivity(dic2, t)
        active_devices = [device for device, times in dic3.items() if t in times]
        if len(active_devices) != 0:
            data[t] = [activity] + active_devices
        else:
            data[t] = [activity]
        

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
    sorted_list_of_sensors = sorted(list(global_sensors))
    devices = [f"{i+1:02d},{j+1:02d}" for i in range(5) for j in range(10)]  # Asumiendo 5 filas y 9 columnas

    for t in enumerate_seconds(tbegin,tend):
        # Crea una lista binaria + número de actividad
        data_pd.append(create_bit_vector(sorted_list_of_sensors+devices,data[t][1:])+[create_act_number(data[t][0])])
    df = pd.DataFrame(data_pd, columns=sorted_list_of_sensors+devices+["Activity"])
    return df

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
        if df_cleaned.iloc[i].equals(df_cleaned.iloc[i + 1]):
            remove_indices.append(i + 1)
    df_cleaned.drop(index=remove_indices, inplace=True)

    return df_cleaned.reset_index(drop=True)