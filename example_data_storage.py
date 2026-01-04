# ============================================================================
# 배터리 데이터 저장 및 로드 예제
# ============================================================================

import data_combiner
import data_storage
import importlib

# 모듈 재로딩
importlib.reload(data_storage)

# ============================================================================
# 1. 데이터 로드 및 저장
# ============================================================================

print("="*80)
print("💾 배터리 데이터 저장 예제")
print("="*80)

# paths 정의
paths = [
    r"C:\Users\Ryu\Python_project\data\dataprocess\Rawdata\A1_MP1_4500mAh_T23_1"
]

# 데이터 로드
print("\n[1단계] 원본 데이터 로드")
data = data_combiner.process_and_combine(paths)

# ============================================================================
# 2. HDF5로 저장 (권장)
# ============================================================================

print("\n[2단계] HDF5로 저장")
hdf5_path = 'battery_data.h5'
data_storage.save_to_hdf5(data, hdf5_path)

# ============================================================================
# 3. Parquet으로 저장 (대안)
# ============================================================================

print("\n[3단계] Parquet으로 저장")
parquet_dir = 'battery_data_parquet'
data_storage.save_to_parquet(data, parquet_dir)

# ============================================================================
# 4. 저장된 데이터 정보 확인
# ============================================================================

print("\n[4단계] 저장된 데이터 정보")
data_storage.get_storage_info(hdf5_path)
data_storage.get_storage_info(parquet_dir)

# ============================================================================
# 5. HDF5에서 로드
# ============================================================================

print("\n[5단계] HDF5에서 로드")
loaded_data_hdf5 = data_storage.load_from_hdf5(hdf5_path)

print(f"\n로드된 데이터 확인:")
print(f"  - 총 채널 수: {loaded_data_hdf5['metadata']['total_channels']}")
print(f"  - Cycler 타입: {loaded_data_hdf5['metadata']['cycler_types']}")

# 첫 번째 채널 확인
if loaded_data_hdf5['channels']:
    channel_key = list(loaded_data_hdf5['channels'].keys())[0]
    channel_data = loaded_data_hdf5['channels'][channel_key]
    print(f"\n첫 번째 채널: {channel_key}")
    print(f"  - Cycler: {channel_data['cycler_type']}")
    if channel_data['cycle'] is not None:
        print(f"  - Cycle 데이터: {len(channel_data['cycle'])}행")
    if channel_data['profile'] is not None:
        print(f"  - Profile 데이터: {len(channel_data['profile'])}행")

# ============================================================================
# 6. Parquet에서 로드
# ============================================================================

print("\n[6단계] Parquet에서 로드")
loaded_data_parquet = data_storage.load_from_parquet(parquet_dir)

print(f"\n로드된 데이터 확인:")
print(f"  - 총 채널 수: {loaded_data_parquet['metadata']['total_channels']}")

# ============================================================================
# 7. 속도 비교 (선택사항)
# ============================================================================

print("\n[7단계] 저장/로드 속도 비교")

import time

# HDF5 저장 속도
start = time.time()
data_storage.save_to_hdf5(data, 'test_hdf5.h5')
hdf5_save_time = time.time() - start

# HDF5 로드 속도
start = time.time()
_ = data_storage.load_from_hdf5('test_hdf5.h5')
hdf5_load_time = time.time() - start

# Parquet 저장 속도
start = time.time()
data_storage.save_to_parquet(data, 'test_parquet')
parquet_save_time = time.time() - start

# Parquet 로드 속도
start = time.time()
_ = data_storage.load_from_parquet('test_parquet')
parquet_load_time = time.time() - start

print(f"\n속도 비교:")
print(f"  HDF5   - 저장: {hdf5_save_time:.2f}초, 로드: {hdf5_load_time:.2f}초")
print(f"  Parquet - 저장: {parquet_save_time:.2f}초, 로드: {parquet_load_time:.2f}초")

# ============================================================================
# 정리
# ============================================================================

print("\n" + "="*80)
print("✅ 예제 완료!")
print("="*80)

print("\n💡 사용 권장사항:")
print("  - 빠른 I/O 필요: HDF5 사용 (.h5)")
print("  - 가독성 중요: Parquet 사용 (디렉토리)")
print("  - 일반적으로 HDF5 권장 (속도 + 압축)")

print("\n💡 실제 사용 예시:")
print("  # 저장")
print("  data = data_combiner.process_and_combine(paths)")
print("  data_storage.save_to_hdf5(data, 'my_battery_data.h5')")
print("")
print("  # 로드")
print("  data = data_storage.load_from_hdf5('my_battery_data.h5')")
print("  # 바로 사용 가능!")
