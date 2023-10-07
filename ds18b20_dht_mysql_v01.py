#!/usr/bin/python3

import os
import glob
import time
import Adafruit_DHT
import urllib.request
from urllib.request import urlopen
from datetime import datetime
import socket
import re

# DECLARATIONS
now = datetime.now()                            # Get time right now
timestamp = now.strftime("%Y-%m-%d-%H:%M:%S")   # Format the timestamp
os.system('modprobe w1-gpio')                   # Adding 1-wire module to the kernel 
os.system('modprobe w1-therm')                  # Adding 1-wire therm module
base_dir = '/sys/bus/w1/devices/'               # Setting the base_dir
device_folder = glob.glob(base_dir + '28*')[0]  # Check if a Dallas DS18B20 is connected
device_file = device_folder + '/w1_slave'       # This file holds the temperature
sensor_type = 11
sensor_pin = 17


# Function to read raw temperature from the DS18b20
# It opens the device_file (/w1_slave), and reads the content, then close the file
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

# Function to read the temperature and format it to Celsius and Fahrenheit
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':	
        time.sleep(0.2)
        lines = read_temp_raw()
    equal_pos = lines[1].find('t=')
    if equal_pos != -1:
        temp_string = lines[1][equal_pos+2:]
        temp_c = float(temp_string) / 1000.0
        global celsius
        celsius = temp_c
        temp_f = temp_c *9.0 / 5.0 + 32.0
        return temp_c, temp_f

# Function that reads the humidity and temperature from the DHT11
# It only saves and use the humidity
def read_humidity():
    global humidity
    humidity, temperature = Adafruit_DHT.read_retry(sensor_type, sensor_pin)
    time.sleep(2)
    while True:
        if humidity is not None and temperature is not None:
            print ('Data from sensor is OK. Humidity= {0:0.1f} %'.format(humidity))
            if humidity > 100:
                read_humidity()
            else:
                break
        else:
            print ('Error getting data from DHT.')

# Function to get the local hostname
# It is used for identify the "senor" in the mySQL database
def get_host_name():
    global local_hostname
    local_hostname = socket.gethostname()

# Function that get the external IP-adress
def get_external_ip_address():
    global external_ip
    url = "http://checkip.dyndns.org"           # This site return one line of text.
    my_request = urlopen(url).read()            # Read the URL
    res = re.findall(b'\d{1,3}', my_request)    # Search and findall integers in my_request
    my_ip_list = list(map(int, res))            # Clean up the list
    my_ip = str(my_ip_list)[1:-1]               # Remove the square brackets
    temp_ip = my_ip.replace(",", ".")           # Replace comma with periods
    external_ip = temp_ip.replace(" ", "")      # Replace <space> with none-space
    print ("External IP: " +external_ip)        # Print the External IP address as xxx.xxx.xxx.xxx

def send_data():
    print (timestamp)                           # For debug purpose
    print (celsius)                             # For debug purpose
    print (humidity)                            # For debug purpose
    print (local_hostname)                      # For debug purpose
    output = "http://svkajsa.no/temperature/add_temp.php?temp="+str(celsius) \
    +"&humi="+str(humidity)+"&time="+str(timestamp)+"&sensor="+str(local_hostname)+"&ip=" \
    +str(external_ip)                           # This is the string that is called by the urlopen
    print (output)                              # For debug purpose
    html = urlopen(output).read()               # Actually performing the call
    print (html)                                # For debug purpose

def main():
    read_temp()
    read_humidity()
    get_host_name()
    get_external_ip_address()
    send_data()
    
if __name__ == "__main__":
    main()