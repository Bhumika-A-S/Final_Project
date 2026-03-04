## Tip Tracker 

TipTrack is a **proof-of-concept application** designed to digitize restaurant tipping and feedback. It now features a Flutter web frontend communicating with a FastAPI backend; the original Streamlit UI has been retained for reference but is no longer required.
It allows customers to:  
- Tip waiters digitally via unique QR codes  
- Provide service ratings  
- Share feedback that is analyzed for sentiment  

The application is powered by synthetic data and runs entirely offline for demonstration purposes, making it simple to test without additional setup.  

---

### Current Capabilities  
- **QR Code Generation** – Unique QR codes for each waiter  
- **Customer Interface** – Enter tip amount, rating, and feedback  
- **Waiter Dashboard** – View earnings, ratings, and feedback sentiment  
- **Owner Dashboard** – See aggregated analytics, rankings, and service trends  

---

### Role-based access (current behavior)
- **Admin**: Full access to all pages, QR generation, and detailed waiter views.
- **Waiter**: After signing in, must select their `waiter_id` in the sidebar and can only view their own dashboard and metrics (no other waiters' details).
- **Owner**: Can view team-level aggregates and recommendations but cannot see per-waiter raw details or individual feedback rows.

---

### Quick start (local)
1. Create a virtual environment and install requirements:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # PowerShell
pip install -r requirements.txt
```
2. (Optional) Generate sample data from the app UI or run the generator:
```powershell
python -m app.generate_data
```
 # TipTrack

TipTrack is a proof-of-concept for digitizing restaurant tips and feedback. Originally built in Streamlit, the project has migrated to a Flutter web frontend backed by a FastAPI service. The system demonstrates QR‑driven customer flows, per‑waiter dashboards, owner analytics, and AI‑driven sentiment insights.

Key principles:
- Local-first: CSVs in `data/` and QR images in `data/qrcodes/` make the demo portable.
- Role-aware UI: `customer`, `waiter`, `owner`, and `admin` roles control what each user can see.
- Extensible insights: a lightweight sentiment/insights module provides recommendations and scores.

---

## REST API Endpoints 📡

The backend exposes a FastAPI service used by the Streamlit frontend or any other client (e.g. Flutter).
All routes are rooted at `http://<host>:8000` by default.  Authentication is handled via JWT tokens obtained
from `/auth/login`.

| Method | Path | Description | Auth | Response Model |
|--------|------|-------------|------|----------------|
| GET    | `/` | Simple health/message | none | `{message}` |
| POST   | `/auth/login` | Obtain access token | none | `AuthToken` |
| GET    | `/waiters` | List all waiters | bearer | `[WaiterResponse]` |
| GET    | `/waiters/{id}` | Get a waiter | bearer | `WaiterResponse` |
| GET    | `/waiters/{id}/summary` | Aggregate stats for one waiter | bearer | `WaiterSummary` |
| POST   | `/transactions` | Submit a tip/rating/feedback | none (customer) | `TransactionResponse` |
| GET    | `/transactions` | **New** – list all transactions (owner/admin) | bearer | `[TransactionResponse]` |
| GET    | `/transactions/waiter/{id}` | Get a waiter's transactions | bearer | `[TransactionResponse]` |
| GET    | `/insights/waiter/{id}` | AI-driven waiter insights | bearer | `InsightResponse` |
| GET    | `/insights/team` | **New** – owner/admin team analytics & leaderboard | bearer | `TeamInsightsResponse` |
| POST   | `/qr/sign` | Admin-only payload signing for QR codes | bearer | `{payload,signature}` |
| POST   | `/qr/validate` | Validate a QR payload from client | none | decoded payload |
| GET    | `/ml/waiter/{id}/recommendations` | Personalized ML tips | bearer | dict |
| GET    | `/ml/owner/recommendations` | Owner-level ML tips | bearer | dict |
| POST   | `/payments/order` | Create Razorpay/Stripe order | none | `PaymentOrderResponse` |
| POST   | `/payments/webhook` | Payment confirmation webhook | none | `PaymentConfirmationResponse` |
| GET    | `/payments/status/{id}` | Query payment status | none | dict |


## Features

- QR code generation for each waiter (admin).
- Customer flow: submit tip amount, rating, and optional feedback via waiter-specific QR link.
- Waiter dashboard: totals, average rating, recent feedback, and AI-driven recommendations.
- Owner dashboard: team-level aggregates, leaderboards, and team recommendations.
- Admin page: bulk QR generation and PNG download.

---

## Quick Start (Windows / PowerShell)

1. Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

2. (Optional) Generate sample data if CSVs are missing. You can either use the app UI (click "Generate data now"), or run the generator directly:

```powershell
python -m app.generate_data
```

3. (Optional) Run the legacy Streamlit app (not required):

```powershell
python -m streamlit run "app/app.py"
```

4. Open http://localhost:8501 in your browser.

---

## Authentication / Demo Accounts

This project uses a simple demo auth flow for demonstration. Default demo credentials in the app UI:

- Admin: `admin` / `adminpass`
- Owner: `owner` / `ownerpass`
- Waiters: use waiter usernames produced by the sample data (sign in, then select `waiter_id` in the sidebar)

Note: This is a demo — do not use these credentials in production.

---

## Files of Interest

- `app/app.py` — **legacy** Streamlit UI (can be removed)
- `app/auth.py` — demo authentication and session handling
- `app/generate_data.py` — synthetic data generator for `data/waiters.csv` and `data/tips.csv`
- `app/sentiment.py` — sentiment analysis and `generate_insights()` helpers
- `app/utils.py` — CSV helpers and constants (`DATA_DIR`, `WAITERS_CSV`, `TIPS_CSV`, `QRCODES_DIR`)
- `data/` — storage for `waiters.csv`, `tips.csv`, and `qrcodes/`
- `test_generate_insights.py` — small test script to exercise insight generation

---

## Dependencies

Main Python dependencies are listed in `requirements.txt`. Important packages include:

- Flutter web application (under `flutter_app/`) — primary UI
- `pandas`, `numpy` — data handling
- `qrcode[pil]`, `pillow` — QR generation and image handling
- `transformers`, `torch` — optional, used by the sentiment module (install only if you need full NLP)

If you run into issues installing the optional NLP packages, you can remove them from `requirements.txt` and the app will still run with reduced sentiment features.

---

## Configuring API Keys for Advanced Insights

The app supports three sentiment providers: **local** (default), **OpenAI**, and **Gemini**. The latter two use large language models and require valid API keys. Follow these steps:

1. Copy `.env.example` to `.env` in the project root:
   ```powershell
   copy .env.example .env
   ```
2. Open `.env` in a text editor and fill in one or both of the following variables:
   ```dotenv
   OPENAI_API_KEY=sk_…       # your OpenAI secret key
   GEMINI_API_KEY=AIza…      # your Google Gemini key
   ```
   Only one provider is needed; leave the other blank or remove it.
3. Optionally set the provider explicitly (defaults to `local`) by adding:
   ```dotenv
   SENTIMENT_PROVIDER=openai  # or gemini
   ```
   The dropdown in the waiter dashboard also allows switching providers at runtime.
4. Restart the Streamlit app so the new environment variables are picked up:
   ```powershell
   python -m streamlit run "app/app.py"
   ```

Once the keys are set, the **Waiter Dashboard → Advanced insights** panel will call the chosen LLM and display tags/root causes/recommendations based on real feedback. If a key is missing or invalid, the app gracefully falls back to the local provider.

---

## Running Tests

There is a small test harness for the insights generator. Run:

```powershell
python -m pytest test_generate_insights.py -q
```

Or run the script directly to inspect outputs:

```powershell
python test_generate_insights.py
```

---

## Extending or Deploying

- Replace the demo auth in `app/auth.py` with real authentication for production.
- Integrate a payment gateway (Stripe, UPI, etc.) in the customer flow before calling `append_tip()`.
- For production, move CSV storage to a database and store QR assets in object storage.

---

## License

This repository includes a `LICENSE.txt` at the project root. Review it for usage terms.

---


