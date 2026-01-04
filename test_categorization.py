# -*- coding: utf-8 -*-
"""
사이클 분류 테스트 스크립트

dataprocess.ipynb에서 생성된 cycle_list를 분류하는 예제
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(__file__))

import cycle_categorizer
import importlib

# 모듈 재로딩 (개발 중)
importlib.reload(cycle_categorizer)

print("=" * 80)
print("사이클 분류 테스트")
print("=" * 80)
print()
print("이 스크립트는 dataprocess.ipynb에서 다음과 같이 사용하세요:")
print()
print("```python")
print("# 사이클 분류 모듈 import")
print("import cycle_categorizer")
print("import importlib")
print()
print("# 모듈 재로딩 (수정 시)")
print("importlib.reload(cycle_categorizer)")
print()
print("# 사이클 분류 실행")
print("categories = cycle_categorizer.categorize_cycles(cycle_list)")
print()
print("# 결과 출력")
print("cycle_categorizer.print_categorization_report(cycle_list, categories)")
print()
print("# 특정 카테고리의 사이클만 추출")
print("rpt_cycles = [cycle_list[i] for i in categories['RPT']]")
print("soc_cycles = [cycle_list[i] for i in categories['SOC_Definition']]")
print("resistance_cycles = [cycle_list[i] for i in categories['Resistance_Measurement']]")
print("aging_cycles = [cycle_list[i] for i in categories['Accelerated_Aging']]")
print("```")
print()
print("=" * 80)
