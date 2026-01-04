"""
모든 채널의 사이클 카테고리화 유틸리티
"""

import cycle_categorizer
import copy


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
    dict : 채널별 카테고리 분류 결과
        {
            'channel_key': {
                'categories': {...},  # categorize_cycles() 출력
                'cycle_list': [...]   # 카테고리 라벨이 추가된 cycle_list (복사본)
            },
            ...
        }
        원본 데이터는 수정되지 않음
    """
    
    print("="*80)
    print("🏷️  전체 채널 사이클 카테고리화")
    print("="*80)
    
    results = {}
    
    for channel_key, channel_data in data['channels'].items():
        print(f"\n처리 중: {channel_key}")
        
        # Profile 데이터 확인
        cycle_list_original = channel_data['profile']
        
        if not isinstance(cycle_list_original, list):
            print("  ⚠️ Cycle list가 아님 - 건너뜀")
            continue
        
        # cycle_list의 깊은 복사본 생성 (원본 보존)
        cycle_list = copy.deepcopy(cycle_list_original)
        
        # 카테고리화 수행
        categories = cycle_categorizer.categorize_cycles(cycle_list)
        
        # 각 사이클에 카테고리 라벨 추가 (복사본에만 적용)
        cycle_categorizer.add_category_labels(cycle_list, categories)
        
        # 결과 저장
        results[channel_key] = {
            'categories': categories,
            'cycle_list': cycle_list  # 복사본 저장
        }
        
        # 요약 출력
        print(f"  ✅ {len(cycle_list)}개 사이클 분류 완료")
        for category, indices in categories.items():
            if indices:
                print(f"    - {category}: {len(indices)}개")
    
    # 전체 요약
    print("\n" + "="*80)
    print("📋 카테고리화 결과 요약")
    print("="*80)
    
    total_channels = len(results)
    print(f"\n처리된 채널 수: {total_channels}개")
    
    # 카테고리별 전체 통계
    total_stats = {
        'Unknown': 0,
        'RPT': 0,
        'SOC_Definition': 0,
        'Resistance_Measurement': 0,
        'Accelerated_Aging': 0
    }
    
    for channel_result in results.values():
        for category, indices in channel_result['categories'].items():
            total_stats[category] += len(indices)
    
    print("\n전체 카테고리별 사이클 수:")
    for category, count in total_stats.items():
        if count > 0:
            print(f"  - {category}: {count}개")
    
    print("\n✅ 전체 카테고리화 완료!")
    print("="*80)
    
    return results


def print_channel_categorization(results, channel_index=0):
    """
    특정 채널의 카테고리화 결과 상세 출력
    
    Parameters:
    -----------
    results : dict
        categorize_all_channels()의 출력
    channel_index : int
        출력할 채널 인덱스 (기본값: 0)
    """
    
    channel_keys = list(results.keys())
    
    if channel_index >= len(channel_keys):
        raise ValueError(f"채널 인덱스 {channel_index}가 범위를 벗어났습니다. (최대: {len(channel_keys)-1})")
    
    channel_key = channel_keys[channel_index]
    channel_result = results[channel_key]
    
    print(f"\n{'='*80}")
    print(f"📊 [{channel_key}] 카테고리화 상세 결과")
    print('='*80)
    
    cycle_categorizer.print_categorization_report(
        channel_result['cycle_list'],
        channel_result['categories']
    )


def get_category_cycles(results, channel_index=0, category='RPT'):
    """
    특정 채널의 특정 카테고리 사이클 가져오기
    
    Parameters:
    -----------
    results : dict
        categorize_all_channels()의 출력
    channel_index : int
        채널 인덱스
    category : str
        카테고리 이름
    
    Returns:
    --------
    list : 해당 카테고리의 사이클 인덱스 리스트
    """
    
    channel_keys = list(results.keys())
    
    if channel_index >= len(channel_keys):
        raise ValueError(f"채널 인덱스 {channel_index}가 범위를 벗어났습니다. (최대: {len(channel_keys)-1})")
    
    channel_key = channel_keys[channel_index]
    categories = results[channel_key]['categories']
    
    if category not in categories:
        raise ValueError(f"카테고리 '{category}'가 존재하지 않습니다. 사용 가능: {list(categories.keys())}")
    
    return categories[category]
