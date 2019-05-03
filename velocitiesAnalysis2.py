#keeps track of script performance
import time
startTime = time.time()

def printRuntime(seconds,finished=False):
  seconds = int(seconds)
  status = 'has been running for' if not finished else 'finished in'

  minutes, seconds = divmod(seconds, 60)
  hours, minutes = divmod(minutes, 60)

  periods = [('hours', hours), ('minutes', minutes), ('seconds', seconds)]
  time_string = ', '.join('{} {}'.format(value, name)
                        for name, value in periods
                        if value)

  print('This script {} {}'.format(status, time_string))
  

# imports
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import geopy.distance
import scipy.integrate as it
import pandas as pd
import scipy.interpolate as pol
import os
import convertTime

  #GPS DATA EXTRACTION

#this counts the number of lines in a particular file in order to run though
#these lines later when reading each line.

filename = '2019-01-17T135058_gps.nmea' #gps file name
countGPS = 0
countMC=0
thefile = open(filename)
for line in thefile.readlines():
  countGPS += 1
  if line[0:6] == '$GPRMC':
    countMC+=1
thefile.close()

# open the file
fp = open(filename, 'r')
timeGPS = []
timeLineGPS=[0]
velLatLon = [0]
velLatLonTest = [0]
velGPS =[]
lat =[]
lon = []
j = 0
k =-1
DisAccum = [0]


"""
  GPS Data extraction is possibly taking up too much computational effort - consider using pandas package for reading CSV
  as used in IMU data pulling.
"""

#this for loop runs through the file for the number of lines in it
for i in range(countGPS):
  #arcs = [] #an empty list for a N number of arcs associated with a node
  ln = fp.readline() #reads and strips first/next line
  ln = ln.split(",") # divide the string using the split() method for strings
  
  if ln[00] == '$GPRMC':
    #converting values to something useful
    ln[7]=float(ln[7])
    ln[1]= convertTime.gps_time_to_utc(ln)
    ln[7]=ln[7] *0.51444444444
    latStr=str(ln[3])
    latVal = -1*(float(latStr[0:2]) + (float(latStr[2:9])/60))
    lonStr=str(ln[5])
    lonVal = (float(lonStr[0:3]) + (float(lonStr[3:10])/60))    
    #add to list
    velocity.append(ln[7])
    lat.append(latVal)
    lon.append(lonVal)
    timeGPS.append(ln[1])
    k+=1
    #number of $GPRMC lines
    if  k>=1 and k<=countMC:
      velLatLon.append(geopy.distance.vincenty((lat[j],lon[j]), (lat[k],lon[k])).m)
      velLatLonTest.append(geopy.distance.distance((lat[j],lon[j]), (lat[k],lon[k])).m)
      timeLineGPS.append (timeGPS[k]-timeGPS[j]+timeLineGPS[j]) 
      DisAccum.append(velLatLon[k] + DisAccum[j]) 
      j+=1

#IMU DATA EXTRACTION
#empty lists for imu data
timeIMU = []
pitch = []
roll = []
accX = []
accY = []
accZ = []
ind =[] #temp list
#reassign k and j for IMU data extraction
k=-1
j=0
timeLineIMU = [0] #WRITE CODE FOR THIS, time should already be converted to seconds. SOLVED
timeDiffIMU =[0]
#read in imu data
if os.path.isfile('firstTestFile'):
  df = pd.read_pickle('firstTestFile')
else:

  df= pd.read_csv('2019-01-31T150525_bug3piv0.4_imu device at stand still.csv', usecols=['Time', 'Pitch(deg)', 'Roll(deg)', 'medfACCx(MilliGs)','medfACCy(MilliGs)','medfACCz(MilliGs)']) ##change this
 
  df.to_pickle('firstTestFile')


#convert columns of df to lists
pitch = df['Pitch(deg)'].tolist()[5:]
roll = df['Roll(deg)'].tolist()[5:]
accX = df['medfACCx(MilliGs)'].tolist()[5:]
accY = df['medfACCy(MilliGs)'].tolist()[5:]
accZ = df['medfACCz(MilliGs)'].tolist()[5:]
countIMU = len(pitch)
#separate date and time
ind = df.Time.tolist()[5:]

for line in ind:
  timeIMU.append(convertTime.localtime_to_utc(line))
  k+=1
  #number of $GPRMC lines
  if  k>=1:
    timeLineIMU.append (timeIMU[k]-timeIMU[j]+timeLineIMU[j])
    timeDiffIMU.append (timeIMU[k]-timeIMU[j])
    j+=1

#IMU filtering attempt - pretty sure this doesnt work lol 
#average freq
freqIMU = countIMU/timeLineIMU[-1]
freqGPS = countMC/timeLineGPS[-1]
intervalIMU= round(1/freqIMU,2)
intervalGPS= round(1/freqGPS,2)
#check
print(freqIMU) #should be about 25
print(freqGPS) #should be about 1
newTimeIMU= np.linspace(0,intervalIMU*countIMU, num =countIMU)
newTimeGPS= np.linspace(0, intervalGPS*countMC, num =countMC)
fPitch=pol.interp1d(timeLineIMU, pitch, fill_value = 0)
fRoll = pol.interp1d(timeLineIMU, roll, fill_value = 0)
fAccX = pol.interp1d(timeLineIMU, accX, fill_value = 0)
fAccY = pol.interp1d(timeLineIMU, accY, fill_value = 0)
fAccZ = pol.interp1d(timeLineIMU, accZ, fill_value = 0)
#GPS stuff
fVelGPS= pol.interp1d(timeLineGPS, velGPS, fill_value = 0)
fVelLatLon= pol.interp1d(timeLineGPS, velLatLon, fill_value = 0)
fVelLatLonTest= pol.interp1d(timeLineGPS, velLatLonTest, fill_value = 0)

#interpolated values.
polPitch= fPitch(newTimeIMU)
polRoll= fRoll(newTimeIMU)
polAccX= fAccX(newTimeIMU)
polAccY= fAccY(newTimeIMU)
polAccZ= fAccZ(newTimeIMU)
#GPS back at it again boiii
polVelGPS= fVelGPS(newTimeGPS)
polVelLatLon= fVelLatLon(newTimeGPS)
polVelLatLoTestn= fVelLatLonTest(newTimeGPS)


accHor =[]
accZImp=[]
i=0
#convert acc from mg to m/s**2 and calculate horizontal acceleration
while i <len(PolAccX):
  accHor.append(float(np.sqrt(((polAccX[i]*0.00980665)**2)+((polAccY[i]*0.00980665)**2))))
  accZTemp = (float(polAccZ[i]*0.00980665)-9.80665)*np.cos((np.pi/4)-polPitch[i]) #removed effect of gravity and pitch
  accZImp.append(accZTemp*np.cos((np.pi/4)-polRoll[i])) #removed effect of roll to get true vertical acceleration

velAcc = it.cumtrapz(accHor, x=timeDiffIMU) 


fig = plt.figure()
ax1 = fig.add_subplot(111)
textsize = 12.
ax1.plot(newTimeGPS, polVelLatLon, c='b', label='Velocity from LatLon')
ax1.plot(newTimeGPS, polVelGPS, c='r', label='Velocity from Knots')
ax1.plot(newTimeGPS, polVelLatLonTest, c='p', label='Velocity from latlon but different')
ax1.plot(newTimeIMU[1:], velAcc, c='g', label='Velocity from Acceleration')
ax1.set_ylabel('Velocity [m/s]', size = textsize)
ax1.set_xlabel('time [s]', size = textsize)
plt.legend(loc='upper left')
plt.show()






