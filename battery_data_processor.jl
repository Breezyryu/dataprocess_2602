"""
배터리 데이터 처리 통합 모듈 (Julia 버전)

이 모듈은 PNE와 Toyo 사이클러 데이터를 로드, 처리, 분류, 저장하는
완전한 파이프라인을 제공합니다.

주요 기능:
- 데이터 로딩 (PNE, Toyo)
- Cycle list 처리
- 사이클 분류 및 카테고리화
- 데이터 통합 및 저장/로드
"""

using DataFrames
using CSV
using Serialization
using Statistics

# ============================================================================
# 유틸리티 함수
# ============================================================================

"""
충방전기 구분 (패턴 폴더 유무로 구분)
"""
function check_cycler(raw_file_path::String)::String
    has_pattern = isdir(joinpath(raw_file_path, "Pattern"))
    return has_pattern ? "PNE" : "Toyo"
end

"""
filepath 이름에서 용량을 추출하는 함수
"""
function name_capacity(data_file_path::String)::Union{Float64, Nothing}
    raw_file_path = replace(data_file_path, r"[._@$()]" => " ")
    m = match(r"(\d+([-.] \d+)?)mAh", raw_file_path)
    if m !== nothing
        min_cap = replace(m.captures[1], "-" => ".")
        return parse(Float64, min_cap)
    end
    return nothing
end

"""
디렉토리 메타 정보 추출
"""
function get_directory_info(path::String)::Dict{String, Any}
    info = Dict{String, Any}(
        "path" => path,
        "folder_name" => basename(path),
        "exists" => isdir(path) || isfile(path),
        "has_pattern" => false,
        "num_subfolders" => 0,
        "num_files" => 0,
        "cycler_type" => "Unknown",
        "capacity_mAh" => nothing
    )
    
    if info["exists"] && isdir(path)
        info["has_pattern"] = isdir(joinpath(path, "Pattern"))
        info["cycler_type"] = check_cycler(path)
        
        try
            items = readdir(path)
            for item in items
                item_path = joinpath(path, item)
                if isdir(item_path)
                    info["num_subfolders"] += 1
                else
                    info["num_files"] += 1
                end
            end
        catch e
            # PermissionError 등 무시
        end
        
        info["capacity_mAh"] = name_capacity(path)
    end
    
    return info
end

"""
PNE 채널 폴더 찾기 (M**Ch***[***] 패턴)
"""
function find_pne_channel_folders(path::String)::Vector{String}
    if !isdir(path)
        return String[]
    end
    
    channel_folders = String[]
    pattern = r"M\d{2}Ch\d{3}\[\d{3}\]"
    
    for item in readdir(path)
        item_path = joinpath(path, item)
        if isdir(item_path) && occursin(pattern, item)
            push!(channel_folders, item_path)
        end
    end
    
    sort!(channel_folders)
    return channel_folders
end

"""
Toyo 채널 폴더 찾기 (숫자로만 이루어진 폴더)
"""
function find_toyo_channel_folders(path::String)::Vector{String}
    if !isdir(path)
        return String[]
    end
    
    channel_folders = String[]
    for item in readdir(path)
        item_path = joinpath(path, item)
        if isdir(item_path) && all(isdigit, item)
            push!(channel_folders, item_path)
        end
    end
    
    sort!(channel_folders)
    return channel_folders
end


# ============================================================================
# 데이터 로딩 함수
# ============================================================================

