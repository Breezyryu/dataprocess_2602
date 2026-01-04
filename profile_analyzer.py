# -*- coding: utf-8 -*-
"""
Profile 데이터 분석 모듈

배터리 profile 데이터를 분석, 필터링, 시각화하는 함수들을 제공합니다.
인터랙티브 시각화를 위해 Plotly를 사용합니다.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Tuple


# ============================================================================
# 데이터 구조 분석 함수
# ============================================================================

def analyze_profile_structure(loaded_data: Dict) -> pd.DataFrame:
    """
    Profile 데이터 구조 분석 및 요약
    
    Parameters:
        loaded_data (dict): process_battery_data()에서 반환된 loaded_data
    
    Returns:
        pd.DataFrame: 각 채널별 데이터 요약 정보
    """
    summary_data = []
    
    print("=" * 80)
    print("📊 PROFILE 데이터 구조 분석")
    print("=" * 80)
    
    # PNE Profile 데이터 분석
    if loaded_data.get('pne_profile'):
        print("\n🔧 PNE Profile 데이터:")
        print("-" * 80)
        
        for key, df in loaded_data['pne_profile'].items():
            print(f"\n채널: {key}")
            print(f"  - 행 개수: {len(df):,}")
            print(f"  - 컬럼: {list(df.columns)}")
            
            # 고유값 분석
            if 'Condition' in df.columns:
                conditions = df['Condition'].unique()
                print(f"  - Condition 고유값: {sorted(conditions)}")
                for cond in sorted(conditions):
                    count = len(df[df['Condition'] == cond])
                    print(f"    • Condition {cond}: {count:,}행")
            
            if 'EndState' in df.columns:
                endstates = df['EndState'].unique()
                print(f"  - EndState 고유값: {sorted(endstates)[:10]}...")  # 처음 10개만
            
            if 'step' in df.columns:
                steps = df['step'].unique()
                print(f"  - Step 고유값 개수: {len(steps)}")
                print(f"  - Step 범위: {df['step'].min()} ~ {df['step'].max()}")
            
            # 요약 데이터 저장
            summary_data.append({
                'channel': key,
                'type': 'PNE',
                'rows': len(df),
                'columns': len(df.columns),
                'conditions': len(df['Condition'].unique()) if 'Condition' in df.columns else 0,
                'steps': len(df['step'].unique()) if 'step' in df.columns else 0,
                'voltage_range': f"{df['Voltage_V'].min():.2f} ~ {df['Voltage_V'].max():.2f}" if 'Voltage_V' in df.columns else 'N/A',
                'current_range': f"{df['Current_mA'].min():.2f} ~ {df['Current_mA'].max():.2f}" if 'Current_mA' in df.columns else 'N/A'
            })
    
    # Toyo Profile 데이터 분석
    if loaded_data.get('toyo_profile'):
        print("\n\n🔧 Toyo Profile 데이터:")
        print("-" * 80)
        
        for key, df in loaded_data['toyo_profile'].items():
            print(f"\n채널: {key}")
            print(f"  - 행 개수: {len(df):,}")
            print(f"  - 컬럼: {list(df.columns)}")
            
            # 요약 데이터 저장
            summary_data.append({
                'channel': key,
                'type': 'Toyo',
                'rows': len(df),
                'columns': len(df.columns),
                'conditions': 0,
                'steps': 0,
                'voltage_range': 'N/A',
                'current_range': 'N/A'
            })
    
    print("\n" + "=" * 80)
    
    return pd.DataFrame(summary_data)


# ============================================================================
# 필터링 함수
# ============================================================================

def filter_by_condition(df: pd.DataFrame, condition: int) -> pd.DataFrame:
    """
    Condition으로 필터링
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
        condition (int): 1=충전, 2=방전
    
    Returns:
        pd.DataFrame: 필터링된 데이터
    """
    if 'Condition' not in df.columns:
        print("⚠️  'Condition' 컬럼이 없습니다.")
        return df
    
    filtered = df[df['Condition'] == condition].copy()
    
    condition_name = {1: '충전', 2: '방전'}.get(condition, f'Condition {condition}')
    print(f"✓ {condition_name} 데이터 필터링: {len(filtered):,}행 (전체의 {len(filtered)/len(df)*100:.1f}%)")
    
    return filtered


def filter_by_step(df: pd.DataFrame, steps: List[int]) -> pd.DataFrame:
    """
    특정 step으로 필터링
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
        steps (list): 필터링할 step 리스트
    
    Returns:
        pd.DataFrame: 필터링된 데이터
    """
    if 'step' not in df.columns:
        print("⚠️  'step' 컬럼이 없습니다.")
        return df
    
    filtered = df[df['step'].isin(steps)].copy()
    
    print(f"✓ Step {steps} 데이터 필터링: {len(filtered):,}행 (전체의 {len(filtered)/len(df)*100:.1f}%)")
    
    return filtered


def identify_cccv_phases(df: pd.DataFrame, cv_current_threshold: float = 50.0) -> pd.DataFrame:
    """
    CCCV 충전 구간 식별 (CC: Constant Current, CV: Constant Voltage)
    
    Parameters:
        df (pd.DataFrame): 충전 profile 데이터
        cv_current_threshold (float): CV 구간 판단 전류 임계값 (mA)
    
    Returns:
        pd.DataFrame: 'phase' 컬럼이 추가된 데이터 ('CC' 또는 'CV')
    """
    if 'Current_mA' not in df.columns:
        print("⚠️  'Current_mA' 컬럼이 없습니다.")
        return df
    
    df_copy = df.copy()
    
    # 전류의 절대값이 임계값보다 작으면 CV, 크면 CC
    df_copy['phase'] = df_copy['Current_mA'].abs().apply(
        lambda x: 'CV' if x < cv_current_threshold else 'CC'
    )
    
    cc_count = len(df_copy[df_copy['phase'] == 'CC'])
    cv_count = len(df_copy[df_copy['phase'] == 'CV'])
    
    print(f"✓ CCCV 구간 식별 완료:")
    print(f"  - CC (정전류) 구간: {cc_count:,}행 ({cc_count/len(df_copy)*100:.1f}%)")
    print(f"  - CV (정전압) 구간: {cv_count:,}행 ({cv_count/len(df_copy)*100:.1f}%)")
    
    return df_copy


def identify_rpt_cycles(cycle_df: pd.DataFrame, rpt_pattern: Optional[int] = None) -> List[int]:
    """
    RPT (Reference Performance Test) 사이클 식별
    
    Parameters:
        cycle_df (pd.DataFrame): 사이클 데이터
        rpt_pattern (int): RPT 주기 (예: 50이면 50, 100, 150... 사이클)
    
    Returns:
        list: RPT 사이클 번호 리스트
    """
    if 'Cycle' not in cycle_df.columns:
        print("⚠️  'Cycle' 컬럼이 없습니다.")
        return []
    
    all_cycles = sorted(cycle_df['Cycle'].unique())
    
    if rpt_pattern:
        # 패턴 기반 RPT 식별
        rpt_cycles = [c for c in all_cycles if c % rpt_pattern == 0]
    else:
        # 첫 사이클과 마지막 사이클을 RPT로 간주
        rpt_cycles = [all_cycles[0], all_cycles[-1]]
    
    print(f"✓ RPT 사이클 식별: {len(rpt_cycles)}개")
    print(f"  - 사이클 번호: {rpt_cycles[:10]}{'...' if len(rpt_cycles) > 10 else ''}")
    
    return rpt_cycles


# ============================================================================
# 성능 최적화 함수
# ============================================================================

def downsample_data(df: pd.DataFrame, max_points: int = 10000) -> pd.DataFrame:
    """
    대용량 데이터 다운샘플링 (시각화 성능 최적화)
    
    Parameters:
        df (pd.DataFrame): 원본 데이터
        max_points (int): 최대 데이터 포인트 수
    
    Returns:
        pd.DataFrame: 다운샘플링된 데이터
    """
    if len(df) <= max_points:
        return df
    
    # 균등 간격 샘플링
    step = len(df) // max_points
    sampled = df.iloc[::step].copy()
    
    print(f"📉 다운샘플링: {len(df):,}행 → {len(sampled):,}행 (시각화 성능 최적화)")
    
    return sampled


# ============================================================================
# 시각화 함수 (Plotly 인터랙티브)
# ============================================================================

def visualize_profile_overview(df: pd.DataFrame, title: str = "Profile 데이터 개요", 
                               max_points: int = 50000):
    """
    Profile 데이터 전체 개요 시각화 (인터랙티브)
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
        title (str): 그래프 제목
        max_points (int): 최대 표시 포인트 수 (성능 최적화)
    """
    # 다운샘플링
    df_plot = downsample_data(df, max_points)
    
    # 서브플롯 생성
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('전압 (V)', '전류 (mA)', '용량 (mAh)'),
        vertical_spacing=0.08,
        shared_xaxes=True
    )
    
    # 전압 프로파일
    if 'Voltage_V' in df_plot.columns and 'time_s' in df_plot.columns:
        fig.add_trace(
            go.Scatter(
                x=df_plot['time_s'], 
                y=df_plot['Voltage_V'],
                mode='lines',
                name='전압',
                line=dict(color='#1f77b4', width=1),
                hovertemplate='시간: %{x:.0f}s<br>전압: %{y:.2f}V<extra></extra>'
            ),
            row=1, col=1
        )
    
    # 전류 프로파일
    if 'Current_mA' in df_plot.columns and 'time_s' in df_plot.columns:
        fig.add_trace(
            go.Scatter(
                x=df_plot['time_s'], 
                y=df_plot['Current_mA'],
                mode='lines',
                name='전류',
                line=dict(color='#ff7f0e', width=1),
                hovertemplate='시간: %{x:.0f}s<br>전류: %{y:.2f}mA<extra></extra>'
            ),
            row=2, col=1
        )
    
    # 용량 프로파일
    if 'ChgCap_mAh' in df_plot.columns and 'DchgCap_mAh' in df_plot.columns and 'time_s' in df_plot.columns:
        fig.add_trace(
            go.Scatter(
                x=df_plot['time_s'], 
                y=df_plot['ChgCap_mAh'],
                mode='lines',
                name='충전 용량',
                line=dict(color='#2ca02c', width=1),
                hovertemplate='시간: %{x:.0f}s<br>충전: %{y:.2f}mAh<extra></extra>'
            ),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=df_plot['time_s'], 
                y=df_plot['DchgCap_mAh'],
                mode='lines',
                name='방전 용량',
                line=dict(color='#d62728', width=1),
                hovertemplate='시간: %{x:.0f}s<br>방전: %{y:.2f}mAh<extra></extra>'
            ),
            row=3, col=1
        )
    
    # 레이아웃 설정
    fig.update_xaxes(title_text="시간 (s)", row=3, col=1)
    fig.update_yaxes(title_text="전압 (V)", row=1, col=1)
    fig.update_yaxes(title_text="전류 (mA)", row=2, col=1)
    fig.update_yaxes(title_text="용량 (mAh)", row=3, col=1)
    
    fig.update_layout(
        title=title,
        height=900,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )
    
    fig.show()


def visualize_voltage_profile(df: pd.DataFrame, color_by: str = 'Condition', 
                              title: str = "전압 프로파일", max_points: int = 50000):
    """
    전압 프로파일 시각화 (Condition 또는 step으로 색상 구분, 인터랙티브)
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
        color_by (str): 색상 구분 기준 ('Condition' 또는 'step')
        title (str): 그래프 제목
        max_points (int): 최대 표시 포인트 수
    """
    if 'Voltage_V' not in df.columns or 'time_s' not in df.columns:
        print("⚠️  'Voltage_V' 또는 'time_s' 컬럼이 없습니다.")
        return
    
    # 다운샘플링
    df_plot = downsample_data(df, max_points)
    
    fig = go.Figure()
    
    if color_by in df_plot.columns:
        unique_values = sorted(df_plot[color_by].unique())
        colors = px.colors.qualitative.Plotly
        
        for idx, value in enumerate(unique_values):
            subset = df_plot[df_plot[color_by] == value]
            label = f'{color_by} {value}'
            if color_by == 'Condition':
                label = {1: '충전', 2: '방전', 3: 'Rest', 8: 'CCCV'}.get(value, f'Condition {value}')
            
            fig.add_trace(
                go.Scatter(
                    x=subset['time_s'],
                    y=subset['Voltage_V'],
                    mode='lines',
                    name=label,
                    line=dict(color=colors[idx % len(colors)], width=1.5),
                    hovertemplate=f'{label}<br>시간: %{{x:.0f}}s<br>전압: %{{y:.2f}}V<extra></extra>'
                )
            )
    else:
        fig.add_trace(
            go.Scatter(
                x=df_plot['time_s'],
                y=df_plot['Voltage_V'],
                mode='lines',
                name='전압',
                line=dict(width=1.5),
                hovertemplate='시간: %{x:.0f}s<br>전압: %{y:.2f}V<extra></extra>'
            )
        )
    
    fig.update_layout(
        title=title,
        xaxis_title='시간 (s)',
        yaxis_title='전압 (V)',
        height=600,
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    fig.show()


def visualize_current_profile(df: pd.DataFrame, title: str = "전류 프로파일", 
                              max_points: int = 50000):
    """
    전류 프로파일 시각화 (인터랙티브)
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
        title (str): 그래프 제목
        max_points (int): 최대 표시 포인트 수
    """
    if 'Current_mA' not in df.columns or 'time_s' not in df.columns:
        print("⚠️  'Current_mA' 또는 'time_s' 컬럼이 없습니다.")
        return
    
    # 다운샘플링
    df_plot = downsample_data(df, max_points)
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df_plot['time_s'],
            y=df_plot['Current_mA'],
            mode='lines',
            name='전류',
            line=dict(color='#ff7f0e', width=1.5),
            hovertemplate='시간: %{x:.0f}s<br>전류: %{y:.2f}mA<extra></extra>'
        )
    )
    
    # 0 기준선
    fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.5)
    
    fig.update_layout(
        title=title,
        xaxis_title='시간 (s)',
        yaxis_title='전류 (mA)',
        height=600,
        hovermode='x unified',
        template='plotly_white'
    )
    
    fig.show()


def visualize_capacity_evolution(cycle_df: pd.DataFrame, title: str = "사이클별 용량 변화"):
    """
    사이클별 용량 변화 시각화 (인터랙티브)
    
    Parameters:
        cycle_df (pd.DataFrame): 사이클 데이터
        title (str): 그래프 제목
    """
    if 'Cycle' not in cycle_df.columns:
        print("⚠️  'Cycle' 컬럼이 없습니다.")
        return
    
    fig = go.Figure()
    
    # 충전 용량
    if 'ChgCap_mAh' in cycle_df.columns:
        fig.add_trace(
            go.Scatter(
                x=cycle_df['Cycle'],
                y=cycle_df['ChgCap_mAh'],
                mode='lines+markers',
                name='충전 용량',
                marker=dict(size=4),
                line=dict(width=2),
                hovertemplate='사이클: %{x}<br>충전: %{y:.2f}mAh<extra></extra>'
            )
        )
    
    # 방전 용량
    if 'DchgCap_mAh' in cycle_df.columns:
        fig.add_trace(
            go.Scatter(
                x=cycle_df['Cycle'],
                y=cycle_df['DchgCap_mAh'],
                mode='lines+markers',
                name='방전 용량',
                marker=dict(size=4, symbol='square'),
                line=dict(width=2),
                hovertemplate='사이클: %{x}<br>방전: %{y:.2f}mAh<extra></extra>'
            )
        )
    
    # Toyo 데이터의 경우
    if 'Capacity_mAh' in cycle_df.columns:
        fig.add_trace(
            go.Scatter(
                x=cycle_df['Cycle'],
                y=cycle_df['Capacity_mAh'],
                mode='lines+markers',
                name='용량',
                marker=dict(size=4),
                line=dict(width=2),
                hovertemplate='사이클: %{x}<br>용량: %{y:.2f}mAh<extra></extra>'
            )
        )
    
    fig.update_layout(
        title=title,
        xaxis_title='사이클',
        yaxis_title='용량 (mAh)',
        height=600,
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.show()


def visualize_condition_distribution(df: pd.DataFrame, title: str = "Condition 분포"):
    """
    Condition별 데이터 분포 시각화 (인터랙티브)
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
        title (str): 그래프 제목
    """
    if 'Condition' not in df.columns:
        print("⚠️  'Condition' 컬럼이 없습니다.")
        return
    
    condition_counts = df['Condition'].value_counts().sort_index()
    
    # 레이블 변경
    labels = []
    for cond in condition_counts.index:
        label = {1: '충전', 2: '방전', 3: 'Rest', 8: 'CCCV'}.get(cond, f'Condition {cond}')
        labels.append(label)
    
    # 비율 계산
    total = condition_counts.sum()
    percentages = (condition_counts / total * 100).round(1)
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            x=labels,
            y=condition_counts.values,
            text=[f'{count:,}<br>({pct}%)' for count, pct in zip(condition_counts.values, percentages)],
            textposition='outside',
            marker=dict(
                color=condition_counts.values,
                colorscale='Viridis',
                showscale=False
            ),
            hovertemplate='%{x}<br>개수: %{y:,}<br>비율: %{text}<extra></extra>'
        )
    )
    
    fig.update_layout(
        title=title,
        xaxis_title='Condition',
        yaxis_title='데이터 개수',
        height=600,
        template='plotly_white',
        showlegend=False
    )
    
    fig.show()


# ============================================================================
# 유틸리티 함수
# ============================================================================

def get_profile_summary(df: pd.DataFrame) -> Dict:
    """
    Profile 데이터 요약 정보 반환
    
    Parameters:
        df (pd.DataFrame): Profile 데이터
    
    Returns:
        dict: 요약 정보
    """
    summary = {
        'total_rows': len(df),
        'columns': list(df.columns),
        'time_range': f"{df['time_s'].min():.2f} ~ {df['time_s'].max():.2f} s" if 'time_s' in df.columns else 'N/A',
        'voltage_range': f"{df['Voltage_V'].min():.2f} ~ {df['Voltage_V'].max():.2f} V" if 'Voltage_V' in df.columns else 'N/A',
        'current_range': f"{df['Current_mA'].min():.2f} ~ {df['Current_mA'].max():.2f} mA" if 'Current_mA' in df.columns else 'N/A',
    }
    
    if 'Condition' in df.columns:
        summary['conditions'] = df['Condition'].unique().tolist()
    
    if 'step' in df.columns:
        summary['steps'] = len(df['step'].unique())
    
    return summary


if __name__ == "__main__":
    print("Profile Analyzer 모듈 (Plotly 인터랙티브 버전)")
    print("사용 가능한 함수:")
    print("  - analyze_profile_structure()")
    print("  - filter_by_condition()")
    print("  - filter_by_step()")
    print("  - identify_cccv_phases()")
    print("  - identify_rpt_cycles()")
    print("  - downsample_data()")
    print("  - visualize_profile_overview()")
    print("  - visualize_voltage_profile()")
    print("  - visualize_current_profile()")
    print("  - visualize_capacity_evolution()")
    print("  - visualize_condition_distribution()")
    print("  - get_profile_summary()")
