#!/usr/bin/env python3
import http.server, json, urllib.request, urllib.error, threading, time, sys, os, socket

def find_port():
    for p in range(8765, 8800):
        try:
            s = socket.socket(); s.bind(('', p)); s.close(); return p
        except: continue
    return 8765

PORT = int(os.environ.get('PORT', find_port()))
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gtm_data.json')

def load_db():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f: return json.load(f)
    except: pass
    return []

def save_db(data):
    try:
        with open(DB_FILE, 'w') as f: json.dump(data, f)
    except: pass

HTML = ""
HTML += "<!DOCTYPE html>\n<html>\n<head>\n"
HTML += "<meta charset='UTF-8'>\n"
HTML += "<meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
HTML += "<title>GTM Scout</title>\n"
HTML += "<link rel='preconnect' href='https://fonts.googleapis.com'>\n"
HTML += "<link href='https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap' rel='stylesheet'>\n"
HTML += "<link rel='icon' href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎯</text></svg>\">\n"
HTML += "<style>\n"
HTML += "*{box-sizing:border-box;margin:0;padding:0}\n"
HTML += ":root{\n"
HTML += "  --bg:#F7F5F0;\n"
HTML += "  --bg2:#EEEAE2;\n"
HTML += "  --surface:#FFFFFF;\n"
HTML += "  --border:#E2DDD6;\n"
HTML += "  --border2:#D4CFC7;\n"
HTML += "  --tx:#1A1714;\n"
HTML += "  --tx2:#6B6560;\n"
HTML += "  --tx3:#A8A39C;\n"
HTML += "  --grn:#00C170;\n"
HTML += "  --grn-bg:#E8FAF3;\n"
HTML += "  --grn-border:#B3EDD6;\n"
HTML += "  --amb:#F59E0B;\n"
HTML += "  --amb-bg:#FFFBEB;\n"
HTML += "  --amb-border:#FDE68A;\n"
HTML += "  --red:#EF4444;\n"
HTML += "  --red-bg:#FEF2F2;\n"
HTML += "  --blu:#3B82F6;\n"
HTML += "  --blu-bg:#EFF6FF;\n"
HTML += "  --accent:#FF5C35;\n"
HTML += "  --accent-bg:#FFF2EF;\n"
HTML += "}\n"
HTML += "body{background:var(--bg);color:var(--tx);font-family:'Manrope',sans-serif;font-size:14px;min-height:100vh;line-height:1.5}\n"

HTML += ".topbar{display:flex;align-items:center;justify-content:space-between;padding:16px 32px;background:var(--surface);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:100;backdrop-filter:blur(8px)}\n"
HTML += ".logo-wrap{display:flex;align-items:center;gap:10px}\n"
HTML += ".logo-icon{width:32px;height:32px;background:var(--accent);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px}\n"
HTML += ".logo-text{font-size:17px;font-weight:800;color:var(--tx);letter-spacing:-0.03em}\n"
HTML += ".logo-sub{font-size:12px;font-weight:500;color:var(--tx3);margin-left:2px}\n"
HTML += ".topbar-right{display:flex;align-items:center;gap:24px}\n"
HTML += ".stat-pill{display:flex;align-items:center;gap:6px;background:var(--bg);border:1px solid var(--border);border-radius:20px;padding:5px 12px}\n"
HTML += ".stat-pill-n{font-size:14px;font-weight:800;color:var(--tx)}\n"
HTML += ".stat-pill-l{font-size:11px;font-weight:500;color:var(--tx3)}\n"
HTML += ".stat-pill.hot .stat-pill-n{color:var(--grn)}\n"

HTML += ".main{max-width:1040px;margin:0 auto;padding:32px 24px}\n"

HTML += ".search-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:20px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,0.04)}\n"
HTML += ".search-row{display:flex;gap:10px;margin-bottom:14px}\n"
HTML += "#ci{flex:1;background:var(--bg);border:1.5px solid var(--border);border-radius:10px;color:var(--tx);font-family:'Manrope',sans-serif;font-size:14px;font-weight:500;padding:11px 16px;outline:none;transition:border-color 0.15s}\n"
HTML += "#ci:focus{border-color:var(--accent);background:var(--surface)}\n"
HTML += "#ci:disabled{opacity:.5}\n"
HTML += "#ci::placeholder{color:var(--tx3)}\n"
HTML += "#rb{background:var(--accent);color:#fff;border:none;border-radius:10px;font-family:'Manrope',sans-serif;font-weight:700;font-size:14px;padding:0 22px;cursor:pointer;white-space:nowrap;transition:opacity 0.15s}\n"
HTML += "#rb:hover{opacity:0.88}\n"
HTML += "#rb:disabled{opacity:.4;cursor:not-allowed}\n"

HTML += ".action-row{display:flex;align-items:center;gap:8px;flex-wrap:wrap}\n"
HTML += ".pill-btn{display:inline-flex;align-items:center;gap:5px;background:var(--bg);border:1.5px solid var(--border);border-radius:20px;padding:5px 12px;font-family:'Manrope',sans-serif;font-size:12px;font-weight:600;color:var(--tx2);cursor:pointer;transition:all 0.15s}\n"
HTML += ".pill-btn:hover{border-color:var(--border2);color:var(--tx);background:var(--bg2)}\n"
HTML += ".pill-btn.blu{color:var(--blu);border-color:#BFDBFE;background:var(--blu-bg)}\n"
HTML += ".pill-btn.blu:hover{background:#DBEAFE}\n"
HTML += ".pill-btn.orange{color:var(--accent);border-color:#FECACA;background:var(--accent-bg)}\n"
HTML += ".pill-btn.orange:hover{background:#FFE4DD}\n"

