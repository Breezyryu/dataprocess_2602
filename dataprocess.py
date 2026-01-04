"""
배터리 데이터 처리 파이프라인

이 모듈은 PNE와 Toyo 사이클러 데이터를 로드하고 처리하는 완전한 파이프라인을 제공합니다.
모든 유틸리티 함수와 메인 처리 로직이 하나의 파일에 통합되어 있습니다.
"""

import os
import re
import pandas as pd


# ============================================================================
# 유틸리티 함수들
# ============================================================================

def check_cycler(raw_file_path):
    """
    충방전기 구분 (패턴 폴더 유무로 구분)
    
    Parameters:
        raw_file_path (str): 분석할 데이터 경로
    
    Returns:
        str: 'PNE' 또는 'Toyo'
    """
    has_pattern = os.path.isdir(os.path.join(raw_file_path, "Pattern"))
    return "PNE" if has_pattern else "Toyo"


def name_capacity(data_file_path):
    """
    filepath 이름에서 용량을 추출하는 함수
    
    Parameters:
        data_file_path (str): 데이터 경로
    
    Returns:
        float or None: 추출된 용량 (mAh), 없으면 None
    """
    raw_file_path = re.sub(r'[._@$()]', ' ', data_file_path)
    match = re.search(r'(\d+([\-.] \d+)?)mAh', raw_file_path)
    if match:
        min_cap = match.group(1).replace('-', '.')
        return float(min_cap)
    return None


def get_directory_info(path):
    """
    디렉토리 메타 정보 추출
    
    Parameters:
        path (str): 분석할 디렉토리 경로
    
    Returns:
        dict: 폴더명, 서브폴더 개수, 파일 개수, Pattern 폴더 유무, 경로 존재 여부
    """
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
    """
    PNE 채널 폴더 찾기 (M**Ch***[***] 패턴)
    
    Parameters:
        path (str): PNE 데이터 경로
    
    Returns:
        list: 채널 폴더 경로 리스트
    """
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
    """
    Toyo 채널 폴더 찾기 (숫자로만 이루어진 폴더)
    
    Parameters:
        path (str): Toyo 데이터 경로
    
    Returns:
        list: 채널 폴더 경로 리스트
    """
    if not os.path.exists(path):
        return []
    
    channel_folders = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path) and item.isdigit():
            channel_folders.append(item_path)
    
    channel_folders.sort()
    return channel_folders


def load_pne_cycle_data(channel_path):
    """
    PNE 사이클 데이터 로딩 (SaveEndData.csv)
    
    Parameters:
        channel_path (str): PNE 채널 경로
    
    Returns:
        pd.DataFrame or None: 사이클 데이터 DataFrame
    """
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
    """
    PNE 프로파일 데이터 로딩 (SaveData*.csv)
    
    Parameters:
        channel_path (str): PNE 채널 경로
    
    Returns:
        pd.DataFrame or None: 프로파일 데이터 DataFrame
    """
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
    """
    Toyo 사이클 데이터 로딩 (capacity.log)
    
    Parameters:
        channel_path (str): Toyo 채널 경로
    
    Returns:
        pd.DataFrame or None: 사이클 데이터 DataFrame
    """
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
    """
    Toyo 프로파일 데이터 로딩 (처음 max_cycles개 사이클만)
    
    Parameters:
        channel_path (str): Toyo 채널 경로
        max_cycles (int): 로드할 최대 사이클 수
    
    Returns:
        pd.DataFrame or None: 프로파일 데이터 DataFrame
    """
    profile_files = []
    
    # 채널 폴더 내의 모든 .csv 파일 찾기
    if not os.path.isdir(channel_path):
        return None
    
    for file in os.listdir(channel_path):
        if file.endswith('.csv') and 'cycle' in file.lower():
            profile_files.append(file)
    
    profile_files.sort()
    
    if not profile_files:
        return None
    
    # 처음 max_cycles개 파일만 로딩
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
# 메인 처리 함수들
# ============================================================================

def process_battery_data(paths):
    """
    배터리 데이터 처리 파이프라인
    
    Parameters:
        paths (list): 분석할 데이터 경로 리스트
    
    Returns:
        tuple: (df_results, loaded_data)
            - df_results: 각 경로의 메타 정보를 담은 DataFrame
            - loaded_data: 채널별로 구성된 데이터 딕셔너리
              {
                  'channel_name': {
                      'cycler_type': 'PNE' or 'Toyo',
                      'capacity_mAh': float,
                      'folder_name': str,
                      'cycle': DataFrame,
                      'profile': DataFrame
                  },
                  ...
              }
    """
    results = []
    loaded_data = {}  # 채널 중심 구조로 변경
    
    print("=" * 70)
    print("🔋 배터리 데이터 처리 파이프라인 시작")
    print("=" * 70)
    
    for idx, path in enumerate(paths, 1):
        print(f"\n[{idx}/{len(paths)}] 처리 중: {os.path.basename(path)}")
        print("-" * 70)
        
        # 디렉토리 정보 수집
        info = get_directory_info(path)
        
        if not info['exists']:
            print(f"  ⚠️  경로가 존재하지 않습니다: {path}")
            results.append(info)
            continue
        
        print(f"  📁 폴더명: {info['folder_name']}")
        print(f"  🔧 사이클러 타입: {info['cycler_type']}")
        print(f"  ⚡ 용량: {info['capacity_mAh']} mAh" if info['capacity_mAh'] else "  ⚡ 용량: 정보 없음")
        
        # 사이클러 타입에 따라 데이터 로드
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
    
    # 결과를 DataFrame으로 변환
    df_results = pd.DataFrame(results)
    
    return df_results, loaded_data


