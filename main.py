import sys
import pandas as pd
import numpy as np
from math import floor
from pprint import pprint
from time import time, ctime, strftime, localtime
from datetime import datetime


def XX_YY(seconds):
    '''
    Converts seconds to XX:YY time 

    '''
    seconds = int(seconds)
    string_seconds = str(seconds % 60) 
    if len(string_seconds) == 1: 
        string_seconds = '0' + string_seconds

    return str(seconds//60) + ':' + string_seconds


def pace_XX_YY(seconds):
    '''
    Converts seconds to XX'YY" time 

    '''
    seconds = int(seconds)
    string_seconds = str(seconds % 60) 

    return str(seconds//60) + "'" +  string_seconds + '"'


def dur_to_sec(xx_yy):
    '''
    Converts XX:YY to seconds 

    '''
    [minutes, seconds]  = xx_yy.split(':')
    return (60*int(minutes)) + int(seconds)


def decimal_minutes(xx_yy):
    '''
    Converts XX:YY to XX,ZZ 

    '''
    [minutes, seconds]  = str(xx_yy).split(':')
    return int(minutes) + (int(seconds)/60)

    
def excel_duration(dur):
    '''
        Converts XX:YY:ZZ to XX::YY
    '''
    if len(str(dur)) == 8:
        return dur[:5]
    return dur

date_convert = lambda epoch_seconds: strftime('%d/%m/%Y', localtime(int(epoch_seconds))) # Converts epoch seconds to date
current_seconds = lambda date: (datetime.strptime(date, "%d/%m/%Y") - datetime(1970, 1, 1)).total_seconds() # Converts date to epoch seconds

def number_input(data_name):
    '''
        Input function in a predefined interval
    '''
    data_dict = {
        'steps': ['Steps', [10, 50000]],
        'avg_hr': ['Average heart rate', [40, 220]],
        'max_hr': ['Max heart rate', [40, 220]],
    }

    a, b = data_dict[data_name][1]
    interval = pd.Interval(left=a, right=b, closed='both')

    while True:
        message = data_dict[data_name][0]
        data_input = int(input(message + ' = '))
        if int(data_input) in interval:
            break
        print('Input value in the interval: [' + str(a) + ', ' + str(b) + ']')

    return data_input


def concat_new(df, odf):
    '''
        Concatenates two dataframes in relation to dates(current and imported ones)
    '''
    current_dates = set(df.index)    
    import_dates = set(odf.index)
    
    new_dates = list(import_dates - import_dates.intersection(current_dates))
    new_dates.sort()
    new_df = odf.loc[list(new_dates)]
    df = pd.concat([df, new_df])
  
    return df


def csv_import():
    '''
        Imports workout_export.csv
    '''
    try:
        df = pd.read_csv('workout_export.csv', sep = ';')
    except FileNotFoundError:
        column_names = ['Date', 'Duration', 'Distance', 'Calories']
        df = pd.DataFrame(columns=column_names) # Creates empty dataframe
    
    df.set_index('Date', inplace=True)

    return df


def original_import(path):
    '''
        Imports original csv
    '''
    column_names = ['Type', 'Date', 'Duration', 'MinPace', 'MaxPace', 'Distance', 'AvgPace', 'Calories']
    df = pd.read_csv(path, names = column_names, sep = ';')[1:]

    df = df[df['Type'] == '8'] # Filter running only
    df = df.drop(['Type', 'MinPace','MaxPace', 'AvgPace'], axis=1)


    df['Date'] = df['Date'].apply(date_convert)
    df['Duration'] = df['Duration'].apply(XX_YY)
    df['Distance'] = df['Distance'].apply(float)
    df['Calories'] = df['Calories'].apply(float, int)

    new_column_names = ['Steps', 'Avg HR', 'Max HR']
    df[new_column_names] = 0 # NEW

    df.set_index('Date', inplace=True)

    return df


def date_manual_input(path, date):
    '''
        Inputs manually steps, average and max heart rate of a specific date.
    '''
    df = csv_import()             # Existing df(new format)
    odf = original_import(path)   # Imported df(xiaomi format)

    df = concat_new(df, odf)

    data_names = ['steps', 'avg_hr', 'max_hr']
    data_list = [number_input(name) for name in data_names]
    
    df.loc[date, ['Steps', 'Avg HR', 'Max HR']] = data_list
    df_dates = set(df.index)        
    sorted_dates = sorted(df_dates, key=lambda x: datetime.strptime(x, "%d/%m/%Y").strftime("%Y-%m-%d"))
    df = df.loc[sorted_dates]

    return df


def calculate(df): 
    '''
        Calculates cadence, stride and pace.
    '''

    # Duration
    df['Duration'] = list(map(excel_duration, df['Duration'])) 

    # Adds three new columns
    calc_columns = ['Cadence', 'Stride', 'Pace']
    df[calc_columns] = 0

    # Cadence
    decimal_minutes_series = df['Duration'].apply(decimal_minutes)
    df['Cadence'] = (df['Steps'] / decimal_minutes_series).apply(round)
    
    # Stride
    red = lambda x: format(x, '.4f')
    df['Stride'] = list(map(red, df['Distance'] / df['Steps']))

    # Pace
    num = (df['Duration']).apply(dur_to_sec)
    denom = df['Distance'] / 1000
    df['Pace'] = num / denom
    df['Pace'] = df['Pace'].apply(pace_XX_YY)

    return df


# Main program
if __name__ == '__main__':

    arguments = sys.argv 
    path = arguments[1] # Path of workout_data.csv
 
    print('------------------------')
    print('------Running data------')
    print('------------------------')
    print('')
    print('------------------------------------------------')
    print('Input manually steps, average and max heart rate')
    print('------------------------------------------------')
    print('')
    
    df = csv_import()             # Existing df(new format)
    odf = original_import(path)   # Imported df(xiaomi format)

    df = concat_new(df, odf)

    new_dates = list(df[df['Steps'] == 0].index) # These will be the new entry dates
    new_sorted_dates = sorted(new_dates, key=lambda x: datetime.strptime(x, "%d/%m/%Y").strftime("%Y-%m-%d")) # Sorts dates

    for date in new_sorted_dates: 
        date_message = 'Date = ' 
        print((len(date)+len(date_message)+1) * '-') # Divider
        print(date_message, date)
        
        df = date_manual_input(path, date)
        df = calculate(df)

        df_dates = df.index
        sorted_dates = sorted(df_dates, key=lambda x: datetime.strptime(x, "%d/%m/%Y").strftime("%Y-%m-%d"))
        df = df.loc[sorted_dates]

        df.to_csv('workout_export.csv', sep=';') # Save current df in every iteration

