import serial
import time
from urllib.request import urlopen
import json
import RPi.GPIO as GPIO
import time
import csv

ser = serial.Serial('/dev/ttyUSB0',9600,timeout =0.3)
reboot_count = 0
nextTime = time.time()
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
hot_pin = 14 
warm_pin = 15
cold_pin = 18
on_pin = 23
blink_status = False
GPIO.setup(on_pin,GPIO.OUT)
GPIO.setup(hot_pin,GPIO.OUT)
GPIO.setup(warm_pin,GPIO.OUT)
GPIO.setup(cold_pin,GPIO.OUT)

GPIO.output(hot_pin,GPIO.HIGH)
GPIO.output(warm_pin,GPIO.HIGH)
GPIO.output(cold_pin,GPIO.HIGH)
time.sleep(2)

GPIO.output(hot_pin,GPIO.LOW)
GPIO.output(warm_pin,GPIO.LOW)
GPIO.output(cold_pin,GPIO.LOW)


def LED(temp):
    if(temp>80):
        GPIO.output(hot_pin,GPIO.HIGH)
        GPIO.output(warm_pin,GPIO.LOW)
        GPIO.output(cold_pin,GPIO.LOW)
    elif(temp>60):
        GPIO.output(hot_pin,GPIO.LOW)
        GPIO.output(warm_pin,GPIO.HIGH)
        GPIO.output(cold_pin,GPIO.LOW)
    else:
        GPIO.output(hot_pin,GPIO.LOW)
        GPIO.output(warm_pin,GPIO.LOW)
        GPIO.output(cold_pin,GPIO.HIGH)

city_file = urlopen('https://www.wunderground.com/about/faq/US_cities.asp')

with open('/home/pi/Desktop/commni/valid_city_entries.json', 'r') as fp:
    valid_city_entries = json.load(fp)

dict_city = {}

for i in valid_city_entries:
        dict_city[int(i)] = valid_city_entries[i]

print("done loading city entries")

def get_json(city_num):
    url_str = dict_city[city_num]
    file = urlopen('http://api.wunderground.com/api/c72540fc54d39cb9/geolookup/conditions/q/'+url_str+'.json')
    json_string = file.read().decode("utf-8") #decode the bytes to string
    parsed_json = json.loads(json_string)
    return parsed_json

def get_min(string):
    colon_digit = string.index(':')
    return string[colon_digit+1:colon_digit+3]

def get_hour(string):
    colon_digit = string.index(':')
    return string[colon_digit-2:colon_digit]

def write_city_name(line):  #working whenn user selects cities
    str_line = line.decode()
    if(str_line[0] == "#"):
        c_num = int(str_line[1:str_line.index('\r')])
        c_str_1 = dict_city[c_num][3:18]
        c_str_2 = dict_city[c_num+1][3:18]
        c_str_1_head = dict_city[c_num][:3]
        c_str_2_head = dict_city[c_num+1][:3]
        print(c_str_1)
        ser.write("(".encode())
        ser.write(c_str_1.encode())
        ser.write("!".encode())
        if(c_str_1_head == c_str_2_head):
            print(c_str_2)
            ser.write(")".encode())
            ser.write(c_str_2.encode())
            ser.write("!".encode())

def get_city_num(line,c_num):  #when user confirm his choice
    str_line = line.decode()
    if(str_line[0] == "@"):
        c_num = int(str_line[1:str_line.index('\r')])
        return c_num
    return c_num

def write_time(h, m):
    print_time(h,m)
    ser.write("/".encode())
    if h<10:
        ser.write(b'0')
    ser.write(b'%d' %h)
    if m<10:
        ser.write(b'0')
    ser.write(b'%d'%m)
    ser.write("!".encode())
            

def write_weather(parsed_json):
    location = parsed_json['location']['city']
    temp_f = parsed_json['current_observation']['temp_f']
    weather = parsed_json['current_observation']['weather']
    precip_today = parsed_json['current_observation']['precip_today_in']
    
    LED(temp_f)
    #if(weather == "Clear"):  weather = "Sunny"
    print ("Current weather in %s: %s" % (location, weather))
    print ("Current temperature in %s: %s" % (location, temp_f))
    print ("Precipitation today in %s will be: ~%s inches" % (location, precip_today))
    m = "Precipitation today in %s will be: ~%s inches" % (location, precip_today)
    
    locationE = location.encode()
    temp_E = str(temp_f).encode()
    weatherE = weather.encode()
    precip_todayE = precip_today.encode()

    ser.write("$".encode())
    ser.write(locationE)
    ser.write("!".encode())

    ser.write("%".encode())
    ser.write(weatherE)
    ser.write("!".encode())

    ser.write("&".encode())
    ser.write(precip_todayE)
    ser.write("!".encode())

    ser.write("+".encode())
    ser.write(temp_E)
    ser.write("!".encode())
 
def print_time(h,m):
    print("Current Time is %d : %d" %(h,m))

def when_reboot(line,h,m,num,reboot_c):
    str_line = line.decode()
    if(str_line[0] == "r" and str_line[1] == "e" and str_line[2] == "a"):
        reboot_c = reboot_c +1;
        if(reboot_c >1):
            write_weather(get_json(num))
            write_time(h,m)
    return reboot_c

            
        
ex_hour =0
ex_min = 0
stop_check = 1
city_num = 734
last_city_num = -1
hour = 0
min = 0
while(city_num != -1):
    if(time.time()- nextTime>0):  #blinking to indicate RPI working
        #print(blink_status)
        blink_status = not blink_status
        if(blink_status):
            GPIO.output(on_pin,GPIO.HIGH)
        else:
            GPIO.output(on_pin,GPIO.LOW)
        nextTime = time.time() + 1.0
    
    if(ser.isOpen()==False):
        ser.open()
    if(ser.in_waiting>0):
        line = ser.readline()
        if(line!= b''):
            print(line)
            write_city_name(line)
            city_num = get_city_num(line,city_num)
            reboot_count = when_reboot(line, hour, min,city_num,reboot_count)
            
    if(last_city_num != city_num):    #update weather even without changing time zone
        write_weather(get_json(city_num))
        last_city_num = city_num
        offset_str = get_json(city_num)['current_observation']['local_tz_offset']
        offset = int(offset_str[:3]) +6
     
    hour = time.localtime().tm_hour + offset
    min = time.localtime().tm_min
    
    if ex_hour != hour:
        if(ser.isOpen):
            write_weather(get_json(city_num))
            ex_hour = hour
            write_time(hour,min)
            ser.close()
    if ex_min != min:
        if(ser.isOpen()):
            ex_min = min
            write_time(hour,min)
            ser.close()

                                                                                                                     