# ============================================================================
# data 구조 출력
# ============================================================================

import json

def print_data_structure(data, max_depth=3):
    """
    data 구조를 보기 좋게 출력
    
    Parameters:
    -----------
    data : dict
        data_combiner.process_and_combine()의 출력
    max_depth : int
        출력할 최대 깊이
    """
    
    print("="*80)
    print("📊 data 구조")
    print("="*80)
    
    # ========================================================================
    # 1. 최상위 구조
    # ========================================================================
    
    print("\n[최상위 키]")
    for key in data.keys():
        print(f"  - {key}")
    
    # ========================================================================
    # 2. metadata 구조
    # ========================================================================
    
    print("\n[metadata]")
    metadata = data['metadata']
    for key, value in metadata.items():
        if isinstance(value, (list, dict)):
            print(f"  - {key}: {type(value).__name__} (길이: {len(value)})")
        else:
            print(f"  - {key}: {value}")
    
    # ========================================================================
    # 3. channels 구조
    # ========================================================================
    
    print("\n[channels]")
    channels = data['channels']
    print(f"  총 채널 수: {len(channels)}개")
    
    print("\n  채널 목록:")
    for channel_key in channels.keys():
        print(f"    - {channel_key}")
    
    # ========================================================================
    # 4. 첫 번째 채널 상세 구조
    # ========================================================================
    
    if channels:
        first_channel_key = list(channels.keys())[0]
        first_channel = channels[first_channel_key]
        
        print(f"\n[첫 번째 채널 상세: {first_channel_key}]")
        
        for key, value in first_channel.items():
            if value is None:
                print(f"  - {key}: None")
            elif isinstance(value, pd.DataFrame):
                print(f"  - {key}: DataFrame")
                print(f"      shape: {value.shape}")
                print(f"      columns: {value.columns.tolist()}")
            else:
                print(f"  - {key}: {value}")
    
    # ========================================================================
    # 5. 전체 구조 요약
    # ========================================================================
    
    print("\n" + "="*80)
    print("📋 구조 요약")
    print("="*80)
    
    print(f"""
data = {{
    'metadata': {{
        'total_channels': {metadata['total_channels']},
        'total_paths': {metadata['total_paths']},
        'cycler_types': {metadata['cycler_types']},
        'paths': [...]
    }},
    'channels': {{
        'channel_name': {{
            'cycler_type': 'PNE' or 'Toyo',
            'capacity_mAh': float,
            'folder_name': str,
            'channel_name': str,
            'cycle': DataFrame or None,
            'profile': DataFrame or None
        }},
        ...  # {len(channels)}개 채널
    }}
}}
""")
    
    print("="*80)


# 실행
print_data_structure(data)
