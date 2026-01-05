"""
모든 채널의 사이클 카테고리화 유틸리티
"""

import cycle_categorizer


def categorize_all_channels(data):
    """
    data 객체의 모든 채널에 대해 사이클 카테고리화 수행
    
    Parameters:
    -----------
    data : dict
        cycle_list_processor.process_all_channels()의 출력
        data['channels'][channel_key]['profile'] = cycle_list
    
    Returns:
    --------
    dict : 입력된 data 객체 (각 채널에 카테고리 정보가 추가됨)
        - data['channels'][channel_key]['profile'][i]에 'category' 컬럼 추가
        - data['channels'][channel_key]['cycle_list'] = {
            'Unknown': [0, 1, 2, ...],  # 인덱스 리스트
            'RPT': [3, 4, ...],
            'SOC_Definition': [5, 6, ...],
            'Resistance_Measurement': [7, 8, ...],
            'Accelerated_Aging': [9, 10, ...]
          }
    """
    
    print("="*80)
    print("🏷️  전체 채널 사이클 카테고리화")
    print("="*80)
    
    for channel_key, channel_data in data['channels'].items():
        print(f"\n처리 중: {channel_key}")
        
        # Profile 데이터 확인
        cycle_list = channel_data['profile']
        
        if not isinstance(cycle_list, list):
            print("  ⚠️ Cycle list가 아님 - 건너뜀")
            continue
        
        # 카테고리화 수행
        categories = cycle_categorizer.categorize_cycles(cycle_list)
        
        # 각 사이클 DataFrame에 category 컬럼 추가
        for category, indices in categories.items():
            for idx in indices:
                cycle_list[idx]['category'] = category
        
        # cycle_list에는 카테고리별 인덱스만 저장 (데이터 중복 방지)
        channel_data['cycle_list'] = categories
        
        # 요약 출력
        total_cycles = sum(len(indices) for indices in categories.values())
        print(f"  ✅ {total_cycles}개 사이클 분류 완료")
        for category, indices in categories.items():
            if indices:
                print(f"    - {category}: {len(indices)}개")
    
    # 전체 요약
    print("\n" + "="*80)
    print("📋 카테고리화 결과 요약")
    print("="*80)
    
    # 처리된 채널 수 계산
    processed_channels = [k for k, v in data['channels'].items() if 'cycle_list' in v]
    total_channels = len(processed_channels)
    print(f"\n처리된 채널 수: {total_channels}개")
    
    # 카테고리별 전체 통계
    total_stats = {
        'Unknown': 0,
        'RPT': 0,
        'SOC_Definition': 0,
        'Resistance_Measurement': 0,
        'Accelerated_Aging': 0
    }
    
    for channel_key in processed_channels:
        categories = data['channels'][channel_key]['cycle_list']
        for category, indices in categories.items():
            total_stats[category] += len(indices)
    
    print("\n전체 카테고리별 사이클 수:")
    for category, count in total_stats.items():
        if count > 0:
            print(f"  - {category}: {count}개")
    
    print("\n✅ 전체 카테고리화 완료!")
    print("="*80)
    
    return data


def print_channel_categorization(data, channel_index=0):
    """
    특정 채널의 카테고리화 결과 상세 출력
    
    Parameters:
    -----------
    data : dict
        categorize_all_channels()의 출력 (data 객체)
    channel_index : int
        출력할 채널 인덱스 (기본값: 0)
    """
    
    channel_keys = list(data['channels'].keys())
    
    if channel_index >= len(channel_keys):
        raise ValueError(f"채널 인덱스 {channel_index}가 범위를 벗어났습니다. (최대: {len(channel_keys)-1})")
    
    channel_key = channel_keys[channel_index]
    channel_data = data['channels'][channel_key]
    
    if 'cycle_list' not in channel_data:
        raise ValueError(f"채널 {channel_key}에 cycle_list가 없습니다. categorize_all_channels()를 먼저 실행하세요.")
    
    print(f"\n{'='*80}")
    print(f"📊 [{channel_key}] 카테고리화 상세 결과")
    print('='*80)
    
    categories = channel_data['cycle_list']
    profile = channel_data['profile']
    
    for category, indices in categories.items():
        print(f"\n{category}: {len(indices)}개 사이클")
        if indices:
            first_cycle = profile[indices[0]]
            print(f"  첫 번째 사이클 인덱스: {indices[0]}")
            print(f"  첫 번째 사이클 shape: {first_cycle.shape}")
            print(f"  인덱스 리스트: {indices[:5]}{'...' if len(indices) > 5 else ''}")


def get_category_cycles(data, channel_index=0, category='RPT'):
    """
    특정 채널의 특정 카테고리 사이클 가져오기
    
    Parameters:
    -----------
    data : dict
        categorize_all_channels()의 출력 (data 객체)
    channel_index : int
        채널 인덱스
    category : str
        카테고리 이름 ('Unknown', 'RPT', 'SOC_Definition', 'Resistance_Measurement', 'Accelerated_Aging')
    
    Returns:
    --------
    list : 해당 카테고리의 사이클 DataFrame 리스트
    """
    
    channel_keys = list(data['channels'].keys())
    
    if channel_index >= len(channel_keys):
        raise ValueError(f"채널 인덱스 {channel_index}가 범위를 벗어났습니다. (최대: {len(channel_keys)-1})")
    
    channel_key = channel_keys[channel_index]
    channel_data = data['channels'][channel_key]
    
    if 'cycle_list' not in channel_data:
        raise ValueError(f"채널 {channel_key}에 cycle_list가 없습니다. categorize_all_channels()를 먼저 실행하세요.")
    
    categories = channel_data['cycle_list']
    
    if category not in categories:
        raise ValueError(f"카테고리 '{category}'가 존재하지 않습니다. 사용 가능: {list(categories.keys())}")
    
    # 인덱스를 사용하여 profile에서 실제 DataFrame 가져오기
    indices = categories[category]
    profile = channel_data['profile']
    
    return [profile[i] for i in indices]


def get_category_indices(data, channel_index=0, category='RPT'):
    """
    특정 채널의 특정 카테고리 사이클 인덱스 가져오기
    
    Parameters:
    -----------
    data : dict
        categorize_all_channels()의 출력 (data 객체)
    channel_index : int
        채널 인덱스
    category : str
        카테고리 이름
    
    Returns:
    --------
    list : 해당 카테고리의 사이클 인덱스 리스트
    """
    
    channel_keys = list(data['channels'].keys())
    
    if channel_index >= len(channel_keys):
        raise ValueError(f"채널 인덱스 {channel_index}가 범위를 벗어났습니다. (최대: {len(channel_keys)-1})")
    
    channel_key = channel_keys[channel_index]
    channel_data = data['channels'][channel_key]
    
    if 'cycle_list' not in channel_data:
        raise ValueError(f"채널 {channel_key}에 cycle_list가 없습니다. categorize_all_channels()를 먼저 실행하세요.")
    
    categories = channel_data['cycle_list']
    
    if category not in categories:
        raise ValueError(f"카테고리 '{category}'가 존재하지 않습니다. 사용 가능: {list(categories.keys())}")
    
    return categories[category]
