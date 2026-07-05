# 환율 데일리 브리핑 (Daily FX Briefing)

매일 아침 **9시(KST)**에 환율 브리핑을 자동 생성하고, **별도의 이메일 발송 스크립트**로
`khyoo@wooribank.com` 에 직접 전송합니다.

## 동작 흐름

매일 09:00 KST에 새 Claude Code 세션이 자동 실행되어:
1. 웹을 조사해 브리핑 3개 섹션을 작성 (아래 참고)
2. 브리핑을 `briefing.md` 로 저장
3. `send_briefing_email.py` 를 실행해 `khyoo@wooribank.com` 로 이메일 발송

브리핑 구성:
1. **📊 전날 환율 이슈 요약** — 전 영업일 원/달러 종가·등락, 주요 통화(엔·유로·위안·DXY) 동향, 핵심 요인.
2. **🔗 꼭 읽어야 할 기사** — 중요 기사 3~5개를 클릭 가능한 링크 + 한 줄 이유와 함께.
3. **📅 오늘의 주요 환율 이벤트** — 오늘 경제지표·FOMC/금통위·연설 등을 한국시간·영향 코멘트와 함께.

## 이메일 발송 스크립트 (`send_briefing_email.py`)

Claude 계정 알림과 무관하게, 표준 라이브러리만으로 SMTP를 통해 지정 주소로 메일을 보냅니다.
(Gmail·네이버·사내 메일 등 어떤 SMTP 서버든 사용 가능)

```bash
python3 send_briefing_email.py --body-file briefing.md
```

### ⚙️ 필요한 환경변수 (환경 설정에 추가하세요)

발송이 실제로 동작하려면 아래 SMTP 자격증명을 **환경(Environment) 설정의 환경변수**에
추가해야 합니다. 코드에는 비밀번호를 넣지 않습니다.

| 변수 | 필수 | 설명 | 예시 |
|------|:---:|------|------|
| `SMTP_HOST` | ✅ | SMTP 서버 주소 | `smtp.gmail.com` |
| `SMTP_USER` | ✅ | SMTP 로그인 계정 | `me@gmail.com` |
| `SMTP_PASS` | ✅ | 비밀번호/앱 비밀번호 | (앱 비밀번호) |
| `SMTP_PORT` | ⬜ | 기본 `587` | `465` |
| `SMTP_FROM` | ⬜ | 발신자 주소 (기본=`SMTP_USER`) | `noreply@…` |
| `SMTP_SECURITY` | ⬜ | `starttls`(기본)·`ssl`·`none` | `ssl` |
| `BRIEFING_TO` | ⬜ | 수신자 (기본=`khyoo@wooribank.com`) | `khyoo@wooribank.com` |

> Gmail 사용 시: 2단계 인증 후 **앱 비밀번호**를 발급받아 `SMTP_PASS` 에 넣으세요
> (`SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`).

## 스케줄 설정

| 항목 | 값 |
|------|-----|
| 트리거 ID | `trig_01DX67bdCtp9xnAYUECYrQxb` |
| Cron (UTC) | `0 0 * * *` = 매일 00:00 UTC = **09:00 KST** |
| 발화 방식 | 매 실행 시 새 세션 생성 (`create_new_session_on_fire`) |
| 수신자 | `khyoo@wooribank.com` (스크립트가 발송) |
| Claude 계정 알림 | 푸시 ✅ / 이메일 ❌ (이메일은 스크립트가 담당) |
| 언어 / 통화 초점 | 한국어 / 원·달러 중심 (엔·유로·위안·DXY 포함) |
