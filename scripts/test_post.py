import requests

url = 'http://localhost:8000/transactions'
payload = {'waiter_id':'W001','amount':5.5,'rating':4,'feedback':'Nice service'}
resp = requests.post(url, json=payload)
print('status:', resp.status_code)
try:
    print('json:', resp.json())
except Exception:
    print('text:', resp.text)
