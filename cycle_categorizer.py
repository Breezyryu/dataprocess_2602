# -*- coding: utf-8 -*-
"""
사이클 분류 모듈

cycle_list를 4가지 범주로 분류:
- RPT (Reference Performance Test) 사이클
- SOC 정의 사이클
- 저항 측정 사이클
- 가속수명패턴 사이클
"""

import pandas as pd
import numpy as np


def categorize_cycle(cycle_df, cycle_index):
    """
    데이터 특성 기반 사이클 분류
    
    분석 결과를 바탕으로 한 결정 트리 방식 분류:
    1. n_points > 10,000 → Resistance_Measurement
    2. endstate_78_ratio > 0.5 → SOC_Definition
    3. voltage_range < 1,400 AND crate_max > 1.5 → Accelerated_Aging
    4. endstate_64_ratio > 0.90 AND voltage_range > 1,400 → RPT
    5. 나머지 → Unknown
    
    Parameters:
    -----------
    cycle_df : pd.DataFrame
        분석할 사이클 데이터
    cycle_index : int
        사이클 인덱스 (0부터 시작, 이 함수에서는 미사용)
    
    Returns:
    --------
    str : 사이클 카테고리
        'Unknown', 'RPT', 'SOC_Definition', 'Resistance_Measurement', 'Accelerated_Aging'
    """
    
    # 기본 특성 추출
    n_points = len(cycle_df)
    voltage_range = cycle_df['Voltage_V'].max() - cycle_df['Voltage_V'].min()
    
    # EndState 분석
    endstate_78_ratio = (cycle_df['EndState'] == 78).sum() / n_points
    endstate_64_ratio = (cycle_df['EndState'] == 64).sum() / n_points
    
    # C-rate 분석 (있는 경우)
    if 'Crate' in cycle_df.columns:
        crate_max = cycle_df['Crate'].abs().max()
    else:
        crate_max = 0
    
    # 분류 규칙 (결정 트리)
    
    # 1. Resistance_Measurement: 데이터 포인트가 매우 많음 (>10,000)
    #    평균: 51,325개 vs 다른 카테고리 <700개
    if n_points > 10000:
        return 'Resistance_Measurement'
    
    # 2. SOC_Definition: EndState 78이 많이 나타남 (>50%) + cycle_index < 500
    #    평균: 0.69 vs 다른 카테고리 0.00
    #    인덱스 제약: Ground Truth는 [2, 102, 202, 301, 401]로 모두 500 미만
    if endstate_78_ratio > 0.5 and cycle_index < 500:
        return 'SOC_Definition'
    
    # 3. Accelerated_Aging: 제한된 전압 범위 (<1,400 mV) + 높은 C-rate (>1.5C)
    #    voltage_range 평균: 1,266 mV, crate_max: 2.0C
    if voltage_range < 1400 and crate_max > 1.5:
        return 'Accelerated_Aging'
    
    # 4. RPT: 높은 EndState 64 비율 (>90%) + full voltage range (>1,400 mV)
    #    endstate_64_ratio 평균: 0.96, voltage_range: 1,501 mV
    if endstate_64_ratio > 0.90 and voltage_range > 1400:
        return 'RPT'
    
    # 5. Unknown: 나머지 (초기화, 종료, 특이 케이스)
    #    cycle 501도 여기에 포함 (endstate_78_ratio가 높지만 cycle_index >= 500)
    return 'Unknown'


def categorize_cycle_by_features(cycle_df, cycle_index):
    """
    데이터 특성을 기반으로 카테고리 분류 (기존 로직 보존)
    
    이 함수는 검증 및 참고 목적으로 보존됩니다.
    실제 분류에는 categorize_cycle() 함수를 사용하세요.
    
    Parameters:
    -----------
    cycle_df : pd.DataFrame
        분석할 사이클 데이터
    cycle_index : int
        사이클 인덱스 (0부터 시작)
    
    Returns:
    --------
    str : 사이클 카테고리
        'RPT', 'SOC_Definition', 'Resistance_Measurement', 'Accelerated_Aging'
    """
    
    # 기본 통계 계산
    endstate_unique = cycle_df['EndState'].nunique()
    endstate_values = cycle_df['EndState'].unique()
    endstate_counts = cycle_df['EndState'].value_counts()
    
    # Condition 분석
    condition_unique = cycle_df['Condition'].nunique()
    condition_values = cycle_df['Condition'].unique()
    
    # EndState 패턴 분석
    has_endstate_64 = 64 in endstate_values
    has_endstate_65 = 65 in endstate_values
    has_endstate_66 = 66 in endstate_values
    has_endstate_78 = 78 in endstate_values
    
    # EndState 64의 비율
    endstate_64_ratio = endstate_counts.get(64, 0) / len(cycle_df) if has_endstate_64 else 0
    
    # Voltage 분석
    voltage_range = cycle_df['Voltage_V'].max() - cycle_df['Voltage_V'].min()
    voltage_mean = cycle_df['Voltage_V'].mean()
    
    # C-rate 통계 (있는 경우)
    if 'Crate' in cycle_df.columns:
        crate_max = cycle_df['Crate'].abs().max()
        crate_mean = cycle_df['Crate'].abs().mean()
        # 고율 충방전 여부 (1C 이상)
        has_high_crate = crate_max > 1.0
    else:
        crate_max = 0
        crate_mean = 0
        has_high_crate = False
    
    # 분류 로직 (데이터 특성 기반)
    
    # 1. 저항 측정 사이클 (Resistance Measurement)
    # - EndState 64가 대부분 (>95%)
    # - 긴 시간 동안 측정 (voltage range가 큼)
    if endstate_64_ratio > 0.95 and voltage_range > 1000:
        return 'Resistance_Measurement'
    
    # 2. SOC 정의 사이클 (SOC Definition)
    # - EndState 78 포함 (전압 컷오프)
    # - EndState 65, 66도 함께 나타남
    elif has_endstate_78 and (has_endstate_65 or has_endstate_66):
        return 'SOC_Definition'
    
    # 3. RPT 사이클 (Reference Performance Test)
    # - EndState 종류가 적음 (<=3)
    # - EndState 64, 65, 66만 사용
    # - EndState 78 없음 (전압 컷오프 없음)
    elif endstate_unique <= 3 and not has_endstate_78 and has_endstate_64:
        return 'RPT'
    
    # 4. 가속수명패턴 (Accelerated Aging)
    # - 나머지 (일반적으로 반복적인 충방전)
    # - EndState 패턴이 단순함
    else:
        return 'Accelerated_Aging'


