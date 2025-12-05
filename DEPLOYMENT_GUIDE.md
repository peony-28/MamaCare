# MamaCare Deployment Guide

Complete step-by-step guide to deploy MamaCare to production.

## 📋 Pre-Deployment Checklist

Before deploying, ensure you have:

- [x] All ML models in `ml_models/` directory
- [x] MongoDB Atlas account (free tier is fine)
- [x] GitHub account (for code repository)
- [x] Render account (or Railway/Heroku)
- [x] All features tested locally
- [x] Environment variables documented

---

## 🗄️ Step 1: Set Up MongoDB Atlas

### 1.1 Create MongoDB Atlas Account
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up for a free account
3. Create a new **Free** cluster (M0)
4. Choose a cloud provider and region (closest to your users)

### 1.2 Configure Database Access
1. Go to **Database Access** → **Add New Database User**
2. Create a user with:
   - **Username**: `mamacare_user` (or your choice)
   - **Password**: Generate a strong password (save it!)
   - **Database User Privileges**: Read and write to any database

### 1.3 Configure Network Access
1. Go to **Network Access** → **Add IP Address**
2. For development: Add your current IP
3. For production: Click **"Allow Access from Anywhere"** (0.0.0.0/0)
   - ⚠️ This is safe because you have username/password authentication

### 1.4 Get Connection String
1. Go to **Database** → **Connect** → **Connect your application**
2. Copy the connection string (looks like):
   ```
   mongodb+srv://username:password@cluster.mongodb.net/
   ```
3. **Important**: Replace `<password>` with your actual password
4. **URL-encode** special characters in password if needed:
   - `@` → `%40`
   - `#` → `%23`
   - `$` → `%24`
   - `%` → `%25`
   - etc.

### 1.5 Test Connection
Use the connection string in your local `.env` file and test:
```bash
python check_mongodb.py
```

---

## 📦 Step 2: Prepare Your Code for Deployment

### 2.1 Update .gitignore
Ensure `.gitignore` includes:
```
.env
*.pkl
db.sqlite3
__pycache__/
venv/
staticfiles/
```

### 2.2 Commit ML Models (Optional)
If models are small (<50MB each), you can commit them:
```bash
git add ml_models/*.pkl
git commit -m "Add ML models"
```

If models are large, consider:
- Using Git LFS (Large File Storage)
- Or uploading to cloud storage and downloading during deployment

### 2.3 Push to GitHub
```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Ready for deployment"

# Create repository on GitHub, then:
git remote add origin https://github.com/yourusername/mamacare.git
git branch -M main
git push -u origin main
```

---

## 🚀 Step 3: Deploy to Render

