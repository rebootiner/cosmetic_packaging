# Development Process (PM / UIUX / DEV / TESTER)

프로젝트: cosmetic-packaging-ai  
작성일: 2026-02-07 (UTC)  
개정: UI 선행 + 컨펌 게이트 적용

## 1) 역할 정의

- **PM (미니봇)**
  - 요구사항 정리
  - TASK 생성 (TASK-001부터 순차)
  - 이슈 등록/상태 관리
  - 진행 보고 및 의사결정 요청
  - 승인 후 머지 진행

- **UIUX Expert (에이전트)**
  - 와이어프레임/플로우 설계
  - UX 휴리스틱 리뷰
  - 접근성/사용성 체크
  - UI 승인 의견(Approve/Change Request)

- **DEV (에이전트)**
  - 기능 구현
  - 단위 테스트 작성(TDD)
  - PR/커밋 준비

- **TESTER (에이전트)**
  - 테스트 시나리오 작성
  - 통합/회귀 테스트
  - 버그 리포트 및 재검증

## 2) 폴더 규칙

- 문서: `PROJECT/cosmetic-packaging-ai/docs`
- 소스: `PROJECT/cosmetic-packaging-ai/source`

## 3) 핵심 원칙

1. **UI First**: 기능개발 전에 UI/UX를 먼저 설계하고 사용자 컨펌을 받는다.
2. **Gate Process**: UI 컨펌 이전에는 기능 구현 착수 금지.
3. **TDD**: 구현 단계는 Red → Green → Refactor를 필수 적용.

## 4) 작업 흐름 (Issue 기반)

1. PM이 TASK 생성 (예: TASK-001)
2. PM이 TASK를 Git Issue로 등록
3. **UIUX Expert가 화면/플로우 시안 작성**
4. **PM이 사용자에게 UI 컨펌 요청**
5. 컨펌 완료 시 DEV 착수
6. DEV가 TDD로 구현 (테스트 선작성)
7. TESTER가 통합/회귀 테스트
8. PM이 결과 확인 후 Merge
9. Issue Close + 릴리즈 노트 반영

## 5) 상태값 정의

- `BACKLOG`
- `READY`
- `UI_DESIGN`
- `UI_REVIEW`
- `WAITING_CONFIRM`
- `IN_PROGRESS`
- `DEV_DONE`
- `TESTING`
- `DONE`
- `BLOCKED`

## 6) 리포팅 규칙

PM은 사용자에게 아래를 보고:
- 현재 스프린트 TASK 현황
- UI 컨펌 필요 항목
- BLOCKER
- 다음 의사결정 필요사항

## 7) 이슈/커밋 컨벤션

- Issue 제목: `[TASK-XXX] 제목`
- Branch: `feature/task-xxx-short-name`
- Commit: `TASK-XXX: 변경 요약`

## 8) 브랜치/머지 정책

- `main` 직접 작업 금지(원칙)
- 기능은 task 브랜치에서 개발
- 최소 조건: 테스트 통과 + UI 컨펌 이력 + PM 승인

## 9) 사용자 확인 필요사항

- GitHub Issue 생성/수정 권한(토큰/gh auth)
- UI 목업 선호 형식(Figma 링크 vs 이미지 vs 코드 기반 화면)
- UI 컨펌 SLA(예: 24시간 이내 피드백)
