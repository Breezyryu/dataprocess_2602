"""
배터리 데이터 처리 통합 모듈

이 모듈은 PNE와 Toyo 사이클러 데이터를 로드, 처리, 분류, 저장하는
완전한 파이프라인을 제공합니다.

주요 기능:
- 데이터 로딩 (PNE, Toyo)
- Cycle list 처리
- 사이클 분류 및 카테고리화
- 데이터 통합 및 저장/로드
"""

import os
import re
import pickle
import pandas as pd
import numpy as np


# ============================================================================
# 유틸리티 함수
# ============================================================================

def check_cycler(raw_file_path):
    """충방전기 구분 (패턴 폴더 유무로 구분)"""
    has_pattern = os.path.isdir(os.path.join(raw_file_path, "Pattern"))
    return "PNE" if has_pattern else "Toyo"


def name_capacity(data_file_path):
    """filepath 이름에서 용량을 추출하는 함수"""
    raw_file_path = re.sub(r'[._@$()]', ' ', data_file_path)
    match = re.search(r'(\d+([\-.] \d+)?)mAh', raw_file_path)
    if match:
        min_cap = match.group(1).replace('-', '.')
        return float(min_cap)
    return None


def get_directory_info(path):
    """디렉토리 메타 정보 추출"""
    info = {
        'path': path,
        'folder_name': os.path.basename(path),
        'exists': os.path.exists(path),
        'has_pattern': False,
        'num_subfolders': 0,
        'num_files': 0,
        'cycler_type': 'Unknown',
        'capacity_mAh': None
    }
    
    if info['exists']:
        info['has_pattern'] = os.path.isdir(os.path.join(path, "Pattern"))
        info['cycler_type'] = check_cycler(path)
        
        try:
            items = os.listdir(path)
            for item in items:
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    info['num_subfolders'] += 1
                else:
                    info['num_files'] += 1
        except PermissionError:
            pass
        
        info['capacity_mAh'] = name_capacity(path)
    
    return info


def find_pne_channel_folders(path):
    """PNE 채널 폴더 찾기 (M**Ch***[***] 패턴)"""
    if not os.path.exists(path):
        return []
    
    channel_folders = []
    pattern = re.compile(r'M\d{2}Ch\d{3}\[\d{3}\]')
    
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path) and pattern.match(item):
            channel_folders.append(item_path)
    
    channel_folders.sort()
    return channel_folders


def find_toyo_channel_folders(path):
    """Toyo 채널 폴더 찾기 (숫자로만 이루어진 폴더)"""
    if not os.path.exists(path):
        return []
    
    channel_folders = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path) and item.isdigit():
            channel_folders.append(item_path)
    
    channel_folders.sort()
    return channel_folders


# ============================================================================
# 데이터 로딩 함수
# ============================================================================

def load_pne_cycle_data(channel_path):
    """PNE 사이클 데이터 로딩 (SaveEndData.csv)"""
    restore_path = os.path.join(channel_path, "Restore")
    
    if not os.path.isdir(restore_path):
        return None
    
    csv_files = [f for f in os.listdir(restore_path) if f.endswith('.csv')]
    end_data_file = None
    
    for file in csv_files:
        if 'SaveEndData' in file:
            end_data_file = file
            break
    
    if not end_data_file:
        return None
    
    try:
        file_path = os.path.join(restore_path, end_data_file)
        if os.stat(file_path).st_size == 0:
            return None
        
        df = pd.read_csv(file_path, sep=',', skiprows=0, engine='c', 
                        header=None, encoding='cp949', on_bad_lines='skip')
        
        df = df[[27, 2, 10, 11, 8, 20, 45, 14, 15, 17, 24, 6, 9]]
        df.columns = ['Cycle', 'Condition', 'ChgCap_mAh','DchgCap_mAh',
        'OCV_mV','imp', 'VoltageMax_mV','ChgPow_mW','DchgPow_mW',
        'Steptime_s', 'Temp_C', 'EndState', 'Current_mA']

        df['Temp_C'] = df['Temp_C'] / 1000
        df['OCV_mV'] = df['OCV_mV'] / 1000
        df['Current_mA'] = df['Current_mA'] / 1000
        df['DchgCap_mAh'] = df['DchgCap_mAh'] / 1000
        df['ChgCap_mAh'] = df['ChgCap_mAh'] / 1000
        df['VoltageMax_mV'] = df['VoltageMax_mV'] / 1000
        df['Steptime_s'] = df['Steptime_s'] / 100
        
        return df
        
    except Exception as e:
        print(f"  ❌ PNE 사이클 데이터 로딩 실패: {e}")
        return None


