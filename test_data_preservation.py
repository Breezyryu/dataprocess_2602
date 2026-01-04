"""
수정된 함수들이 원본 데이터를 훼손하지 않는지 테스트
"""

import data_combiner
import cycle_list_processor
import channel_categorizer
import importlib

# 모듈 재로딩
importlib.reload(data_combiner)
importlib.reload(cycle_list_processor)
importlib.reload(channel_categorizer)

# 테스트 데이터 로드
paths = [
    r"C:\Users\Ryu\Python_project\data\dataprocess\Rawdata\A1_MP1_4500mAh_T23_1",
]

print("=" * 80)
print("🧪 원본 데이터 보존 테스트")
print("=" * 80)

# 1. 데이터 로드
print("\n[1단계] 데이터 로드")
data_original = data_combiner.process_and_combine(paths)

# 원본 데이터의 ID 저장
original_data_id = id(data_original)
original_channel_ids = {k: id(v['profile']) for k, v in data_original['channels'].items()}

print(f"✓ 원본 data 객체 ID: {original_data_id}")
print(f"✓ 원본 채널 수: {len(data_original['channels'])}")

# 2. Cycle List 처리
print("\n[2단계] Cycle List 처리")
data_processed = cycle_list_processor.process_all_channels(data_original)

# 데이터 ID 비교
processed_data_id = id(data_processed)
print(f"\n📊 ID 비교:")
print(f"  - 원본 data ID: {original_data_id}")
print(f"  - 처리된 data ID: {processed_data_id}")
print(f"  - 동일한 객체? {original_data_id == processed_data_id}")

# 원본 데이터가 수정되었는지 확인
print(f"\n📊 원본 데이터 상태 확인:")
for channel_key, channel_data in data_original['channels'].items():
    profile = channel_data['profile']
    is_list = isinstance(profile, list)
    print(f"  - {channel_key}: profile이 list로 변환됨? {is_list}")
    if not is_list:
        print(f"    ✅ 원본 보존됨! (DataFrame 유지)")
    else:
        print(f"    ❌ 원본 훼손됨! (list로 변환됨)")

# 3. 채널 카테고리화
print("\n[3단계] 채널 카테고리화")
results = channel_categorizer.categorize_all_channels(data_processed)

# 처리된 데이터가 수정되었는지 확인
print(f"\n📊 처리된 데이터 상태 확인:")
for channel_key, channel_data in data_processed['channels'].items():
    cycle_list = channel_data['profile']
    if isinstance(cycle_list, list) and len(cycle_list) > 0:
        has_category = 'category' in cycle_list[0].columns
        print(f"  - {channel_key}: cycle_list에 'category' 컬럼 추가됨? {has_category}")
        if not has_category:
            print(f"    ✅ 원본 보존됨! (category 컬럼 없음)")
        else:
            print(f"    ❌ 원본 훼손됨! (category 컬럼 추가됨)")

# 4. 결과 확인
print(f"\n📊 결과 데이터 상태 확인:")
for channel_key, result in results.items():
    cycle_list = result['cycle_list']
    if isinstance(cycle_list, list) and len(cycle_list) > 0:
        has_category = 'category' in cycle_list[0].columns
        print(f"  - {channel_key}: cycle_list에 'category' 컬럼 있음? {has_category}")
        if has_category:
            print(f"    ✅ 결과에 category 추가됨!")
        else:
            print(f"    ❌ 결과에 category 없음!")

print("\n" + "=" * 80)
print("✅ 테스트 완료!")
print("=" * 80)
