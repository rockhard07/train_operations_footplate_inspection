# Quick Start Guide

## Get Started in 5 Minutes

### 1. Clone & Setup
```bash
git clone <repository-url>
cd footplate-inspection-system
pip install -r requirements.txt
```

### 2. Configure Secrets
```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

Create `.streamlit/secrets.toml`:
```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key"
```

### 3. Setup Database
1. Go to Supabase SQL Editor
2. Copy all SQL from `database_migration.sql`
3. Execute it

### 4. Run Application
```bash
streamlit run app_footplate.py
```

### 5. Login
Use credentials created in Supabase:
- **Email**: Your registered email
- **Password**: Your password

---

## File Guide

| File | Purpose |
|------|---------|
| `app_footplate.py` | Main entry point, auth gate, page router |
| `auth.py` | Authentication & authorization utilities |
| `_footplate_inspection_form.py` | Multi-part inspection form |
| `_footplate_executive_dashboard.py` | Analytics dashboard |
| `database_migration.sql` | Database schema & setup |
| `requirements.txt` | Python dependencies |
| `README.md` | Full documentation |
| `SETUP.md` | Deployment guide |
| `.env.example` | Environment template |
| `.streamlit/config.toml` | Streamlit settings |

---

## Key Features Quick Reference

### Inspection Form
- **Parts**: A (35 items), B (25 items), C (20 items) = 50 total
- **Scoring**: Max 1-2 marks per item
- **Save**: Stores inspection + all 50 item scores normalized
- **Prevent Duplicates**: One inspection per employee per date

### Dashboard
- **Manager**: Form + Dashboard
- **HOD**: Form + Dashboard + Executive Dashboard
- **Admin**: All access

### Executive Dashboard
- Inspector performance (last 30 days)
- Latest 10 inspections
- Employee inspection history
- Average scores by part

---

## Troubleshooting

### App won't start?
```bash
# Clear cache
rm -rf .streamlit/cache
# Try again
streamlit run app_footplate.py
```

### Can't connect to Supabase?
- Check credentials in `.streamlit/secrets.toml`
- Verify Supabase project is active
- Check network connection

### Forgot password?
- Go to Supabase → Authentication
- Users can reset via email

---

## Next Steps

1. ✅ Create Supabase account
2. ✅ Run database migration
3. ✅ Create test user
4. ✅ Start inspection workflow
5. 📊 View analytics in executive dashboard

---

**Need Help?** See `SETUP.md` or `README.md` for detailed info.