HTML += ".panel-extra{display:none;margin-top:14px;padding-top:14px;border-top:1px solid var(--border)}\n"
HTML += ".panel-label{font-size:11px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px}\n"
HTML += "#bi,#ii{width:100%;background:var(--bg);border:1.5px solid var(--border);border-radius:10px;color:var(--tx);font-family:'Manrope',sans-serif;font-size:13px;padding:10px 14px;min-height:90px;resize:vertical;outline:none;line-height:1.6;font-weight:500}\n"
HTML += "#bi:focus,#ii:focus{border-color:var(--accent)}\n"
HTML += "#ii{border-color:#BFDBFE}\n"
HTML += "#ii:focus{border-color:var(--blu)}\n"
HTML += ".action-btn{background:var(--accent);color:#fff;border:none;border-radius:8px;font-family:'Manrope',sans-serif;font-weight:700;font-size:13px;padding:8px 18px;cursor:pointer;margin-top:10px;transition:opacity 0.15s}\n"
HTML += ".action-btn:hover{opacity:0.88}\n"
HTML += ".action-btn.blu{background:var(--blu)}\n"
HTML += "#ierr{color:var(--red);font-size:12px;margin-top:6px;display:none;font-weight:500}\n"

HTML += "#ldg{display:none;margin-top:12px;padding:10px 14px;background:var(--bg);border-radius:8px;font-size:13px;color:var(--tx2);font-weight:500;display:none;align-items:center;gap:10px}\n"
HTML += ".ldg-dot{width:8px;height:8px;border-radius:50%;background:var(--accent);animation:pulse 1s ease-in-out infinite}\n"
HTML += "@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.4;transform:scale(0.8)}}\n"
HTML += "#err{display:none;margin-top:10px;padding:10px 14px;background:var(--red-bg);border:1px solid #FECACA;border-radius:8px;color:var(--red);font-size:13px;font-weight:500;word-break:break-all}\n"

HTML += ".fetch-card{background:linear-gradient(135deg,#FFF2EF 0%,#FFF8F6 100%);border:1.5px solid #FECDC0;border-radius:16px;padding:20px;margin-bottom:20px}\n"
HTML += ".fetch-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}\n"
HTML += ".fetch-title{font-size:15px;font-weight:800;color:var(--tx);letter-spacing:-0.02em}\n"
HTML += ".fetch-sub{font-size:12px;color:var(--tx2);font-weight:500;margin-top:2px}\n"
HTML += ".source-pills{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:14px}\n"
HTML += ".source-pill{padding:5px 12px;border-radius:20px;font-size:12px;font-weight:600;border:1.5px solid var(--border);background:var(--surface);color:var(--tx2);cursor:pointer;transition:all 0.15s}\n"
HTML += ".source-pill.active{background:var(--accent);border-color:var(--accent);color:#fff}\n"
HTML += "#fetch-btn{background:var(--accent);color:#fff;border:none;border-radius:10px;font-family:'Manrope',sans-serif;font-weight:700;font-size:14px;padding:10px 22px;cursor:pointer;transition:opacity 0.15s}\n"
HTML += "#fetch-btn:hover{opacity:0.88}\n"
HTML += "#fetch-btn:disabled{opacity:.4;cursor:not-allowed}\n"
HTML += "#fetch-results{display:none;margin-top:14px;padding-top:14px;border-top:1px solid #FECDC0}\n"
HTML += ".fetch-company-list{display:flex;flex-direction:column;gap:6px;margin-bottom:12px;max-height:280px;overflow-y:auto}\n"
HTML += ".fetch-item{display:flex;align-items:center;gap:10px;padding:10px 12px;background:var(--surface);border:1.5px solid var(--border);border-radius:10px;cursor:pointer;transition:all 0.15s}\n"
HTML += ".fetch-item:hover{border-color:var(--accent);background:#FFF8F6}\n"
HTML += ".fetch-item.selected{border-color:var(--accent);background:var(--accent-bg)}\n"
HTML += ".fetch-item input[type=checkbox]{accent-color:var(--accent);width:16px;height:16px;cursor:pointer}\n"
HTML += ".fetch-item-name{font-size:13px;font-weight:700;color:var(--tx)}\n"
HTML += ".fetch-item-meta{font-size:11px;color:var(--tx3);font-weight:500}\n"
HTML += "#research-selected-btn{background:var(--accent);color:#fff;border:none;border-radius:10px;font-family:'Manrope',sans-serif;font-weight:700;font-size:14px;padding:10px 22px;cursor:pointer}\n"

HTML += ".toolbar{display:none;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap}\n"
HTML += ".filter-btn{padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1.5px solid var(--border);background:var(--surface);color:var(--tx2);cursor:pointer;transition:all 0.15s;font-family:'Manrope',sans-serif}\n"
HTML += ".filter-btn:hover{border-color:var(--border2);color:var(--tx)}\n"
HTML += ".filter-btn.on{background:var(--tx);border-color:var(--tx);color:#fff}\n"
HTML += ".filter-btn.on.hot{background:var(--grn);border-color:var(--grn)}\n"
HTML += ".filter-btn.on.warm{background:var(--amb);border-color:var(--amb)}\n"
HTML += ".filter-btn.on.cold{background:var(--tx3);border-color:var(--tx3)}\n"
HTML += ".tb-right{margin-left:auto;display:flex;gap:8px}\n"
HTML += ".tb-btn{padding:6px 14px;border-radius:20px;font-size:12px;font-weight:700;border:1.5px solid var(--border);background:var(--surface);color:var(--tx2);cursor:pointer;font-family:'Manrope',sans-serif;transition:all 0.15s}\n"
HTML += ".tb-btn:hover{border-color:var(--border2);color:var(--tx)}\n"
HTML += ".tb-btn.danger{color:var(--red);border-color:#FECACA}\n"
HTML += ".tb-btn.danger:hover{background:var(--red-bg)}\n"

