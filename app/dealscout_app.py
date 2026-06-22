import html
import logging
import queue
import threading
import time

import gradio as gr
from dotenv import load_dotenv

from dealscout.config import DEMO_MODE
from dealscout.framework.log_utils import reformat

load_dotenv(override=True)

# The visible pipeline the dashboard narrates as a stepper.
PIPELINE_STEPS = ["Scrape", "Summarize", "Price", "Rank", "Notify"]

APP_CSS = """
#ds-shell { max-width: 1180px; margin: 0 auto; padding: 8px 6px 28px; }
.ds-hero { display:grid; grid-template-columns:1.15fr 0.85fr; gap:22px;
  background: radial-gradient(1200px 400px at -10% -40%, rgba(45,212,191,0.18), transparent 60%),
  radial-gradient(1000px 400px at 120% 140%, rgba(99,102,241,0.20), transparent 55%),
  linear-gradient(135deg,0F1620_10F1620_1 0%,131C28_1131C28_1 100%);
  border:1px solid 223040_1223040_1; border-radius:18px; padding:26px 28px; box-shadow:0 16px 40px rgba(0,0,0,0.35); }
.ds-brand { display:flex; align-items:center; gap:10px; font-weight:800; font-size:1.05rem; color:#e8eef5; }
.ds-logo { color:#2dd4bf; font-size:1.3rem; }
.ds-pill { background:linear-gradient(135deg,2DD4BF_12DD4BF_1,6366F1_16366F1_1); color:#06121a; font-size:.66rem; font-weight:800; padding:3px 8px; border-radius:999px; letter-spacing:.08em; }
.ds-hero-title { margin:14px 0 8px; font-size:2.05rem; line-height:1.08; color:#f2f7fb; font-weight:800; }
.ds-hero-sub { margin:0; color:#9fb3c6; font-size:1rem; line-height:1.6; max-width:52ch; }
.ds-status { display:flex; flex-wrap:wrap; gap:8px; margin-top:18px; }
.ds-chip { background:rgba(255,255,255,0.05); border:1px solid 25333F_125333F_1; color:#aebecd; font-size:.78rem; font-weight:600; padding:5px 10px; border-radius:999px; }
.ds-chip-demo { color:#2dd4bf; border-color:rgba(45,212,191,.4); background:rgba(45,212,191,.08); }
.ds-chip-live { color:#fbbf24; border-color:rgba(251,191,36,.4); background:rgba(251,191,36,.08); }
.ds-hero-right { display:flex; }
.ds-spotlight { flex:1; background:rgba(8,13,19,0.55); border:1px solid 243140_1243140_1; border-radius:14px; padding:18px; display:flex; flex-direction:column; gap:12px; }
.ds-spot-label { text-transform:uppercase; font-size:.72rem; font-weight:800; letter-spacing:.08em; color:#7f93a6; }
.ds-spot-title { font-size:1.05rem; font-weight:700; color:#eaf1f7; line-height:1.3; }
.ds-spot-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; }
.ds-spot-cell { background:#0e1620; border:1px solid 22303D_122303D_1; border-radius:10px; padding:9px 10px; }
.ds-spot-cell span { display:block; font-size:.68rem; text-transform:uppercase; letter-spacing:.05em; color:#7f93a6; margin-bottom:4px; }
.ds-spot-cell strong { font-size:1.02rem; color:#eaf1f7; font-variant-numeric:tabular-nums; }
.ds-spot-save strong { color:#34d399; }
.ds-spot-foot { display:flex; align-items:center; justify-content:space-between; }
.ds-save-badge { background:rgba(52,211,153,.12); color:#34d399; border:1px solid rgba(52,211,153,.35); font-weight:700; font-size:.78rem; padding:4px 10px; border-radius:999px; }
.ds-spot-link { color:#7dd3fc; font-weight:700; font-size:.85rem; text-decoration:none; }
.ds-spot-link:hover { text-decoration:underline; }
.ds-kpis { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-top:14px; }
.ds-kpi { background:#121a24; border:1px solid 223040_1223040_1; border-radius:14px; padding:14px 16px; }
.ds-kpi-label { display:block; font-size:.74rem; text-transform:uppercase; letter-spacing:.06em; color:#7f93a6; font-weight:700; margin-bottom:6px; }
.ds-kpi-value { font-size:1.5rem; font-weight:800; color:#eaf1f7; font-variant-numeric:tabular-nums; }
.ds-good { color:#34d399; }
.ds-pipeline-wrap { margin-top:16px; background:#121a24; border:1px solid 223040_1223040_1; border-radius:14px; padding:14px 18px; }
.ds-pipeline-title { font-size:.74rem; text-transform:uppercase; letter-spacing:.06em; color:#7f93a6; font-weight:700; margin-bottom:12px; }
.ds-pipeline { display:flex; align-items:center; }
.ds-step { display:flex; flex-direction:column; align-items:center; gap:7px; min-width:64px; }
.ds-step-dot { width:34px; height:34px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-weight:800; font-size:.9rem; background:#0e1620; border:2px solid 2A3A48_12A3A48_1; color:#7f93a6; transition:all .25s; }
.ds-step-label { font-size:.78rem; color:#8298ab; font-weight:600; }
.ds-step.is-active .ds-step-dot { border-color:#2dd4bf; color:#06121a; background:#2dd4bf; box-shadow:0 0 0 4px rgba(45,212,191,.18); }
.ds-step.is-active .ds-step-label { color:#cdeee7; }
.ds-step.is-done .ds-step-dot { border-color:#34d399; color:#34d399; background:rgba(52,211,153,.12); }
.ds-step.is-done .ds-step-label { color:#9fb3c6; }
.ds-step-line { flex:1; height:2px; background:#2a3a48; margin:0 6px 22px; }
.ds-toolbar { gap:10px !important; margin-top:16px; }
#ds-run { max-width:220px; }
#ds-alert { max-width:240px; }
.ds-section { font-size:.78rem; text-transform:uppercase; letter-spacing:.07em; color:#7f93a6; font-weight:800; margin:20px 2px 8px; }
#ds-table { border-radius:12px; overflow:hidden; }
.ds-panel { background:#121a24; border:1px solid 223040_1223040_1; border-radius:14px; padding:14px 16px; height:100%; }
.ds-panel-title { font-size:.74rem; text-transform:uppercase; letter-spacing:.06em; color:#7f93a6; font-weight:800; margin-bottom:10px; }
.ds-log { height:330px; overflow-y:auto; font-family:Consolas,Monaco,monospace; font-size:.84rem; }
.ds-log-line { padding:5px 2px; border-bottom:1px solid 1B2530_11B2530_1; line-height:1.5; word-break:break-word; }
.ds-log-line:last-child { border-bottom:0; }
.ds-muted { color:#6c7f90; }
.ds-notif-list { display:flex; flex-direction:column; gap:10px; max-height:330px; overflow-y:auto; }
.ds-notif { background:linear-gradient(135deg,0F1620_10F1620_1,15202C_115202C_1); border:1px solid 26404A_126404A_1; border-left:3px solid 2DD4BF_12DD4BF_1; border-radius:12px; padding:11px 13px; }
.ds-notif-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:5px; }
.ds-notif-app { font-weight:800; font-size:.78rem; color:#2dd4bf; }
.ds-notif-time { font-size:.72rem; color:#7f93a6; }
.ds-notif-title { font-weight:700; color:#eaf1f7; font-size:.9rem; margin-bottom:3px; }
.ds-notif-body { color:#9fb3c6; font-size:.84rem; }
.ds-notif-est { color:#6c7f90; }
.ds-empty { color:#7f93a6; font-size:.88rem; line-height:1.6; padding:18px 8px; text-align:center; border:1px dashed 2A3A48_12A3A48_1; border-radius:10px; }
@media (max-width:900px){ .ds-hero{grid-template-columns:1fr;} .ds-kpis{grid-template-columns:repeat(2,1fr);} }
"""


