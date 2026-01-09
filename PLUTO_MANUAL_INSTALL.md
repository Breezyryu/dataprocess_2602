# Pluto 수동 설치 가이드 (방화벽 우회)

방화벽 문제로 `pkg> add Pluto`가 실행되지 않을 때 GitHub에서 직접 다운받아 설치하는 방법입니다.

## 방법 1: 웹 브라우저로 다운로드 (권장)

### 1단계: GitHub에서 다운로드

브라우저에서 다음 링크로 이동하여 ZIP 파일 다운로드:

**Pluto 일반 버전:**
- URL: https://github.com/fonsp/Pluto.jl/archive/refs/heads/main.zip
- 또는 https://github.com/fonsp/Pluto.jl 접속 → Code → Download ZIP

**Pluto vscode-webview-proxy 버전:**
- URL: https://github.com/fonsp/Pluto.jl/archive/refs/heads/vscode-webview-proxy.zip
- 또는 https://github.com/fonsp/Pluto.jl/tree/vscode-webview-proxy 접속 → Code → Download ZIP

### 2단계: 압축 해제

다운로드한 ZIP 파일을 적절한 위치에 압축 해제:
```
예: C:\Users\Ryu\Downloads\Pluto.jl-main
```

### 3단계: Julia에서 dev 명령으로 설치

Julia REPL에서:

```julia
# Julia 패키지 모드로 진입 (]키)
pkg> dev "C:/Users/Ryu/Downloads/Pluto.jl-main"
```

또는 Julia 코드로:

```julia
using Pkg
Pkg.develop(path="C:/Users/Ryu/Downloads/Pluto.jl-main")
```

### 4단계: 의존성 설치

```julia
pkg> instantiate
```

의존성 설치도 실패하면, 각 의존성을 개별적으로 수동 설치해야 합니다.

## 방법 2: 의존성 패키지도 수동 설치

Pluto의 주요 의존성 패키지들:

### 필수 패키지 다운로드 링크

1. **HTTP.jl**
   - https://github.com/JuliaWeb/HTTP.jl/archive/refs/heads/master.zip

2. **MsgPack.jl**
   - https://github.com/JuliaIO/MsgPack.jl/archive/refs/heads/master.zip

3. **Configurations.jl**
   - https://github.com/Roger-luo/Configurations.jl/archive/refs/heads/master.zip

4. **FuzzyCompletions.jl**
   - https://github.com/JunoLab/FuzzyCompletions.jl/archive/refs/heads/master.zip

5. **Tables.jl**
   - https://github.com/JuliaData/Tables.jl/archive/refs/heads/main.zip

### 각 패키지 설치 순서

```julia
# 1. 의존성 패키지부터 설치
using Pkg
Pkg.develop(path="C:/Users/Ryu/Downloads/HTTP.jl-master")
Pkg.develop(path="C:/Users/Ryu/Downloads/MsgPack.jl-master")
Pkg.develop(path="C:/Users/Ryu/Downloads/Configurations.jl-master")
Pkg.develop(path="C:/Users/Ryu/Downloads/FuzzyCompletions.jl-master")
Pkg.develop(path="C:/Users/Ryu/Downloads/Tables.jl-main")

# 2. 마지막으로 Pluto 설치
Pkg.develop(path="C:/Users/Ryu/Downloads/Pluto.jl-main")

# 3. 모든 패키지 precompile
Pkg.precompile()
```

## 방법 3: Julia 패키지 디렉토리에 직접 복사

### 1단계: Julia 패키지 디렉토리 확인

```julia
using Pkg
Pkg.depots1()
# 결과 예: C:\Users\Ryu\.julia
```

### 2단계: 직접 복사

다운로드한 패키지를 다음 위치에 복사:

```
C:\Users\Ryu\.julia\dev\Pluto
```

### 3단계: Julia에서 인식

```julia
using Pkg
Pkg.resolve()
Pkg.build("Pluto")
```

## 방법 4: 로컬 레지스트리 사용 (고급)

완전히 오프라인 환경이라면 로컬 레지스트리를 구축할 수 있습니다.

## 설치 확인

모든 설치가 완료되면:

```julia
using Pluto
Pluto.run()
```

브라우저에서 `http://localhost:1234` 가 열리면 성공!

## 문제 해결

### 의존성 에러 발생 시

```julia
# 현재 설치된 패키지 상태 확인
pkg> status

# 문제가 있는 패키지 제거 후 재설치
pkg> rm Pluto
pkg> dev "경로"
```

### precompile 에러 발생 시

```julia
# 캐시 삭제
using Pkg
Pkg.gc()

# 다시 precompile
Pkg.precompile()
```

## 주의사항

1. **경로 구분자**: Windows에서는 경로를 `C:/...` (슬래시) 또는 `raw"C:\..."` 형식으로 사용
2. **폴더명**: ZIP 파일 압축 해제 시 폴더명이 `Pluto.jl-main` 형태가 될 수 있음
3. **버전**: `vscode-webview-proxy` 브랜치는 VSCode 통합용이므로, 일반적으로는 `main` 브랜치 권장

## 빠른 시작 스크립트

다음 PowerShell 스크립트로 자동화할 수 있습니다:

```powershell
# PowerShell에서 실행
$downloadUrl = "https://github.com/fonsp/Pluto.jl/archive/refs/heads/main.zip"
$zipFile = "$env:USERPROFILE\Downloads\Pluto.zip"
$extractPath = "$env:USERPROFILE\Downloads\Pluto.jl-main"

# 다운로드
Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile

# 압축 해제
Expand-Archive -Path $zipFile -DestinationPath "$env:USERPROFILE\Downloads" -Force

# Julia 설치 스크립트 실행
julia -e "using Pkg; Pkg.develop(path=raw\"$extractPath\"); Pkg.instantiate()"
```

이 방법으로도 안 되면 의존성까지 모두 수동으로 다운받아야 합니다.
