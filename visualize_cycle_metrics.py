# ============================================================================
# Cycle-Level 지표 시각화
# ============================================================================

import cycle_metrics_visualizer
import importlib

# 모듈 재로딩
importlib.reload(cycle_metrics_visualizer)

print("="*80)
print("📊 Cycle-Level 지표 시각화")
print("="*80)

# ============================================================================
# 1. 각 채널별 개별 시각화 (자동 순회)
# ============================================================================

print("\n[1] 각 채널별 상세 분석")
print("-"*80)

# PNE Cycle 데이터
if loaded_data['pne_cycle']:
    pne_channels = list(loaded_data['pne_cycle'].items())
    print(f"PNE 채널 수: {len(pne_channels)}개")
    
    for i, (channel_key, df_cycle) in enumerate(pne_channels, 1):
        print(f"\n[{i}/{len(pne_channels)}] 시각화 중: {channel_key}")
        fig = cycle_metrics_visualizer.plot_cycle_metrics(df_cycle, channel_key)
        if fig:
            plt.show()

# Toyo Cycle 데이터
if loaded_data['toyo_cycle']:
    toyo_channels = list(loaded_data['toyo_cycle'].items())
    print(f"\nToyo 채널 수: {len(toyo_channels)}개")
    
    for i, (channel_key, df_cycle) in enumerate(toyo_channels, 1):
        print(f"\n[{i}/{len(toyo_channels)}] 시각화 중: {channel_key}")
        fig = cycle_metrics_visualizer.plot_cycle_metrics(df_cycle, channel_key)
        if fig:
            plt.show()

# ============================================================================
# 2. 전체 채널 용량 비교
# ============================================================================

print("\n[2] 전체 채널 용량 비교")
print("-"*80)

capacity_fig = cycle_metrics_visualizer.plot_all_channels_comparison(
    loaded_data, metric='capacity_mAh'
)
plt.show()

# ============================================================================
# 3. 전체 채널 용량 보존율 (Capacity Retention)
# ============================================================================

print("\n[3] 전체 채널 용량 보존율")
print("-"*80)

retention_fig = cycle_metrics_visualizer.plot_capacity_retention(loaded_data)
plt.show()

# ============================================================================
# 4. 전체 채널 효율 비교 (선택사항)
# ============================================================================

print("\n[4] 전체 채널 효율 비교 (선택사항)")
print("-"*80)

efficiency_fig = cycle_metrics_visualizer.plot_all_channels_comparison(
    loaded_data, metric='efficiency_%'
)
plt.show()

print("\n" + "="*80)
print("✅ Cycle-Level 시각화 완료!")
print("="*80)

print("\n💡 사용 가능한 함수:")
print("  1. plot_cycle_metrics(df_cycle, channel_name)")
print("     - 단일 채널의 모든 지표 시각화")
print("  ")
print("  2. plot_all_channels_comparison(loaded_data, metric)")
print("     - 모든 채널의 특정 지표 비교")
print("     - metric: 'capacity_mAh', 'efficiency_%', 'Voltage_V' 등")
print("  ")
print("  3. plot_capacity_retention(loaded_data)")
print("     - 모든 채널의 용량 보존율 비교")