def load_pne_profile_data(channel_path):
    """PNE 프로파일 데이터 로딩 (SaveData*.csv)"""
    restore_path = os.path.join(channel_path, "Restore")
    
    if not os.path.isdir(restore_path):
        return None
    
    csv_files = [f for f in os.listdir(restore_path) 
                 if f.endswith('.csv') and 'SaveData' in f and 'SaveEndData' not in f]
    csv_files.sort()
    
    if not csv_files:
        return None
    
    dataframes = []
    for file in csv_files:
        try:
            file_path = os.path.join(restore_path, file)
            df_temp = pd.read_csv(file_path, sep=',', skiprows=0, engine='c',
                                 header=None, encoding='cp949', on_bad_lines='skip')
            dataframes.append(df_temp)
        except:
            continue
    
    if dataframes:
        df_combined = pd.concat(dataframes, ignore_index=True)
        df_combined = df_combined[[0, 18, 19, 8, 9, 21, 10, 11, 2, 6,7, 17, 27]]
        df_combined.columns = ['index', 'time_day', 'time_s', 'Voltage_V', 'Current_mA', 
                               'Temp_C', 'ChgCap_mAh', 'DchgCap_mAh', 'Condition','EndState' ,'step', 'Steptime_s', 'Cycle']
        
        df_combined['Temp_C'] = df_combined['Temp_C'] / 1000
        df_combined['Current_mA'] = df_combined['Current_mA'] / 1000
        df_combined['DchgCap_mAh'] = df_combined['DchgCap_mAh'] / 1000
        df_combined['ChgCap_mAh'] = df_combined['ChgCap_mAh'] / 1000
        df_combined['Steptime_s'] = df_combined['Steptime_s'] / 100
        df_combined['time_s'] = (df_combined['time_day'] * 24 * 60 * 60) + df_combined['time_s'] / 100
        df_combined['time_min'] = df_combined['time_s'] / 60
        df_combined['time_hour'] = df_combined['time_min'] / 60
        df_combined['time_day'] = df_combined['time_hour'] / 24
        df_combined['Voltage_V'] = df_combined['Voltage_V'] / 1000
        df_combined = df_combined[df_combined['Condition'] != 8]
        
        return df_combined
    else:
        return None


def load_toyo_cycle_data(channel_path):
    """Toyo 사이클 데이터 로딩 (capacity.log)"""
    capacity_file = os.path.join(channel_path, 'capacity.log')
    
    if not os.path.isfile(capacity_file):
        return None
    
    try:
        df = pd.read_csv(capacity_file, sep=',', skiprows=0, engine='c', 
                        encoding='cp949', on_bad_lines='skip')
        
        if 'Cap[mAh]' in df.columns:
            df = df[['TotlCycle', 'Condition', 'Cap[mAh]', 'Ocv', 'PeakTemp[Deg]', 'AveVolt[V]']]
            df.columns = ['Cycle', 'Condition', 'Capacity_mAh', 'OCV_V', 'Temp_C', 'AvgVolt_V']
        elif 'Capacity[mAh]' in df.columns:
            df = df[['Total Cycle', 'Condition', 'Capacity[mAh]', 'OCV[V]', 'Peak Temp.[deg]', 'Ave. Volt.[V]']]
            df.columns = ['Cycle', 'Condition', 'Capacity_mAh', 'OCV_V', 'Temp_C', 'AvgVolt_V']
        
        return df
        
    except Exception as e:
        print(f"  ❌ Toyo 사이클 데이터 로딩 실패: {e}")
        return None


def load_toyo_profile_data(channel_path, max_cycles=3):
    """Toyo 프로파일 데이터 로딩 (처음 max_cycles개 사이클만)"""
    profile_files = []
    
    if not os.path.isdir(channel_path):
        return None
    
    for file in os.listdir(channel_path):
        if file.endswith('.csv') and 'cycle' in file.lower():
            profile_files.append(file)
    
    profile_files.sort()
    
    if not profile_files:
        return None
    
    dataframes = []
    for file in profile_files[:max_cycles]:
        try:
            file_path = os.path.join(channel_path, file)
            df_temp = pd.read_csv(file_path, sep=',', skiprows=0, engine='c',
                                 encoding='cp949', on_bad_lines='skip')
            dataframes.append(df_temp)
        except:
            continue
    
    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    else:
        return None


