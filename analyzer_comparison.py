# -*- coding: utf-8 -*-
"""
РџСЂРѕРіСЂР°РјРјР° РґР»СЏ СЃСЂР°РІРЅРµРЅРёСЏ РґР°РЅРЅС‹С… Р°РЅР°Р»РёР·Р°С‚РѕСЂРѕРІ SO2 Рё H2S
РћС‚РѕР±СЂР°Р¶Р°РµС‚ РІСЂРµРјРµРЅРЅС‹Рµ СЂСЏРґС‹ СЃ РёРЅС‚РµСЂР°РєС‚РёРІРЅС‹Рј РїРµСЂРµРєСЂРµСЃС‚РёРµРј
"""

import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QFileDialog, QLabel,
                             QTableWidget, QTableWidgetItem, QSplitter, QDialog,
                             QTextEdit, QTabWidget, QScrollArea, QFrame, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pyqtgraph as pg
from pyqtgraph import DateAxisItem
from datetime import datetime

class DataDebuggerDialog(QDialog):
    """Р’РёР·СѓР°Р»СЊРЅС‹Р№ РѕС‚Р»Р°РґС‡РёРє РґР°РЅРЅС‹С…"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('РћС‚Р»Р°РґС‡РёРє РґР°РЅРЅС‹С… Excel С„Р°Р№Р»РѕРІ')
        self.setGeometry(200, 200, 1000, 700)
        self.init_ui()
    
    def init_ui(self):
        """РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РёРЅС‚РµСЂС„РµР№СЃР° РѕС‚Р»Р°РґС‡РёРєР°"""
        layout = QVBoxLayout(self)
        
        # Р—Р°РіРѕР»РѕРІРѕРє
        title = QLabel('РћРўР›РђР”Р§РРљ Р”РђРќРќР«РҐ EXCEL Р¤РђР™Р›РћР’')
        title.setStyleSheet('QLabel { font-size: 16px; font-weight: bold; color: #2c3e50; padding: 10px; }')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Р’РєР»Р°РґРєРё РґР»СЏ СЂР°Р·РЅС‹С… С‚РёРїРѕРІ Р°РЅР°Р»РёР·Р°
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Р’РєР»Р°РґРєР° "РЎС‚СЂСѓРєС‚СѓСЂР° С„Р°Р№Р»Р°"
        self.structure_tab = QWidget()
        self.tabs.addTab(self.structure_tab, 'РЎС‚СЂСѓРєС‚СѓСЂР° С„Р°Р№Р»Р°')
        self.init_structure_tab()
        
        # Р’РєР»Р°РґРєР° "РђРЅР°Р»РёР· РґР°РЅРЅС‹С…"
        self.analysis_tab = QWidget()
        self.tabs.addTab(self.analysis_tab, 'РђРЅР°Р»РёР· РґР°РЅРЅС‹С…')
        self.init_analysis_tab()
        
        # Р’РєР»Р°РґРєР° "РџСЂРѕР±Р»РµРјС‹ РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёСЏ"
        self.problems_tab = QWidget()
        self.tabs.addTab(self.problems_tab, 'РџСЂРѕР±Р»РµРјС‹')
        self.init_problems_tab()
        
        # РљРЅРѕРїРєРё СѓРїСЂР°РІР»РµРЅРёСЏ
        buttons_layout = QHBoxLayout()
        
        refresh_btn = QPushButton('РћР±РЅРѕРІРёС‚СЊ Р°РЅР°Р»РёР·')
        refresh_btn.clicked.connect(self.refresh_analysis)
        refresh_btn.setStyleSheet('QPushButton { padding: 8px; font-size: 11px; background-color: #3498db; color: white; }')
        buttons_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton('Р­РєСЃРїРѕСЂС‚ РѕС‚С‡РµС‚Р°')
        export_btn.clicked.connect(self.export_report)
        export_btn.setStyleSheet('QPushButton { padding: 8px; font-size: 11px; background-color: #27ae60; color: white; }')
        buttons_layout.addWidget(export_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton('Р—Р°РєСЂС‹С‚СЊ')
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet('QPushButton { padding: 8px; font-size: 11px; }')
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def init_structure_tab(self):
        """РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РІРєР»Р°РґРєРё СЃС‚СЂСѓРєС‚СѓСЂС‹ С„Р°Р№Р»Р°"""
        layout = QVBoxLayout(self.structure_tab)
        
        self.structure_text = QTextEdit()
        self.structure_text.setFont(QFont('Consolas', 10))
        self.structure_text.setReadOnly(True)
        layout.addWidget(self.structure_text)
    
    def init_analysis_tab(self):
        """РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РІРєР»Р°РґРєРё Р°РЅР°Р»РёР·Р° РґР°РЅРЅС‹С…"""
        layout = QVBoxLayout(self.analysis_tab)
        
        self.analysis_text = QTextEdit()
        self.analysis_text.setFont(QFont('Consolas', 10))
        self.analysis_text.setReadOnly(True)
        layout.addWidget(self.analysis_text)
    
    def init_problems_tab(self):
        """РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РІРєР»Р°РґРєРё РїСЂРѕР±Р»РµРј"""
        layout = QVBoxLayout(self.problems_tab)
        
        self.problems_text = QTextEdit()
        self.problems_text.setFont(QFont('Consolas', 10))
        self.problems_text.setReadOnly(True)
        layout.addWidget(self.problems_text)
    
    def analyze_data(self, data_files):
        """РђРЅР°Р»РёР· Р·Р°РіСЂСѓР¶РµРЅРЅС‹С… РґР°РЅРЅС‹С…"""
        self.data_files = data_files
        self.refresh_analysis()
    
    def refresh_analysis(self):
        """РћР±РЅРѕРІР»РµРЅРёРµ Р°РЅР°Р»РёР·Р° РґР°РЅРЅС‹С…"""
        if not hasattr(self, 'data_files') or not self.data_files:
            self.structure_text.setText("[ERROR] РќРµС‚ Р·Р°РіСЂСѓР¶РµРЅРЅС‹С… С„Р°Р№Р»РѕРІ РґР»СЏ Р°РЅР°Р»РёР·Р°")
            self.analysis_text.setText("[ERROR] РќРµС‚ РґР°РЅРЅС‹С… РґР»СЏ Р°РЅР°Р»РёР·Р°")
            self.problems_text.setText("[ERROR] РќРµС‚ РґР°РЅРЅС‹С… РґР»СЏ Р°РЅР°Р»РёР·Р° РїСЂРѕР±Р»РµРј")
            return
        
        # РђРЅР°Р»РёР· СЃС‚СЂСѓРєС‚СѓСЂС‹
        structure_info = self.analyze_structure()
        self.structure_text.setText(structure_info)
        
        # РђРЅР°Р»РёР· РґР°РЅРЅС‹С…
        analysis_info = self.analyze_data_conversion()
        self.analysis_text.setText(analysis_info)
        
        # РђРЅР°Р»РёР· РїСЂРѕР±Р»РµРј
        problems_info = self.analyze_problems()
        self.problems_text.setText(problems_info)
    
    def analyze_structure(self):
        """РђРЅР°Р»РёР· СЃС‚СЂСѓРєС‚СѓСЂС‹ С„Р°Р№Р»РѕРІ"""
        result = []
        result.append("рџ“‹ РЎРўР РЈРљРўРЈР Рђ Р—РђР“Р РЈР–Р•РќРќР«РҐ Р¤РђР™Р›РћР’")
        result.append("=" * 50)
        
        for file_type, file_data in self.data_files.items():
            df = file_data['data']
            result.append(f"\nрџ“Ѓ Р¤Р°Р№Р»: {file_type}")
            result.append(f"   РџСѓС‚СЊ: {file_data['path']}")
            result.append(f"   РЎС‚СЂРѕРє: {len(df)}")
            result.append(f"   РљРѕР»РѕРЅРѕРє: {len(df.columns)}")
            
            result.append(f"\n   РљРѕР»РѕРЅРєРё:")
            for i, col in enumerate(df.columns):
                dtype = df[col].dtype
                non_null = df[col].notna().sum()
                result.append(f"     {i:2d}. '{col}' | РўРёРї: {dtype} | РќРµ-null: {non_null}")
        
        return "\n".join(result)
    
    def analyze_data_conversion(self):
        """РђРЅР°Р»РёР· РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёСЏ РґР°РЅРЅС‹С…"""
        result = []
        result.append("рџ”¬ РђРќРђР›РР— РџР Р•РћР‘Р РђР—РћР’РђРќРРЇ Р”РђРќРќР«РҐ")
        result.append("=" * 50)
        
        for file_type, file_data in self.data_files.items():
            df = file_data['data']
            result.append(f"\nрџ“Љ Р¤Р°Р№Р»: {file_type}")
            
            # РћРїСЂРµРґРµР»СЏРµРј РєРѕР»РѕРЅРєРё РґР°РЅРЅС‹С…
            time_col, data_cols = self.identify_columns(df)
            result.append(f"   РљРѕР»РѕРЅРєР° РІСЂРµРјРµРЅРё: '{time_col}'")
            result.append(f"   РљРѕР»РѕРЅРєРё РґР°РЅРЅС‹С…: {len(data_cols)}")
            
            # РђРЅР°Р»РёР·РёСЂСѓРµРј РїРµСЂРІСѓСЋ РєРѕР»РѕРЅРєСѓ РґР°РЅРЅС‹С…
            if data_cols:
                test_col = data_cols[0]
                values = df[test_col]
                result.append(f"\n   рџ”Ќ РђРЅР°Р»РёР· РєРѕР»РѕРЅРєРё '{test_col}':")
                result.append(f"     РўРёРї РґР°РЅРЅС‹С…: {values.dtype}")
                result.append(f"     Р’СЃРµРіРѕ Р·РЅР°С‡РµРЅРёР№: {len(values)}")
                
                # РџРѕРєР°Р·С‹РІР°РµРј РїСЂРёРјРµСЂС‹ Р·РЅР°С‡РµРЅРёР№
                result.append(f"\n     РџСЂРёРјРµСЂС‹ Р·РЅР°С‡РµРЅРёР№:")
                for i in range(min(10, len(values))):
                    val = values.iloc[i]
                    result.append(f"       [{i}] '{val}' (С‚РёРї: {type(val).__name__})")
                
                # РўРµСЃС‚РёСЂСѓРµРј РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёРµ
                numeric_pd = pd.to_numeric(values, errors='coerce')
                valid_count = numeric_pd.notna().sum()
                nan_count = numeric_pd.isna().sum()
                zero_count = (numeric_pd == 0).sum()
                
                result.append(f"\n     Р РµР·СѓР»СЊС‚Р°С‚ pd.to_numeric:")
                result.append(f"       Р’Р°Р»РёРґРЅС‹С…: {valid_count}")
                result.append(f"       NaN: {nan_count}")
                result.append(f"       РќСѓР»РµР№: {zero_count}")
        
        return "\n".join(result)
    
    def analyze_problems(self):
        """РђРЅР°Р»РёР· РїСЂРѕР±Р»РµРј РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёСЏ"""
        result = []
        result.append("вљ пёЏ РђРќРђР›РР— РџР РћР‘Р›Р•Рњ РџР Р•РћР‘Р РђР—РћР’РђРќРРЇ")
        result.append("=" * 50)
        
        total_problems = 0
        
        for file_type, file_data in self.data_files.items():
            df = file_data['data']
            result.append(f"\nрџ”Ќ Р¤Р°Р№Р»: {file_type}")
            
            time_col, data_cols = self.identify_columns(df)
            
            for col in data_cols[:3]:  # РђРЅР°Р»РёР·РёСЂСѓРµРј РїРµСЂРІС‹Рµ 3 РєРѕР»РѕРЅРєРё
                values = df[col]
                result.append(f"\n   рџ“Љ РљРѕР»РѕРЅРєР° '{col}':")
                
                # РўРµСЃС‚РёСЂСѓРµРј pd.to_numeric
                numeric_pd = pd.to_numeric(values, errors='coerce')
                
                # РС‰РµРј РїСЂРѕР±Р»РµРјС‹
                problems = []
                for i in range(min(20, len(values))):
                    orig = values.iloc[i]
                    converted = numeric_pd.iloc[i]
                    
                    # РџСЂРѕР±Р»РµРјР°: РЅРµ-РЅРѕР»СЊ СЃС‚Р°Р» РЅСѓР»РµРј
                    if (pd.notna(converted) and converted == 0 and 
                        orig != 0 and orig != '0' and pd.notna(orig) and orig != ''):
                        problems.append((i, orig, converted))
                    # РџСЂРѕР±Р»РµРјР°: С‡РёСЃР»Рѕ СЃС‚Р°Р»Рѕ NaN
                    elif (pd.isna(converted) and pd.notna(orig) and 
                          orig != '' and str(orig).replace(',', '.').replace(' ', '').replace('-', '').replace('+', '').replace('e', '').replace('E', '').replace('.', '').isdigit()):
                        problems.append((i, orig, converted))
                
                if problems:
                    result.append(f"     вќЊ РќРђР™Р”Р•РќРћ РџР РћР‘Р›Р•Рњ: {len(problems)}")
                    total_problems += len(problems)
                    for idx, orig, conv in problems[:5]:
                        result.append(f"       РЎС‚СЂРѕРєР° {idx}: '{orig}' -> {conv}")
                    if len(problems) > 5:
                        result.append(f"       ... Рё РµС‰Рµ {len(problems) - 5} РїСЂРѕР±Р»РµРј")
                else:
                    result.append(f"     вњ… РџСЂРѕР±Р»РµРј РЅРµ РЅР°Р№РґРµРЅРѕ")
        
        if total_problems > 0:
            result.insert(2, f"\nрџљЁ Р’РЎР•Р“Рћ РќРђР™Р”Р•РќРћ РџР РћР‘Р›Р•Рњ: {total_problems}")
            result.insert(3, "рџ’Ў Р Р•РљРћРњР•РќР”РђР¦РРЇ: РСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ СЂСѓС‡РЅРѕРµ РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёРµ РґР»СЏ РёСЃРїСЂР°РІР»РµРЅРёСЏ")
        else:
            result.insert(2, f"\nвњ… РџР РћР‘Р›Р•Рњ РќР• РќРђР™Р”Р•РќРћ")
            result.insert(3, "вњ… pd.to_numeric СЂР°Р±РѕС‚Р°РµС‚ РєРѕСЂСЂРµРєС‚РЅРѕ")
        
        return "\n".join(result)
    
    def identify_columns(self, df):
        """РћРїСЂРµРґРµР»РµРЅРёРµ РєРѕР»РѕРЅРѕРє РІСЂРµРјРµРЅРё Рё РґР°РЅРЅС‹С… (РєРѕРїРёСЏ РёР· РѕСЃРЅРѕРІРЅРѕРіРѕ РєР»Р°СЃСЃР°)"""
        time_col = None
        data_cols = []
        
        exclude_keywords = ['tagname', 'tag_name', 'С‚РµРі', 'РЅР°Р·РІР°РЅРёРµ']
        time_keywords = ['РІСЂРµРјСЏ', 'time', 'РґР°С‚Р°', 'date', 'timestamp', 'datetime']
        
        # РџРѕРёСЃРє РєРѕР»РѕРЅРєРё РІСЂРµРјРµРЅРё
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in time_keywords):
                time_col = col
                break
        
        if time_col is None and len(df.columns) > 0:
            time_col = df.columns[0]
        
        # РџРѕРёСЃРє РєРѕР»РѕРЅРѕРє РґР°РЅРЅС‹С…
        for col in df.columns:
            col_lower = str(col).lower()
            if col == time_col:
                continue
            if any(keyword in col_lower for keyword in exclude_keywords):
                continue
            
            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                if numeric_data.notna().any():
                    data_cols.append(col)
            except:
                pass
        
        return time_col, data_cols
    
    def export_report(self):
        """Р­РєСЃРїРѕСЂС‚ РѕС‚С‡РµС‚Р° РѕС‚Р»Р°РґС‡РёРєР° РІ С„Р°Р№Р»"""
        try:
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            from datetime import datetime
            
            # Р’С‹Р±РѕСЂ С„Р°Р№Р»Р° РґР»СЏ СЃРѕС…СЂР°РЅРµРЅРёСЏ
            filename, _ = QFileDialog.getSaveFileName(
                self,
                'РЎРѕС…СЂР°РЅРёС‚СЊ РѕС‚С‡РµС‚ РѕС‚Р»Р°РґС‡РёРєР°',
                f'debug_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt',
                'Text Files (*.txt)'
            )
            
            if filename:
                # РЎРѕР±РёСЂР°РµРј РІРµСЃСЊ РѕС‚С‡РµС‚
                report = []
                report.append("рџ”Ќ РћРўР§Р•Рў РћРўР›РђР”Р§РРљРђ Р”РђРќРќР«РҐ")
                report.append("=" * 60)
                report.append(f"Р”Р°С‚Р° СЃРѕР·РґР°РЅРёСЏ: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
                report.append("")
                
                # Р”РѕР±Р°РІР»СЏРµРј СЃРѕРґРµСЂР¶РёРјРѕРµ РІСЃРµС… РІРєР»Р°РґРѕРє
                report.append(self.structure_text.toPlainText())
                report.append("\n" + "=" * 60 + "\n")
                report.append(self.analysis_text.toPlainText())
                report.append("\n" + "=" * 60 + "\n")
                report.append(self.problems_text.toPlainText())
                
                # РЎРѕС…СЂР°РЅСЏРµРј РІ С„Р°Р№Р»
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(report))
                
                QMessageBox.information(self, 'РЈСЃРїРµС…', f'РћС‚С‡РµС‚ СЃРѕС…СЂР°РЅРµРЅ РІ С„Р°Р№Р»:\n{filename}')
                
        except Exception as e:
            QMessageBox.critical(self, 'РћС€РёР±РєР°', f'РќРµ СѓРґР°Р»РѕСЃСЊ СЃРѕС…СЂР°РЅРёС‚СЊ РѕС‚С‡РµС‚:\n{str(e)}')

class AnalyzerComparisonApp(QMainWindow):
    """Р“Р»Р°РІРЅРѕРµ РѕРєРЅРѕ РїСЂРёР»РѕР¶РµРЅРёСЏ РґР»СЏ СЃСЂР°РІРЅРµРЅРёСЏ Р°РЅР°Р»РёР·Р°С‚РѕСЂРѕРІ"""
    
    def __init__(self):
        super().__init__()
        self.data_files = {}  # РЎР»РѕРІР°СЂСЊ РґР»СЏ С…СЂР°РЅРµРЅРёСЏ Р·Р°РіСЂСѓР¶РµРЅРЅС‹С… РґР°РЅРЅС‹С…
        self.plots = []  # РЎРїРёСЃРѕРє РіСЂР°С„РёРєРѕРІ
        self.crosshair_lines = []  # Р›РёРЅРёРё РїРµСЂРµРєСЂРµСЃС‚РёСЏ
        self.value_labels = []  # РњРµС‚РєРё РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ Р·РЅР°С‡РµРЅРёР№
        self.highlight_items = []  # Р­Р»РµРјРµРЅС‚С‹ РІС‹РґРµР»РµРЅРёСЏ РЅР° РіСЂР°С„РёРєРµ
        self.init_ui()
        
    def init_ui(self):
        """РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЊСЃРєРѕРіРѕ РёРЅС‚РµСЂС„РµР№СЃР°"""
        self.setWindowTitle('РЎСЂР°РІРЅРµРЅРёРµ Р°РЅР°Р»РёР·Р°С‚РѕСЂРѕРІ SO2 Рё H2S')
        self.setGeometry(100, 100, 1600, 1000)  # РЈРІРµР»РёС‡РёРІР°РµРј СЂР°Р·РјРµСЂ РѕРєРЅР°
        
        # Р¦РµРЅС‚СЂР°Р»СЊРЅС‹Р№ РІРёРґР¶РµС‚
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # РџР°РЅРµР»СЊ СѓРїСЂР°РІР»РµРЅРёСЏ
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # РџР°РЅРµР»СЊ РёРЅС„РѕСЂРјР°С†РёРё (РјРµС‚РєРё РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ Р·РЅР°С‡РµРЅРёР№ РїСЂРё РїРµСЂРµРєСЂРµСЃС‚РёРё)
        self.info_label = QLabel('РќР°РІРµРґРёС‚Рµ РєСѓСЂСЃРѕСЂ РЅР° РіСЂР°С„РёРє РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ Р·РЅР°С‡РµРЅРёР№')
        self.info_label.setStyleSheet('QLabel { background-color: #f0f0f0; padding: 10px; font-size: 12px; }')
        self.info_label.setMinimumHeight(120)
        self.info_label.setMaximumHeight(180)
        self.info_label.setWordWrap(True)
        main_layout.addWidget(self.info_label)
        
        # РЎРѕР·РґР°РµРј РіРѕСЂРёР·РѕРЅС‚Р°Р»СЊРЅС‹Р№ СЂР°Р·РґРµР»РёС‚РµР»СЊ РґР»СЏ РіСЂР°С„РёРєР° Рё С‚Р°Р±Р»РёС†С‹
        content_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(content_splitter, stretch=1)
        
        # Р›РµРІР°СЏ С‡Р°СЃС‚СЊ - РѕР±Р»Р°СЃС‚СЊ РіСЂР°С„РёРєРѕРІ
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.plot_widget.setBackground('w')
        content_splitter.addWidget(self.plot_widget)
        
        # РџСЂР°РІР°СЏ С‡Р°СЃС‚СЊ - С‚Р°Р±Р»РёС†Р° РґР°РЅРЅС‹С…
        self.create_data_table_panel(content_splitter)
        
        # РЈСЃС‚Р°РЅР°РІР»РёРІР°РµРј РїСЂРѕРїРѕСЂС†РёРё: 70% РіСЂР°С„РёРє, 30% С‚Р°Р±Р»РёС†Р°
        content_splitter.setSizes([1120, 480])
    
    def create_data_table_panel(self, parent_splitter):
        """РЎРѕР·РґР°РЅРёРµ РїР°РЅРµР»Рё СЃ С‚Р°Р±Р»РёС†РµР№ РґР°РЅРЅС‹С…"""
        # РљРѕРЅС‚РµР№РЅРµСЂ РґР»СЏ С‚Р°Р±Р»РёС†С‹
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        # Р—Р°РіРѕР»РѕРІРѕРє С‚Р°Р±Р»РёС†С‹
        table_header = QLabel('Р”Р°РЅРЅС‹Рµ РІСЂРµРјРµРЅРЅРѕРіРѕ СЂСЏРґР°')
        table_header.setStyleSheet('QLabel { font-size: 14px; font-weight: bold; color: #2c3e50; padding: 5px; }')
        table_layout.addWidget(table_header)
        
        # РЎРµР»РµРєС‚РѕСЂ С„Р°Р№Р»Р° РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ
        file_selector_layout = QHBoxLayout()
        
        file_selector_label = QLabel('Р¤Р°Р№Р»:')
        file_selector_layout.addWidget(file_selector_label)
        
        self.file_selector = QComboBox()
        self.file_selector.addItem('Р’С‹Р±РµСЂРёС‚Рµ С„Р°Р№Р»...')
        self.file_selector.currentTextChanged.connect(self.on_file_selector_changed)
        file_selector_layout.addWidget(self.file_selector)
        
        file_selector_layout.addStretch()
        
        # РљРЅРѕРїРєР° РѕР±РЅРѕРІР»РµРЅРёСЏ С‚Р°Р±Р»РёС†С‹
        refresh_table_btn = QPushButton('РћР±РЅРѕРІРёС‚СЊ')
        refresh_table_btn.clicked.connect(self.refresh_data_table)
        refresh_table_btn.setStyleSheet('QPushButton { padding: 4px; font-size: 10px; }')
        file_selector_layout.addWidget(refresh_table_btn)
        
        table_layout.addLayout(file_selector_layout)
        
        # РўР°Р±Р»РёС†Р° РґР°РЅРЅС‹С…
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setSelectionMode(QTableWidget.SingleSelection)
        self.data_table.itemSelectionChanged.connect(self.on_table_selection_changed)
        
        # РЎС‚РёР»СЊ С‚Р°Р±Р»РёС†С‹
        self.data_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #d0d0d0;
                font-size: 10px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #ecf0f1;
                padding: 4px;
                border: 1px solid #bdc3c7;
                font-weight: bold;
            }
        """)
        
        table_layout.addWidget(self.data_table)
        
        # РРЅС„РѕСЂРјР°С†РёСЏ Рѕ РІС‹Р±СЂР°РЅРЅРѕР№ СЃС‚СЂРѕРєРµ
        self.selection_info = QLabel('Р’С‹Р±РµСЂРёС‚Рµ СЃС‚СЂРѕРєСѓ РІ С‚Р°Р±Р»РёС†Рµ РґР»СЏ РІС‹РґРµР»РµРЅРёСЏ РЅР° РіСЂР°С„РёРєРµ')
        self.selection_info.setStyleSheet('QLabel { color: #7f8c8d; font-size: 10px; padding: 5px; }')
        table_layout.addWidget(self.selection_info)
        
        parent_splitter.addWidget(table_widget)
        
    def create_control_panel(self):
        """РЎРѕР·РґР°РЅРёРµ РїР°РЅРµР»Рё СѓРїСЂР°РІР»РµРЅРёСЏ СЃ РєРЅРѕРїРєР°РјРё Р·Р°РіСЂСѓР·РєРё С„Р°Р№Р»РѕРІ"""
        panel = QWidget()
        layout = QHBoxLayout(panel)
        
        # РљРЅРѕРїРєР° Р·Р°РіСЂСѓР·РєРё С„Р°Р№Р»Р° H2S
        self.btn_load_h2s = QPushButton('рџ“Ѓ Р—Р°РіСЂСѓР·РёС‚СЊ С„Р°Р№Р» H2S')
        self.btn_load_h2s.clicked.connect(lambda: self.load_file('H2S'))
        self.btn_load_h2s.setStyleSheet('QPushButton { font-size: 11px; padding: 8px; }')
        layout.addWidget(self.btn_load_h2s)
        
        # РњРµС‚РєР° СЃС‚Р°С‚СѓСЃР° H2S
        self.label_h2s = QLabel('Р¤Р°Р№Р» РЅРµ Р·Р°РіСЂСѓР¶РµРЅ')
        self.label_h2s.setStyleSheet('QLabel { color: gray; font-size: 10px; }')
        layout.addWidget(self.label_h2s)
        
        layout.addStretch()
        
        # РљРЅРѕРїРєР° Р·Р°РіСЂСѓР·РєРё С„Р°Р№Р»Р° SO2
        self.btn_load_so2 = QPushButton('рџ“Ѓ Р—Р°РіСЂСѓР·РёС‚СЊ С„Р°Р№Р» SO2')
        self.btn_load_so2.clicked.connect(lambda: self.load_file('SO2'))
        self.btn_load_so2.setStyleSheet('QPushButton { font-size: 11px; padding: 8px; }')
        layout.addWidget(self.btn_load_so2)
        
        # РњРµС‚РєР° СЃС‚Р°С‚СѓСЃР° SO2
        self.label_so2 = QLabel('Р¤Р°Р№Р» РЅРµ Р·Р°РіСЂСѓР¶РµРЅ')
        self.label_so2.setStyleSheet('QLabel { color: gray; font-size: 10px; }')
        layout.addWidget(self.label_so2)
        
        layout.addStretch()
        
        # РљРЅРѕРїРєР° РѕС‚Р»Р°РґС‡РёРєР° РґР°РЅРЅС‹С…
        self.btn_debug = QPushButton('рџ”§ РћС‚Р»Р°РґС‡РёРє РґР°РЅРЅС‹С…')
        self.btn_debug.clicked.connect(self.show_data_debugger)
        self.btn_debug.setEnabled(False)
        self.btn_debug.setStyleSheet('QPushButton { font-size: 11px; padding: 8px; background-color: #FF9800; color: white; } QPushButton:disabled { background-color: #cccccc; }')
        layout.addWidget(self.btn_debug)
        
        # РљРЅРѕРїРєР° РїРѕСЃС‚СЂРѕРµРЅРёСЏ РіСЂР°С„РёРєРѕРІ
        self.btn_plot = QPushButton('рџ“Љ РџРѕСЃС‚СЂРѕРёС‚СЊ РіСЂР°С„РёРєРё')
        self.btn_plot.clicked.connect(self.plot_data)
        self.btn_plot.setEnabled(False)
        self.btn_plot.setStyleSheet('QPushButton { font-size: 11px; padding: 8px; background-color: #4CAF50; color: white; } QPushButton:disabled { background-color: #cccccc; }')
        layout.addWidget(self.btn_plot)
        
        # РљРЅРѕРїРєР° РѕС‡РёСЃС‚РєРё
        btn_clear = QPushButton('рџ—‘пёЏ РћС‡РёСЃС‚РёС‚СЊ')
        btn_clear.clicked.connect(self.clear_all)
        btn_clear.setStyleSheet('QPushButton { font-size: 11px; padding: 8px; }')
        layout.addWidget(btn_clear)
        
        return panel
    
    def debug_data_conversion(self, df, file_type):
        """РћРўР›РђР”Р§РРљ: РђРЅР°Р»РёР· РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёСЏ РґР°РЅРЅС‹С… РёР· Excel С„Р°Р№Р»Р°"""
        print(f"\n[DEBUG] РћРўР›РђР”Р§РРљ Р”РђРќРќР«РҐ - {file_type}")
        print("=" * 60)
        
        # РћРїСЂРµРґРµР»СЏРµРј РєРѕР»РѕРЅРєРё РґР°РЅРЅС‹С…
        time_col, data_cols = self.identify_columns(df)
        
        if data_cols and len(data_cols) > 0:
            test_col = data_cols[0]  # Р‘РµСЂРµРј РїРµСЂРІСѓСЋ РєРѕР»РѕРЅРєСѓ РґР»СЏ Р°РЅР°Р»РёР·Р°
            print(f"[ANALYZE] РђРЅР°Р»РёР· РєРѕР»РѕРЅРєРё: '{test_col}'")
            
            values = df[test_col]
            print(f"РўРёРї РґР°РЅРЅС‹С…: {values.dtype}")
            print(f"Р’СЃРµРіРѕ Р·РЅР°С‡РµРЅРёР№: {len(values)}")
            
            # РџРѕРєР°Р·С‹РІР°РµРј РїРµСЂРІС‹Рµ 10 Р·РЅР°С‡РµРЅРёР№
            print("\nРџРµСЂРІС‹Рµ 10 РёСЃС…РѕРґРЅС‹С… Р·РЅР°С‡РµРЅРёР№:")
            for i in range(min(10, len(values))):
                val = values.iloc[i]
                print(f"  [{i}] '{val}' (С‚РёРї: {type(val).__name__})")
            
            # РўРµСЃС‚РёСЂСѓРµРј pd.to_numeric
            print(f"\n[TEST] РўРµСЃС‚ pd.to_numeric:")
            numeric_pd = pd.to_numeric(values, errors='coerce')
            
            # РС‰РµРј РїСЂРѕР±Р»РµРјС‹
            problems = []
            for i in range(min(20, len(values))):
                orig = values.iloc[i]
                converted = numeric_pd.iloc[i]
                
                # РџСЂРѕР±Р»РµРјР°: РЅРµ-РЅРѕР»СЊ СЃС‚Р°Р» РЅСѓР»РµРј
                if (pd.notna(converted) and converted == 0 and 
                    orig != 0 and orig != '0' and pd.notna(orig)):
                    problems.append((i, orig, converted))
            
            if problems:
                print(f"[WARNING] РќРђР™Р”Р•РќР« РџР РћР‘Р›Р•РњР« ({len(problems)} СЃР»СѓС‡Р°РµРІ):")
                for idx, orig, conv in problems[:5]:
                    print(f"  РЎС‚СЂРѕРєР° {idx}: '{orig}' -> {conv}")
                print("рџ”§ Р Р•РљРћРњР•РќР”РђР¦РРЇ: РСЃРїРѕР»СЊР·РѕРІР°С‚СЊ СЂСѓС‡РЅРѕРµ РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёРµ!")
            else:
                print("вњ… pd.to_numeric СЂР°Р±РѕС‚Р°РµС‚ РєРѕСЂСЂРµРєС‚РЅРѕ")
            
            # РЎС‚Р°С‚РёСЃС‚РёРєР° РЅСѓР»РµР№
            original_zeros = (values == 0) | (values == '0')
            converted_zeros = (numeric_pd == 0)
            new_zeros = converted_zeros & ~original_zeros
            
            print(f"\nрџ“€ РЎС‚Р°С‚РёСЃС‚РёРєР° РЅСѓР»РµР№:")
            print(f"  РСЃС…РѕРґРЅС‹С… РЅСѓР»РµР№: {original_zeros.sum()}")
            print(f"  РџРѕСЃР»Рµ РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёСЏ: {converted_zeros.sum()}")
            print(f"  РќРѕРІС‹С… РЅСѓР»РµР№: {new_zeros.sum()}")
            
            if new_zeros.sum() > 0:
                print("[WARNING] Р’РќРРњРђРќРР•: РџРѕСЏРІРёР»РёСЃСЊ РЅРѕРІС‹Рµ РЅСѓР»Рё!")
        
        print("=" * 60)

    def load_file(self, file_type):
        """Р—Р°РіСЂСѓР·РєР° Excel С„Р°Р№Р»Р° СЃ РґР°РЅРЅС‹РјРё"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            f'Р’С‹Р±РµСЂРёС‚Рµ С„Р°Р№Р» {file_type}', 
            '', 
            'Excel Files (*.xlsx *.xls)'
        )
        
        if file_path:
            try:
                # Р§С‚РµРЅРёРµ Excel С„Р°Р№Р»Р°
                df = pd.read_excel(file_path)
                
                # РџСЂРѕРІРµСЂРєР° РЅР°Р»РёС‡РёСЏ РґР°РЅРЅС‹С…
                if df.empty:
                    self.show_error(f'Р¤Р°Р№Р» {file_type} РїСѓСЃС‚')
                    return
                
                # Р—РђРџРЈРЎРљ РћРўР›РђР”Р§РРљРђ
                self.debug_data_conversion(df, file_type)
                
                # РЎРѕС…СЂР°РЅРµРЅРёРµ РґР°РЅРЅС‹С…
                self.data_files[file_type] = {
                    'path': file_path,
                    'data': df
                }
                
                # РћР±РЅРѕРІР»РµРЅРёРµ РјРµС‚РєРё СЃС‚Р°С‚СѓСЃР°
                if file_type == 'H2S':
                    self.label_h2s.setText(f'вњ… Р—Р°РіСЂСѓР¶РµРЅРѕ: {len(df)} Р·Р°РїРёСЃРµР№')
                    self.label_h2s.setStyleSheet('color: green;')
                else:
                    self.label_so2.setText(f'вњ… Р—Р°РіСЂСѓР¶РµРЅРѕ: {len(df)} Р·Р°РїРёСЃРµР№')
                    self.label_so2.setStyleSheet('color: green;')
                
                # РђРєС‚РёРІР°С†РёСЏ РєРЅРѕРїРѕРє
                if len(self.data_files) > 0:
                    self.btn_plot.setEnabled(True)
                    self.btn_debug.setEnabled(True)
                
                # РћР±РЅРѕРІР»СЏРµРј СЃРµР»РµРєС‚РѕСЂ С„Р°Р№Р»РѕРІ РІ С‚Р°Р±Р»РёС†Рµ
                self.update_file_selector()
                    
            except Exception as e:
                self.show_error(f'РћС€РёР±РєР° РїСЂРё Р·Р°РіСЂСѓР·РєРµ С„Р°Р№Р»Р° {file_type}: {str(e)}')
    
    def plot_data(self):
        """РџРѕСЃС‚СЂРѕРµРЅРёРµ РіСЂР°С„РёРєРѕРІ СЃ РґР°РЅРЅС‹РјРё РёР· Р·Р°РіСЂСѓР¶РµРЅРЅС‹С… С„Р°Р№Р»РѕРІ"""
        # РћС‡РёСЃС‚РєР° РїСЂРµРґС‹РґСѓС‰РёС… РіСЂР°С„РёРєРѕРІ
        self.plot_widget.clear()
        self.plots = []
        self.crosshair_lines = []
        
        # РћРїСЂРµРґРµР»РµРЅРёРµ РєРѕР»РёС‡РµСЃС‚РІР° РіСЂР°С„РёРєРѕРІ
        plot_configs = []
        
        if 'H2S' in self.data_files:
            df_h2s = self.data_files['H2S']['data']
            # РџРѕРёСЃРє РєРѕР»РѕРЅРѕРє СЃ РІСЂРµРјРµРЅРµРј Рё РґР°РЅРЅС‹РјРё
            time_col, data_cols = self.identify_columns(df_h2s)
            if time_col and data_cols:
                plot_configs.append(('H2S', df_h2s, time_col, data_cols))
        
        if 'SO2' in self.data_files:
            df_so2 = self.data_files['SO2']['data']
            time_col, data_cols = self.identify_columns(df_so2)
            if time_col and data_cols:
                plot_configs.append(('SO2', df_so2, time_col, data_cols))
        
        if not plot_configs:
            self.show_error('РќРµ СѓРґР°Р»РѕСЃСЊ РѕРїСЂРµРґРµР»РёС‚СЊ СЃС‚СЂСѓРєС‚СѓСЂСѓ РґР°РЅРЅС‹С…')
            return
        
        # РЎРѕР·РґР°РЅРёРµ РіСЂР°С„РёРєРѕРІ
        for i, (gas_type, df, time_col, data_cols) in enumerate(plot_configs):
            # РџСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёРµ РІСЂРµРјРµРЅРё РІ timestamp СЃ СЂР°СЃС€РёСЂРµРЅРЅРѕР№ Р»РѕРіРёРєРѕР№
            time_data = None  # РРЅРёС†РёР°Р»РёР·Р°С†РёСЏ РїРµСЂРµРјРµРЅРЅРѕР№
            
            # 1) РџСЂСЏРјР°СЏ РїРѕРїС‹С‚РєР° (СѓС‡РµС‚ dayfirst)
            # РџСЂРѕР±СѓРµРј СЂР°Р·РЅС‹Рµ РІР°СЂРёР°РЅС‚С‹ РїР°СЂСЃРёРЅРіР° РґР»СЏ РјР°РєСЃРёРјР°Р»СЊРЅРѕР№ СЃРѕРІРјРµСЃС‚РёРјРѕСЃС‚Рё
            parsed = None
            try:
                # РЎРЅР°С‡Р°Р»Р° РїСЂРѕР±СѓРµРј СЃ dayfirst=True (С„РѕСЂРјР°С‚ Р”Р”.РњРњ.Р“Р“Р“Р“)
                parsed = pd.to_datetime(df[time_col], dayfirst=True, errors='coerce')
                invalid_count = parsed.isna().sum()
                
                # Р•СЃР»Рё РјРЅРѕРіРѕ РЅРµРІР°Р»РёРґРЅС‹С… Р·РЅР°С‡РµРЅРёР№, РїСЂРѕР±СѓРµРј Р±РµР· dayfirst
                if invalid_count > len(df) * 0.3:  # Р•СЃР»Рё Р±РѕР»СЊС€Рµ 30% РЅРµРІР°Р»РёРґРЅС‹С…
                    parsed_alt = pd.to_datetime(df[time_col], dayfirst=False, errors='coerce')
                    # РСЃРїРѕР»СЊР·СѓРµРј РІР°СЂРёР°РЅС‚ СЃ РјРµРЅСЊС€РёРј РєРѕР»РёС‡РµСЃС‚РІРѕРј РѕС€РёР±РѕРє
                    if parsed_alt.isna().sum() < invalid_count:
                        parsed = parsed_alt
                        print(f"РСЃРїРѕР»СЊР·РѕРІР°РЅ РїР°СЂСЃРёРЅРі Р±РµР· dayfirst (РјРµРЅСЊС€Рµ РѕС€РёР±РѕРє: {parsed_alt.isna().sum()} vs {invalid_count})")
                
                # Р”РѕРїРѕР»РЅРёС‚РµР»СЊРЅР°СЏ РїСЂРѕРІРµСЂРєР°: РµСЃР»Рё РµСЃС‚СЊ РЅРµРІР°Р»РёРґРЅС‹Рµ Р·РЅР°С‡РµРЅРёСЏ, РїСЂРѕР±СѓРµРј РїР°СЂСЃРёС‚СЊ РёС… РѕС‚РґРµР»СЊРЅРѕ
                # Р­С‚Рѕ РІР°Р¶РЅРѕ, РµСЃР»Рё С„РѕСЂРјР°С‚ РІСЂРµРјРµРЅРё РјРµРЅСЏРµС‚СЃСЏ РІ СЃРµСЂРµРґРёРЅРµ С„Р°Р№Р»Р°
                if parsed.isna().any():
                    invalid_mask = parsed.isna()
                    invalid_indices = df.index[invalid_mask]
                    invalid_values = df.loc[invalid_mask, time_col]

                    print(f"  РћР±РЅР°СЂСѓР¶РµРЅРѕ {invalid_mask.sum()} РЅРµСЂР°СЃРїР°СЂСЃРµРЅРЅС‹С… РґР°С‚, РїСЂРѕР±СѓРµРј РґСЂСѓРіРёРµ С„РѕСЂРјР°С‚С‹...")

                    # РџСЂРѕР±СѓРµРј СЂР°Р·РЅС‹Рµ С„РѕСЂРјР°С‚С‹ РґР»СЏ РЅРµРІР°Р»РёРґРЅС‹С… Р·РЅР°С‡РµРЅРёР№
                    # Р’РђР–РќРћ: РґРѕР±Р°РІР»РµРЅ С„РѕСЂРјР°С‚ '%d.%m.%Y %H:%M' РґР»СЏ РґР°С‚ Р‘Р•Р— СЃРµРєСѓРЅРґ
                    formats_to_try = [
                        '%d.%m.%Y %H:%M',         # РљР РРўРР§РќРћ: С„РѕСЂРјР°С‚ Р±РµР· СЃРµРєСѓРЅРґ (17.11.2025 0:00)
                        '%d.%m.%Y %H:%M:%S',
                        '%d/%m/%Y %H:%M:%S',
                        '%d/%m/%Y %H:%M',
                        '%Y-%m-%d %H:%M:%S',
                        '%Y-%m-%d %H:%M',
                        '%d.%m.%Y',
                        '%Y.%m.%d %H:%M:%S',
                        '%d-%m-%Y %H:%M:%S'
                    ]

                    for fmt in formats_to_try:
                        # РџСЂРѕРІРµСЂСЏРµРј С‚РѕР»СЊРєРѕ С‚Рµ, С‡С‚Рѕ РµС‰Рµ РЅРµ СЂР°СЃРїР°СЂСЃРµРЅС‹
                        current_invalid = parsed.isna()
                        if not current_invalid.any():
                            break  # Р’СЃРµ СЂР°СЃРїР°СЂСЃРµРЅРѕ

                        current_invalid_values = df.loc[current_invalid, time_col]
                        try:
                            parsed_manual = pd.to_datetime(current_invalid_values, format=fmt, errors='coerce')
                            # Р—Р°РјРµРЅСЏРµРј СѓСЃРїРµС€РЅРѕ СЂР°СЃРїР°СЂСЃРµРЅРЅС‹Рµ Р·РЅР°С‡РµРЅРёСЏ
                            success_mask = parsed_manual.notna()
                            if success_mask.any():
                                success_indices = current_invalid_values.index[success_mask]
                                parsed.loc[success_indices] = parsed_manual[success_mask]
                                print(f"  [OK] Р’РѕСЃСЃС‚Р°РЅРѕРІР»РµРЅРѕ {success_mask.sum()} Р·Р°РїРёСЃРµР№ СЃ С„РѕСЂРјР°С‚РѕРј {fmt}")
                        except Exception as e:
                            pass
                    
                    # Р¤РёРЅР°Р»СЊРЅР°СЏ РїСЂРѕРІРµСЂРєР°: РµСЃР»Рё РІСЃРµ РµС‰Рµ РµСЃС‚СЊ РЅРµРІР°Р»РёРґРЅС‹Рµ, РїСЂРѕР±СѓРµРј infer_datetime_format
                    if parsed.isna().any():
                        remaining_invalid = df.loc[parsed.isna(), time_col]
                        try:
                            parsed_infer = pd.to_datetime(remaining_invalid, infer_datetime_format=True, errors='coerce')
                            success_mask = parsed_infer.notna()
                            if success_mask.any():
                                remaining_indices = df.index[parsed.isna()][success_mask]
                                parsed.loc[remaining_indices] = parsed_infer[success_mask]
                                print(f"  Р’РѕСЃСЃС‚Р°РЅРѕРІР»РµРЅРѕ {success_mask.sum()} Р·Р°РїРёСЃРµР№ СЃ Р°РІС‚РѕРјР°С‚РёС‡РµСЃРєРёРј РѕРїСЂРµРґРµР»РµРЅРёРµРј С„РѕСЂРјР°С‚Р°")
                        except:
                            pass
                            
            except Exception as e:
                print(f"РћС€РёР±РєР° РїСЂРё РїР°СЂСЃРёРЅРіРµ РІСЂРµРјРµРЅРё: {e}")
                parsed = pd.Series([pd.NaT] * len(df))

            # 2) Р•СЃР»Рё РІСЃС‘ NaT, РїС‹С‚Р°РµРјСЃСЏ СЂР°СЃРїРѕР·РЅР°С‚СЊ С‡РёСЃР»Р° (Unix sec/ms РёР»Рё Excel serial)
            if parsed.isna().all():
                numeric = pd.to_numeric(df[time_col], errors='coerce')
                if numeric.notna().any():
                    if numeric.median() > 1e12:
                        # Р’РµСЂРѕСЏС‚РЅРѕ РјРёР»Р»РёСЃРµРєСѓРЅРґС‹ Unix
                        try:
                            parsed = pd.to_datetime(numeric, unit='ms', errors='coerce')
                        except Exception:
                            pass
                    elif numeric.median() > 1e9:
                        # Р’РµСЂРѕСЏС‚РЅРѕ СЃРµРєСѓРЅРґС‹ Unix
                        try:
                            parsed = pd.to_datetime(numeric, unit='s', errors='coerce')
                        except Exception:
                            pass
                    elif 20000 < numeric.median() < 60000:
                        # Р’РµСЂРѕСЏС‚РЅРѕ Excel serial days
                        try:
                            parsed = pd.to_datetime(numeric, unit='D', origin='1899-12-30', errors='coerce')
                        except Exception:
                            pass

            # 3) Р•СЃР»Рё СѓРґР°Р»РѕСЃСЊ РїРѕР»СѓС‡РёС‚СЊ РґР°С‚С‹, РёСЃРїРѕР»СЊР·СѓРµРј DateAxisItem СЃ РµРґРёРЅС‹Рј С„РѕСЂРјР°С‚РѕРј, РёРЅР°С‡Рµ РёРЅРґРµРєСЃС‹
            if parsed.isna().all():
                time_data = None
                timestamps = np.arange(len(df))
                plot = self.plot_widget.addPlot(row=i, col=0)  # РѕР±С‹С‡РЅР°СЏ С‡РёСЃР»РѕРІР°СЏ РѕСЃСЊ
                # РЎРѕР·РґР°РµРј РєРѕРїРёСЋ DataFrame РґР»СЏ СЃРѕСЂС‚РёСЂРѕРІРєРё (РїРѕ РёРЅРґРµРєСЃСѓ)
                df_sorted = df.copy()
            else:
                time_data = parsed
                # РЎРћР РўРР РћР’РљРђ Р”РђРќРќР«РҐ РџРћ Р’Р Р•РњР•РќР - РєСЂРёС‚РёС‡РЅРѕ РґР»СЏ РєРѕСЂСЂРµРєС‚РЅРѕРіРѕ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ РіСЂР°С„РёРєР°
                # РЎРѕР·РґР°РµРј РІСЂРµРјРµРЅРЅСѓСЋ РєРѕР»РѕРЅРєСѓ РґР»СЏ СЃРѕСЂС‚РёСЂРѕРІРєРё
                df_sorted = df.copy()
                df_sorted['_temp_time'] = time_data
                
                # РџСЂРѕРІРµСЂСЏРµРј, СЃРєРѕР»СЊРєРѕ РґР°РЅРЅС‹С… Р±СѓРґРµС‚ РїРѕС‚РµСЂСЏРЅРѕ РїСЂРё С„РёР»СЊС‚СЂР°С†РёРё
                valid_time_count = df_sorted['_temp_time'].notna().sum()
                total_count = len(df_sorted)
                if valid_time_count < total_count:
                    print(f"РџСЂРµРґСѓРїСЂРµР¶РґРµРЅРёРµ: {total_count - valid_time_count} Р·Р°РїРёСЃРµР№ СЃ РЅРµРІР°Р»РёРґРЅС‹Рј РІСЂРµРјРµРЅРµРј Р±СѓРґСѓС‚ РёСЃРєР»СЋС‡РµРЅС‹")
                
                # РЈРґР°Р»СЏРµРј СЃС‚СЂРѕРєРё СЃ РЅРµРІР°Р»РёРґРЅС‹Рј РІСЂРµРјРµРЅРµРј РїРµСЂРµРґ СЃРѕСЂС‚РёСЂРѕРІРєРѕР№
                # Р’РђР–РќРћ: СЃРѕС…СЂР°РЅСЏРµРј РІСЃРµ РґР°РЅРЅС‹Рµ, РґР°Р¶Рµ РµСЃР»Рё РІСЂРµРјСЏ РЅРµ СЂР°СЃРїР°СЂСЃРёР»РѕСЃСЊ
                df_sorted = df_sorted[df_sorted['_temp_time'].notna()].copy()
                
                # РџСЂРѕРІРµСЂСЏРµРј, С‡С‚Рѕ РѕСЃС‚Р°Р»РёСЃСЊ РґР°РЅРЅС‹Рµ
                if len(df_sorted) == 0:
                    print(f"РћРЁРР‘РљРђ: Р’СЃРµ Р·Р°РїРёСЃРё РёРјРµСЋС‚ РЅРµРІР°Р»РёРґРЅРѕРµ РІСЂРµРјСЏ!")
                    continue
                
                # РЎРѕСЂС‚РёСЂСѓРµРј РїРѕ РІСЂРµРјРµРЅРё
                df_sorted = df_sorted.sort_values('_temp_time').reset_index(drop=True)
                # РћР±РЅРѕРІР»СЏРµРј time_data РїРѕСЃР»Рµ СЃРѕСЂС‚РёСЂРѕРІРєРё
                time_data = df_sorted['_temp_time']
                
                # РћС‚Р»Р°РґРѕС‡РЅР°СЏ РёРЅС„РѕСЂРјР°С†РёСЏ Рѕ РґРёР°РїР°Р·РѕРЅРµ РґР°С‚
                if len(time_data) > 0:
                    min_date = time_data.min()
                    max_date = time_data.max()
                    print(f"Р”РёР°РїР°Р·РѕРЅ РґР°С‚ РґР»СЏ {gas_type}: {min_date} - {max_date} ({len(time_data)} Р·Р°РїРёСЃРµР№)")
                
                try:
                    timestamps = time_data.astype('int64') / 1e9
                except Exception:
                    timestamps = time_data.view('int64') / 1e9

                class FixedDateAxis(DateAxisItem):
                    def tickStrings(self, values, scale, spacing):  # noqa: N802
                        from datetime import datetime as _dt
                        # Р•РґРёРЅС‹Р№ С„РѕСЂРјР°С‚ РґР»СЏ РІСЃРµС… РіСЂР°С„РёРєРѕРІ
                        return [_dt.utcfromtimestamp(v).strftime('%d.%m.%Y %H:%M:%S') for v in values]

                axis = FixedDateAxis(orientation='bottom')
                plot = self.plot_widget.addPlot(row=i, col=0, axisItems={'bottom': axis})
            
            plot.setLabel('left', f'{gas_type} РєРѕРЅС†РµРЅС‚СЂР°С†РёСЏ', units='РјРі/РјВі')
            plot.setLabel('bottom', 'Р”Р°С‚Р° Рё РІСЂРµРјСЏ')
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.addLegend()
            
            # РџРѕСЃС‚СЂРѕРµРЅРёРµ Р»РёРЅРёР№ РґР»СЏ РєР°Р¶РґРѕР№ РєРѕР»РѕРЅРєРё РґР°РЅРЅС‹С…
            colors = ['b', 'r', 'g', 'm', 'c', 'y']
            for j, col in enumerate(data_cols):
                try:
                    # РџРѕР»СѓС‡Р°РµРј РёСЃС…РѕРґРЅС‹Рµ Р·РЅР°С‡РµРЅРёСЏ РёР· РѕС‚СЃРѕСЂС‚РёСЂРѕРІР°РЅРЅРѕРіРѕ DataFrame
                    original_values = df_sorted[col]

                    print(f"\n--- РћР‘Р РђР‘РћРўРљРђ РљРћР›РћРќРљР {col} ---")
                    print(f"РўРёРї РґР°РЅРЅС‹С…: {original_values.dtype}")
                    print(f"Р’СЃРµРіРѕ Р·РЅР°С‡РµРЅРёР№: {len(original_values)}")

                    # РџРѕРєР°Р·С‹РІР°РµРј РїРµСЂРІС‹Рµ Р·РЅР°С‡РµРЅРёСЏ РґР»СЏ РґРёР°РіРЅРѕСЃС‚РёРєРё
                    print("РџРµСЂРІС‹Рµ 5 РёСЃС…РѕРґРЅС‹С… Р·РЅР°С‡РµРЅРёР№:")
                    for i in range(min(5, len(original_values))):
                        val = original_values.iloc[i]
                        print(f"  [{i}] '{val}' (С‚РёРї: {type(val).__name__})")

                    # РРЎРџР РђР’Р›Р•РќРР•: РЎСЂР°Р·Сѓ РїСЂРёРјРµРЅСЏРµРј РїСЂР°РІРёР»СЊРЅРѕРµ РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёРµ СЃ РїРѕРґРґРµСЂР¶РєРѕР№ Р·Р°РїСЏС‚С‹С…
                    print(f"\nрџ”§ РџСЂРёРјРµРЅСЏРµРј СЂСѓС‡РЅРѕРµ РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёРµ РґР»СЏ С‚РѕС‡РЅРѕСЃС‚Рё...")
                    numeric_values = self.manual_numeric_conversion(original_values, col)
                    
                    # Р”РѕРїРѕР»РЅРёС‚РµР»СЊРЅР°СЏ РґРёР°РіРЅРѕСЃС‚РёРєР° СЂРµР·СѓР»СЊС‚Р°С‚Р°
                    valid_count = pd.notna(numeric_values).sum()
                    zero_count = (numeric_values == 0).sum()
                    print(f"Р РµР·СѓР»СЊС‚Р°С‚ РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёСЏ: {valid_count} РІР°Р»РёРґРЅС‹С…, {zero_count} РЅСѓР»РµР№")
                    
                    # РџСЂРѕРІРµСЂСЏРµРј, РµСЃС‚СЊ Р»Рё РїСЂРѕР±Р»РµРјРЅС‹Рµ РЅСѓР»Рё
                    if zero_count > 0:
                        print("РђРЅР°Р»РёР· РЅСѓР»РµРІС‹С… Р·РЅР°С‡РµРЅРёР№:")
                        zero_indices = np.where(numeric_values == 0)[0][:3]
                        for zi in zero_indices:
                            if zi < len(original_values):
                                orig_val = original_values.iloc[zi]
                                print(f"  РСЃС…РѕРґРЅРѕРµ '{orig_val}' -> 0 (РєРѕСЂСЂРµРєС‚РЅРѕ: {orig_val == 0 or orig_val == '0'})")

                    # РЎРѕР·РґР°РµРј РјР°СЃРєСѓ РџРћРЎР›Р• РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёСЏ
                    can_plot_mask = pd.notna(numeric_values) & np.isfinite(numeric_values)

                    # РџСЂРѕРІРµСЂСЏРµРј РґР»РёРЅСѓ РґР°РЅРЅС‹С…
                    if len(timestamps) != len(numeric_values):
                        print(f"[WARNING] РќРµСЃРѕРѕС‚РІРµС‚СЃС‚РІРёРµ РґР»РёРЅС‹: timestamps={len(timestamps)}, values={len(numeric_values)}")
                        min_len = min(len(timestamps), len(numeric_values))
                        timestamps_aligned = timestamps[:min_len]
                        numeric_aligned = numeric_values[:min_len]
                        can_plot_aligned = can_plot_mask[:min_len]
                    else:
                        timestamps_aligned = timestamps
                        numeric_aligned = numeric_values
                        can_plot_aligned = can_plot_mask

                    # РџСЂРёРјРµРЅСЏРµРј РјР°СЃРєСѓ РґР»СЏ РїРѕР»СѓС‡РµРЅРёСЏ РІР°Р»РёРґРЅС‹С… РґР°РЅРЅС‹С…
                    if isinstance(timestamps_aligned, pd.Series):
                        valid_timestamps = timestamps_aligned[can_plot_aligned].values
                    else:
                        valid_timestamps = timestamps_aligned[can_plot_aligned]

                    valid_values = numeric_aligned[can_plot_aligned]

                    # РЎС‚Р°С‚РёСЃС‚РёРєР°
                    print(f"Р’Р°Р»РёРґРЅС‹С… Р·РЅР°С‡РµРЅРёР№ РґР»СЏ РіСЂР°С„РёРєР°: {len(valid_values)}")
                    if len(valid_values) > 0:
                        zero_count = (valid_values == 0).sum()
                        non_zero_count = (valid_values != 0).sum()
                        min_val = np.nanmin(valid_values)
                        max_val = np.nanmax(valid_values)
                        print(f"  РќСѓР»РµР№: {zero_count}, РќРµРЅСѓР»РµРІС‹С…: {non_zero_count}")
                        print(f"  Р”РёР°РїР°Р·РѕРЅ: {min_val:.4f} - {max_val:.4f}")

                        # РџРѕСЃС‚СЂРѕРµРЅРёРµ РіСЂР°С„РёРєР° СЃРѕ Р’РЎР•РњР РІР°Р»РёРґРЅС‹РјРё РґР°РЅРЅС‹РјРё
                        color = colors[j % len(colors)]
                        plot.plot(np.array(valid_timestamps), np.array(valid_values),
                                pen=pg.mkPen(color, width=2), name=col)
                        print(f"  [OK] Р“СЂР°С„РёРє РїРѕСЃС‚СЂРѕРµРЅ СЃ {len(valid_values)} С‚РѕС‡РєР°РјРё")
                    else:
                        print(f"  [WARNING] РќРµС‚ РґР°РЅРЅС‹С… РґР»СЏ РїРѕСЃС‚СЂРѕРµРЅРёСЏ РіСЂР°С„РёРєР°")

                except Exception as e:
                    print(f"РћС€РёР±РєР° РїСЂРё РїРѕСЃС‚СЂРѕРµРЅРёРё {col}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # РЈРґР°Р»СЏРµРј РІСЂРµРјРµРЅРЅСѓСЋ РєРѕР»РѕРЅРєСѓ РёР· РѕС‚СЃРѕСЂС‚РёСЂРѕРІР°РЅРЅРѕРіРѕ DataFrame (РµСЃР»Рё РѕРЅР° Р±С‹Р»Р° СЃРѕР·РґР°РЅР°)
            if '_temp_time' in df_sorted.columns:
                df_sorted = df_sorted.drop(columns=['_temp_time'])
            
            # Р›РёРЅРёРё РїРµСЂРµРєСЂРµСЃС‚РёСЏ
            vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('k', width=1, style=Qt.DashLine))
            hLine = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('k', width=1, style=Qt.DashLine))
            plot.addItem(vLine, ignoreBounds=True)
            plot.addItem(hLine, ignoreBounds=True)
            
            self.crosshair_lines.append((vLine, hLine))
            self.plots.append({
                'plot': plot,
                'gas_type': gas_type,
                'timestamps': timestamps,
                'time_data': time_data,
                'time_col': time_col,  # РЎРѕС…СЂР°РЅСЏРµРј РЅР°Р·РІР°РЅРёРµ РєРѕР»РѕРЅРєРё РІСЂРµРјРµРЅРё
                'data_cols': data_cols,
                'df': df_sorted  # РСЃРїРѕР»СЊР·СѓРµРј РѕС‚СЃРѕСЂС‚РёСЂРѕРІР°РЅРЅС‹Р№ DataFrame
            })
            
            # РџРѕРґРєР»СЋС‡РµРЅРёРµ РѕР±СЂР°Р±РѕС‚С‡РёРєР° РґРІРёР¶РµРЅРёСЏ РјС‹С€Рё
            plot.scene().sigMouseMoved.connect(self.on_mouse_moved)
        
        # РЎРёРЅС…СЂРѕРЅРёР·Р°С†РёСЏ РѕСЃРµР№ X РІСЃРµС… РіСЂР°С„РёРєРѕРІ
        if len(self.plots) > 1:
            # РЎРІСЏР·С‹РІР°РµРј РІСЃРµ РіСЂР°С„РёРєРё РїРѕ РѕСЃРё X СЃ РїРµСЂРІС‹Рј РіСЂР°С„РёРєРѕРј
            first_plot = self.plots[0]['plot']
            for i in range(1, len(self.plots)):
                self.plots[i]['plot'].setXLink(first_plot)
        
        self.info_label.setText('Р“СЂР°С„РёРєРё РїРѕСЃС‚СЂРѕРµРЅС‹. РќР°РІРµРґРёС‚Рµ РєСѓСЂСЃРѕСЂ РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ Р·РЅР°С‡РµРЅРёР№.')
        
        # РћР±РЅРѕРІР»СЏРµРј С‚Р°Р±Р»РёС†Сѓ РґР°РЅРЅС‹С…, РµСЃР»Рё С„Р°Р№Р» СѓР¶Рµ РІС‹Р±СЂР°РЅ
        current_file = self.file_selector.currentText()
        if current_file != 'Р’С‹Р±РµСЂРёС‚Рµ С„Р°Р№Р»...' and current_file in self.data_files:
            self.populate_data_table(current_file)
    
    def manual_numeric_conversion(self, series, column_name=""):
        """
        Р СѓС‡РЅРѕРµ РїСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёРµ Р·РЅР°С‡РµРЅРёР№ РІ С‡РёСЃР»Р° Р±РµР· РёСЃРїРѕР»СЊР·РѕРІР°РЅРёСЏ pd.to_numeric
        РЎРѕС…СЂР°РЅСЏРµС‚ С‚РѕС‡РЅС‹Рµ Р·РЅР°С‡РµРЅРёСЏ РёР· С„Р°Р№Р»Р°
        """
        result = []
        problems = []
        
        for i, val in enumerate(series):
            try:
                if pd.isna(val) or val == '' or val == ' ':
                    result.append(np.nan)
                elif isinstance(val, (int, float)):
                    # РЈР¶Рµ С‡РёСЃР»Рѕ
                    result.append(float(val))
                elif isinstance(val, str):
                    # РЎС‚СЂРѕРєР° - РїСЂРѕР±СѓРµРј РїСЂРµРѕР±СЂР°Р·РѕРІР°С‚СЊ
                    cleaned = val.strip()
                    if cleaned == '':
                        result.append(np.nan)
                    else:
                        # Р—Р°РјРµРЅСЏРµРј Р·Р°РїСЏС‚С‹Рµ РЅР° С‚РѕС‡РєРё (СЂСѓСЃСЃРєРёР№ С„РѕСЂРјР°С‚)
                        cleaned = cleaned.replace(',', '.')
                        try:
                            num_val = float(cleaned)
                            result.append(num_val)
                        except ValueError:
                            problems.append((i, val))
                            result.append(np.nan)
                else:
                    # Р”СЂСѓРіРѕР№ С‚РёРї - РїСЂРѕР±СѓРµРј РїСЂРµРѕР±СЂР°Р·РѕРІР°С‚СЊ С‡РµСЂРµР· str
                    try:
                        str_val = str(val).strip().replace(',', '.')
                        num_val = float(str_val)
                        result.append(num_val)
                    except (ValueError, TypeError):
                        problems.append((i, val))
                        result.append(np.nan)
            except Exception as e:
                problems.append((i, val, str(e)))
                result.append(np.nan)
        
        if problems:
            print(f"  {column_name}: {len(problems)} Р·РЅР°С‡РµРЅРёР№ РЅРµ СѓРґР°Р»РѕСЃСЊ РїСЂРµРѕР±СЂР°Р·РѕРІР°С‚СЊ:")
            for item in problems[:3]:
                if len(item) == 2:
                    idx, val = item
                    print(f"    [{idx}] '{val}' (С‚РёРї: {type(val).__name__})")
                else:
                    idx, val, error = item
                    print(f"    [{idx}] '{val}' -> РћС€РёР±РєР°: {error}")
        
        return np.array(result)

    def identify_columns(self, df):
        """РћРїСЂРµРґРµР»РµРЅРёРµ РєРѕР»РѕРЅРѕРє СЃ РІСЂРµРјРµРЅРµРј Рё РґР°РЅРЅС‹РјРё"""
        time_col = None
        data_cols = []
        
        # РЎРїРёСЃРѕРє РєРѕР»РѕРЅРѕРє, РєРѕС‚РѕСЂС‹Рµ РЅСѓР¶РЅРѕ РёСЃРєР»СЋС‡РёС‚СЊ РёР· РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ
        exclude_keywords = ['tagname', 'tag_name', 'С‚РµРі', 'РЅР°Р·РІР°РЅРёРµ']
        
        # РџРѕРёСЃРє РєРѕР»РѕРЅРєРё РІСЂРµРјРµРЅРё
        time_keywords = ['РІСЂРµРјСЏ', 'time', 'РґР°С‚Р°', 'date', 'timestamp', 'datetime']
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in time_keywords):
                time_col = col
                break
        
        # Р•СЃР»Рё РЅРµ РЅР°Р№РґРµРЅР° РєРѕР»РѕРЅРєР° РІСЂРµРјРµРЅРё, Р±РµСЂРµРј РїРµСЂРІСѓСЋ
        if time_col is None and len(df.columns) > 0:
            time_col = df.columns[0]
        
        # РћСЃС‚Р°Р»СЊРЅС‹Рµ С‡РёСЃР»РѕРІС‹Рµ РєРѕР»РѕРЅРєРё СЃС‡РёС‚Р°РµРј РґР°РЅРЅС‹РјРё (РёСЃРєР»СЋС‡Р°СЏ TagName Рё РїРѕРґРѕР±РЅС‹Рµ)
        for col in df.columns:
            col_lower = str(col).lower()
            
            # РџСЂРѕРїСѓСЃРєР°РµРј РєРѕР»РѕРЅРєСѓ РІСЂРµРјРµРЅРё
            if col == time_col:
                continue
            
            # РџСЂРѕРїСѓСЃРєР°РµРј РєРѕР»РѕРЅРєРё РёР· СЃРїРёСЃРєР° РёСЃРєР»СЋС‡РµРЅРёР№
            if any(keyword in col_lower for keyword in exclude_keywords):
                continue
            
            # РџСЂРѕРІРµСЂСЏРµРј, СЏРІР»СЏРµС‚СЃСЏ Р»Рё РєРѕР»РѕРЅРєР° С‡РёСЃР»РѕРІРѕР№
            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                # Р•СЃР»Рё РµСЃС‚СЊ С…РѕС‚СЏ Р±С‹ РѕРґРЅРѕ С‡РёСЃР»РѕРІРѕРµ Р·РЅР°С‡РµРЅРёРµ, РґРѕР±Р°РІР»СЏРµРј РєРѕР»РѕРЅРєСѓ
                if numeric_data.notna().any():
                    data_cols.append(col)
            except:
                pass
        
        return time_col, data_cols
    
    def on_mouse_moved(self, pos):
        """РћР±СЂР°Р±РѕС‚С‡РёРє РґРІРёР¶РµРЅРёСЏ РјС‹С€Рё РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ РїРµСЂРµРєСЂРµСЃС‚РёСЏ Рё Р·РЅР°С‡РµРЅРёР№"""
        info_text = []
        
        # РќР°С…РѕРґРёРј РіСЂР°С„РёРє, РЅР°Рґ РєРѕС‚РѕСЂС‹Рј РЅР°С…РѕРґРёС‚СЃСЏ РєСѓСЂСЃРѕСЂ
        active_plot_idx = None
        active_x = None
        
        for i, plot_data in enumerate(self.plots):
            plot = plot_data['plot']
            
            # РџСЂРѕРІРµСЂСЏРµРј, РЅР°С…РѕРґРёС‚СЃСЏ Р»Рё РєСѓСЂСЃРѕСЂ РІ РѕР±Р»Р°СЃС‚Рё РіСЂР°С„РёРєР°
            if plot.sceneBoundingRect().contains(pos):
                mouse_point = plot.vb.mapSceneToView(pos)
                active_x = mouse_point.x()
                active_plot_idx = i
                break
        
        # Р•СЃР»Рё РєСѓСЂСЃРѕСЂ РЅР°Рґ РєР°РєРёРј-С‚Рѕ РіСЂР°С„РёРєРѕРј, РѕР±РЅРѕРІР»СЏРµРј РІСЃРµ РіСЂР°С„РёРєРё
        if active_plot_idx is not None:
            for i, plot_data in enumerate(self.plots):
                plot = plot_data['plot']
                
                # РћР±РЅРѕРІР»РµРЅРёРµ Р»РёРЅРёР№ РїРµСЂРµРєСЂРµСЃС‚РёСЏ РґР»СЏ РІСЃРµС… РіСЂР°С„РёРєРѕРІ СЃ РѕРґРёРЅР°РєРѕРІС‹Рј X
                vLine, hLine = self.crosshair_lines[i]
                vLine.setPos(active_x)
                
                # Y Р»РёРЅРёСЋ РѕР±РЅРѕРІР»СЏРµРј С‚РѕР»СЊРєРѕ РґР»СЏ Р°РєС‚РёРІРЅРѕРіРѕ РіСЂР°С„РёРєР°
                if i == active_plot_idx:
                    mouse_point = plot.vb.mapSceneToView(pos)
                    y = mouse_point.y()
                    hLine.setPos(y)
                
                # РџРѕРёСЃРє Р±Р»РёР¶Р°Р№С€РµР№ С‚РѕС‡РєРё РґР°РЅРЅС‹С…
                timestamps = plot_data['timestamps']
                idx = np.argmin(np.abs(timestamps - active_x))
                
                if idx < len(plot_data['df']):
                    # РџРѕР»СѓС‡РµРЅРёРµ РґР°РЅРЅС‹С… РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ
                    gas_type = plot_data['gas_type']
                    
                    # Р’СЂРµРјСЏ (РїРѕРєР°Р·С‹РІР°РµРј С‚РѕР»СЊРєРѕ РѕРґРёРЅ СЂР°Р·)
                    if i == 0 or len(info_text) == 0:
                        if plot_data['time_data'] is not None:
                            try:
                                time_str = plot_data['time_data'].iloc[idx].strftime('%d.%m.%Y %H:%M:%S')
                            except:
                                time_str = str(plot_data['time_data'].iloc[idx])
                        else:
                            # РџС‹С‚Р°РµРјСЃСЏ РїРѕР»СѓС‡РёС‚СЊ РІСЂРµРјСЏ РёР· РёСЃС…РѕРґРЅРѕР№ РєРѕР»РѕРЅРєРё
                            time_col = plot_data.get('time_col')
                            if time_col and time_col in plot_data['df'].columns:
                                try:
                                    raw_time = plot_data['df'][time_col].iloc[idx]
                                    # РџС‹С‚Р°РµРјСЃСЏ РїСЂРµРѕР±СЂР°Р·РѕРІР°С‚СЊ РІ РґР°С‚Сѓ
                                    time_val = pd.to_datetime(raw_time)
                                    time_str = time_val.strftime('%d.%m.%Y %H:%M:%S')
                                except:
                                    # Р•СЃР»Рё РЅРµ СѓРґР°Р»РѕСЃСЊ РїСЂРµРѕР±СЂР°Р·РѕРІР°С‚СЊ, РїРѕРєР°Р·С‹РІР°РµРј РєР°Рє РµСЃС‚СЊ
                                    time_str = str(raw_time)
                            else:
                                time_str = f"Р—Р°РїРёСЃСЊ {idx}"
                        
                        info_text.append(f"<b>рџ“… Р”Р°С‚Р°:</b> {time_str}")
                        info_text.append("")  # РџСѓСЃС‚Р°СЏ СЃС‚СЂРѕРєР° РґР»СЏ СЂР°Р·РґРµР»РµРЅРёСЏ
                    
                    info_text.append(f"<b style='color: #2c3e50; font-size: 13px;'>{gas_type}</b>")
                    
                    # РџРѕРёСЃРє СЌС‚Р°Р»РѕРЅРЅРѕРіРѕ Р·РЅР°С‡РµРЅРёСЏ (Ametek)
                    reference_value = None
                    reference_col = None
                    for col in plot_data['data_cols']:
                        col_lower = str(col).lower()
                        if 'ametek' in col_lower or 'Р°Рјetek' in col_lower:
                            try:
                                raw_ref_value = plot_data['df'][col].iloc[idx]
                                reference_value = pd.to_numeric(raw_ref_value, errors='coerce')
                                if pd.notna(reference_value):
                                    reference_col = col
                                    break
                            except:
                                pass
                    
                    # Р—РЅР°С‡РµРЅРёСЏ РїР°СЂР°РјРµС‚СЂРѕРІ СЃ РїСЂРѕС†РµРЅС‚РЅРѕР№ СЂР°Р·РЅРёС†РµР№
                    for col in plot_data['data_cols']:
                        try:
                            # РРЎРџР РђР’Р›Р•РќРР•: РџРѕРєР°Р·С‹РІР°РµРј РўРћР§РќРћ С‚Рѕ Р·РЅР°С‡РµРЅРёРµ, С‡С‚Рѕ РІ С„Р°Р№Р»Рµ
                            raw_value = plot_data['df'][col].iloc[idx]
                            
                            # РџСЂРѕРІРµСЂСЏРµРј, СЏРІР»СЏРµС‚СЃСЏ Р»Рё Р·РЅР°С‡РµРЅРёРµ С‡РёСЃР»РѕРј РґР»СЏ СЂР°СЃС‡РµС‚РѕРІ
                            numeric_value = pd.to_numeric(raw_value, errors='coerce')
                            
                            if pd.notna(numeric_value):
                                # РџРѕРєР°Р·С‹РІР°РµРј РёСЃС…РѕРґРЅРѕРµ Р·РЅР°С‡РµРЅРёРµ (РєР°Рє РІ С„Р°Р№Р»Рµ), РЅРѕ РёСЃРїРѕР»СЊР·СѓРµРј С‡РёСЃР»РѕРІРѕРµ РґР»СЏ СЂР°СЃС‡РµС‚РѕРІ
                                display_value = raw_value if not pd.isna(raw_value) else numeric_value
                                info_text.append(f"  <span style='color: #34495e;'>{col}:</span> <b style='color: #27ae60;'>{display_value}</b>")
                                
                                # Р Р°СЃС‡РµС‚ РїСЂРѕС†РµРЅС‚РЅРѕР№ СЂР°Р·РЅРёС†С‹ РѕС‚РЅРѕСЃРёС‚РµР»СЊРЅРѕ Ametek
                                if reference_value is not None and pd.notna(reference_value) and reference_col != col and reference_value != 0:
                                    try:
                                        diff_percent = ((numeric_value - reference_value) / reference_value) * 100
                                        # Р¦РІРµС‚ РІ Р·Р°РІРёСЃРёРјРѕСЃС‚Рё РѕС‚ Р·РЅР°РєР° СЂР°Р·РЅРёС†С‹
                                        color = '#e74c3c' if abs(diff_percent) > 5 else '#95a5a6'
                                        sign = '+' if diff_percent > 0 else ''
                                        info_text.append(f"    <span style='color: {color}; font-size: 11px;'>О” РѕС‚ СЌС‚Р°Р»РѕРЅР°: {sign}{diff_percent:.2f}%</span>")
                                    except Exception as e:
                                        print(f"РћС€РёР±РєР° СЂР°СЃС‡РµС‚Р° СЂР°Р·РЅРѕСЃС‚Рё РґР»СЏ {col}: {e}")
                            else:
                                # РџРѕРєР°Р·С‹РІР°РµРј РёСЃС…РѕРґРЅРѕРµ Р·РЅР°С‡РµРЅРёРµ РєР°Рє РµСЃС‚СЊ, РµСЃР»Рё СЌС‚Рѕ РЅРµ С‡РёСЃР»Рѕ
                                info_text.append(f"  <span style='color: #34495e;'>{col}:</span> <span style='color: #95a5a6;'>{raw_value}</span>")
                        except Exception as e:
                            print(f"РћС€РёР±РєР° РѕР±СЂР°Р±РѕС‚РєРё РєРѕР»РѕРЅРєРё {col} РІ РїРµСЂРµРєСЂРµСЃС‚РёРё: {e}")
                    
                    # Р”РѕР±Р°РІР»СЏРµРј РїСѓСЃС‚СѓСЋ СЃС‚СЂРѕРєСѓ РјРµР¶РґСѓ РіСЂР°С„РёРєР°РјРё
                    if i < len(self.plots) - 1:
                        info_text.append("")
        
        if info_text:
            self.info_label.setText('<br>'.join(info_text))
    
    def clear_all(self):
        """РћС‡РёСЃС‚РєР° РІСЃРµС… РґР°РЅРЅС‹С… Рё РіСЂР°С„РёРєРѕРІ"""
        self.data_files = {}
        self.plot_widget.clear()
        self.plots = []
        self.crosshair_lines = []
        
        self.label_h2s.setText('Р¤Р°Р№Р» РЅРµ Р·Р°РіСЂСѓР¶РµРЅ')
        self.label_h2s.setStyleSheet('')
        self.label_so2.setText('Р¤Р°Р№Р» РЅРµ Р·Р°РіСЂСѓР¶РµРЅ')
        self.label_so2.setStyleSheet('')
        
        self.btn_plot.setEnabled(False)
        self.btn_debug.setEnabled(False)
        self.info_label.setText('РќР°РІРµРґРёС‚Рµ РєСѓСЂСЃРѕСЂ РЅР° РіСЂР°С„РёРє РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ Р·РЅР°С‡РµРЅРёР№')
        
        # РћС‡РёС‰Р°РµРј С‚Р°Р±Р»РёС†Сѓ Рё СЃРµР»РµРєС‚РѕСЂ
        self.data_table.clear()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)
        self.file_selector.clear()
        self.file_selector.addItem('Р’С‹Р±РµСЂРёС‚Рµ С„Р°Р№Р»...')
        self.selection_info.setText('Р’С‹Р±РµСЂРёС‚Рµ СЃС‚СЂРѕРєСѓ РІ С‚Р°Р±Р»РёС†Рµ РґР»СЏ РІС‹РґРµР»РµРЅРёСЏ РЅР° РіСЂР°С„РёРєРµ')
        
        # РћС‡РёС‰Р°РµРј РІС‹РґРµР»РµРЅРёСЏ РЅР° РіСЂР°С„РёРєРµ
        self.clear_highlights()
    
    def show_data_debugger(self):
        """РџРѕРєР°Р· РІРёР·СѓР°Р»СЊРЅРѕРіРѕ РѕС‚Р»Р°РґС‡РёРєР° РґР°РЅРЅС‹С…"""
        if not self.data_files:
            self.show_error('РЎРЅР°С‡Р°Р»Р° Р·Р°РіСЂСѓР·РёС‚Рµ С„Р°Р№Р»С‹ РґР»СЏ Р°РЅР°Р»РёР·Р°')
            return
        
        # РЎРѕР·РґР°РµРј Рё РїРѕРєР°Р·С‹РІР°РµРј РѕРєРЅРѕ РѕС‚Р»Р°РґС‡РёРєР°
        debugger = DataDebuggerDialog(self)
        debugger.analyze_data(self.data_files)
        debugger.exec_()
    
    def update_file_selector(self):
        """РћР±РЅРѕРІР»РµРЅРёРµ СЃРµР»РµРєС‚РѕСЂР° С„Р°Р№Р»РѕРІ РІ С‚Р°Р±Р»РёС†Рµ"""
        self.file_selector.clear()
        self.file_selector.addItem('Р’С‹Р±РµСЂРёС‚Рµ С„Р°Р№Р»...')
        
        for file_type in self.data_files.keys():
            self.file_selector.addItem(file_type)
    
    def on_file_selector_changed(self, file_type):
        """РћР±СЂР°Р±РѕС‚РєР° РёР·РјРµРЅРµРЅРёСЏ РІС‹Р±СЂР°РЅРЅРѕРіРѕ С„Р°Р№Р»Р°"""
        if file_type == 'Р’С‹Р±РµСЂРёС‚Рµ С„Р°Р№Р»...' or file_type not in self.data_files:
            self.data_table.clear()
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            self.selection_info.setText('Р’С‹Р±РµСЂРёС‚Рµ С„Р°Р№Р» РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ РґР°РЅРЅС‹С…')
            return
        
        self.populate_data_table(file_type)
    
    def populate_data_table(self, file_type):
        """Р—Р°РїРѕР»РЅРµРЅРёРµ С‚Р°Р±Р»РёС†С‹ РґР°РЅРЅС‹РјРё РёР· РІС‹Р±СЂР°РЅРЅРѕРіРѕ С„Р°Р№Р»Р°"""
        try:
            df = self.data_files[file_type]['data']
            
            # РћРїСЂРµРґРµР»СЏРµРј РєРѕР»РѕРЅРєРё РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ
            time_col, data_cols = self.identify_columns(df)
            display_cols = [time_col] + data_cols
            
            # РќР°СЃС‚СЂР°РёРІР°РµРј С‚Р°Р±Р»РёС†Сѓ
            self.data_table.setRowCount(len(df))
            self.data_table.setColumnCount(len(display_cols))
            self.data_table.setHorizontalHeaderLabels(display_cols)
            
            # Р—Р°РїРѕР»РЅСЏРµРј РґР°РЅРЅС‹РјРё
            for row in range(len(df)):
                for col_idx, col_name in enumerate(display_cols):
                    value = df[col_name].iloc[row]
                    
                    # Р¤РѕСЂРјР°С‚РёСЂСѓРµРј Р·РЅР°С‡РµРЅРёРµ РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ
                    if col_name == time_col:
                        # Р’СЂРµРјСЏ - РїРѕРєР°Р·С‹РІР°РµРј РєР°Рє РµСЃС‚СЊ
                        display_value = str(value)
                    else:
                        # Р§РёСЃР»РѕРІС‹Рµ РґР°РЅРЅС‹Рµ - С„РѕСЂРјР°С‚РёСЂСѓРµРј
                        try:
                            numeric_val = pd.to_numeric(value, errors='coerce')
                            if pd.notna(numeric_val):
                                display_value = f"{numeric_val:.4f}"
                            else:
                                display_value = str(value)
                        except:
                            display_value = str(value)
                    
                    item = QTableWidgetItem(display_value)
                    item.setData(Qt.UserRole, row)  # РЎРѕС…СЂР°РЅСЏРµРј РёРЅРґРµРєСЃ СЃС‚СЂРѕРєРё
                    self.data_table.setItem(row, col_idx, item)
            
            # РђРІС‚РѕРјР°С‚РёС‡РµСЃРєРё РїРѕРґРіРѕРЅСЏРµРј С€РёСЂРёРЅСѓ РєРѕР»РѕРЅРѕРє
            self.data_table.resizeColumnsToContents()
            
            self.selection_info.setText(f'РћС‚РѕР±СЂР°Р¶Р°РµС‚СЃСЏ {len(df)} Р·Р°РїРёСЃРµР№ РёР· С„Р°Р№Р»Р° {file_type}')
            
        except Exception as e:
            self.show_error(f'РћС€РёР±РєР° РїСЂРё Р·Р°РїРѕР»РЅРµРЅРёРё С‚Р°Р±Р»РёС†С‹: {str(e)}')
    
    def refresh_data_table(self):
        """РћР±РЅРѕРІР»РµРЅРёРµ С‚Р°Р±Р»РёС†С‹ РґР°РЅРЅС‹С…"""
        current_file = self.file_selector.currentText()
        if current_file != 'Р’С‹Р±РµСЂРёС‚Рµ С„Р°Р№Р»...':
            self.populate_data_table(current_file)
    
    def on_table_selection_changed(self):
        """РћР±СЂР°Р±РѕС‚РєР° РёР·РјРµРЅРµРЅРёСЏ РІС‹Р±РѕСЂР° РІ С‚Р°Р±Р»РёС†Рµ"""
        selected_items = self.data_table.selectedItems()
        if not selected_items:
            self.clear_highlights()
            self.selection_info.setText('Р’С‹Р±РµСЂРёС‚Рµ СЃС‚СЂРѕРєСѓ РІ С‚Р°Р±Р»РёС†Рµ РґР»СЏ РІС‹РґРµР»РµРЅРёСЏ РЅР° РіСЂР°С„РёРєРµ')
            return
        
        # РџРѕР»СѓС‡Р°РµРј РёРЅРґРµРєСЃ РІС‹Р±СЂР°РЅРЅРѕР№ СЃС‚СЂРѕРєРё
        row_index = selected_items[0].data(Qt.UserRole)
        if row_index is None:
            return
        
        # Р’С‹РґРµР»СЏРµРј С‚РѕС‡РєСѓ РЅР° РіСЂР°С„РёРєРµ
        self.highlight_point_on_graph(row_index)
        
        # РћР±РЅРѕРІР»СЏРµРј РёРЅС„РѕСЂРјР°С†РёСЋ
        current_file = self.file_selector.currentText()
        self.selection_info.setText(f'Р’С‹Р±СЂР°РЅР° СЃС‚СЂРѕРєР° {row_index + 1} РёР· С„Р°Р№Р»Р° {current_file}')
    
    def highlight_point_on_graph(self, row_index):
        """Р’С‹РґРµР»РµРЅРёРµ С‚РѕС‡РєРё РЅР° РіСЂР°С„РёРєРµ"""
        try:
            # РћС‡РёС‰Р°РµРј РїСЂРµРґС‹РґСѓС‰РёРµ РІС‹РґРµР»РµРЅРёСЏ
            self.clear_highlights()
            
            current_file = self.file_selector.currentText()
            if current_file not in self.data_files:
                return
            
            # РќР°С…РѕРґРёРј СЃРѕРѕС‚РІРµС‚СЃС‚РІСѓСЋС‰РёР№ РіСЂР°С„РёРє
            plot_data = None
            for plot_info in self.plots:
                if plot_info['gas_type'] == current_file:
                    plot_data = plot_info
                    break
            
            if not plot_data:
                return
            
            # РџРѕР»СѓС‡Р°РµРј РґР°РЅРЅС‹Рµ РґР»СЏ РІС‹РґРµР»РµРЅРёСЏ
            timestamps = plot_data['timestamps']
            df = plot_data['df']
            
            if row_index >= len(timestamps) or row_index >= len(df):
                return
            
            # РљРѕРѕСЂРґРёРЅР°С‚С‹ С‚РѕС‡РєРё РґР»СЏ РІС‹РґРµР»РµРЅРёСЏ
            x_coord = timestamps[row_index]
            
            # Р’С‹РґРµР»СЏРµРј С‚РѕС‡РєСѓ РЅР° РєР°Р¶РґРѕР№ Р»РёРЅРёРё РіСЂР°С„РёРєР°
            plot = plot_data['plot']
            data_cols = plot_data['data_cols']
            
            for col in data_cols:
                try:
                    # РџРѕР»СѓС‡Р°РµРј Р·РЅР°С‡РµРЅРёРµ РґР»СЏ СЌС‚РѕР№ РєРѕР»РѕРЅРєРё
                    value = pd.to_numeric(df[col].iloc[row_index], errors='coerce')
                    if pd.notna(value):
                        # РЎРѕР·РґР°РµРј РјР°СЂРєРµСЂ РІС‹РґРµР»РµРЅРёСЏ
                        highlight_item = pg.ScatterPlotItem(
                            [x_coord], [value], 
                            pen=pg.mkPen('red', width=3),
                            brush=pg.mkBrush('red'),
                            size=10,
                            symbol='o'
                        )
                        plot.addItem(highlight_item)
                        self.highlight_items.append(highlight_item)
                except:
                    continue
                    
        except Exception as e:
            print(f"РћС€РёР±РєР° РїСЂРё РІС‹РґРµР»РµРЅРёРё С‚РѕС‡РєРё: {e}")
    
    def clear_highlights(self):
        """РћС‡РёСЃС‚РєР° РІС‹РґРµР»РµРЅРёР№ РЅР° РіСЂР°С„РёРєРµ"""
        for item in self.highlight_items:
            try:
                # РќР°С…РѕРґРёРј РіСЂР°С„РёРє, СЃРѕРґРµСЂР¶Р°С‰РёР№ СЌС‚РѕС‚ СЌР»РµРјРµРЅС‚, Рё СѓРґР°Р»СЏРµРј РµРіРѕ
                for plot_info in self.plots:
                    plot = plot_info['plot']
                    if item in plot.items:
                        plot.removeItem(item)
            except:
                pass
        self.highlight_items.clear()
    
    def show_error(self, message):
        """РћС‚РѕР±СЂР°Р¶РµРЅРёРµ СЃРѕРѕР±С‰РµРЅРёСЏ РѕР± РѕС€РёР±РєРµ"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(self, 'РћС€РёР±РєР°', message)


def main():
    """Р“Р»Р°РІРЅР°СЏ С„СѓРЅРєС†РёСЏ Р·Р°РїСѓСЃРєР° РїСЂРёР»РѕР¶РµРЅРёСЏ"""
    app = QApplication(sys.argv)
    window = AnalyzerComparisonApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
