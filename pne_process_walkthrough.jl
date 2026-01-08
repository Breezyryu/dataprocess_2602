### A Pluto.jl notebook ###
# v0.19.36

using Markdown
using InteractiveUtils

# ╔═╡ Cell order:
# ╟─35950411
# ╠═e0076337
# ╟─data_check
# ╠═check_structure
# ╟─plot_section
# ╠═plot_imports
# ╟─cycle_plot_header
# ╠═cycle_plots
# ╟─steps_analysis_header
# ╠═steps_analysis
# ╟─helper_function_demo
# ╠═use_helpers
# ╟─profile_plot_header
# ╠═profile_plots
# ╟─category_plot_header
# ╠═category_analysis
# ╟─multi_channel_header
# ╠═multi_channel_comparison
# ╠═00000000-0000-0000-0000-000000000001
# ╠═00000000-0000-0000-0000-000000000002

# ╔═╡ 35950411 ╠═╡ skip_as_script = true
#=╠═╡
md"""
### 1. Data 로드
"""
  ╠═╡ =#

# ╔═╡ e0076337 ╠═╡ skip_as_script = true
#=╠═╡
begin
	# battery_data_processor 모듈 포함
	include("battery_data_processor.jl")

	# 분석할 경로 리스트 (사용자가 수정)
	paths = [
		raw"C:\Users\Ryu\Python_project\data\dataprocess_2601\Rawdata\A1_MP1_4500mAh_T23_1",
		# 추가 경로를 여기에 입력하세요
	]

	println("분석 대상 경로 개수: $(length(paths))")

	# 데이터 로드
	data = process_and_combine(paths)
	data = process_all_channels!(data)
	data = categorize_all_channels!(data)
end
  ╠═╡ =#

# ╔═╡ data_check ╠═╡ skip_as_script = true
#=╠═╡
md"""
### 1.1 데이터 구조 확인
"""
  ╠═╡ =#

# ╔═╡ check_structure ╠═╡ skip_as_script = true
#=╠═╡
begin
	# 첫 번째 채널의 데이터 구조 확인
	channel_keys = collect(keys(data["channels"]))
	first_channel_key = channel_keys[1]
	channel_data = data["channels"][first_channel_key]

	println("선택된 채널: $first_channel_key")
	println("Cycler Type: $(channel_data["cycler_type"])")
	println("Capacity: $(channel_data["capacity_mAh"]) mAh")
	println("\n=== 데이터 구조 ===")
	println("cycle 키 존재: $(haskey(channel_data, "cycle"))")
	println("cycle_summary 키 존재: $(haskey(channel_data, "cycle_summary"))")
	println("cycle_steps 키 존재: $(haskey(channel_data, "cycle_steps"))")

	if get(channel_data, "cycle_summary", nothing) !== nothing
		summary = channel_data["cycle_summary"]
		println("\n=== 사이클 대표 용량 (Condition == 8) ===")
		println("  행 수: $(nrow(summary))")
		println("  Condition 값: $(unique(summary.Condition))")
		println("  Cycle 범위: $(minimum(summary.Cycle)) ~ $(maximum(summary.Cycle))")
		println("  첫 5개 행:")
		println(first(summary[!, [:Cycle, :Condition, :ChgCap_mAh, :DchgCap_mAh]], 5))
	end

	if get(channel_data, "cycle_steps", nothing) !== nothing
		steps = channel_data["cycle_steps"]
		println("\n=== 스텝별 용량 (Condition != 8) ===")
		println("  행 수: $(nrow(steps))")
		println("  Condition 값: $(sort(unique(steps.Condition)))")
		println("  Condition 분포:")
		println(combine(groupby(steps, :Condition), nrow => :count))
	end
end
  ╠═╡ =#

# ╔═╡ plot_section ╠═╡ skip_as_script = true
#=╠═╡
md"""
### 2. 데이터 시각화
"""
  ╠═╡ =#

# ╔═╡ plot_imports ╠═╡ skip_as_script = true
#=╠═╡
begin
	using Plots
	using Statistics

	# Plots 설정
	gr()  # GR backend 사용
	default(size=(800, 600), dpi=100)
