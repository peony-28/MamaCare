#!/usr/bin/env python3
"""Quick script to check new preeclampsia model compatibility"""
import joblib
from pathlib import Path

ml_models_dir = Path('ml_models')

print("=" * 70)
print("CHECKING NEW PREECLAMPSIA MODEL")
print("=" * 70)

try:
    scaler = joblib.load(ml_models_dir / 'preeclampsia_scaler.pkl')
    print("✅ Model loaded successfully\n")
    
    if hasattr(scaler, 'feature_names_in_'):
        features = list(scaler.feature_names_in_)
        print(f"📋 Model has {len(features)} features:")
        for i, feat in enumerate(features, 1):
            print(f"   {i:2d}. '{feat}'")
        
        # Required features
        required = [
            'gravida', 'parity', 'gestational age (weeks)', 'Age (yrs)', 
            'BMI  [kg/m²]', 'diabetes', 'History of hypertension (y/n)', 
            'Systolic BP', 'Diastolic BP', 'HB', 'fetal weight(kgs)', 
            'Protien Uria', 'amniotic fluid levels(cm)'
        ]
        
        print(f"\n📊 Compatibility:")
        print(f"   Required: {len(required)} features")
        print(f"   Model has: {len(features)} features")
        
        # Check matches
        matches = [f for f in required if f in features]
        missing = [f for f in required if f not in features]
        extra = [f for f in features if f not in required]
        
        print(f"\n   ✅ Matching: {len(matches)}/{len(required)}")
        if missing:
            print(f"   ❌ Missing: {len(missing)}")
            for m in missing:
                print(f"      - '{m}'")
        if extra:
            print(f"   ⚠️  Extra features: {len(extra)}")
            for e in extra:
                print(f"      - '{e}'")
        
        print("\n" + "=" * 70)
        if len(missing) == 0 and len(features) == len(required):
            print("🎉 COMPATIBLE! Model will work with current UI.")
            print("   Just restart Django server to use new model.")
        elif len(missing) <= 2:
            print("⚠️  MOSTLY COMPATIBLE")
            print("   Minor differences - may need feature mapping.")
        else:
            print("❌ NOT COMPATIBLE")
            print("   Significant differences in features.")
            print("   Need to update code or rename columns.")
        print("=" * 70)
        
    else:
        print("⚠️  Model doesn't store feature names")
        print("   Ensure training used exact feature names from required list.")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

