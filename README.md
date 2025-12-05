# MamaCare - Maternal Health Risk Prediction System

A Django-based web application that uses machine learning to predict maternal health risks in Kenya. The system combines three specialized models (General Health Risk, Preeclampsia, and Gestational Diabetes) to provide unified risk assessments.

## 🎯 Project Overview

MamaCare is designed to help healthcare workers in rural and sub-county health facilities in Kenya identify high-risk pregnancies early, enabling timely interventions and reducing preventable maternal deaths.

## 🏗️ Architecture

- **Backend**: Django 4.2+
- **ML Models**: scikit-learn (Logistic Regression)
- **Database**: MongoDB (via PyMongo)
- **Frontend**: Bootstrap 5, HTML/CSS/JavaScript
- **Deployment**: Render/Railway ready

## 📋 Features

- ✅ Unified prediction system combining three ML models
- ✅ User authentication and role-based access
- ✅ Prediction history and dashboard
- ✅ MongoDB integration for data storage
- ✅ Responsive web interface
- ✅ Secure data handling (Data Protection Act compliant)

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- MongoDB (local or MongoDB Atlas)
- pip

### Installation

1. **Clone or navigate to the project directory**

```bash
cd MamaCare
```

2. **Create a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Set up ML Models**

You need to train and save your models first. See the `MamaCare.ipynb` notebook.

After training, save models using the code in `save_models.py`:

```python
# In your notebook, after training all models:
import joblib
from pathlib import Path

ml_models_dir = Path('ml_models')
ml_models_dir.mkdir(exist_ok=True)

# Save General Risk Model
joblib.dump(model, ml_models_dir / 'general_risk_model.pkl')
joblib.dump(scaler, ml_models_dir / 'general_risk_scaler.pkl')
joblib.dump(label_encoder, ml_models_dir / 'general_risk_label_encoder.pkl')

# Save Preeclampsia Model
joblib.dump(model_preeclampsia, ml_models_dir / 'preeclampsia_model.pkl')
joblib.dump(scaler_preeclampsia, ml_models_dir / 'preeclampsia_scaler.pkl')

# Save GDM Model
joblib.dump(model_gestational_diabetes, ml_models_dir / 'gdm_model.pkl')
joblib.dump(scaler_gestational_diabetes, ml_models_dir / 'gdm_scaler.pkl')
```

6. **Set up database**

```bash
python manage.py migrate
```

7. **Create superuser**

```bash
python manage.py createsuperuser
```

8. **Run development server**

```bash
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## 📊 ML Models

The system uses three separate models that are combined to provide unified predictions:

1. **General Maternal Health Risk Model** - Predicts overall risk level (High/Low)
2. **Preeclampsia Model** - Predicts preeclampsia risk
3. **Gestational Diabetes Model** - Predicts GDM risk

All models are loaded at startup and used together to generate comprehensive risk assessments.

## 🗄️ Database Setup

### Local MongoDB

```bash
# Install MongoDB (Ubuntu/Debian)
sudo apt-get install mongodb

# Start MongoDB
sudo systemctl start mongodb
```

### MongoDB Atlas (Cloud - Recommended)

1. Sign up at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Get your connection string
4. Update `.env` file:

```
MONGODB_HOST=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_NAME=mamacare_db
```

## 🚢 Deployment

### Deploy to Render (Recommended)

1. Push your code to GitHub
2. Sign up at [Render](https://render.com)
3. Create a new Web Service
4. Connect your GitHub repository
5. Use these settings:
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command**: `gunicorn mamacare_project.wsgi:application`
6. Add environment variables from `.env`
7. Deploy!

### Deploy to Railway

1. Push your code to GitHub
2. Sign up at [Railway](https://railway.app)
3. Create a new project from GitHub
4. Add environment variables
5. Railway auto-detects Django and deploys

### Environment Variables for Production

Make sure to set:
- `SECRET_KEY` (generate a new one)
- `DEBUG=False`
- `ALLOWED_HOSTS=your-domain.com`
- MongoDB connection string

## 📁 Project Structure

```
MamaCare/
├── mamacare_project/      # Django project settings
├── predictions/           # Main app
│   ├── ml_service.py     # ML model service
│   ├── db_service.py     # MongoDB service
│   ├── forms.py          # Django forms
│   ├── views.py          # Views
│   └── urls.py           # URL routing
├── templates/            # HTML templates
├── ml_models/            # Trained ML models (not in git)
├── static/               # Static files
├── manage.py
├── requirements.txt
└── README.md
```

## 🔒 Security Features

- Django authentication system
- CSRF protection
- Secure password hashing
- MongoDB connection security
- Environment variable configuration
- Data Protection Act compliance

## 📝 Usage

1. **Login** with your credentials
2. **Enter patient data** in the prediction form
3. **View results** with unified risk assessment
4. **Check dashboard** for statistics and history
5. **Review history** of all predictions

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Check for issues
python manage.py check
```

## 📚 Documentation

- See `DEPLOYMENT_RECOMMENDATIONS.md` for platform recommendations
- See `Proposal chapter(1-4).docx` for project proposal
- See `MamaCare.ipynb` for model training details

## 🤝 Contributing

This is a final-term project. For questions or issues, please contact the project supervisor.

## 📄 License

This project is part of academic research at [Your Institution].

## 👥 Authors

- **Nellie Nduati** - Student (658003)
- **Dr. Stanley Githinji** - Supervisor

## 🙏 Acknowledgments

- Kenya Demographic and Health Survey (KDHS) for data insights
- Healthcare workers in Kenya for their invaluable service

---

**Note**: This system is designed as a decision-support tool and should complement, not replace, clinical expertise.

