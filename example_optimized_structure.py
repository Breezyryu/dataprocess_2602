"""
최적화된 데이터 구조 사용 예시
- profile의 각 사이클 DataFrame에 'category' 컬럼 추가
- cycle_list에는 카테고리별 인덱스만 저장 (데이터 중복 방지)
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
print("🔋 최적화된 데이터 구조 사용 예시")
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

# 4. 최적화된 데이터 구조 확인
print("\n" + "=" * 80)
print("📊 최적화된 데이터 구조 확인")
print("=" * 80)

# 첫 번째 채널 가져오기
channel_key = list(data['channels'].keys())[0]
print(f"\n채널: {channel_key}")

# 데이터 구조 확인
channel_data = data['channels'][channel_key]
profile = channel_data['profile']
cycle_list = channel_data['cycle_list']

print(f"\n✅ 데이터 구조:")
print(f"   - profile: {len(profile)}개 사이클 DataFrame")
print(f"   - cycle_list: 카테고리별 인덱스 딕셔너리")
print(f"   - 카테고리 키: {list(cycle_list.keys())}")

# 각 카테고리별 인덱스 수 출력
print(f"\n📋 카테고리별 인덱스 수:")
for category, indices in cycle_list.items():
    print(f"   - {category}: {len(indices)}개 인덱스")

# 5. category 컬럼 확인
print("\n" + "=" * 80)
print("🏷️ Profile에 추가된 'category' 컬럼 확인")
print("=" * 80)

# 첫 번째 사이클 확인
first_cycle = profile[0]
print(f"\n첫 번째 사이클 (인덱스 0):")
print(f"   - Shape: {first_cycle.shape}")
print(f"   - Columns: {list(first_cycle.columns)}")
if 'category' in first_cycle.columns:
    print(f"   - Category: {first_cycle['category'].iloc[0]}")
    print(f"   ✅ 'category' 컬럼이 추가되었습니다!")

# 6. 카테고리별 접근 방법
print("\n" + "=" * 80)
print("🎯 카테고리별 접근 방법")
print("=" * 80)

# 방법 1: 인덱스를 사용하여 직접 접근
print("\n[방법 1] 인덱스를 사용하여 직접 접근:")
rpt_indices = cycle_list['RPT']
print(f"   RPT 인덱스: {rpt_indices}")
if rpt_indices:
    rpt_cycles = [profile[i] for i in rpt_indices]
    print(f"   RPT 사이클: {len(rpt_cycles)}개")
    print(f"   첫 번째 RPT 사이클 shape: {rpt_cycles[0].shape}")

# 방법 2: 헬퍼 함수 사용 (인덱스만)
print("\n[방법 2] get_category_indices() 함수 사용:")
rpt_indices_helper = channel_categorizer.get_category_indices(data, channel_index=0, category='RPT')
print(f"   RPT 인덱스: {rpt_indices_helper}")

# 방법 3: 헬퍼 함수 사용 (DataFrame 리스트)
print("\n[방법 3] get_category_cycles() 함수 사용:")
rpt_cycles_helper = channel_categorizer.get_category_cycles(data, channel_index=0, category='RPT')
print(f"   RPT 사이클: {len(rpt_cycles_helper)}개")

# 방법 4: category 컬럼으로 필터링
print("\n[방법 4] category 컬럼으로 필터링:")
rpt_cycles_filtered = [cycle for cycle in profile if 'category' in cycle.columns and cycle['category'].iloc[0] == 'RPT']
print(f"   RPT 사이클: {len(rpt_cycles_filtered)}개")

# 7. 메모리 효율성 확인
print("\n" + "=" * 80)
print("💾 메모리 효율성 확인")
print("=" * 80)

import sys

# profile 크기
profile_size = sys.getsizeof(profile)
print(f"\nprofile 리스트 크기: {profile_size:,} bytes")

# cycle_list 크기 (인덱스만)
cycle_list_size = sys.getsizeof(cycle_list)
for indices in cycle_list.values():
    cycle_list_size += sys.getsizeof(indices)
print(f"cycle_list 딕셔너리 크기: {cycle_list_size:,} bytes")

print(f"\n✅ cycle_list는 인덱스만 저장하므로 메모리 효율적입니다!")
print(f"   (DataFrame 복사본을 저장했다면 훨씬 더 큰 메모리를 사용했을 것입니다)")

print("\n" + "=" * 80)
print("✅ 예시 완료!")
print("=" * 80)

# 8. 사용 방법 요약
print("\n" + "=" * 80)
print("📝 사용 방법 요약")
print("=" * 80)
print("""
최적화된 데이터 구조:
    1. profile: 모든 사이클 DataFrame 리스트 (각 DataFrame에 'category' 컬럼 추가)
       data['channels'][channel_key]['profile'][i]['category']
    
    2. cycle_list: 카테고리별 인덱스 딕셔너리
       data['channels'][channel_key]['cycle_list'] = {
           'Unknown': [0, 1, 2, ...],
           'RPT': [3, 4, ...],
           'SOC_Definition': [5, 6, ...],
           'Resistance_Measurement': [7, 8, ...],
           'Accelerated_Aging': [9, 10, ...]
       }

카테고리별 사이클 접근 방법:

1. 인덱스로 직접 접근:
   indices = data['channels'][channel_key]['cycle_list']['RPT']
   rpt_cycles = [data['channels'][channel_key]['profile'][i] for i in indices]

2. 헬퍼 함수 - 인덱스만:
   indices = channel_categorizer.get_category_indices(data, channel_index=0, category='RPT')

3. 헬퍼 함수 - DataFrame 리스트:
   rpt_cycles = channel_categorizer.get_category_cycles(data, channel_index=0, category='RPT')

4. category 컬럼으로 필터링:
   profile = data['channels'][channel_key]['profile']
   rpt_cycles = [cycle for cycle in profile if cycle['category'].iloc[0] == 'RPT']

5. 특정 사이클 접근:
   first_rpt_idx = data['channels'][channel_key]['cycle_list']['RPT'][0]
   first_rpt_cycle = data['channels'][channel_key]['profile'][first_rpt_idx]

장점:
✅ 데이터 중복 없음 (메모리 효율적)
✅ profile에 category 정보 포함 (DataFrame 자체에 메타데이터)
✅ cycle_list로 빠른 카테고리별 접근
✅ 유연한 접근 방법 제공
""")
