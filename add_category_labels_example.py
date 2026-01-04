# ============================================================================
# 각 사이클에 카테고리 라벨 추가 예제
# ============================================================================

import cycle_categorizer
import importlib

# 모듈 재로딩
importlib.reload(cycle_categorizer)

print("="*80)
print("🏷️  각 사이클에 카테고리 라벨 추가")
print("="*80)

# ============================================================================
# 1. 사이클 분류 및 라벨 추가
# ============================================================================

print("\n[1단계] 사이클 분류 및 라벨 추가")
print("-"*80)

# 분류 수행 및 각 사이클에 'category' 컬럼 추가
categories = cycle_categorizer.add_category_labels(cycle_list)

print("✅ 모든 사이클에 'category' 컬럼이 추가되었습니다.")
print(f"   - 총 {len(cycle_list)}개 사이클 처리 완료")

# ============================================================================
# 2. 라벨 확인
# ============================================================================

print("\n[2단계] 추가된 라벨 확인")
print("-"*80)

# 처음 10개 사이클의 카테고리 확인
print("\n처음 10개 사이클의 카테고리:")
for i in range(min(10, len(cycle_list))):
    category = cycle_categorizer.get_cycle_category(cycle_list[i])
    print(f"  cycle_list[{i}]: {category}")

# ============================================================================
# 3. 특정 사이클 상세 확인
# ============================================================================

print("\n[3단계] 특정 사이클 상세 확인")
print("-"*80)

# 예시: cycle_list[2] 확인
if len(cycle_list) > 2:
    cycle_2 = cycle_list[2]
    print(f"\ncycle_list[2] 정보:")
    print(f"  - 카테고리: {cycle_categorizer.get_cycle_category(cycle_2)}")
    print(f"  - 데이터 포인트 수: {len(cycle_2)}")
    print(f"  - 컬럼: {list(cycle_2.columns)}")
    print(f"\n  첫 5개 행:")
    print(cycle_2[['time_cyc', 'Voltage_V', 'Current_mA', 'category']].head())

# ============================================================================
# 4. 카테고리별 통계
# ============================================================================

print("\n[4단계] 카테고리별 통계")
print("-"*80)

for category, indices in categories.items():
    print(f"\n[{category}]")
    print(f"  - 사이클 개수: {len(indices)}")
    if indices:
        print(f"  - 사이클 인덱스: {indices[:5]}", end="")
        if len(indices) > 5:
            print(f" ... 외 {len(indices)-5}개")
        else:
            print()

# ============================================================================
# 5. DataFrame으로 요약
# ============================================================================

print("\n[5단계] 전체 사이클 카테고리 요약 테이블")
print("-"*80)

import pandas as pd

# 각 사이클의 카테고리를 DataFrame으로 정리
summary_data = []
for i, cycle in enumerate(cycle_list):
    category = cycle_categorizer.get_cycle_category(cycle)
    v_min = cycle['Voltage_V'].min()
    v_max = cycle['Voltage_V'].max()
    n_points = len(cycle)
    
    summary_data.append({
        'Cycle_Index': i,
        'Category': category,
        'Data_Points': n_points,
        'V_min': f"{v_min:.2f}",
        'V_max': f"{v_max:.2f}"
    })

summary_df = pd.DataFrame(summary_data)

print("\n전체 사이클 요약 (처음 20개):")
print(summary_df.head(20).to_string(index=False))

print(f"\n... 총 {len(summary_df)}개 사이클")

# 카테고리별 개수
print("\n카테고리별 사이클 개수:")
print(summary_df['Category'].value_counts().to_string())

print("\n" + "="*80)
print("✅ 카테고리 라벨 추가 완료!")
print("="*80)

# ============================================================================
# 6. 선택사항: 카테고리별로 사이클 필터링 예제
# ============================================================================

print("\n[선택사항] 카테고리별 필터링 예제")
print("-"*80)

# RPT 사이클만 추출
rpt_cycles = [cycle for cycle in cycle_list 
              if cycle_categorizer.get_cycle_category(cycle) == 'RPT']
print(f"\n✓ RPT 사이클: {len(rpt_cycles)}개")

# SOC Definition 사이클만 추출
soc_cycles = [cycle for cycle in cycle_list 
              if cycle_categorizer.get_cycle_category(cycle) == 'SOC_Definition']
print(f"✓ SOC Definition 사이클: {len(soc_cycles)}개")

# Resistance Measurement 사이클만 추출
res_cycles = [cycle for cycle in cycle_list 
              if cycle_categorizer.get_cycle_category(cycle) == 'Resistance_Measurement']
print(f"✓ Resistance Measurement 사이클: {len(res_cycles)}개")

# Accelerated Aging 사이클만 추출
aging_cycles = [cycle for cycle in cycle_list 
                if cycle_categorizer.get_cycle_category(cycle) == 'Accelerated_Aging']
print(f"✓ Accelerated Aging 사이클: {len(aging_cycles)}개")