# ============================================================================
# 메인 처리 파이프라인
# ============================================================================

def process_battery_data(paths):
    """배터리 데이터 처리 파이프라인"""
    results = []
    loaded_data = {}
    
    print("=" * 70)
    print("🔋 배터리 데이터 처리 파이프라인 시작")
    print("=" * 70)
    
    for idx, path in enumerate(paths, 1):
        print(f"\n[{idx}/{len(paths)}] 처리 중: {os.path.basename(path)}")
        print("-" * 70)
        
        info = get_directory_info(path)
        
        if not info['exists']:
            print(f"  ⚠️  경로가 존재하지 않습니다: {path}")
            results.append(info)
            continue
        
        print(f"  📁 폴더명: {info['folder_name']}")
        print(f"  🔧 사이클러 타입: {info['cycler_type']}")
        print(f"  ⚡ 용량: {info['capacity_mAh']} mAh" if info['capacity_mAh'] else "  ⚡ 용량: 정보 없음")
        
        if info['cycler_type'] == 'PNE':
            _process_pne_data(path, info, loaded_data)
        elif info['cycler_type'] == 'Toyo':
            _process_toyo_data(path, info, loaded_data)
        else:
            print(f"  ❌ 알 수 없는 사이클러 타입")
        
        results.append(info)
    
    print("\n" + "=" * 70)
    print("✅ 데이터 처리 완료")
    print(f"   총 채널 수: {len(loaded_data)}개")
    print("=" * 70)
    
    df_results = pd.DataFrame(results)
    return df_results, loaded_data


def _process_pne_data(path, info, loaded_data):
    """PNE 데이터 처리"""
    channel_folders = find_pne_channel_folders(path)
    
    if not channel_folders:
        print(f"  ⚠️  PNE 채널 폴더를 찾을 수 없습니다")
        return
    
    print(f"  📊 발견된 채널: {len(channel_folders)}개")
    
    for channel_path in channel_folders:
        channel_name = os.path.basename(channel_path)
        print(f"    - {channel_name} 로딩 중...")
        
        key = f"{info['folder_name']}_{channel_name}"
        
        loaded_data[key] = {
            'cycler_type': 'PNE',
            'capacity_mAh': info['capacity_mAh'],
            'folder_name': info['folder_name'],
            'channel_name': channel_name,
            'cycle': None,
            'profile': None
        }
        
        cycle_df = load_pne_cycle_data(channel_path)
        if cycle_df is not None and not cycle_df.empty:
            loaded_data[key]['cycle'] = cycle_df
            print(f"      ✓ 사이클 데이터: {len(cycle_df):,}행")
        else:
            print(f"      ✗ 사이클 데이터 없음")
        
        profile_df = load_pne_profile_data(channel_path)
        if profile_df is not None and not profile_df.empty:
            loaded_data[key]['profile'] = profile_df
            print(f"      ✓ 프로파일 데이터: {len(profile_df):,}행")
        else:
            print(f"      ✗ 프로파일 데이터 없음")


def _process_toyo_data(path, info, loaded_data):
    """Toyo 데이터 처리"""
    channel_folders = find_toyo_channel_folders(path)
    
    if not channel_folders:
        print(f"  ⚠️  Toyo 채널 폴더를 찾을 수 없습니다")
        return
    
    print(f"  📊 발견된 채널: {len(channel_folders)}개")
    
    for channel_path in channel_folders:
        channel_name = os.path.basename(channel_path)
        print(f"    - 채널 {channel_name} 로딩 중...")
        
        key = f"{info['folder_name']}_ch{channel_name}"
        
        loaded_data[key] = {
            'cycler_type': 'Toyo',
            'capacity_mAh': info['capacity_mAh'],
            'folder_name': info['folder_name'],
            'channel_name': f"ch{channel_name}",
            'cycle': None,
            'profile': None
        }
        
        cycle_df = load_toyo_cycle_data(channel_path)
        if cycle_df is not None and not cycle_df.empty:
            loaded_data[key]['cycle'] = cycle_df
            print(f"      ✓ 사이클 데이터: {len(cycle_df):,}행")
        else:
            print(f"      ✗ 사이클 데이터 없음")
        
        profile_df = load_toyo_profile_data(channel_path, max_cycles=3)
        if profile_df is not None and not profile_df.empty:
            loaded_data[key]['profile'] = profile_df
            print(f"      ✓ 프로파일 데이터: {len(profile_df):,}행 (처음 3 사이클)")
        else:
            print(f"      ✗ 프로파일 데이터 없음")


