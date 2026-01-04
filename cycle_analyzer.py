"""
Cycle 데이터 구조 분석 모듈
cycle_list의 구조와 통계를 분석
"""

import pandas as pd
import numpy as np


def analyze_cycle_structure(cycle_list):
    """
    cycle_list의 구조 분석
    
    Parameters:
    -----------
    cycle_list : list of pd.DataFrame
        사이클 리스트
    
    Returns:
    --------
    pd.DataFrame : 사이클 구조 요약 테이블
    """
    
    if not cycle_list:
        print("⚠️ cycle_list가 비어있습니다.")
        return pd.DataFrame()
    
    summary_data = []
    
    for idx, cycle in enumerate(cycle_list):
        # 기본 정보
        info = {
            'Cycle_Index': idx,
            'Data_Points': len(cycle),
            'Columns': len(cycle.columns),
            'Column_Names': ', '.join(cycle.columns.tolist()[:5]) + ('...' if len(cycle.columns) > 5 else ''),
        }
        
        # Voltage 정보
        if 'Voltage_V' in cycle.columns:
            info['Voltage_Min'] = cycle['Voltage_V'].min()
            info['Voltage_Max'] = cycle['Voltage_V'].max()
            info['Voltage_Range'] = cycle['Voltage_V'].max() - cycle['Voltage_V'].min()
        
        # Current 정보
        if 'Current_mA' in cycle.columns:
            info['Current_Min'] = cycle['Current_mA'].min()
            info['Current_Max'] = cycle['Current_mA'].max()
        
        # Time 정보
        if 'time_cyc' in cycle.columns:
            info['Duration_s'] = cycle['time_cyc'].max() - cycle['time_cyc'].min()
        
        # EndState 정보
        if 'EndState' in cycle.columns:
            info['EndState_Unique'] = cycle['EndState'].nunique()
            info['EndState_Values'] = ', '.join([str(int(x)) for x in sorted(cycle['EndState'].unique())])
        
        # Condition 정보
        if 'Condition' in cycle.columns:
            info['Condition_Unique'] = cycle['Condition'].nunique()
            condition_counts = cycle['Condition'].value_counts()
            condition_map = {1: 'Charge', 2: 'Discharge', 3: 'Rest'}
            info['Condition_Types'] = ', '.join([condition_map.get(int(k), str(int(k))) 
                                                  for k in sorted(cycle['Condition'].unique())])
        
        # C-rate 정보
        if 'Crate' in cycle.columns:
            info['Crate_Max'] = cycle['Crate'].abs().max()
            info['Crate_Mean'] = cycle['Crate'].abs().mean()
        
        # Category 정보 (있는 경우)
        if 'category' in cycle.columns:
            info['Category'] = cycle['category'].iloc[0]
        
        summary_data.append(info)
    
    summary_df = pd.DataFrame(summary_data)
    
    return summary_df


def print_cycle_statistics(cycle_list):
    """
    cycle_list의 전체 통계 출력
    
    Parameters:
    -----------
    cycle_list : list of pd.DataFrame
        사이클 리스트
    """
    
    if not cycle_list:
        print("⚠️ cycle_list가 비어있습니다.")
        return
    
    print("="*80)
    print("📊 Cycle 데이터 전체 통계")
    print("="*80)
    
    # 기본 통계
    print(f"\n총 사이클 수: {len(cycle_list)}")
    
    # 데이터 포인트 통계
    data_points = [len(cycle) for cycle in cycle_list]
    print(f"\n데이터 포인트 수:")
    print(f"  평균: {np.mean(data_points):.0f}")
    print(f"  최소: {np.min(data_points)}")
    print(f"  최대: {np.max(data_points)}")
    print(f"  표준편차: {np.std(data_points):.0f}")
    
    # Voltage 통계
    if 'Voltage_V' in cycle_list[0].columns:
        voltage_ranges = [cycle['Voltage_V'].max() - cycle['Voltage_V'].min() 
                         for cycle in cycle_list]
        print(f"\nVoltage 범위 (mV):")
        print(f"  평균: {np.mean(voltage_ranges):.0f}")
        print(f"  최소: {np.min(voltage_ranges):.0f}")
        print(f"  최대: {np.max(voltage_ranges):.0f}")
    
    # Duration 통계
    if 'time_cyc' in cycle_list[0].columns:
        durations = [cycle['time_cyc'].max() - cycle['time_cyc'].min() 
                    for cycle in cycle_list]
        print(f"\n사이클 지속 시간 (s):")
        print(f"  평균: {np.mean(durations):.0f}")
        print(f"  최소: {np.min(durations):.0f}")
        print(f"  최대: {np.max(durations):.0f}")
    
    # Category 분포 (있는 경우)
    if 'category' in cycle_list[0].columns:
        categories = [cycle['category'].iloc[0] for cycle in cycle_list if len(cycle) > 0]
        category_counts = pd.Series(categories).value_counts()
        print(f"\n카테고리 분포:")
        for cat, count in category_counts.items():
            print(f"  {cat}: {count}개 ({count/len(cycle_list)*100:.1f}%)")
    
    # 컬럼 정보
    print(f"\n컬럼 정보:")
    if cycle_list:
        columns = cycle_list[0].columns.tolist()
        print(f"  컬럼 수: {len(columns)}")
        print(f"  컬럼 목록: {', '.join(columns)}")
    
    print("\n" + "="*80)


def analyze_cycle_differences(cycle_list, indices):
    """
    특정 사이클들 간의 차이 분석
    
    Parameters:
    -----------
    cycle_list : list of pd.DataFrame
        사이클 리스트
    indices : list of int
        비교할 사이클 인덱스 리스트
    
    Returns:
    --------
    pd.DataFrame : 비교 테이블
    """
    
    comparison_data = []
    
    for idx in indices:
        if idx >= len(cycle_list):
            continue
        
        cycle = cycle_list[idx]
        
        info = {
            'Cycle': idx,
            'Points': len(cycle),
        }
        
        if 'Voltage_V' in cycle.columns:
            info['V_min'] = cycle['Voltage_V'].min()
            info['V_max'] = cycle['Voltage_V'].max()
            info['V_range'] = cycle['Voltage_V'].max() - cycle['Voltage_V'].min()
        
        if 'time_cyc' in cycle.columns:
            info['Duration'] = cycle['time_cyc'].max() - cycle['time_cyc'].min()
        
        if 'EndState' in cycle.columns:
            info['EndStates'] = len(cycle['EndState'].unique())
        
        if 'Crate' in cycle.columns:
            info['Crate_max'] = cycle['Crate'].abs().max()
        
        if 'category' in cycle.columns:
            info['Category'] = cycle['category'].iloc[0]
        
        comparison_data.append(info)
    
    return pd.DataFrame(comparison_data)
