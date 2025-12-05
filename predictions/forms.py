"""
Forms for MamaCare prediction system
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    """Form for registering new health workers"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class PredictionForm(forms.Form):
    """Form for collecting maternal health data for prediction"""
    
    # Patient Information
    patient_id = forms.CharField(
        label='Patient ID (leave blank for new patient)',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter existing Patient ID or leave blank for new patient',
            'id': 'patient_id_input'
        }),
        help_text='If this is a returning patient, enter their Patient ID. Otherwise, leave blank and a new ID will be assigned.'
    )
    
    patient_name = forms.CharField(
        label='Patient Name',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter patient full name',
            'required': True
        })
    )
    
    # General Health Parameters
    age = forms.IntegerField(
        label='Age (years)',
        min_value=15,
        max_value=50,
        initial=25,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    systolic_bp = forms.IntegerField(
        label='Systolic BP (mmHg)',
        min_value=80,
        max_value=200,
        initial=120,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    diastolic_bp = forms.IntegerField(
        label='Diastolic BP (mmHg)',
        min_value=40,
        max_value=120,
        initial=80,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    bs = forms.FloatField(
        label='Blood Sugar (mmol/L)',
        min_value=3.0,
        max_value=20.0,
        initial=7.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'required': True})
    )
    
    body_temp = forms.FloatField(
        label='Body Temperature (°C)',
        min_value=35.0,
        max_value=42.0,
        initial=37.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'required': True})
    )
    
    heart_rate = forms.IntegerField(
        label='Heart Rate (bpm)',
        min_value=50,
        max_value=150,
        initial=75,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    bmi_val = forms.FloatField(
        label='BMI (kg/m²)',
        min_value=15.0,
        max_value=50.0,
        initial=22.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'required': True})
    )
    
    # Pregnancy History
    gravida = forms.IntegerField(
        label='Gravida (Number of pregnancies)',
        min_value=0,
        max_value=15,
        initial=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    parity = forms.IntegerField(
        label='Parity (Number of live births)',
        min_value=0,
        max_value=15,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    gestational_age_weeks = forms.FloatField(
        label='Gestational Age (weeks)',
        min_value=0,
        max_value=42,
        initial=28.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'required': True})
    )
    
    num_pregnancies = forms.IntegerField(
        label='Number of Pregnancies (GDM Model)',
        min_value=0,
        max_value=15,
        initial=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    gestation_previous_pregnancy = forms.IntegerField(
        label='Gestation in Previous Pregnancy',
        min_value=0,
        max_value=42,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    # Medical History Flags (0=No, 1=Yes)
    previous_complications = forms.IntegerField(
        label='Previous Complications',
        min_value=0,
        max_value=1,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    preexisting_diabetes_flag = forms.IntegerField(
        label='Preexisting Diabetes',
        min_value=0,
        max_value=1,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    gestational_diabetes_flag_gen_model = forms.IntegerField(
        label='Gestational Diabetes (General Model)',
        min_value=0,
        max_value=1,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    mental_health = forms.IntegerField(
        label='Mental Health (0=Good, 1=Poor)',
        min_value=0,
        max_value=1,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    diabetes_history_preeclampsia = forms.IntegerField(
        label='Diabetes History (for Preeclampsia Model)',
        min_value=0,
        max_value=1,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    history_hypertension = forms.IntegerField(
        label='History of Hypertension',
        min_value=0,
        max_value=1,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    family_history = forms.IntegerField(
        label='Family History',
        min_value=0,
        max_value=1,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    unexplained_prenatal_loss = forms.IntegerField(
        label='Unexplained Prenatal Loss',
        min_value=0,
        max_value=1,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    large_child_birth_default = forms.IntegerField(
        label='Large Child or Birth Default',
        min_value=0,
        max_value=1,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    pcos = forms.IntegerField(
        label='PCOS',
        min_value=0,
        max_value=1,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    sedentary_lifestyle = forms.IntegerField(
        label='Sedentary Lifestyle',
        min_value=0,
        max_value=1,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    prediabetes_flag_gdm = forms.IntegerField(
        label='Prediabetes Flag (for GDM Model)',
        min_value=0,
        max_value=1,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    # Lab Values
    hemoglobin_val = forms.FloatField(
        label='Hemoglobin (g/dL)',
        min_value=5.0,
        max_value=20.0,
        initial=12.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'required': True})
    )
    
    hdl = forms.FloatField(
        label='HDL (mg/dL)',
        min_value=20.0,
        max_value=100.0,
        initial=50.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'required': True})
    )
    
    ogtt = forms.FloatField(
        label='OGTT (mg/dL)',
        min_value=50.0,
        max_value=300.0,
        initial=140.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'required': True})
    )
    
    # Fetal/Amniotic Parameters
    fetal_weight_kgs = forms.FloatField(
        label='Fetal Weight (kgs)',
        min_value=0.1,
        max_value=5.0,
        initial=1.5,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'required': True})
    )
    
    protein_uria = forms.IntegerField(
        label='Protein Uria (0=No, >0=Yes)',
        min_value=0,
        max_value=5,
        initial=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'required': True})
    )
    
    amniotic_fluid_levels_cm = forms.FloatField(
        label='Amniotic Fluid Levels (cm)',
        min_value=0.0,
        max_value=30.0,
        initial=12.0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'required': True})
    )
