# ============================================================================
# SOC_Definition 패턴 상세 분석
# ============================================================================

import pandas as pd

print("="*80)
print("🔍 SOC_Definition 패턴 분석")
print("="*80)

# Ground Truth SOC_Definition 사이클
soc_cycles = [2, 102, 202, 301, 401]

print("\nGround Truth SOC_Definition 인덱스:")
print(soc_cycles)

# 인덱스 패턴 분석
print("\n인덱스 패턴 분석:")
for idx in soc_cycles:
    mod_100 = idx % 100
    print(f"  cycle {idx}: {idx} % 100 = {mod_100}")

# 제외된 사이클 501
print(f"\n제외된 cycle 501: 501 % 100 = {501 % 100}")

# 패턴 규칙 추출
print("\n패턴 규칙:")
print("  - cycle_index % 100 == 2 (2, 102, 202)")
print("  - cycle_index % 100 == 1 (301, 401)")
print("  - 단, cycle_index < 500")

print("\n또는:")
print("  - cycle_index in [2, 102, 202, 301, 401]")

# ============================================================================
# 다른 카테고리와의 인덱스 패턴 비교
# ============================================================================

print("\n" + "="*80)
print("📊 모든 카테고리의 인덱스 패턴")
print("="*80)

patterns = {
    'Unknown': [0, 600],
    'RPT': [1, 101, 201, 300, 400, 500],
    'SOC_Definition': [2, 102, 202, 301, 401],
    'Resistance_Measurement': [3, 103, 203, 302, 402, 502],
}

for category, indices in patterns.items():
    print(f"\n[{category}]")
    print(f"  인덱스: {indices}")
    if indices:
        mods = [idx % 100 for idx in indices]
        print(f"  % 100: {mods}")
        print(f"  범위: {min(indices)} ~ {max(indices)}")

# ============================================================================
# 500번대 패턴 분석
# ============================================================================

print("\n" + "="*80)
print("🔍 500번대 패턴 분석")
print("="*80)

cycle_500_range = [500, 501, 502, 503]
for idx in cycle_500_range:
    if idx < len(cycle_list):
        import cycle_categorizer
        import importlib
        importlib.reload(cycle_categorizer)
        
        category = cycle_categorizer.categorize_cycle(cycle_list[idx], idx)
        
        # 특성 확인
        c = cycle_list[idx]
        n_points = len(c)
        voltage_range = c['Voltage_V'].max() - c['Voltage_V'].min()
        endstate_78_ratio = (c['EndState'] == 78).sum() / n_points
        
        print(f"\ncycle {idx}:")
        print(f"  자동 분류: {category}")
        print(f"  n_points: {n_points}")
        print(f"  voltage_range: {voltage_range:.1f}")
        print(f"  endstate_78_ratio: {endstate_78_ratio:.3f}")

# ============================================================================
# 제안: 하이브리드 접근
# ============================================================================

print("\n" + "="*80)
print("💡 제안: 하이브리드 분류 규칙")
print("="*80)

print("\n[방법 1] 인덱스 범위 제약 추가")
print("  - SOC_Definition: endstate_78_ratio > 0.5 AND cycle_index < 500")
print("  - 장점: 간단, 명확")
print("  - 단점: 인덱스 의존성 추가")

print("\n[방법 2] 명시적 인덱스 리스트")
print("  - SOC_Definition: cycle_index in [2, 102, 202, 301, 401]")
print("  - 장점: 100% 정확도 보장")
print("  - 단점: 완전 인덱스 기반")

print("\n[방법 3] 데이터 특성 + 인덱스 패턴")
print("  - SOC_Definition: endstate_78_ratio > 0.5 AND (cycle_index % 100 in [1, 2]) AND cycle_index < 500")
print("  - 장점: 데이터 특성 유지하면서 패턴 활용")
print("  - 단점: 복잡")

print("\n" + "="*80)
print("✅ 분석 완료!")
print("="*80)