end
  ╠═╡ =#

# ╔═╡ cycle_plot_header ╠═╡ skip_as_script = true
#=╠═╡
md"""
#### 2.1 Cycle 데이터 시각화 (사이클 대표 용량)
"""
  ╠═╡ =#

# ╔═╡ cycle_plots ╠═╡ skip_as_script = true
#=╠═╡
begin
	# cycle_summary 사용 (Condition == 8, 사이클 대표 용량)
	if get(channel_data, "cycle_summary", nothing) !== nothing
		df_cycle = channel_data["cycle_summary"]

		# 4개의 서브플롯
		p1 = plot(df_cycle.Cycle, df_cycle.DchgCap_mAh, 
			marker=:circle, markersize=3, linewidth=1, color=:red,
			xlabel="Cycle Number", ylabel="Discharge Capacity (mAh)",
			title="방전 용량 변화", legend=false, grid=true)

		p2 = plot(df_cycle.Cycle, df_cycle.ChgCap_mAh, 
			label="Charge", linewidth=1.5, color=:blue, alpha=0.7)
		plot!(p2, df_cycle.Cycle, df_cycle.DchgCap_mAh,
			label="Discharge", linewidth=1.5, color=:red, alpha=0.7,
			xlabel="Cycle Number", ylabel="Capacity (mAh)",
			title="충방전 용량 비교", grid=true)

		p3 = plot(df_cycle.Cycle, df_cycle.Temp_C,
			linewidth=1, color=:green,
			xlabel="Cycle Number", ylabel="Temperature (°C)",
			title="온도 변화", legend=false, grid=true)

		# Coulombic Efficiency 계산
		efficiency = (df_cycle.DchgCap_mAh ./ df_cycle.ChgCap_mAh) .* 100
		p4 = plot(df_cycle.Cycle, efficiency,
			linewidth=1, color=:purple,
			xlabel="Cycle Number", ylabel="Coulombic Efficiency (%)",
			title="쿨롱 효율", legend=false, grid=true, ylims=(90, 102))

		plot(p1, p2, p3, p4, layout=(2, 2), size=(1200, 800),
			plot_title="Cycle 데이터 분석: $first_channel_key (Condition==8)")

		# 통계 정보
		println("\n=== Cycle 데이터 통계 (사이클 대표 용량) ===")
		println("총 사이클 수: $(nrow(df_cycle))")
		println("방전 용량 범위: $(round(minimum(df_cycle.DchgCap_mAh), digits=2)) ~ $(round(maximum(df_cycle.DchgCap_mAh), digits=2)) mAh")
		println("방전 용량 평균: $(round(mean(df_cycle.DchgCap_mAh), digits=2)) mAh")
		println("온도 범위: $(round(minimum(df_cycle.Temp_C), digits=2)) ~ $(round(maximum(df_cycle.Temp_C), digits=2)) °C")
	else
		println("Cycle summary 데이터가 없습니다.")
	end
end
  ╠═╡ =#

# ╔═╡ steps_analysis_header ╠═╡ skip_as_script = true
#=╠═╡
md"""
#### 2.2 스텝별 용량 분석 (Condition != 8)
"""
  ╠═╡ =#

