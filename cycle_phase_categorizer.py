# -*- coding: utf-8 -*-
"""
사이클 내부 카테고리 분류 모듈

각 사이클을 Condition과 EndState 변화를 기반으로 세부 단계로 분류합니다.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


def categorize_cycle_phases(cycle_df: pd.DataFrame, 
                           crate_thresholds: Dict[str, float] = None) -> pd.DataFrame:
    """
    단일 사이클을 Condition, EndState, C-rate 기반으로 단계별로 카테고리 분류
    
    Parameters:
        cycle_df (pd.DataFrame): 단일 사이클 데이터
        crate_thresholds (dict): C-rate 구간 임계값 (선택적)
            예: {'low': 0.5, 'medium': 1.0, 'high': 2.0}
    
    Returns:
        pd.DataFrame: 'phase_category' 컬럼이 추가된 데이터
    """
    df = cycle_df.copy()
    
    # 기본 C-rate 임계값 설정
    if crate_thresholds is None:
        crate_thresholds = {
            'low': 0.5,      # 0.5C 이하
            'medium': 1.0,   # 0.5C ~ 1.0C
            'high': 2.0      # 1.0C ~ 2.0C
            # 2.0C 이상은 'very_high'
        }
    
    # Condition 매핑
    condition_map = {
        1: 'Charge',
        2: 'Discharge', 
        3: 'Rest',
        8: 'CCCV'
    }
    
    # C-rate 레벨 결정 함수
    def get_crate_level(crate_value):
        abs_crate = abs(crate_value)
        if abs_crate <= crate_thresholds['low']:
            return 'Low'
        elif abs_crate <= crate_thresholds['medium']:
            return 'Mid'
        elif abs_crate <= crate_thresholds['high']:
            return 'High'
        else:
            return 'VHigh'
    
    # phase_category 초기화
    df['phase_category'] = 'Unknown'
    
    if 'Condition' in df.columns:
        # Condition 기반 기본 카테고리
        df['condition_name'] = df['Condition'].map(
            lambda x: condition_map.get(x, f'Cond_{x}')
        )
        
        # C-rate 레벨 추가
        if 'Crate' in df.columns:
            df['crate_level'] = df['Crate'].apply(get_crate_level)
        else:
            df['crate_level'] = 'Unknown'
        
        # EndState 변화 감지하여 세부 단계 추가
        if 'EndState' in df.columns:
            # EndState가 변경되는 지점 찾기
            df['endstate_change'] = (df['EndState'] != df['EndState'].shift(1)).astype(int)
            df['phase_id'] = df['endstate_change'].cumsum()
            
            # Condition, C-rate, phase_id 조합으로 세부 카테고리 생성
            df['phase_category'] = df.apply(
                lambda row: f"{row['condition_name']}_{row['crate_level']}_{row['phase_id']:02d}",
                axis=1
            )
            
            # 임시 컬럼 제거
            df.drop(['endstate_change', 'phase_id'], axis=1, inplace=True)
        else:
            # EndState가 없으면 Condition과 C-rate만으로 분류
            df['phase_category'] = df.apply(
                lambda row: f"{row['condition_name']}_{row['crate_level']}",
                axis=1
            )
        
        # 임시 컬럼 제거
        df.drop(['condition_name', 'crate_level'], axis=1, inplace=True)
    
    return df


def categorize_all_cycle_phases(cycle_list: List[pd.DataFrame],
                                crate_thresholds: Dict[str, float] = None) -> List[pd.DataFrame]:
    """
    모든 사이클에 대해 단계별 카테고리 분류
    
    Parameters:
        cycle_list (list): 사이클 데이터프레임 리스트
        crate_thresholds (dict): C-rate 구간 임계값 (선택적)
    
    Returns:
        list: phase_category가 추가된 사이클 리스트
    """
    categorized_cycles = []
    
    print("=" * 80)
    print("🔍 사이클별 단계 카테고리 분류 중... (Condition + C-rate + EndState)")
    print("=" * 80)
    
    # C-rate 임계값 출력
    if crate_thresholds is None:
        crate_thresholds = {'low': 0.5, 'medium': 1.0, 'high': 2.0}
    
    print(f"\nC-rate 구간:")
    print(f"  Low:  ≤ {crate_thresholds['low']}C")
    print(f"  Mid:  {crate_thresholds['low']}C ~ {crate_thresholds['medium']}C")
    print(f"  High: {crate_thresholds['medium']}C ~ {crate_thresholds['high']}C")
    print(f"  VHigh: > {crate_thresholds['high']}C")
    print()
    
    for idx, cycle in enumerate(cycle_list):
        categorized_cycle = categorize_cycle_phases(cycle, crate_thresholds)
        categorized_cycles.append(categorized_cycle)
        
        # 진행상황 출력
        if (idx + 1) % 10 == 0 or idx == 0:
            unique_phases = categorized_cycle['phase_category'].nunique()
            print(f"  Cycle {idx}: {unique_phases}개 단계 발견")
    
    print(f"\n✅ 총 {len(cycle_list)}개 사이클 분류 완료")
    print("=" * 80)
    
    return categorized_cycles


def get_phase_summary(cycle_df: pd.DataFrame) -> pd.DataFrame:
    """
    단일 사이클의 단계별 요약 정보
    
    Parameters:
        cycle_df (pd.DataFrame): phase_category가 포함된 사이클 데이터
    
    Returns:
        pd.DataFrame: 단계별 요약 통계
    """
    if 'phase_category' not in cycle_df.columns:
        print("⚠️  'phase_category' 컬럼이 없습니다. categorize_cycle_phases()를 먼저 실행하세요.")
        return pd.DataFrame()
    
    summary_data = []
    
    for phase in cycle_df['phase_category'].unique():
        phase_data = cycle_df[cycle_df['phase_category'] == phase]
        
        summary = {
            'phase': phase,
            'count': len(phase_data),
            'duration_s': phase_data['time_cyc'].max() - phase_data['time_cyc'].min() if 'time_cyc' in phase_data.columns else 0,
            'start_time': phase_data['time_cyc'].min() if 'time_cyc' in phase_data.columns else 0,
            'end_time': phase_data['time_cyc'].max() if 'time_cyc' in phase_data.columns else 0,
        }
        
        # 전압 정보
        if 'Voltage_V' in phase_data.columns:
            summary['voltage_mean'] = phase_data['Voltage_V'].mean()
            summary['voltage_min'] = phase_data['Voltage_V'].min()
            summary['voltage_max'] = phase_data['Voltage_V'].max()
        
        # 전류 정보
        if 'Current_mA' in phase_data.columns:
            summary['current_mean'] = phase_data['Current_mA'].mean()
            summary['current_min'] = phase_data['Current_mA'].min()
            summary['current_max'] = phase_data['Current_mA'].max()
        
        # C-rate 정보
        if 'Crate' in phase_data.columns:
            summary['crate_mean'] = phase_data['Crate'].mean()
            summary['crate_min'] = phase_data['Crate'].min()
            summary['crate_max'] = phase_data['Crate'].max()
        
        # 용량 정보
        if 'Capa_cyc' in phase_data.columns:
            summary['capacity_change'] = phase_data['Capa_cyc'].iloc[-1] - phase_data['Capa_cyc'].iloc[0]
        
        summary_data.append(summary)
    
    return pd.DataFrame(summary_data).sort_values('start_time')


def print_cycle_phase_report(cycle_df: pd.DataFrame, cycle_index: int = 0):
    """
    단일 사이클의 단계별 상세 보고서 출력
    
    Parameters:
        cycle_df (pd.DataFrame): phase_category가 포함된 사이클 데이터
        cycle_index (int): 사이클 인덱스 (표시용)
    """
    print("=" * 80)
    print(f"📊 Cycle {cycle_index} 단계별 분석 보고서 (Condition + C-rate + EndState)")
    print("=" * 80)
    
    if 'phase_category' not in cycle_df.columns:
        print("⚠️  'phase_category' 컬럼이 없습니다.")
        return
    
    summary = get_phase_summary(cycle_df)
    
    print(f"\n총 데이터 포인트: {len(cycle_df):,}")
    print(f"총 단계 수: {cycle_df['phase_category'].nunique()}")
    
    if 'time_cyc' in cycle_df.columns:
        total_time = cycle_df['time_cyc'].max()
        print(f"총 소요 시간: {total_time:.0f}초 ({total_time/3600:.2f}시간)")
    
    print("\n" + "-" * 80)
    print("단계별 상세 정보:")
    print("-" * 80)
    
    for idx, row in summary.iterrows():
        print(f"\n【{row['phase']}】")
        print(f"  데이터 포인트: {row['count']:,}개")
        print(f"  시간: {row['start_time']:.0f}s ~ {row['end_time']:.0f}s (지속: {row['duration_s']:.0f}s)")
        
        if 'voltage_mean' in row:
            print(f"  전압: {row['voltage_mean']:.2f}V (범위: {row['voltage_min']:.2f} ~ {row['voltage_max']:.2f}V)")
        
        if 'current_mean' in row:
            print(f"  전류: {row['current_mean']:.2f}mA (범위: {row['current_min']:.2f} ~ {row['current_max']:.2f}mA)")
        
        if 'crate_mean' in row:
            print(f"  C-rate: {row['crate_mean']:.3f}C (범위: {row['crate_min']:.3f} ~ {row['crate_max']:.3f}C)")
        
        if 'capacity_change' in row:
            print(f"  용량 변화: {row['capacity_change']:.2f}mAh")
    
    print("\n" + "=" * 80)


def visualize_cycle_phases(cycle_df: pd.DataFrame, cycle_index: int = 0):
    """
    사이클의 단계별 시각화
    
    Parameters:
        cycle_df (pd.DataFrame): phase_category가 포함된 사이클 데이터
        cycle_index (int): 사이클 인덱스 (표시용)
    """
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    
    if 'phase_category' not in cycle_df.columns:
        print("⚠️  'phase_category' 컬럼이 없습니다.")
        return
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 10))
    
    # 고유 단계 및 색상 매핑
    unique_phases = cycle_df['phase_category'].unique()
    colors = cm.tab20(np.linspace(0, 1, len(unique_phases)))
    phase_colors = dict(zip(unique_phases, colors))
    
    # 1. 전압 프로파일
    if 'Voltage_V' in cycle_df.columns and 'time_cyc' in cycle_df.columns:
        for phase in unique_phases:
            phase_data = cycle_df[cycle_df['phase_category'] == phase]
            axes[0].plot(phase_data['time_cyc'], phase_data['Voltage_V'], 
                        color=phase_colors[phase], label=phase, linewidth=1.5)
        
        axes[0].set_ylabel('전압 (V)', fontsize=12)
        axes[0].set_title(f'Cycle {cycle_index} - 전압 프로파일 (단계별)', fontsize=14, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    
    # 2. 전류 프로파일
    if 'Current_mA' in cycle_df.columns and 'time_cyc' in cycle_df.columns:
        for phase in unique_phases:
            phase_data = cycle_df[cycle_df['phase_category'] == phase]
            axes[1].plot(phase_data['time_cyc'], phase_data['Current_mA'], 
                        color=phase_colors[phase], linewidth=1.5)
        
        axes[1].axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        axes[1].set_ylabel('전류 (mA)', fontsize=12)
        axes[1].set_title(f'Cycle {cycle_index} - 전류 프로파일 (단계별)', fontsize=14, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
    
    # 3. 용량 변화
    if 'Capa_cyc' in cycle_df.columns and 'time_cyc' in cycle_df.columns:
        for phase in unique_phases:
            phase_data = cycle_df[cycle_df['phase_category'] == phase]
            axes[2].plot(phase_data['time_cyc'], phase_data['Capa_cyc'], 
                        color=phase_colors[phase], linewidth=1.5)
        
        axes[2].set_xlabel('시간 (s)', fontsize=12)
        axes[2].set_ylabel('용량 (mAh)', fontsize=12)
        axes[2].set_title(f'Cycle {cycle_index} - 용량 변화 (단계별)', fontsize=14, fontweight='bold')
        axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("사이클 단계 카테고리 분류 모듈")
    print("\n사용 가능한 함수:")
    print("  - categorize_cycle_phases(cycle_df)")
    print("  - categorize_all_cycle_phases(cycle_list)")
    print("  - get_phase_summary(cycle_df)")
    print("  - print_cycle_phase_report(cycle_df, cycle_index)")
    print("  - visualize_cycle_phases(cycle_df, cycle_index)")
    
    print("\n기본 사용법:")
    print("```python")
    print("import cycle_phase_categorizer")
    print("")
    print("# 모든 사이클에 단계 카테고리 추가")
    print("categorized_cycles = cycle_phase_categorizer.categorize_all_cycle_phases(cycle_list)")
    print("")
    print("# 특정 사이클 분석")
    print("cycle_phase_categorizer.print_cycle_phase_report(categorized_cycles[0], cycle_index=0)")
    print("")
    print("# 시각화")
    print("cycle_phase_categorizer.visualize_cycle_phases(categorized_cycles[0], cycle_index=0)")
    print("```")
