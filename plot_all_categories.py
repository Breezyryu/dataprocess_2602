"""
카테고리별 모든 사이클 시각화 모듈
각 카테고리에 속한 모든 사이클을 플롯하여 분류 결과를 검증
"""

import matplotlib.pyplot as plt
import numpy as np


def plot_category_cycles(cycle_list, categories, category_name, max_cols=5):
    """
    특정 카테고리의 모든 사이클을 그리드 형태로 시각화
    
    Parameters:
    -----------
    cycle_list : list
        전체 사이클 리스트
    categories : dict
        카테고리별 사이클 인덱스 딕셔너리
    category_name : str
        시각화할 카테고리 이름
    max_cols : int
        한 행당 최대 플롯 개수
    """
    indices = categories[category_name]
    
    if not indices:
        print(f"⚠️ {category_name} 카테고리에 사이클이 없습니다.")
        return
    
    n_cycles = len(indices)
    n_cols = min(max_cols, n_cycles)
    n_rows = (n_cycles + n_cols - 1) // n_cols
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 3*n_rows))
    fig.suptitle(f'{category_name} - 총 {n_cycles}개 사이클', fontsize=16, fontweight='bold')
    
    # axes를 1차원 배열로 변환
    if n_cycles == 1:
        axes = [axes]
    else:
        axes = axes.flatten() if n_rows > 1 or n_cols > 1 else [axes]
    
    for i, idx in enumerate(indices):
        ax1 = axes[i]
        cycle = cycle_list[idx]
        
        # Voltage 플롯 (왼쪽 y축)
        color1 = 'tab:blue'
        ax1.plot(cycle['time_cyc'], cycle['Voltage_V'], color=color1, linewidth=0.5, alpha=0.7)
        ax1.set_title(f'Cycle {idx}', fontsize=10)
        ax1.set_xlabel('Time (s)', fontsize=8)
        ax1.set_ylabel('Voltage (V)', color=color1, fontsize=8)
        ax1.tick_params(axis='y', labelcolor=color1, labelsize=7)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', labelsize=7)
        
        # C-rate 플롯 (오른쪽 y축)
        if 'Crate' in cycle.columns:
            ax2 = ax1.twinx()
            color2 = 'tab:red'
            ax2.plot(cycle['time_cyc'], cycle['Crate'], color=color2, linewidth=0.5, alpha=0.5)
            ax2.set_ylabel('C-rate', color=color2, fontsize=8)
            ax2.tick_params(axis='y', labelcolor=color2, labelsize=7)
        
        # 통계 정보 추가
        v_min = cycle['Voltage_V'].min()
        v_max = cycle['Voltage_V'].max()
        ax1.text(0.02, 0.98, f'V: {v_min:.2f}-{v_max:.2f}V', 
                transform=ax1.transAxes, fontsize=7, 
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    # 사용하지 않는 subplot 숨기기
    for i in range(n_cycles, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    return fig


def plot_all_categories(cycle_list, categories, max_cols=5):
    """
    모든 카테고리의 사이클을 시각화
    
    Parameters:
    -----------
    cycle_list : list
        전체 사이클 리스트
    categories : dict
        카테고리별 사이클 인덱스 딕셔너리
    max_cols : int
        한 행당 최대 플롯 개수
    
    Returns:
    --------
    dict : 카테고리별 Figure 객체 딕셔너리
    """
    figures = {}
    
    category_order = ['RPT', 'SOC_Definition', 'Resistance_Measurement', 'Accelerated_Aging']
    
    for cat_name in category_order:
        if cat_name in categories and categories[cat_name]:
            print(f"\n📊 {cat_name} 시각화 중... ({len(categories[cat_name])}개 사이클)")
            fig = plot_category_cycles(cycle_list, categories, cat_name, max_cols)
            figures[cat_name] = fig
        else:
            print(f"\n⚠️ {cat_name}: 사이클 없음")
    
    return figures


def plot_category_comparison(cycle_list, categories):
    """
    각 카테고리의 대표 사이클을 비교하는 플롯
    
    Parameters:
    -----------
    cycle_list : list
        전체 사이클 리스트
    categories : dict
        카테고리별 사이클 인덱스 딕셔너리
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('카테고리별 대표 사이클 비교', fontsize=16, fontweight='bold')
    
    categories_info = [
        ('RPT', 0, 0, 'blue'),
        ('SOC_Definition', 0, 1, 'green'),
        ('Resistance_Measurement', 1, 0, 'red'),
        ('Accelerated_Aging', 1, 1, 'purple')
    ]
    
    for cat_name, row, col, color in categories_info:
        ax1 = axes[row, col]
        
        if categories[cat_name]:
            # 첫 3개 사이클 플롯 (있는 경우)
            for i, idx in enumerate(categories[cat_name][:3]):
                cycle = cycle_list[idx]
                alpha = 1.0 - i * 0.2
                # Voltage 플롯 (왼쪽 y축)
                ax1.plot(cycle['time_cyc'], cycle['Voltage_V'], 
                       color=color, linewidth=1.0, alpha=alpha,
                       label=f'Cycle {idx}')
            
            ax1.set_title(f'{cat_name} (총 {len(categories[cat_name])}개)', 
                        fontsize=12, fontweight='bold')
            ax1.set_xlabel('Time (s)', fontsize=10)
            ax1.set_ylabel('Voltage (V)', color='tab:blue', fontsize=10)
            ax1.tick_params(axis='y', labelcolor='tab:blue')
            ax1.grid(True, alpha=0.3)
            ax1.legend(fontsize=8, loc='upper left')
            
            # C-rate 플롯 (오른쪽 y축) - 첫 번째 사이클만
            if categories[cat_name]:
                idx = categories[cat_name][0]
                cycle = cycle_list[idx]
                if 'Crate' in cycle.columns:
                    ax2 = ax1.twinx()
                    ax2.plot(cycle['time_cyc'], cycle['Crate'], 
                           color='tab:red', linewidth=0.8, alpha=0.5, linestyle='--')
                    ax2.set_ylabel('C-rate', color='tab:red', fontsize=10)
                    ax2.tick_params(axis='y', labelcolor='tab:red')
        else:
            ax1.text(0.5, 0.5, 'No data', ha='center', va='center', fontsize=14)
            ax1.set_title(f'{cat_name}', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_voltage_current_overlay(cycle_list, categories, category_name, max_cycles=10):
    """
    특정 카테고리의 Voltage와 Current를 함께 표시
    
    Parameters:
    -----------
    cycle_list : list
        전체 사이클 리스트
    categories : dict
        카테고리별 사이클 인덱스 딕셔너리
    category_name : str
        시각화할 카테고리 이름
    max_cycles : int
        최대 표시할 사이클 개수
    """
    indices = categories[category_name][:max_cycles]
    
    if not indices:
        print(f"⚠️ {category_name} 카테고리에 사이클이 없습니다.")
        return
    
    n_cycles = len(indices)
    fig, axes = plt.subplots(n_cycles, 1, figsize=(14, 4*n_cycles))
    fig.suptitle(f'{category_name} - Voltage & Current (최대 {max_cycles}개)', 
                 fontsize=16, fontweight='bold')
    
    if n_cycles == 1:
        axes = [axes]
    
    for i, idx in enumerate(indices):
        ax1 = axes[i]
        cycle = cycle_list[idx]
        
        # Voltage 플롯
        color1 = 'tab:blue'
        ax1.set_xlabel('Time (s)', fontsize=10)
        ax1.set_ylabel('Voltage (V)', color=color1, fontsize=10)
        ax1.plot(cycle['time_cyc'], cycle['Voltage_V'], color=color1, linewidth=1.0)
        ax1.tick_params(axis='y', labelcolor=color1)
        ax1.grid(True, alpha=0.3)
        
        # Current 플롯 (같은 축에)
        ax2 = ax1.twinx()
        color2 = 'tab:red'
        ax2.set_ylabel('Current (mA)', color=color2, fontsize=10)
        ax2.plot(cycle['time_cyc'], cycle['Current_mA'], color=color2, 
                linewidth=0.8, alpha=0.7)
        ax2.tick_params(axis='y', labelcolor=color2)
        
        # 제목
        ax1.set_title(f'Cycle {idx}', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    return fig


def save_all_plots(figures, output_dir='./plots'):
    """
    모든 플롯을 파일로 저장
    
    Parameters:
    -----------
    figures : dict
        카테고리별 Figure 객체 딕셔너리
    output_dir : str
        저장할 디렉토리 경로
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    for cat_name, fig in figures.items():
        filename = f"{output_dir}/{cat_name}_all_cycles.png"
        fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"✅ 저장 완료: {filename}")