"""
PNE 사이클 데이터 로딩 (SaveEndData.csv)
"""
function load_pne_cycle_data(channel_path::String)::Union{DataFrame, Nothing}
    restore_path = joinpath(channel_path, "Restore")
    
    if !isdir(restore_path)
        return nothing
    end
    
    csv_files = filter(f -> endswith(f, ".csv"), readdir(restore_path))
    end_data_file = nothing
    
    for file in csv_files
        if occursin("SaveEndData", file)
            end_data_file = file
            break
        end
    end
    
    if end_data_file === nothing
        return nothing
    end
    
    try
        file_path = joinpath(restore_path, end_data_file)
        if filesize(file_path) == 0
            return nothing
        end
        
        df = CSV.read(file_path, DataFrame, 
                     header=false, 
                     silencewarnings=true)
        
        # 필요한 컬럼만 선택 (Python의 인덱스는 0부터, Julia는 1부터)
        # [27, 2, 10, 11, 8, 20, 45, 14, 15, 17, 24, 6, 9] -> +1
        df = df[:, [28, 3, 11, 12, 9, 21, 46, 15, 16, 18, 25, 7, 10]]
        rename!(df, [
            :Cycle, :Condition, :ChgCap_mAh, :DchgCap_mAh,
            :OCV_mV, :imp, :VoltageMax_mV, :ChgPow_mW, :DchgPow_mW,
            :Steptime_s, :Temp_C, :EndState, :Current_mA
        ])
        
        # 단위 변환
        df.Temp_C = df.Temp_C ./ 1000
        df.OCV_mV = df.OCV_mV ./ 1000
        df.Current_mA = df.Current_mA ./ 1000
        df.DchgCap_mAh = df.DchgCap_mAh ./ 1000
        df.ChgCap_mAh = df.ChgCap_mAh ./ 1000
        df.VoltageMax_mV = df.VoltageMax_mV ./ 1000
        df.Steptime_s = df.Steptime_s ./ 100
        
        return df
        
    catch e
        println("  ❌ PNE 사이클 데이터 로딩 실패: $e")
        return nothing
    end
end

"""
PNE 프로파일 데이터 로딩 (SaveData*.csv)
"""
function load_pne_profile_data(channel_path::String)::Union{DataFrame, Nothing}
    restore_path = joinpath(channel_path, "Restore")
    
    if !isdir(restore_path)
        return nothing
    end
    
    csv_files = filter(readdir(restore_path)) do f
        endswith(f, ".csv") && occursin("SaveData", f) && !occursin("SaveEndData", f)
    end
    sort!(csv_files)
    
    if isempty(csv_files)
        return nothing
    end
    
    dataframes = DataFrame[]
    for file in csv_files
        try
            file_path = joinpath(restore_path, file)
            df_temp = CSV.read(file_path, DataFrame,
                             header=false,
                             silencewarnings=true)
            push!(dataframes, df_temp)
        catch
            continue
        end
    end
    
    if !isempty(dataframes)
        df_combined = vcat(dataframes...)
        # [0, 18, 19, 8, 9, 21, 10, 11, 2, 6, 7, 17, 27] -> +1
        df_combined = df_combined[:, [1, 19, 20, 9, 10, 22, 11, 12, 3, 7, 8, 18, 28]]
        rename!(df_combined, [
            :index, :time_day, :time_s, :Voltage_V, :Current_mA,
            :Temp_C, :ChgCap_mAh, :DchgCap_mAh, :Condition, :EndState,
            :step, :Steptime_s, :Cycle
        ])
        
        # 단위 변환
        df_combined.Temp_C = df_combined.Temp_C ./ 1000
        df_combined.Current_mA = df_combined.Current_mA ./ 1000
        df_combined.DchgCap_mAh = df_combined.DchgCap_mAh ./ 1000
        df_combined.ChgCap_mAh = df_combined.ChgCap_mAh ./ 1000
        df_combined.Steptime_s = df_combined.Steptime_s ./ 100
        df_combined.time_s = (df_combined.time_day .* 24 .* 60 .* 60) .+ df_combined.time_s ./ 100
        df_combined.time_min = df_combined.time_s ./ 60
        df_combined.time_hour = df_combined.time_min ./ 60
        df_combined.time_day = df_combined.time_hour ./ 24
        df_combined.Voltage_V = df_combined.Voltage_V ./ 1000
        
        # Condition != 8 필터링
        df_combined = filter(row -> row.Condition != 8, df_combined)
        
        return df_combined
    else
        return nothing
    end
end