# ╔═╡ steps_analysis ╠═╡ skip_as_script = true
#=╠═╡
begin
	# 스텝별 용량 확인 (Condition != 8)
	if get(channel_data, "cycle_steps", nothing) !== nothing
		df_steps = channel_data["cycle_steps"]

		println("=== 스텝별 용량 분석 ===")
		println("총 행 수: $(nrow(df_steps))")
		println("\nCondition별 분포:")
		condition_counts = combine(groupby(df_steps, :Condition), nrow => :count)
		println(sort(condition_counts, :Condition))

		# 특정 사이클 (예: Cycle 0)의 스텝별 용량 확인
		cycle_num = 0
		cycle_0_steps = filter(row -> row.Cycle == cycle_num, df_steps)

		if nrow(cycle_0_steps) > 0
			println("\n=== Cycle $cycle_num의 스텝별 상세 ===")
			println(cycle_0_steps[!, [:Cycle, :Condition, :ChgCap_mAh, :DchgCap_mAh, :EndState]])

			# 스텝별 용량 시각화
			conditions = sort(unique(cycle_0_steps.Condition))
			capacities = [cycle_0_steps[cycle_0_steps.Condition .== c, :DchgCap_mAh][1] for c in conditions]

			bar(string.(conditions), capacities,
				xlabel="Condition", ylabel="Discharge Capacity (mAh)",
				title="Cycle $cycle_num의 Condition별 방전 용량",
				legend=false, grid=true, size=(1000, 500), alpha=0.7)
		else
			println("\nCycle $cycle_num의 스텝 데이터가 없습니다.")
		end
	else
		println("Cycle steps 데이터가 없습니다.")
	end
end
  ╠═╡ =#

# ╔═╡ helper_function_demo ╠═╡ skip_as_script = true
#=╠═╡
md"""
#### 2.3 헬퍼 함수 사용 예시
"""
  ╠═╡ =#

# ╔═╡ use_helpers ╠═╡ skip_as_script = true
#=╠═╡
begin
	# 헬퍼 함수로 사이클 대표 용량 가져오기
	summary_helper = get_cycle_summary(data, 0)

	if summary_helper !== nothing
		println("\n첫 5개 사이클의 방전 용량:")
		println(first(summary_helper[!, [:Cycle, :DchgCap_mAh]], 5))
	end

	println("\n" * "="^50)

	# 헬퍼 함수로 스텝별 용량 가져오기
	steps_helper = get_cycle_steps(data, 0)

	if steps_helper !== nothing
		println("\nCycle 0의 스텝별 용량:")
		cycle_0_data = filter(row -> row.Cycle == 0, steps_helper)
		println(cycle_0_data[!, [:Cycle, :Condition, :DchgCap_mAh]])
	end
end
  ╠═╡ =#

# ╔═╡ profile_plot_header ╠═╡ skip_as_script = true
#=╠═╡
md"""
#### 2.4 Profile 데이터 시각화 (특정 사이클)
"""
  ╠═╡ =#

# ╔═╡ profile_plots ╠═╡ skip_as_script = true
#=╠═╡
begin
	# Profile이 cycle_list로 처리된 경우
	if isa(channel_data["profile"], Vector)
		cycle_list = channel_data["profile"]

		# 시각화할 사이클 선택
		cycles_to_plot = [1, 11, 51, 101, 201, 301]  # Julia는 1-indexed
		cycles_to_plot = filter(c -> c <= length(cycle_list), cycles_to_plot)

		# 4개의 서브플롯
		p1 = plot(xlabel="Time (hours)", ylabel="Voltage (V)", 
			title="전압 프로파일", legend=:best, grid=true)
		p2 = plot(xlabel="Time (hours)", ylabel="Current (mA)", 
			title="전류 프로파일", legend=:best, grid=true)
		p3 = plot(xlabel="Capacity (mAh)", ylabel="Voltage (V)", 
			title="전압-용량 곡선", legend=:best, grid=true)
		p4 = plot(xlabel="Time (hours)", ylabel="Temperature (°C)", 
			title="온도 프로파일", legend=:best, grid=true)

		for cycle_idx in cycles_to_plot
			cycle_df = cycle_list[cycle_idx]
			label_text = "Cycle $(cycle_idx-1)"  # 0-indexed display

			plot!(p1, cycle_df.time_cyc ./ 3600, cycle_df.Voltage_V, 
				label=label_text, linewidth=1.5)
			plot!(p2, cycle_df.time_cyc ./ 3600, cycle_df.Current_mA, 
				label=label_text, linewidth=1.5)

			if "Capa_cyc" in names(cycle_df)
				plot!(p3, abs.(cycle_df.Capa_cyc), cycle_df.Voltage_V, 
					label=label_text, linewidth=1.5)
			end

			if "Temp_C" in names(cycle_df)
				plot!(p4, cycle_df.time_cyc ./ 3600, cycle_df.Temp_C, 
					label=label_text, linewidth=1.5)
			end
		end

		plot(p1, p2, p3, p4, layout=(2, 2), size=(1200, 800),
			plot_title="Profile 데이터 분석: $first_channel_key")

		println("\n총 사이클 수: $(length(cycle_list))개")
		println("시각화된 사이클: $(cycles_to_plot .- 1)")  # 0-indexed display
	else
		println("Profile 데이터가 처리되지 않았습니다. process_all_channels!()를 먼저 실행하세요.")
	end
