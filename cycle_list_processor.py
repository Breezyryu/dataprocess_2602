"""
배터리 데이터 Cycle List 처리 유틸리티
모든 채널에 대해 cycle_list 생성 및 계산
"""

import numpy as np
import copy


def process_all_channels(data):
    """
    모든 채널에 대해 cycle_list 생성 및 처리
    
    Parameters:
    -----------
    data : dict
        data_combiner.process_and_combine()의 출력
        {'metadata': {...}, 'channels': {...}}
    
    Returns:
    --------
    dict : 새로운 data 객체 (각 채널의 profile이 cycle_list로 업데이트됨)
        data['channels'][channel_key]['profile'] = [cycle1_df, cycle2_df, ...]
        원본 데이터는 수정되지 않음
    """
    
    # 입력 데이터의 깊은 복사본 생성 (원본 보존)
    data = copy.deepcopy(data)

    
    print("="*80)
    print("🔄 전체 채널 Cycle List 처리")
    print("="*80)
    
    for channel_key, channel_data in data['channels'].items():
        print(f"\n처리 중: {channel_key}")
        
        # Profile 데이터 확인
        if channel_data['profile'] is None:
            print("  ⚠️ Profile 데이터 없음 - 건너뜀")
            continue
        
        # 이미 처리된 경우(cycle_list) 건너뛰기
        if isinstance(channel_data['profile'], list):
            print("  ℹ️ 이미 처리됨 - 건너뜀")
            continue
        
        df = channel_data['profile']
        
        # Cycle별로 데이터프레임 분할
        cycle_list = [group.copy() for _, group in df.groupby('Cycle')]
        
        # time_cyc 생성
        for cycle in cycle_list:
            cycle['time_cyc'] = cycle['time_s'] - cycle['time_s'].iloc[0]
        
        # 최소 용량 가져오기
        if channel_data['cycle'] is not None:
            df_cycle = channel_data['cycle']
            
            # PNE: DchgCap_mAh, Toyo: Capacity_mAh
            if 'DchgCap_mAh' in df_cycle.columns:
                mincapa = df_cycle['DchgCap_mAh'].iloc[0]
            elif 'Capacity_mAh' in df_cycle.columns:
                mincapa = df_cycle['Capacity_mAh'].iloc[0]
            else:
                mincapa = channel_data['capacity_mAh'] or 1000
        else:
            mincapa = channel_data['capacity_mAh'] or 1000
        
        # Capa_cyc와 Crate 계산
        for cycle in cycle_list:
            cycle['Capa_cyc'] = (cycle['Current_mA'] * cycle['time_cyc'].diff().fillna(0) / 3600).cumsum()
            cycle['Crate'] = cycle['Current_mA'] / mincapa
        
        # cycle_list를 원본 데이터 구조에 저장
        channel_data['profile'] = cycle_list
        
        print(f"  ✅ {len(cycle_list)}개 사이클 처리 완료")
    
    # 결과 요약
    print("\n" + "="*80)
    print("📋 처리 결과")
    print("="*80)
    
    processed_channels = {k: v['profile'] for k, v in data['channels'].items() if isinstance(v['profile'], list)}
    total_channels = len(processed_channels)
    total_cycles = sum(len(cycle_list) for cycle_list in processed_channels.values())
    
    print(f"\n처리된 채널 수: {total_channels}개")
    print(f"총 사이클 수: {total_cycles}개")
    
    if processed_channels:
        print(f"\n채널별 사이클 수:")
        for channel_key, cycle_list in processed_channels.items():
            print(f"  - {channel_key}: {len(cycle_list)}개")
    
    print("\n✅ 전체 처리 완료!")
    print("="*80)
    
    return data


def get_channel_cycle_list(data, channel_index=0):
    """
    특정 채널의 cycle_list 가져오기
    
    Parameters:
    -----------
    data : dict
        process_all_channels()의 출력 (data 객체)
    channel_index : int
        채널 인덱스 (기본값: 0)
    
    Returns:
    --------
    tuple : (channel_key, cycle_list)
    """
    
    channel_keys = list(data['channels'].keys())
    
    if channel_index >= len(channel_keys):
        raise ValueError(f"채널 인덱스 {channel_index}가 범위를 벗어났습니다. (최대: {len(channel_keys)-1})")
    
    channel_key = channel_keys[channel_index]
    cycle_list = data['channels'][channel_key]['profile']
    
    print(f"선택된 채널: {channel_key}")
    print(f"사이클 수: {len(cycle_list) if isinstance(cycle_list, list) else 0}개")
    
    return channel_key, cycle_list
