# ============================================================================
# Cycle 처리 유틸리티 사용 예제
# ============================================================================

import cycle_processor
import importlib

# 모듈 재로딩
importlib.reload(cycle_processor)

print("="*80)
print("🔄 Cycle 처리 유틸리티 사용 예제")
print("="*80)

# ============================================================================
# 방법 1: 모든 채널 자동 처리
# ============================================================================

print("\n[방법 1] 모든 채널 자동 처리")
print("-"*80)

# loaded_data의 모든 채널을 자동으로 처리
all_cycle_lists = cycle_processor.process_all_channels(loaded_data, default_capacity=1000)

print(f"처리된 채널 수: {len(all_cycle_lists)}개")

# 각 채널의 요약 정보
for channel_key, cycle_list in all_cycle_lists.items():
    summary = cycle_processor.get_cycle_summary(cycle_list)
    print(f"\n{channel_key}:")
    print(f"  - 사이클 수: {summary['total_cycles']}")
    print(f"  - 총 데이터 포인트: {summary['total_data_points']}")
    if 'avg_duration' in summary:
        print(f"  - 평균 지속 시간: {summary['avg_duration']:.1f}초")
    if 'avg_max_crate' in summary:
        print(f"  - 평균 최대 C-rate: {summary['avg_max_crate']:.2f}C")

# ============================================================================
# 방법 2: 단일 채널 처리 (기존 방식과 동일)
# ============================================================================

print("\n[방법 2] 단일 채널 처리 (예시)")
print("-"*80)

# 특정 채널의 데이터 가져오기
if loaded_data['pne_profile']:
    sample_key = list(loaded_data['pne_profile'].keys())[0]
    df = loaded_data['pne_profile'][sample_key]
    
    # cycle 데이터 가져오기
    cycle_key = sample_key.replace('profile', 'cycle')
    df_results = loaded_data['pne_cycle'].get(cycle_key)
    
    # cycle_list 생성 및 처리
    cycle_list = cycle_processor.process_cycle_list(df, df_results, default_capacity=1000)
    
    print(f"채널: {sample_key}")
    print(f"생성된 사이클 수: {len(cycle_list)}")
    
    # 요약 정보
    summary = cycle_processor.get_cycle_summary(cycle_list)
    print(f"\n요약 정보:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

# ============================================================================
# 결과 확인
# ============================================================================

print("\n" + "="*80)
print("✅ Cycle 처리 완료!")
print("="*80)

print("\n💡 사용 가능한 변수:")
print("  - all_cycle_lists: 모든 채널의 cycle_list 딕셔너리")
print("  - cycle_list: 마지막으로 처리한 단일 채널의 cycle_list")

print("\n💡 다음 단계:")
print("  - 특정 채널 선택: cycle_list = all_cycle_lists['channel_name']")
print("  - 카테고리 분류: categories = cycle_categorizer.categorize_cycles(cycle_list)")
print("  - 시각화: cycle_visualizer.plot_all_cycles_overview(cycle_list)")
