# ============================================================================
# 모든 채널에 대해 Cycle List 생성 및 처리
# ============================================================================

import matplotlib.cm as cm
import numpy as np

print("="*80)
print("📊 전체 채널 Cycle List 생성 및 처리")
print("="*80)

# 모든 cycle_list를 저장할 딕셔너리
all_cycle_lists = {}

# ============================================================================
# PNE Profile 데이터 처리
# ============================================================================

if loaded_data['pne_profile']:
    print("\n[PNE Profile 데이터 처리]")
    print("-"*80)
    
    for channel_key, df in loaded_data['pne_profile'].items():
        print(f"\n처리 중: {channel_key}")
        
        # 1. Cycle별로 데이터프레임 분할
        cycle_list = [group for _, group in df.groupby('Cycle')]
        print(f"  - 총 {len(cycle_list)}개 사이클 생성")
        
        # 2. 각 사이클마다 time_cyc 생성 (0부터 시작)
        for cycle in cycle_list:
            cycle['time_cyc'] = cycle['time_s'] - cycle['time_s'].iloc[0]
        
        # 3. 최소 용량 가져오기 (df_results에서)
        # 해당 채널의 df_results 찾기
        cycle_key = channel_key.replace('profile', 'cycle')
        if cycle_key in loaded_data['pne_cycle']:
            df_results = loaded_data['pne_cycle'][cycle_key]
            if len(df_results) > 0 and 'capacity_mAh' in df_results.columns:
                mincapa = df_results['capacity_mAh'].iloc[0]
            else:
                # capacity_mAh가 없으면 기본값 사용
                mincapa = 1000  # 기본값 1000mAh
                print(f"  ⚠️ capacity_mAh 없음, 기본값 {mincapa}mAh 사용")
        else:
            mincapa = 1000  # 기본값
            print(f"  ⚠️ cycle 데이터 없음, 기본값 {mincapa}mAh 사용")
        
        # 4. Capa_cyc와 Crate 계산
        for cycle in cycle_list:
            # 시간 차이(초)를 시간(hour) 단위로 변환하여 전류(mA)와 곱한 후 누적 합산 (mAh)
            cycle['Capa_cyc'] = (cycle['Current_mA'] * cycle['time_cyc'].diff().fillna(0) / 3600).cumsum()
            cycle['Crate'] = cycle['Current_mA'] / mincapa
        
        print(f"  ✓ time_cyc, Capa_cyc, Crate 계산 완료")
        
        # 5. cycle_list 저장
        all_cycle_lists[channel_key] = cycle_list

# ============================================================================
# Toyo Profile 데이터 처리
# ============================================================================

if loaded_data['toyo_profile']:
    print("\n[Toyo Profile 데이터 처리]")
    print("-"*80)
    
    for channel_key, df in loaded_data['toyo_profile'].items():
        print(f"\n처리 중: {channel_key}")
        
        # 1. Cycle별로 데이터프레임 분할
        cycle_list = [group for _, group in df.groupby('Cycle')]
        print(f"  - 총 {len(cycle_list)}개 사이클 생성")
        
        # 2. 각 사이클마다 time_cyc 생성 (0부터 시작)
        for cycle in cycle_list:
            cycle['time_cyc'] = cycle['time_s'] - cycle['time_s'].iloc[0]
        
        # 3. 최소 용량 가져오기
        cycle_key = channel_key.replace('profile', 'cycle')
        if cycle_key in loaded_data['toyo_cycle']:
            df_results = loaded_data['toyo_cycle'][cycle_key]
            if len(df_results) > 0 and 'capacity_mAh' in df_results.columns:
                mincapa = df_results['capacity_mAh'].iloc[0]
            else:
                mincapa = 1000
                print(f"  ⚠️ capacity_mAh 없음, 기본값 {mincapa}mAh 사용")
        else:
            mincapa = 1000
            print(f"  ⚠️ cycle 데이터 없음, 기본값 {mincapa}mAh 사용")
        
        # 4. Capa_cyc와 Crate 계산
        for cycle in cycle_list:
            cycle['Capa_cyc'] = (cycle['Current_mA'] * cycle['time_cyc'].diff().fillna(0) / 3600).cumsum()
            cycle['Crate'] = cycle['Current_mA'] / mincapa
        
        print(f"  ✓ time_cyc, Capa_cyc, Crate 계산 완료")
        
        # 5. cycle_list 저장
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
        print(f"  {channel_key}: {len(cycle_list)}개 사이클")

print("\n✅ 전체 채널 Cycle List 처리 완료!")
print("\n💡 사용 방법:")
print("  - all_cycle_lists: 모든 채널의 cycle_list를 담은 딕셔너리")
print("  - all_cycle_lists['channel_name']: 특정 채널의 cycle_list")
print("  - 예: cycle_list = all_cycle_lists[list(all_cycle_lists.keys())[0]]")
