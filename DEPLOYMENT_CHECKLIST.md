# 🚀 MamaCare Deployment Checklist

Use this checklist to ensure a smooth deployment.

## Pre-Deployment

### Code Preparation
- [ ] All code committed to Git
- [ ] ML models in `ml_models/` directory
- [ ] `.env` file NOT committed (in `.gitignore`)
- [ ] `requirements.txt` is up to date
- [ ] `Procfile` exists and is correct
- [ ] `render.yaml` configured (optional)
- [ ] All tests pass locally

### MongoDB Atlas Setup
- [ ] MongoDB Atlas account created
- [ ] Free cluster created (M0)
- [ ] Database user created with read/write permissions
- [ ] Network access configured (0.0.0.0/0 for production)
- [ ] Connection string obtained and tested locally
- [ ] Password URL-encoded if needed

### GitHub Setup
- [ ] Repository created on GitHub
- [ ] Code pushed to GitHub
- [ ] Repository is private (recommended) or public

## Deployment

### Render Setup
- [ ] Render account created
- [ ] GitHub account connected
- [ ] New Web Service created
- [ ] Repository selected
- [ ] Build command set: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- [ ] Start command set: `gunicorn mamacare_project.wsgi:application`
- [ ] Instance type selected (Free or Starter)

### Environment Variables
- [ ] `SECRET_KEY` set (generated securely)
- [ ] `DEBUG` set to `False`
- [ ] `ALLOWED_HOSTS` set to your Render URL
- [ ] `MONGODB_HOST` set (full connection string)
- [ ] `MONGODB_NAME` set to `mamacare_db`
- [ ] `MONGODB_USERNAME` set
- [ ] `MONGODB_PASSWORD` set (URL-encoded if needed)

### Initial Deployment
- [ ] Deployment started
- [ ] Build logs checked (no errors)
- [ ] Application started successfully
- [ ] URL accessible

## Post-Deployment

### Functionality Testing
- [ ] Home page loads
- [ ] User registration works
- [ ] User login works
- [ ] Prediction form loads
- [ ] ML predictions work correctly
- [ ] Results page displays correctly
- [ ] Patient history works
- [ ] Dashboard loads (for health workers)
- [ ] Admin features work (for admins)
- [ ] Patient lookup works
- [ ] Export CSV works (admin)
- [ ] Analytics charts load (admin)

### Admin Setup
- [ ] Superuser created via Render Shell
- [ ] Admin login works at `/admin/`
- [ ] Can access Django admin panel
- [ ] Can manage users

### Database Verification
- [ ] Test prediction saved to MongoDB
- [ ] Can view data in MongoDB Atlas
- [ ] Patient records created correctly
- [ ] Audit logs working

### Security Verification
- [ ] HTTPS enabled (automatic on Render)
- [ ] `DEBUG=False` confirmed
- [ ] Strong `SECRET_KEY` in use
- [ ] MongoDB password is secure
- [ ] Admin credentials are secure

### Performance
- [ ] Page load times acceptable
- [ ] ML predictions respond quickly
- [ ] Static files load correctly
- [ ] No 500 errors in logs

## Documentation
- [ ] Deployment guide shared with team
- [ ] Admin credentials documented (securely)
- [ ] MongoDB connection details documented (securely)
- [ ] Team trained on using the system

## Monitoring Setup
- [ ] Render logs monitoring enabled
- [ ] MongoDB Atlas monitoring checked
- [ ] Error alerts configured (if available)
- [ ] Usage metrics being tracked

## Final Steps
- [ ] Share application URL with stakeholders
- [ ] Test with real users
- [ ] Gather feedback
- [ ] Plan for improvements

---

## Quick Commands Reference

```bash
# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Test MongoDB connection locally
python check_mongodb.py

# Test static files collection
python manage.py collectstatic --dry-run

# Check deployment readiness
python manage.py check --deploy
```

---

**Status**: ⬜ Not Started | 🟡 In Progress | ✅ Complete

