# ============================================================================
# 카테고리별 전체 사이클 시각화 (Voltage + C-rate)
# ============================================================================

import plot_all_categories
import importlib

# 모듈 재로딩
importlib.reload(plot_all_categories)

print("="*80)
print("📊 카테고리별 모든 사이클 시각화 (Voltage + C-rate)")
print("="*80)

# 모든 카테고리의 모든 사이클 플롯 (그리드 형태)
# 각 플롯에 Voltage(왼쪽 y축, 파랑)와 C-rate(오른쪽 y축, 빨강) 표시
figures = plot_all_categories.plot_all_categories(cycle_list, categories, max_cols=5)

# 카테고리별 대표 사이클 비교
# Voltage(색깔별)와 C-rate(빨강 점선) 함께 표시
comparison_fig = plot_all_categories.plot_category_comparison(cycle_list, categories)
plt.show()

print("\n✅ 시각화 완료!")
print("  - 파랑: Voltage (왼쪽 y축)")
print("  - 빨강: C-rate (오른쪽 y축)")