"""
Toyo 사이클 데이터 로딩 (capacity.log)
"""
function load_toyo_cycle_data(channel_path::String)::Union{DataFrame, Nothing}
    capacity_file = joinpath(channel_path, "capacity.log")
    
    if !isfile(capacity_file)
        return nothing
    end
    
    try
        df = CSV.read(capacity_file, DataFrame, silencewarnings=true)
        
        if "Cap[mAh]" in names(df)
            df = df[:, [:TotlCycle, :Condition, Symbol("Cap[mAh]"), :Ocv, Symbol("PeakTemp[Deg]"), Symbol("AveVolt[V]")]]
            rename!(df, [:Cycle, :Condition, :Capacity_mAh, :OCV_V, :Temp_C, :AvgVolt_V])
        elseif "Capacity[mAh]" in names(df)
            df = df[:, [Symbol("Total Cycle"), :Condition, Symbol("Capacity[mAh]"), Symbol("OCV[V]"), Symbol("Peak Temp.[deg]"), Symbol("Ave. Volt.[V]")]]
            rename!(df, [:Cycle, :Condition, :Capacity_mAh, :OCV_V, :Temp_C, :AvgVolt_V])
        end
        
        return df
        
    catch e
        println("  ❌ Toyo 사이클 데이터 로딩 실패: $e")
        return nothing
    end
end

"""
Toyo 프로파일 데이터 로딩 (처음 max_cycles개 사이클만)
"""
function load_toyo_profile_data(channel_path::String; max_cycles::Int=3)::Union{DataFrame, Nothing}
    if !isdir(channel_path)
        return nothing
    end
    
    profile_files = filter(readdir(channel_path)) do file
        endswith(file, ".csv") && occursin("cycle", lowercase(file))
    end
    sort!(profile_files)
    
    if isempty(profile_files)
        return nothing
    end
    
    dataframes = DataFrame[]
    for file in profile_files[1:min(max_cycles, length(profile_files))]
        try
            file_path = joinpath(channel_path, file)
            df_temp = CSV.read(file_path, DataFrame, silencewarnings=true)
            push!(dataframes, df_temp)
        catch
            continue
        end
    end
    
    if !isempty(dataframes)
        return vcat(dataframes...)
    else
        return nothing
    end
end


# ============================================================================
# 메인 처리 파이프라인
# ============================================================================

"""
배터리 데이터 처리 파이프라인
"""
function process_battery_data(paths::Vector{String})
    results = []
    loaded_data = Dict{String, Any}()
    
    println("=" ^ 70)
    println("🔋 배터리 데이터 처리 파이프라인 시작")
    println("=" ^ 70)
    
    for (idx, path) in enumerate(paths)
        println("\n[$(idx)/$(length(paths))] 처리 중: $(basename(path))")
        println("-" ^ 70)
        
        info = get_directory_info(path)
        
        if !info["exists"]
            println("  ⚠️  경로가 존재하지 않습니다: $path")
            push!(results, info)
            continue
        end
        
        println("  📁 폴더명: $(info["folder_name"])")
        println("  🔧 사이클러 타입: $(info["cycler_type"])")
        if info["capacity_mAh"] !== nothing
            println("  ⚡ 용량: $(info["capacity_mAh"]) mAh")
        else
            println("  ⚡ 용량: 정보 없음")
        end
        
        if info["cycler_type"] == "PNE"
            _process_pne_data!(path, info, loaded_data)
        elseif info["cycler_type"] == "Toyo"
            _process_toyo_data!(path, info, loaded_data)
        else
            println("  ❌ 알 수 없는 사이클러 타입")
        end
        
        push!(results, info)
    end
    
    println("\n" * "=" ^ 70)
    println("✅ 데이터 처리 완료")
    println("   총 채널 수: $(length(loaded_data))개")
    println("=" ^ 70)
    
    df_results = DataFrame(results)
    return df_results, loaded_data
end

