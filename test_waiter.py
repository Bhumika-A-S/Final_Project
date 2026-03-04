import requests

r1 = requests.post('http://127.0.0.1:8000/auth/login', json={'username':'owner','password':'ownerpass'})
if r1.status_code == 200:
    token = r1.json()['access_token']
    
    # Test waiter summary
    r2 = requests.get('http://127.0.0.1:8000/waiters/W001/summary', headers={'Authorization': f'Bearer {token}'})
    print(f'GET /waiters/W001/summary: {r2.status_code}')
    if r2.status_code == 200:
        data = r2.json()
        print(f'  ✓ Total Tips: {data.get("total_tips")}')
        print(f'  ✓ Avg Rating: {data.get("avg_rating")}')
        print(f'  ✓ Num Tips: {data.get("num_tips")}')
    else:
        print(f'  ✗ Error: {r2.text[:300]}')
    
    # Test waiter insights
    r3 = requests.get('http://127.0.0.1:8000/insights/waiter/W001', headers={'Authorization': f'Bearer {token}'})
    print(f'\nGET /insights/waiter/W001: {r3.status_code}')
    if r3.status_code == 200:
        data = r3.json()
        print(f'  ✓ Score: {data.get("score")}')
        print(f'  ✓ Trend: {data.get("trend")}')
    else:
        print(f'  ✗ Error: {r3.text[:300]}')
