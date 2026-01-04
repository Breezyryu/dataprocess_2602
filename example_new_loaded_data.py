# ============================================================================
# 새로운 loaded_data 구조 사용 예제
# ============================================================================

import dataprocess

# 데이터 로드
df_results, loaded_data = dataprocess.process_battery_data(paths)

print("="*80)
print("📊 새로운 loaded_data 구조 사용 예제")
print("="*80)

# ============================================================================
# 1. loaded_data 구조 확인
# ============================================================================

print("\n[1] loaded_data 구조")
print("-"*80)
print(f"총 채널 수: {len(loaded_data)}개")
print(f"\n채널 목록:")
for channel_key in loaded_data.keys():
    print(f"  - {channel_key}")

# ============================================================================
# 2. 특정 채널 데이터 접근
# ============================================================================

print("\n[2] 특정 채널 데이터 접근")
print("-"*80)

# 첫 번째 채널 선택
channel_key = list(loaded_data.keys())[0]
channel_data = loaded_data[channel_key]

print(f"선택된 채널: {channel_key}")
print(f"\n채널 정보:")
print(f"  - Cycler 타입: {channel_data['cycler_type']}")
print(f"  - 용량: {channel_data['capacity_mAh']} mAh")
print(f"  - 폴더명: {channel_data['folder_name']}")
print(f"  - 채널명: {channel_data['channel_name']}")

# Cycle 데이터
if channel_data['cycle'] is not None:
    print(f"\n  - Cycle 데이터: {len(channel_data['cycle'])}행")
    print(f"    컬럼: {channel_data['cycle'].columns.tolist()}")
else:
    print(f"\n  - Cycle 데이터: 없음")

# Profile 데이터
if channel_data['profile'] is not None:
    print(f"\n  - Profile 데이터: {len(channel_data['profile'])}행")
    print(f"    컬럼: {channel_data['profile'].columns.tolist()}")
else:
    print(f"\n  - Profile 데이터: 없음")

# ============================================================================
# 3. 모든 채널 순회
# ============================================================================

print("\n[3] 모든 채널 순회")
print("-"*80)

for channel_key, channel_data in loaded_data.items():
    print(f"\n{channel_key}:")
    print(f"  Cycler: {channel_data['cycler_type']}")
    print(f"  Cycle 데이터: {'있음' if channel_data['cycle'] is not None else '없음'}")
    print(f"  Profile 데이터: {'있음' if channel_data['profile'] is not None else '없음'}")

# ============================================================================
# 4. Cycler 타입별 필터링
# ============================================================================

print("\n[4] Cycler 타입별 필터링")
print("-"*80)

# PNE 채널만 필터링
pne_channels = {k: v for k, v in loaded_data.items() if v['cycler_type'] == 'PNE'}
print(f"PNE 채널 수: {len(pne_channels)}개")

# Toyo 채널만 필터링
toyo_channels = {k: v for k, v in loaded_data.items() if v['cycler_type'] == 'Toyo'}
print(f"Toyo 채널 수: {len(toyo_channels)}개")

# ============================================================================
# 5. Cycle 데이터 분석 예시
# ============================================================================

print("\n[5] Cycle 데이터 분석 예시")
print("-"*80)

for channel_key, channel_data in loaded_data.items():
    if channel_data['cycle'] is not None:
        df_cycle = channel_data['cycle']
        print(f"\n{channel_key}:")
        
        if 'Capacity_mAh' in df_cycle.columns or 'DchgCap_mAh' in df_cycle.columns:
            capacity_col = 'Capacity_mAh' if 'Capacity_mAh' in df_cycle.columns else 'DchgCap_mAh'
            print(f"  초기 용량: {df_cycle[capacity_col].iloc[0]:.2f} mAh")
            print(f"  최종 용량: {df_cycle[capacity_col].iloc[-1]:.2f} mAh")
            print(f"  용량 보존율: {df_cycle[capacity_col].iloc[-1] / df_cycle[capacity_col].iloc[0] * 100:.1f}%")

# ============================================================================
# 6. Profile 데이터 분석 예시
# ============================================================================

print("\n[6] Profile 데이터 분석 예시")
print("-"*80)

for channel_key, channel_data in loaded_data.items():
    if channel_data['profile'] is not None:
        df_profile = channel_data['profile']
        print(f"\n{channel_key}:")
        print(f"  총 데이터 포인트: {len(df_profile):,}개")
        
        if 'Cycle' in df_profile.columns:
            print(f"  사이클 범위: {df_profile['Cycle'].min()} ~ {df_profile['Cycle'].max()}")
        
        if 'Voltage_V' in df_profile.columns:
            print(f"  전압 범위: {df_profile['Voltage_V'].min():.3f} ~ {df_profile['Voltage_V'].max():.3f} V")

print("\n" + "="*80)
print("✅ 예제 완료!")
print("="*80)

print("\n💡 주요 변경사항:")
print("  [이전 구조]")
print("  loaded_data['pne_cycle']['channel_name']")
print("  loaded_data['pne_profile']['channel_name']")
print("")
print("  [새로운 구조]")
print("  loaded_data['channel_name']['cycle']")
print("  loaded_data['channel_name']['profile']")
print("  loaded_data['channel_name']['cycler_type']")
print("  loaded_data['channel_name']['capacity_mAh']")