# ============================================================================
# Cycle List 처리
# ============================================================================

def process_all_channels(data):
    """모든 채널에 대해 cycle_list 생성 및 처리"""
    print("="*80)
    print("🔄 전체 채널 Cycle List 처리")
    print("="*80)
    
    for channel_key, channel_data in data['channels'].items():
        print(f"\n처리 중: {channel_key}")
        
        if channel_data['profile'] is None:
            print("  ⚠️ Profile 데이터 없음 - 건너뜀")
            continue
        
        if isinstance(channel_data['profile'], list):
            print("  ℹ️ 이미 처리됨 - 건너뜀")
            continue
        
        df = channel_data['profile']
        
        cycle_list = [group.copy() for _, group in df.groupby('Cycle')]
        
        for cycle in cycle_list:
            cycle['time_cyc'] = cycle['time_s'] - cycle['time_s'].iloc[0]
        
        if channel_data['cycle'] is not None:
            df_cycle = channel_data['cycle']
            
            if 'DchgCap_mAh' in df_cycle.columns:
                mincapa = df_cycle['DchgCap_mAh'].iloc[0]
            elif 'Capacity_mAh' in df_cycle.columns:
                mincapa = df_cycle['Capacity_mAh'].iloc[0]
            else:
                mincapa = channel_data['capacity_mAh'] or 1000
        else:
            mincapa = channel_data['capacity_mAh'] or 1000
        
        for cycle in cycle_list:
            cycle['Capa_cyc'] = (cycle['Current_mA'] * cycle['time_cyc'].diff().fillna(0) / 3600).cumsum()
            cycle['Crate'] = cycle['Current_mA'] / mincapa
        
        channel_data['profile'] = cycle_list
        
        print(f"  ✅ {len(cycle_list)}개 사이클 처리 완료")
    
    print("\n" + "="*80)
    print("📋 처리 결과")
    print("="*80)
    
    processed_channels = {k: v['profile'] for k, v in data['channels'].items() if isinstance(v['profile'], list)}
    total_channels = len(processed_channels)
    total_cycles = sum(len(cycle_list) for cycle_list in processed_channels.values())
    
    print(f"\n처리된 채널 수: {total_channels}개")
    print(f"총 사이클 수: {total_cycles}개")
    
    if processed_channels:
        print(f"\n채널별 사이클 수:")
        for channel_key, cycle_list in processed_channels.items():
            print(f"  - {channel_key}: {len(cycle_list)}개")
    
    print("\n✅ 전체 처리 완료!")
    print("="*80)
    
    return data


def get_channel_cycle_list(data, channel_index=0):
    """특정 채널의 cycle_list 가져오기"""
    channel_keys = list(data['channels'].keys())
    
    if channel_index >= len(channel_keys):
        raise ValueError(f"채널 인덱스 {channel_index}가 범위를 벗어났습니다. (최대: {len(channel_keys)-1})")
    
    channel_key = channel_keys[channel_index]
    cycle_list = data['channels'][channel_key]['profile']
    
    print(f"선택된 채널: {channel_key}")
    print(f"사이클 수: {len(cycle_list) if isinstance(cycle_list, list) else 0}개")
    
    return channel_key, cycle_list


# ============================================================================
# 사이클 분류
# ============================================================================

def categorize_cycle(cycle_df, cycle_index):
    """데이터 특성 기반 사이클 분류"""
    n_points = len(cycle_df)
    voltage_range = cycle_df['Voltage_V'].max() - cycle_df['Voltage_V'].min()
    
    endstate_78_ratio = (cycle_df['EndState'] == 78).sum() / n_points
    endstate_64_ratio = (cycle_df['EndState'] == 64).sum() / n_points
    
    if 'Crate' in cycle_df.columns:
        crate_max = cycle_df['Crate'].abs().max()
    else:
        crate_max = 0
    
    if n_points > 10000:
        return 'Resistance_Measurement'
    
    if endstate_78_ratio > 0.5 and cycle_index < 500:
        return 'SOC_Definition'
    
    if voltage_range < 1400 and crate_max > 1.5:
        return 'Accelerated_Aging'
    
    if endstate_64_ratio > 0.90 and voltage_range > 1400:
        return 'RPT'
    
    return 'Unknown'