class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(self.format(record))


def setup_logging(log_queue):
    handler = QueueHandler(log_queue)
    formatter = logging.Formatter(
        "[%(asctime)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S %z",
    )
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return handler


def teardown_logging(handler):
    logging.getLogger().removeHandler(handler)
    handler.close()


# ---------------------------------------------------------------------------
# Pure render helpers - tolerant of both demo and real Opportunity objects.
# ---------------------------------------------------------------------------
def money(value):
    return f"${value:,.2f}"


def truncate(text, limit=60):
    text = (text or "").strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "\u2026"


def short_url(url, limit=42):
    cleaned = (url or "").replace("https://", "").replace("http://", "").rstrip("/")
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 1] + "\u2026"


def deal_title(opp):
    title = getattr(opp.deal, "title", "") or ""
    return title if title else truncate(opp.deal.product_description)


def deal_source(opp):
    return getattr(opp.deal, "source", "") or "Live feed"


def discount_pct(opp):
    estimate = getattr(opp, "estimate", 0) or 0
    discount = getattr(opp, "discount", 0) or 0
    return (discount / estimate * 100) if estimate > 0 else 0


def best_opportunity(opps):
    return max(opps, key=lambda item: item.discount) if opps else None


def table_for(opps):
    return [
        [
            deal_title(opp),
            money(opp.deal.price),
            money(opp.estimate),
            money(opp.discount),
            deal_source(opp),
            short_url(opp.deal.url),
        ]
        for opp in opps
    ]


