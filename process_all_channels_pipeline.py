# ============================================================================
# 전체 채널 자동 처리 파이프라인
# ============================================================================

import cycle_processor
import profile_analyzer
import importlib
import matplotlib.cm as cm
import numpy as np

# 모듈 재로딩
importlib.reload(cycle_processor)
importlib.reload(profile_analyzer)

print("="*80)
print("🔄 전체 채널 자동 처리 파이프라인")
print("="*80)

# 전체 채널의 cycle_list를 저장할 딕셔너리
all_cycle_lists = {}
all_summaries = {}

# ============================================================================
# PNE Profile 데이터 처리
# ============================================================================

if loaded_data['pne_profile']:
    print("\n" + "="*80)
    print("📊 PNE Profile 데이터 처리")
    print("="*80)
    
    for channel_key in loaded_data['pne_profile'].keys():
        print(f"\n{'─'*80}")
        print(f"처리 중: {channel_key}")
        print('─'*80)
        
        # 1. Profile 데이터 가져오기
        df = loaded_data['pne_profile'][channel_key]
        print(f"데이터 shape: {df.shape}")
        
        # 2. Profile 요약 정보
        summary = profile_analyzer.get_profile_summary(df)
        print(f"\n데이터 요약:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # 3. Cycle 데이터에서 capacity 가져오기
        cycle_key = channel_key.replace('profile', 'cycle')
        if cycle_key in loaded_data['pne_cycle']:
            df_results = loaded_data['pne_cycle'][cycle_key]
            if len(df_results) > 0 and 'capacity_mAh' in df_results.columns:
                mincapa = df_results['capacity_mAh'].iloc[0]
                print(f"\n최소 용량: {mincapa:.2f} mAh")
            else:
                mincapa = 1000  # 기본값
                print(f"\n⚠️ capacity_mAh 없음, 기본값 {mincapa} mAh 사용")
        else:
            mincapa = 1000
            print(f"\n⚠️ cycle 데이터 없음, 기본값 {mincapa} mAh 사용")
        
        # 4. Cycle별로 데이터프레임 분할
        cycle_list = [group.copy() for _, group in df.groupby('Cycle')]
        print(f"\n생성된 사이클 수: {len(cycle_list)}개")
        
        # 5. 각 사이클마다 계산 수행
        for cycle in cycle_list:
            # time_cyc: 각 사이클마다 0부터 시작
            cycle['time_cyc'] = cycle['time_s'] - cycle['time_s'].iloc[0]
            
            # Capa_cyc: 누적 용량 (mAh)
            cycle['Capa_cyc'] = (cycle['Current_mA'] * cycle['time_cyc'].diff().fillna(0) / 3600).cumsum()
            
            # Crate: C-rate
            cycle['Crate'] = cycle['Current_mA'] / mincapa
        
        print("✓ time_cyc, Capa_cyc, Crate 계산 완료")
        
        # 6. 저장
        all_cycle_lists[channel_key] = cycle_list
        all_summaries[channel_key] = summary

# ============================================================================
# Toyo Profile 데이터 처리
# ============================================================================

if loaded_data['toyo_profile']:
    print("\n" + "="*80)
    print("📊 Toyo Profile 데이터 처리")
    print("="*80)
    
    for channel_key in loaded_data['toyo_profile'].keys():
        print(f"\n{'─'*80}")
        print(f"처리 중: {channel_key}")
        print('─'*80)
        
        # 1. Profile 데이터 가져오기
        df = loaded_data['toyo_profile'][channel_key]
        print(f"데이터 shape: {df.shape}")
        
        # 2. Profile 요약 정보
        summary = profile_analyzer.get_profile_summary(df)
        print(f"\n데이터 요약:")
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        # 3. Cycle 데이터에서 capacity 가져오기
        cycle_key = channel_key.replace('profile', 'cycle')
        if cycle_key in loaded_data['toyo_cycle']:
            df_results = loaded_data['toyo_cycle'][cycle_key]
            if len(df_results) > 0 and 'capacity_mAh' in df_results.columns:
                mincapa = df_results['capacity_mAh'].iloc[0]
                print(f"\n최소 용량: {mincapa:.2f} mAh")
            else:
                mincapa = 1000
                print(f"\n⚠️ capacity_mAh 없음, 기본값 {mincapa} mAh 사용")
        else:
            mincapa = 1000
            print(f"\n⚠️ cycle 데이터 없음, 기본값 {mincapa} mAh 사용")
        
        # 4. Cycle별로 데이터프레임 분할
        cycle_list = [group.copy() for _, group in df.groupby('Cycle')]
        print(f"\n생성된 사이클 수: {len(cycle_list)}개")
        
        # 5. 각 사이클마다 계산 수행
        for cycle in cycle_list:
            cycle['time_cyc'] = cycle['time_s'] - cycle['time_s'].iloc[0]
            cycle['Capa_cyc'] = (cycle['Current_mA'] * cycle['time_cyc'].diff().fillna(0) / 3600).cumsum()
            cycle['Crate'] = cycle['Current_mA'] / mincapa
        
        print("✓ time_cyc, Capa_cyc, Crate 계산 완료")
        
        # 6. 저장
        all_cycle_lists[channel_key] = cycle_list
        all_summaries[channel_key] = summary

# ============================================================================
# 전체 결과 요약
# ============================================================================

print("\n" + "="*80)
print("📋 전체 처리 결과 요약")
print("="*80)

total_channels = len(all_cycle_lists)
total_cycles = sum(len(cycle_list) for cycle_list in all_cycle_lists.values())

print(f"\n처리된 채널 수: {total_channels}개")
print(f"총 사이클 수: {total_cycles}개")

if all_cycle_lists:
    print(f"\n채널별 상세 정보:")
    print(f"{'채널명':<40} {'사이클 수':>10} {'데이터 포인트':>15}")
    print("-"*70)
    
    for channel_key, cycle_list in all_cycle_lists.items():
        n_cycles = len(cycle_list)
        n_points = sum(len(cycle) for cycle in cycle_list)
        print(f"{channel_key:<40} {n_cycles:>10} {n_points:>15,}")

print("\n" + "="*80)
print("✅ 전체 채널 처리 완료!")
print("="*80)

print("\n💡 생성된 변수:")
print("  - all_cycle_lists: 채널별 cycle_list 딕셔너리")
print("  - all_summaries: 채널별 profile 요약 딕셔너리")

print("\n💡 사용 예시:")
print("  # 특정 채널의 cycle_list 가져오기")
print("  channel_name = list(all_cycle_lists.keys())[0]")
print("  cycle_list = all_cycle_lists[channel_name]")
print("  ")
print("  # 첫 번째 채널 선택 (간단한 방법)")
if all_cycle_lists:
    first_channel = list(all_cycle_lists.keys())[0]
    print(f"  cycle_list = all_cycle_lists['{first_channel}']")
