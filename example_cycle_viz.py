# ============================================================================
# Cycle-Level 시각화 - 간단한 함수 호출 방식
# ============================================================================

import cycle_metrics_visualizer
import matplotlib.pyplot as plt

# ============================================================================
# 1. 개별 채널 분석
# ============================================================================

# PNE 채널 분석
for i, (channel_key, df_cycle) in enumerate(loaded_data['pne_cycle'].items(), 1):
    print(f"[{i}] {channel_key}")
    cycle_metrics_visualizer.plot_cycle_metrics(df_cycle, channel_key)
    plt.show()

# Toyo 채널 분석 (있는 경우)
if loaded_data.get('toyo_cycle'):
    for i, (channel_key, df_cycle) in enumerate(loaded_data['toyo_cycle'].items(), 1):
        print(f"[{i}] {channel_key}")
        cycle_metrics_visualizer.plot_cycle_metrics(df_cycle, channel_key)
        plt.show()

# ============================================================================
# 2. 전체 채널 비교
# ============================================================================

# 용량 비교
cycle_metrics_visualizer.plot_all_channels_comparison(loaded_data, 'capacity_mAh')
plt.show()

# 용량 보존율
cycle_metrics_visualizer.plot_capacity_retention(loaded_data)
plt.show()

# 효율 비교 (선택)
cycle_metrics_visualizer.plot_all_channels_comparison(loaded_data, 'efficiency_%')
plt.show()
