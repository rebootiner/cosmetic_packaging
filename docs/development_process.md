# Development Process (PM / DEV / TESTER)

프로젝트: cosmetic-packaging-ai  
작성일: 2026-02-07 (UTC)

## 1) 역할 정의

- **PM (미니봇)**
  - 요구사항 정리
  - TASK 생성 (TASK-001부터 순차)
  - 이슈 등록/상태 관리
  - 진행 보고 및 의사결정 요청
  - 승인 후 머지 진행

- **DEV (에이전트)**
  - 기능 구현
  - 단위 테스트 작성
  - PR/커밋 준비

- **TESTER (에이전트)**
  - 테스트 시나리오 작성
  - 통합/회귀 테스트
  - 버그 리포트 및 재검증

## 2) 폴더 규칙

- 문서: `PROJECT/cosmetic-packaging-ai/docs`
- 소스: `PROJECT/cosmetic-packaging-ai/source`

## 3) 기본 개발 방식: TDD

모든 기능은 아래 순서로 진행:

1. **Red**: 실패하는 테스트 먼저 작성
2. **Green**: 테스트를 통과시키는 최소 구현
3. **Refactor**: 구조 개선 + 테스트 유지
4. TESTER가 통합 테스트/회귀 테스트 수행

## 4) 작업 흐름 (Issue 기반)

1. PM이 TASK 생성 (예: TASK-001)
2. PM이 TASK를 Git Issue로 등록
3. DEV가 브랜치 생성 후 구현 + 테스트
4. TESTER가 검증
5. PM이 결과 확인 후 Merge
6. Issue Close + 릴리즈 노트 반영

## 5) 상태값 정의

- `BACKLOG`
- `READY`
- `IN_PROGRESS`
- `DEV_DONE`
- `TESTING`
- `DONE`
- `BLOCKED`

## 6) 리포팅 규칙

- PM은 사용자에게 아래를 보고:
  - 현재 스프린트 TASK 현황
  - BLOCKER
  - 다음 의사결정 필요사항

## 7) 이슈/커밋 컨벤션

- Issue 제목: `[TASK-XXX] 제목`
- Branch: `feature/task-xxx-short-name`
- Commit: `TASK-XXX: 변경 요약`

## 8) 초기 백로그(1단계 기준)

- TASK-001: 이미지 업로드 API/화면 뼈대
- TASK-002: 이미지 전처리/세그멘테이션
- TASK-003: 형상 근사 모델 생성
- TASK-004: 치수 자동 추출 + 보정 반영
- TASK-005: 3D 뷰어 연동
- TASK-006: Geometry JSON 출력
- TASK-007: TDD 테스트 스위트 구축
- TASK-008: 통합 테스트 및 안정화

## 9) 사용자 확인 필요사항

- Git Issue를 등록할 원격 저장소(organization/repo) 정보
- 브랜치 보호 규칙(main 직접 푸시 금지 여부)
- 테스트 우선순위(정확도 vs 속도)
