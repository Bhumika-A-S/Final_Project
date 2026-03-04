import requests

# Test login
r1 = requests.post('http://127.0.0.1:8000/auth/login', json={'username':'owner','password':'ownerpass'})
if r1.status_code == 200:
    token = r1.json()['access_token']
    print('✓ Login successful')
    
    # Test list all transactions (simpler endpoint)
    r2 = requests.get('http://127.0.0.1:8000/transactions', headers={'Authorization': f'Bearer {token}'})
    print(f'\n1. GET /transactions: {r2.status_code}')
    if r2.status_code == 200:
        txs = r2.json()
        print(f'   ✓ Found {len(txs)} transactions')
    else:
        print(f'   ✗ Error: {r2.text[:300]}')
    
    # Test team insights with more details
    r3 = requests.get('http://127.0.0.1:8000/insights/team', headers={'Authorization': f'Bearer {token}'})
    print(f'\n2. GET /insights/team: {r3.status_code}')
    if r3.status_code == 200:
        data = r3.json()
        print(f'   ✓ Total Orders: {data.get("total_orders", 0)}')
    else:
        print(f'   ✗ Error response:')
        print(f'   {r3.text[:500]}')
else:
    print(f'✗ Login failed: {r1.status_code}')

