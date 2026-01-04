# ============================================================================
# loaded_data를 통합 DataFrame으로 변환
# ============================================================================

import data_combiner
import importlib

# 모듈 재로딩
importlib.reload(data_combiner)

print("="*80)
print("🔄 데이터 통합 DataFrame 변환")
print("="*80)

# ============================================================================
# 방법 1: Cycle 데이터만 통합 (권장)
# ============================================================================

print("\n[방법 1] Cycle 데이터만 통합")
print("-"*80)

df_cycle_combined = data_combiner.get_cycle_data_only(loaded_data)

print(f"생성된 DataFrame 크기: {df_cycle_combined.shape}")
print(f"컬럼: {df_cycle_combined.columns.tolist()}")

# 요약 정보
data_combiner.print_dataframe_summary(df_cycle_combined)

# 처음 몇 행 확인
print("\n데이터 샘플:")
display(df_cycle_combined.head(10))

# ============================================================================
# 방법 2: Profile 데이터만 통합
# ============================================================================

print("\n[방법 2] Profile 데이터만 통합")
print("-"*80)

df_profile_combined = data_combiner.get_profile_data_only(loaded_data)

print(f"생성된 DataFrame 크기: {df_profile_combined.shape}")

# ============================================================================
# 방법 3: 모든 데이터 통합 (Cycle + Profile)
# ============================================================================

print("\n[방법 3] 모든 데이터 통합 (Cycle + Profile)")
print("-"*80)

df_all_combined = data_combiner.combine_to_dataframe(loaded_data)

print(f"생성된 DataFrame 크기: {df_all_combined.shape}")

# ============================================================================
# 사용 예시
# ============================================================================

print("\n" + "="*80)
print("💡 사용 예시")
print("="*80)

print("\n# 특정 채널 데이터 필터링")
print("channel_name = df_cycle_combined['channel'].unique()[0]")
print("df_channel = df_cycle_combined[df_cycle_combined['channel'] == channel_name]")

print("\n# 특정 사이클 범위 필터링")
print("df_cycles_0_100 = df_cycle_combined[df_cycle_combined['Cycle'] <= 100]")

print("\n# Cycler 타입별 그룹화")
print("grouped = df_cycle_combined.groupby('cycler_type')")

print("\n# 채널별 평균 용량 계산")
if 'capacity_mAh' in df_cycle_combined.columns:
    print("avg_capacity = df_cycle_combined.groupby('channel')['capacity_mAh'].mean()")

print("\n✅ 통합 DataFrame 생성 완료!")
print("\n생성된 변수:")
print("  - df_cycle_combined: Cycle 데이터 통합 DataFrame")
print("  - df_profile_combined: Profile 데이터 통합 DataFrame")
print("  - df_all_combined: 모든 데이터 통합 DataFrame")
