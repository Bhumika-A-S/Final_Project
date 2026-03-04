# TipTrack - Full API Integration Guide

## 📋 Current Setup

✅ **Backend (FastAPI)**: Running on `http://127.0.0.1:8000`
✅ **Flutter Frontend**: Ready to connect at `http://localhost:8000` (web)
✅ **All API endpoints**: Implemented and connected
✅ **Database**: SQLite with demo users

---

## 🚀 How to Run Everything

### **Step 1: Start Backend API** (Terminal 1)
```powershell
cd c:\Users\ADMIN\Desktop\TipTrack
.venv\Scripts\uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### **Step 2: Build & Run Flutter** (Terminal 2)
```powershell
cd c:\Users\ADMIN\Desktop\TipTrack\flutter_app
flutter run -d chrome
```
**Expected Output:**
```
Flutter app running on http://localhost:3000
```

---

## 👤 Demo Login Credentials

Use these to test each role:

| Role     | Username  | Password     | Access                                  |
|----------|-----------|--------------|----------------------------------------|
| **Admin**    | admin     | adminpass    | QR signing, backend status check       |
| **Owner**    | owner     | ownerpass    | Team insights, leaderboard, analytics  |
| **Waiter**   | waiter1   | waiterpass   | Personal dashboard, tips summary       |
| **Customer** | customer  | customerpass | Submit tips & feedback                 |

---

## 🔌 API Integration Summary

### **Customer Page** (Unauthenticated)
- ✅ Fetch waiter list: `GET /waiters`
- ✅ Submit tip + feedback: `POST /transactions`
- **Data displayed**: Waiter dropdown, tip form, submission confirmation

### **Waiter Dashboard** (Authenticated)
- ✅ Fetch personal summary: `GET /waiters/{waiter_id}/summary`
  - Total tips, average rating, count
- ✅ Fetch insights: `GET /insights/waiter/{waiter_id}`
  - Performance score, trend, recommendations
- **Data displayed**: Cards showing metrics, insights, and AI recommendations

### **Owner Dashboard** (Authenticated)
- ✅ Fetch team insights: `GET /insights/team`
  - Total orders, overall score, low ratings %, leaderboard
- ✅ Pull-to-refresh capability to reload data
- **Data displayed**: Analytics cards + ranked leaderboard of waiters

### **Admin Page** (Authenticated)
- ✅ Check backend status: `GET /`
- ✅ Sign QR payload: `POST /qr/sign`
- **Data displayed**: Backend health indicator, QR code generator UI

---

## 🐛 Debugging Tips

### **If No Data Shows on Pages:**

1. **Check Backend Logs** (Terminal 1)
   - Look for error messages from FastAPI
   - Verify database queries are executing

2. **Check Browser Console** (F12 in Flutter Web)
   - View network requests to backend
   - See any CORS or authentication errors
   - Check `[API]` logs in browser console

3. **Verify Database**
   - Check `data/app.db` exists
   - Run `seed_db.py` if needed:
     ```powershell
     .venv\Scripts\python seed_db.py
     ```

4. **Test API Directly**
   - Open browser: `http://127.0.0.1:8000/docs`
   - Swagger UI shows all endpoints with try-it-out buttons
   - Test endpoints without authentication first

### **Common Issues:**

| Issue | Solution |
|-------|----------|
| "Backend unreachable" on login | Ensure backend is running on port 8000 |
| "No waiters in dropdown" | Check if `/waiters` endpoint returns data |
| "Invalid credentials" | Verify you're using correct username/password from table above |
| "Admin features forbidden" | Ensure you're logged in as admin/adminpass |
| "CORS errors" | Backend already has CORS enabled; check browser console |

---

## 📱 What Each Page Should Show

### **Login Page**
- Username & password fields
- Eye icon to toggle password visibility
- Clear error messages showing:
  - "Backend unreachable" if server isn't running
  - "Invalid credentials" if wrong password
  - "Backend responded XXX" if server replies with error

### **Customer Page**
- Dropdown list of all waiters
- Amount, rating slider (1-5), optional feedback
- "✓ Tip submitted successfully" when successful
- Can submit multiple times

### **Waiter Dashboard**
- Enter waiter ID manually or auto-fill if logged in as waiter
- Shows summary card: Total Tips ($), Average Rating, Count
- Shows insights card: Performance Score, Trend, Recommendations
- Recommendations displayed as bullet points

### **Owner Dashboard**
- Total Orders counter
- Team Performance Score (0-100)
- Low Ratings percentage
- Ranked leaderboard with rank badges (#1, #2, etc.)
- Pull-to-refresh to reload data

### **Admin Page**
- Backend Status indicator with refresh button
- Shows "Backend OK (200)" or error message
- QR code generator section
- Paste generated URL into browser to test

---

## 🔍 Checking Integration Works

### **Test 1: Submit a Tip (Customer Role)**
1. Login with `customer`/`customerpass`
2. Select a waiter from dropdown
3. Enter amount like `5.50`
4. Set rating to 4
5. Add feedback like "Great service!"
6. Click "Submit Tip"
7. **Expected**: Green success message, form clears

### **Test 2: View Waiter Insights (Waiter Role)**
1. Login with `waiter1`/`waiterpass`
2. Wait for dashboard to auto-load your summary
3. **Expected**: See your total tips, average rating, # of tips
4. **Expected**: See your performance score and recommendations

### **Test 3: View Team Leaderboard (Owner Role)**
1. Login with `owner`/`ownerpass`
2. **Expected**: See total orders count
3. **Expected**: See leaderboard sorted by tip count
4. Pull down to refresh and see latest data

### **Test 4: Check Backend Health (Admin Role)**
1. Login with `admin`/`adminpass`
2. Click the refresh button next to "Backend Status"
3. **Expected**: Shows "Backend OK (200)"

---

## 📊 API Endpoints Reference

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/` | GET | No | Health check |
| `/auth/login` | POST | No | Get JWT token |
| `/waiters` | GET | Yes | List all waiters |
| `/waiters/{id}/summary` | GET | Yes | Waiter summary stats |
| `/insights/waiter/{id}` | GET | Yes | Waiter AI insights |
| `/transactions` | GET | Owner/Admin | List all tips |
| `/transactions` | POST | No | Submit customer tip |
| `/insights/team` | GET | Owner/Admin | Team analytics |
| `/qr/sign` | POST | Admin | Sign QR payload |

---

## ✨ Key Features Implemented

✅ Real-time logging of all API calls (check browser DevTools)
✅ Detailed error messages to help debug issues
✅ Backend health check from admin page
✅ Password visibility toggle on login page
✅ Pull-to-refresh on owner dashboard
✅ Loading indicators on all data-fetching pages
✅ Proper authentication with JWT tokens
✅ Role-based access control (RBAC)
✅ Responsive UI that works on mobile/web
✅ Graceful error handling for network issues

---

## 🎯 Next Steps

1. **Run the backend** (see Step 1 above)
2. **Run Flutter** (see Step 2 above)
3. **Try logging in** with demo credentials
4. **Test each page** following the test cases above
5. **Check browser console** (F12) if anything doesn't work
6. **Review backend logs** to see API activity

**All API calls are now fully integrated!** 🎉
