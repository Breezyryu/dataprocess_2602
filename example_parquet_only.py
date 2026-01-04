# ============================================================================
# Parquet 사용 예제 (tables 패키지 없이 사용 가능)
# ============================================================================

import data_combiner
import data_storage
import importlib

# 모듈 재로딩
importlib.reload(data_storage)

print("="*80)
print("💾 Parquet 저장/로드 예제 (tables 패키지 불필요)")
print("="*80)

# paths 정의
paths = [
    r"C:\Users\Ryu\Python_project\data\dataprocess\Rawdata\A1_MP1_4500mAh_T23_1"
]

# ============================================================================
# 1. 데이터 로드
# ============================================================================

print("\n[1단계] 데이터 로드")
data = data_combiner.process_and_combine(paths)

print(f"\nMetadata:")
print(f"  - 총 채널 수: {data['metadata']['total_channels']}")
print(f"  - Cycler 타입: {data['metadata']['cycler_types']}")

# ============================================================================
# 2. Parquet으로 저장 (자동 파일명)
# ============================================================================

print("\n[2단계] Parquet으로 저장")
saved_dir = data_storage.save_to_parquet(data)
print(f"저장 완료: {saved_dir}")

# ============================================================================
# 3. Parquet에서 로드
# ============================================================================

print("\n[3단계] Parquet에서 로드")
loaded_data = data_storage.load_from_parquet(saved_dir)

print(f"\n로드 성공!")
print(f"  - 채널 수: {loaded_data['metadata']['total_channels']}")
print(f"  - Cycler 타입: {loaded_data['metadata']['cycler_types']}")

# 첫 번째 채널 확인
if loaded_data['channels']:
    channel_key = list(loaded_data['channels'].keys())[0]
    channel_data = loaded_data['channels'][channel_key]
    print(f"\n첫 번째 채널: {channel_key}")
    print(f"  - Cycler: {channel_data['cycler_type']}")
    if channel_data['cycle'] is not None:
        print(f"  - Cycle 데이터: {len(channel_data['cycle'])}행")
    if channel_data['profile'] is not None:
        print(f"  - Profile 데이터: {len(channel_data['profile'])}행")

# ============================================================================
# 4. 저장 정보 확인
# ============================================================================

print("\n[4단계] 저장 정보 확인")
data_storage.get_storage_info(saved_dir)

print("\n" + "="*80)
print("✅ Parquet 사용 완료!")
print("="*80)

print("\n💡 Parquet 장점:")
print("  - ✅ tables 패키지 불필요")
print("  - ✅ Python 3.14 완벽 호환")
print("  - ✅ 가독성 높은 디렉토리 구조")
print("  - ✅ 빠른 컬럼 기반 I/O")

print("\n💡 실제 사용:")
print("  # 저장")
print("  saved_dir = data_storage.save_to_parquet(data)")
print("")
print("  # 로드")
print("  data = data_storage.load_from_parquet(saved_dir)")