"""
PNE 데이터 처리
"""
function _process_pne_data!(path::String, info::Dict{String, Any}, loaded_data::Dict{String, Any})
    channel_folders = find_pne_channel_folders(path)
    
    if isempty(channel_folders)
        println("  ⚠️  PNE 채널 폴더를 찾을 수 없습니다")
        return
    end
    
    println("  📊 발견된 채널: $(length(channel_folders))개")
    
    for channel_path in channel_folders
        channel_name = basename(channel_path)
        println("    - $channel_name 로딩 중...")
        
        key = "$(info["folder_name"])_$(channel_name)"
        
        loaded_data[key] = Dict{String, Any}(
            "cycler_type" => "PNE",
            "capacity_mAh" => info["capacity_mAh"],
            "folder_name" => info["folder_name"],
            "channel_name" => channel_name,
            "cycle" => nothing,
            "cycle_summary" => nothing,
            "cycle_steps" => nothing,
            "profile" => nothing
        )
        
        cycle_df = load_pne_cycle_data(channel_path)
        if cycle_df !== nothing && nrow(cycle_df) > 0
            # 전체 데이터 저장 (하위 호환성)
            loaded_data[key]["cycle"] = cycle_df
            
            # Condition == 8: 사이클 대표 용량 (충방전 완료 시점)
            cycle_summary = filter(row -> row.Condition == 8, cycle_df)
            loaded_data[key]["cycle_summary"] = cycle_summary
            
            # Condition != 8: 스텝별 용량
            cycle_steps = filter(row -> row.Condition != 8, cycle_df)
            loaded_data[key]["cycle_steps"] = cycle_steps
            
            println("      ✓ 사이클 데이터: $(nrow(cycle_df))행")
            println("        - 사이클 대표 용량 (Condition==8): $(nrow(cycle_summary))행")
            println("        - 스텝별 용량 (Condition!=8): $(nrow(cycle_steps))행")
        else
            println("      ✗ 사이클 데이터 없음")
        end
        
        profile_df = load_pne_profile_data(channel_path)
        if profile_df !== nothing && nrow(profile_df) > 0
            loaded_data[key]["profile"] = profile_df
            println("      ✓ 프로파일 데이터: $(nrow(profile_df))행")
        else
            println("      ✗ 프로파일 데이터 없음")
        end
    end
end

"""
Toyo 데이터 처리
"""
function _process_toyo_data!(path::String, info::Dict{String, Any}, loaded_data::Dict{String, Any})
    channel_folders = find_toyo_channel_folders(path)
    
    if isempty(channel_folders)
        println("  ⚠️  Toyo 채널 폴더를 찾을 수 없습니다")
        return
    end
    
    println("  📊 발견된 채널: $(length(channel_folders))개")
    
    for channel_path in channel_folders
        channel_name = basename(channel_path)
        println("    - 채널 $channel_name 로딩 중...")
        
        key = "$(info["folder_name"])_ch$(channel_name)"
        
        loaded_data[key] = Dict{String, Any}(
            "cycler_type" => "Toyo",
            "capacity_mAh" => info["capacity_mAh"],
            "folder_name" => info["folder_name"],
            "channel_name" => "ch$(channel_name)",
            "cycle" => nothing,
            "profile" => nothing
        )
        
        cycle_df = load_toyo_cycle_data(channel_path)
        if cycle_df !== nothing && nrow(cycle_df) > 0
            loaded_data[key]["cycle"] = cycle_df
            println("      ✓ 사이클 데이터: $(nrow(cycle_df))행")
        else
            println("      ✗ 사이클 데이터 없음")
        end
        
        profile_df = load_toyo_profile_data(channel_path, max_cycles=3)
        if profile_df !== nothing && nrow(profile_df) > 0
            loaded_data[key]["profile"] = profile_df
            println("      ✓ 프로파일 데이터: $(nrow(profile_df))행 (처음 3 사이클)")
        else
            println("      ✗ 프로파일 데이터 없음")
        end
    end
end


# ============================================================================
# Cycle List 처리
# ============================================================================

