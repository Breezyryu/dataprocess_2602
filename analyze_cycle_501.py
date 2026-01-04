# ============================================================================
# cycle 501 특성 분석 스크립트
# ============================================================================

import pandas as pd

print("="*80)
print("🔍 cycle 501 상세 분석")
print("="*80)

# ============================================================================
# 1. cycle 501 특성 추출
# ============================================================================

if len(cycle_list) > 501:
    cycle_501 = cycle_list[501]
    
    print("\n[cycle 501 기본 정보]")
    print("-"*80)
    print(f"데이터 포인트 수: {len(cycle_501)}")
    print(f"Voltage 범위: {cycle_501['Voltage_V'].min():.2f} ~ {cycle_501['Voltage_V'].max():.2f} mV")
    print(f"Voltage range: {cycle_501['Voltage_V'].max() - cycle_501['Voltage_V'].min():.2f} mV")
    print(f"Current 범위: {cycle_501['Current_mA'].min():.2f} ~ {cycle_501['Current_mA'].max():.2f} mA")
    
    # EndState 분석
    print(f"\n[EndState 분석]")
    print("-"*80)
    endstate_counts = cycle_501['EndState'].value_counts()
    print(f"EndState 값 종류: {cycle_501['EndState'].nunique()}개")
    print(f"EndState 값: {sorted(cycle_501['EndState'].unique())}")
    print(f"\nEndState 분포:")
    for es, count in endstate_counts.items():
        ratio = count / len(cycle_501)
        print(f"  EndState {int(es)}: {count}회 ({ratio*100:.1f}%)")
    
    # 특히 EndState 78 비율 확인
    endstate_78_ratio = (cycle_501['EndState'] == 78).sum() / len(cycle_501)
    endstate_64_ratio = (cycle_501['EndState'] == 64).sum() / len(cycle_501)
    print(f"\nEndState 78 비율: {endstate_78_ratio:.3f} (임계값: 0.5)")
    print(f"EndState 64 비율: {endstate_64_ratio:.3f}")
    
    # Condition 분석
    print(f"\n[Condition 분석]")
    print("-"*80)
    condition_counts = cycle_501['Condition'].value_counts()
    condition_map = {1: '충전', 2: '방전', 3: 'Rest'}
    for cond, count in condition_counts.items():
        ratio = count / len(cycle_501)
        print(f"  {condition_map.get(cond, cond)}: {count}회 ({ratio*100:.1f}%)")
    
    # C-rate 분석
    if 'Crate' in cycle_501.columns:
        print(f"\n[C-rate 분석]")
        print("-"*80)
        crate_max = cycle_501['Crate'].abs().max()
        crate_mean = cycle_501['Crate'].abs().mean()
        print(f"최대 C-rate: {crate_max:.3f}C (Accelerated_Aging 임계값: 1.5C)")
        print(f"평균 C-rate: {crate_mean:.3f}C")
    
    # 분류 결과
    print(f"\n[분류 결과]")
    print("-"*80)
    import cycle_categorizer
    import importlib
    importlib.reload(cycle_categorizer)
    
    category = cycle_categorizer.categorize_cycle(cycle_501, 501)
    print(f"자동 분류: {category}")
    
    # 왜 SOC_Definition으로 분류되었는지 확인
    print(f"\n분류 규칙 체크:")
    print(f"  1. n_points > 10,000? {len(cycle_501)} > 10,000 = {len(cycle_501) > 10000}")
    print(f"  2. endstate_78_ratio > 0.5? {endstate_78_ratio:.3f} > 0.5 = {endstate_78_ratio > 0.5}")
    
    # ============================================================================
    # 2. 주변 사이클과 비교
    # ============================================================================
    
    print("\n" + "="*80)
    print("🔄 주변 사이클과 비교 (500, 501, 502)")
    print("="*80)
    
    comparison_data = []
    for idx in [500, 501, 502]:
        if idx < len(cycle_list):
            c = cycle_list[idx]
            cat = cycle_categorizer.categorize_cycle(c, idx)
            
            comparison_data.append({
                'Cycle': idx,
                'Category': cat,
                'n_points': len(c),
                'voltage_range': c['Voltage_V'].max() - c['Voltage_V'].min(),
                'endstate_78_ratio': (c['EndState'] == 78).sum() / len(c),
                'endstate_64_ratio': (c['EndState'] == 64).sum() / len(c),
                'crate_max': c['Crate'].abs().max() if 'Crate' in c.columns else 0
            })
    
    comparison_df = pd.DataFrame(comparison_data)
    print("\n비교 테이블:")
    print(comparison_df.to_string(index=False))
    
    # ============================================================================
    # 3. SOC_Definition 카테고리와 비교
    # ============================================================================
    
    print("\n" + "="*80)
    print("📊 SOC_Definition 카테고리 평균과 비교")
    print("="*80)
    
    soc_cycles = [2, 102, 202, 301, 401]
    soc_features = []
    for idx in soc_cycles:
        if idx < len(cycle_list):
            c = cycle_list[idx]
            soc_features.append({
                'n_points': len(c),
                'voltage_range': c['Voltage_V'].max() - c['Voltage_V'].min(),
                'endstate_78_ratio': (c['EndState'] == 78).sum() / len(c),
                'endstate_64_ratio': (c['EndState'] == 64).sum() / len(c),
            })
    
    soc_df = pd.DataFrame(soc_features)
    
    print("\nSOC_Definition 평균:")
    print(f"  n_points: {soc_df['n_points'].mean():.1f}")
    print(f"  voltage_range: {soc_df['voltage_range'].mean():.1f}")
    print(f"  endstate_78_ratio: {soc_df['endstate_78_ratio'].mean():.3f}")
    print(f"  endstate_64_ratio: {soc_df['endstate_64_ratio'].mean():.3f}")
    
    print(f"\ncycle 501:")
    print(f"  n_points: {len(cycle_501)}")
    print(f"  voltage_range: {cycle_501['Voltage_V'].max() - cycle_501['Voltage_V'].min():.1f}")
    print(f"  endstate_78_ratio: {endstate_78_ratio:.3f}")
    print(f"  endstate_64_ratio: {endstate_64_ratio:.3f}")
    
    print("\n" + "="*80)
    print("✅ 분석 완료!")
    print("="*80)
    
    # 시각화
    print("\n📊 cycle 501 시각화")
    print("-"*80)
    
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Voltage vs Time
    ax1 = axes[0, 0]
    ax1.plot(cycle_501['time_cyc'], cycle_501['Voltage_V'], 'b-', linewidth=0.8)
    ax1.set_title('cycle 501: Voltage vs Time', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Voltage (V)')
    ax1.grid(True, alpha=0.3)
    
    # Current vs Time
    ax2 = axes[0, 1]
    ax2.plot(cycle_501['time_cyc'], cycle_501['Current_mA'], 'r-', linewidth=0.8)
    ax2.set_title('cycle 501: Current vs Time', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Current (mA)')
    ax2.grid(True, alpha=0.3)
    
    # EndState distribution
    ax3 = axes[1, 0]
    endstate_counts.plot(kind='bar', ax=ax3, color='green', alpha=0.7)
    ax3.set_title('cycle 501: EndState 분포', fontsize=12, fontweight='bold')
    ax3.set_xlabel('EndState')
    ax3.set_ylabel('빈도')
    ax3.grid(True, alpha=0.3)
    
    # Condition distribution
    ax4 = axes[1, 1]
    condition_counts.plot(kind='bar', ax=ax4, color='orange', alpha=0.7)
    ax4.set_title('cycle 501: Condition 분포', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Condition')
    ax4.set_ylabel('빈도')
    ax4.set_xticklabels([condition_map.get(int(x.get_text()), x.get_text()) 
                          for x in ax4.get_xticklabels()])
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
else:
    print("⚠️ cycle 501이 존재하지 않습니다.")