def categorize_cycles(cycle_list):
    """전체 cycle_list를 분류"""
    categories = {
        'Unknown': [],
        'RPT': [],
        'SOC_Definition': [],
        'Resistance_Measurement': [],
        'Accelerated_Aging': []
    }
    
    for idx, cycle in enumerate(cycle_list):
        category = categorize_cycle(cycle, idx)
        categories[category].append(idx)
    
    return categories


def add_category_labels(cycle_list, categories=None):
    """각 사이클에 카테고리 라벨을 추가"""
    if categories is None:
        categories = categorize_cycles(cycle_list)
    
    for category, indices in categories.items():
        for idx in indices:
            cycle_list[idx]['category'] = category
    
    return categories


def print_categorization_report(cycle_list, categories):
    """분류 결과 리포트 출력"""
    print("=" * 80)
    print("📊 사이클 분류 결과")
    print("=" * 80)
    print()
    
    for category, indices in categories.items():
        print(f"\n[{category}]")
        print(f"  총 {len(indices)}개 사이클")
        
        if indices:
            print(f"  사이클 인덱스: {indices[:10]}")
            if len(indices) > 10:
                print(f"  ... 외 {len(indices) - 10}개")
            
            first_idx = indices[0]
            cycle = cycle_list[first_idx]
            
            print(f"\n  [대표 사이클 {first_idx} 특성]")
            
            v_min = cycle['Voltage_V'].min()
            v_max = cycle['Voltage_V'].max()
            v_range = v_max - v_min
            print(f"    - Voltage 범위: {v_min:.0f} ~ {v_max:.0f} mV (범위: {v_range:.0f} mV)")
            
            endstate_counts = cycle['EndState'].value_counts()
            endstate_str = ", ".join([f"{int(k)}({v}회)" for k, v in endstate_counts.head(3).items()])
            print(f"    - EndState 패턴: {endstate_str}")
            
            condition_counts = cycle['Condition'].value_counts()
            condition_map = {1: '충전', 2: '방전', 3: 'Rest'}
            condition_str = ", ".join([f"{condition_map.get(k, k)}({v}회)" for k, v in condition_counts.items()])
            print(f"    - Condition: {condition_str}")
            
            if 'Crate' in cycle.columns:
                crate_abs = cycle['Crate'].abs()
                print(f"    - C-rate: 평균 {crate_abs.mean():.3f}C, 최대 {crate_abs.max():.3f}C")
    
    print("\n" + "=" * 80)


# ============================================================================
# 채널 카테고리화
# ============================================================================

def categorize_all_channels(data):
    """data 객체의 모든 채널에 대해 사이클 카테고리화 수행"""
    print("="*80)
    print("🏷️  전체 채널 사이클 카테고리화")
    print("="*80)
    
    for channel_key, channel_data in data['channels'].items():
        print(f"\n처리 중: {channel_key}")
        
        cycle_list = channel_data['profile']
        
        if not isinstance(cycle_list, list):
            print("  ⚠️ Cycle list가 아님 - 건너뜀")
            continue
        
        categories = categorize_cycles(cycle_list)
        
        for category, indices in categories.items():
            for idx in indices:
                cycle_list[idx]['category'] = category
        
        channel_data['cycle_list'] = categories
        
        total_cycles = sum(len(indices) for indices in categories.values())
        print(f"  ✅ {total_cycles}개 사이클 분류 완료")
        for category, indices in categories.items():
            if indices:
                print(f"    - {category}: {len(indices)}개")
    
    print("\n" + "="*80)
    print("📋 카테고리화 결과 요약")
    print("="*80)
    
    processed_channels = [k for k, v in data['channels'].items() if 'cycle_list' in v]
    total_channels = len(processed_channels)
    print(f"\n처리된 채널 수: {total_channels}개")
    
    total_stats = {
        'Unknown': 0,
        'RPT': 0,
        'SOC_Definition': 0,
        'Resistance_Measurement': 0,
        'Accelerated_Aging': 0
    }
    
    for channel_key in processed_channels:
        categories = data['channels'][channel_key]['cycle_list']
        for category, indices in categories.items():
            total_stats[category] += len(indices)
    
    print("\n전체 카테고리별 사이클 수:")
    for category, count in total_stats.items():
        if count > 0:
            print(f"  - {category}: {count}개")
    
    print("\n✅ 전체 카테고리화 완료!")
    print("="*80)
    
    return data


