from urllib.request import urlopen
import json
import csv
import time
t = time.time()

file = urlopen('https://www.wunderground.com/about/faq/US_cities.asp')

txt = file.read().decode()
first_point = txt.index('Central')
end_point = txt.index('Peipeinimaru')
new_txt = txt[first_point:end_point]

txt_list = list(new_txt)
txt_list.insert(0,'\n')
dict_city = {}

def get_str(start, end):
    result  = str('')
    for i in range(start, end):
        result = result + str(txt_list[i])
    return result

city_in_state = 'String AK[]={'
city = ' '
state = ' '
last_state = 'AK'
space_index = 0
init_index = 0
state_arr = 'String*states[] = {AK, '
state_str = 'String state_str[] = {"AK", '
city_num = 0
state_city_num = 'int state_city_num[] ={'
entries = txt_list.count('\n')
for i in range(entries-1):
        space_index = txt_list.index(' ')
        while txt_list[space_index+1] !=  ' ':
            #print(space_index)
            temp = txt_list[space_index + 1:]
            space_index = temp.index(' ')+space_index+1
        city = get_str(init_index+1,space_index)
        city_num = city_num + 1;
        city = '"' + city + '"'
        state = get_str(init_index+31,init_index+33)
        if state != last_state:
            state_city_num = state_city_num + str(city_num) + ', '
            city_num = 0
            city_in_state = city_in_state[:-2]
            city_in_state = city_in_state + '}'+ ';'
            city_in_state = city_in_state + '//' + last_state
            print(city_in_state)
            last_state = state
            state_arr = state_arr + state + ', '
            state_str = state_str + '"' + state + '", '
            city_in_state = 'String ' + state + '[]={'
        city_in_state = city_in_state + city + ', '
        txt_list.pop(0)
        txt_list = txt_list[txt_list.index('\n'):]
        
city_in_state =city_in_state[:-2]+'};'
print(city_in_state)

state_arr = state_arr[:-2] + '};'
print(state_arr)

state_str = state_str[:-2] + '};'
print(state_str)

state_city_num = state_city_num[:-2] + '};'
print(state_city_num)
