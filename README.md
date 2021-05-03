# Running Workout Exporter
Exports your running workouts in workout_data.csv (from Mi Fit/Zepp) to a readable format. 

It uses pandas to handle the csv file as a dataframe and exports it again a csv file.

## Getting Started

### Install
Just download and unzip the file.

### Prerequisites
- pandas
- numpy
- workout_data.csv(from the Mi Fit website)

### Obtaining the csv

1. Download data from [Mi Fit](https://user.huami.com/privacy/index.html?v=4.0.3&platform_app=com.xiaomi.hm.health#/chooseDestory).
2. Unzip the file and locate the workout_data.csv in SPORT folder.
3. Copy the path.

## Usage
Run this script in the terminal and add the path of the workout_data.csv as an argument.

```
python3 main.py /Users/USERNAME/Downloads/FOLDER/SPORT/workout_data.csv
```
Then you input the steps, average and max heart rate for each date(manually from the app). 

You can press CTRL+C to stop the input as the csv file is saved at each iteration.
