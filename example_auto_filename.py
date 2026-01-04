# ============================================================================
# 자동 파일명 생성 예제
# ============================================================================

import data_combiner
import data_storage
import importlib

# 모듈 재로딩
importlib.reload(data_storage)

print("="*80)
print("💾 자동 파일명 생성 저장 예제")
print("="*80)

# paths 정의
paths = [
    r"C:\Users\Ryu\Python_project\data\dataprocess\Rawdata\A1_MP1_4500mAh_T23_1"
]

# 데이터 로드
print("\n[1단계] 데이터 로드")
data = data_combiner.process_and_combine(paths)

print(f"\nMetadata:")
print(f"  - Cycler 타입: {data['metadata']['cycler_types']}")
print(f"  - Path: {data['metadata']['paths'][0]}")
print(f"  - 폴더명: {os.path.basename(data['metadata']['paths'][0])}")

# ============================================================================
# 방법 1: 자동 파일명 생성 (권장)
# ============================================================================

print("\n" + "="*80)
print("방법 1: 자동 파일명 생성")
print("="*80)

# HDF5 - 파일명 자동 생성
saved_hdf5 = data_storage.save_to_hdf5(data)
print(f"저장된 파일: {saved_hdf5}")

# Parquet - 디렉토리명 자동 생성
saved_parquet = data_storage.save_to_parquet(data)
print(f"저장된 디렉토리: {saved_parquet}")

# ============================================================================
# 방법 2: 수동 파일명 지정
# ============================================================================

print("\n" + "="*80)
print("방법 2: 수동 파일명 지정")
print("="*80)

# HDF5 - 수동 지정
data_storage.save_to_hdf5(data, 'my_custom_name.h5')

# Parquet - 수동 지정
data_storage.save_to_parquet(data, 'my_custom_parquet')

# ============================================================================
# 로드 테스트
# ============================================================================

print("\n" + "="*80)
print("로드 테스트")
print("="*80)

# 자동 생성된 파일 로드
loaded_data = data_storage.load_from_hdf5(saved_hdf5)
print(f"\n로드 성공!")
print(f"  - 채널 수: {loaded_data['metadata']['total_channels']}")

# ============================================================================
# 파일명 규칙
# ============================================================================

print("\n" + "="*80)
print("📝 파일명 생성 규칙")
print("="*80)

print("\n형식: {cycler_type}_{folder_name}.h5")
print("\n예시:")
print("  - PNE_A1_MP1_4500mAh_T23_1.h5")
print("  - Toyo_B2_LG_3000mAh_T25.h5")
print("  - PNE_Toyo_Mixed_Test.h5 (여러 cycler 타입)")

print("\n✅ 자동 파일명 생성으로 일관된 네이밍 규칙 유지!")
