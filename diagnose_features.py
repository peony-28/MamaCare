"""
Run this script to see what feature names your saved models actually expect
"""
import joblib
from pathlib import Path

ml_models_dir = Path('ml_models')

print("=" * 70)
print("DIAGNOSING MODEL FEATURE NAMES")
print("=" * 70)

# Check Preeclampsia scaler
print("\n1. PREECLAMPSIA MODEL:")
try:
    scaler = joblib.load(ml_models_dir / 'preeclampsia_scaler.pkl')
    print(f"   Scaler type: {type(scaler)}")
    
    if hasattr(scaler, 'feature_names_in_'):
        print(f"   ✓ Feature names stored in scaler:")
        for i, name in enumerate(scaler.feature_names_in_, 1):
            print(f"      {i}. '{name}'")
        print(f"\n   ⚠️  Look for the BMI column name above - note exact spacing!")
    else:
        print("   ⚠️  Scaler doesn't store feature names (older scikit-learn)")
        print("   Need to use exact feature names from training")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check General model
print("\n2. GENERAL RISK MODEL:")
try:
    scaler = joblib.load(ml_models_dir / 'general_risk_scaler.pkl')
    if hasattr(scaler, 'feature_names_in_'):
        print(f"   ✓ Feature names:")
        for i, name in enumerate(scaler.feature_names_in_, 1):
            print(f"      {i}. '{name}'")
    else:
        print("   ⚠️  No feature names stored")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check GDM model
print("\n3. GDM MODEL:")
try:
    scaler = joblib.load(ml_models_dir / 'gdm_scaler.pkl')
    if hasattr(scaler, 'feature_names_in_'):
        print(f"   ✓ Feature names:")
        for i, name in enumerate(scaler.feature_names_in_, 1):
            print(f"      {i}. '{name}'")
    else:
        print("   ⚠️  No feature names stored")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("Copy the exact feature names (especially BMI column) and update")
print("the preeclampsia_features list in predictions/ml_service.py")
print("=" * 70)