def stepper_html(active, done=False):
    cells = []
    for index, label in enumerate(PIPELINE_STEPS):
        complete = done or (active >= 0 and index < active)
        if complete:
            state, icon = "is-done", "\u2713"
        elif active == index:
            state, icon = "is-active", str(index + 1)
        else:
            state, icon = "", str(index + 1)
        cells.append(
            f'<div class="ds-step {state}"><span class="ds-step-dot">{icon}</span>'
            f'<span class="ds-step-label">{label}</span></div>'
        )
    inner = '<span class="ds-step-line"></span>'.join(cells)
    return (
        '<div class="ds-pipeline-wrap"><div class="ds-pipeline-title">Live pipeline</div>'
        f'<div class="ds-pipeline">{inner}</div></div>'
    )


def log_html(lines):
    if lines:
        body = "".join(f'<div class="ds-log-line">{line}</div>' for line in lines[-22:])
    else:
        body = '<div class="ds-log-line ds-muted">Waiting for the agent to start\u2026</div>'
    return (
        '<div class="ds-panel"><div class="ds-panel-title">Agent activity</div>'
        f'<div class="ds-log">{body}</div></div>'
    )


def notifications_html(notifs):
    notifs = list(notifs or [])
    if not notifs:
        message = (
            "No alerts yet. Run a scan and DealScout will ping you here the moment it spots a deep discount."
            if DEMO_MODE
            else "Live mode delivers deal alerts straight to your phone via Pushover."
        )
        return (
            '<div class="ds-panel"><div class="ds-panel-title">Notifications</div>'
            f'<div class="ds-empty">{message}</div></div>'
        )
    cards = []
    for note in notifs[:8]:
        cards.append(
            f"""<div class="ds-notif">
          <div class="ds-notif-head"><span class="ds-notif-app">\u25ce DealScout</span><span class="ds-notif-time">{note['time']}</span></div>
          <div class="ds-notif-title">Deal alert \u00b7 save {money(note['discount'])} ({note['discount_pct']:.0f}%)</div>
          <div class="ds-notif-body">{html.escape(note['title'])} \u2014 {money(note['price'])} <span class="ds-notif-est">est. {money(note['estimate'])}</span></div>
        </div>"""
        )
    return (
        '<div class="ds-panel"><div class="ds-panel-title">Notifications</div>'
        f'<div class="ds-notif-list">{"".join(cards)}</div></div>'
    )