def get_category_cycles(data, channel_index=0, category='RPT'):
    """특정 채널의 특정 카테고리 사이클 가져오기"""
    channel_keys = list(data['channels'].keys())
    
    if channel_index >= len(channel_keys):
        raise ValueError(f"채널 인덱스 {channel_index}가 범위를 벗어났습니다.")
    
    channel_key = channel_keys[channel_index]
    channel_data = data['channels'][channel_key]
    
    if 'cycle_list' not in channel_data:
        raise ValueError(f"채널 {channel_key}에 cycle_list가 없습니다.")
    
    categories = channel_data['cycle_list']
    
    if category not in categories:
        raise ValueError(f"카테고리 '{category}'가 존재하지 않습니다.")
    
    indices = categories[category]
    profile = channel_data['profile']
    
    return [profile[i] for i in indices]


# ============================================================================
# 데이터 통합 및 변환
# ============================================================================

def process_and_combine(paths):
    """paths를 입력받아 데이터 로드 및 통합"""
    df_results, loaded_data = process_battery_data(paths)
    
    cycler_types = {}
    for channel_data in loaded_data.values():
        cycler_type = channel_data['cycler_type']
        cycler_types[cycler_type] = cycler_types.get(cycler_type, 0) + 1
    
    result = {
        'metadata': {
            'total_channels': len(loaded_data),
            'total_paths': len(paths),
            'cycler_types': cycler_types,
            'paths': paths
        },
        'channels': loaded_data
    }
    
    return result


def combine_to_dataframe(loaded_data):
    """채널 기반 loaded_data를 통합 DataFrame으로 변환"""
    all_data = []
    
    for channel_key, channel_data in loaded_data.items():
        if channel_data['cycle'] is not None and len(channel_data['cycle']) > 0:
            df_temp = channel_data['cycle'].copy()
            df_temp['channel'] = channel_key
            df_temp['cycler_type'] = channel_data['cycler_type']
            df_temp['capacity_mAh_meta'] = channel_data['capacity_mAh']
            df_temp['folder_name'] = channel_data['folder_name']
            df_temp['data_type'] = 'cycle'
            all_data.append(df_temp)
        
        if channel_data['profile'] is not None and len(channel_data['profile']) > 0:
            df_temp = channel_data['profile'].copy()
            df_temp['channel'] = channel_key
            df_temp['cycler_type'] = channel_data['cycler_type']
            df_temp['capacity_mAh_meta'] = channel_data['capacity_mAh']
            df_temp['folder_name'] = channel_data['folder_name']
            df_temp['data_type'] = 'profile'
            all_data.append(df_temp)
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        meta_cols = ['channel', 'cycler_type', 'data_type', 'folder_name']
        if 'Cycle' in combined_df.columns:
            meta_cols.append('Cycle')
        
        other_cols = [col for col in combined_df.columns if col not in meta_cols]
        combined_df = combined_df[meta_cols + other_cols]
        
        return combined_df
    else:
        return pd.DataFrame()


# ============================================================================
# 데이터 저장/로드
# ============================================================================

def _generate_filename_from_metadata(data):
    """metadata에서 자동으로 파일명 생성"""
    metadata = data['metadata']
    
    cycler_types = sorted(metadata['cycler_types'].keys())
    cycler_str = '_'.join(cycler_types)
    
    if metadata['paths']:
        first_path = metadata['paths'][0]
        folder_name = os.path.basename(first_path.rstrip('/\\'))
    else:
        folder_name = 'unknown'
    
    filename = f"{cycler_str}_{folder_name}"
    
    return filename


def save_data(data, filepath=None):
    """통합 데이터를 Pickle 파일로 저장"""
    if filepath is None:
        filename = _generate_filename_from_metadata(data)
        filepath = f"{filename}.pkl"
    
    print(f"💾 데이터 저장 중: {filepath}")
    
    with open(filepath, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    file_size = os.path.getsize(filepath) / (1024 * 1024)
    print(f"✅ 저장 완료! 파일: {filepath} ({file_size:.2f} MB)")
    
    return filepath


def load_data(filepath):
    """Pickle 파일에서 데이터 로드"""
    print(f"📂 데이터 로드 중: {filepath}")
    
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    
    channels_count = len(data['channels'])
    print(f"✅ 로드 완료! 채널 수: {channels_count}")
    
    return data


# 하위 호환성을 위한 별칭
save_to_pickle = save_data
load_from_pickle = load_data


# ============================================================================
# 테스트 코드
# ============================================================================

if __name__ == "__main__":
    print("배터리 데이터 처리 통합 모듈")
    print("이 모듈을 import하여 사용하세요.")
