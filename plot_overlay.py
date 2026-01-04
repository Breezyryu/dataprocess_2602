"""
카테고리별 전체 사이클을 겹쳐서 시각화하는 추가 함수
뇌과학적으로 구분하기 좋은 색상 그라데이션 사용
"""

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize


def plot_category_overlay(cycle_list, categories, show_crate=True):
    """
    각 카테고리의 모든 사이클을 겹쳐서 표시 (뇌과학적 색상 그라데이션)
    
    지각적으로 균일하고 색맹 친화적인 colormap 사용:
    - viridis: 어두운 보라 → 녹색 → 노란색
    - plasma: 어두운 보라 → 주황 → 노란색
    - cividis: 완전 색맹 친화적 (파랑 → 노란색)
    - turbo: 무지개색 (더 많은 색상 변화)
    
    Parameters:
    -----------
    cycle_list : list
        전체 사이클 리스트
    categories : dict
        카테고리별 사이클 인덱스 딕셔너리
    show_crate : bool
        C-rate 표시 여부
    """
    fig, axes = plt.subplots(2, 2, figsize=(18, 14))
    fig.suptitle('카테고리별 전체 사이클 오버레이 (색상 그라데이션)', fontsize=16, fontweight='bold')
    
    # 카테고리별 colormap 설정 (뇌과학적으로 구분하기 좋은 색상)
    categories_info = [
        ('RPT', 0, 0, 'viridis'),           # 어두운 보라 → 녹색 → 노란색
        ('SOC_Definition', 0, 1, 'plasma'), # 어두운 보라 → 주황 → 노란색
        ('Resistance_Measurement', 1, 0, 'cividis'),  # 색맹 친화적 파랑 → 노란색
        ('Accelerated_Aging', 1, 1, 'turbo')  # 무지개색 (파랑 → 빨강)
    ]
    
    for cat_name, row, col, cmap_name in categories_info:
        ax1 = axes[row, col]
        
        if cat_name not in categories or not categories[cat_name]:
            ax1.text(0.5, 0.5, 'No data', ha='center', va='center', fontsize=14)
            ax1.set_title(f'{cat_name}', fontsize=12, fontweight='bold')
            continue
        
        indices = categories[cat_name]
        n_cycles = len(indices)
        
        # Colormap 생성 (사이클 인덱스 기반 그라데이션)
        cmap = cm.get_cmap(cmap_name)
        norm = Normalize(vmin=0, vmax=n_cycles-1)
        
        # 모든 사이클 겹쳐 그리기
        for i, idx in enumerate(indices):
            cycle = cycle_list[idx]
            color = cmap(norm(i))
            
            # Voltage 플롯 (왼쪽 y축)
            ax1.plot(cycle['time_cyc'], cycle['Voltage_V'], 
                   color=color, linewidth=0.8, alpha=0.6)
        
        # 축 설정
        ax1.set_title(f'{cat_name} (총 {n_cycles}개 사이클)', 
                    fontsize=12, fontweight='bold')
        ax1.set_xlabel('Time (s)', fontsize=10)
        ax1.set_ylabel('Voltage (V)', color='black', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # C-rate 플롯 (오른쪽 y축) - 대표 사이클 (첫/중간/마지막)
        if show_crate and 'Crate' in cycle_list[indices[0]].columns:
            ax2 = ax1.twinx()
            
            # 대표 사이클 3개: 첫 번째, 중간, 마지막
            representative_indices = [
                (0, '첫 번째'),
                (n_cycles // 2, '중간'),
                (n_cycles - 1, '마지막')
            ]
            
            for i, label in representative_indices:
                if i < n_cycles:
                    idx = indices[i]
                    cycle = cycle_list[idx]
                    color = cmap(norm(i))
                    ax2.plot(cycle['time_cyc'], cycle['Crate'], 
                           color=color, linewidth=1.0, alpha=0.8, linestyle='--',
                           label=f'{label} (cycle {idx})')
            
            ax2.set_ylabel('C-rate', color='black', fontsize=10)
            ax2.legend(fontsize=8, loc='upper right')
        
        # Colorbar 추가 (그라데이션 범례)
        sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax1, orientation='vertical', pad=0.15 if show_crate else 0.02)
        cbar.set_label('사이클 순서', fontsize=9)
        cbar.ax.tick_params(labelsize=8)
    
    plt.tight_layout()
    return fig