"""
모든 채널에 대해 cycle_list 생성 및 처리
"""
function process_all_channels!(data::Dict{String, Any})
    println("=" ^ 80)
    println("🔄 전체 채널 Cycle List 처리")
    println("=" ^ 80)
    
    for (channel_key, channel_data) in data["channels"]
        println("\n처리 중: $channel_key")
        
        if channel_data["profile"] === nothing
            println("  ⚠️ Profile 데이터 없음 - 건너뜀")
            continue
        end
        
        if isa(channel_data["profile"], Vector)
            println("  ℹ️ 이미 처리됨 - 건너뜀")
            continue
        end
        
        df = channel_data["profile"]
        
        # Cycle별로 그룹화
        cycle_list = []
        for group_df in groupby(df, :Cycle)
            push!(cycle_list, copy(group_df))
        end
        
        # time_cyc 계산
        for cycle in cycle_list
            cycle.time_cyc = cycle.time_s .- cycle.time_s[1]
        end
        
        # mincapa 결정
        if channel_data["cycle"] !== nothing
            df_cycle = channel_data["cycle"]
            
            if "DchgCap_mAh" in names(df_cycle)
                mincapa = df_cycle.DchgCap_mAh[1]
            elseif "Capacity_mAh" in names(df_cycle)
                mincapa = df_cycle.Capacity_mAh[1]
            else
                mincapa = channel_data["capacity_mAh"] !== nothing ? channel_data["capacity_mAh"] : 1000
            end
        else
            mincapa = channel_data["capacity_mAh"] !== nothing ? channel_data["capacity_mAh"] : 1000
        end
        
        # Capa_cyc와 Crate 계산
        for cycle in cycle_list
            time_diff = vcat(0, diff(cycle.time_cyc))
            cycle.Capa_cyc = cumsum(cycle.Current_mA .* time_diff ./ 3600)
            cycle.Crate = cycle.Current_mA ./ mincapa
        end
        
        channel_data["profile"] = cycle_list
        
        println("  ✅ $(length(cycle_list))개 사이클 처리 완료")
    end
    
    println("\n" * "=" ^ 80)
    println("📋 처리 결과")
    println("=" ^ 80)
    
    processed_channels = filter(data["channels"]) do (k, v)
        isa(v["profile"], Vector)
    end
    
    total_channels = length(processed_channels)
    total_cycles = sum(length(v["profile"]) for (k, v) in processed_channels)
    
    println("\n처리된 채널 수: $(total_channels)개")
    println("총 사이클 수: $(total_cycles)개")
    
    if !isempty(processed_channels)
        println("\n채널별 사이클 수:")
        for (channel_key, channel_data) in processed_channels
            println("  - $channel_key: $(length(channel_data["profile"]))개")
        end
    end
    
    println("\n✅ 전체 처리 완료!")
    println("=" ^ 80)
    
    return data
end

"""
특정 채널의 cycle_list 가져오기
"""
function get_channel_cycle_list(data::Dict{String, Any}, channel_index::Int=0)
    channel_keys = collect(keys(data["channels"]))
    
    if channel_index >= length(channel_keys)
        error("채널 인덱스 $channel_index가 범위를 벗어났습니다. (최대: $(length(channel_keys)-1))")
    end
    
    channel_key = channel_keys[channel_index + 1]  # Julia는 1-indexed
    cycle_list = data["channels"][channel_key]["profile"]
    
    println("선택된 채널: $channel_key")
    println("사이클 수: $(isa(cycle_list, Vector) ? length(cycle_list) : 0)개")
    
    return channel_key, cycle_list
end

"""
특정 채널의 사이클 대표 용량 가져오기 (Condition == 8)
"""
function get_cycle_summary(data::Dict{String, Any}, channel_index::Int=0)
    channel_keys = collect(keys(data["channels"]))
    
    if channel_index >= length(channel_keys)
        error("채널 인덱스 $channel_index가 범위를 벗어났습니다. (최대: $(length(channel_keys)-1))")
    end
    
    channel_key = channel_keys[channel_index + 1]
    cycle_summary = get(data["channels"][channel_key], "cycle_summary", nothing)
    
    if cycle_summary === nothing
        println("⚠️ 채널 $channel_key에 cycle_summary가 없습니다.")
    else
        println("선택된 채널: $channel_key")
        println("사이클 대표 용량 (Condition==8): $(nrow(cycle_summary))행")
    end
    
    return cycle_summary
end

"""
특정 채널의 스텝별 용량 가져오기 (Condition != 8)
"""
function get_cycle_steps(data::Dict{String, Any}, channel_index::Int=0)
    channel_keys = collect(keys(data["channels"]))
    
    if channel_index >= length(channel_keys)
        error("채널 인덱스 $channel_index가 범위를 벗어났습니다. (최대: $(length(channel_keys)-1))")
    end
    
    channel_key = channel_keys[channel_index + 1]
    cycle_steps = get(data["channels"][channel_key], "cycle_steps", nothing)
    
    if cycle_steps === nothing
        println("⚠️ 채널 $channel_key에 cycle_steps가 없습니다.")
    else
        println("선택된 채널: $channel_key")
        println("스텝별 용량 (Condition!=8): $(nrow(cycle_steps))행")
    end
    
    return cycle_steps
