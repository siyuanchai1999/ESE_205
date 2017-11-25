import serial
import time
from urllib.request import urlopen
import json
import RPi.GPIO as GPIO
import time
import csv
ser = serial.Serial('/dev/ttyACM1',9600,timeout =0.3)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
hot_pin = 14
warm_pin = 15
cold_pin = 18
GPIO.setup(hot_pin,GPIO.OUT)
GPIO.setup(warm_pin,GPIO.OUT)
GPIO.setup(cold_pin,GPIO.OUT)
    
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

txt = city_file.read().decode()
first_point = txt.index('Central')
end_point = txt.index('Peipeinimaru')
new_txt = txt[first_point:end_point]  #eliminate other data from website
txt_list = list(new_txt)
txt_list.insert(0,'\n')
dict_city = {}

city = ' '
state = ' ' 
space_index = 0
init_index = 0
entries = txt_list.count('\n')

def get_str(start, end):
    result  = str('')
    for i in range(start, end):
        result = result + str(txt_list[i])
    return result

for i in range(entries-1):
        space_index = txt_list.index(' ')
        while txt_list[space_index+1] !=  ' ':
            #print(space_index)
            temp = txt_list[space_index + 1:]
            space_index = temp.index(' ')+space_index+1
        city = get_str(init_index+1,space_index)
        city = city.replace(' ', '_')
        state = get_str(init_index+31,init_index+33)
        dict_city[i] =  state + '/' + city
        #print(dict_city[i])
        txt_list.pop(0)
        txt_list = txt_list[txt_list.index('\n'):]

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
  
def write_city_name(line):
    str_line = line.decode()
    if(str_line[0] == "#"):
        c_num = int(str_line[1:str_line.index('\r')])
        c_str_1 = dict_city[c_num][3:]
        c_str_2 = dict_city[c_num+1][3:]
        print(c_str_1)
        print(c_str_2)
        ser.write("(".encode())
        ser.write(c_str_1.encode())
        ser.write("!".encode())
        ser.write(")".encode())
        ser.write(c_str_2.encode())
        ser.write("!".encode())
                         
        
def weather(parsed_json):
    location = parsed_json['location']['city']
    temp_f = parsed_json['current_observation']['temp_f']
    weather = parsed_json['current_observation']['weather']
    precip_today = parsed_json['current_observation']['precip_today_in']
    local_time_str= parsed_json['current_observation']['local_time_rfc822']
    
    LED(temp_f)
    print (local_time_str)
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
    
    

ex_hour =0
ex_min = 0
stop_check = 1
city_num = 850
last_city_num = -1
while(city_num != -1):
    
    
    if(ser.isOpen()==False):
        ser.open()
    if(ser.in_waiting>0):
        line = ser.readline()
        if(line!= b''):
            print(line)
            write_city_name(line)
    if(last_city_num != city_num):    #update weather even without changing time zone
        weather(get_json(city_num))
        last_city_num = city_num
        offset_str = get_json(city_num)['current_observation']['local_tz_offset']
        offset = int(offset_str[:3]) +6
        
    hour = time.localtime().tm_hour + offset
    min = time.localtime().tm_min
    
    if ex_hour != hour:
        if(ser.isOpen):
            weather(get_json(city_num))
            ex_hour = hour
            ser.write("/".encode())
            if hour<10:
                m = ser.write(b'0')
            m = ser.write(b'%d' %hour)
            if min<10:
                n = ser.write(b'0')
            n = ser.write(b'%d'%min)
            ser.write("!".encode())
            ser.close()
    if ex_min != min:
        if(ser.isOpen()):
            ex_min = min
            ser.write("/".encode())
            if hour<10:
                m = ser.write(b'0')
            m = ser.write(b'%d' %hour)
            if min<10:
                n = ser.write(b'0')
            n = ser.write(b'%d'%min)
            ser.write("!".encode())
            ser.close()
    #city_num = int(input("press  to stop, city num to continue"))

                                                                                                                     