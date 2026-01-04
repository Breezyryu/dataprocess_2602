# ============================================================================
# 카테고리별 전체 사이클 시각화
# ============================================================================

import plot_all_categories
import importlib

# 모듈 재로딩
importlib.reload(plot_all_categories)

print("="*80)
print("📊 카테고리별 모든 사이클 시각화 시작")
print("="*80)

# ============================================================================
# 방법 1: 모든 카테고리의 모든 사이클 플롯 (그리드 형태)
# ============================================================================

print("\n[방법 1] 카테고리별 모든 사이클 그리드 플롯")
print("-"*80)

figures = plot_all_categories.plot_all_categories(cycle_list, categories, max_cols=5)

# ============================================================================
# 방법 2: 카테고리별 대표 사이클 비교
# ============================================================================

print("\n[방법 2] 카테고리별 대표 사이클 비교")
print("-"*80)

comparison_fig = plot_all_categories.plot_category_comparison(cycle_list, categories)
plt.show()

# ============================================================================
# 방법 3: 특정 카테고리의 Voltage & Current 오버레이
# ============================================================================

print("\n[방법 3] Voltage & Current 오버레이 플롯")
print("-"*80)

# RPT 사이클 (최대 10개)
if categories['RPT']:
    print("\n📈 RPT 사이클 Voltage & Current")
    rpt_vc_fig = plot_all_categories.plot_voltage_current_overlay(
        cycle_list, categories, 'RPT', max_cycles=10
    )
    plt.show()

# SOC Definition 사이클 (전체)
if categories['SOC_Definition']:
    print("\n📈 SOC Definition 사이클 Voltage & Current")
    soc_vc_fig = plot_all_categories.plot_voltage_current_overlay(
        cycle_list, categories, 'SOC_Definition', max_cycles=10
    )
    plt.show()

# Resistance Measurement 사이클 (전체)
if categories['Resistance_Measurement']:
    print("\n📈 Resistance Measurement 사이클 Voltage & Current")
    res_vc_fig = plot_all_categories.plot_voltage_current_overlay(
        cycle_list, categories, 'Resistance_Measurement', max_cycles=10
    )
    plt.show()

# Accelerated Aging 사이클 (있는 경우)
if categories['Accelerated_Aging']:
    print("\n📈 Accelerated Aging 사이클 Voltage & Current")
    aging_vc_fig = plot_all_categories.plot_voltage_current_overlay(
        cycle_list, categories, 'Accelerated_Aging', max_cycles=10
    )
    plt.show()

# ============================================================================
# 선택사항: 플롯 저장
# ============================================================================

print("\n" + "="*80)
print("💾 플롯 저장 (선택사항)")
print("="*80)

# 저장하려면 아래 주석 해제
# plot_all_categories.save_all_plots(figures, output_dir='./category_plots')

print("\n✅ 모든 시각화 완료!")
print("="*80)