end


# ============================================================================
# 사이클 분류
# ============================================================================

"""
데이터 특성 기반 사이클 분류
"""
function categorize_cycle(cycle_df::DataFrame, cycle_index::Int)::String
    n_points = nrow(cycle_df)
    voltage_range = maximum(cycle_df.Voltage_V) - minimum(cycle_df.Voltage_V)
    
    endstate_78_ratio = sum(cycle_df.EndState .== 78) / n_points
    endstate_64_ratio = sum(cycle_df.EndState .== 64) / n_points
    
    if "Crate" in names(cycle_df)
        crate_max = maximum(abs.(cycle_df.Crate))
    else
        crate_max = 0
    end
    
    if n_points > 10000
        return "Resistance_Measurement"
    end
    
    if endstate_78_ratio > 0.5 && cycle_index < 500
        return "SOC_Definition"
    end
    
    if voltage_range < 1400 && crate_max > 1.5
        return "Accelerated_Aging"
    end
    
    if endstate_64_ratio > 0.90 && voltage_range > 1400
        return "RPT"
    end
    
    return "Unknown"
end

"""
전체 cycle_list를 분류
"""
function categorize_cycles(cycle_list::Vector)::Dict{String, Vector{Int}}
    categories = Dict{String, Vector{Int}}(
        "Unknown" => Int[],
        "RPT" => Int[],
        "SOC_Definition" => Int[],
        "Resistance_Measurement" => Int[],
        "Accelerated_Aging" => Int[]
    )
    
    for (idx, cycle) in enumerate(cycle_list)
        category = categorize_cycle(cycle, idx - 1)  # 0-indexed for consistency
        push!(categories[category], idx)
    end
    
    return categories
end

"""
각 사이클에 카테고리 라벨을 추가
"""
function add_category_labels!(cycle_list::Vector, categories::Union{Dict{String, Vector{Int}}, Nothing}=nothing)
    if categories === nothing
        categories = categorize_cycles(cycle_list)
    end
    
    for (category, indices) in categories
        for idx in indices
            cycle_list[idx].category = repeat([category], nrow(cycle_list[idx]))
        end
    end
    
    return categories
end

"""
분류 결과 리포트 출력
"""
function print_categorization_report(cycle_list::Vector, categories::Dict{String, Vector{Int}})
    println("=" ^ 80)
    println("📊 사이클 분류 결과")
    println("=" ^ 80)
    println()
    
    condition_map = Dict(1 => "충전", 2 => "방전", 3 => "Rest")
    
    for (category, indices) in categories
        println("\n[$category]")
        println("  총 $(length(indices))개 사이클")
        
        if !isempty(indices)
            println("  사이클 인덱스: $(indices[1:min(10, length(indices))])")
            if length(indices) > 10
                println("  ... 외 $(length(indices) - 10)개")
            end
            
            first_idx = indices[1]
            cycle = cycle_list[first_idx]
            
            println("\n  [대표 사이클 $(first_idx - 1) 특성]")  # 0-indexed display
            
            v_min = minimum(cycle.Voltage_V)
            v_max = maximum(cycle.Voltage_V)
            v_range = v_max - v_min
            println("    - Voltage 범위: $(round(v_min, digits=0)) ~ $(round(v_max, digits=0)) mV (범위: $(round(v_range, digits=0)) mV)")
            
            endstate_counts = combine(groupby(cycle, :EndState), nrow => :count)
            sort!(endstate_counts, :count, rev=true)
            endstate_str = join(["$(Int(row.EndState))($(row.count)회)" for row in first(endstate_counts, 3)], ", ")
            println("    - EndState 패턴: $endstate_str")
            
            condition_counts = combine(groupby(cycle, :Condition), nrow => :count)
            condition_str = join(["$(get(condition_map, row.Condition, row.Condition))($(row.count)회)" for row in condition_counts], ", ")
            println("    - Condition: $condition_str")
            
            if "Crate" in names(cycle)
                crate_abs = abs.(cycle.Crate)
                println("    - C-rate: 평균 $(round(mean(crate_abs), digits=3))C, 최대 $(round(maximum(crate_abs), digits=3))C")
            end
        end
    end
    
    println("\n" * "=" ^ 80)
