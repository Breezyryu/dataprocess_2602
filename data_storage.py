"""
배터리 데이터 영구 저장 모듈
Pickle 형식으로 저장/로드 지원 (Python 3.14 호환)
"""

import pandas as pd
import os
import json
import pickle


def _generate_filename_from_metadata(data):
    """
    metadata에서 자동으로 파일명 생성
    
    Parameters:
    -----------
    data : dict
        통합 데이터 딕셔너리
    
    Returns:
    --------
    str : 생성된 파일명 (확장자 제외)
    """
    metadata = data['metadata']
    
    # Cycler 타입 추출 (예: PNE, Toyo, PNE_Toyo)
    cycler_types = sorted(metadata['cycler_types'].keys())
    cycler_str = '_'.join(cycler_types)
    
    # 첫 번째 path의 마지막 폴더 이름 추출
    if metadata['paths']:
        first_path = metadata['paths'][0]
        folder_name = os.path.basename(first_path.rstrip('/\\'))
    else:
        folder_name = 'unknown'
    
    # 파일명 생성: {cycler_type}_{folder_name}
    filename = f"{cycler_str}_{folder_name}"
    
    return filename


def save_data(data, filepath=None):
    """
    통합 데이터를 Pickle 파일로 저장
    
    Parameters:
    -----------
    data : dict
        process_and_combine()의 출력
    filepath : str, optional
        저장할 파일 경로 (.pkl)
        None이면 metadata에서 자동 생성
    
    Returns:
    --------
    str : 저장된 파일 경로
    """
    
    # 파일명 자동 생성
    if filepath is None:
        filename = _generate_filename_from_metadata(data)
        filepath = f"{filename}.pkl"
    
    print(f"💾 데이터 저장 중: {filepath}")
    
    # Pickle로 저장
    with open(filepath, 'wb') as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
    print(f"✅ 저장 완료! 파일: {filepath} ({file_size:.2f} MB)")
    
    return filepath


def load_data(filepath):
    """
    Pickle 파일에서 데이터 로드
    
    Parameters:
    -----------
    filepath : str
        Pickle 파일 경로 (.pkl)
    
    Returns:
    --------
    dict : 통합 데이터 딕셔너리
    """
    
    print(f"📂 데이터 로드 중: {filepath}")
    
    # Pickle에서 로드
    with open(filepath, 'rb') as f:
        data = pickle.load(f)
    
    channels_count = len(data['channels'])
    print(f"✅ 로드 완료! 채널 수: {channels_count}")
    
    return data


def get_storage_info(filepath):
    """
    저장된 데이터 정보 확인
    
    Parameters:
    -----------
    filepath : str
        Pickle 파일 경로
    """
    
    print("="*80)
    print("📊 저장된 데이터 정보")
    print("="*80)
    
    if os.path.isfile(filepath):
        file_size = os.path.getsize(filepath) / (1024*1024)
        
        print(f"\n파일: {filepath}")
        print(f"크기: {file_size:.2f} MB")
        
        # 데이터 로드하여 정보 확인
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            
            print(f"\n메타데이터:")
            print(f"  - 총 채널 수: {data['metadata']['total_channels']}")
            print(f"  - Cycler 타입: {data['metadata']['cycler_types']}")
            
            print(f"\n채널 목록:")
            for channel_key in data['channels'].keys():
                print(f"  - {channel_key}")
        except Exception as e:
            print(f"\n⚠️ 데이터 로드 실패: {e}")
    else:
        print(f"\n❌ 파일을 찾을 수 없습니다: {filepath}")
    
    print("\n" + "="*80)


# 하위 호환성을 위한 별칭
save_to_parquet = save_data
load_from_parquet = load_data
save_to_pickle = save_data
load_from_pickle = load_data
