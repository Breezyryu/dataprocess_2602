# ============================================================================
# 통합 데이터 구조 사용 예제
# ============================================================================

import data_combiner

# paths 정의
paths = [
    r"C:\Users\Ryu\Python_project\data\dataprocess\Rawdata\A1_MP1_4500mAh_T23_1"
]

# ============================================================================
# 데이터 로드 (단일 출력)
# ============================================================================

print("="*80)
print("🔋 배터리 데이터 처리 (통합 출력)")
print("="*80)

# 하나의 딕셔너리로 모든 데이터 받기
data = data_combiner.process_and_combine(paths)

print("\n✅ 처리 완료!")
print(f"  - 총 경로 수: {data['metadata']['total_paths']}")
print(f"  - 총 채널 수: {data['metadata']['total_channels']}")
print(f"  - Cycler 타입: {data['metadata']['cycler_types']}")

# ============================================================================
# 메타데이터 접근
# ============================================================================

print("\n" + "="*80)
print("📊 메타데이터")
print("="*80)

metadata = data['metadata']
print(f"\n총 채널 수: {metadata['total_channels']}")
print(f"처리된 경로: {metadata['total_paths']}개")
print(f"\nCycler 타입별 채널 수:")
for cycler_type, count in metadata['cycler_types'].items():
    print(f"  - {cycler_type}: {count}개")

# ============================================================================
# 채널 데이터 접근
# ============================================================================

print("\n" + "="*80)
print("📁 채널 데이터")
print("="*80)

channels = data['channels']
print(f"\n채널 목록:")
for channel_key in channels.keys():
    print(f"  - {channel_key}")

# 첫 번째 채널 상세 정보
if channels:
    channel_key = list(channels.keys())[0]
    channel_data = channels[channel_key]
    
    print(f"\n첫 번째 채널 상세: {channel_key}")
    print(f"  - Cycler 타입: {channel_data['cycler_type']}")
    print(f"  - 용량: {channel_data['capacity_mAh']} mAh")
    print(f"  - 폴더명: {channel_data['folder_name']}")
    
    if channel_data['cycle'] is not None:
        print(f"  - Cycle 데이터: {len(channel_data['cycle'])}행")
    
    if channel_data['profile'] is not None:
        print(f"  - Profile 데이터: {len(channel_data['profile'])}행")

# ============================================================================
# 모든 채널 순회
# ============================================================================

print("\n" + "="*80)
print("🔄 모든 채널 순회")
print("="*80)

for channel_key, channel_data in data['channels'].items():
    print(f"\n{channel_key}:")
    print(f"  Cycler: {channel_data['cycler_type']}")
    print(f"  Cycle: {'있음' if channel_data['cycle'] is not None else '없음'}")
    print(f"  Profile: {'있음' if channel_data['profile'] is not None else '없음'}")

# ============================================================================
# 필요시 DataFrame 생성
# ============================================================================

print("\n" + "="*80)
print("📊 DataFrame 생성 (필요시)")
print("="*80)

# Cycle 데이터만 DataFrame으로
df_cycle = data_combiner.get_cycle_data_only(data['channels'])
print(f"\nCycle DataFrame: {len(df_cycle):,}행")

# Profile 데이터만 DataFrame으로
df_profile = data_combiner.get_profile_data_only(data['channels'])
print(f"Profile DataFrame: {len(df_profile):,}행")

# 전체 통합 DataFrame
df_combined = data_combiner.combine_to_dataframe(data['channels'])
print(f"통합 DataFrame: {len(df_combined):,}행")

# ============================================================================
# 데이터 분석 예시
# ============================================================================

print("\n" + "="*80)
print("💡 데이터 분석 예시")
print("="*80)

# 특정 채널의 Cycle 데이터 분석
for channel_key, channel_data in data['channels'].items():
    if channel_data['cycle'] is not None:
        df = channel_data['cycle']
        print(f"\n{channel_key}:")
        
        # 용량 분석 (PNE)
        if 'DchgCap_mAh' in df.columns:
            initial = df['DchgCap_mAh'].iloc[0]
            final = df['DchgCap_mAh'].iloc[-1]
            retention = final / initial * 100
            print(f"  용량 보존율: {retention:.1f}%")
        
        # 용량 분석 (Toyo)
        elif 'Capacity_mAh' in df.columns:
            initial = df['Capacity_mAh'].iloc[0]
            final = df['Capacity_mAh'].iloc[-1]
            retention = final / initial * 100
            print(f"  용량 보존율: {retention:.1f}%")

print("\n" + "="*80)
print("✅ 예제 완료!")
print("="*80)

print("\n💡 통합 구조 장점:")
print("  1. 하나의 변수로 모든 데이터 관리")
print("  2. 메타데이터와 채널 데이터 분리")
print("  3. 중복 없는 깔끔한 구조")
print("  4. 필요시에만 DataFrame 생성")
