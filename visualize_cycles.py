# ============================================================================
# Cycle List 종합 시각화
# ============================================================================

import cycle_visualizer
import importlib

# 모듈 재로딩
importlib.reload(cycle_visualizer)

print("="*80)
print("📊 Cycle List 종합 시각화")
print("="*80)

# ============================================================================
# 1. 전체 사이클 오버뷰
# ============================================================================

print("\n[1] 전체 사이클 오버뷰 (모든 사이클 겹쳐 표시)")
print("-"*80)

# 모든 사이클을 한 그래프에 겹쳐 표시
overview_fig = cycle_visualizer.plot_all_cycles_overview(cycle_list, max_cycles=None)
plt.show()

# ============================================================================
# 2. Cycle 그리드 뷰
# ============================================================================

print("\n[2] Cycle 그리드 뷰 (개별 사이클)")
print("-"*80)

# 처음 20개 사이클을 그리드로 표시
grid_fig = cycle_visualizer.plot_cycle_grid(cycle_list, indices=None, cols=4)
plt.show()

# 특정 사이클들만 표시 (예: 0, 1, 2, 3, 4, 5)
# grid_fig = cycle_visualizer.plot_cycle_grid(cycle_list, indices=[0, 1, 2, 3, 4, 5], cols=3)
# plt.show()

# ============================================================================
# 3. Voltage vs Capacity
# ============================================================================

print("\n[3] Voltage vs Capacity (배터리 특성 곡선)")
print("-"*80)

# 대표 사이클의 V-Q 곡선
vq_fig = cycle_visualizer.plot_voltage_vs_capacity(cycle_list)
plt.show()

# ============================================================================
# 4. Cycle 통계 추세
# ============================================================================

print("\n[4] Cycle 통계 추세")
print("-"*80)

# 데이터 포인트, Voltage 범위, Duration, C-rate 추세
stats_fig = cycle_visualizer.plot_cycle_statistics(cycle_list)
plt.show()

# ============================================================================
# 5. 단일 사이클 상세 분석 (선택사항)
# ============================================================================

print("\n[5] 단일 사이클 상세 분석 (예시: cycle 1)")
print("-"*80)

# cycle 1의 상세 분석
detail_fig = cycle_visualizer.plot_single_cycle_detailed(cycle_list, cycle_index=1)
plt.show()

print("\n" + "="*80)
print("✅ Cycle List 시각화 완료!")
print("="*80)

print("\n💡 사용 가능한 함수:")
print("  1. plot_all_cycles_overview(): 전체 사이클 오버뷰")
print("  2. plot_cycle_grid(): 그리드 형태 개별 사이클")
print("  3. plot_voltage_vs_capacity(): V-Q 곡선")
print("  4. plot_cycle_statistics(): 통계 추세")
print("  5. plot_single_cycle_detailed(): 단일 사이클 상세 분석")
