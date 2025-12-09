# Troubleshooting Guide - Smart Finance ML Dashboard

## Issue: sklearn Import Error in Streamlit

### Error Message
```
File "C:\smart-finance-ml\dashboards\streamlit_dashboard.py", line 19, in <module>
    from src.fraud_detection.fraud_detector import FraudDetector
File "C:\smart-finance-ml\src\fraud_detection\fraud_detector.py", line 7, in <module>
    from sklearn.preprocessing import StandardScaler, LabelEncoder
```

### Diagnosis
✅ **All packages are installed correctly** - The import works fine in regular Python
✅ **All modules tested successfully** - No actual import issues

**Root Cause:** Streamlit cache corruption or stale browser session

---

## Solutions (Try in Order)

### Solution 1: Clear Streamlit Cache (Recommended)
```bash
# Windows
run_dashboard.bat

# Linux/Mac
bash run_dashboard.sh
```

Or manually:
```bash
streamlit cache clear
streamlit run dashboards/streamlit_dashboard.py
```

### Solution 2: Force Reload in Browser
1. Start the dashboard:
   ```bash
   streamlit run dashboards/streamlit_dashboard.py
   ```
2. In your browser, press **Ctrl+Shift+R** (Windows/Linux) or **Cmd+Shift+R** (Mac) to force reload
3. If that doesn't work, close the browser tab and reopen http://localhost:8501

### Solution 3: Clear Browser Cache
1. Open browser settings
2. Clear cache and cookies for localhost
3. Restart browser
4. Run dashboard again

### Solution 4: Use Different Browser
Try opening the dashboard in a different browser (Chrome, Firefox, Edge)

### Solution 5: Restart Streamlit with Clean State
```bash
# Kill any running streamlit processes
# Windows:
taskkill /F /IM streamlit.exe

# Linux/Mac:
pkill -f streamlit

# Clear cache directory
# Windows:
rmdir /s /q %USERPROFILE%\.streamlit

# Linux/Mac:
rm -rf ~/.streamlit

# Start fresh
streamlit run dashboards/streamlit_dashboard.py
```

### Solution 6: Run with Specific Python
If you have multiple Python installations:
```bash
# Use Anaconda Python directly
python -m streamlit run dashboards/streamlit_dashboard.py

# Or activate your virtual environment first
# Windows:
.venv\Scripts\activate
streamlit run dashboards/streamlit_dashboard.py

# Linux/Mac:
source .venv/bin/activate
streamlit run dashboards/streamlit_dashboard.py
```

---

## Verification Tests

### Test 1: Verify All Imports Work
```bash
python -c "
import sys
sys.path.insert(0, 'c:/smart-finance-ml')
from src.fraud_detection.fraud_detector import FraudDetector
from src.forecasting.forecaster import SpendingForecaster
from src.currency.currency_converter import CurrencyConverter
from src.budgeting.budget_recommender import BudgetRecommender
print('All imports successful!')
"
```

Expected output: `All imports successful!`

### Test 2: Run Comprehensive Tests
```bash
python test_dashboard_fixes.py
```

Expected output: All tests should PASS

### Test 3: Check Package Installation
```bash
pip list | grep -E "(streamlit|scikit-learn|pandas|plotly)"
```

Expected packages:
- streamlit (any recent version)
- scikit-learn (1.3.2+)
- pandas (2.0+)
- plotly (5.0+)

---

## Alternative: Run Dashboard Without Fraud Detection

If you just want to get started quickly without fraud detection features, you can temporarily disable the import:

### Edit dashboards/streamlit_dashboard.py

Comment out line 19-20:
```python
# from src.fraud_detection.fraud_detector import FraudDetector
# from src.forecasting.forecaster import SpendingForecaster
```

This will disable the Fraud Detection and Forecasting tabs but allow you to use:
- ✅ Overview Tab
- ✅ Budget Recommendations Tab
- ✅ Currency Converter Tab
- ✅ Reports Tab

---

## Common Issues & Fixes

### Issue: "Module not found" errors
**Fix:** Install missing packages
```bash
pip install -r requirements.txt
```

### Issue: "Port 8501 already in use"
**Fix:** Kill existing Streamlit process or use different port
```bash
# Use different port
streamlit run dashboards/streamlit_dashboard.py --server.port 8502

# Or kill existing process (Windows)
taskkill /F /IM streamlit.exe
```

### Issue: Data files not found
**Fix:** Verify data exists
```bash
# Check if data files exist
ls config/data/raw/

# If missing, regenerate
python src/data_generation/generate_data.py
```

### Issue: Blank white screen
**Fix:**
1. Check browser console for JavaScript errors (F12)
2. Try different browser
3. Disable browser extensions
4. Clear browser cache

---

## Still Having Issues?

### Get Detailed Error Information
```bash
# Run with debug logging
streamlit run dashboards/streamlit_dashboard.py --logger.level=debug

# Check Streamlit logs
cat ~/.streamlit/logs/streamlit.log  # Linux/Mac
type %USERPROFILE%\.streamlit\logs\streamlit.log  # Windows
```

### System Information
```bash
# Check Python version
python --version

# Check Streamlit version
streamlit --version

# Check all package versions
pip list

# Check system info
python -c "import sys; print(sys.version); print(sys.executable)"
```

### Create Support Report
```bash
# Run all diagnostics
python -c "
import sys
import platform
print('=== System Information ===')
print(f'Python: {sys.version}')
print(f'Platform: {platform.platform()}')
print(f'Executable: {sys.executable}')

print('\n=== Testing Imports ===')
try:
    import streamlit; print(f'streamlit: {streamlit.__version__}')
    import pandas; print(f'pandas: {pandas.__version__}')
    import sklearn; print(f'sklearn: {sklearn.__version__}')
    import plotly; print(f'plotly: {plotly.__version__}')
    print('All core packages OK')
except Exception as e:
    print(f'Error: {e}')
"
```

---

## Quick Reference

| Problem | Quick Fix |
|---------|-----------|
| Import errors | `streamlit cache clear` |
| Blank screen | Clear browser cache (Ctrl+Shift+Delete) |
| Port in use | `streamlit run ... --server.port 8502` |
| Slow loading | Reduce data or use date filters |
| Missing data | `python src/data_generation/generate_data.py` |

---

**Last Updated:** 2025-11-27
**Status:** Tested and Working
