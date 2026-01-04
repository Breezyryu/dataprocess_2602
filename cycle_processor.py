"""
Cycle 데이터 처리 유틸리티 함수
"""

import numpy as np


def process_cycle_list(df, df_results=None, default_capacity=1000):
    """
    DataFrame을 Cycle별로 분할하고 time_cyc, Capa_cyc, Crate 계산
    
    Parameters:
    -----------
    df : pd.DataFrame
        Profile 데이터 (Cycle 컬럼 필요)
    df_results : pd.DataFrame, optional
        Cycle 결과 데이터 (capacity_mAh 포함)
    default_capacity : float
        기본 용량 (mAh), df_results가 없을 때 사용
    
    Returns:
    --------
    list : 처리된 cycle_list
    """
    
    # 1. Cycle별로 데이터프레임 분할
    cycle_list = [group.copy() for _, group in df.groupby('Cycle')]
    
    # 2. 최소 용량 결정
    if df_results is not None and len(df_results) > 0 and 'capacity_mAh' in df_results.columns:
        mincapa = df_results['capacity_mAh'].iloc[0]
    else:
        mincapa = default_capacity
    
    # 3. 각 사이클 처리
    for cycle in cycle_list:
        # time_cyc: 각 사이클마다 0부터 시작
        cycle['time_cyc'] = cycle['time_s'] - cycle['time_s'].iloc[0]
        
        # Capa_cyc: 누적 용량 (mAh)
        cycle['Capa_cyc'] = (cycle['Current_mA'] * cycle['time_cyc'].diff().fillna(0) / 3600).cumsum()
        
        # Crate: C-rate
        cycle['Crate'] = cycle['Current_mA'] / mincapa
    
    return cycle_list


def process_all_channels(loaded_data, default_capacity=1000):
    """
    loaded_data의 모든 채널을 처리하여 cycle_list 생성
    
    Parameters:
    -----------
    loaded_data : dict
        로드된 데이터 딕셔너리
        {'pne_profile': {...}, 'pne_cycle': {...}, 
         'toyo_profile': {...}, 'toyo_cycle': {...}}
    default_capacity : float
        기본 용량 (mAh)
    
    Returns:
    --------
    dict : 채널별 cycle_list 딕셔너리
        {channel_key: cycle_list, ...}
    """
    
    all_cycle_lists = {}
    
    # PNE Profile 데이터 처리
    if 'pne_profile' in loaded_data and loaded_data['pne_profile']:
        for channel_key, df in loaded_data['pne_profile'].items():
            # 해당 채널의 cycle 데이터 찾기
            cycle_key = channel_key.replace('profile', 'cycle')
            df_results = loaded_data.get('pne_cycle', {}).get(cycle_key)
            
            # cycle_list 생성
            cycle_list = process_cycle_list(df, df_results, default_capacity)
            all_cycle_lists[channel_key] = cycle_list
    
    # Toyo Profile 데이터 처리
    if 'toyo_profile' in loaded_data and loaded_data['toyo_profile']:
        for channel_key, df in loaded_data['toyo_profile'].items():
            # 해당 채널의 cycle 데이터 찾기
            cycle_key = channel_key.replace('profile', 'cycle')
            df_results = loaded_data.get('toyo_cycle', {}).get(cycle_key)
            
            # cycle_list 생성
            cycle_list = process_cycle_list(df, df_results, default_capacity)
            all_cycle_lists[channel_key] = cycle_list
    
    return all_cycle_lists


def get_cycle_summary(cycle_list):
    """
    cycle_list의 요약 정보 반환
    
    Parameters:
    -----------
    cycle_list : list
        사이클 리스트
    
    Returns:
    --------
    dict : 요약 정보
    """
    
    summary = {
        'total_cycles': len(cycle_list),
        'total_data_points': sum(len(cycle) for cycle in cycle_list),
        'avg_points_per_cycle': np.mean([len(cycle) for cycle in cycle_list]),
    }
    
    if cycle_list and 'Voltage_V' in cycle_list[0].columns:
        voltage_ranges = [cycle['Voltage_V'].max() - cycle['Voltage_V'].min() 
                         for cycle in cycle_list]
        summary['avg_voltage_range'] = np.mean(voltage_ranges)
        summary['min_voltage_range'] = np.min(voltage_ranges)
        summary['max_voltage_range'] = np.max(voltage_ranges)
    
    if cycle_list and 'time_cyc' in cycle_list[0].columns:
        durations = [cycle['time_cyc'].max() for cycle in cycle_list]
        summary['avg_duration'] = np.mean(durations)
        summary['total_duration'] = np.sum(durations)
    
    if cycle_list and 'Crate' in cycle_list[0].columns:
        crate_maxs = [cycle['Crate'].abs().max() for cycle in cycle_list]
        summary['avg_max_crate'] = np.mean(crate_maxs)
        summary['max_crate'] = np.max(crate_maxs)
    
    return summary
