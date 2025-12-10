import sys
import logging
from PyQt5.QtWidgets import QApplication

# Setup logging to console for verification
logging.basicConfig(level=logging.INFO)

try:
    print("Importing analyzer_comparison...")
    import analyzer_comparison
    print("Import successful.")
    
    print("Checking AnalyzerLogic integration...")
    from analyzer_logic import AnalyzerLogic
    logic = AnalyzerLogic()
    print("AnalyzerLogic instantiated.")
    
    print("Checking AnalyzerComparisonApp class...")
    app = QApplication(sys.argv)
    window = analyzer_comparison.AnalyzerComparisonApp()
    print("AnalyzerComparisonApp instantiated successfully.")
    
    if hasattr(window, 'logic'):
        print("window.logic attribute exists.")
        assert isinstance(window.logic, AnalyzerLogic)
    else:
        print("ERROR: window.logic attribute MISSING.")
        sys.exit(1)
        
    print("\nVERIFICATION SUCCESSFUL")
    
except Exception as e:
    print(f"\nVERIFICATION FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