HTML += ".card{background:var(--surface);border:1.5px solid var(--border);border-radius:14px;margin-bottom:10px;overflow:hidden;transition:box-shadow 0.15s}\n"
HTML += ".card:hover{box-shadow:0 4px 16px rgba(0,0,0,0.07)}\n"
HTML += ".ctop{display:flex;align-items:center;gap:14px;padding:16px 20px;cursor:pointer}\n"
HTML += ".score-badge{min-width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:17px;font-weight:800;flex-shrink:0}\n"
HTML += ".score-badge.hot{background:var(--grn-bg);color:var(--grn)}\n"
HTML += ".score-badge.warm{background:var(--amb-bg);color:var(--amb)}\n"
HTML += ".score-badge.cold{background:var(--bg);color:var(--tx3)}\n"
HTML += ".cinfo{flex:1;min-width:0}\n"
HTML += ".cname-row{display:flex;align-items:center;gap:8px;margin-bottom:3px}\n"
HTML += ".cname{font-size:16px;font-weight:800;color:var(--tx);letter-spacing:-0.02em}\n"
HTML += ".visit-link{font-size:11px;font-weight:600;color:var(--blu);background:var(--blu-bg);border:1px solid #BFDBFE;border-radius:6px;padding:2px 7px;text-decoration:none;transition:background 0.15s}\n"
HTML += ".visit-link:hover{background:#DBEAFE}\n"
HTML += ".cmeta{font-size:12px;color:var(--tx3);font-weight:500;display:flex;gap:8px;flex-wrap:wrap}\n"
HTML += ".cmeta-dot{opacity:0.4}\n"
HTML += ".clbl{padding:4px 10px;border-radius:20px;font-size:11px;font-weight:700;flex-shrink:0}\n"
HTML += ".clbl.hot{background:var(--grn-bg);color:var(--grn)}\n"
HTML += ".clbl.warm{background:var(--amb-bg);color:var(--amb)}\n"
HTML += ".clbl.cold{background:var(--bg);color:var(--tx3)}\n"
HTML += ".chevron{font-size:12px;color:var(--tx3);flex-shrink:0;transition:transform 0.2s}\n"
HTML += ".chevron.open{transform:rotate(180deg)}\n"

HTML += ".cbody{display:none;border-top:1.5px solid var(--border)}\n"
HTML += ".cbody.open{display:flex;flex-wrap:wrap}\n"
HTML += ".cleft{flex:1 1 280px;padding:20px;border-right:1.5px solid var(--border)}\n"
HTML += ".cright{flex:1 1 220px;padding:20px;background:var(--bg)}\n"
HTML += ".sec{font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:0.08em;margin:16px 0 8px}\n"
HTML += ".sec:first-child{margin-top:0}\n"
HTML += ".pgrid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:4px}\n"
HTML += ".pcell{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:8px 10px}\n"
HTML += ".pkey{font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:0.06em;margin-bottom:3px}\n"
HTML += ".pval{font-size:12px;font-weight:600;color:var(--tx)}\n"
HTML += ".pval.dim{color:var(--tx3);font-weight:400}\n"
HTML += ".pval a{color:var(--blu);text-decoration:none}\n"
HTML += ".pval a:hover{text-decoration:underline}\n"
HTML += ".social-chips{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:4px}\n"
HTML += ".social-chip{font-size:11px;font-weight:600;padding:4px 10px;border-radius:20px;border:1px solid var(--border);color:var(--tx2);text-decoration:none;background:var(--surface);transition:all 0.15s}\n"
HTML += ".social-chip:hover{border-color:var(--border2);color:var(--tx)}\n"
HTML += ".founder-row{display:flex;gap:10px;align-items:center;padding:8px 10px;background:var(--surface);border:1px solid var(--border);border-radius:8px;margin-bottom:5px}\n"
HTML += ".fav{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800;flex-shrink:0}\n"
HTML += ".fname{font-size:13px;font-weight:700;color:var(--tx)}\n"
HTML += ".frole{font-size:11px;color:var(--tx3);font-weight:500}\n"
HTML += ".sig-row{display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--border)}\n"
HTML += ".sig-row:last-child{border-bottom:none}\n"
HTML += ".sig-label{font-size:12px;font-weight:500;color:var(--tx2)}\n"
HTML += ".sig-val{font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px}\n"
HTML += ".sig-val.y{background:var(--grn-bg);color:var(--grn)}\n"
HTML += ".sig-val.n{background:var(--red-bg);color:var(--red)}\n"
HTML += ".sig-val.u{background:var(--bg);color:var(--tx3)}\n"
HTML += ".analysis-block{margin-bottom:12px}\n"
HTML += ".analysis-text{font-size:12px;color:var(--tx2);line-height:1.7;font-weight:500}\n"
HTML += ".pitch-box{background:linear-gradient(135deg,#FFF2EF,#FFF8F6);border:1.5px solid #FECDC0;border-radius:10px;padding:14px;margin-top:4px}\n"
HTML += ".pitch-label{font-size:10px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px;display:flex;align-items:center;gap:5px}\n"
HTML += ".pitch-text{font-size:12px;color:#8B3520;line-height:1.75;font-weight:500;font-style:italic}\n"
HTML += ".reach-label{font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:4px}\n"
HTML += ".reach-val{font-size:13px;font-weight:700;color:var(--blu)}\n"

HTML += ".cact{display:flex;gap:6px;padding:12px 20px;background:var(--bg);border-top:1.5px solid var(--border);flex-wrap:wrap}\n"
HTML += ".act-btn{font-size:12px;font-weight:600;padding:6px 12px;border-radius:8px;border:1.5px solid var(--border);background:var(--surface);color:var(--tx2);cursor:pointer;font-family:'Manrope',sans-serif;transition:all 0.15s}\n"
HTML += ".act-btn:hover{border-color:var(--border2);color:var(--tx)}\n"
HTML += ".act-btn.primary{background:var(--accent);border-color:var(--accent);color:#fff}\n"
HTML += ".act-btn.primary:hover{opacity:0.88}\n"
HTML += ".act-btn.ghost{margin-left:auto;color:var(--tx3)}\n"

HTML += ".empty{text-align:center;padding:80px 20px}\n"
HTML += ".empty-icon{font-size:48px;margin-bottom:16px;opacity:0.3}\n"
HTML += ".empty-title{font-size:18px;font-weight:800;color:var(--tx);margin-bottom:8px;letter-spacing:-0.02em}\n"
HTML += ".empty-sub{font-size:14px;color:var(--tx3);font-weight:500;line-height:1.7}\n"
HTML += "</style>\n"
HTML += "</head>\n<body>\n"

