# ============================================================================
# 사이클 분류 검증 스크립트
# ============================================================================

import cycle_categorizer
import importlib

# 모듈 재로딩
importlib.reload(cycle_categorizer)

print("="*80)
print("🔍 사이클 분류 결과 검증")
print("="*80)

# ============================================================================
# 1. 사용자 수동 분류 결과 (Ground Truth)
# ============================================================================

print("\n[1단계] Ground Truth 정의")
print("-"*80)

ground_truth = {
    'Unknown': [0, 600],
    'RPT': [1, 101, 201, 300, 400, 500],
    'SOC_Definition': [2, 102, 202, 301, 401],
    'Resistance_Measurement': [3, 103, 203, 302, 402, 502],
    'Accelerated_Aging': (
        list(range(4, 101)) +      # 4~100
        list(range(104, 201)) +    # 104~200
        list(range(204, 300)) +    # 204~299
        list(range(303, 400)) +    # 303~399
        list(range(403, 500)) +    # 403~499
        list(range(503, 600))      # 503~599
    )
}

print("사용자 수동 분류 결과:")
for category, indices in ground_truth.items():
    print(f"  {category}: {len(indices)}개")

total_ground_truth = sum(len(indices) for indices in ground_truth.values())
print(f"\n총 사이클 수: {total_ground_truth}개")

# ============================================================================
# 2. 자동 분류 수행
# ============================================================================

print("\n[2단계] 자동 분류 수행")
print("-"*80)

categories = cycle_categorizer.categorize_cycles(cycle_list)

print("자동 분류 결과:")
for category, indices in categories.items():
    print(f"  {category}: {len(indices)}개")

total_auto = sum(len(indices) for indices in categories.values())
print(f"\n총 사이클 수: {total_auto}개")

# ============================================================================
# 3. 비교 및 검증
# ============================================================================

print("\n[3단계] Ground Truth와 비교")
print("-"*80)

all_match = True
mismatches = {}

for category in ground_truth.keys():
    expected = set(ground_truth[category])
    actual = set(categories.get(category, []))
    
    missing = expected - actual  # Ground truth에는 있지만 자동 분류에는 없음
    extra = actual - expected    # 자동 분류에는 있지만 ground truth에는 없음
    
    if expected == actual:
        print(f"✅ {category}: 완벽히 일치 ({len(expected)}개)")
    else:
        all_match = False
        print(f"❌ {category}: 불일치")
        if missing:
            print(f"   누락된 사이클: {sorted(list(missing))[:10]}", end="")
            if len(missing) > 10:
                print(f" ... 외 {len(missing)-10}개")
            else:
                print()
        if extra:
            print(f"   추가된 사이클: {sorted(list(extra))[:10]}", end="")
            if len(extra) > 10:
                print(f" ... 외 {len(extra)-10}개")
            else:
                print()
        
        mismatches[category] = {'missing': missing, 'extra': extra}

# ============================================================================
# 4. 전체 검증 결과
# ============================================================================

print("\n" + "="*80)
if all_match:
    print("🎉 검증 성공! 모든 카테고리가 Ground Truth와 100% 일치합니다.")
else:
    print("⚠️ 검증 실패: 일부 카테고리에서 불일치가 발견되었습니다.")
    print("\n불일치 상세:")
    for category, diff in mismatches.items():
        print(f"\n[{category}]")
        if diff['missing']:
            print(f"  누락: {len(diff['missing'])}개 - {sorted(list(diff['missing']))[:20]}")
        if diff['extra']:
            print(f"  추가: {len(diff['extra'])}개 - {sorted(list(diff['extra']))[:20]}")

print("="*80)

# ============================================================================
# 5. 개별 사이클 검증 (샘플)
# ============================================================================

print("\n[5단계] 개별 사이클 검증 (샘플)")
print("-"*80)

# 각 카테고리에서 샘플 확인
sample_indices = {
    'Unknown': [0, 600],
    'RPT': [1, 101, 201],
    'SOC_Definition': [2, 102, 202],
    'Resistance_Measurement': [3, 103, 203],
    'Accelerated_Aging': [4, 50, 100, 104, 200]
}

print("\n샘플 사이클 분류 결과:")
for expected_category, indices in sample_indices.items():
    print(f"\n[{expected_category}]")
    for idx in indices:
        if idx < len(cycle_list):
            actual_category = cycle_categorizer.categorize_cycle(cycle_list[idx], idx)
            match = "✅" if actual_category == expected_category else "❌"
            print(f"  {match} cycle {idx}: {actual_category}")
        else:
            print(f"  ⚠️ cycle {idx}: 존재하지 않음")

print("\n" + "="*80)
print("✅ 검증 완료!")
print("="*80)
