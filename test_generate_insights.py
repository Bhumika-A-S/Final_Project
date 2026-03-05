import json
from datetime import datetime, timedelta
import pandas as pd

from legacy_streamlit.sentiment import generate_insights

now = datetime.now()

def make_rows(waiter_id, ratings):
    rows = []
    for i, r in enumerate(ratings):
        ts = (now - timedelta(days=len(ratings) - i)).isoformat()
        rows.append({
            "timestamp": ts,
            "waiter_id": waiter_id,
            "amount": 10 + i,
            "rating": r,
            "feedback": "Great service" if r >= 4 else ("Okay" if r == 3 else "Slow service"),
            "sentiment": ""
        })
    return rows

# Scenario A: improving ratings for W001
rows_a = make_rows("W001", [2, 2, 3, 4, 5])
# Scenario B: declining ratings for W002
rows_b = make_rows("W002", [5, 5, 4, 3, 2])
# Scenario C: stable middling ratings for W003
rows_c = make_rows("W003", [3, 3, 3, 3, 3])
# Scenario D: few noisy ratings for W004
rows_d = make_rows("W004", [4, 2, 5, 3])
# Combine into one DataFrame
all_rows = rows_a + rows_b + rows_c + rows_d

df = pd.DataFrame(all_rows)

print("DataFrame sample:\n", df.head().to_string(index=False))

for waiter in ["W001", "W002", "W003", "W004", "W999"]:
    print('\n=== Insights for', waiter, '===')
    out = generate_insights(df, waiter)
    print(json.dumps(out, indent=2))

# Also show team insights
print('\n=== Team insights ===')
print(json.dumps(generate_insights.__module__ and __import__('app.sentiment').sentiment.generate_team_insights(df), indent=2))