HTML += "<div class='topbar'>\n"
HTML += "  <div class='logo-wrap'>\n"
HTML += "    <div class='logo-icon'>🎯</div>\n"
HTML += "    <div><span class='logo-text'>GTM Scout</span><span class='logo-sub'></span></div>\n"
HTML += "  </div>\n"
HTML += "  <div class='topbar-right'>\n"
HTML += "    <div class='stat-pill'><span class='stat-pill-n' id='stt'>0</span><span class='stat-pill-l'>companies</span></div>\n"
HTML += "    <div class='stat-pill hot'><span class='stat-pill-n' id='sth'>0</span><span class='stat-pill-l'>hot leads</span></div>\n"
HTML += "  </div>\n"
HTML += "</div>\n"

HTML += "<div class='main'>\n"

# Fetch leads card
HTML += "  <div class='fetch-card'>\n"
HTML += "    <div class='fetch-header'>\n"
HTML += "      <div>\n"
HTML += "        <div class='fetch-title'>✨ Fetch New Leads</div>\n"
HTML += "        <div class='fetch-sub'>Pull recently funded companies from free sources</div>\n"
HTML += "      </div>\n"
HTML += "      <button id='fetch-btn'>Fetch Leads</button>\n"
HTML += "    </div>\n"
HTML += "    <div class='source-pills'>\n"
HTML += "      <div class='source-pill active' data-src='techcrunch'>TechCrunch</div>\n"
HTML += "      <div class='source-pill active' data-src='blockworks'>Blockworks</div>\n"
HTML += "      <div class='source-pill active' data-src='theblock'>The Block</div>\n"
HTML += "      <div class='source-pill' data-src='cryptofunding'>crypto-fundraising.info</div>\n"
HTML += "    </div>\n"
HTML += "    <div id='fetch-results'>\n"
HTML += "      <div class='panel-label'>Found companies — select which to research:</div>\n"
HTML += "      <div class='fetch-company-list' id='fetch-list'></div>\n"
HTML += "      <div style='display:flex;align-items:center;gap:10px'>\n"
HTML += "        <button id='research-selected-btn'>Research Selected</button>\n"
HTML += "        <span id='fetch-count' style='font-size:12px;color:var(--tx3);font-weight:500'></span>\n"
HTML += "      </div>\n"
HTML += "    </div>\n"
HTML += "    <div id='fetch-loading' style='display:none;margin-top:12px;font-size:13px;color:var(--tx2);font-weight:500;display:none;align-items:center;gap:8px'>\n"
HTML += "      <div class='ldg-dot'></div><span id='fetch-msg'>Fetching funding news...</span>\n"
HTML += "    </div>\n"
HTML += "    <div id='fetch-err' style='display:none;margin-top:10px;padding:10px;background:var(--red-bg);border:1px solid #FECACA;border-radius:8px;color:var(--red);font-size:13px;font-weight:500'></div>\n"
HTML += "  </div>\n"

# Search card
HTML += "  <div class='search-card'>\n"
HTML += "    <div class='search-row'>\n"
HTML += "      <input id='ci' type='text' placeholder='Or research a company manually, e.g. Privy, Alchemy...'>\n"
HTML += "      <button id='rb'>Research</button>\n"
HTML += "    </div>\n"
HTML += "    <div id='ldg' style='display:none'><div class='ldg-dot'></div><span>Searching for <b id='lname'></b>... <span id='ltimer'>0s</span></span></div>\n"
HTML += "    <div id='err'></div>\n"
HTML += "    <div class='action-row'>\n"
HTML += "      <button class='pill-btn' id='btog'>+ Bulk research</button>\n"
HTML += "      <button class='pill-btn blu' id='itog'>+ Import JSON</button>\n"
HTML += "    </div>\n"
HTML += "    <div class='panel-extra' id='bpanel'>\n"
HTML += "      <div class='panel-label'>One company per line</div>\n"
HTML += "      <textarea id='bi' placeholder='Privy&#10;Alchemy&#10;EigenLayer'></textarea>\n"
HTML += "      <button class='action-btn' id='brb'>Research All</button>\n"
HTML += "    </div>\n"
HTML += "    <div class='panel-extra' id='ipanel'>\n"
HTML += "      <div class='panel-label' style='color:var(--blu)'>Paste JSON array or single company object</div>\n"
HTML += "      <textarea id='ii' placeholder='[{&quot;company&quot;:&quot;Privy&quot;,...}]'></textarea>\n"
HTML += "      <div id='ierr'></div>\n"
HTML += "      <button class='action-btn blu' id='iib'>Import</button>\n"
HTML += "    </div>\n"
HTML += "  </div>\n"

# Toolbar
HTML += "  <div class='toolbar' id='tb'>\n"
HTML += "    <button class='filter-btn on' data-f='all'>All</button>\n"
HTML += "    <button class='filter-btn' data-f='hot'>🔥 Hot</button>\n"
HTML += "    <button class='filter-btn' data-f='warm'>🌤 Warm</button>\n"
HTML += "    <button class='filter-btn' data-f='cold'>🧊 Cold</button>\n"
HTML += "    <div class='tb-right'>\n"
HTML += "      <button class='tb-btn' id='csvbtn'>↓ Export CSV</button>\n"
HTML += "      <button class='tb-btn danger' id='clrbtn'>Clear All</button>\n"
HTML += "    </div>\n"
HTML += "  </div>\n"

HTML += "  <div id='cards'></div>\n"
HTML += "  <div class='empty' id='empty'>\n"
HTML += "    <div class='empty-icon'>🎯</div>\n"
HTML += "    <div class='empty-title'>No leads yet</div>\n"
HTML += "    <div class='empty-sub'>Fetch leads from funding news above,<br>or research a company manually.</div>\n"
HTML += "  </div>\n"
HTML += "</div>\n"