### 3.1 Create Render Account
1. Go to [Render](https://render.com)
2. Sign up with GitHub (recommended for easy deployment)

### 3.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Select the `mamacare` repository

### 3.3 Configure Service Settings

**Basic Settings:**
- **Name**: `mamacare` (or your choice)
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main` (or your default branch)

**Build & Deploy:**
- **Build Command**: 
  ```bash
  pip install -r requirements.txt && python manage.py collectstatic --noinput
  ```
- **Start Command**: 
  ```bash
  gunicorn mamacare_project.wsgi:application
  ```

**Instance Type:**
- **Free Tier**: 512MB RAM (good for testing)
- **Starter Plan**: $7/month (recommended for production)

### 3.4 Set Environment Variables

In Render dashboard, go to **Environment** tab and add:

```
SECRET_KEY=<generate-a-random-secret-key>
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
MONGODB_HOST=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_NAME=mamacare_db
MONGODB_USERNAME=your-mongodb-username
MONGODB_PASSWORD=your-mongodb-password
```

**Generate SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Important Notes:**
- Replace `your-app-name.onrender.com` with your actual Render URL
- Use the **full MongoDB connection string** (with password)
- Make sure password is URL-encoded if it has special characters

### 3.5 Deploy
1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Run collectstatic
   - Start the application

### 3.6 Monitor Deployment
- Watch the build logs for any errors
- First deployment takes 5-10 minutes
- Subsequent deployments are faster

---

## ✅ Step 4: Post-Deployment Verification

### 4.1 Test the Application
1. Visit your Render URL: `https://your-app-name.onrender.com`
2. Test these features:
   - [ ] Home page loads
   - [ ] User registration works
   - [ ] Login works
   - [ ] Prediction form works
   - [ ] ML predictions work
   - [ ] Dashboard loads
   - [ ] Patient history works
   - [ ] Admin features work

### 4.2 Create Admin User
You need to create a superuser for admin access:

**Option 1: Using Render Shell**
1. In Render dashboard, go to **Shell**
2. Run:
   ```bash
   python manage.py createsuperuser
   ```
3. Follow prompts to create admin user

**Option 2: Using Django Admin**
1. Visit: `https://your-app-name.onrender.com/admin/`
2. Use the superuser credentials

### 4.3 Verify MongoDB Connection
1. Make a test prediction
2. Check MongoDB Atlas dashboard → **Collections**
3. Verify data is being saved

---

## 🔧 Step 5: Configuration Updates

### 5.1 Update render.yaml (Optional)
If using `render.yaml` for infrastructure as code:

```yaml
services:
  - type: web
    name: mamacare
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput
    startCommand: gunicorn mamacare_project.wsgi:application
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: False
      - key: ALLOWED_HOSTS
        value: your-app-name.onrender.com
      - key: MONGODB_HOST
        sync: false  # Set manually in dashboard
      - key: MONGODB_NAME
        value: mamacare_db
      - key: MONGODB_USERNAME
        sync: false
      - key: MONGODB_PASSWORD
        sync: false
```

### 5.2 Update Static Files Configuration
Ensure `settings.py` has:
```python
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

---

## 🐛 Troubleshooting

### Issue: Application won't start
**Solution:**
- Check build logs in Render dashboard
- Verify all environment variables are set
- Check that `requirements.txt` is correct
- Ensure `Procfile` exists and is correct

### Issue: Static files not loading
**Solution:**
- Verify `collectstatic` runs in build command
- Check `STATIC_ROOT` and `STATIC_URL` in settings
- Ensure `whitenoise` is in `MIDDLEWARE`
- Check `STATICFILES_DIRS` includes `static/`

### Issue: MongoDB connection fails
**Solution:**
- Verify connection string is correct
- Check password is URL-encoded
- Verify IP is whitelisted in MongoDB Atlas
- Test connection string locally first

### Issue: ML models not found
**Solution:**
- Ensure models are committed to git (or uploaded separately)
- Check `ML_MODELS_DIR` path in settings
- Verify models are in `ml_models/` directory
- Check file permissions

### Issue: 500 Internal Server Error
**Solution:**
- Check Render logs for detailed error
- Verify `DEBUG=False` in production
- Check all required environment variables
- Test locally with production settings

### Issue: Slow response times
**Solution:**
- Upgrade to paid tier (more RAM)
- Optimize ML model loading (cache models)
- Use CDN for static files
- Enable database indexing

---

## 🔒 Security Checklist

Before going live, ensure:

- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is strong and unique
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] HTTPS/SSL is enabled (automatic on Render)
- [ ] MongoDB password is strong
- [ ] Admin credentials are secure
- [ ] CSRF protection is enabled (default in Django)
- [ ] SQL injection protection (Django ORM handles this)
- [ ] XSS protection (Django templates escape by default)

---

## 📊 Monitoring & Maintenance

### Regular Tasks:
1. **Monitor Logs**: Check Render logs regularly
2. **Database Backups**: MongoDB Atlas auto-backups (verify enabled)
3. **Update Dependencies**: Keep packages updated
4. **Monitor Usage**: Check MongoDB Atlas usage
5. **Performance**: Monitor response times

### Scaling:
- **Free Tier**: Good for testing, ~100 requests/day
- **Starter ($7/month)**: Good for production, ~1000 requests/day
- **Professional**: For high traffic, auto-scaling

---

## 🎯 Alternative Platforms

### Railway
1. Sign up at [Railway](https://railway.app)
2. Connect GitHub repository
3. Add environment variables
4. Deploy (similar to Render)

### Heroku
1. Sign up at [Heroku](https://heroku.com)
2. Install Heroku CLI
3. Run: `heroku create`
4. Set environment variables
5. Deploy: `git push heroku main`

---

## 📝 Quick Reference

### Important URLs:
- **Application**: `https://your-app-name.onrender.com`
- **Admin Panel**: `https://your-app-name.onrender.com/admin/`
- **MongoDB Atlas**: https://cloud.mongodb.com

### Key Commands:
```bash
# Local testing with production settings
python manage.py collectstatic
python manage.py check --deploy

# Create superuser
python manage.py createsuperuser

# Check deployment
python manage.py check
```

---

## ✅ Deployment Complete!

Once deployed, your MamaCare application will be:
- ✅ Accessible worldwide
- ✅ Secure (HTTPS enabled)
- ✅ Scalable (can upgrade as needed)
- ✅ Backed up (MongoDB Atlas backups)

**Next Steps:**
1. Share the URL with your team
2. Train health workers on using the system
3. Monitor usage and performance
4. Gather feedback for improvements

---

## 🆘 Need Help?

Common issues and solutions are in the Troubleshooting section above. For platform-specific help:
- **Render**: https://render.com/docs
- **MongoDB Atlas**: https://docs.atlas.mongodb.com
- **Django**: https://docs.djangoproject.com

Good luck with your deployment! 🚀