def _process_pne_data(path, info, loaded_data):
    """
    PNE 데이터 처리 (채널 중심 구조)
    
    Parameters:
        path (str): PNE 데이터 경로
        info (dict): 디렉토리 정보
        loaded_data (dict): 채널별 데이터를 저장할 딕셔너리
    """
    channel_folders = find_pne_channel_folders(path)
    
    if not channel_folders:
        print(f"  ⚠️  PNE 채널 폴더를 찾을 수 없습니다")
        return
    
    print(f"  📊 발견된 채널: {len(channel_folders)}개")
    
    for channel_path in channel_folders:
        channel_name = os.path.basename(channel_path)
        print(f"    - {channel_name} 로딩 중...")
        
        # 채널 키 생성
        key = f"{info['folder_name']}_{channel_name}"
        
        # 채널 정보 초기화
        loaded_data[key] = {
            'cycler_type': 'PNE',
            'capacity_mAh': info['capacity_mAh'],
            'folder_name': info['folder_name'],
            'channel_name': channel_name,
            'cycle': None,
            'profile': None
        }
        
        # 사이클 데이터 로드
        cycle_df = load_pne_cycle_data(channel_path)
        if cycle_df is not None and not cycle_df.empty:
            loaded_data[key]['cycle'] = cycle_df
            print(f"      ✓ 사이클 데이터: {len(cycle_df):,}행")
        else:
            print(f"      ✗ 사이클 데이터 없음")
        
        # 프로파일 데이터 로드
        profile_df = load_pne_profile_data(channel_path)
        if profile_df is not None and not profile_df.empty:
            loaded_data[key]['profile'] = profile_df
            print(f"      ✓ 프로파일 데이터: {len(profile_df):,}행")
        else:
            print(f"      ✗ 프로파일 데이터 없음")


def _process_toyo_data(path, info, loaded_data):
    """
    Toyo 데이터 처리 (채널 중심 구조)
    
    Parameters:
        path (str): Toyo 데이터 경로
        info (dict): 디렉토리 정보
        loaded_data (dict): 채널별 데이터를 저장할 딕셔너리
    """
    channel_folders = find_toyo_channel_folders(path)
    
    if not channel_folders:
        print(f"  ⚠️  Toyo 채널 폴더를 찾을 수 없습니다")
        return
    
    print(f"  📊 발견된 채널: {len(channel_folders)}개")
    
    for channel_path in channel_folders:
        channel_name = os.path.basename(channel_path)
        print(f"    - 채널 {channel_name} 로딩 중...")
        
        # 채널 키 생성
        key = f"{info['folder_name']}_ch{channel_name}"
        
        # 채널 정보 초기화
        loaded_data[key] = {
            'cycler_type': 'Toyo',
            'capacity_mAh': info['capacity_mAh'],
            'folder_name': info['folder_name'],
            'channel_name': f"ch{channel_name}",
            'cycle': None,
            'profile': None
        }
        
        # 사이클 데이터 로드
        cycle_df = load_toyo_cycle_data(channel_path)
        if cycle_df is not None and not cycle_df.empty:
            loaded_data[key]['cycle'] = cycle_df
            print(f"      ✓ 사이클 데이터: {len(cycle_df):,}행")
        else:
            print(f"      ✗ 사이클 데이터 없음")
        
        # 프로파일 데이터 로드 (처음 3개 사이클만)
        profile_df = load_toyo_profile_data(channel_path, max_cycles=3)
        if profile_df is not None and not profile_df.empty:
            loaded_data[key]['profile'] = profile_df
            print(f"      ✓ 프로파일 데이터: {len(profile_df):,}행 (처음 3 사이클)")
        else:
            print(f"      ✗ 프로파일 데이터 없음")


# ============================================================================
# 테스트 코드
# ============================================================================

if __name__ == "__main__":
    # 테스트용 코드
    test_paths = [
        r"C:\Users\Ryu\Python_project\data\dataprocess\Rawdata\A1_MP1_4500mAh_T23_1"
    ]
    
    df_results, loaded_data = process_battery_data(test_paths)
    print("\n결과 요약:")
    print(df_results[['folder_name', 'cycler_type', 'capacity_mAh']])