JS = """
var DB = [];
var busy = false;
var fil = 'all';
var ti = null;
var activeSources = ['techcrunch','blockworks','theblock'];

var SYS = 'Return ONLY a valid JSON object, no markdown, no backticks, no text before or after. Fields: company, tagline, website, sector, hq, founded, stage, funding_amount, funding_date, lead_investor, other_investors, employee_count, socials (object: twitter, linkedin, discord, telegram, github), founders (array of: name/role/background), has_cmo (bool), has_marketing_hire (bool), marketing_notes, product_status, community_size, gtm_readiness_score (integer 0-100), gtm_label (exactly "Hot Lead" if 80+, "Warm Lead" if 50-79, "Cold Lead" if below 50), gtm_signals (object of booleans: recently_funded, no_cmo, pre_launch_or_early, active_community, has_product, small_team, marketing_gap_visible), why_fit, risks, pitch_opener, decision_maker. Use null for unknown.';

var RSS_FETCH_SYS = 'You are a funding news analyst. Search the web for recent startup funding announcements from the last 14 days. Find companies in AI, web3, crypto, blockchain, DeFi, or tech that have recently raised funding. Return ONLY a valid JSON array of objects, no markdown. Each object: {"company": "Name", "sector": "AI/Web3/DeFi/etc", "funding": "$XM", "stage": "Seed/Series A/etc", "source": "publication name"}. Return 10-15 companies maximum. Only include companies that actually raised money recently.';

function load() {
  fetch('/db').then(function(r) { return r.json(); }).then(function(data) {
    if (Array.isArray(data)) { DB = data; renderAll(); }
  }).catch(function() { DB = []; });
}

function save() {
  fetch('/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(DB)
  }).catch(function() {});
}

function showPanel(id) {
  var panels = ['bpanel', 'ipanel'];
  panels.forEach(function(pid) {
    var el = document.getElementById(pid);
    var isTarget = pid === id;
    var isOpen = el.style.display === 'block';
    el.style.display = (isTarget && !isOpen) ? 'block' : 'none';
  });
  document.getElementById('btog').textContent = document.getElementById('bpanel').style.display === 'block' ? '- Bulk research' : '+ Bulk research';
  document.getElementById('itog').textContent = document.getElementById('ipanel').style.display === 'block' ? '- Import JSON' : '+ Import JSON';
}

// ── FETCH LEADS ───────────────────────────────────────────────────────────────
function fetchLeads() {
  var btn = document.getElementById('fetch-btn');
  var loadEl = document.getElementById('fetch-loading');
  var errEl = document.getElementById('fetch-err');
  var resultsEl = document.getElementById('fetch-results');
  btn.disabled = true;
  errEl.style.display = 'none';
  resultsEl.style.display = 'none';
  loadEl.style.display = 'flex';
  document.getElementById('fetch-msg').textContent = 'Searching funding news from the last 14 days...';

  var sourceNames = activeSources.map(function(s) {
    return s === 'techcrunch' ? 'TechCrunch' : s === 'blockworks' ? 'Blockworks' : s === 'theblock' ? 'The Block' : 'crypto-fundraising.info';
  }).join(', ');

  var prompt = 'Search ' + sourceNames + ' and other tech/crypto news sites for startup funding announcements from the last 14 days. Focus on AI, web3, crypto, blockchain, DeFi, and tech startups. Return a JSON array of recently funded companies.';

  fetch('/api', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key: '', company: prompt, system: RSS_FETCH_SYS, mode: 'fetch' })
  }).then(function(r) { return r.json(); })
  .then(function(d) {
    if (d.error) throw new Error(d.error);
    var text = d.text || '';
    text = text.replace(/```json/g, '').replace(/```/g, '').trim();
    var a = text.indexOf('['), b = text.lastIndexOf(']');
    if (a < 0 || b < 0) throw new Error('No results found');
    var companies = JSON.parse(text.slice(a, b + 1));
    if (!companies.length) throw new Error('No companies found');

    var list = document.getElementById('fetch-list');
    list.innerHTML = '';
    companies.forEach(function(co, i) {
      var item = document.createElement('div');
      item.className = 'fetch-item selected';
      item.innerHTML = '<input type="checkbox" checked data-company="' + encodeURIComponent(JSON.stringify(co)) + '">' +
        '<div><div class="fetch-item-name">' + (co.company || 'Unknown') + '</div>' +
        '<div class="fetch-item-meta">' + [co.sector, co.funding, co.stage, co.source].filter(Boolean).join(' · ') + '</div></div>';
      item.onclick = function(e) {
        if (e.target.type === 'checkbox') return;
        var cb = item.querySelector('input');
        cb.checked = !cb.checked;
        item.classList.toggle('selected', cb.checked);
        updateFetchCount();
      };
      item.querySelector('input').onchange = function() {
        item.classList.toggle('selected', this.checked);
        updateFetchCount();
      };
      list.appendChild(item);
    });
    updateFetchCount();
    loadEl.style.display = 'none';
    resultsEl.style.display = 'block';
    btn.disabled = false;
  })
  .catch(function(e) {
    loadEl.style.display = 'none';
    errEl.textContent = 'Error: ' + e.message;
    errEl.style.display = 'block';
    btn.disabled = false;
  });
}

function updateFetchCount() {
  var checked = document.querySelectorAll('#fetch-list input:checked').length;
  document.getElementById('fetch-count').textContent = checked + ' selected';
}

function researchSelected() {
  var checkboxes = document.querySelectorAll('#fetch-list input:checked');
  var names = [];
  checkboxes.forEach(function(cb) {
    try { var co = JSON.parse(decodeURIComponent(cb.getAttribute('data-company'))); if (co.company) names.push(co.company); } catch(e) {}
  });
  if (!names.length) return;
  document.getElementById('fetch-results').style.display = 'none';
  var i = 0;
  function next() { if (i >= names.length) return; run(names[i++], next); }
  next();
}

// ── RESEARCH ──────────────────────────────────────────────────────────────────
function go() {
  var v = document.getElementById('ci').value.trim();
  if (!v || busy) return;
  document.getElementById('ci').value = '';
  run(v);
}

function bulk() {
  if (busy) return;
  var names = document.getElementById('bi').value.trim().split('\\n').map(function(s) { return s.trim(); }).filter(Boolean);
  if (!names.length) return;
  document.getElementById('bi').value = '';
  var i = 0;
  function next() { if (i >= names.length) return; run(names[i++], next); }
  next();
}

function importJSON() {
  var raw = document.getElementById('ii').value.trim();
  var errEl = document.getElementById('ierr');
  errEl.style.display = 'none';
  try {
    var clean = raw.replace(/```json/g, '').replace(/```/g, '').trim();
    var parsed = clean.charAt(0) === '[' ? JSON.parse(clean) : [JSON.parse(clean.slice(clean.indexOf('{'), clean.lastIndexOf('}') + 1))];
    var added = 0;
    for (var i = 0; i < parsed.length; i++) {
      var r = parsed[i];
      if (r && r.company) { r._id = 'id' + Date.now() + Math.floor(Math.random() * 9999); r._open = true; DB.unshift(r); added++; }
    }
    if (!added) throw new Error('No valid company objects found');
    save(); renderAll();
    document.getElementById('ii').value = '';
    document.getElementById('ipanel').style.display = 'none';
    document.getElementById('itog').textContent = '+ Import JSON';
  } catch(e) { errEl.textContent = 'Error: ' + e.message; errEl.style.display = 'block'; }
}

function run(company, callback) {
  busy = true;
  document.getElementById('rb').disabled = true;
  document.getElementById('ci').disabled = true;
  document.getElementById('err').style.display = 'none';
  document.getElementById('lname').textContent = company;
  document.getElementById('ldg').style.display = 'flex';
  var secs = 0;
  document.getElementById('ltimer').textContent = '0s';
  ti = setInterval(function() { document.getElementById('ltimer').textContent = (++secs) + 's'; }, 1000);

  fetch('/api', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key: '', company: company, system: SYS })
  }).then(function(r) { return r.json(); })
  .then(function(d) {
    if (d.error) throw new Error(d.error);
    var t = (d.text || '').replace(/```json/g, '').replace(/```/g, '').trim();
    var a = t.indexOf('{'), b = t.lastIndexOf('}');
    if (a < 0 || b < 0) throw new Error('No JSON returned');
    var res = JSON.parse(t.slice(a, b + 1));
    res._id = 'id' + Date.now(); res._open = true;
    DB.unshift(res); save(); renderAll();
  })
  .catch(function(e) {
    var el = document.getElementById('err');
    el.textContent = 'Error: ' + e.message;
    el.style.display = 'block';
  })
  .finally(function() {
    clearInterval(ti);
    document.getElementById('ldg').style.display = 'none';
    document.getElementById('rb').disabled = false;
    document.getElementById('ci').disabled = false;
    busy = false;
    if (callback) setTimeout(callback, 500);
  });
}

// ── RENDER ────────────────────────────────────────────────────────────────────
function sc(n) { return n >= 80 ? 'hot' : n >= 50 ? 'warm' : 'cold'; }
function su(v) { if (!v || v === 'null' || v === 'undefined') return ''; return String(v).indexOf('http') === 0 ? v : 'https://' + v; }

function renderAll() {
  document.getElementById('stt').textContent = DB.length;
  document.getElementById('sth').textContent = DB.filter(function(r) { return r.gtm_label === 'Hot Lead'; }).length;
  document.getElementById('empty').style.display = DB.length ? 'none' : 'block';
  document.getElementById('tb').style.display = DB.length ? 'flex' : 'none';
  renderCards();
}

function renderCards() {
  var shown = fil === 'all' ? DB : DB.filter(function(r) {
    return r.gtm_label === (fil === 'hot' ? 'Hot Lead' : fil === 'warm' ? 'Warm Lead' : 'Cold Lead');
  });
  var cont = document.getElementById('cards');
  cont.innerHTML = '';

  shown.forEach(function(r) {
    var n = r.gtm_readiness_score || 0;
    var cls = sc(n);
    var s = r.socials || {};
    var g = r.gtm_signals || {};
    var ff = Array.isArray(r.founders) ? r.founders : [];
    var id = r._id;
    var open = r._open;
    var site = su(r.website);
    var labelText = r.gtm_label || '';

    var card = document.createElement('div');
    card.className = 'card';

    var top = document.createElement('div');
    top.className = 'ctop';
    var nameHtml = '<div class="cname-row"><span class="cname">' + (r.company || '') + '</span>';
    if (site) nameHtml += '<a class="visit-link" href="' + site + '" target="_blank">visit ↗</a>';
    nameHtml += '</div>';
    var metaParts = [r.sector, r.funding_amount, r.stage, r.employee_count ? r.employee_count + ' people' : ''].filter(function(v) { return v && v !== 'Unknown'; });
    nameHtml += '<div class="cmeta">' + metaParts.map(function(v, i) { return (i > 0 ? '<span class="cmeta-dot">·</span>' : '') + v; }).join(' ') + '</div>';

    top.innerHTML = '<div class="score-badge ' + cls + '">' + n + '</div><div class="cinfo">' + nameHtml + '</div><span class="clbl ' + cls + '">' + labelText + '</span><span class="chevron' + (open ? ' open' : '') + '">▾</span>';
    top.onclick = function() { r._open = !r._open; save(); renderCards(); };
    card.appendChild(top);

    if (open) {
      var body = document.createElement('div');
      body.className = 'cbody open';

      // Left column
      var left = document.createElement('div');
      left.className = 'cleft';

      var pg = '<div class="pgrid">';
      [['Website',r.website,true],['HQ',r.hq],['Founded',r.founded],['Team',r.employee_count],['Stage',r.stage],['Product',r.product_status],['Funding',r.funding_amount],['Investor',r.lead_investor]].forEach(function(x) {
        var u = x[2] ? su(x[1]) : '';
        pg += '<div class="pcell"><div class="pkey">' + x[0] + '</div><div class="pval' + (!x[1] || x[1] === 'Unknown' ? ' dim' : '') + '">';
        if (u) pg += '<a href="' + u + '" target="_blank">' + String(x[1]).replace(/^https?:\/\//, '') + '</a>';
        else pg += x[1] && x[1] !== 'Unknown' ? x[1] : '—';
        pg += '</div></div>';
      });
      pg += '</div>';

      var chips = '<div class="social-chips">';
      var tw = s.twitter ? 'https://twitter.com/' + String(s.twitter).replace('@', '') : '';
      [[tw,'𝕏 Twitter'],[s.linkedin,'in LinkedIn'],[s.discord,'◈ Discord'],[s.telegram,'✈ Telegram'],[s.github,'⌥ GitHub']].forEach(function(x) {
        var u = su(x[0]); if (u) chips += '<a class="social-chip" href="' + u + '" target="_blank">' + x[1] + '</a>';
      });
      chips += '</div>';

      var fnd = '<div>';
      var avatarColors = [['#FFE4DD','#FF5C35'],['#E8FAF3','#00C170'],['#EFF6FF','#3B82F6'],['#FFFBEB','#F59E0B']];
      if (ff.length) {
        ff.forEach(function(f, i) {
          var ini = String(f.name || '?').split(' ').map(function(w) { return w[0]; }).slice(0,2).join('').toUpperCase();
          var ac = avatarColors[i % avatarColors.length];
          fnd += '<div class="founder-row"><div class="fav" style="background:' + ac[0] + ';color:' + ac[1] + '">' + ini + '</div><div><div class="fname">' + (f.name||'') + '</div><div class="frole">' + (f.role||'') + (f.background ? ' · ' + f.background : '') + '</div></div></div>';
        });
      } else fnd += '<div style="font-size:12px;color:var(--tx3);font-weight:500">Unknown</div>';
      fnd += '</div>';

      var inv = [r.lead_investor, r.other_investors].filter(function(v) { return v && v !== 'null'; }).join(', ');
      left.innerHTML = '<div class="sec">Profile</div>' + pg +
        (inv ? '<div class="sec">Investors</div><div class="analysis-text">' + inv + '</div>' : '') +
        '<div class="sec">Socials</div>' + chips +
        '<div class="sec">Founders</div>' + fnd +
        '<div class="sec">Community</div><div class="analysis-text">' + (r.community_size || 'Unknown') + '</div>' +
        '<div class="sec">Marketing Status</div><div class="analysis-text">' + (r.marketing_notes || '—') + '</div>';

      // Right column
      var right = document.createElement('div');
      right.className = 'cright';

      var sigs = '<div class="sec" style="margin-top:0">GTM Signals</div><div>';
      [['recently_funded','Recently funded'],['no_cmo','No CMO'],['pre_launch_or_early','Pre-launch / early GTM'],['has_product','Has product'],['small_team','Small team'],['marketing_gap_visible','Marketing gap'],['active_community','Active community']].forEach(function(x) {
        var v = g[x[0]];
        var cls2 = v === true ? 'y' : v === false ? 'n' : 'u';
        var t = v === true ? 'Yes' : v === false ? 'No' : '?';
        sigs += '<div class="sig-row"><span class="sig-label">' + x[1] + '</span><span class="sig-val ' + cls2 + '">' + t + '</span></div>';
      });
      sigs += '</div>';

      right.innerHTML = sigs +
        '<div class="sec">Why They Fit</div><div class="analysis-block"><div class="analysis-text">' + (r.why_fit || '—') + '</div></div>' +
        '<div class="sec">Risks</div><div class="analysis-block"><div class="analysis-text" style="color:var(--amb)">' + (r.risks || '—') + '</div></div>' +
        '<div class="sec">Reach Out To</div><div class="reach-val" style="margin-bottom:14px">' + (r.decision_maker || '—') + '</div>' +
        '<div class="pitch-box"><div class="pitch-label">🎯 Pitch Opener</div><div class="pitch-text" id="pt' + id + '">' + (r.pitch_opener || '—') + '</div></div>';

      body.appendChild(left);
      body.appendChild(right);
      card.appendChild(body);

      var acts = document.createElement('div');
      acts.className = 'cact';

      var cp = document.createElement('button');
      cp.className = 'act-btn primary';
      cp.textContent = 'Copy Pitch';
      (function(cardId) {
        cp.onclick = function() {
          var el = document.getElementById('pt' + cardId);
          if (el) navigator.clipboard.writeText(el.textContent);
          cp.textContent = 'Copied!';
          setTimeout(function() { cp.textContent = 'Copy Pitch'; }, 1800);
        };
      })(id);
      acts.appendChild(cp);

      if (site) { var sb = document.createElement('button'); sb.className = 'act-btn'; sb.textContent = 'Visit Site'; (function(u) { sb.onclick = function() { window.open(u, '_blank'); }; })(site); acts.appendChild(sb); }
      var liu = su(s.linkedin); if (liu) { var lb = document.createElement('button'); lb.className = 'act-btn'; lb.textContent = 'LinkedIn'; (function(u) { lb.onclick = function() { window.open(u, '_blank'); }; })(liu); acts.appendChild(lb); }
      if (s.twitter && s.twitter !== 'null') { var twb = document.createElement('button'); twb.className = 'act-btn'; twb.textContent = 'Twitter'; (function(h) { twb.onclick = function() { window.open('https://twitter.com/' + h.replace('@', ''), '_blank'); }; })(s.twitter); acts.appendChild(twb); }

      var rm = document.createElement('button'); rm.className = 'act-btn ghost'; rm.textContent = 'Remove';
      (function(cardId) { rm.onclick = function() { DB = DB.filter(function(x) { return x._id !== cardId; }); save(); renderAll(); }; })(id);
      acts.appendChild(rm);
      card.appendChild(acts);
    }
    cont.appendChild(card);
  });
}

function doCSV() {
  var h = ['Company','Tagline','Website','Sector','HQ','Founded','Stage','Funding','Date','Lead Investor','Other Investors','Employees','Twitter','LinkedIn','Discord','Telegram','GitHub','Founders','Has CMO','Mktg Notes','Product','Community','Score','Label','Funded','No CMO','Pre-launch','Has Product','Small Team','Mktg Gap','Why Fit','Risks','Pitch','Decision Maker'];
  function esc(v) { var str = String(v == null ? '' : v).replace(/"/g, '""'); return (str.indexOf(',') >= 0 || str.indexOf('\\n') >= 0) ? '"' + str + '"' : str; }
  var rows = DB.map(function(r) {
    var s = r.socials || {}, g = r.gtm_signals || {}, f = (r.founders || []).map(function(x) { return x.name + ' (' + x.role + ')'; }).join('; ');
    return [r.company,r.tagline,r.website,r.sector,r.hq,r.founded,r.stage,r.funding_amount,r.funding_date,r.lead_investor,r.other_investors,r.employee_count,s.twitter,s.linkedin,s.discord,s.telegram,s.github,f,r.has_cmo,r.marketing_notes,r.product_status,r.community_size,r.gtm_readiness_score,r.gtm_label,g.recently_funded,g.no_cmo,g.pre_launch_or_early,g.has_product,g.small_team,g.marketing_gap_visible,r.why_fit,r.risks,r.pitch_opener,r.decision_maker].map(esc).join(',');
  });
  var a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([[h.join(',')].concat(rows).join('\\n')], { type: 'text/csv' }));
  a.download = 'gtm-leads.csv'; a.click();
}

document.addEventListener('DOMContentLoaded', function() {
  load();

  document.getElementById('rb').onclick = go;
  document.getElementById('ci').addEventListener('keydown', function(e) { if (e.key === 'Enter') go(); });
  document.getElementById('btog').onclick = function() { showPanel('bpanel'); };
  document.getElementById('itog').onclick = function() { showPanel('ipanel'); };
  document.getElementById('brb').onclick = bulk;
  document.getElementById('iib').onclick = importJSON;
  document.getElementById('csvbtn').onclick = doCSV;
  document.getElementById('fetch-btn').onclick = fetchLeads;
  document.getElementById('research-selected-btn').onclick = researchSelected;
  document.getElementById('clrbtn').onclick = function() {
    if (confirm('Clear all saved companies?')) { DB = []; save(); renderAll(); }
  };

  document.querySelectorAll('.source-pill').forEach(function(pill) {
    pill.onclick = function() {
      var src = pill.getAttribute('data-src');
      var idx = activeSources.indexOf(src);
      if (idx >= 0) { activeSources.splice(idx, 1); pill.classList.remove('active'); }
      else { activeSources.push(src); pill.classList.add('active'); }
    };
  });

  document.querySelectorAll('.filter-btn').forEach(function(btn) {
    btn.onclick = function() {
      fil = btn.getAttribute('data-f');
      document.querySelectorAll('.filter-btn').forEach(function(b) { b.classList.remove('on'); });
      btn.classList.add('on');
      renderCards();
    };
  });
});
"""

