import json
with open('valid_city_entries.json', 'r') as fp:
    valid_city_entries = json.load(fp)

dict_city = valid_city_entries.copy()

for i in valid_city_entries:
        dict_city[int(i)] = valid_city_entries[i]

print("done")

    