end
  ╠═╡ =#

# ╔═╡ category_plot_header ╠═╡ skip_as_script = true
#=╠═╡
md"""
#### 2.5 카테고리별 사이클 분석
"""
  ╠═╡ =#

# ╔═╡ category_analysis ╠═╡ skip_as_script = true
#=╠═╡
begin
	# 카테고리별 사이클 분석
	if haskey(channel_data, "cycle_list")
		categories = channel_data["cycle_list"]
		cycle_list_cat = channel_data["profile"]

		# 카테고리별 통계
		println("=== 카테고리별 사이클 통계 ===")
		for (category, indices) in categories
			if !isempty(indices)
				println("\n[$category]: $(length(indices))개")
				show_indices = indices[1:min(10, length(indices))]
				println("  사이클 인덱스: $(show_indices .- 1)$(length(indices) > 10 ? "..." : "")")  # 0-indexed
			end
		end

		# 카테고리별 대표 사이클 비교
		colors_cat = Dict(
			"RPT" => :blue, 
			"SOC_Definition" => :green,
			"Resistance_Measurement" => :red, 
			"Accelerated_Aging" => :orange, 
			"Unknown" => :gray
		)

		p1 = plot(xlabel="Time (hours)", ylabel="Voltage (V)", 
			title="전압 프로파일 비교", legend=:best, grid=true)
		p2 = plot(xlabel="Time (hours)", ylabel="Current (mA)", 
			title="전류 프로파일 비교", legend=:best, grid=true)
		p3 = plot(xlabel="Capacity (mAh)", ylabel="Voltage (V)", 
			title="전압-용량 곡선 비교", legend=:best, grid=true)
		p4 = plot(xlabel="C-rate", ylabel="Frequency", 
			title="C-rate 분포", legend=:best, grid=true)

		for (category, indices) in categories
			if !isempty(indices)
				cycle_df = cycle_list_cat[indices[1]]
				color = get(colors_cat, category, :black)

				plot!(p1, cycle_df.time_cyc ./ 3600, cycle_df.Voltage_V,
					label=category, color=color, linewidth=1.5, alpha=0.7)

				plot!(p2, cycle_df.time_cyc ./ 3600, cycle_df.Current_mA,
					label=category, color=color, linewidth=1.5, alpha=0.7)

				if "Capa_cyc" in names(cycle_df)
					plot!(p3, abs.(cycle_df.Capa_cyc), cycle_df.Voltage_V,
						label=category, color=color, linewidth=1.5, alpha=0.7)
				end

				if "Crate" in names(cycle_df)
					histogram!(p4, abs.(cycle_df.Crate), bins=50, alpha=0.5,
						label=category, color=color)
				end
			end
		end

		plot(p1, p2, p3, p4, layout=(2, 2), size=(1200, 800),
			plot_title="카테고리별 대표 사이클 비교: $first_channel_key")
	else
		println("카테고리 정보가 없습니다. categorize_all_channels!()를 먼저 실행하세요.")
	end
end
  ╠═╡ =#

# ╔═╡ multi_channel_header ╠═╡ skip_as_script = true
#=╠═╡
md"""
#### 2.6 전체 채널 비교 (사이클 대표 용량)
"""
  ╠═╡ =#

