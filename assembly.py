import serial
import time
from urllib.request import urlopen
import json
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def weather():
    hot_pin = 14
    warm_pin = 15
    cold_pin = 18
    GPIO.setup(hot_pin,GPIO.OUT)
    GPIO.setup(warm_pin,GPIO.OUT)
    GPIO.setup(cold_pin,GPIO.OUT)
    file = urlopen('http://api.wunderground.com/api/c72540fc54d39cb9/geolookup/conditions/q/MO/St_Louis.json')
    json_string = file.read().decode("utf-8") #decode the bytes to string
    parsed_json = json.loads(json_string)

    location = parsed_json['location']['city']
    temp_f = parsed_json['current_observation']['temp_f']
    weather = parsed_json['current_observation']['weather']
    precip_today = parsed_json['current_observation']['precip_today_in']

    print ("Current weather in %s: %s" % (location, weather))
    print ("Current temperature in %s: %s" % (location, temp_f))
    print ("Precipitation today in %s will be: ~%s inches" % (location, precip_today))
    m = "Precipitation today in %s will be: ~%s inches" % (location, precip_today)
    
    if(temp_f>80):
        GPIO.output(hot_pin,GPIO.HIGH)
        GPIO.output(warm_pin,GPIO.LOW)
        GPIO.output(cold_pin,GPIO.LOW)
    elif(temp_f>60):
        GPIO.output(hot_pin,GPIO.LOW)
        GPIO.outpuSt(warm_pin,GPIO.HIGH)
        GPIO.output(cold_pin,GPIO.LOW)
    else:
        GPIO.output(hot_pin,GPIO.LOW)
        GPIO.output(warm_pin,GPIO.LOW)
        GPIO.output(cold_pin,GPIO.HIGH)

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

    file.close()
    
    
ser = serial.Serial('/dev/ttyACM0',9600)
ex_hour =0
ex_min = 0
stop_check = 1

while(stop_check == 1):
    hour = time.localtime().tm_hour
    min = time.localtime().tm_min
    print(hour)
    print(min)
    if(ser.isOpen()==False):
        ser.open()
    if ex_hour != hour:
        if(ser.isOpen):
            weather()
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
    stop_check = int(input("press 0 to stop, 1 to continue"))

                                                                                                                     