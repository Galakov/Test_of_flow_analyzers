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
        self.setGeometry(100, 100, 1600, 1000)
        
        # Р¦РµРЅС‚СЂР°Р»СЊРЅС‹Р№ РІРёРґР¶РµС‚
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # РџР°РЅРµР»СЊ СѓРїСЂР°РІР»РµРЅРёСЏ
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # РџР°РЅРµР»СЊ РёРЅС„РѕСЂРјР°С†РёРё
        self.info_label = QLabel('РќР°РІРµРґРёС‚Рµ РєСѓСЂСЃРѕСЂ РЅР° РіСЂР°С„РёРє РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ Р·РЅР°С‡РµРЅРёР№')
        self.info_label.setStyleSheet('QLabel { background-color: #f0f0f0; padding: 10px; font-size: 12px; }')
        self.info_label.setMinimumHeight(120)
        self.info_label.setMaximumHeight(180)
        self.info_label.setWordWrap(True)
        main_layout.addWidget(self.info_label)
        
        # РћР±Р»Р°СЃС‚СЊ РіСЂР°С„РёРєРѕРІ
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.plot_widget.setBackground('w')
        main_layout.addWidget(self.plot_widget, stretch=1)
    
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
                
                # РђРєС‚РёРІР°С†РёСЏ РєРЅРѕРїРєРё РїРѕСЃС‚СЂРѕРµРЅРёСЏ РіСЂР°С„РёРєРѕРІ
                if len(self.data_files) > 0:
                    self.btn_plot.setEnabled(True)
                    
            except Exception as e:
                self.show_error(f'РћС€РёР±РєР° РїСЂРё Р·Р°РіСЂСѓР·РєРµ С„Р°Р№Р»Р° {file_type}: {str(e)}')
    
    def plot_data(self):
        """РџРѕСЃС‚СЂРѕРµРЅРёРµ РіСЂР°С„РёРєРѕРІ СЃ РґР°РЅРЅС‹РјРё РёР· Р·Р°РіСЂСѓР¶РµРЅРЅС‹С… С„Р°Р№Р»РѕРІ"""
        # РћС‡РёСЃС‚РєР° РїСЂРµРґС‹РґСѓС‰РёС… РіСЂР°С„РёРєРѕРІ
        self.plot_widget.clear()
        self.plots = []
        
        # РћРїСЂРµРґРµР»РµРЅРёРµ РєРѕР»РёС‡РµСЃС‚РІР° РіСЂР°С„РёРєРѕРІ
        plot_configs = []
        
        if 'H2S' in self.data_files:
            df_h2s = self.data_files['H2S']['data']
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
            # РџСЂРµРѕР±СЂР°Р·РѕРІР°РЅРёРµ РІСЂРµРјРµРЅРё
            try:
                time_data = pd.to_datetime(df[time_col], dayfirst=True, errors='coerce')
                timestamps = time_data.astype('int64') / 1e9
                
                class FixedDateAxis(DateAxisItem):
                    def tickStrings(self, values, scale, spacing):
                        from datetime import datetime as _dt
                        return [_dt.utcfromtimestamp(v).strftime('%d.%m.%Y %H:%M:%S') for v in values]

                axis = FixedDateAxis(orientation='bottom')
                plot = self.plot_widget.addPlot(row=i, col=0, axisItems={'bottom': axis})
            except:
                timestamps = np.arange(len(df))
                plot = self.plot_widget.addPlot(row=i, col=0)
            
            plot.setLabel('left', f'{gas_type} РєРѕРЅС†РµРЅС‚СЂР°С†РёСЏ', units='РјРі/РјВі')
            plot.setLabel('bottom', 'Р”Р°С‚Р° Рё РІСЂРµРјСЏ')
            plot.showGrid(x=True, y=True, alpha=0.3)
            plot.addLegend()
            
            # РџРѕСЃС‚СЂРѕРµРЅРёРµ Р»РёРЅРёР№ РґР»СЏ РєР°Р¶РґРѕР№ РєРѕР»РѕРЅРєРё РґР°РЅРЅС‹С…
            colors = ['b', 'r', 'g', 'm', 'c', 'y']
            for j, col in enumerate(data_cols):
                try:
                    values = pd.to_numeric(df[col], errors='coerce')
                    valid_mask = pd.notna(values) & np.isfinite(values)
                    
                    if valid_mask.any():
                        color = colors[j % len(colors)]
                        plot.plot(timestamps[valid_mask], values[valid_mask],
                                pen=pg.mkPen(color, width=2), name=col)
                except Exception as e:
                    print(f"РћС€РёР±РєР° РїСЂРё РїРѕСЃС‚СЂРѕРµРЅРёРё {col}: {e}")
        
        self.info_label.setText('Р“СЂР°С„РёРєРё РїРѕСЃС‚СЂРѕРµРЅС‹. РќР°РІРµРґРёС‚Рµ РєСѓСЂСЃРѕСЂ РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ Р·РЅР°С‡РµРЅРёР№.')

    def identify_columns(self, df):
        """РћРїСЂРµРґРµР»РµРЅРёРµ РєРѕР»РѕРЅРѕРє СЃ РІСЂРµРјРµРЅРµРј Рё РґР°РЅРЅС‹РјРё"""
        time_col = None
        data_cols = []
        
        # РџРѕРёСЃРє РєРѕР»РѕРЅРєРё РІСЂРµРјРµРЅРё
        time_keywords = ['РІСЂРµРјСЏ', 'time', 'РґР°С‚Р°', 'date', 'timestamp', 'datetime']
        for col in df.columns:
            col_lower = str(col).lower()
            if any(keyword in col_lower for keyword in time_keywords):
                time_col = col
                break
        
        if time_col is None and len(df.columns) > 0:
            time_col = df.columns[0]
        
        # РџРѕРёСЃРє РєРѕР»РѕРЅРѕРє РґР°РЅРЅС‹С…
        exclude_keywords = ['tagname', 'tag_name', 'С‚РµРі', 'РЅР°Р·РІР°РЅРёРµ']
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
    
    def clear_all(self):
        """РћС‡РёСЃС‚РєР° РІСЃРµС… РґР°РЅРЅС‹С… Рё РіСЂР°С„РёРєРѕРІ"""
        self.data_files = {}
        self.plot_widget.clear()
        self.plots = []
        
        self.label_h2s.setText('Р¤Р°Р№Р» РЅРµ Р·Р°РіСЂСѓР¶РµРЅ')
        self.label_h2s.setStyleSheet('')
        self.label_so2.setText('Р¤Р°Р№Р» РЅРµ Р·Р°РіСЂСѓР¶РµРЅ')
        self.label_so2.setStyleSheet('')
        
        self.btn_plot.setEnabled(False)
        self.info_label.setText('РќР°РІРµРґРёС‚Рµ РєСѓСЂСЃРѕСЂ РЅР° РіСЂР°С„РёРє РґР»СЏ РѕС‚РѕР±СЂР°Р¶РµРЅРёСЏ Р·РЅР°С‡РµРЅРёР№')
    
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
