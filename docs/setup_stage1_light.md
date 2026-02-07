# Stage1 Light Setup (DB 비의존)

Stage1 데모/개발 경로는 DB 없이 `backend + frontend`만 실행합니다.

## 빠른 실행 (권장)

```bash
make demo-stage1
```

실행 후 접속:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Health: http://localhost:8000/health

중지:
```bash
make down-stage1-light
```

---

## 동작 방식

- 기본 `docker-compose.yml`의 `backend` 정의를 재사용
- `docker-compose.stage1-light.yml`에서
  - `backend depends_on(db)` 제거
  - `frontend` 서비스 추가
- 따라서 Stage1 Light 경로에서는 DB를 기동하지 않아도 동작

---

## Frontend ↔ Backend 연결 규칙

기본값(추가 설정 없이 동작):
- 브라우저는 `/api/...` 호출
- Vite dev server가 `http://localhost:8000`(또는 compose에서는 `http://backend:8000`)로 프록시

환경변수:
- `VITE_API_PROXY_TARGET`: Vite 프록시 타겟 (기본 `http://localhost:8000`)
- `VITE_API_BASE_URL`: API 절대 베이스 URL이 필요할 때만 설정 (기본 빈값)
- `VITE_BASE_PATH`: 프론트 base path (기본 `/`)

예시(로컬 프론트 단독 실행):
```bash
cd source/frontend
VITE_API_PROXY_TARGET=http://localhost:8000 npm run dev
```

예시(외부 API 직접 호출):
```bash
cd source/frontend
VITE_API_BASE_URL=https://api.example.com npm run dev
```

---

## 기존 DB 포함 경로 유지

기존 full stack(backend + db) 경로는 그대로 사용 가능:

```bash
make up
```

즉,
- Stage1 Light: `make demo-stage1` (DB 없음)
- 기존 경로: `make up` (DB 포함)