end


# ============================================================================
# 채널 카테고리화
# ============================================================================

"""
data 객체의 모든 채널에 대해 사이클 카테고리화 수행
"""
function categorize_all_channels!(data::Dict{String, Any})
    println("=" ^ 80)
    println("🏷️  전체 채널 사이클 카테고리화")
    println("=" ^ 80)
    
    for (channel_key, channel_data) in data["channels"]
        println("\n처리 중: $channel_key")
        
        cycle_list = channel_data["profile"]
        
        if !isa(cycle_list, Vector)
            println("  ⚠️ Cycle list가 아님 - 건너뜀")
            continue
        end
        
        categories = categorize_cycles(cycle_list)
        
        for (category, indices) in categories
            for idx in indices
                cycle_list[idx].category = repeat([category], nrow(cycle_list[idx]))
            end
        end
        
        channel_data["cycle_list"] = categories
        
        total_cycles = sum(length(indices) for (cat, indices) in categories)
        println("  ✅ $(total_cycles)개 사이클 분류 완료")
        for (category, indices) in categories
            if !isempty(indices)
                println("    - $category: $(length(indices))개")
            end
        end
    end
    
    println("\n" * "=" ^ 80)
    println("📋 카테고리화 결과 요약")
    println("=" ^ 80)
    
    processed_channels = filter(data["channels"]) do (k, v)
        haskey(v, "cycle_list")
    end
    
    total_channels = length(processed_channels)
    println("\n처리된 채널 수: $(total_channels)개")
    
    total_stats = Dict{String, Int}(
        "Unknown" => 0,
        "RPT" => 0,
        "SOC_Definition" => 0,
        "Resistance_Measurement" => 0,
        "Accelerated_Aging" => 0
    )
    
    for (channel_key, channel_data) in processed_channels
        categories = channel_data["cycle_list"]
        for (category, indices) in categories
            total_stats[category] += length(indices)
        end
    end
    
    println("\n전체 카테고리별 사이클 수:")
    for (category, count) in total_stats
        if count > 0
            println("  - $category: $(count)개")
        end
    end
    
    println("\n✅ 전체 카테고리화 완료!")
    println("=" ^ 80)
    
    return data
end

"""
특정 채널의 특정 카테고리 사이클 가져오기
"""
function get_category_cycles(data::Dict{String, Any}, channel_index::Int=0, category::String="RPT")
    channel_keys = collect(keys(data["channels"]))
    
    if channel_index >= length(channel_keys)
        error("채널 인덱스 $channel_index가 범위를 벗어났습니다.")
    end
    
    channel_key = channel_keys[channel_index + 1]
    channel_data = data["channels"][channel_key]
    
    if !haskey(channel_data, "cycle_list")
        error("채널 $channel_key에 cycle_list가 없습니다.")
    end
    
    categories = channel_data["cycle_list"]
    
    if !haskey(categories, category)
        error("카테고리 '$category'가 존재하지 않습니다.")
    end
    
    indices = categories[category]
    profile = channel_data["profile"]
    
    return [profile[i] for i in indices]
end


# ============================================================================
# 데이터 통합 및 변환
# ============================================================================

"""
paths를 입력받아 데이터 로드 및 통합
"""
function process_and_combine(paths::Vector{String})::Dict{String, Any}
    df_results, loaded_data = process_battery_data(paths)
    
    cycler_types = Dict{String, Int}()
    for (channel_key, channel_data) in loaded_data
        cycler_type = channel_data["cycler_type"]
        cycler_types[cycler_type] = get(cycler_types, cycler_type, 0) + 1
    end
    
    result = Dict{String, Any}(
        "metadata" => Dict{String, Any}(
            "total_channels" => length(loaded_data),
            "total_paths" => length(paths),
            "cycler_types" => cycler_types,
            "paths" => paths
        ),
        "channels" => loaded_data
    )
    
    return result
