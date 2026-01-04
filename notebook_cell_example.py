import os
import pandas as pd
import matplotlib.pyplot as plt
import data_combiner
import data_storage
import importlib

# 모듈 재로딩 (수정 후 필수!)
importlib.reload(data_combiner)
importlib.reload(data_storage)

# 분석할 경로 리스트 (사용자가 수정)
paths = [
    r"C:\Users\Ryu\Python_project\data\dataprocess\Rawdata\A1_MP1_4500mAh_T23_1",
    # 추가 경로를 여기에 입력하세요
]

print(f"분석 대상 경로 개수: {len(paths)}")

# 데이터 로드
data = data_combiner.process_and_combine(paths)

# 저장 (자동 파일명)
saved_dir = data_storage.save_data(data)

print(f"\n저장 완료: {saved_dir}")
print(f"채널 수: {data['metadata']['total_channels']}")
print(f"Cycler 타입: {data['metadata']['cycler_types']}")
