import requests
from pprint import pprint
import json


main_link = 'https://api.github.com/'

user = 'likelios'
link_tail = 'users/' + user + '/repos'

header = {'User-agent': 'Chrome/77.0.3865.7'}

req = requests.get(main_link + link_tail, headers=header)
if req.ok:
    data = json.loads(req.text)
    pprint(data)

with open(user + '_reps.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=2, ensure_ascii=False)
