"""
Script to check what feature names the saved models expect
Run this to see the actual feature names from your trained models
"""
import joblib
from pathlib import Path

ml_models_dir = Path('ml_models')

print("=" * 70)
print("Checking Model Feature Names")
print("=" * 70)

# Check Preeclampsia model
try:
    preeclampsia_scaler = joblib.load(ml_models_dir / 'preeclampsia_scaler.pkl')
    print("\n✅ Preeclampsia Scaler loaded")
    
    # Try to get feature names if available
    if hasattr(preeclampsia_scaler, 'feature_names_in_'):
        print("Feature names expected by preeclampsia scaler:")
        for i, name in enumerate(preeclampsia_scaler.feature_names_in_):
            print(f"  {i+1}. '{name}'")
    else:
        print("⚠️  Scaler doesn't have feature_names_in_ attribute")
        print("   This means we need to use the exact order from training")
        
except Exception as e:
    print(f"❌ Error loading preeclampsia scaler: {e}")

# Check General model
try:
    general_scaler = joblib.load(ml_models_dir / 'general_risk_scaler.pkl')
    print("\n✅ General Risk Scaler loaded")
    
    if hasattr(general_scaler, 'feature_names_in_'):
        print("Feature names expected by general risk scaler:")
        for i, name in enumerate(general_scaler.feature_names_in_):
            print(f"  {i+1}. '{name}'")
    else:
        print("⚠️  Scaler doesn't have feature_names_in_ attribute")
        
except Exception as e:
    print(f"❌ Error loading general scaler: {e}")

# Check GDM model
try:
    gdm_scaler = joblib.load(ml_models_dir / 'gdm_scaler.pkl')
    print("\n✅ GDM Scaler loaded")
    
    if hasattr(gdm_scaler, 'feature_names_in_'):
        print("Feature names expected by GDM scaler:")
        for i, name in enumerate(gdm_scaler.feature_names_in_):
            print(f"  {i+1}. '{name}'")
    else:
        print("⚠️  Scaler doesn't have feature_names_in_ attribute")
        
except Exception as e:
    print(f"❌ Error loading GDM scaler: {e}")

print("\n" + "=" * 70)
print("Note: If feature_names_in_ is not available, the models were")
print("trained with scikit-learn < 1.0. We need to use the exact")
print("feature names and order from the training notebook.")
print("=" * 70)

