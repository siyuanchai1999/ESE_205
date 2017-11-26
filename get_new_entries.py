import time
from urllib.request import urlopen
import json
import time
import csv

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
print("ready");
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

def get_city_num(line,c_num):
    str_line = line.decode()
    if(str_line[0] == "@"):
        c_num = int(str_line[1:str_line.index('\r')])
        return c_num
    return c_num
        
def weather(parsed_json):
    location = parsed_json['location']['city']
    temp_f = parsed_json['current_observation']['temp_f']
    weather = parsed_json['current_observation']['weather']
    precip_today = parsed_json['current_observation']['precip_today_in']
    '''
    print ("Current weather in %s: %s" % (location, weather))
    print ("Current temperature in %s: %s" % (location, temp_f))
    print ("Precipitation today in %s will be: ~%s inches" % (location, precip_today))
    m = "Precipitation today in %s will be: ~%s inches" % (location, precip_today)
    '''
    locationE = location.encode()
    temp_E = str(temp_f).encode()
    weatherE = weather.encode()
    precip_todayE = precip_today.encode()

def print_time(h,m):
    print("Current Time is %d : %d" %(h,m))
  
valid_city_dict = dict_city.copy()
for i in range(len(dict_city)):
    try:
        weather(get_json(i))
    except:
        #print(dict_city[i])
        valid_city_dict.pop(i)
print("done generating valid_city_dict")

valid_city_dict_order = {}
values = valid_city_dict.values()
for i in range(len(valid_city_dict)):
    valid_city_dict_order[i] = list(values)[i]
    
import json
with open('valid_city_entries.json', 'w') as fp:
    json.dump(valid_city_dict_order,fp)

                                                                                                                