# ╔═╡ multi_channel_comparison ╠═╡ skip_as_script = true
#=╠═╡
begin
	# 모든 채널의 Discharge Capacity 비교 (cycle_summary 사용)
	p_multi = plot(xlabel="Cycle Number", ylabel="Discharge Capacity (mAh)",
		title="전체 채널 방전 용량 비교 (사이클 대표 용량)",
		legend=:best, grid=true, size=(1200, 600))

	for (channel_key, ch_data) in data["channels"]
		# cycle_summary 사용 (Condition == 8만)
		if get(ch_data, "cycle_summary", nothing) !== nothing
			df_summary = ch_data["cycle_summary"]

			if "DchgCap_mAh" in names(df_summary)
				plot!(p_multi, df_summary.Cycle, df_summary.DchgCap_mAh,
					marker=:circle, markersize=2, linewidth=1, alpha=0.8,
					label=channel_key)
			end
		end
	end

	println("\n총 $(length(data["channels"]))개 채널 비교 완료")
	p_multi
end
  ╠═╡ =#

# ╔═╡ 00000000-0000-0000-0000-000000000001
PLUTO_PROJECT_TOML_CONTENTS = """
[deps]
DataFrames = "a93c6f00-e57d-5684-b7b6-d8193f3e46c0"
Plots = "91a5bcdd-55d7-5caf-9e0b-520d859cae80"
Statistics = "10745b16-79ce-11e8-11f9-7d13ad32a3b2"

[compat]
DataFrames = "~1.6"
Plots = "~1.39"
"""

# ╔═╡ 00000000-0000-0000-0000-000000000002
PLUTO_MANIFEST_TOML_CONTENTS = """
# This file is machine-generated - editing it directly is not advised

julia_version = "1.10.0"
manifest_format = "2.0"
project_hash = "da39a3ee5e6b4b0d3255bfef95601890afd80709"

[[deps.DataFrames]]
deps = ["Compat", "DataAPI", "Future", "InvertedIndices", "IteratorInterfaceExtensions", "LinearAlgebra", "Markdown", "Missings", "PooledArrays", "PrettyTables", "Printf", "REPL", "Random", "Reexport", "SnoopPrecompile", "SortingAlgorithms", "Statistics", "TableTraits", "Tables", "Unicode"]
git-tree-sha1 = "d4f69885afa5e6149d0cab3818491565cf41446d"
uuid = "a93c6f00-e57d-5684-b7b6-d8193f3e46c0"
version = "1.6.10"

[[deps.Plots]]
deps = ["Base64", "Contour", "Dates", "Downloads", "FFMPEG", "FixedPointNumbers", "GR", "JLFzf", "JSON", "LaTeXStrings", "Latexify", "LinearAlgebra", "Measures", "NaNMath", "Pkg", "PlotThemes", "PlotUtils", "PrecompileTools", "Preferences", "Printf", "REPL", "Random", "RecipesBase", "RecipesPipeline", "Reexport", "RelocatableFolders", "Requires", "Scratch", "Showoff", "SnoopPrecompile", "SparseArrays", "Statistics", "StatsBase", "UUIDs", "UnicodeFun", "Unzip"]
git-tree-sha1 = "6f2dd1cf7a4bbf4f305a0d8750e351cb46dfbe80"
uuid = "91a5bcdd-55d7-5caf-9e0b-520d859cae80"
version = "1.39.0"

[[deps.Statistics]]
deps = ["LinearAlgebra", "SparseArrays"]
uuid = "10745b16-79ce-11e8-11f9-7d13ad32a3b2"
"""

# ╔═╡ Cell order:
# ╟─35950411
# ╠═e0076337
# ╟─data_check
# ╠═check_structure
# ╟─plot_section
# ╠═plot_imports
# ╟─cycle_plot_header
# ╠═cycle_plots
# ╟─steps_analysis_header
# ╠═steps_analysis
# ╟─helper_function_demo
# ╠═use_helpers
# ╟─profile_plot_header
# ╠═profile_plots
# ╟─category_plot_header
# ╠═category_analysis
# ╟─multi_channel_header
# ╠═multi_channel_comparison
# ╠═00000000-0000-0000-0000-000000000001
# ╠═00000000-0000-0000-0000-000000000002
