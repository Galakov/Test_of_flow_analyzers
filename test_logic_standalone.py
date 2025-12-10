import pandas as pd
import numpy as np
from analyzer_logic import AnalyzerLogic

def test_logic():
    logic = AnalyzerLogic()
    
    # Test 1: Numeric Conversion
    print("Test 1: Numeric Conversion")
    s = pd.Series(['1,5', '2.5', '3', 'invalid', '0'])
    res = logic.manual_numeric_conversion(s)
    print(f"Input: {s.tolist()}")
    print(f"Output: {res.tolist()}")
    assert res[0] == 1.5
    assert res[1] == 2.5
    assert pd.isna(res[3])
    
    # Test 2: Outlier Filter
    print("\nTest 2: Outlier Filter")
    vals = np.array([5.0, 0.0, 5.2, 1.0, 5.3])
    filtered = logic.apply_outlier_filter(vals)
    print(f"Input: {vals}")
    print(f"Output: {filtered}")
    assert filtered[1] == 5.0
    assert filtered[3] == 5.2
    
    # Test 3: Date Parsing
    print("\nTest 3: Date Parsing")
    dates = pd.Series(['22.11.2025 16:20', '2025-11-22 16:30:00', 'invalid'])
    parsed = logic.parse_dates(dates)
    print(f"Input: {dates.tolist()}")
    print(f"Output: {parsed.tolist()}")
    assert parsed[0].year == 2025
    assert parsed[0].month == 11
    assert parsed[0].day == 22
    
    print("\nALL TESTS PASSED")

if __name__ == "__main__":
    test_logic()
