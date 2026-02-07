# TASK Board (PM 관리)

기준: Stage 1 (이미지 업로드 → 3D/치수 → 보정 → JSON)

상태코드: BACKLOG / READY / IN_PROGRESS / DEV_DONE / TESTING / DONE / BLOCKED

---

## TASK-001 [READY] 개발환경 초기 설정

### 목표
- 팀 공통 개발환경/실행환경을 재현 가능하게 구성

### 작업범위
- `source/backend`, `source/frontend` 기본 구조 생성
- Python/Node 버전 고정(.python-version, .nvmrc)
- docker-compose 작성(API, DB)
- `.env.example` 작성
- lint/test 기본 스크립트 정의

### 산출물
- 프로젝트 부트스트랩 코드
- 실행가이드 문서(`docs/setup.md`)

### TDD
- 환경 검증 테스트(헬스체크/DB 연결) 먼저 작성

### 완료기준
- 신규 개발자가 30분 내 로컬 실행 가능

---

## TASK-002 [BACKLOG] 업로드 API + Job 상태관리

### 목표
- 이미지 업로드 후 비동기 작업 생성/조회 가능

### 작업범위
- `POST /api/v1/jobs` 구현
- `GET /api/v1/jobs/{job_id}` 구현
- 파일 저장 및 메타 DB 기록

### TDD
- 정상/실패 케이스 API 테스트 우선 작성

### 완료기준
- 업로드 시 job_id 반환, 상태조회 동작

---

## TASK-003 [BACKLOG] 이미지 전처리/세그멘테이션

### 목표
- 제품 영역 마스크 추출

### 작업범위
- 전처리(리사이즈/노이즈 제거)
- 세그멘테이션 + 컨투어 추출
- 품질 메트릭 저장

### TDD
- 샘플 이미지 기준 마스크 품질 테스트

### 완료기준
- 샘플셋 기준 마스크 성공률 목표치 달성

---

## TASK-004 [BACKLOG] 형상 근사 엔진(Primitive Fitting)

### 목표
- 제품 형상 후보 생성 및 최적 모델 선택

### 작업범위
- box/cylinder/ellipsoid 후보 fitting
- 오차 계산 및 best-fit 선택
- hybrid proxy 생성

### TDD
- synthetic 데이터 기반 fitting 정확도 테스트

### 완료기준
- 기준 데이터에서 기대 형상 타입 선택 정확도 충족

---

## TASK-005 [BACKLOG] 치수 산출 엔진 + 품질지표

### 목표
- width/depth/height/max_diameter/volume 계산

### 작업범위
- 치수 계산 함수 구현
- shape_confidence, tolerance 계산
- `PATCH /dimensions` 보정 반영 로직

### TDD
- 치수 계산 단위 테스트 선작성
- 보정 반영 테스트 선작성

### 완료기준
- 보정 전/후 결과 차이가 JSON에 정확히 반영

---

## TASK-006 [BACKLOG] 결과 API + Geometry JSON 산출

### 목표
- 표준 결과(JSON + mesh URL) 제공

### 작업범위
- `GET /api/v1/jobs/{job_id}/result`
- JSON 스키마 검증 로직
- GLB 산출물 경로 연결

### TDD
- JSON schema validation 테스트 선작성

### 완료기준
- PRD 스키마 준수 100%

---

## TASK-007 [BACKLOG] 프론트엔드 업로드/결과/보정 UI

### 목표
- 사용자 입력 최소화 UX 구현

### 작업범위
- 단일 업로드 화면
- 결과화면(치수 + 신뢰도)
- 보정 입력 UI
- 상태 폴링/에러처리

### TDD
- 컴포넌트 테스트(렌더/입력/요청) 선작성

### 완료기준
- 업로드→확정 사용자 클릭 5회 이내

---

## TASK-008 [BACKLOG] 3D 뷰어 연동

### 목표
- 결과 형상을 브라우저에서 확인 가능

### 작업범위
- Three.js 기반 뷰어
- 회전/줌/리셋
- 치수 오버레이 표시

### TDD
- 뷰어 로딩/에셋 실패 처리 테스트

### 완료기준
- mesh 표시 + 기본 조작 동작

---

## TASK-009 [BACKLOG] 통합 테스트/회귀 테스트

### 목표
- E2E 안정성 확보

### 작업범위
- 업로드→처리→조회→보정 E2E
- 샘플셋 회귀테스트 파이프라인
- 성능 측정(평균 처리시간)

### TDD
- E2E 실패 케이스 우선 작성

### 완료기준
- CI에서 테스트 통과, 회귀 기준선 저장

---

## TASK-010 [BACKLOG] 문서화/릴리즈 준비

### 목표
- 사용자/개발자 문서 완료 및 릴리즈 준비

### 작업범위
- API 명세 문서
- 운영 매뉴얼
- Known limitations 정리

### 완료기준
- MVP 데모 가능한 상태
