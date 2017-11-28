import json

with open('valid_city_entries.json','r') as fp:
    valid_city_entries = json.load(fp)

dict_city = {}

for i in valid_city_entries:
        dict_city[int(i)] = valid_city_entries[i]

print(len(dict_city))
print(len(valid_city_entries))

print("done")

state_city_num_str = 'const int state_city_num[] = {'
state_str = 'char*state_str[] = {"AK",'
last_state = 'AK'
state = ''
city = ''
count = 0

length = len(dict_city)
for i in range(length):
    state = dict_city[i][:2]
    city = dict_city[i][3:]
    if(state != last_state):
        state_city_num_str = state_city_num_str + str(count) + ', '
        state_str = state_str + '"' + state + '"'+ ', '
        count = 0
        last_state = state
    count = count + 1
    
        
state_city_num_str = state_city_num_str +str(count)+'};'
print(state_city_num_str)

state_str = state_str[:-2]+'};'
print(state_str)
