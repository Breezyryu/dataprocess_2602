"""
Cycle List 종합 시각화 모듈
cycle_list에 대한 다양한 시각화 옵션 제공
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
import numpy as np


def plot_all_cycles_overview(cycle_list, max_cycles=None, figsize=(16, 10)):
    """
    모든 사이클의 Voltage 프로파일을 한 그래프에 겹쳐 표시
    
    Parameters:
    -----------
    cycle_list : list of pd.DataFrame
        사이클 리스트
    max_cycles : int, optional
        표시할 최대 사이클 수 (None이면 전체)
    figsize : tuple
        Figure 크기
    """
    
    cycles_to_plot = cycle_list[:max_cycles] if max_cycles else cycle_list
    n_cycles = len(cycles_to_plot)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
    fig.suptitle(f'전체 사이클 오버뷰 (총 {n_cycles}개)', fontsize=16, fontweight='bold')
    
    # Colormap 설정 (시간 순서)
    cmap = cm.get_cmap('viridis')
    norm = Normalize(vmin=0, vmax=n_cycles-1)
    
    # 상단: Voltage vs Time
    for i, cycle in enumerate(cycles_to_plot):
        color = cmap(norm(i))
        ax1.plot(cycle['time_cyc'], cycle['Voltage_V'], 
                color=color, linewidth=0.5, alpha=0.6)
    
    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('Voltage (V)', fontsize=12)
    ax1.set_title('Voltage vs Time (전체 사이클)', fontsize=13)
    ax1.grid(True, alpha=0.3)
    
    # 하단: C-rate vs Time (있는 경우)
    if 'Crate' in cycles_to_plot[0].columns:
        for i, cycle in enumerate(cycles_to_plot):
            color = cmap(norm(i))
            ax2.plot(cycle['time_cyc'], cycle['Crate'], 
                    color=color, linewidth=0.5, alpha=0.6)
        
        ax2.set_xlabel('Time (s)', fontsize=12)
        ax2.set_ylabel('C-rate', fontsize=12)
        ax2.set_title('C-rate vs Time (전체 사이클)', fontsize=13)
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(0.5, 0.5, 'C-rate 데이터 없음', 
                ha='center', va='center', fontsize=14)
    
    # Colorbar
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=[ax1, ax2], orientation='vertical', pad=0.02)
    cbar.set_label('사이클 순서', fontsize=11)
    
    plt.tight_layout()
    return fig


def plot_cycle_grid(cycle_list, indices=None, cols=4, figsize_per_plot=(4, 3)):
    """
    지정된 사이클들을 그리드 형태로 표시
    
    Parameters:
    -----------
    cycle_list : list of pd.DataFrame
        사이클 리스트
    indices : list of int, optional
        표시할 사이클 인덱스 리스트 (None이면 처음 20개)
    cols : int
        그리드 열 수
    figsize_per_plot : tuple
        각 플롯의 크기
    """
    
    if indices is None:
        indices = list(range(min(20, len(cycle_list))))
    
    n_cycles = len(indices)
    rows = (n_cycles + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(figsize_per_plot[0]*cols, figsize_per_plot[1]*rows))
    fig.suptitle(f'Cycle 그리드 뷰 ({n_cycles}개)', fontsize=16, fontweight='bold')
    
    # axes를 1차원 배열로 변환
    if n_cycles == 1:
        axes = [axes]
    else:
        axes = axes.flatten() if rows > 1 or cols > 1 else [axes]
    
    for i, idx in enumerate(indices):
        ax1 = axes[i]
        cycle = cycle_list[idx]
        
        # Voltage 플롯
        color1 = 'tab:blue'
        ax1.plot(cycle['time_cyc'], cycle['Voltage_V'], 
                color=color1, linewidth=0.8)
        ax1.set_title(f'Cycle {idx}', fontsize=10, fontweight='bold')
        ax1.set_xlabel('Time (s)', fontsize=8)
        ax1.set_ylabel('Voltage (V)', color=color1, fontsize=8)
        ax1.tick_params(axis='y', labelcolor=color1, labelsize=7)
        ax1.grid(True, alpha=0.3)
        
        # C-rate 플롯 (오른쪽 y축)
        if 'Crate' in cycle.columns:
            ax2 = ax1.twinx()
            color2 = 'tab:red'
            ax2.plot(cycle['time_cyc'], cycle['Crate'],
                    color=color2, linewidth=0.6, alpha=0.5, linestyle='--')
            ax2.set_ylabel('C-rate', color=color2, fontsize=8)
            ax2.tick_params(axis='y', labelcolor=color2, labelsize=7)
    
    # 사용하지 않는 subplot 숨기기
    for i in range(n_cycles, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    return fig


def plot_voltage_vs_capacity(cycle_list, indices=None, figsize=(14, 8)):
    """
    Voltage vs Capacity 플롯 (배터리 특성 곡선)
    
    Parameters:
    -----------
    cycle_list : list of pd.DataFrame
        사이클 리스트
    indices : list of int, optional
        표시할 사이클 인덱스 리스트 (None이면 대표 사이클)
    figsize : tuple
        Figure 크기
    """
    
    if indices is None:
        # 대표 사이클: 첫, 중간, 마지막
        n = len(cycle_list)
        indices = [0, n//2, n-1]
    
    fig, ax = plt.subplots(figsize=figsize)
    fig.suptitle('Voltage vs Capacity', fontsize=16, fontweight='bold')
    
    # Colormap
    cmap = cm.get_cmap('plasma')
    norm = Normalize(vmin=0, vmax=len(indices)-1)
    
    for i, idx in enumerate(indices):
        cycle = cycle_list[idx]
        color = cmap(norm(i))
        
        # Capacity 계산 (있는 경우)
        if 'Capacity_mAh' in cycle.columns:
            capacity = cycle['Capacity_mAh']
        elif 'Current_mA' in cycle.columns and 'time_cyc' in cycle.columns:
            # Current 적분으로 Capacity 근사
            time_diff = cycle['time_cyc'].diff().fillna(0) / 3600  # 시간을 시간 단위로
            capacity = (cycle['Current_mA'] * time_diff).cumsum()
        else:
            capacity = np.arange(len(cycle))
        
        ax.plot(capacity, cycle['Voltage_V'], 
               color=color, linewidth=2, alpha=0.7, label=f'Cycle {idx}')
    
    ax.set_xlabel('Capacity (mAh)', fontsize=12)
    ax.set_ylabel('Voltage (V)', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    plt.tight_layout()
    return fig


def plot_cycle_statistics(cycle_list, figsize=(16, 10)):
    """
    사이클 통계 시각화 (데이터 포인트, Voltage 범위, Duration 등)
    
    Parameters:
    -----------
    cycle_list : list of pd.DataFrame
        사이클 리스트
    figsize : tuple
        Figure 크기
    """
    
    # 통계 계산
    cycle_indices = list(range(len(cycle_list)))
    data_points = [len(cycle) for cycle in cycle_list]
    voltage_ranges = [cycle['Voltage_V'].max() - cycle['Voltage_V'].min() 
                     for cycle in cycle_list]
    
    durations = []
    crate_maxs = []
    
    for cycle in cycle_list:
        if 'time_cyc' in cycle.columns:
            durations.append(cycle['time_cyc'].max() - cycle['time_cyc'].min())
        if 'Crate' in cycle.columns:
            crate_maxs.append(cycle['Crate'].abs().max())
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    fig.suptitle('Cycle 통계 추세', fontsize=16, fontweight='bold')
    
    # 1. 데이터 포인트 수
    ax1 = axes[0, 0]
    ax1.plot(cycle_indices, data_points, 'o-', markersize=3, linewidth=0.8)
    ax1.set_xlabel('Cycle Index', fontsize=10)
    ax1.set_ylabel('Data Points', fontsize=10)
    ax1.set_title('데이터 포인트 수 추세', fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # 2. Voltage 범위
    ax2 = axes[0, 1]
    ax2.plot(cycle_indices, voltage_ranges, 'o-', markersize=3, linewidth=0.8, color='green')
    ax2.set_xlabel('Cycle Index', fontsize=10)
    ax2.set_ylabel('Voltage Range (mV)', fontsize=10)
    ax2.set_title('Voltage 범위 추세', fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # 3. Duration
    ax3 = axes[1, 0]
    if durations:
        ax3.plot(cycle_indices, durations, 'o-', markersize=3, linewidth=0.8, color='red')
        ax3.set_xlabel('Cycle Index', fontsize=10)
        ax3.set_ylabel('Duration (s)', fontsize=10)
        ax3.set_title('사이클 지속 시간 추세', fontsize=11)
        ax3.grid(True, alpha=0.3)
    else:
        ax3.text(0.5, 0.5, 'Duration 데이터 없음', ha='center', va='center')
    
    # 4. C-rate max
    ax4 = axes[1, 1]
    if crate_maxs:
        ax4.plot(cycle_indices, crate_maxs, 'o-', markersize=3, linewidth=0.8, color='purple')
        ax4.set_xlabel('Cycle Index', fontsize=10)
        ax4.set_ylabel('Max C-rate', fontsize=10)
        ax4.set_title('최대 C-rate 추세', fontsize=11)
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'C-rate 데이터 없음', ha='center', va='center')
    
    plt.tight_layout()
    return fig


def plot_single_cycle_detailed(cycle_list, cycle_index, figsize=(16, 12)):
    """
    단일 사이클의 상세 분석 플롯
    
    Parameters:
    -----------
    cycle_list : list of pd.DataFrame
        사이클 리스트
    cycle_index : int
        분석할 사이클 인덱스
    figsize : tuple
        Figure 크기
    """
    
    cycle = cycle_list[cycle_index]
    
    fig, axes = plt.subplots(3, 2, figsize=figsize)
    fig.suptitle(f'Cycle {cycle_index} 상세 분석', fontsize=16, fontweight='bold')
    
    # 1. Voltage vs Time
    ax1 = axes[0, 0]
    ax1.plot(cycle['time_cyc'], cycle['Voltage_V'], 'b-', linewidth=1)
    ax1.set_xlabel('Time (s)', fontsize=10)
    ax1.set_ylabel('Voltage (V)', fontsize=10)
    ax1.set_title('Voltage vs Time', fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # 2. Current vs Time
    ax2 = axes[0, 1]
    if 'Current_mA' in cycle.columns:
        ax2.plot(cycle['time_cyc'], cycle['Current_mA'], 'r-', linewidth=1)
        ax2.set_xlabel('Time (s)', fontsize=10)
        ax2.set_ylabel('Current (mA)', fontsize=10)
        ax2.set_title('Current vs Time', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(0.5, 0.5, 'Current 데이터 없음', ha='center', va='center')
    
    # 3. C-rate vs Time
    ax3 = axes[1, 0]
    if 'Crate' in cycle.columns:
        ax3.plot(cycle['time_cyc'], cycle['Crate'], 'g-', linewidth=1)
        ax3.set_xlabel('Time (s)', fontsize=10)
        ax3.set_ylabel('C-rate', fontsize=10)
        ax3.set_title('C-rate vs Time', fontsize=11, fontweight='bold')
        ax3.grid(True, alpha=0.3)
    else:
        ax3.text(0.5, 0.5, 'C-rate 데이터 없음', ha='center', va='center')
    
    # 4. Voltage vs Capacity
    ax4 = axes[1, 1]
    if 'Capacity_mAh' in cycle.columns:
        ax4.plot(cycle['Capacity_mAh'], cycle['Voltage_V'], 'm-', linewidth=1)
        ax4.set_xlabel('Capacity (mAh)', fontsize=10)
        ax4.set_ylabel('Voltage (V)', fontsize=10)
        ax4.set_title('Voltage vs Capacity', fontsize=11, fontweight='bold')
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'Capacity 데이터 없음', ha='center', va='center')
    
    # 5. EndState 분포
    ax5 = axes[2, 0]
    if 'EndState' in cycle.columns:
        endstate_counts = cycle['EndState'].value_counts()
        endstate_counts.plot(kind='bar', ax=ax5, color='orange', alpha=0.7)
        ax5.set_xlabel('EndState', fontsize=10)
        ax5.set_ylabel('빈도', fontsize=10)
        ax5.set_title('EndState 분포', fontsize=11, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
    else:
        ax5.text(0.5, 0.5, 'EndState 데이터 없음', ha='center', va='center')
    
    # 6. Condition 분포
    ax6 = axes[2, 1]
    if 'Condition' in cycle.columns:
        condition_counts = cycle['Condition'].value_counts()
        condition_map = {1: 'Charge', 2: 'Discharge', 3: 'Rest'}
        condition_counts.index = [condition_map.get(int(x), str(int(x))) for x in condition_counts.index]
        condition_counts.plot(kind='bar', ax=ax6, color='cyan', alpha=0.7)
        ax6.set_xlabel('Condition', fontsize=10)
        ax6.set_ylabel('빈도', fontsize=10)
        ax6.set_title('Condition 분포', fontsize=11, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='y')
    else:
        ax6.text(0.5, 0.5, 'Condition 데이터 없음', ha='center', va='center')
    
    plt.tight_layout()
    return fig
