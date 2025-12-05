"""Quick test to see if new models work"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mamacare_project.settings')
django.setup()

from predictions.ml_service import ml_service

print("Loading models...")
ml_service.load_models()

print("\n" + "="*70)
print("MODEL LOADING RESULTS")
print("="*70)

if ml_service.models_loaded:
    print("✅ All models loaded successfully!")
    print(f"\nPreeclampsia features ({len(ml_service.preeclampsia_features)}):")
    for i, feat in enumerate(ml_service.preeclampsia_features, 1):
        print(f"   {i:2d}. '{feat}'")
    
    # Test a prediction
    print("\n" + "="*70)
    print("TESTING PREDICTION")
    print("="*70)
    
    test_data = {
        'age': 35, 'systolic_bp': 150, 'diastolic_bp': 95, 'bs': 10.0,
        'body_temp': 38.0, 'heart_rate': 90, 'bmi_val': 32.0,
        'gravida': 3, 'parity': 2, 'gestational_age_weeks': 30.0,
        'diabetes_history_preeclampsia': 1, 'history_hypertension': 1,
        'hemoglobin_val': 11.0, 'fetal_weight_kgs': 1.2, 'protein_uria': 1,
        'amniotic_fluid_levels_cm': 10.0, 'num_pregnancies': 3,
        'gestation_previous_pregnancy': 1, 'hdl': 40.0, 'family_history': 1,
        'unexplained_prenatal_loss': 0, 'large_child_birth_default': 0,
        'pcos': 0, 'ogtt': 180.0, 'sedentary_lifestyle': 1,
        'prediabetes_flag_gdm': 1, 'previous_complications': 1,
        'preexisting_diabetes_flag': 1, 'gestational_diabetes_flag_gen_model': 1,
        'mental_health': 0
    }
    
    try:
        result = ml_service.predict_all_risks(test_data)
        print("✅ Prediction successful!")
        print(f"\nResults:")
        print(f"   General Risk: {result['general_risk']}")
        print(f"   Preeclampsia: {result['preeclampsia_risk']}")
        print(f"   GDM: {result['gdm_risk']}")
        print(f"   Overall: {result['overall_assessment']}")
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("❌ Models not loaded")

print("="*70)

