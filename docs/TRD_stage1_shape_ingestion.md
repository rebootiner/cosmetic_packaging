# TRD — Stage 1 Image-to-Geometry Pipeline

프로젝트: cosmetic-packaging-ai  
작성일: 2026-02-07 (UTC)  
버전: v0.1

## 1. 목적

본 TRD는 PRD(v0.2)를 구현하기 위한 기술 설계를 정의합니다.
목표는 제품 이미지를 입력받아 3D 근사 형상과 치수를 생성하고, 사용자 수정 후 Geometry JSON을 산출하는 것입니다.

---

## 2. 시스템 아키텍처

### 2.1 구성요소
- Frontend (React + Three.js)
  - 업로드 UI
  - 결과/보정 UI
  - 3D 미리보기
- Backend API (FastAPI)
  - 업로드/작업생성
  - 이미지 전처리 및 형상 추정
  - 치수 계산 및 JSON 생성
- Worker (비동기 작업)
  - 이미지 처리/형상 생성 파이프라인 실행
- Storage
  - 원본 이미지, 중간 산출물, GLB 파일 저장
- DB (PostgreSQL)
  - 작업 상태, 결과 메타, 사용자 보정 이력

### 2.2 처리 흐름
1) 사용자 이미지 업로드  
2) Job 생성 (`queued`)  
3) Worker가 전처리/세그멘테이션/형상근사/치수추출 수행  
4) 결과 저장 (`done`)  
5) UI에서 3D+치수 확인  
6) 필요 시 치수 수정  
7) Geometry JSON 재생성/저장

---

## 3. API 설계 (MVP)

### POST /api/v1/jobs
- 설명: 이미지 업로드 후 작업 생성
- Request: multipart/form-data (`image`)
- Response:
```json
{ "job_id": "uuid", "status": "queued" }
```

### GET /api/v1/jobs/{job_id}
- 설명: 작업 상태 조회
- Response:
```json
{ "job_id":"uuid", "status":"queued|processing|done|failed", "progress": 0 }
```

### GET /api/v1/jobs/{job_id}/result
- 설명: 결과 조회
- Response: Geometry JSON + mesh url

### PATCH /api/v1/jobs/{job_id}/dimensions
- 설명: 사용자 치수 보정
- Request:
```json
{ "width": 0, "depth": 0, "height": 0, "max_diameter": 0 }
```
- Response: 갱신된 Geometry JSON

---

## 4. 파이프라인 알고리즘

### 4.1 전처리
- 리사이즈/노이즈 제거
- 배경 분리(세그멘테이션)
- 윤곽 컨투어 추출

### 4.2 형상 추정
- Primitive fitting (cylinder/box/ellipsoid 후보)
- 후보별 오차 계산 후 최소 오차 모델 선택
- 필요 시 hybrid proxy(OBB + convex hull) 생성

### 4.3 치수 산출
- 픽셀기반 치수 계산 + 스케일 변환
- width/depth/height/max_diameter 계산
- volume 추정

### 4.4 품질지표
- `shape_confidence` = 모델 일치도 기반 점수
- `dimension_tolerance_mm` = 입력 품질/스케일 신뢰도 기반 추정치

---

## 5. 데이터 모델

### 5.1 jobs
- id (uuid)
- status (queued/processing/done/failed)
- input_image_path
- result_json_path
- mesh_glb_path
- error_message
- created_at, updated_at

### 5.2 corrections
- id
- job_id
- field_name
- old_value
- new_value
- created_at

---

## 6. 테스트 전략 (TDD)

### 6.1 단위 테스트
- 이미지 업로드 유효성 검증
- 세그멘테이션 결과 마스크 품질 체크
- primitive fitting 선택 로직 검증
- 치수 계산 함수 검증
- JSON 스키마 검증

### 6.2 통합 테스트
- 업로드→처리→결과조회 전체 플로우
- 보정 PATCH 후 JSON 재생성 검증
- 실패 케이스(손상 이미지, 비지원 포맷)

### 6.3 회귀 테스트
- 샘플 이미지 세트 고정
- 기준 결과 오차 한계 이상 변화 시 실패

---

## 7. 개발환경 표준

- Python 3.11
- Node 20+
- FastAPI, Uvicorn, Pydantic
- React + Vite + Three.js
- pytest, pytest-cov
- Docker / docker-compose

환경파일:
- `.env.example` 제공
- 로컬: `.env.local` (git ignore)

---

## 8. 배포/운영

- 개발: docker-compose up
- 스테이징: main push 후 수동 배포
- 로깅: API request id + job id 기준 추적
- 모니터링: job 성공률, 평균 처리시간, 실패 사유

---

## 9. 보안/권한

- 업로드 파일 MIME 검사
- 파일 크기 제한(MVP: 20MB)
- 저장소 접근권한 분리(원본/결과)
- 민감 데이터 로그 마스킹

---

## 10. 완료 기준

- 업로드부터 결과까지 E2E 동작
- TDD 기반 테스트 통과 (단위/통합)
- PRD의 MVP 필수 항목 충족
- README + 실행가이드 + 샘플 데이터 포함
