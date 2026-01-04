# ============================================================================
# paths를 입력으로 받아 데이터 로드 및 통합 DataFrame 생성
# ============================================================================

import data_combiner

# ============================================================================
# 방법 1: 한 번에 모든 처리 (권장)
# ============================================================================

print("="*80)
print("🔋 배터리 데이터 처리 및 통합 (One-Step)")
print("="*80)

# paths 정의
paths = [
    r"C:\Users\Ryu\Python_project\data\dataprocess\Rawdata\A1_MP1_4500mAh_T23_1"
]

# 한 번에 처리
df_results, loaded_data, df_combined = data_combiner.process_and_combine(paths)

print("\n✅ 처리 완료!")
print(f"  - df_results: {len(df_results)}개 경로")
print(f"  - loaded_data: {len(loaded_data)}개 채널")
print(f"  - df_combined: {len(df_combined):,}행")

# 요약 정보 출력
data_combiner.print_dataframe_summary(df_combined)

# ============================================================================
# 방법 2: 단계별 처리
# ============================================================================

print("\n" + "="*80)
print("🔋 배터리 데이터 처리 및 통합 (Step-by-Step)")
print("="*80)

import dataprocess

# 1단계: 데이터 로드
df_results, loaded_data = dataprocess.process_battery_data(paths)

# 2단계: 통합 DataFrame 생성
df_combined = data_combiner.combine_to_dataframe(loaded_data)

# 또는 Cycle만
df_cycle_only = data_combiner.get_cycle_data_only(loaded_data)

# 또는 Profile만
df_profile_only = data_combiner.get_profile_data_only(loaded_data)

print(f"\n생성된 DataFrame:")
print(f"  - df_combined: {len(df_combined):,}행 (Cycle + Profile)")
print(f"  - df_cycle_only: {len(df_cycle_only):,}행 (Cycle만)")
print(f"  - df_profile_only: {len(df_profile_only):,}행 (Profile만)")

# ============================================================================
# 데이터 사용 예시
# ============================================================================

print("\n" + "="*80)
print("💡 데이터 사용 예시")
print("="*80)

# 특정 채널 필터링
if len(df_combined) > 0:
    channel_name = df_combined['channel'].iloc[0]
    df_channel = df_combined[df_combined['channel'] == channel_name]
    print(f"\n채널 '{channel_name}' 데이터: {len(df_channel):,}행")

# Cycle 데이터만 필터링
df_cycles = df_combined[df_combined['data_type'] == 'cycle']
print(f"\nCycle 데이터: {len(df_cycles):,}행")

# PNE 데이터만 필터링
df_pne = df_combined[df_combined['cycler_type'] == 'PNE']
print(f"\nPNE 데이터: {len(df_pne):,}행")

# 채널별 그룹화
if 'channel' in df_combined.columns:
    grouped = df_combined.groupby('channel')
    print(f"\n채널별 데이터 수:")
    for channel, group in grouped:
        print(f"  - {channel}: {len(group):,}행")

print("\n✅ 예제 완료!")
