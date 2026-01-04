# ============================================================================
# 모든 채널에 대해 Profile 및 Cycle 데이터 처리
# ============================================================================

import profile_analyzer
import numpy as np
import matplotlib.cm as cm

# 모든 채널의 cycle_list를 저장할 딕셔너리
all_cycle_lists = {}

print("="*80)
print("📊 전체 채널 Profile 및 Cycle 데이터 처리")
print("="*80)

# ============================================================================
# 모든 채널 순회
# ============================================================================

for channel_key, channel_data in data['channels'].items():
    print(f"\n{'─'*80}")
    print(f"처리 중: {channel_key}")
    print('─'*80)
    
    print(f"  - Cycler 타입: {channel_data['cycler_type']}")
    print(f"  - 용량: {channel_data['capacity_mAh']} mAh")
    
    # ========================================================================
    # 1. Profile 데이터 확인
    # ========================================================================
    
    if channel_data['profile'] is None:
        print("  ⚠️ Profile 데이터 없음 - 건너뜀")
        continue
    
    sample_df = channel_data['profile']
    print(f"  - Profile shape: {sample_df.shape}")
    
    # 데이터 요약
    summary = profile_analyzer.get_profile_summary(sample_df)
    print(f"\n  데이터 요약:")
    for key, value in summary.items():
        print(f"    {key}: {value}")
    
    # ========================================================================
    # 2. Cycle List 생성
    # ========================================================================
    
    df = channel_data['profile']
    cycle_list = [group.copy() for _, group in df.groupby('Cycle')]
    print(f"\n  생성된 사이클 수: {len(cycle_list)}개")
    
    # ========================================================================
    # 3. time_cyc 생성
    # ========================================================================
    
    for cycle in cycle_list:
        cycle['time_cyc'] = cycle['time_s'] - cycle['time_s'].iloc[0]
    
    # ========================================================================
    # 4. 최소 용량 가져오기
    # ========================================================================
    
    if channel_data['cycle'] is not None:
        df_cycle = channel_data['cycle']
        
        # PNE: DchgCap_mAh, Toyo: Capacity_mAh
        if 'DchgCap_mAh' in df_cycle.columns:
            mincapa = df_cycle['DchgCap_mAh'].iloc[0]
        elif 'Capacity_mAh' in df_cycle.columns:
            mincapa = df_cycle['Capacity_mAh'].iloc[0]
        else:
            mincapa = channel_data['capacity_mAh'] or 1000
    else:
        mincapa = channel_data['capacity_mAh'] or 1000
    
    print(f"  최소 용량: {mincapa:.2f} mAh")
    
    # ========================================================================
    # 5. Capa_cyc와 Crate 계산
    # ========================================================================
    
    for cycle in cycle_list:
        # 시간 차이(초)를 시간(hour) 단위로 변환하여 전류(mA)와 곱한 후 누적 합산 (mAh)
        cycle['Capa_cyc'] = (cycle['Current_mA'] * cycle['time_cyc'].diff().fillna(0) / 3600).cumsum()
        cycle['Crate'] = cycle['Current_mA'] / mincapa
    
    print("  ✅ time_cyc, Capa_cyc, Crate 계산 완료")
    
    # 첫 번째 사이클 정보
    if len(cycle_list) > 0:
        print(f"\n  첫 번째 사이클 정보:")
        print(f"    - 데이터 포인트: {len(cycle_list[0])}개")
        print(f"    - 지속 시간: {cycle_list[0]['time_cyc'].max():.1f}초")
        print(f"    - 최대 C-rate: {cycle_list[0]['Crate'].abs().max():.2f}C")
    
    # ========================================================================
    # 6. cycle_list 저장
    # ========================================================================
    
    all_cycle_lists[channel_key] = cycle_list

# ============================================================================
# 결과 요약
# ============================================================================

print("\n" + "="*80)
print("📋 처리 결과 요약")
print("="*80)

total_channels = len(all_cycle_lists)
total_cycles = sum(len(cycle_list) for cycle_list in all_cycle_lists.values())

print(f"\n처리된 채널 수: {total_channels}개")
print(f"총 사이클 수: {total_cycles}개")

if all_cycle_lists:
    print(f"\n채널별 사이클 수:")
    for channel_key, cycle_list in all_cycle_lists.items():
        print(f"  - {channel_key}: {len(cycle_list)}개")

print("\n✅ 전체 채널 처리 완료!")

print("\n" + "="*80)
print("💡 사용 방법")
print("="*80)
print("\n# 특정 채널의 cycle_list 사용:")
print("channel_key = list(all_cycle_lists.keys())[0]")
print("cycle_list = all_cycle_lists[channel_key]")
print("\n# 모든 채널 순회:")
print("for channel_key, cycle_list in all_cycle_lists.items():")
print("    # 분석 코드...")
