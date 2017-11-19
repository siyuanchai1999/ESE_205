from urllib.request import urlopen
import json
import requests
import csv

file = urlopen('https://www.wunderground.com/about/faq/US_cities.asp')

page = requests.get('https://www.wunderground.com/about/faq/US_cities.asp')
txt = page.text
first_point = txt.index('Central')
end_point = txt.index('Peipeinimaru')
new_txt = txt[first_point:end_point]

txt_list = list(new_txt)
txt_list.insert(0,'\n')
length = txt_list.count('\n')
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
        city = get_str(init_index+1,space_index)
        state = get_str(init_index+31,init_index+33)
        dict_city[i] =  state + '/' + city
        print(dict_city[i])
        txt_list.pop(0)
        txt_list = txt_list[txt_list.index('\n'):]
        