def render_dashboard(opps, alerts, last_scan):
    best = best_opportunity(opps)
    count = len(opps)
    top = best.discount if best else 0
    average = (sum(max(0, opp.discount) for opp in opps) / count) if count else 0
    mode_chip = (
        '<span class="ds-chip ds-chip-demo">\u25cf Demo mode \u00b7 no live API calls</span>'
        if DEMO_MODE
        else '<span class="ds-chip ds-chip-live">\u25cf Live mode \u00b7 using your keys</span>'
    )
    pill = '<span class="ds-pill">DEMO</span>' if DEMO_MODE else ""
    if best:
        spotlight = f"""<div class="ds-spotlight">
          <div class="ds-spot-label">Top opportunity right now</div>
          <div class="ds-spot-title">{html.escape(deal_title(best))}</div>
          <div class="ds-spot-grid">
            <div class="ds-spot-cell"><span>Deal price</span><strong>{money(best.deal.price)}</strong></div>
            <div class="ds-spot-cell"><span>AI estimate</span><strong>{money(best.estimate)}</strong></div>
            <div class="ds-spot-cell ds-spot-save"><span>You save</span><strong>{money(best.discount)}</strong></div>
          </div>
          <div class="ds-spot-foot"><span class="ds-save-badge">{discount_pct(best):.0f}% under value</span><a class="ds-spot-link" href="{html.escape(best.deal.url, quote=True)}" target="_blank" rel="noreferrer">Open deal \u2197</a></div>
        </div>"""
    else:
        spotlight = '<div class="ds-spotlight"><div class="ds-empty">Run a scan to surface the best live deal.</div></div>'
    return f"""<div class="ds-hero">
      <div class="ds-hero-left">
        <div class="ds-brand"><span class="ds-logo">\u25ce</span><span>DealScout</span>{pill}</div>
        <h1 class="ds-hero-title">Autonomous bargain hunting on autopilot</h1>
        <p class="ds-hero-sub">DealScout continuously scrapes live deal feeds, prices every find with an AI model ensemble, and fires you a push notification the moment something sells for far below what it's really worth.</p>
        <div class="ds-status">{mode_chip}<span class="ds-chip">Watching 5 sources</span><span class="ds-chip">Last scan \u00b7 {last_scan}</span></div>
      </div>
      <div class="ds-hero-right">{spotlight}</div>
    </div>
    <div class="ds-kpis">
      <div class="ds-kpi"><span class="ds-kpi-label">Deals tracked</span><span class="ds-kpi-value">{count}</span></div>
      <div class="ds-kpi"><span class="ds-kpi-label">Best savings</span><span class="ds-kpi-value ds-good">{money(top)}</span></div>
      <div class="ds-kpi"><span class="ds-kpi-label">Avg savings</span><span class="ds-kpi-value">{money(average)}</span></div>
      <div class="ds-kpi"><span class="ds-kpi-label">Alerts sent</span><span class="ds-kpi-value">{alerts}</span></div>
    </div>"""


def infer_step(message):
    lowered = message.lower()
    if "summar" in lowered:
        return 1
    if "scanner" in lowered or "fetch" in lowered or "scraping" in lowered:
        return 0
    if any(word in lowered for word in ("ensemble", "specialist", "frontier", "neural", "pricing")):
        return 2
    if "best deal" in lowered or "identified" in lowered or "ranking" in lowered:
        return 3
    if any(word in lowered for word in ("messaging", "notif", "alert", "push")):
        return 4
    return None


