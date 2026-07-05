#!/usr/bin/env python3
"""환율 데일리 브리핑 이메일 발송기.

브리핑 본문(Markdown)을 읽어 SMTP로 지정 수신자에게 발송한다.
표준 라이브러리만 사용하며, 모든 접속 정보는 환경변수로 주입한다.

환경변수
--------
SMTP_HOST      (필수) SMTP 서버 주소.        예) smtp.gmail.com, smtp.naver.com
SMTP_PORT      (선택) 기본 587.
SMTP_USER      (필수) SMTP 로그인 계정.
SMTP_PASS      (필수) SMTP 비밀번호(또는 앱 비밀번호).
SMTP_FROM      (선택) 발신자 주소. 기본값 = SMTP_USER.
SMTP_SECURITY  (선택) starttls(기본) | ssl | none.
BRIEFING_TO    (선택) 수신자 주소. 기본값 = khyoo@wooribank.com.

사용법
------
    python send_briefing_email.py --body-file briefing.md
    python send_briefing_email.py --subject "환율 브리핑 7/6" --body-file briefing.md
    echo "본문" | python send_briefing_email.py            # stdin 으로도 입력 가능
"""

import argparse
import html as html_lib
import os
import re
import smtplib
import sys
from datetime import datetime, timezone, timedelta
from email.message import EmailMessage

DEFAULT_TO = "khyoo@wooribank.com"
KST = timezone(timedelta(hours=9))


def env(name, default=None, required=False):
    value = os.environ.get(name, default)
    if required and not value:
        sys.exit(f"[send_briefing_email] 환경변수 {name} 가 설정되지 않았습니다.")
    return value


def markdown_to_html(md: str) -> str:
    """링크·굵은글씨·제목·리스트 정도만 처리하는 경량 변환기(의존성 없음)."""
    lines = []
    for raw in md.splitlines():
        line = html_lib.escape(raw)
        # [text](url) -> <a>
        line = re.sub(
            r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
            r'<a href="\2">\1</a>',
            line,
        )
        # **bold**
        line = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", line)
        # headings
        m = re.match(r"(#{1,4})\s+(.*)", raw)
        if m:
            level = len(m.group(1))
            inner = re.sub(
                r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
                r'<a href="\2">\1</a>',
                html_lib.escape(m.group(2)),
            )
            inner = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", inner)
            lines.append(f"<h{level}>{inner}</h{level}>")
            continue
        # bullets
        bm = re.match(r"\s*[-*]\s+(.*)", raw)
        if bm:
            inner = re.sub(
                r"\[([^\]]+)\]\((https?://[^\s)]+)\)",
                r'<a href="\2">\1</a>',
                html_lib.escape(bm.group(1)),
            )
            inner = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", inner)
            lines.append(f"<li>{inner}</li>")
            continue
        if raw.strip() == "":
            lines.append("<br>")
        else:
            lines.append(f"<p>{line}</p>")
    body = "\n".join(lines)
    return (
        '<div style="font-family:-apple-system,Segoe UI,Roboto,'
        'Apple SD Gothic Neo,Malgun Gothic,sans-serif;'
        'font-size:15px;line-height:1.6;color:#1a1a1a;max-width:680px">'
        f"{body}</div>"
    )


def main():
    parser = argparse.ArgumentParser(description="환율 데일리 브리핑 이메일 발송")
    parser.add_argument("--body-file", help="브리핑 본문 파일(Markdown). 없으면 stdin.")
    parser.add_argument("--subject", help="메일 제목. 없으면 날짜로 자동 생성.")
    parser.add_argument("--to", help="수신자 주소 override.")
    args = parser.parse_args()

    if args.body_file:
        with open(args.body_file, encoding="utf-8") as f:
            body_md = f.read()
    else:
        body_md = sys.stdin.read()

    if not body_md.strip():
        sys.exit("[send_briefing_email] 발송할 본문이 비어 있습니다.")

    today = datetime.now(KST).strftime("%Y년 %m월 %d일")
    subject = args.subject or f"🗞️ 환율 데일리 브리핑 — {today}"

    host = env("SMTP_HOST", required=True)
    port = int(env("SMTP_PORT", "587"))
    user = env("SMTP_USER", required=True)
    password = env("SMTP_PASS", required=True)
    sender = env("SMTP_FROM", user)
    security = env("SMTP_SECURITY", "starttls").lower()
    recipient = args.to or env("BRIEFING_TO", DEFAULT_TO)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.set_content(body_md)  # text/plain (Markdown 원문)
    msg.add_alternative(markdown_to_html(body_md), subtype="html")

    if security == "ssl":
        server = smtplib.SMTP_SSL(host, port, timeout=30)
    else:
        server = smtplib.SMTP(host, port, timeout=30)
    try:
        server.ehlo()
        if security == "starttls":
            server.starttls()
            server.ehlo()
        server.login(user, password)
        server.send_message(msg)
    finally:
        server.quit()

    print(f"[send_briefing_email] 발송 완료 → {recipient} (제목: {subject})")


if __name__ == "__main__":
    main()
