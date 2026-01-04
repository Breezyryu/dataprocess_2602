# ============================================================================
# 카테고리별 데이터 특성 분석 스크립트
# ============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("="*80)
print("🔬 카테고리별 데이터 특성 분석")
print("="*80)

# ============================================================================
# 1. Ground Truth 정의 (사용자 수동 분류)
# ============================================================================

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

# ============================================================================
# 2. 특성 추출 함수
# ============================================================================

def extract_features(cycle_df, cycle_index):
    """단일 사이클의 모든 특성 추출"""
    
    features = {
        'cycle_index': cycle_index,
        
        # 데이터 크기
        'n_points': len(cycle_df),
        
        # Voltage 특성
        'voltage_min': cycle_df['Voltage_V'].min(),
        'voltage_max': cycle_df['Voltage_V'].max(),
        'voltage_range': cycle_df['Voltage_V'].max() - cycle_df['Voltage_V'].min(),
        'voltage_mean': cycle_df['Voltage_V'].mean(),
        'voltage_std': cycle_df['Voltage_V'].std(),
        
        # Current 특성
        'current_min': cycle_df['Current_mA'].min(),
        'current_max': cycle_df['Current_mA'].max(),
        'current_range': cycle_df['Current_mA'].max() - cycle_df['Current_mA'].min(),
        'current_mean': cycle_df['Current_mA'].mean(),
        
        # EndState 특성
        'endstate_unique': cycle_df['EndState'].nunique(),
        'endstate_values': tuple(sorted(cycle_df['EndState'].unique())),
        'endstate_dominant': cycle_df['EndState'].mode()[0] if len(cycle_df['EndState'].mode()) > 0 else None,
        'endstate_64_ratio': (cycle_df['EndState'] == 64).sum() / len(cycle_df),
        'endstate_65_ratio': (cycle_df['EndState'] == 65).sum() / len(cycle_df),
        'endstate_66_ratio': (cycle_df['EndState'] == 66).sum() / len(cycle_df),
        'endstate_78_ratio': (cycle_df['EndState'] == 78).sum() / len(cycle_df),
        
        # Condition 특성
        'condition_unique': cycle_df['Condition'].nunique(),
        'has_charge': (cycle_df['Condition'] == 1).any(),
        'has_discharge': (cycle_df['Condition'] == 2).any(),
        'has_rest': (cycle_df['Condition'] == 3).any(),
        'charge_ratio': (cycle_df['Condition'] == 1).sum() / len(cycle_df),
        'discharge_ratio': (cycle_df['Condition'] == 2).sum() / len(cycle_df),
        'rest_ratio': (cycle_df['Condition'] == 3).sum() / len(cycle_df),
    }
    
    # C-rate 특성 (있는 경우)
    if 'Crate' in cycle_df.columns:
        features['crate_max'] = cycle_df['Crate'].abs().max()
        features['crate_mean'] = cycle_df['Crate'].abs().mean()
        features['crate_std'] = cycle_df['Crate'].abs().std()
    else:
        features['crate_max'] = None
        features['crate_mean'] = None
        features['crate_std'] = None
    
    return features

# ============================================================================
# 3. 각 카테고리별 특성 수집
# ============================================================================

print("\n[1단계] 각 카테고리별 특성 수집")
print("-"*80)

category_features = {}

for category, indices in ground_truth.items():
    print(f"\n{category} 분석 중... ({len(indices)}개 사이클)")
    
    features_list = []
    for idx in indices:
        if idx < len(cycle_list):
            features = extract_features(cycle_list[idx], idx)
            features_list.append(features)
    
    category_features[category] = pd.DataFrame(features_list)
    print(f"  ✓ {len(features_list)}개 사이클 특성 추출 완료")

# ============================================================================
# 4. 카테고리별 통계 분석
# ============================================================================

print("\n[2단계] 카테고리별 통계 분석")
print("="*80)

numeric_features = [
    'n_points', 'voltage_min', 'voltage_max', 'voltage_range', 'voltage_mean',
    'current_range', 'endstate_unique', 'endstate_64_ratio', 'endstate_78_ratio',
    'charge_ratio', 'discharge_ratio', 'rest_ratio', 'crate_max', 'crate_mean'
]

for category in ground_truth.keys():
    df = category_features[category]
    
    print(f"\n{'='*80}")
    print(f"[{category}] 통계 요약 (n={len(df)})")
    print('='*80)
    
    for feature in numeric_features:
        if feature in df.columns and df[feature].notna().any():
            mean_val = df[feature].mean()
            std_val = df[feature].std()
            min_val = df[feature].min()
            max_val = df[feature].max()
            
            print(f"\n{feature}:")
            print(f"  평균: {mean_val:.2f} ± {std_val:.2f}")
            print(f"  범위: [{min_val:.2f}, {max_val:.2f}]")
    
    # EndState 패턴 분석
    print(f"\nEndState 값 분포:")
    endstate_values_all = []
    for val in df['endstate_values']:
        endstate_values_all.extend(val)
    unique_endstates = set(endstate_values_all)
    print(f"  출현 EndState: {sorted(unique_endstates)}")
    
    # 가장 흔한 EndState 조합
    print(f"\n가장 흔한 EndState 조합 (Top 3):")
    for idx, (val, count) in enumerate(df['endstate_values'].value_counts().head(3).items()):
        print(f"  {idx+1}. {val}: {count}회")

# ============================================================================
# 5. 구분력 있는 특성 파악
# ============================================================================

print("\n[3단계] 카테고리 간 구분력 분석")
print("="*80)

# 주요 수치 특성들의 카테고리별 평균 비교
comparison_features = ['n_points', 'voltage_range', 'endstate_unique', 
                       'endstate_64_ratio', 'endstate_78_ratio', 'charge_ratio']

comparison_df = pd.DataFrame()
for category in ground_truth.keys():
    df = category_features[category]
    row = {}
    for feature in comparison_features:
        if feature in df.columns:
            row[feature] = df[feature].mean()
    comparison_df[category] = pd.Series(row)

print("\n카테고리별 주요 특성 평균:")
print(comparison_df.T.to_string())

# ============================================================================
# 6. 시각화
# ============================================================================

print("\n[4단계] 특성 분포 시각화")
print("-"*80)

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('카테고리별 주요 특성 분포', fontsize=16, fontweight='bold')

features_to_plot = [
    ('n_points', '데이터 포인트 수'),
    ('voltage_range', 'Voltage 범위 (mV)'),
    ('endstate_unique', 'EndState 종류 수'),
    ('endstate_64_ratio', 'EndState=64 비율'),
    ('endstate_78_ratio', 'EndState=78 비율'),
    ('charge_ratio', 'Charge 비율')
]

for idx, (feature, label) in enumerate(features_to_plot):
    ax = axes[idx // 3, idx % 3]
    
    for category in ground_truth.keys():
        df = category_features[category]
        if feature in df.columns and df[feature].notna().any():
            ax.hist(df[feature], alpha=0.5, label=category, bins=20)
    
    ax.set_xlabel(label, fontsize=10)
    ax.set_ylabel('빈도', fontsize=10)
    ax.set_title(f'{label} 분포', fontsize=11)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\n" + "="*80)
print("✅ 특성 분석 완료!")
print("="*80)
