"""
ML Model Service for MamaCare
Handles loading and using the three trained models for unified predictions
"""
import os
import joblib
import pandas as pd
import numpy as np
from django.conf import settings
from pathlib import Path


class MLModelService:
    """
    Service class to manage all three ML models and provide unified predictions
    """
    
    def __init__(self):
        self.models_loaded = False
        self.general_model = None
        self.general_scaler = None
        self.general_label_encoder = None
        self.general_features = None
        
        self.preeclampsia_model = None
        self.preeclampsia_scaler = None
        self.preeclampsia_features = None
        
        self.gdm_model = None
        self.gdm_scaler = None
        self.gdm_features = None
        
    def load_models(self):
        """Load all three ML models and their preprocessors"""
        if self.models_loaded:
            return
        
        models_dir = settings.ML_MODELS_DIR
        
        try:
            # Load General Maternal Health Risk Model
            self.general_model = joblib.load(models_dir / 'general_risk_model.pkl')
            self.general_scaler = joblib.load(models_dir / 'general_risk_scaler.pkl')
            self.general_label_encoder = joblib.load(models_dir / 'general_risk_label_encoder.pkl')
            self.general_features = [
                'Age', 'Systolic BP', 'Diastolic', 'BS', 'Body Temp', 'BMI',
                'Previous Complications', 'Preexisting Diabetes', 'Gestational Diabetes',
                'Mental Health', 'Heart Rate'
            ]
            
            # Load Preeclampsia Model
            self.preeclampsia_model = joblib.load(models_dir / 'preeclampsia_model.pkl')
            self.preeclampsia_scaler = joblib.load(models_dir / 'preeclampsia_scaler.pkl')
            
            # Get feature names from scaler (scikit-learn >= 1.0 stores them)
            if hasattr(self.preeclampsia_scaler, 'feature_names_in_'):
                self.preeclampsia_features = list(self.preeclampsia_scaler.feature_names_in_)
                print(f"✓ Loaded preeclampsia features from model: {len(self.preeclampsia_features)} features")
            else:
                # Fallback: exact feature names from diagnostic (with TWO spaces in BMI)
                self.preeclampsia_features = [
                    'gravida', 'parity', 'gestational age (weeks)', 'Age (yrs)', 'BMI  [kg/m²]',  # TWO spaces!
                    'diabetes', 'History of hypertension (y/n)', 'Systolic BP', 'Diastolic BP',
                    'HB', 'fetal weight(kgs)', 'Protien Uria', 'amniotic fluid levels(cm)'
                ]
                print("⚠️  Using hardcoded feature names (model doesn't store feature names)")
            
            # Load Gestational Diabetes Model
            self.gdm_model = joblib.load(models_dir / 'gdm_model.pkl')
            self.gdm_scaler = joblib.load(models_dir / 'gdm_scaler.pkl')
            
            # Get feature names from scaler
            if hasattr(self.gdm_scaler, 'feature_names_in_'):
                self.gdm_features = list(self.gdm_scaler.feature_names_in_)
                print(f"✓ Loaded GDM features from model: {len(self.gdm_features)} features")
            else:
                # Fallback: feature names from diagnostic (Note: 'Case Number' is NOT in the actual model)
                self.gdm_features = [
                    'Age', 'No of Pregnancy', 'Gestation in previous Pregnancy',
                    'BMI', 'HDL', 'Family History', 'unexplained prenetal loss',
                    'Large Child or Birth Default', 'PCOS', 'Sys BP', 'Dia BP', 'OGTT',
                    'Hemoglobin', 'Sedentary Lifestyle', 'Prediabetes'
                ]
                print("⚠️  Using hardcoded GDM feature names")
            
            self.models_loaded = True
            print("✓ All ML models loaded successfully")
            
        except FileNotFoundError as e:
            print(f"⚠ Warning: Model files not found. Please train and save models first.")
            print(f"Expected directory: {models_dir}")
            print("Creating placeholder models for development...")
            self._create_placeholder_models()
            self.models_loaded = True
    
    def _create_placeholder_models(self):
        """Create placeholder models for development/testing"""
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler, LabelEncoder
        
        # Placeholder for General Model
        self.general_features = [
            'Age', 'Systolic BP', 'Diastolic', 'BS', 'Body Temp', 'BMI',
            'Previous Complications', 'Preexisting Diabetes', 'Gestational Diabetes',
            'Mental Health', 'Heart Rate'
        ]
        self.general_scaler = StandardScaler()
        self.general_label_encoder = LabelEncoder()
        self.general_label_encoder.fit(['Low', 'High'])
        self.general_model = LogisticRegression(random_state=42)
        # Fit with dummy data
        dummy_X = np.random.rand(10, len(self.general_features))
        dummy_y = np.random.randint(0, 2, 10)
        self.general_scaler.fit(dummy_X)
        self.general_model.fit(self.general_scaler.transform(dummy_X), dummy_y)
        
        # Placeholder for Preeclampsia Model
        self.preeclampsia_features = [
            'gravida', 'parity', 'gestational age (weeks)', 'Age (yrs)', 'BMI [kg/m²]',
            'diabetes', 'History of hypertension (y/n)', 'Systolic BP', 'Diastolic BP',
            'HB', 'fetal weight(kgs)', 'Protien Uria', 'amniotic fluid levels(cm)'
        ]
        self.preeclampsia_scaler = StandardScaler()
        self.preeclampsia_model = LogisticRegression(random_state=42)
        dummy_X = np.random.rand(10, len(self.preeclampsia_features))
        dummy_y = np.zeros(10)  # All zeros as per notebook observation
        self.preeclampsia_scaler.fit(dummy_X)
        self.preeclampsia_model.fit(self.preeclampsia_scaler.transform(dummy_X), dummy_y)
        
        # Placeholder for GDM Model
        self.gdm_features = [
            'Case Number', 'Age', 'No of Pregnancy', 'Gestation in previous Pregnancy',
            'BMI', 'HDL', 'Family History', 'unexplained prenetal loss',
            'Large Child or Birth Default', 'PCOS', 'Sys BP', 'Dia BP', 'OGTT',
            'Hemoglobin', 'Sedentary Lifestyle', 'Prediabetes'
        ]
        self.gdm_scaler = StandardScaler()
        self.gdm_model = LogisticRegression(random_state=42)
        dummy_X = np.random.rand(10, len(self.gdm_features))
        dummy_y = np.random.randint(0, 2, 10)
        self.gdm_scaler.fit(dummy_X)
        self.gdm_model.fit(self.gdm_scaler.transform(dummy_X), dummy_y)
    
    def predict_all_risks(self, input_data):
        """
        Unified prediction function that combines all three models
        Returns predictions that appear as if from a single model
        
        Args:
            input_data: Dictionary containing all input features
            
        Returns:
            dict: Unified risk assessment with all three predictions
        """
        if not self.models_loaded:
            self.load_models()
        
        # Extract input values
        age = input_data.get('age', 25)
        systolic_bp = input_data.get('systolic_bp', 120)
        diastolic_bp = input_data.get('diastolic_bp', 80)
        bs = input_data.get('bs', 7.0)
        body_temp = input_data.get('body_temp', 37.0)
        heart_rate = input_data.get('heart_rate', 75)
        previous_complications = input_data.get('previous_complications', 0)
        preexisting_diabetes_flag = input_data.get('preexisting_diabetes_flag', 0)
        gestational_diabetes_flag_gen_model = input_data.get('gestational_diabetes_flag_gen_model', 0)
        mental_health = input_data.get('mental_health', 0)
        bmi_val = input_data.get('bmi_val', 22.0)
        gravida = input_data.get('gravida', 2)
        parity = input_data.get('parity', 1)
        gestational_age_weeks = input_data.get('gestational_age_weeks', 28.0)
        diabetes_history_preeclampsia = input_data.get('diabetes_history_preeclampsia', 0)
        history_hypertension = input_data.get('history_hypertension', 0)
        hemoglobin_val = input_data.get('hemoglobin_val', 12.0)
        fetal_weight_kgs = input_data.get('fetal_weight_kgs', 1.5)
        protein_uria = input_data.get('protein_uria', 0)
        amniotic_fluid_levels_cm = input_data.get('amniotic_fluid_levels_cm', 12.0)
        num_pregnancies = input_data.get('num_pregnancies', 2)
        gestation_previous_pregnancy = input_data.get('gestation_previous_pregnancy', 0)
        hdl = input_data.get('hdl', 50.0)
        family_history = input_data.get('family_history', 0)
        unexplained_prenatal_loss = input_data.get('unexplained_prenatal_loss', 0)
        large_child_birth_default = input_data.get('large_child_birth_default', 0)
        pcos = input_data.get('pcos', 0)
        ogtt = input_data.get('ogtt', 140.0)
        sedentary_lifestyle = input_data.get('sedentary_lifestyle', 0)
        prediabetes_flag_gdm = input_data.get('prediabetes_flag_gdm', 0)
        
        # --- 1. General Maternal Health Risk Prediction ---
        input_df_general = pd.DataFrame([{
            'Age': age,
            'Systolic BP': systolic_bp,
            'Diastolic': diastolic_bp,
            'BS': bs,
            'Body Temp': body_temp,
            'BMI': bmi_val,
            'Previous Complications': previous_complications,
            'Preexisting Diabetes': preexisting_diabetes_flag,
            'Gestational Diabetes': gestational_diabetes_flag_gen_model,
            'Mental Health': mental_health,
            'Heart Rate': heart_rate
        }])
        
        scaled_input_general = self.general_scaler.transform(input_df_general[self.general_features])
        prediction_general_numeric = self.general_model.predict(scaled_input_general)
        predicted_general_risk = self.general_label_encoder.inverse_transform(prediction_general_numeric)[0]
        
        # --- 2. Preeclampsia Risk Prediction ---
        # Detect which model format we're using and map features accordingly
        
        # Check if this is the new model format (has 'age', 'gest_age', etc.)
        new_model_features = ['age', 'gest_age', 'height', 'weight', 'bmi', 'sysbp', 'diabp', 
                             'hb', 'platelet', 'creatinine', 'tsh', 'diabetes', 'sp_art']
        
        is_new_model = all(feat in self.preeclampsia_features for feat in ['age', 'gest_age', 'sysbp'])
        
        if is_new_model:
            # NEW MODEL FORMAT - Map UI inputs to new feature names
            # Calculate weight from BMI (assuming average height ~160cm for estimation)
            estimated_height = 160.0  # cm (average)
            estimated_weight = (bmi_val * (estimated_height/100)**2) if bmi_val else 60.0
            
            preeclampsia_data = {
                'age': age,
                'gest_age': gestational_age_weeks,  # gestational age in weeks
                'height': estimated_height,  # Not in UI - using average (160cm)
                'weight': estimated_weight,  # Estimated from BMI
                'bmi': bmi_val,
                'sysbp': systolic_bp,  # systolic blood pressure
                'diabp': diastolic_bp,  # diastolic blood pressure
                'hb': hemoglobin_val,  # hemoglobin
                'platelet': 250.0,  # Not in UI - using normal range default (150-450)
                'creatinine': 0.8,  # Not in UI - using normal range default (0.6-1.2)
                'tsh': 2.0,  # Not in UI - using normal range default (0.4-4.0)
                'diabetes': diabetes_history_preeclampsia,
                'sp_art': history_hypertension  # Special arterial/hypertension history
            }
        else:
            # OLD MODEL FORMAT - Use original feature names
            preeclampsia_data = {
                'gravida': gravida,
                'parity': parity,
                'gestational age (weeks)': gestational_age_weeks,
                'Age (yrs)': age,
                'diabetes': diabetes_history_preeclampsia,
                'History of hypertension (y/n)': history_hypertension,
                'Systolic BP': systolic_bp,
                'Diastolic BP': diastolic_bp,
                'HB': hemoglobin_val,
                'fetal weight(kgs)': fetal_weight_kgs,
                'Protien Uria': protein_uria,
                'amniotic fluid levels(cm)': amniotic_fluid_levels_cm
            }
            
            # Add BMI with the EXACT column name from model
            bmi_column = [f for f in self.preeclampsia_features if 'BMI' in f.upper() or 'bmi' in f.lower()]
            if bmi_column:
                preeclampsia_data[bmi_column[0]] = bmi_val
        
        input_df_preeclampsia = pd.DataFrame([preeclampsia_data])
        
        # Reorder columns to match exactly what the scaler expects
        try:
            input_df_preeclampsia = input_df_preeclampsia[self.preeclampsia_features]
        except KeyError as e:
            # If exact match fails, try to match by normalizing names
            available_cols = list(input_df_preeclampsia.columns)
            expected_cols = self.preeclampsia_features
            
            # Create mapping
            col_mapping = {}
            for exp_col in expected_cols:
                # Try exact match first
                if exp_col in available_cols:
                    col_mapping[exp_col] = exp_col
                else:
                    # Try case-insensitive, space-normalized match
                    exp_normalized = exp_col.strip().lower().replace('  ', ' ')
                    for avail_col in available_cols:
                        avail_normalized = avail_col.strip().lower().replace('  ', ' ')
                        if exp_normalized == avail_normalized:
                            col_mapping[exp_col] = avail_col
                            break
                    else:
                        raise ValueError(f"Could not map feature '{exp_col}'. Available: {available_cols}")
            
            # Rebuild DataFrame with mapped columns
            mapped_data = {exp_col: input_df_preeclampsia[col_mapping[exp_col]].values[0] 
                          for exp_col in expected_cols}
            input_df_preeclampsia = pd.DataFrame([mapped_data])[self.preeclampsia_features]
        
        # Ensure we have all required features in the correct order
        try:
            scaled_input_preeclampsia = self.preeclampsia_scaler.transform(
                input_df_preeclampsia[self.preeclampsia_features]
            )
        except KeyError as e:
            # If feature names don't match, try to find and map them
            print(f"⚠️  Feature name mismatch: {e}")
            print(f"Expected features: {self.preeclampsia_features}")
            print(f"Available features: {list(input_df_preeclampsia.columns)}")
            
            # Try to match features case-insensitively and handle spaces
            feature_map = {}
            for expected_feat in self.preeclampsia_features:
                for actual_feat in input_df_preeclampsia.columns:
                    # Normalize both (remove extra spaces, case insensitive)
                    normalized_expected = expected_feat.strip().lower().replace(' ', '')
                    normalized_actual = actual_feat.strip().lower().replace(' ', '')
                    if normalized_expected == normalized_actual:
                        feature_map[expected_feat] = actual_feat
                        break
                else:
                    # If no match found, try partial match
                    for actual_feat in input_df_preeclampsia.columns:
                        if expected_feat.lower().replace(' ', '') in actual_feat.lower().replace(' ', ''):
                            feature_map[expected_feat] = actual_feat
                            break
            
            # Rebuild DataFrame with correct feature names
            mapped_data = {}
            for expected_feat in self.preeclampsia_features:
                if expected_feat in feature_map:
                    mapped_data[expected_feat] = input_df_preeclampsia[feature_map[expected_feat]].values[0]
                elif expected_feat in input_df_preeclampsia.columns:
                    mapped_data[expected_feat] = input_df_preeclampsia[expected_feat].values[0]
                else:
                    raise ValueError(f"Could not map feature: {expected_feat}")
            
            input_df_preeclampsia = pd.DataFrame([mapped_data])[self.preeclampsia_features]
            scaled_input_preeclampsia = self.preeclampsia_scaler.transform(input_df_preeclampsia)
        prediction_preeclampsia_numeric = self.preeclampsia_model.predict(scaled_input_preeclampsia)
        predicted_preeclampsia_risk = "Preeclampsia Present" if prediction_preeclampsia_numeric[0] == 1 else "No Preeclampsia"
        
        # --- 3. Gestational Diabetes Risk Prediction ---
        # Note: 'Case Number' is NOT in the actual model features
        input_df_gdm = pd.DataFrame([{
            'Age': age,
            'No of Pregnancy': num_pregnancies,
            'Gestation in previous Pregnancy': gestation_previous_pregnancy,
            'BMI': bmi_val,
            'HDL': hdl,
            'Family History': family_history,
            'unexplained prenetal loss': unexplained_prenatal_loss,
            'Large Child or Birth Default': large_child_birth_default,
            'PCOS': pcos,
            'Sys BP': systolic_bp,
            'Dia BP': diastolic_bp,
            'OGTT': ogtt,
            'Hemoglobin': hemoglobin_val,
            'Sedentary Lifestyle': sedentary_lifestyle,
            'Prediabetes': prediabetes_flag_gdm
        }])
        
        # Ensure columns match exactly what the model expects
        input_df_gdm = input_df_gdm[self.gdm_features]
        
        scaled_input_gdm = self.gdm_scaler.transform(input_df_gdm[self.gdm_features])
        prediction_gdm_numeric = self.gdm_model.predict(scaled_input_gdm)
        predicted_gdm_risk = "Gestational Diabetes (GDM)" if prediction_gdm_numeric[0] == 1 else "Non Gestational Diabetes (Non-GDM)"
        
        # Return unified results
        return {
            'general_risk': predicted_general_risk,
            'preeclampsia_risk': predicted_preeclampsia_risk,
            'gdm_risk': predicted_gdm_risk,
            'overall_assessment': self._generate_overall_assessment(
                predicted_general_risk,
                predicted_preeclampsia_risk,
                predicted_gdm_risk
            )
        }
    
    def _generate_overall_assessment(self, general_risk, preeclampsia_risk, gdm_risk):
        """
        Generate an overall risk assessment based on all three predictions
        This makes it appear as if it's from a single unified model
        """
        risk_levels = []
        
        # General risk
        if general_risk == 'High':
            risk_levels.append('HIGH')
        elif general_risk == 'Low':
            risk_levels.append('LOW')
        
        # Preeclampsia
        if 'Present' in preeclampsia_risk:
            risk_levels.append('HIGH')
        
        # GDM
        if 'GDM' in gdm_risk:
            risk_levels.append('MODERATE')
        
        # Determine overall risk
        if 'HIGH' in risk_levels:
            return 'HIGH RISK - Immediate medical attention recommended'
        elif 'MODERATE' in risk_levels:
            return 'MODERATE RISK - Regular monitoring advised'
        else:
            return 'LOW RISK - Continue routine care'


# Global instance
ml_service = MLModelService()