class App:
    def __init__(self):
        self.framework = None
        self._lock = threading.Lock()
        self.last_scan = "\u2014"
        self.ui = None

    def get_framework(self):
        """Lazily create the right engine so demo mode never imports heavy deps."""
        if self.framework:
            return self.framework
        with self._lock:
            if not self.framework:
                if DEMO_MODE:
                    from dealscout.demo.demo_engine import DemoAgentFramework

                    self.framework = DemoAgentFramework()
                else:
                    from dealscout.framework.deal_agent_framework import DealAgentFramework

                    self.framework = DealAgentFramework()
        return self.framework

    def _render_all(self, framework, logs, active, done=False):
        notifs = getattr(framework, "notifications", [])
        return (
            logs,
            render_dashboard(framework.memory, len(notifs), self.last_scan),
            stepper_html(active, done),
            table_for(framework.memory),
            log_html(logs),
            notifications_html(notifs),
        )

    def stream_demo(self, log_data):
        """Narrate one simulated cycle, streaming UI updates per progress event."""
        framework = self.get_framework()
        self.last_scan = time.strftime("%H:%M:%S")
        logs = list(log_data)
        active = -1
        yield self._render_all(framework, logs, active)
        for progress in framework.run():
            if progress.log is not None:
                logs = (logs + [reformat(progress.log)])[-200:]
            if progress.step is not None:
                active = progress.step
            yield self._render_all(framework, logs, active, done=progress.done)

    def stream_real(self, log_data):
        """Run the real agent framework on a worker thread, streaming its logs."""
        framework = self.get_framework()
        self.last_scan = time.strftime("%H:%M:%S")
        logs = list(log_data)
        log_queue = queue.Queue()
        result_queue = queue.Queue()
        handler = setup_logging(log_queue)

        def worker():
            try:
                result_queue.put(("ok", framework.run()))
            except Exception as exc:  # noqa: BLE001
                result_queue.put(("error", exc))

        threading.Thread(target=worker, daemon=True).start()
        active = -1
        yield self._render_all(framework, logs, active)
        try:
            while True:
                try:
                    message = log_queue.get_nowait()
                    logs = (logs + [reformat(message)])[-200:]
                    step = infer_step(message)
                    if step is not None:
                        active = step
                    yield self._render_all(framework, logs, active)
                except queue.Empty:
                    try:
                        status, payload = result_queue.get_nowait()
                        if status == "error":
                            logs = (logs + [f'<span style="color:#fb7185">Run failed: {html.escape(str(payload))}</span>'])[-200:]
                        yield self._render_all(framework, logs, active, done=True)
                        break
                    except queue.Empty:
                        time.sleep(0.1)
        finally:
            teardown_logging(handler)

    def stream(self, log_data):
        if DEMO_MODE:
            yield from self.stream_demo(log_data)
        else:
            yield from self.stream_real(log_data)

    def _send_alert(self, framework, opportunity):
        if DEMO_MODE:
            framework.alert(opportunity)
        else:
            planner = getattr(framework, "planner", None)
            messenger = getattr(planner, "messenger", None) if planner else None
            if messenger:
                messenger.alert(opportunity)

    def send_top_alert(self):
        framework = self.get_framework()
        best = best_opportunity(framework.memory)
        if best is None:
            gr.Warning("No deals to alert on yet - run a scan first.")
        else:
            self._send_alert(framework, best)
            gr.Info(f"Push notification sent \u00b7 {deal_title(best)}")
        notifs = getattr(framework, "notifications", [])
        return notifications_html(notifs), render_dashboard(framework.memory, len(notifs), self.last_scan)

    def on_select(self, event: gr.SelectData):
        framework = self.get_framework()
        row = event.index[0]
        if row < len(framework.memory):
            opportunity = framework.memory[row]
            self._send_alert(framework, opportunity)
            gr.Info(f"Alert sent \u00b7 {deal_title(opportunity)}")
        notifs = getattr(framework, "notifications", [])
        return notifications_html(notifs), render_dashboard(framework.memory, len(notifs), self.last_scan)

    def build(self):
        with gr.Blocks(css=APP_CSS, title="DealScout", fill_width=True, analytics_enabled=False) as ui:
            log_data = gr.State([])
            with gr.Column(elem_id="ds-shell"):
                dashboard = gr.HTML(render_dashboard([], 0, "\u2014"))
                stepper = gr.HTML(stepper_html(-1))
                with gr.Row(elem_classes=["ds-toolbar"]):
                    run_btn = gr.Button("\u21bb Run a scan now", variant="primary", elem_id="ds-run")
                    alert_btn = gr.Button("\U0001f514 Send top deal alert", elem_id="ds-alert")
                gr.HTML('<div class="ds-section">Opportunities</div>')
                table = gr.Dataframe(
                    headers=["Deal", "Price", "Estimate", "Savings", "Source", "URL"],
                    wrap=True,
                    column_widths=[7, 2, 2, 2, 3, 3],
                    row_count=8,
                    col_count=6,
                    max_height=420,
                    elem_id="ds-table",
                )
                with gr.Row(equal_height=True):
                    with gr.Column(scale=3):
                        logs = gr.HTML(log_html([]))
                    with gr.Column(scale=2):
                        notifications = gr.HTML(notifications_html([]))

            outputs = [log_data, dashboard, stepper, table, logs, notifications]
            ui.load(self.stream, inputs=[log_data], outputs=outputs)
            run_btn.click(self.stream, inputs=[log_data], outputs=outputs)
            alert_btn.click(self.send_top_alert, outputs=[notifications, dashboard])
            table.select(self.on_select, outputs=[notifications, dashboard])
            timer = gr.Timer(value=180 if DEMO_MODE else 300, active=True)
            timer.tick(self.stream, inputs=[log_data], outputs=outputs)
        self.ui = ui
        return ui

    def launch(self, **kwargs):
        ui = self.ui or self.build()
        ui.launch(**kwargs)

    def run(self):
        self.launch(share=False, inbrowser=True)


if __name__ == "__main__":
    App().run()