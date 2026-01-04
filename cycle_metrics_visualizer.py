"""
Cycle-Level 시각화 모듈
loaded_data의 cycle 데이터를 사이클 번호 vs 다양한 지표로 시각화
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_cycle_metrics(df_cycle, channel_name, figsize=(16, 10)):
    """
    단일 채널의 사이클 레벨 지표 시각화
    
    Parameters:
    -----------
    df_cycle : pd.DataFrame
        사이클 결과 데이터
    channel_name : str
        채널 이름
    figsize : tuple
        Figure 크기
    """
    
    if df_cycle is None or len(df_cycle) == 0:
        print(f"⚠️ {channel_name}: 데이터 없음")
        return None
    
    fig, axes = plt.subplots(3, 2, figsize=figsize)
    fig.suptitle(f'{channel_name} - Cycle Level 분석', fontsize=16, fontweight='bold')
    
    cycle_numbers = df_cycle.index if 'Cycle' not in df_cycle.columns else df_cycle['Cycle']
    
    # 1. Capacity (충전/방전)
    ax1 = axes[0, 0]
    if 'capacity_mAh' in df_cycle.columns:
        ax1.plot(cycle_numbers, df_cycle['capacity_mAh'], 'o-', 
                label='Discharge Capacity', markersize=4)
    if 'charge_capacity_mAh' in df_cycle.columns:
        ax1.plot(cycle_numbers, df_cycle['charge_capacity_mAh'], 's-', 
                label='Charge Capacity', markersize=4, alpha=0.7)
    ax1.set_xlabel('Cycle', fontsize=10)
    ax1.set_ylabel('Capacity (mAh)', fontsize=10)
    ax1.set_title('Capacity vs Cycle', fontsize=11, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 2. Efficiency
    ax2 = axes[0, 1]
    if 'efficiency_%' in df_cycle.columns:
        ax2.plot(cycle_numbers, df_cycle['efficiency_%'], 'o-', 
                color='green', markersize=4)
        ax2.set_xlabel('Cycle', fontsize=10)
        ax2.set_ylabel('Efficiency (%)', fontsize=10)
        ax2.set_title('Efficiency vs Cycle', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(0.5, 0.5, 'Efficiency 데이터 없음', 
                ha='center', va='center', fontsize=12)
    
    # 3. Voltage (평균/최대/최소)
    ax3 = axes[1, 0]
    voltage_plotted = False
    if 'Voltage_V' in df_cycle.columns:
        ax3.plot(cycle_numbers, df_cycle['Voltage_V'], 'o-', 
                label='Voltage', markersize=4)
        voltage_plotted = True
    if 'max_voltage_V' in df_cycle.columns:
        ax3.plot(cycle_numbers, df_cycle['max_voltage_V'], '^-', 
                label='Max Voltage', markersize=3, alpha=0.7)
        voltage_plotted = True
    if 'min_voltage_V' in df_cycle.columns:
        ax3.plot(cycle_numbers, df_cycle['min_voltage_V'], 'v-', 
                label='Min Voltage', markersize=3, alpha=0.7)
        voltage_plotted = True
    
    if voltage_plotted:
        ax3.set_xlabel('Cycle', fontsize=10)
        ax3.set_ylabel('Voltage (V)', fontsize=10)
        ax3.set_title('Voltage vs Cycle', fontsize=11, fontweight='bold')
        ax3.legend(fontsize=9)
        ax3.grid(True, alpha=0.3)
    else:
        ax3.text(0.5, 0.5, 'Voltage 데이터 없음', 
                ha='center', va='center', fontsize=12)
    
    # 4. Energy
    ax4 = axes[1, 1]
    if 'energy_Wh' in df_cycle.columns:
        ax4.plot(cycle_numbers, df_cycle['energy_Wh'], 'o-', 
                color='purple', markersize=4)
        ax4.set_xlabel('Cycle', fontsize=10)
        ax4.set_ylabel('Energy (Wh)', fontsize=10)
        ax4.set_title('Energy vs Cycle', fontsize=11, fontweight='bold')
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'Energy 데이터 없음', 
                ha='center', va='center', fontsize=12)
    
    # 5. Resistance (있는 경우)
    ax5 = axes[2, 0]
    resistance_plotted = False
    if 'resistance_mOhm' in df_cycle.columns:
        ax5.plot(cycle_numbers, df_cycle['resistance_mOhm'], 'o-', 
                color='red', markersize=4)
        resistance_plotted = True
    if 'IR_mOhm' in df_cycle.columns:
        ax5.plot(cycle_numbers, df_cycle['IR_mOhm'], 's-', 
                label='IR', markersize=4, alpha=0.7)
        resistance_plotted = True
    
    if resistance_plotted:
        ax5.set_xlabel('Cycle', fontsize=10)
        ax5.set_ylabel('Resistance (mΩ)', fontsize=10)
        ax5.set_title('Resistance vs Cycle', fontsize=11, fontweight='bold')
        ax5.grid(True, alpha=0.3)
    else:
        ax5.text(0.5, 0.5, 'Resistance 데이터 없음', 
                ha='center', va='center', fontsize=12)
    
    # 6. Temperature (있는 경우)
    ax6 = axes[2, 1]
    if 'temperature_C' in df_cycle.columns or 'PeakTemp[Deg]' in df_cycle.columns:
        temp_col = 'temperature_C' if 'temperature_C' in df_cycle.columns else 'PeakTemp[Deg]'
        ax6.plot(cycle_numbers, df_cycle[temp_col], 'o-', 
                color='orange', markersize=4)
        ax6.set_xlabel('Cycle', fontsize=10)
        ax6.set_ylabel('Temperature (°C)', fontsize=10)
        ax6.set_title('Temperature vs Cycle', fontsize=11, fontweight='bold')
        ax6.grid(True, alpha=0.3)
    else:
        ax6.text(0.5, 0.5, 'Temperature 데이터 없음', 
                ha='center', va='center', fontsize=12)
    
    plt.tight_layout()
    return fig


def plot_all_channels_comparison(loaded_data, metric='capacity_mAh', figsize=(16, 8)):
    """
    모든 채널의 특정 지표 비교
    
    Parameters:
    -----------
    loaded_data : dict
        로드된 데이터 딕셔너리
    metric : str
        비교할 지표 (capacity_mAh, efficiency_%, 등)
    figsize : tuple
        Figure 크기
    """
    
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle(f'전체 채널 비교: {metric}', fontsize=16, fontweight='bold')
    
    channel_count = 0
    
    # PNE cycle 데이터
    if 'pne_cycle' in loaded_data and loaded_data['pne_cycle']:
        for channel_key, df_cycle in loaded_data['pne_cycle'].items():
            if df_cycle is not None and len(df_cycle) > 0 and metric in df_cycle.columns:
                cycle_numbers = df_cycle.index if 'Cycle' not in df_cycle.columns else df_cycle['Cycle']
                ax.plot(cycle_numbers, df_cycle[metric], 'o-', 
                       label=channel_key, markersize=3, alpha=0.7)
                channel_count += 1
    
    # Toyo cycle 데이터
    if 'toyo_cycle' in loaded_data and loaded_data['toyo_cycle']:
        for channel_key, df_cycle in loaded_data['toyo_cycle'].items():
            if df_cycle is not None and len(df_cycle) > 0 and metric in df_cycle.columns:
                cycle_numbers = df_cycle.index if 'Cycle' not in df_cycle.columns else df_cycle['Cycle']
                ax.plot(cycle_numbers, df_cycle[metric], 's-', 
                       label=channel_key, markersize=3, alpha=0.7)
                channel_count += 1
    
    if channel_count > 0:
        ax.set_xlabel('Cycle', fontsize=12)
        ax.set_ylabel(metric, fontsize=12)
        ax.legend(fontsize=9, loc='best')
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, f'{metric} 데이터 없음', 
               ha='center', va='center', fontsize=14)
    
    plt.tight_layout()
    return fig


def plot_capacity_retention(loaded_data, figsize=(16, 8)):
    """
    모든 채널의 용량 보존율 (Capacity Retention) 비교
    
    Parameters:
    -----------
    loaded_data : dict
        로드된 데이터 딕셔너리
    figsize : tuple
        Figure 크기
    """
    
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle('전체 채널 용량 보존율 (Capacity Retention)', fontsize=16, fontweight='bold')
    
    channel_count = 0
    
    # PNE cycle 데이터
    if 'pne_cycle' in loaded_data and loaded_data['pne_cycle']:
        for channel_key, df_cycle in loaded_data['pne_cycle'].items():
            if df_cycle is not None and len(df_cycle) > 0 and 'capacity_mAh' in df_cycle.columns:
                cycle_numbers = df_cycle.index if 'Cycle' not in df_cycle.columns else df_cycle['Cycle']
                initial_capacity = df_cycle['capacity_mAh'].iloc[0]
                retention = (df_cycle['capacity_mAh'] / initial_capacity * 100)
                ax.plot(cycle_numbers, retention, 'o-', 
                       label=f'{channel_key} (초기: {initial_capacity:.1f} mAh)', 
                       markersize=3, alpha=0.7)
                channel_count += 1
    
    # Toyo cycle 데이터
    if 'toyo_cycle' in loaded_data and loaded_data['toyo_cycle']:
        for channel_key, df_cycle in loaded_data['toyo_cycle'].items():
            if df_cycle is not None and len(df_cycle) > 0 and 'capacity_mAh' in df_cycle.columns:
                cycle_numbers = df_cycle.index if 'Cycle' not in df_cycle.columns else df_cycle['Cycle']
                initial_capacity = df_cycle['capacity_mAh'].iloc[0]
                retention = (df_cycle['capacity_mAh'] / initial_capacity * 100)
                ax.plot(cycle_numbers, retention, 's-', 
                       label=f'{channel_key} (초기: {initial_capacity:.1f} mAh)', 
                       markersize=3, alpha=0.7)
                channel_count += 1
    
    if channel_count > 0:
        ax.set_xlabel('Cycle', fontsize=12)
        ax.set_ylabel('Capacity Retention (%)', fontsize=12)
        ax.axhline(y=80, color='r', linestyle='--', alpha=0.5, label='80% EOL')
        ax.legend(fontsize=9, loc='best')
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, 'Capacity 데이터 없음', 
               ha='center', va='center', fontsize=14)
    
    plt.tight_layout()
    return fig
