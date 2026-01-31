# Setup & Deployment Guide

## Local Development Setup

### Prerequisites
- Python 3.8+
- pip package manager
- Git

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Create Environment Files

#### Create `.env` file:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

#### Create `.streamlit/secrets.toml` file:
```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key"
```

**⚠️ Never commit `secrets.toml` or `.env` - add to `.gitignore`**

### Step 3: Database Setup

1. Create a Supabase project at https://supabase.com
2. Go to SQL Editor
3. Copy all SQL from `database_migration.sql`
4. Execute the SQL to create tables and indexes

### Step 4: Create Test User

In Supabase Dashboard:
1. Navigate to Authentication → Users
2. Click "Add User"
3. Enter email: `manager@example.com`, password: `Test@123`
4. Go to SQL Editor and run:

```sql
INSERT INTO public.users (id, email, full_name, role)
SELECT id, email, 'Test Manager', 'manager'
FROM auth.users WHERE email = 'manager@example.com'
ON CONFLICT DO NOTHING;
```

### Step 5: Run Application

```bash
streamlit run app_footplate.py
```

App opens at: `http://localhost:8501`

---

## Production Deployment

### Option 1: Streamlit Cloud (Recommended)

#### Prerequisites
- GitHub repository with project
- Streamlit account

#### Steps:

1. **Push to GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Connect GitHub repo
   - Select `app_footplate.py` as main file
   - Set Python version: 3.9+

3. **Set Secrets in Cloud**
   - In app settings, go to "Secrets"
   - Paste contents of `.streamlit/secrets.toml`:
   ```toml
   [supabase]
   url = "https://your-project.supabase.co"
   key = "your-anon-key"
   ```

4. **Deploy**
   - Click "Deploy"
   - App will be live in 1-2 minutes

### Option 2: Docker Container

#### Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app_footplate.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Build & Run:
```bash
docker build -t footplate-inspection .
docker run -p 8501:8501 -e STREAMLIT_SERVER_HEADLESS=true footplate-inspection
```

### Option 3: AWS/GCP/Azure Deployment

See cloud provider documentation for Python app deployment.

---

## Environment-Specific Configuration

### Development
```toml
[logger]
level = "debug"

[client]
toolbarMode = "developer"
```

### Production
```toml
[logger]
level = "info"

[client]
toolbarMode = "minimal"

[server]
sslCertFile = "/path/to/cert.pem"
sslKeyFile = "/path/to/key.pem"
```

---

## Database Backup & Recovery

### Backup Supabase Data

Use Supabase CLI:

```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Backup
supabase db pull

# Creates migration files for data
```

### Restore from Backup

```bash
supabase db push
```

---

## Monitoring & Maintenance

### Enable Supabase Logging

In Supabase Dashboard:
1. Settings → Logs
2. Monitor query performance
3. Set up alerts for errors

### Health Checks

```python
# Simple health check endpoint
@st.cache_resource
def health_check():
    try:
        supabase.table("employees").select("id").limit(1).execute()
        return "✅ Database connected"
    except:
        return "❌ Database error"
```

### Performance Monitoring

- Monitor app load times
- Track database query duration
- Use Streamlit metrics dashboard

---

## Scaling Considerations

### For Large Datasets

1. **Implement pagination** in inspection queries:
```python
def get_inspections_paginated(page=0, size=50):
    offset = page * size
    return supabase.table("footplate_inspections").select("*").offset(offset).limit(size).execute()
```

2. **Use database views** for complex queries:
```sql
CREATE VIEW inspector_stats AS
SELECT 
  inspected_by_name,
  COUNT(*) as total_inspections,
  MAX(submitted_at) as last_inspection
FROM footplate_inspections
GROUP BY inspected_by_name;
```

3. **Archive old data**:
```sql
-- Archive inspections older than 2 years
INSERT INTO footplate_inspections_archive
SELECT * FROM footplate_inspections
WHERE inspection_date < CURRENT_DATE - INTERVAL '2 years';

DELETE FROM footplate_inspections
WHERE inspection_date < CURRENT_DATE - INTERVAL '2 years';
```

---

## Troubleshooting Deployment

### Issue: App shows "Secrets not found"

**Solution**: Ensure `.streamlit/secrets.toml` is created with correct Supabase credentials.

### Issue: Database connection timeout

**Solution**: 
- Check network connectivity
- Verify Supabase project is active
- Check IP whitelist in Supabase settings

### Issue: High memory usage

**Solution**:
- Reduce cache TTL in `@st.cache_data(ttl=30)`
- Implement pagination for large datasets
- Use `st.cache_resource` only for client connections

---

## Version Management

### Updating Dependencies

```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade streamlit

# Update all
pip install --upgrade -r requirements.txt
```

Update `requirements.txt`:
```bash
pip freeze > requirements.txt
```

---

## Contact & Support

For deployment issues, please:
1. Check logs: `streamlit run app_footplate.py --logger.level=debug`
2. Review Supabase status page
3. Open GitHub issue with error details

---

**Last Updated**: January 31, 2026
