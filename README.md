# Footplate Inspection System

A comprehensive Streamlit-based application for managing footplate inspections for train operations. Features role-based access control (Manager, HOD, Admin), multi-part assessment forms (Parts A/B/C with 50 total items), and an executive dashboard for analytics.

## Features

- **🔐 Authentication**: Supabase-based email/password authentication with role-based access control
- **📝 Inspection Form**: Multi-part assessment form (Parts A/B/C) with 50 total evaluation items
- **👥 Employee Management**: Built-in employee database with designation tracking
- **📊 Dashboard**: Role-based dashboards for managers, HODs, and admins
- **📈 Executive Analytics**: Comprehensive inspection analytics including:
  - Inspector performance metrics (last 30 days)
  - Latest inspections with scores
  - Detailed employee inspection history
  - Average score analysis by part
- **🗄️ Data Persistence**: Normalized Supabase PostgreSQL backend with:
  - Employees table (master data)
  - Footplate inspections table (inspection metadata)
  - Inspection scores table (per-item normalized scores)
  - Users table (authentication & role management)

## Project Structure

```
footplate-inspection-system/
├── app_footplate.py                    # Main entry point
├── auth.py                             # Authentication utilities
├── _footplate_inspection_form.py       # Inspection form module
├── _footplate_executive_dashboard.py   # Executive dashboard module
├── requirements.txt                    # Python dependencies
├── database_migration.sql              # Database schema setup
├── .env.example                        # Environment variables template
├── .streamlit/config.toml              # Streamlit configuration
├── README.md                           # This file
├── SETUP.md                            # Setup & deployment guide
├── .gitignore                          # Git ignore rules
└── LICENSE                             # Project license (MIT)
```

## Tech Stack

- **Frontend**: Streamlit 1.29.0
- **Backend**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly

## Installation

### Prerequisites

- Python 3.8+
- Supabase account (free tier available at https://supabase.com)
- Git

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd footplate-inspection-system
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Setup Environment Variables

Copy `.env.example` to `.env` and fill in your Supabase credentials:

```bash
cp .env.example .env
```

Edit `.env` with your values:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
```

### Step 4: Setup Streamlit Secrets

Create `.streamlit/secrets.toml`:

```toml
[supabase]
url = "https://your-project.supabase.co"
key = "your-anon-key"
```

### Step 5: Setup Database

1. Log in to your Supabase project
2. Go to SQL Editor
3. Copy and run all SQL from `database_migration.sql`
4. This will create all required tables and indexes

### Step 6: Run Application

```bash
streamlit run app_footplate.py
```

The app will be available at `http://localhost:8501`

## User Roles

### Manager
- Access: Inspection Form, Dashboard
- Can: Submit footplate inspections, view own submissions

### HOD (Head of Department)
- Access: Inspection Form, Dashboard, Executive Dashboard
- Can: Submit inspections, view all inspections, see analytics

### Admin
- Access: All features
- Can: Full system access, user management (future)

## Default Login Credentials

After database setup, create users through Supabase Auth:

1. Go to Supabase → Authentication → Users
2. Click "Add User"
3. Enter email and password
4. Go to `users` table and set the `role` field

## API Reference

### Authentication Endpoints

- `POST /auth/sign_in` - Email/password login
- `POST /auth/sign_up` - Create new account (if enabled)
- `POST /auth/sign_out` - Logout

### Database Tables

See `database_migration.sql` for complete schema.

## Configuration

### Streamlit Config (.streamlit/config.toml)

Default configuration included. Customize theme, layout, and other options as needed.

### Environment Variables (.env)

```
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-anon-key>
```

## Database Schema

### employees
```sql
employee_id (PK), name, designation, created_at
```

### footplate_inspections
```sql
id (PK), employee_id (FK), inspection_date, submitted_at,
inspected_by_user_id (FK to auth.users), inspected_by_name, inspected_by_role,
part_a_total, part_b_total, part_c_total, overall_total,
observations, defects_identified, corrective_actions,
ip_address, device_info, UNIQUE(employee_id, inspection_date)
```

### inspection_scores
```sql
id (PK), inspection_id (FK), part, section, item_no, item_text,
max_marks, marks_awarded
```

### users
```sql
id (PK, FK to auth.users), email, full_name, role, created_at
```

## Troubleshooting

### Error: "Supabase package not installed"
```bash
pip install supabase python-dotenv
```

### Error: "Failed to connect to Supabase"
- Check Supabase credentials in `.streamlit/secrets.toml`
- Verify network connectivity
- Ensure Supabase project is active

### Error: "Duplicate key in session state"
- Clear Streamlit cache: Press `C` in the Streamlit app
- Restart the server

### Multiple button widgets with same key
- All widgets have unique keys
- Clear browser cache and restart app

## Performance Optimization

- Employee list is cached for 60 seconds
- Use indexes on `inspection_date`, `inspected_by_user_id`, and `inspected_by_role`
- Pagination recommended for large inspection datasets

## Security Considerations

- Credentials stored in `.streamlit/secrets.toml` (never commit)
- Row-level security (RLS) can be enabled in Supabase for data isolation
- Recommend HTTPS in production
- Implement rate limiting on Supabase

## Future Enhancements

- [ ] PDF report generation
- [ ] CSV/Excel export
- [ ] Inspection trends visualization
- [ ] Performance scoring system
- [ ] Mobile-responsive design
- [ ] Multi-language support
- [ ] Data audit logs
- [ ] User activity tracking

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Deployment

See [SETUP.md](SETUP.md) for detailed deployment instructions (Streamlit Cloud, Docker, etc.).

---

**Last Updated**: January 31, 2026
**Version**: 1.0.0
