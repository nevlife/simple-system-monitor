# System Monitor Agent

## 프로젝트 설명

이 프로젝트는 Python으로 작성된 간단한 시스템 모니터링 에이전트입니다. 로컬 시스템의 다양한 성능 지표(CPU, 메모리, 디스크, 네트워크 등)를 주기적으로 수집하여 지정된 HTTP 서버로 전송합니다.

## 주요 기능

- **포괄적인 메트릭 수집**:
  - **CPU**: 사용률, 코어 정보, 현재 주파수, 온도 등
  - **메모리**: 전체/사용/가능 메모리, 사용률, 스왑 메모리 정보
  - **디스크**: 파티션별 사용량, 전체 디스크 I/O
  - **네트워크**: 인터페이스별 상태, 속도, 초당 트래픽, 누적 데이터 및 오류
  - **GPU**: NVIDIA GPU 사용률, 메모리 사용량, 온도, 전력 (nvidia-smi 필요)
  - **시스템**: 호스트 이름, OS 정보, 부팅 시간, 현재 접속자 등
- **유연한 설정**: `config.yaml` 파일을 통해 수집 간격, 서버 정보, 각 메트릭 모듈 활성화 여부를 쉽게 설정할 수 있습니다.
- **HTTP 전송**: 수집된 데이터를 지정된 서버의 API 엔드포인트로 JSON 형식으로 전송합니다. 재시도 로직이 포함되어 있습니다.

## 요구사항

프로젝트를 실행하기 위해 다음 라이브러리가 필요합니다.

- `psutil`
- `requests`
- `pyyaml`

다음 명령어로 필요한 라이브러리를 설치할 수 있습니다.
```bash
pip install -r requirements.txt
```
**참고**: GPU 메트릭을 수집하려면 시스템에 `nvidia-smi` CLI 도구(NVIDIA 드라이버에 포함)가 설치되어 있고, PATH에 잡혀 있어야 합니다.

## 설정

프로젝트 루트 디렉토리에 `config.yaml` 파일을 생성하고 아래 형식에 맞게 내용을 작성해야 합니다.

```yaml
# config.yaml

# 데이터를 전송할 서버 정보
server:
  url: "http://127.0.0.1:8000"
  endpoint: "/api/metrics/"
  timeout: 10
  max_retries: 3

# 데이터 수집기 설정
collector:
  interval: 5         # 데이터 수집 간격 (초)
  batch_size: 10      # 몇 개의 데이터를 모아서 전송할지 결정
  modules:            # 각 모듈 활성화 여부
    cpu: true
    memory: true
    disk: true
    network: true
    gpu: false        # NVIDIA GPU가 없는 경우 false로 설정
    system: true

# 클라이언트 식별자
client:
  id: "my-first-agent" # 이 에이전트를 식별할 고유 ID

# 로깅 설정 (현재 미사용)
logging:
  level: "INFO"
```

## 사용법

설정이 완료되면 다음 명령어로 에이전트를 실행합니다.

```bash
python main.py
```

에이전트는 `config.yaml` 파일에 설정된 `interval` 간격으로 계속 실행되며, `Ctrl+C`를 눌러 중지할 수 있습니다.

## 전송 데이터 구조 예시

서버로 전송되는 데이터는 다음과 같은 JSON 구조를 가집니다.

```json
{
  "client_id": "my-first-agent",
  "cpu": {
    "usage_percent": 15.4,
    "freq_current": 3400.0,
    "temperature": -1,
    "load_average": -1,
    "iowait": -1,
    "user": 12345.6,
    "system": 6789.0,
    "idle": 98765.4,
    "ctx_switches": 100000,
    "interrupts": 50000,
    "soft_interrupts": 20000
  },
  "memory": {
    "total": 16000000000,
    "available": 8000000000,
    "percent": 50.0,
    "...": "..."
  },
  "disk": {
    "usage_per_partition": {
      "C:\\": {
        "total": 500000000000,
        "used": 250000000000,
        "percent": 50.0,
        "...": "..."
      }
    },
    "io_total": {
      "read_count": 12345,
      "write_count": 54321,
      "...": "..."
    }
  },
  "network": {
    "summary": { "...": "..." },
    "interfaces": { "...": "..." }
  },
  "system": {
    "timestamp": "2025-10-03T18:00:00.000000",
    "uptime": 3600.0,
    "...": "..."
  },
  "gpu": {
      "gpus": []
  }
}
```