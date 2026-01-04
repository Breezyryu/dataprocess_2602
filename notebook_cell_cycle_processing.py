# ============================================================================
# Jupyter 노트북 셀 - Cycle List 처리
# ============================================================================

import cycle_list_processor
import importlib

# 모듈 재로딩
importlib.reload(cycle_list_processor)

# ============================================================================
# 방법 1: 함수 사용 (권장)
# ============================================================================

# 모든 채널 처리
all_cycle_lists = cycle_list_processor.process_all_channels(data)

# 특정 채널 선택
channel_key, cycle_list = cycle_list_processor.get_channel_cycle_list(all_cycle_lists, channel_index=0)

# ============================================================================
# 방법 2: 직접 사용
# ============================================================================

# 첫 번째 채널의 cycle_list
first_channel = list(all_cycle_lists.keys())[0]
cycle_list = all_cycle_lists[first_channel]

print(f"\n사용 가능한 변수:")
print(f"  - all_cycle_lists: 모든 채널의 cycle_list")
print(f"  - cycle_list: 선택된 채널의 cycle_list")
print(f"  - channel_key: 선택된 채널 이름")

# ============================================================================
# 사용 예시
# ============================================================================

# 특정 사이클 접근
cycle_1 = cycle_list[0]  # 첫 번째 사이클
print(f"\n첫 번째 사이클 컬럼: {cycle_1.columns.tolist()}")

# 모든 채널 순회
for ch_key, ch_cycle_list in all_cycle_lists.items():
    print(f"{ch_key}: {len(ch_cycle_list)}개 사이클")
