"""Генерация текстового и HTML отчёта по анализу регистрации аккаунта."""

from datetime import datetime

# Draft icons intentionally mirror inline.py. Replace the emoji IDs there when
# you choose your final custom premium emoji. TXT uses the Unicode fallback;
# HTML reports use the same visual fallback so they remain portable.
REPORT_EMOJI = {
    "id": "👾",
    "registration": "📅",
    "age": "⏳",
    "precision": "⚙️",
    "bot": "📍",
    "download": "📥",
    "go": "🚀",
}


def generate_txt_report(user_id: int, reg_date: datetime, timestamp: int,
                         years: int, months: int, days: int,
                         precision: str, milestones_count: int,
                         username: str = None) -> str:
    current = datetime.now()
    lines = [
        f"{REPORT_EMOJI["bot"]} РЕГИСТРАЦИОННЫЙ АНАЛИЗ",
        f"{REPORT_EMOJI["id"]} ID: {user_id}",
    ]
    if username:
        lines.append(f"{REPORT_EMOJI["bot"]} USERNAME: @{username}")
    lines += [
        "",
        f"{REPORT_EMOJI["registration"]} дата регистрации: {reg_date.strftime('%d.%m.%Y %H:%M:%S')}",
        f"unix timestamp (мс): {timestamp}",
        f"{REPORT_EMOJI["age"]} возраст аккаунта: {years} лет, {months} мес, {days} дн",
        "",
        "метод расчета: кусочно-линейная интерполяция + изотоническая коррекция",
        f"опорных точек: {milestones_count}",
        f"{REPORT_EMOJI["precision"]} точность: {precision}",
        "",
        f"{REPORT_EMOJI["go"]} анализ завершен: {current.strftime('%Y-%m-%d %H:%M:%S')}",
    ]
    return "\n".join(lines)


_PRECISION_STYLE = {
    "эталонная точность": ("#34d399", "REFERENCE"),
    "интерполяция": ("#60a5fa", "INTERPOLATED"),
    "экстраполяция": ("#fbbf24", "PROJECTED"),
}


def generate_html_report(user_id: int, reg_date: datetime, timestamp: int,
                          years: int, months: int, days: int,
                          precision: str, milestones_count: int,
                          username: str = None) -> str:
    current = datetime.now()
    accent, precision_tag = _PRECISION_STYLE.get(precision, ("#a78bfa", precision.upper()))

    username_row = ""
    if username:
        username_row = f"""
        <div class="row">
          <div class="k">📍 Username</div>
          <div class="v">@{username}</div>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Отчёт · {user_id}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    min-height: 100vh;
    background:
      radial-gradient(1200px 600px at 15% -10%, rgba(124, 92, 255, 0.18), transparent 60%),
      radial-gradient(900px 500px at 100% 10%, rgba(52, 211, 153, 0.10), transparent 55%),
      #0b0c10;
    color: #e7e9ee;
    font-family: 'Inter', system-ui, sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px 16px;
  }}

  .card {{
    width: 100%;
    max-width: 560px;
    background: linear-gradient(180deg, #14151b 0%, #101116 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    box-shadow: 0 30px 60px -20px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.02) inset;
    overflow: hidden;
  }}

  .banner {{
    padding: 26px 28px 22px;
    background: linear-gradient(135deg, rgba(124,92,255,0.20), rgba(124,92,255,0.02));
    border-bottom: 1px solid rgba(255,255,255,0.06);
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}

  .banner .title {{
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #9ea3af;
  }}

  .banner .id {{
    margin-top: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px;
    font-weight: 700;
    color: #f5f6f8;
  }}

  .badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: {accent};
    background: {accent}1a;
    border: 1px solid {accent}55;
    padding: 6px 12px;
    border-radius: 999px;
    white-space: nowrap;
  }}

  .body {{
    padding: 22px 28px 8px;
  }}

  .hero {{
    text-align: center;
    padding: 14px 0 22px;
    border-bottom: 1px dashed rgba(255,255,255,0.10);
    margin-bottom: 18px;
  }}

  .hero .age {{
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(90deg, #ffffff, #b9c0ff);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }}

  .hero .age-label {{
    margin-top: 4px;
    font-size: 12.5px;
    color: #8b90a0;
  }}

  .row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }}

  .row:last-child {{ border-bottom: none; }}

  .k {{
    font-size: 13px;
    color: #8b90a0;
    font-weight: 500;
  }}

  .v {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 13.5px;
    color: #e7e9ee;
    font-weight: 600;
    text-align: right;
  }}

  .footer {{
    padding: 18px 28px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }}

  .footer .dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: {accent};
    display: inline-block;
    margin-right: 7px;
    box-shadow: 0 0 0 4px {accent}22;
  }}

  .footer .stamp {{
    font-size: 11.5px;
    color: #6b7080;
  }}

  .footer .method {{
    font-size: 11.5px;
    color: #6b7080;
    text-align: right;
  }}
</style>
</head>
<body>
  <div class="card">
    <div class="banner">
      <div>
        <div class="title">Registration Analysis</div>
        <div class="id">#{user_id}</div>
      </div>
      <div class="badge">{precision_tag}</div>
    </div>

    <div class="body">
      <div class="hero">
        <div class="age">{years} л. {months} мес. {days} дн.</div>
        <div class="age-label">возраст аккаунта</div>
      </div>

      {username_row}
      <div class="row">
        <div class="k">📅 Дата регистрации</div>
        <div class="v">{reg_date.strftime('%d.%m.%Y %H:%M:%S')}</div>
      </div>
      <div class="row">
        <div class="k">Unix timestamp (мс)</div>
        <div class="v">{timestamp}</div>
      </div>
      <div class="row">
        <div class="k">Метод расчёта</div>
        <div class="v" style="font-size:12px;">интерполяция + изо-коррекция</div>
      </div>
      <div class="row">
        <div class="k">Опорных точек</div>
        <div class="v">{milestones_count}</div>
      </div>
    </div>

    <div class="footer">
      <div class="stamp"><span class="dot"></span>завершено {current.strftime('%Y-%m-%d %H:%M:%S')}</div>
      <div class="method">precision: {precision}</div>
    </div>
  </div>
</body>
</html>"""
    return html