def categorize_cycles(cycle_list):
    """
    전체 cycle_list를 분류
    
    Parameters:
    -----------
    cycle_list : list of pd.DataFrame
        분류할 사이클 리스트
    
    Returns:
    --------
    dict : 카테고리별로 분류된 사이클
        {
            'RPT': [cycle_indices],
            'SOC_Definition': [cycle_indices],
            'Resistance_Measurement': [cycle_indices],
            'Accelerated_Aging': [cycle_indices]
        }
    """
    
    categories = {
        'Unknown': [],
        'RPT': [],
        'SOC_Definition': [],
        'Resistance_Measurement': [],
        'Accelerated_Aging': []
    }
    
    for idx, cycle in enumerate(cycle_list):
        category = categorize_cycle(cycle, idx)
        categories[category].append(idx)
    
    return categories


def add_category_labels(cycle_list, categories=None):
    """
    각 사이클에 카테고리 라벨을 추가
    
    Parameters:
    -----------
    cycle_list : list of pd.DataFrame
        사이클 리스트 (원본이 수정됨)
    categories : dict, optional
        categorize_cycles의 반환값. None이면 자동으로 분류 수행
    
    Returns:
    --------
    dict : 카테고리별 사이클 인덱스 딕셔너리
    """
    
    # categories가 없으면 자동으로 분류
    if categories is None:
        categories = categorize_cycles(cycle_list)
    
    # 각 사이클에 category 컬럼 추가
    for category, indices in categories.items():
        for idx in indices:
            cycle_list[idx]['category'] = category
    
    return categories


def get_cycle_category(cycle_df):
    """
    단일 사이클의 카테고리를 반환 (이미 라벨이 추가된 경우)
    
    Parameters:
    -----------
    cycle_df : pd.DataFrame
        사이클 데이터
    
    Returns:
    --------
    str or None : 카테고리 명 (라벨이 없으면 None)
    """
    if 'category' in cycle_df.columns and len(cycle_df) > 0:
        return cycle_df['category'].iloc[0]
    return None


def print_categorization_report(cycle_list, categories):
    """
    분류 결과 리포트 출력
    
    Parameters:
    -----------
    cycle_list : list of pd.DataFrame
        사이클 리스트
    categories : dict
        categorize_cycles의 반환값
    """
    
    print("=" * 80)
    print("📊 사이클 분류 결과")
    print("=" * 80)
    print()
    
    for category, indices in categories.items():
        print(f"\n[{category}]")
        print(f"  총 {len(indices)}개 사이클")
        
        if indices:
            print(f"  사이클 인덱스: {indices[:10]}")  # 처음 10개만 표시
            if len(indices) > 10:
                print(f"  ... 외 {len(indices) - 10}개")
            
            # 첫 번째 사이클의 상세 정보
            first_idx = indices[0]
            cycle = cycle_list[first_idx]
            
            print(f"\n  [대표 사이클 {first_idx} 특성]")
            
            # Voltage 정보
            v_min = cycle['Voltage_V'].min()
            v_max = cycle['Voltage_V'].max()
            v_range = v_max - v_min
            print(f"    - Voltage 범위: {v_min:.0f} ~ {v_max:.0f} mV (범위: {v_range:.0f} mV)")
            
            # EndState 패턴
            endstate_counts = cycle['EndState'].value_counts()
            endstate_str = ", ".join([f"{int(k)}({v}회)" for k, v in endstate_counts.head(3).items()])
            print(f"    - EndState 패턴: {endstate_str}")
            
            # Condition 정보
            condition_counts = cycle['Condition'].value_counts()
            condition_map = {1: '충전', 2: '방전', 3: 'Rest'}
            condition_str = ", ".join([f"{condition_map.get(k, k)}({v}회)" for k, v in condition_counts.items()])
            print(f"    - Condition: {condition_str}")
            
            # C-rate 정보
            if 'Crate' in cycle.columns:
                crate_abs = cycle['Crate'].abs()
                print(f"    - C-rate: 평균 {crate_abs.mean():.3f}C, 최대 {crate_abs.max():.3f}C")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("사이클 분류 모듈")
    print("이 모듈은 dataprocess.ipynb에서 import하여 사용하세요.")
