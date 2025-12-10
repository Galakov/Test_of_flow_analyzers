# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import logging
from itertools import combinations

class AnalyzerLogic:
    """
    Business logic for Analyzer Comparison Tool.
    Handles data parsing, conversion, filtering, and statistical calculations.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def identify_columns(self, df):
        """
        Identify time and data columns in the DataFrame.
        """
        time_col = None
        data_cols = []

        exclude_keywords = ['tagname', 'tag_name', 'тег', 'название']
        time_keywords = ['время', 'time', 'дата', 'date', 'timestamp', 'datetime']

        # Find time column
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in time_keywords):
                time_col = col
                break

        if time_col is None and len(df.columns) > 0:
            time_col = df.columns[0]

        # Find data columns
        for col in df.columns:
            col_lower = str(col).lower()
            if col == time_col:
                continue
            if any(keyword in col_lower for keyword in exclude_keywords):
                continue

            # Check if column is numeric (or can be converted)
            # We use a quick check on a sample to avoid expensive full conversion here
            try:
                sample = df[col].dropna().head(100)
                if len(sample) > 0:
                    # Try converting sample
                    numeric_sample = pd.to_numeric(sample, errors='coerce')
                    if numeric_sample.notna().any():
                        data_cols.append(col)
            except:
                pass

        return time_col, data_cols

    def manual_numeric_conversion(self, series):
        """
        Optimized numeric conversion using vectorization.
        Handles comma as decimal separator.
        """
        # Convert to string, replace comma with dot, then to numeric
        # This is much faster than iterating row by row
        if series.dtype == object:
            # Only do string manipulation if it's an object type (strings)
            series_str = series.astype(str).str.replace(',', '.', regex=False)
            return pd.to_numeric(series_str, errors='coerce')
        else:
            # Already numeric or compatible
            return pd.to_numeric(series, errors='coerce')

    def apply_outlier_filter(self, numeric_values):
        """
        Filter outliers: replace 0 and 1 with previous valid values.
        Vectorized implementation not fully possible for forward fill logic dependent on values,
        but we can optimize using pandas ffill.
        """
        # Create a Series to use pandas methods
        s = pd.Series(numeric_values)
        
        # Mask for values to replace (0 or 1)
        mask = (s == 0) | (s == 1)
        
        if not mask.any():
            return numeric_values
            
        # Replace 0 and 1 with NaN temporarily
        s_masked = s.copy()
        s_masked[mask] = np.nan
        
        # Forward fill to propagate last valid value
        s_filled = s_masked.ffill()
        
        # If the series starts with 0/1, they will remain NaN after ffill.
        # We can leave them as NaN or fill with next valid value (bfill) or 0.
        # Original logic left them as is (if last_valid_value was None).
        # We will fill remaining NaNs with original values (revert to 0/1 if no previous value)
        # or just leave as NaN (which effectively filters them out from plots).
        # Let's fill with original values to match original logic closely (if no prev value, keep it)
        s_final = s_filled.fillna(s)
        
        return s_final.values

    def parse_dates(self, series):
        """
        Robust date parsing with multiple strategies.
        Returns parsed Series and success boolean.
        """
        # 1. Try dayfirst=True (most common for RU locale)
        parsed = pd.to_datetime(series, dayfirst=True, errors='coerce')
        
        if parsed.isna().all():
             # 2. Try dayfirst=False
            parsed = pd.to_datetime(series, dayfirst=False, errors='coerce')

        # 3. If still have NaNs, try specific formats for remaining invalid
        if parsed.isna().any():
            # Formats to try for stubborn values
            formats = [
                '%d.%m.%Y %H:%M',         # No seconds
                '%d.%m.%Y %H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
            ]
            
            for fmt in formats:
                mask = parsed.isna()
                if not mask.any():
                    break
                
                try:
                    # Try parsing only the invalid ones
                    subset = pd.to_datetime(series[mask], format=fmt, errors='coerce')
                    # Fill in successful parses
                    parsed = parsed.fillna(subset)
                except:
                    pass

        return parsed

    def extract_range_data(self, timestamps, data_values, x_start, x_end):
        """
        Extract data within a time range.
        """
        if len(timestamps) != len(data_values):
            return None
            
        # Create mask
        if isinstance(timestamps, pd.Series):
            mask = (timestamps >= x_start) & (timestamps <= x_end)
        else:
            mask = (timestamps >= x_start) & (timestamps <= x_end)
            
        if not mask.any():
            return None
            
        return data_values[mask]

    def calculate_averages(self, extracted_data):
        """
        Calculate statistics for extracted data.
        """
        results = {}
        for col, values in extracted_data.items():
            # Filter NaNs and Infs
            valid_values = values[np.isfinite(values)]

            if len(valid_values) > 0:
                results[col] = {
                    'mean': float(np.mean(valid_values)),
                    'count': int(len(valid_values)),
                    'std': float(np.std(valid_values)),
                    'min': float(np.min(valid_values)),
                    'max': float(np.max(valid_values)),
                    'median': float(np.median(valid_values))
                }
        return results

    def calculate_comparisons(self, averages, extracted_data, analyzer_scales=None, gas_type=None):
        """
        Calculate pairwise comparisons.
        """
        comparisons = []
        col_names = list(averages.keys())

        if len(col_names) < 2:
            return comparisons

        for col1, col2 in combinations(col_names, 2):
            mean1 = averages[col1]['mean']
            mean2 = averages[col2]['mean']

            # Determine reference (Ametek)
            col1_lower = col1.lower()
            col2_lower = col2.lower()
            is_col1_ref = 'ametek' in col1_lower or 'амetek' in col1_lower
            is_col2_ref = 'ametek' in col2_lower or 'амetek' in col2_lower

            if is_col1_ref:
                base_mean = mean1
                diff_abs = mean2 - mean1
            elif is_col2_ref:
                # Swap so col1 is reference
                col1, col2 = col2, col1
                mean1, mean2 = mean2, mean1
                base_mean = mean1
                diff_abs = mean2 - mean1
            else:
                base_mean = mean1
                diff_abs = mean2 - mean1

            # Relative difference
            if base_mean != 0:
                diff_pct = (diff_abs / base_mean) * 100
            else:
                diff_pct = np.nan if diff_abs != 0 else 0.0

            # Correlation
            correlation = np.nan
            try:
                data1 = extracted_data.get(col1)
                data2 = extracted_data.get(col2)
                
                if data1 is not None and data2 is not None:
                    # Align lengths if needed (should be same from extract_range_data but safe check)
                    min_len = min(len(data1), len(data2))
                    d1 = data1[:min_len]
                    d2 = data2[:min_len]
                    
                    valid = np.isfinite(d1) & np.isfinite(d2)
                    if valid.sum() > 1:
                        correlation = np.corrcoef(d1[valid], d2[valid])[0, 1]
            except Exception as e:
                self.logger.error(f"Correlation error {col1} vs {col2}: {e}")

            # Reduced error
            reduced_error = None
            if analyzer_scales and gas_type and gas_type in analyzer_scales:
                scale1 = analyzer_scales[gas_type].get(col1, {}).get('scale')
                scale2 = analyzer_scales[gas_type].get(col2, {}).get('scale')
                
                max_scale = None
                if scale1 and scale2:
                    max_scale = max(scale1, scale2)
                elif scale1:
                    max_scale = scale1
                elif scale2:
                    max_scale = scale2
                    
                if max_scale:
                    reduced_error = (diff_abs / max_scale) * 100.0

            comparisons.append({
                'pair': (col1, col2),
                'mean1': mean1,
                'mean2': mean2,
                'diff_abs': diff_abs,
                'diff_pct': diff_pct,
                'count1': averages[col1]['count'],
                'count2': averages[col2]['count'],
                'correlation': correlation,
                'reduced_error': reduced_error
            })

        return comparisons
