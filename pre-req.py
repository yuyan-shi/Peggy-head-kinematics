import pandas as pd
import csv
import numpy as np
import matplotlib.pyplot as plt

#import csv file with recorded left, right servo angles and their corresponding roll and pitch values
df = pd.read_csv('C:/Users/yuyan.shi/Desktop/work/head-neck/kinematics/tabblepeggy reference tables/mid_servo_angle_2deg_3.csv') #change address to csv file address

#remove all the NaN rows
df = df.apply (pd.to_numeric, errors='coerce')
df = df.dropna()

#scatter plot of all avaiable left and right servo angles
plt.scatter(df['left_rel_angle'], df['right_rel_angle'])
plt.xlabel('Left servo angle(deg)')
plt.ylabel('Right servo angle(deg)')
plt.title('Plot of left and right servo values')
plt.show()

#scatter plot of all avaiable roll and pitch angles
plt.scatter(df['roll'], df['pitch'])
plt.xlabel('Roll(deg)')
plt.ylabel('Pitch(deg)')
plt.title('Plot of roll and pitch values')
plt.show()

#change to integer	
df['roll'] = df['roll'].astype('int8')
df['pitch'] = df['pitch'].astype('int8')

#sort df by roll(ascending) and then pitch(ascending) 
df_sorted = df.sort_values(by=['roll', 'pitch']).reset_index(drop=True)

#group dataframe by roll and pitch values (i.e. collect the data sets with the same roll and pitch outputs) and calculate the mean for left and right servo values
df_sorted = df.groupby(['pitch','roll']).mean().reset_index()

#change left and right servo values to integer
df_sorted['left_rel_angle'] = df_sorted['left_rel_angle'].astype('int8')
df_sorted['right_rel_angle'] = df_sorted['right_rel_angle'].astype('int8')

#group left and right servo value together into a tuple
df_sorted['servo_angles'] = df_sorted[['left_rel_angle', 'right_rel_angle']].apply(tuple, axis=1)

#change table format to row index:pitch, column index: roll, create two tables with left and right servo angles
df_sorted_left = df_sorted.pivot(index ='pitch', columns='roll', values='left_rel_angle')
df_sorted_right = df_sorted.pivot(index ='pitch', columns='roll', values='right_rel_angle')

#for every cell that is empty, write it a value of it's left or right most adjacent available cell
df_sorted_left.bfill(axis ='columns', inplace = True)
df_sorted_left.ffill(axis ='columns', inplace = True)
df_sorted_right.bfill(axis ='columns', inplace = True)
df_sorted_right.ffill(axis ='columns', inplace = True)

#change table type to integer
df_sorted_left = df_sorted_left.astype('int8')
df_sorted_right = df_sorted_right.astype('int8') 

#save the left and right servo table files locally (debugging step)
df_sorted_left.to_csv (r'C:/Users/yuyan.shi/Desktop/test files/left_test.csv')
df_sorted_right.to_csv (r'C:/Users/yuyan.shi/Desktop/test files/right_test.csv')

#create empty data table and row 
data = []
row = []

for i in range(-55,52): #for i in pitch range (rows); check the left_test.csv or right_test.csv file to find out the range of pitch values 
	row = []
	for j in range(-21, 23): #for j in roll range (column); check the left_test.csv or right_test.csv file to find out the range of pitch values
		tup = (df_sorted_left[j][i], df_sorted_right[j][i]) #create a tuple in the format of (left_serve_angle, right_servo_angle)
		# print(i,j)
		# print(tup)
		row.append(tup) #apend tuple to row
	data.append(row) #append row to data

df_concat = pd.DataFrame(data=data)
# df_concat = df_concat.applymap(str)
df_concat = df_concat.astype(str)
df_concat.to_csv (r'C:/Users/yuyan.shi/Desktop/test files/mid_servo_2.csv')

# df_concat = df_concat.str.replace('(','{')
# df_concat = df_concat.str.replace(')','},')
# df_concat.to_csv (r'C:/Users/yuyan.shi/Desktop/test files/tabblepeggy_2_angle_reference_TEST.csv')

'''
Run the next two lines after you open the csv file and edited the following:
1. change all "(" to "{"
2. change all ")" to "}"
3. delete the first column (index column) 
'''
# df_concat = pd.read_csv('C:/Users/yuyan.shi/Desktop/test files/mid_servo_2.csv')
# np.savetxt(r'C:/Users/yuyan.shi/Desktop/test files/mid_servo_2deg_1.h', df_concat, fmt='%s', newline="}, \n {", header="#ifndef NECK_H_\n#define NECK_H_")