end

"""
채널 기반 loaded_data를 통합 DataFrame으로 변환
"""
function combine_to_dataframe(loaded_data::Dict{String, Any})::DataFrame
    all_data = DataFrame[]
    
    for (channel_key, channel_data) in loaded_data
        if channel_data["cycle"] !== nothing && nrow(channel_data["cycle"]) > 0
            df_temp = copy(channel_data["cycle"])
            df_temp.channel = repeat([channel_key], nrow(df_temp))
            df_temp.cycler_type = repeat([channel_data["cycler_type"]], nrow(df_temp))
            df_temp.capacity_mAh_meta = repeat([channel_data["capacity_mAh"]], nrow(df_temp))
            df_temp.folder_name = repeat([channel_data["folder_name"]], nrow(df_temp))
            df_temp.data_type = repeat(["cycle"], nrow(df_temp))
            push!(all_data, df_temp)
        end
        
        if channel_data["profile"] !== nothing && nrow(channel_data["profile"]) > 0
            df_temp = copy(channel_data["profile"])
            df_temp.channel = repeat([channel_key], nrow(df_temp))
            df_temp.cycler_type = repeat([channel_data["cycler_type"]], nrow(df_temp))
            df_temp.capacity_mAh_meta = repeat([channel_data["capacity_mAh"]], nrow(df_temp))
            df_temp.folder_name = repeat([channel_data["folder_name"]], nrow(df_temp))
            df_temp.data_type = repeat(["profile"], nrow(df_temp))
            push!(all_data, df_temp)
        end
    end
    
    if !isempty(all_data)
        combined_df = vcat(all_data..., cols=:union)
        
        # 컬럼 재배치
        meta_cols = ["channel", "cycler_type", "data_type", "folder_name"]
        if "Cycle" in names(combined_df)
            push!(meta_cols, "Cycle")
        end
        
        other_cols = filter(col -> !(String(col) in meta_cols), names(combined_df))
        select!(combined_df, append!(Symbol.(meta_cols), Symbol.(other_cols)))
        
        return combined_df
    else
        return DataFrame()
    end
end


# ============================================================================
# 데이터 저장/로드
# ============================================================================

"""
metadata에서 자동으로 파일명 생성
"""
function _generate_filename_from_metadata(data::Dict{String, Any})::String
    metadata = data["metadata"]
    
    cycler_types = sort(collect(keys(metadata["cycler_types"])))
    cycler_str = join(cycler_types, "_")
    
    if !isempty(metadata["paths"])
        first_path = metadata["paths"][1]
        folder_name = basename(rstrip(first_path, ['/', '\\']))
    else
        folder_name = "unknown"
    end
    
    filename = "$(cycler_str)_$(folder_name)"
    
    return filename
end

"""
통합 데이터를 직렬화 파일로 저장 (Julia의 Serialization)
"""
function save_data(data::Dict{String, Any}, filepath::Union{String, Nothing}=nothing)::String
    if filepath === nothing
        filename = _generate_filename_from_metadata(data)
        filepath = "$(filename).jls"  # Julia serialization
    end
    
    println("💾 데이터 저장 중: $filepath")
    
    open(filepath, "w") do f
        serialize(f, data)
    end
    
    file_size = filesize(filepath) / (1024 * 1024)
    println("✅ 저장 완료! 파일: $filepath ($(round(file_size, digits=2)) MB)")
    
    return filepath
end

"""
직렬화 파일에서 데이터 로드
"""
function load_data(filepath::String)::Dict{String, Any}
    println("📂 데이터 로드 중: $filepath")
    
    data = open(filepath, "r") do f
        deserialize(f)
    end
    
    channels_count = length(data["channels"])
    println("✅ 로드 완료! 채널 수: $channels_count")
    
    return data
end


# ============================================================================
# 테스트 코드
# ============================================================================

if abspath(PROGRAM_FILE) == @__FILE__
    println("배터리 데이터 처리 통합 모듈 (Julia 버전)")
    println("이 모듈을 include하여 사용하세요.")
end
