# ============================================================================
# Cycle 데이터 구조 분석
# ============================================================================

import cycle_analyzer
import importlib

# 모듈 재로딩
importlib.reload(cycle_analyzer)

print("="*80)
print("🔬 Cycle 데이터 구조 분석")
print("="*80)

# ============================================================================
# 1. 전체 통계
# ============================================================================

cycle_analyzer.print_cycle_statistics(cycle_list)

# ============================================================================
# 2. 구조 요약 테이블
# ============================================================================

print("\n📋 Cycle 구조 요약 테이블 (처음 20개)")
print("-"*80)

cycle_summary = cycle_analyzer.analyze_cycle_structure(cycle_list)

# 처음 20개만 표시
display(cycle_summary.head(20))

print(f"\n총 {len(cycle_summary)}개 사이클")

# ============================================================================
# 3. 주요 수치 특성 분포
# ============================================================================

print("\n📊 주요 수치 특성 요약")
print("-"*80)

numeric_cols = ['Data_Points', 'Voltage_Min', 'Voltage_Max', 'Voltage_Range', 
                'Duration_s', 'Crate_Max', 'Crate_Mean']

available_cols = [col for col in numeric_cols if col in cycle_summary.columns]

if available_cols:
    stats = cycle_summary[available_cols].describe()
    display(stats)

# ============================================================================
# 4. 카테고리별 통계 (있는 경우)
# ============================================================================

if 'Category' in cycle_summary.columns:
    print("\n📈 카테고리별 평균 특성")
    print("-"*80)
    
    category_stats = cycle_summary.groupby('Category')[available_cols].mean()
    display(category_stats)

# ============================================================================
# 5. 특정 사이클 비교 (예시)
# ============================================================================

print("\n🔍 특정 사이클 비교 (0, 1, 2, 3, 4, 5)")
print("-"*80)

comparison = cycle_analyzer.analyze_cycle_differences(cycle_list, [0, 1, 2, 3, 4, 5])
display(comparison)

print("\n✅ Cycle 데이터 구조 분석 완료!")
