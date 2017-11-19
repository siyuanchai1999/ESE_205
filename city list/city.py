from urllib.request import urlopen
import json
import csv

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

city = ' '
state = ' ' 
space_index = 0
init_index = 0
entries = txt_list.count('\n')
for i in range(entries-1):
        space_index = txt_list.index(' ')
        while txt_list[space_index+1] !=  ' ':
            #print(space_index)
            temp = txt_list[space_index + 1:]
            space_index = temp.index(' ')+space_index+1
        city = get_str(init_index+1,space_index)
        state = get_str(init_index+31,init_index+33)
        dict_city[i] =  state + '/' + city
        print(dict_city[i])
        txt_list.pop(0)
        txt_list = txt_list[txt_list.index('\n'):]
        
