# TASK Board (PM 관리)

기준: Stage 1 (이미지 업로드 → OCR 치수추출/검증 → 보정 → JSON)
원칙: **UI First + 사용자 컨펌 후 개발 착수 + TDD**
추가 원칙(확정): **Stage 1에서는 DB 저장을 사용하지 않음(메모리/파일 기반 임시 처리)**

상태코드: BACKLOG / READY / UI_DESIGN / UI_REVIEW / WAITING_CONFIRM / IN_PROGRESS / DEV_DONE / TESTING / DONE / BLOCKED

---

## TASK-001 [DONE] 개발환경 초기 설정

### 목표
- 팀 공통 개발환경/실행환경 재현 가능 구성

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
- 환경 검증 테스트(헬스체크/DB 연결) 선작성

### 완료기준
- 신규 개발자가 30분 내 로컬 실행 가능

---

## TASK-002 [DONE] UI 정보구조(IA) + 사용자 플로우 설계

### 목표
- Stage1 전체 사용자 플로우 정의

### 작업범위
- 업로드 → 자동분석 → 결과확인 → 치수수정(선택) → 확정 플로우 설계
- 실패/예외 플로우(이미지 품질 낮음, 처리 실패) 정의

### 담당
- UIUX Expert

### 산출물
- `docs/ui_flow.md`
- 화면 전이 다이어그램

### 완료기준
- PM 리뷰 통과

---

## TASK-003 [DONE] UI 와이어프레임 제작

### 목표
- 핵심 4화면 와이어프레임 제작

### 작업범위
- 화면1: 업로드
- 화면2: 자동 결과(3D+치수)
- 화면3: 치수 보정
- 화면4: 확정/저장

### 담당
- UIUX Expert

### 산출물
- `docs/wireframes_stage1.md` (또는 이미지)

### 완료기준
- 사용자 컨펌 요청 가능한 수준

---

## TASK-004 [DONE] UIUX 전문가 리뷰 + 개선 반영

### 목표
- 와이어프레임 사용성 검증

### 작업범위
- 휴리스틱 리뷰(일관성/피드백/오류예방/가시성)
- 개선안 반영

### 담당
- UIUX Expert

### 산출물
- `docs/uiux_review_report.md`

### 완료기준
- Approve 또는 Change Request 확정

---

## TASK-005 [DONE] 사용자 UI 컨펌 게이트

### 목표
- 개발 착수 전 UI 확정

### 작업범위
- PM이 사용자에게 UI 시안 공유
- 피드백 반영 및 최종 승인 획득

### 산출물
- `docs/ui_signoff.md`

### 완료기준
- 사용자 승인 기록 완료 (승인 전 DEV 착수 금지)

---

## TASK-006 [DONE] 업로드 API + Job 상태관리

### 목표
- 이미지 업로드 후 비동기 작업 생성/조회

### 작업범위
- `POST /api/v1/jobs`
- `GET /api/v1/jobs/{job_id}`
- 파일 저장/메타 DB 기록

### TDD
- 정상/실패 API 테스트 선작성

### 완료기준
- 업로드 시 job_id 반환, 상태조회 동작

---

## TASK-007 [DONE] 이미지 전처리/세그멘테이션

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

## TASK-008 [DONE] 형상 근사 + 치수 산출 엔진

### 목표
- 3D 근사 모델 + 치수/품질지표 계산

### 작업범위
- primitive fitting
- width/depth/height/max_diameter/volume 산출
- shape_confidence/tolerance 계산

### TDD
- fitting/치수 계산 단위 테스트 선작성

### 완료기준
- 기준 샘플 오차 목표 충족

---

## TASK-009 [DONE] 결과 API + Geometry JSON + 보정 반영

### 목표
- 표준 JSON 결과 제공 + 보정 반영

### 작업범위
- `GET /api/v1/jobs/{job_id}/result`
- `PATCH /api/v1/jobs/{job_id}/dimensions`
- JSON 스키마 검증

### TDD
- schema validation/보정 반영 테스트 선작성

### 완료기준
- 보정 전/후 결과 JSON 정확 반영

---

## TASK-010 [DONE] 프론트엔드 구현(컨펌 UI 기준)

### 목표
- 컨펌된 UI를 코드로 구현

### 작업범위
- 업로드/결과/보정/확정 화면 구현
- 상태 폴링/에러 처리
- Three.js 뷰어 연동

### TDD
- 컴포넌트/흐름 테스트 선작성

### 완료기준
- 업로드→확정 사용자 클릭 5회 이내

---

## TASK-011 [DONE] 통합 테스트/회귀 테스트

### 목표
- E2E 안정성 확보

### 작업범위
- 업로드→처리→조회→보정 E2E
- 샘플셋 회귀 테스트
- 성능 측정(평균 처리시간)

### TDD
- E2E 실패 케이스 선작성

### 완료기준
- CI 통과 + 회귀 기준선 저장

---

## TASK-012 [BACKLOG] 문서화/릴리즈 준비

### 목표
- 사용자/개발자 문서 완료

### 작업범위
- API 명세
- 운영 매뉴얼
- known limitations
- Stage1 비DB 정책 반영 문서화

### 완료기준
- MVP 데모 가능한 상태

---

## TASK-013 [IN_PROGRESS] OCR 치수 추출 파이프라인(백엔드)

### 목표
- 도면/이미지 내 치수 텍스트를 OCR로 추출해 구조화

### 작업범위
- OCR 엔진 연동(숫자/소수/단위 인식)
- 추출 결과 스키마(`text`, `value`, `unit`, `bbox`, `confidence`) 정의
- Stage1 비DB 원칙에 맞춰 메모리/파일 임시 처리

### TDD
- 샘플 도면 이미지 기준 추출 성공/실패 테스트 선작성

### 완료기준
- 샘플셋에서 핵심 치수 텍스트 추출 가능

---

## TASK-014 [READY] 치수선-숫자 매핑 및 Geometry 보정 엔진

### 목표
- OCR 숫자를 도면 구조(치수선/구간/전체치수)와 매핑

### 작업범위
- 치수선/화살표/기준선 검출 규칙 추가
- 매핑 결과로 `dimensions_mm` 계산/보정
- 충돌/중복 치수 처리 규칙 정의

### TDD
- 기준 이미지별 expected dimensions 검증 테스트

### 완료기준
- 도면 기반 치수 결과가 현재 고정 scale 추정보다 유의미하게 개선

---

## TASK-015 [READY] 결과 화면 오버레이 렌더링 + 수동 보정 UX

### 목표
- 마지막 화면에서 OCR/치수 추출 결과를 시각적으로 검증 가능하게 표시

### 작업범위
- 원본 이미지 위 bbox/치수 라벨 오버레이
- 추출 치수 리스트 패널 + 인라인 수정
- 사용자 확정 시 최종 JSON 내보내기

### TDD
- 오버레이 렌더/수정/확정 플로우 테스트

### 완료기준
- 사용자가 추출값을 보고 즉시 수정/확정 가능

---

## TASK-016 [BACKLOG] Stage1 경량 아키텍처 정리(DB 비의존)

### 목표
- Stage1 실행 구성을 경량화하여 재현성/테스트 편의 향상

### 작업범위
- docker-compose에서 Stage1 경로의 DB 의존 제거(또는 optional화)
- frontend-backend 연결 안정화(proxy/base URL)
- 로컬 실행 가이드 간소화

### 완료기준
- `docker compose up` + 최소 명령으로 데모 가능
