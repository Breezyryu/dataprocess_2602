"""
새로운 데이터 구조 사용 예시
categorize_all_channels() 함수가 data 구조에 직접 카테고리별 cycle_list를 저장합니다.
"""

import data_combiner
import cycle_list_processor
import channel_categorizer
import importlib

# 모듈 재로딩
importlib.reload(data_combiner)
importlib.reload(cycle_list_processor)
importlib.reload(channel_categorizer)

# 데이터 로드
paths = [
    r"C:\Users\Ryu\Python_project\data\dataprocess\Rawdata\A1_MP1_4500mAh_T23_1",
]

print("=" * 80)
print("🔋 새로운 데이터 구조 사용 예시")
print("=" * 80)

# 1. 데이터 로드
print("\n[1단계] 데이터 로드")
data = data_combiner.process_and_combine(paths)

# 2. Cycle List 처리
print("\n[2단계] Cycle List 처리")
data = cycle_list_processor.process_all_channels(data)

# 3. 채널 카테고리화
print("\n[3단계] 채널 카테고리화")
data = channel_categorizer.categorize_all_channels(data)

# 4. 새로운 데이터 구조 확인
print("\n" + "=" * 80)
print("📊 새로운 데이터 구조 확인")
print("=" * 80)

# 첫 번째 채널 가져오기
channel_key = list(data['channels'].keys())[0]
print(f"\n채널: {channel_key}")

# cycle_list 구조 확인
if 'cycle_list' in data['channels'][channel_key]:
    cycle_list = data['channels'][channel_key]['cycle_list']
    print(f"\n✅ cycle_list 딕셔너리가 생성되었습니다!")
    print(f"   카테고리 키: {list(cycle_list.keys())}")
    
    # 각 카테고리별 사이클 수 출력
    print(f"\n📋 카테고리별 사이클 수:")
    for category, cycles in cycle_list.items():
        print(f"   - {category}: {len(cycles)}개")
    
    # 5. 카테고리별 접근 예시
    print("\n" + "=" * 80)
    print("🎯 카테고리별 접근 예시")
    print("=" * 80)
    
    # RPT 사이클만 가져오기
    if 'RPT' in cycle_list and len(cycle_list['RPT']) > 0:
        rpt_cycles = cycle_list['RPT']
        print(f"\n✅ RPT 사이클: {len(rpt_cycles)}개")
        print(f"   첫 번째 RPT 사이클 shape: {rpt_cycles[0].shape}")
        print(f"   첫 번째 RPT 사이클 컬럼: {list(rpt_cycles[0].columns)}")
    
    # Accelerated_Aging 사이클만 가져오기
    if 'Accelerated_Aging' in cycle_list and len(cycle_list['Accelerated_Aging']) > 0:
        aging_cycles = cycle_list['Accelerated_Aging']
        print(f"\n✅ Accelerated_Aging 사이클: {len(aging_cycles)}개")
        print(f"   첫 번째 Aging 사이클 shape: {aging_cycles[0].shape}")
    
    # 6. 헬퍼 함수 사용 예시
    print("\n" + "=" * 80)
    print("🛠️ 헬퍼 함수 사용 예시")
    print("=" * 80)
    
    # get_category_cycles 함수 사용
    print("\n[방법 1] get_category_cycles() 함수 사용:")
    rpt_cycles_helper = channel_categorizer.get_category_cycles(data, channel_index=0, category='RPT')
    print(f"   RPT 사이클: {len(rpt_cycles_helper)}개")
    
    # 직접 접근
    print("\n[방법 2] 직접 접근:")
    rpt_cycles_direct = data['channels'][channel_key]['cycle_list']['RPT']
    print(f"   RPT 사이클: {len(rpt_cycles_direct)}개")
    
    print("\n✅ 두 방법 모두 동일한 결과!")
    
else:
    print("\n❌ cycle_list가 생성되지 않았습니다!")

print("\n" + "=" * 80)
print("✅ 예시 완료!")
print("=" * 80)

# 7. 사용 방법 요약
print("\n" + "=" * 80)
print("📝 사용 방법 요약")
print("=" * 80)
print("""
새로운 데이터 구조:
    data['channels'][channel_key]['cycle_list'] = {
        'Unknown': [cycle_df, cycle_df, ...],
        'RPT': [cycle_df, cycle_df, ...],
        'SOC_Definition': [cycle_df, cycle_df, ...],
        'Resistance_Measurement': [cycle_df, cycle_df, ...],
        'Accelerated_Aging': [cycle_df, cycle_df, ...]
    }

카테고리별 사이클 접근 방법:

1. 직접 접근:
   rpt_cycles = data['channels'][channel_key]['cycle_list']['RPT']

2. 헬퍼 함수 사용:
   rpt_cycles = channel_categorizer.get_category_cycles(data, channel_index=0, category='RPT')

3. 특정 사이클 가져오기:
   first_rpt_cycle = data['channels'][channel_key]['cycle_list']['RPT'][0]

4. 모든 카테고리 순회:
   for category, cycles in data['channels'][channel_key]['cycle_list'].items():
       print(f"{category}: {len(cycles)}개")
""")