HTML += "<script>" + JS + "</script>\n"
HTML += "</body>\n</html>\n"


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        if self.path == '/db':
            data = json.dumps(load_db()).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        content = HTML.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
        if self.path == '/save':
            length = int(self.headers.get('Content-Length', 0))
            try:
                data = json.loads(self.rfile.read(length))
                save_db(data)
                self.respond({'ok': True})
            except Exception as e:
                self.respond({'error': str(e)})
            return

        if self.path != '/api':
            self.send_response(404); self.end_headers(); return

        length = int(self.headers.get('Content-Length', 0))
        try:
            body = json.loads(self.rfile.read(length))
        except:
            self.respond({'error': 'Bad request'}); return

        key = body.get('key', '').strip()
        company = body.get('company', '').strip()
        system = body.get('system', '')
        actual_key = os.environ.get('ANTHROPIC_API_KEY', key)

        if not actual_key:
            self.respond({'error': 'No API key configured'}); return
        if not company:
            self.respond({'error': 'Missing company name'}); return

        # Use web search only for fetch mode, otherwise use training knowledge (much cheaper)
        mode = body.get('mode', 'research')
        use_search = (mode == 'fetch')

        if use_search:
            messages = [{'role': 'user', 'content': 'Search the web and research this: "' + company + '". Then return the JSON response.'}]
            final_text = ''
            for _ in range(10):
                payload = json.dumps({
                    'model': 'claude-sonnet-4-20250514',
                    'max_tokens': 1500,
                    'system': system,
                    'tools': [{'type': 'web_search_20250305', 'name': 'web_search'}],
                    'messages': messages
                }).encode('utf-8')
                req = urllib.request.Request(
                    'https://api.anthropic.com/v1/messages',
                    data=payload,
                    headers={'Content-Type': 'application/json', 'x-api-key': actual_key, 'anthropic-version': '2023-06-01'},
                    method='POST'
                )
                try:
                    with urllib.request.urlopen(req, timeout=90) as resp:
                        data = json.loads(resp.read())
                except urllib.error.HTTPError as e:
                    err = e.read().decode('utf-8', errors='replace')
                    self.respond({'error': 'API error ' + str(e.code) + ': ' + err[:300]}); return
                except Exception as e:
                    self.respond({'error': str(e)}); return
                content = data.get('content', [])
                stop_reason = data.get('stop_reason', '')
                for block in content:
                    if block.get('type') == 'text':
                        final_text = block.get('text', '')
                if stop_reason == 'end_turn':
                    break
                elif stop_reason == 'tool_use':
                    messages.append({'role': 'assistant', 'content': content})
                    tool_results = [{'type': 'tool_result', 'tool_use_id': b['id'], 'content': [{'type': 'text', 'text': 'ok'}]} for b in content if b.get('type') == 'tool_use']
                    messages.append({'role': 'user', 'content': tool_results})
                else:
                    break
            self.respond({'text': final_text})
        else:
            # No web search — use training knowledge only (~10x cheaper)
            payload = json.dumps({
                'model': 'claude-sonnet-4-20250514',
                'max_tokens': 1200,
                'system': system,
                'messages': [{'role': 'user', 'content': 'Research this company using your knowledge and return the JSON profile: "' + company + '"'}]
            }).encode('utf-8')
            req = urllib.request.Request(
                'https://api.anthropic.com/v1/messages',
                data=payload,
                headers={'Content-Type': 'application/json', 'x-api-key': actual_key, 'anthropic-version': '2023-06-01'},
                method='POST'
            )
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read())
                text = ''.join(b.get('text','') for b in data.get('content',[]) if b.get('type')=='text')
                self.respond({'text': text})
            except urllib.error.HTTPError as e:
                err = e.read().decode('utf-8', errors='replace')
                self.respond({'error': 'API error ' + str(e.code) + ': ' + err[:300]})
            except Exception as e:
                self.respond({'error': str(e)})

    def respond(self, obj):
        data = json.dumps(obj).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    print('\n  GTM Scout running at http://localhost:' + str(PORT))
    print('  Press Ctrl+C to stop.\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Stopped.')
        sys.exit(0)
