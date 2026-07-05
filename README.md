# 환율 데일리 브리핑 (Daily FX Briefing)

매일 아침 **9시(KST)**에 원/달러 환율 브리핑을 자동 생성해 **웹페이지에 게시**하고,
**Vercel**로 자동 배포합니다.

## 웹사이트 구성 (정적 사이트, 빌드 불필요)

```
index.html                 # 최신 브리핑 + 아카이브 뷰어 (자체 완결 · 라이트/다크 대응)
briefings/
  manifest.json            # 브리핑 목록 (날짜·제목, 최신순)
  YYYY-MM-DD.md            # 각 날짜 브리핑 원문 (Markdown)
  YYYY-MM-DD.html          # 렌더링된 HTML 프래그먼트
scripts/publish_briefing.mjs   # 브리핑 게시 생성기 (의존성 없음)
vercel.json                # 정적 호스팅 설정 (cleanUrls + no-cache)
```

브라우저는 `index.html`이 `manifest.json`을 읽어 최신 브리핑을 표시하고, 왼쪽
아카이브에서 지난 날짜를 선택할 수 있습니다. (`#YYYY-MM-DD` 딥링크 지원)

## 매일 하는 일

매일 09:00 KST에 새 Claude Code 세션이 자동 실행되어:
1. 웹을 조사해 브리핑 작성 (전날 이슈 요약 · 필독 기사 · 오늘 이벤트)
2. `node scripts/publish_briefing.mjs --in briefing.md` 로 사이트에 게시
3. 변경분을 커밋 & 푸시 → **Vercel이 자동 배포**

## 브리핑 게시 생성기

```bash
node scripts/publish_briefing.mjs --in briefing.md               # 오늘 날짜(KST)로 게시
node scripts/publish_briefing.mjs --in briefing.md --date 2026-07-06
```
`briefings/<date>.md`·`<date>.html` 생성 및 `manifest.json` 갱신을 수행합니다.

## 🚀 Vercel 배포 (최초 1회 연결 필요)

> ⚠️ 이 실행 환경은 네트워크 정책상 Vercel(`vercel.com`)에 접속할 수 없어
> CLI 배포를 대신 실행할 수 없습니다. 대신 **Git 연동**을 쓰면 매일 커밋·푸시할 때마다
> Vercel이 자동 배포하므로 우리 쪽에서 Vercel에 접속할 필요가 없습니다.

**최초 1회 설정 (Vercel 대시보드에서):**
1. [vercel.com/new](https://vercel.com/new) → **Import Git Repository** → `maxaiteacher/kh` 선택
2. **Framework Preset: `Other`**, Build Command / Output Directory **비워둠** (정적 사이트)
3. **Deploy** 클릭
4. 프로젝트 **Settings → Git → Production Branch** 를
   `claude/daily-currency-briefing-euy4np` 로 지정 (또는 이 브랜치를 `main`에 병합)

이후에는 매일 브리핑 커밋이 푸시될 때마다 자동으로 재배포되어 최신 내용이 게시됩니다.

## 스케줄 트리거

| 항목 | 값 |
|------|-----|
| Cron (UTC) | `0 0 * * *` = 매일 00:00 UTC = **09:00 KST** |
| 발화 방식 | 매 실행 시 새 세션 생성 |
| 언어 / 통화 초점 | 한국어 / 원·달러 중심 (엔·유로·위안·DXY 포함) |
