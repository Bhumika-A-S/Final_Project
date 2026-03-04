# Quick Verification - Flutter + Backend Integration ✅

## Status Check

**Backend API**: ✅ Running on `http://127.0.0.1:8000`
**Flutter App**: Ready to launch
**All Pages**: Fully integrated with backend APIs

---

## Quick Start (< 5 minutes)

### Terminal 1: Start Backend
```powershell
cd c:\Users\ADMIN\Desktop\TipTrack
.venv\Scripts\uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
Wait for: `INFO:     Uvicorn running on http://127.0.0.1:8000`

### Terminal 2: Run Flutter
```powershell
cd c:\Users\ADMIN\Desktop\TipTrack\flutter_app
flutter run -d chrome
```
Wait for app to open in Chrome

### Browser: Open DevTools
Press `F12` → Go to "Console" tab → Look for `[API]` logs

---

## Test Scenarios

### Test 1: Login (1 minute)
1. Username: `admin`
2. Password: `adminpass`
3. Click "Login"
4. **Expected**: 
   - Login succeeds
   - Redirects to appropriate dashboard
   - Console shows: `[API] Login successful for admin`

❌ **If it fails**:
- Check Console: Look for `[API] Backend responded XXX` or unreachable message
- Check backend is running (Terminal 1)
- Check Network tab in DevTools

---

### Test 2: Customer Submits Tip (2 minutes)
1. Login with `customer`/`customerpass`
2. Should be on Customer page
3. Select any waiter from dropdown
4. Enter amount: `5.50`
5. Rate: `4` stars
6. Feedback: "Amazing service!"  
7. Click "Submit Tip"
8. **Expected**:
   - Green success message appears
   - Form clears
   - Console shows: `[API] Tip submitted successfully`
   - Network tab shows `POST /transactions 200`

---

### Test 3: Waiter Views Dashboard (2 minutes)
1. Logout (drawer → Sign out)
2. Login with `waiter1`/`waiterpass`
3. Wait 1-2 seconds for data to load
4. **Expected**:
   - Dashboard auto-fills with "waiter1"
   - Shows cards with: Total Tips, Average Rating, # Tips
   - Shows Performance Score, Trend, Recommendations
   - Console shows `[API] Fetched waiter summary: {...}`

---

### Test 4: Owner Views Analytics (1 minute)
1. Logout
2. Login with `owner`/`ownerpass`
3. Should see Owner Dashboard
4. **Expected**:
   - Shows "Total Orders" count
   - Shows "Team Performance Score"
   - Shows "Low Ratings %"
   - Shows ranked leaderboard with waiter names
   - Can pull down to refresh (gray circular indicator)
   - Console shows: `[API] Fetched team insights: total_orders=...`

---

### Test 5: Admin Checks Backend Health (1 minute)
1. Logout
2. Login with `admin`/`adminpass`
3. Should see Admin page
4. Look for "Backend Status" card
5. Click refresh icon (circular arrow)
6. **Expected**:
   - Shows "Backend OK (200)"
   - Response appears almost instantly
   - No errors in console

---

## Console Log Examples

### Successful Login
```
[API] POST http://127.0.0.1:8000/auth/login with username=admin
[API] Response status: 200
[API] Login successful for admin
[API] Token set: eyJhbGc...
```

### Successful Tip Submission
```
[API] POST http://127.0.0.1:8000/transactions for waiter=waiter1, amount=5.5, rating=4
[API] Response status: 200
[API] Tip submitted successfully
```

### Successful Waiter Dashboard Load
```
[API] GET http://127.0.0.1:8000/waiters/waiter1/summary
[API] Response status: 200
[API] Fetched waiter summary: {total_tips: 10.50, avg_rating: 4.2, num_tips: 3}
```

---

## Backend Network Requests (F12 → Network Tab)

You should see these requests when testing:

| Request | Method | URL | Status | Expected Response |
|---------|--------|-----|--------|-------------------|
| Login | POST | `/auth/login` | 200 | `{access_token, role}` |
| List Waiters | GET | `/waiters` | 200 | `[{waiter_id, name, ...}]` |
| Submit Tip | POST | `/transactions` | 200 | `{id, amount, rating, ...}` |
| Summary | GET | `/waiters/{id}/summary` | 200 | `{total_tips, avg_rating, num_tips}` |
| Insights | GET | `/insights/waiter/{id}` | 200 | `{score, trend, recommendations}` |
| Team Data | GET | `/insights/team` | 200 | `{total_orders, leaderboard, ...}` |

---

## Troubleshooting

### Problem: "Unable to reach backend"
**Fix**: 
1. Check Terminal 1 - is backend running?
2. Ensure no firewall is blocking port 8000
3. Verify: `http://127.0.0.1:8000/` loads in browser

### Problem: "Invalid credentials"
**Fix**:
1. Check username/password spelling
2. Use demo creds from table above
3. Verify backend is responding (check Network tab)

### Problem: No data showing on pages
**Fix**:
1. Wait 2 seconds for API calls to complete
2. Check Console for `[API]` error messages
3. Check Network tab for failed requests
4. Verify you're logged in as correct role
5. Try pulling down to refresh (Owner Dashboard)

### Problem: "Signing failed (admin privileges required)"
**Fix**:
1. Logout and login as `admin`/`adminpass`
2. Check token in Network → auth/login response

### Problem: Waiter Dashboard shows empty
**Fix**:
1. Log in as `waiter1` exactly (case-sensitive)
2. First time accessing might have no tip data (it's OK, shows zeros)
3. Try submitting a tip first as customer, then view as waiter

---

## Files Modified for Integration

| File | Changes |
|------|---------|
| `lib/services/api.dart` | Added logging, error handling, timeouts |
| `lib/pages/login_page.dart` | Better error messages, backend health check |
| `lib/pages/customer_page.dart` | Better success/error feedback |
| `lib/pages/waiter_dashboard_page.dart` | Improved UI, better error handling |
| `lib/pages/owner_dashboard_page.dart` | Complete redesign with pull-refresh |
| `lib/pages/admin_page.dart` | Added backend health indicator |

---

## Success Indicators

✅ You'll know it's working when you see:
1. `[API]` logs in browser console
2. Network requests in DevTools Network tab
3. Real data from backend displayed on pages
4. Green success messages on form submissions
5. Loading spinners while fetching data
6. Clear error messages if something fails

---

## Next Steps

1. ✅ Run backend (Terminal 1)
2. ✅ Run Flutter (Terminal 2)
3. ✅ Test login flow
4. ✅ Test each page scenario above
5. ✅ Watch console logs
6. ✅ Verify Network requests

**Everything is fully integrated!** 🎉

If any test fails, check the console logs first - they'll tell you exactly what went wrong and how to fix it.
