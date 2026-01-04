"""
배터리 데이터 처리 및 통합 DataFrame 변환 유틸리티
새로운 채널 기반 loaded_data 구조에 맞게 업데이트됨
"""

import pandas as pd


def process_and_combine(paths):
    """
    paths를 입력받아 데이터 로드 및 통합 (단일 출력)
    
    Parameters:
    -----------
    paths : list
        분석할 데이터 경로 리스트
    
    Returns:
    --------
    dict : 통합 데이터 딕셔너리
        {
            'metadata': {
                'total_channels': int,
                'total_paths': int,
                'cycler_types': dict
            },
            'channels': {
                'channel_name': {
                    'cycler_type': 'PNE' or 'Toyo',
                    'capacity_mAh': float,
                    'folder_name': str,
                    'channel_name': str,
                    'cycle': DataFrame,
                    'profile': DataFrame
                },
                ...
            }
        }
    """
    import dataprocess
    
    # 데이터 로드
    df_results, loaded_data = dataprocess.process_battery_data(paths)
    
    # 메타데이터 생성
    cycler_types = {}
    for channel_data in loaded_data.values():
        cycler_type = channel_data['cycler_type']
        cycler_types[cycler_type] = cycler_types.get(cycler_type, 0) + 1
    
    # 통합 출력
    result = {
        'metadata': {
            'total_channels': len(loaded_data),
            'total_paths': len(paths),
            'cycler_types': cycler_types,
            'paths': paths
        },
        'channels': loaded_data
    }
    
    return result


def combine_to_dataframe(loaded_data):
    """
    새로운 채널 기반 loaded_data를 통합 DataFrame으로 변환
    
    Parameters:
    -----------
    loaded_data : dict
        채널별 데이터 딕셔너리
        {
            'channel_name': {
                'cycler_type': 'PNE' or 'Toyo',
                'capacity_mAh': float,
                'folder_name': str,
                'channel_name': str,
                'cycle': DataFrame,
                'profile': DataFrame
            },
            ...
        }
    
    Returns:
    --------
    pd.DataFrame : 통합 DataFrame
        컬럼: channel, cycler_type, data_type, ...
    """
    
    all_data = []
    
    # 각 채널 순회
    for channel_key, channel_data in loaded_data.items():
        # Cycle 데이터 처리
        if channel_data['cycle'] is not None and len(channel_data['cycle']) > 0:
            df_temp = channel_data['cycle'].copy()
            df_temp['channel'] = channel_key
            df_temp['cycler_type'] = channel_data['cycler_type']
            df_temp['capacity_mAh_meta'] = channel_data['capacity_mAh']
            df_temp['folder_name'] = channel_data['folder_name']
            df_temp['data_type'] = 'cycle'
            all_data.append(df_temp)
        
        # Profile 데이터 처리
        if channel_data['profile'] is not None and len(channel_data['profile']) > 0:
            df_temp = channel_data['profile'].copy()
            df_temp['channel'] = channel_key
            df_temp['cycler_type'] = channel_data['cycler_type']
            df_temp['capacity_mAh_meta'] = channel_data['capacity_mAh']
            df_temp['folder_name'] = channel_data['folder_name']
            df_temp['data_type'] = 'profile'
            all_data.append(df_temp)
    
    # 통합
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # 컬럼 순서 정리 (메타데이터를 앞으로)
        meta_cols = ['channel', 'cycler_type', 'data_type', 'folder_name']
        if 'Cycle' in combined_df.columns:
            meta_cols.append('Cycle')
        
        other_cols = [col for col in combined_df.columns if col not in meta_cols]
        combined_df = combined_df[meta_cols + other_cols]
        
        return combined_df
    else:
        return pd.DataFrame()


def get_cycle_data_only(loaded_data):
    """
    Cycle 데이터만 통합 DataFrame으로 변환 (Profile 제외)
    
    Parameters:
    -----------
    loaded_data : dict
        채널별 데이터 딕셔너리
    
    Returns:
    --------
    pd.DataFrame : Cycle 데이터만 포함한 통합 DataFrame
    """
    
    all_data = []
    
    for channel_key, channel_data in loaded_data.items():
        if channel_data['cycle'] is not None and len(channel_data['cycle']) > 0:
            df_temp = channel_data['cycle'].copy()
            df_temp['channel'] = channel_key
            df_temp['cycler_type'] = channel_data['cycler_type']
            df_temp['capacity_mAh_meta'] = channel_data['capacity_mAh']
            df_temp['folder_name'] = channel_data['folder_name']
            all_data.append(df_temp)
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # 컬럼 순서 정리
        meta_cols = ['channel', 'cycler_type', 'folder_name']
        if 'Cycle' in combined_df.columns:
            meta_cols.append('Cycle')
        
        other_cols = [col for col in combined_df.columns if col not in meta_cols]
        combined_df = combined_df[meta_cols + other_cols]
        
        return combined_df
    else:
        return pd.DataFrame()


def get_profile_data_only(loaded_data):
    """
    Profile 데이터만 통합 DataFrame으로 변환 (Cycle 제외)
    
    Parameters:
    -----------
    loaded_data : dict
        채널별 데이터 딕셔너리
    
    Returns:
    --------
    pd.DataFrame : Profile 데이터만 포함한 통합 DataFrame
    """
    
    all_data = []
    
    for channel_key, channel_data in loaded_data.items():
        if channel_data['profile'] is not None and len(channel_data['profile']) > 0:
            df_temp = channel_data['profile'].copy()
            df_temp['channel'] = channel_key
            df_temp['cycler_type'] = channel_data['cycler_type']
            df_temp['capacity_mAh_meta'] = channel_data['capacity_mAh']
            df_temp['folder_name'] = channel_data['folder_name']
            all_data.append(df_temp)
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # 컬럼 순서 정리
        meta_cols = ['channel', 'cycler_type', 'folder_name']
        if 'Cycle' in combined_df.columns:
            meta_cols.append('Cycle')
        
        other_cols = [col for col in combined_df.columns if col not in meta_cols]
        combined_df = combined_df[meta_cols + other_cols]
        
        return combined_df
    else:
        return pd.DataFrame()


def print_dataframe_summary(df):
    """
    통합 DataFrame의 요약 정보 출력
    
    Parameters:
    -----------
    df : pd.DataFrame
        통합 DataFrame
    """
    
    print("="*80)
    print("📊 통합 DataFrame 요약")
    print("="*80)
    
    print(f"\n전체 행 수: {len(df):,}")
    print(f"전체 컬럼 수: {len(df.columns)}")
    
    if 'channel' in df.columns:
        print(f"\n채널 수: {df['channel'].nunique()}")
        print("채널 목록:")
        for channel in df['channel'].unique():
            count = len(df[df['channel'] == channel])
            print(f"  - {channel}: {count:,}행")
    
    if 'cycler_type' in df.columns:
        print(f"\nCycler 타입 분포:")
        print(df['cycler_type'].value_counts())
    
    if 'data_type' in df.columns:
        print(f"\n데이터 타입 분포:")
        print(df['data_type'].value_counts())
    
    if 'Cycle' in df.columns:
        print(f"\n사이클 범위: {df['Cycle'].min()} ~ {df['Cycle'].max()}")
    
    print(f"\n컬럼 목록:")
    print(df.columns.tolist())
    
    print("\n" + "="*80)
