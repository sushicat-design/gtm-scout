#!/usr/bin/env python3
#v20
import http.server, json, urllib.request, urllib.error, time, sys, os, socket

def find_port():
    for p in range(8765, 8800):
        try:
            s = socket.socket(); s.bind(('', p)); s.close(); return p
        except: continue
    return 8765

PORT = int(os.environ.get('PORT', find_port()))
# Persistent storage via GitHub Gist (free, survives Railway deploys)
GIST_ID = os.environ.get('GIST_ID', '')
GIST_TOKEN = os.environ.get('GIST_TOKEN', '')

def load_db():
    # Try GitHub Gist first
    if GIST_ID and GIST_TOKEN:
        try:
            req = urllib.request.Request(
                'https://api.github.com/gists/' + GIST_ID,
                headers={
                    'Authorization': 'token ' + GIST_TOKEN,
                    'Accept': 'application/vnd.github.v3+json',
                    'User-Agent': 'Scout-App'
                },
                method='GET'
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                gist_data = json.loads(resp.read())
                content = gist_data['files']['scout_db.json']['content']
                data = json.loads(content)
                if isinstance(data, list) and len(data) > 0 and 'init' not in str(data[0]):
                    print('[DB] Loaded', len(data), 'records from GitHub Gist')
                    return data
                print('[DB] Gist has placeholder data, returning empty')
        except Exception as e:
            print('[DB] Gist load error:', e)
    else:
        print('[DB] No Gist credentials - GIST_ID:', bool(GIST_ID), 'GIST_TOKEN:', bool(GIST_TOKEN))
    # Fallback to local file
    try:
        db_file = '/tmp/scout_db.json'
        if os.path.exists(db_file):
            with open(db_file) as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                print('[DB] Loaded', len(data), 'records from local file')
                return data
    except Exception as e:
        print('[DB] Local load error:', e)
    return []

def save_db(data):
    # Always save to local file first
    try:
        db_file = '/tmp/scout_db.json'
        with open(db_file, 'w') as f:
            json.dump(data, f)
        print('[DB] Saved', len(data), 'records to local file')
    except Exception as e:
        print('[DB] Local save error:', e)
    # Save to GitHub Gist
    if GIST_ID and GIST_TOKEN:
        try:
            payload = json.dumps({
                'files': {
                    'scout_db.json': {
                        'content': json.dumps(data)
                    }
                }
            }).encode('utf-8')
            req = urllib.request.Request(
                'https://api.github.com/gists/' + GIST_ID,
                data=payload,
                headers={
                    'Authorization': 'token ' + GIST_TOKEN,
                    'Accept': 'application/vnd.github.v3+json',
                    'Content-Type': 'application/json',
                    'User-Agent': 'Scout-App'
                },
                method='PATCH'
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                print('[DB] Saved', len(data), 'records to GitHub Gist, status:', resp.status)
        except Exception as e:
            print('[DB] Gist save error:', e)
    else:
        print('[DB] No Gist credentials')

CSS = """

*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#07090f;
  --sur:#0c1018;
  --sur2:#111620;
  --bor:#1c2333;
  --bor2:#263044;
  --pip:#2d9de8;
  --pip-dim:rgba(45,157,232,0.07);
  --pip-bor:rgba(45,157,232,0.2);
  --pip-deep:#1565c0;
  --pip-light:#5bc4f5;
  --amb:#f0a500;
  --red:#f85149;
  --grn:#3dd68c;
  --tx:#e2e8f0;
  --tx2:#8896aa;
  --tx3:#445566;
  --r:12px;
  --r-sm:8px;
  --r-pill:999px;
}
body{background:var(--bg);color:var(--tx);font-family:'Nunito',sans-serif;font-size:14px;min-height:100vh;font-weight:500}

/* ── TOPBAR ── */
.topbar{display:flex;align-items:center;gap:0;border-bottom:1px solid var(--bor);position:sticky;top:0;background:rgba(7,9,15,0.95);backdrop-filter:blur(20px);z-index:100}
.topbar-brand{display:flex;align-items:center;gap:10px;padding:14px 28px;border-right:1px solid var(--bor)}
.logo-mark{width:32px;height:32px;display:flex;align-items:center;justify-content:center}
.logo-text{font-family:'Nunito',sans-serif;font-size:18px;font-weight:800;letter-spacing:-0.03em;color:var(--tx)}
.nav{display:flex;align-items:stretch;flex:1}
.nav-tab{padding:0 24px;font-size:13px;font-weight:600;color:var(--tx3);cursor:pointer;border:none;background:none;font-family:'Nunito',sans-serif;border-bottom:2px solid transparent;transition:all .2s;display:flex;align-items:center;gap:7px;height:54px}
.nav-tab:hover{color:var(--tx2)}
.nav-tab.active{color:var(--pip);border-bottom-color:var(--pip)}
.nav-tab .badge{background:var(--pip);color:#fff;font-size:10px;font-weight:700;padding:1px 6px;border-radius:var(--r-pill);min-width:18px;text-align:center}
.nav-tab .badge.amber{background:var(--amb)}
.topbar-right{display:flex;align-items:center;gap:12px;padding:0 24px;margin-left:auto}
.save-ind{font-size:11px;color:var(--tx3);min-width:60px;text-align:right}

/* ── PAGES ── */
.page{display:none;padding:32px 28px;max-width:1200px;margin:0 auto}
.page.active{display:block}

/* ── SEARCH PAGE ── */
.search-hero{text-align:center;padding:40px 0 32px}
.search-hero h1{font-size:32px;font-weight:800;letter-spacing:-0.04em;margin-bottom:8px}
.search-hero p{font-size:14px;color:var(--tx3)}
.search-box{display:flex;gap:8px;max-width:600px;margin:28px auto 0}
#ci{flex:1;background:var(--sur);border:1px solid var(--bor2);color:var(--tx);font-family:'Nunito',sans-serif;font-size:14px;font-weight:500;padding:12px 18px;outline:none;border-radius:var(--r);transition:border-color .2s}
#ci:focus{border-color:var(--pip)}
#rb{background:var(--pip);color:#fff;border:none;font-weight:700;font-size:13px;padding:12px 24px;cursor:pointer;white-space:nowrap;font-family:'Nunito',sans-serif;border-radius:var(--r);transition:opacity .2s}
#rb:hover{opacity:.88}
#rb:disabled{opacity:.35;cursor:not-allowed}
.search-actions{display:flex;gap:10px;justify-content:center;margin-top:10px}
.tlink{background:none;border:1px solid var(--bor);color:var(--tx3);font-size:12px;cursor:pointer;font-family:'Nunito',sans-serif;padding:6px 14px;border-radius:var(--r-pill);transition:all .2s}
.tlink:hover{border-color:var(--pip);color:var(--pip)}
.tlink.blu{color:var(--pip);border-color:var(--pip-bor)}
#ldg{display:none;align-items:center;justify-content:center;gap:10px;margin-top:16px;font-size:13px;color:var(--tx3)}
.spinner{width:14px;height:14px;border:2px solid var(--bor2);border-top-color:var(--pip);border-radius:50%;animation:spin .7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
#err{display:none;margin-top:12px;padding:12px 16px;background:rgba(248,81,73,0.06);border:1px solid rgba(248,81,73,0.2);color:var(--red);font-size:12px;border-radius:var(--r);max-width:600px;margin-left:auto;margin-right:auto}
.panel-extra{display:none;background:var(--sur);border:1px solid var(--bor);padding:16px;margin-top:16px;border-radius:var(--r);max-width:600px;margin-left:auto;margin-right:auto}
.panel-label{font-size:10px;color:var(--tx3);text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;font-weight:700}
#bi,#ii{width:100%;background:var(--bg);border:1px solid var(--bor2);color:var(--tx);font-family:'Nunito',sans-serif;font-size:13px;padding:10px 14px;min-height:90px;resize:vertical;outline:none;line-height:1.7;border-radius:var(--r-sm)}
#bi:focus,#ii:focus{border-color:var(--pip)}
.sub-btn{background:var(--pip);color:#fff;border:none;font-weight:700;font-size:12px;padding:8px 18px;cursor:pointer;margin-top:8px;font-family:'Nunito',sans-serif;border-radius:var(--r-sm)}
#ierr{display:none;color:var(--red);font-size:12px;margin-top:6px}


/* ── FETCH MODAL ── */
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.6);backdrop-filter:blur(4px);z-index:200;align-items:flex-start;justify-content:center;padding-top:100px}
.modal-overlay.open{display:flex}
.modal{background:var(--sur);border:1px solid var(--bor2);border-radius:var(--r);padding:24px;width:480px;max-width:90vw;box-shadow:0 20px 60px rgba(0,0,0,0.5)}
.modal-title{font-size:16px;font-weight:800;letter-spacing:-.02em;margin-bottom:4px}
.modal-sub{font-size:12px;color:var(--tx3);margin-bottom:18px}
.modal-close{position:absolute;top:16px;right:16px;background:none;border:none;color:var(--tx3);font-size:18px;cursor:pointer;line-height:1;padding:4px 8px;border-radius:var(--r-sm)}
.modal-close:hover{color:var(--tx);background:var(--bor)}
.modal-footer{display:flex;gap:8px;justify-content:flex-end;margin-top:18px;padding-top:16px;border-top:1px solid var(--bor)}
.modal-btn{font-size:12px;padding:8px 18px;border-radius:var(--r-sm);font-family:'Nunito',sans-serif;font-weight:700;cursor:pointer;transition:all .2s}
.modal-btn.primary{background:var(--pip);color:#fff;border:none}
.modal-btn.primary:hover{opacity:.88}
.modal-btn.primary:disabled{opacity:.35;cursor:not-allowed}
.modal-btn.secondary{background:none;border:1px solid var(--bor2);color:var(--tx2)}
.modal-btn.secondary:hover{border-color:var(--pip);color:var(--pip)}

/* ── FETCH PANEL on search page ── */
.fetch-panel{background:var(--pip-dim);border:1px solid var(--pip-bor);padding:20px;margin-top:32px;border-radius:var(--r)}
.fetch-title{font-size:14px;font-weight:800;color:var(--pip);margin-bottom:4px;letter-spacing:-.02em}
.fetch-sub{font-size:12px;color:var(--tx3);margin-bottom:14px}
.fetch-top{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:14px}
.src-pills{display:flex;gap:6px;flex-wrap:wrap}
.src-pill{padding:4px 12px;font-size:11px;font-weight:600;border:1px solid var(--bor2);background:var(--bg);color:var(--tx3);cursor:pointer;font-family:'Nunito',sans-serif;text-transform:uppercase;letter-spacing:.04em;border-radius:var(--r-pill);transition:all .2s}
.src-pill.on{border-color:var(--pip);color:var(--pip);background:var(--pip-dim)}
#fetch-btn{background:var(--pip);color:#fff;border:none;font-weight:700;font-size:12px;padding:10px 20px;cursor:pointer;font-family:'Nunito',sans-serif;border-radius:var(--r);transition:opacity .2s}
#fetch-btn:hover{opacity:.88}
#fetch-btn:disabled{opacity:.35;cursor:not-allowed}
#fetch-ldg{display:none;align-items:center;gap:8px;font-size:12px;color:var(--tx3);margin-top:10px}
#fetch-err{display:none;margin-top:10px;padding:10px 14px;background:rgba(248,81,73,0.06);border:1px solid rgba(248,81,73,0.2);color:var(--red);font-size:12px;border-radius:var(--r-sm)}
#fetch-results{display:none;margin-top:14px;padding-top:14px;border-top:1px solid var(--pip-bor)}
.fetch-list{display:flex;flex-direction:column;gap:4px;margin-bottom:12px;max-height:280px;overflow-y:auto}
.fetch-item{display:flex;align-items:center;gap:10px;padding:10px 14px;background:var(--bg);border:1px solid var(--bor);cursor:pointer;border-radius:var(--r-sm);transition:border-color .2s}
.fetch-item:hover{border-color:var(--pip)}
.fetch-item.sel{border-color:var(--pip);background:var(--pip-dim)}
.fetch-item input{accent-color:var(--pip);width:15px;height:15px;cursor:pointer;flex-shrink:0}
.fetch-item-name{font-size:13px;font-weight:700;color:var(--tx)}
.fetch-item-meta{font-size:11px;color:var(--tx3);margin-top:1px}
#res-sel-btn{background:var(--pip);color:#fff;border:none;font-weight:700;font-size:12px;padding:9px 18px;cursor:pointer;font-family:'Nunito',sans-serif;border-radius:var(--r-sm)}
#fetch-count{font-size:11px;color:var(--tx3);margin-left:10px}

/* ── PIPELINE PAGE ── */
.pipeline-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px}
.pipeline-header h2{font-size:22px;font-weight:800;letter-spacing:-.03em}
.pipeline-board{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;align-items:start}
.pipeline-col{background:var(--sur);border:1px solid var(--bor);padding:14px;border-radius:var(--r)}
.pipeline-col-header{font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.12em;padding-bottom:12px;border-bottom:1px solid var(--bor);margin-bottom:10px;display:flex;align-items:center;justify-content:space-between}
.pipeline-card{background:var(--bg);border:1px solid var(--bor);padding:16px;margin-bottom:8px;cursor:pointer;transition:all .2s;border-radius:var(--r-sm)}
.pipeline-card:hover{border-color:var(--pip);transform:translateY(-1px);box-shadow:0 4px 16px rgba(45,157,232,0.12)}
.pipeline-card-name{font-size:14px;font-weight:800;margin-bottom:4px;color:var(--tx);letter-spacing:-.02em}
.pipeline-card-meta{font-size:11px;color:var(--tx3);margin-bottom:6px}
.pipeline-card-note{font-size:11px;color:var(--tx3);font-style:italic;margin-top:6px;line-height:1.5}
.pipeline-card-date{font-size:11px;color:var(--amb);margin-top:4px}
.pipeline-empty{font-size:12px;color:var(--tx3);text-align:center;padding:24px 0;font-style:italic}

/* ── SAVED LEADS PAGE (3-col open cards) ── */
.leads-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}
.leads-header h2{font-size:22px;font-weight:800;letter-spacing:-.03em}
.leads-toolbar{display:flex;align-items:center;gap:8px;margin-bottom:20px;flex-wrap:wrap}
.fb{font-size:11px;padding:6px 14px;background:none;border:1px solid var(--bor);color:var(--tx3);cursor:pointer;font-family:'Nunito',sans-serif;border-radius:var(--r-pill);transition:all .2s;font-weight:600}
.fb:hover{border-color:var(--pip);color:var(--pip)}
.fb.on{border-color:var(--pip);color:var(--pip);background:var(--pip-dim)}
.tb-right{margin-left:auto;display:flex;gap:8px}
.tb-btn{font-size:11px;padding:6px 14px;background:none;border:1px solid var(--bor2);color:var(--tx2);cursor:pointer;font-family:'Nunito',sans-serif;border-radius:var(--r-sm);font-weight:600;transition:all .2s}
.tb-btn:hover{border-color:var(--pip);color:var(--pip)}
.tb-btn.danger{color:var(--red);border-color:rgba(248,81,73,0.2)}

/* 3-col open cards grid */
.cards-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.lead-card{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);overflow:hidden;transition:border-color .2s,box-shadow .2s}
.lead-card:hover{border-color:var(--bor2);box-shadow:0 4px 20px rgba(0,0,0,0.3)}
.lead-card-header{padding:16px 18px 12px;border-bottom:1px solid var(--bor)}
.lead-card-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:6px}
.lead-card-name{font-size:16px;font-weight:800;letter-spacing:-.02em;color:var(--tx)}
.lead-card-score{font-size:20px;font-weight:800;letter-spacing:-.03em}
.lead-card-meta{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.lead-card-tag{font-size:10px;font-weight:700;padding:2px 9px;border-radius:var(--r-pill);border:1px solid;text-transform:uppercase;letter-spacing:.05em}
.lead-card-sector{font-size:11px;color:var(--tx3)}
.lead-card-body{padding:16px 18px}
.lc-sec{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.14em;margin:12px 0 8px;display:flex;align-items:center;gap:8px;font-weight:700}
.lc-sec::after{content:'';flex:1;height:1px;background:var(--bor)}
.lc-grid{display:grid;grid-template-columns:1fr 1fr;gap:4px;margin-bottom:4px}
.lc-cell{background:var(--bg);border:1px solid var(--bor);padding:7px 10px;border-radius:var(--r-sm)}
.lc-key{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.06em;margin-bottom:2px;font-weight:700}
.lc-val{font-size:12px;color:var(--tx)}
.lc-val a{color:var(--pip);text-decoration:none}
.lc-val.dim{color:var(--tx3);font-style:italic}
.lc-text{font-size:12px;color:var(--tx2);line-height:1.75;margin-bottom:4px}
.sig-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid var(--bor);font-size:12px}
.sig-row:last-child{border-bottom:none}
.sy{font-size:11px;font-weight:700;color:var(--pip)}
.sn{font-size:11px;font-weight:700;color:var(--red)}
.su{font-size:11px;color:var(--tx3)}
.pitch-box{background:var(--pip-dim);border:1px solid var(--pip-bor);padding:14px;margin-top:8px;border-radius:var(--r-sm)}
.pitch-label{font-size:9px;color:var(--pip);text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;font-weight:700}
.pitch-text{font-size:12px;color:#c8e8ff;line-height:1.8;font-style:italic}
.founder-row{display:flex;gap:10px;align-items:flex-start;padding:8px 10px;background:var(--bg);border:1px solid var(--bor);margin-bottom:4px;border-radius:var(--r-sm)}
.fav{width:28px;height:28px;border-radius:50%;background:var(--pip-dim);border:1px solid var(--pip-bor);display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:var(--pip);flex-shrink:0;margin-top:1px}
.fname{font-size:13px;font-weight:700}
.frole{font-size:11px;color:var(--tx3);line-height:1.5}
.social-links{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px}
.social-links a{font-size:11px;padding:3px 10px;border:1px solid var(--bor);color:var(--tx2);text-decoration:none;border-radius:var(--r-pill);transition:all .2s}
.social-links a:hover{border-color:var(--pip);color:var(--pip)}
.lead-card-actions{display:flex;gap:6px;padding:12px 16px;background:var(--bg);border-top:1px solid var(--bor);flex-wrap:wrap;align-items:center}
.abtn{font-size:11px;padding:5px 12px;background:none;border:1px solid var(--bor2);color:var(--tx2);cursor:pointer;font-family:'Nunito',sans-serif;border-radius:var(--r-pill);transition:all .2s;font-weight:600}
.abtn:hover{border-color:var(--pip);color:var(--pip)}
.abtn.g{border-color:var(--pip-bor);color:var(--pip);background:var(--pip-dim)}
.abtn.ghost{margin-left:auto;color:var(--tx3)}
.notes-area{width:100%;background:var(--bg);border:1px solid var(--bor2);color:var(--tx);font-family:'Nunito',sans-serif;font-size:12px;padding:8px 12px;min-height:56px;resize:none;outline:none;line-height:1.6;border-radius:var(--r-sm);margin-top:4px}
.notes-area:focus{border-color:var(--pip)}
.hiring-badge{font-size:10px;color:var(--pip-light);border:1px solid rgba(91,196,245,0.3);padding:2px 8px;font-weight:700;border-radius:var(--r-pill)}

/* ── INBOX PAGE ── */
.inbox-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.inbox-header h2{font-size:22px;font-weight:800;letter-spacing:-.03em}
.inbox-empty{text-align:center;padding:80px 20px;color:var(--tx3)}
.inbox-empty-title{font-size:18px;font-weight:700;color:var(--tx2);margin-bottom:8px;letter-spacing:-.02em}
.inbox-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.inbox-card{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);overflow:hidden;transition:all .2s}
.inbox-card:hover{border-color:var(--bor2)}
.inbox-card-header{padding:16px 18px 12px}
.inbox-card-name{font-size:15px;font-weight:800;letter-spacing:-.02em;margin-bottom:3px}
.inbox-card-meta{font-size:11px;color:var(--tx3);margin-bottom:8px}
.inbox-card-body{padding:0 18px 14px;font-size:12px;color:var(--tx2);line-height:1.75}
.inbox-card-actions{display:flex;gap:8px;padding:12px 16px;background:var(--bg);border-top:1px solid var(--bor)}
.btn-approve{flex:1;background:var(--pip);color:#fff;border:none;font-weight:700;font-size:12px;padding:9px;cursor:pointer;font-family:'Nunito',sans-serif;border-radius:var(--r-sm);transition:opacity .2s}
.btn-approve:hover{opacity:.88}
.btn-dismiss{flex:1;background:none;color:var(--tx3);border:1px solid var(--bor);font-weight:600;font-size:12px;padding:9px;cursor:pointer;font-family:'Nunito',sans-serif;border-radius:var(--r-sm);transition:all .2s}
.btn-dismiss:hover{border-color:var(--red);color:var(--red)}

/* ── EMPTY STATE ── */
.empty{text-align:center;padding:80px 20px;color:var(--tx3)}
.empty-title{font-size:18px;font-weight:800;color:var(--tx2);margin-bottom:10px;letter-spacing:-.03em}
.empty p{font-size:13px;line-height:2}

/* ── PIP HUNT ── */
.ph-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.ph-header h2{font-size:22px;font-weight:800;letter-spacing:-.03em}
.ph-tabs{display:flex;gap:4px;margin-bottom:20px;border-bottom:1px solid var(--bor);padding-bottom:0}
.ph-tab{padding:8px 20px;font-size:13px;font-weight:600;color:var(--tx3);cursor:pointer;border:none;background:none;font-family:'Nunito',sans-serif;border-bottom:2px solid transparent;transition:all .2s;margin-bottom:-1px}
.ph-tab:hover{color:var(--tx2)}
.ph-tab.active{color:var(--pip);border-bottom-color:var(--pip)}
.ph-controls{display:flex;align-items:center;gap:10px;margin-bottom:20px;flex-wrap:wrap}
.ph-filter{font-size:11px;padding:5px 12px;background:none;border:1px solid var(--bor);color:var(--tx3);cursor:pointer;font-family:'Nunito',sans-serif;border-radius:var(--r-pill);transition:all .2s;font-weight:600}
.ph-filter:hover{border-color:var(--pip);color:var(--pip)}
.ph-filter.on{border-color:var(--pip);color:var(--pip);background:var(--pip-dim)}
.ph-fetch-btn{background:var(--pip);color:#fff;border:none;font-weight:700;font-size:12px;padding:9px 20px;cursor:pointer;font-family:'Nunito',sans-serif;border-radius:var(--r);transition:opacity .2s;margin-left:auto}
.ph-fetch-btn:hover{opacity:.88}
.ph-fetch-btn:disabled{opacity:.35;cursor:not-allowed}
.ph-status{font-size:11px;color:var(--tx3);margin-left:8px}
.ph-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.ph-card{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);overflow:hidden;transition:all .2s}
.ph-card:hover{border-color:var(--bor2);box-shadow:0 4px 20px rgba(0,0,0,0.3)}
.ph-card.saved{border-color:var(--pip-bor);background:var(--pip-dim)}
.ph-card-header{padding:16px 18px 12px}
.ph-card-role{font-size:14px;font-weight:800;letter-spacing:-.02em;color:var(--tx);margin-bottom:4px}
.ph-card-company{font-size:13px;font-weight:700;color:var(--pip);margin-bottom:4px}
.ph-card-meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}
.ph-tag{font-size:10px;font-weight:600;padding:2px 9px;border-radius:var(--r-pill);border:1px solid var(--bor2);color:var(--tx3)}
.ph-tag.remote{border-color:var(--pip-bor);color:var(--pip-light)}
.ph-tag.salary{border-color:rgba(240,165,0,0.3);color:var(--amb)}
.ph-tag.new{border-color:rgba(61,214,140,0.3);color:var(--grn)}
.ph-card-body{padding:0 18px 14px}
.ph-desc{font-size:12px;color:var(--tx2);line-height:1.75;margin-bottom:12px}
.ph-apply{display:flex;align-items:center;gap:6px;padding:10px 12px;background:var(--bg);border:1px solid var(--bor);border-radius:var(--r-sm);margin-bottom:8px}
.ph-apply-method{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:var(--tx3);min-width:60px}
.ph-apply-link{font-size:12px;color:var(--pip);text-decoration:none;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ph-apply-link:hover{text-decoration:underline}
.ph-card-actions{display:flex;gap:6px;padding:10px 16px;background:var(--bg);border-top:1px solid var(--bor);flex-wrap:wrap}
.ph-saved-list{margin-top:32px}
.ph-saved-list h3{font-size:16px;font-weight:800;letter-spacing:-.02em;margin-bottom:14px;color:var(--tx2)}
.ph-empty{text-align:center;padding:80px 20px;color:var(--tx3)}
.ph-empty-title{font-size:18px;font-weight:800;color:var(--tx2);margin-bottom:8px;letter-spacing:-.03em}

"""

JS = """

var DB = [];
var INBOX = [];
var busy = false;
var activeSources = ['techcrunch','blockworks','theblock','producthunt','linkedinjobs'];
var currentPage = 'search';
var fil = 'all';

var SYS = "Return ONLY a valid JSON object, no markdown, no backticks, no text before or after. Fields: company, tagline, website, sector, hq, founded, stage, funding_amount, funding_date, lead_investor, other_investors, employee_count, socials (object: twitter, linkedin, discord, telegram, github), founders (array of: name/role/background), has_cmo (bool), has_marketing_hire (bool), marketing_notes, product_status, community_size, hiring_remote (bool - true if they have open remote job listings especially marketing/growth/comms roles), gtm_readiness_score (integer 0-100), gtm_label (exactly Hot Lead if 80+, Warm Lead if 50-79, Cold Lead if below 50), gtm_signals (object of booleans: recently_funded, no_cmo, pre_launch_or_early, active_community, has_product, small_team, marketing_gap_visible), why_fit, risks, pitch_opener, decision_maker, outreach_status (always set to not_contacted), best_contact_title (the exact title of the best person to reach out to for fractional CMO services - prefer CMO, VP Marketing, Head of Growth, Head of Marketing, Co-founder if no marketing hire, or CEO as last resort), best_contact_name (their name if known, else null). Use null for unknown.";
var FETCH_SYS = "You are a funding news analyst. Search the web for startup funding announcements from the last 14 days. Focus on AI, web3, crypto, blockchain, DeFi, fintech. Return ONLY a valid JSON array, no markdown. Each item: {company:Name,sector:AI/Web3/etc,funding:$XM,stage:Seed/Series A/etc,source:publication}. Max 15 companies. Only include real recent raises.";

function load() {
  fetch('/db').then(function(r){return r.json();}).then(function(d){
    if(Array.isArray(d)){
      DB = d.filter(function(x){return !x._inbox;});
      INBOX = d.filter(function(x){return x._inbox;});
      updateBadges();
      if(currentPage==='leads') renderLeads();
      if(currentPage==='pipeline') renderPipelinePage();
      if(currentPage==='inbox') renderInbox();
    }
  }).catch(function(){DB=[];INBOX=[];});
}


function save() {
  var ind = document.getElementById('save-ind');
  if(ind) { ind.textContent = 'saving...'; ind.style.color = 'var(--tx3)'; }
  fetch('/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(DB)})
  .then(function(r){return r.json();})
  .then(function(d){
    if(ind) { ind.textContent = d.ok ? 'saved ✓' : 'save error'; ind.style.color = d.ok ? 'var(--grn)' : 'var(--red)'; }
    setTimeout(function(){ if(ind) ind.textContent = ''; }, 3000);
  })
  .catch(function(e){
    if(ind) { ind.textContent = 'save failed'; ind.style.color = 'var(--red)'; }
  });
}


function saveAll() {
  var all = DB.concat(INBOX);
  fetch('/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(all)})
  .then(function(r){return r.json();})
  .then(function(d){
    var ind=document.getElementById('save-ind');
    if(ind){ind.textContent=d.ok?'saved ✓':'save error';ind.style.color=d.ok?'var(--pip)':'var(--red)';}
    setTimeout(function(){var ind=document.getElementById('save-ind');if(ind)ind.textContent='';},3000);
  }).catch(function(){
    var ind=document.getElementById('save-ind');
    if(ind){ind.textContent='save failed';ind.style.color='var(--red)';}
  });
}

// Override save to use saveAll
function save(){ saveAll(); }

function updateBadges() {
  var lb = document.getElementById('leads-badge');
  var ib = document.getElementById('inbox-badge');
  if(lb) lb.textContent = DB.length;
  if(ib) { ib.textContent = INBOX.length; ib.style.display = INBOX.length ? '' : 'none'; }
}

function setPage(page) {
  currentPage = page;
  document.querySelectorAll('.page').forEach(function(p){p.classList.remove('active');});
  document.querySelectorAll('.nav-tab').forEach(function(t){t.classList.remove('active');});
  document.getElementById('page-'+page).classList.add('active');
  document.getElementById('tab-'+page).classList.add('active');
  if(page==='leads') renderLeads();
  if(page==='pipeline') renderPipelinePage();
  if(page==='inbox') renderInbox();
  if(page==='piphunt'){phLoad();phRenderJobs();}
}

// ── HELPERS ──────────────────────────────────────────────────────────────────
function sc(n){return n>=80?'var(--pip)':n>=50?'var(--amb)':'var(--tx3)';}
function su(v){if(!v||v==='null'||v==='undefined')return '';return String(v).indexOf('http')===0?v:'https://'+v;}

// ── SEARCH PAGE ──────────────────────────────────────────────────────────────
function go(){var v=document.getElementById('ci').value.trim();if(!v||busy)return;document.getElementById('ci').value='';run(v);}

function bulk(){
  if(busy)return;
  var names=document.getElementById('bi').value.trim().split('\\n').map(function(s){return s.trim();}).filter(Boolean);
  if(!names.length)return;
  document.getElementById('bi').value='';
  var i=0;function next(){if(i>=names.length)return;run(names[i++],next);}next();
}

function importJSON(){
  var raw=document.getElementById('ii').value.trim();
  var errEl=document.getElementById('ierr');errEl.style.display='none';
  try{
    var clean=raw.replace(/```json/g,'').replace(/```/g,'').trim();
    var parsed=clean.charAt(0)==='['?JSON.parse(clean):[JSON.parse(clean.slice(clean.indexOf('{'),clean.lastIndexOf('}')+1))];
    var added=0;
    for(var i=0;i<parsed.length;i++){var r=parsed[i];if(r&&r.company){r._id='id'+Date.now()+Math.floor(Math.random()*9999);r._open=true;DB.unshift(r);added++;}}
    if(!added)throw new Error('No valid company objects found');
    save();updateBadges();document.getElementById('ii').value='';
    document.getElementById('ipanel').style.display='none';
  }catch(e){errEl.textContent='Error: '+e.message;errEl.style.display='block';}
}

function showPanel(id){
  ['bpanel','ipanel'].forEach(function(pid){
    var el=document.getElementById(pid);
    if(el) el.style.display=(pid===id&&el.style.display!=='block')?'block':'none';
  });
  var btog=document.getElementById('btog');
  var itog=document.getElementById('itog');
  if(btog) btog.textContent=document.getElementById('bpanel').style.display==='block'?'− Bulk':'+ Bulk';
  if(itog) itog.textContent=document.getElementById('ipanel').style.display==='block'?'− Import JSON':'+ Import JSON';
}


function run(company,callback){
  busy=true;document.getElementById('rb').disabled=true;document.getElementById('ci').disabled=true;
  document.getElementById('err').style.display='none';document.getElementById('lname').textContent=company;
  document.getElementById('ldg').style.display='flex';
  var secs=0;document.getElementById('ltimer').textContent='0s';
  ti=setInterval(function(){document.getElementById('ltimer').textContent=(++secs)+'s';},1000);
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:'',company:company,system:SYS})})
  .then(function(r){return r.json();}).then(function(d){
    if(d.error)throw new Error(d.error);
    var t=(d.text||'').replace(/```json/g,'').replace(/```/g,'').trim();
    var a=t.indexOf('{'),b=t.lastIndexOf('}');if(a<0||b<0)throw new Error('No JSON returned');
    var res=JSON.parse(t.slice(a,b+1));
    if(!res.company)throw new Error('Missing company data');
    res._open=true;
    // Update existing or add new
    var existing=DB.findIndex(function(x){return x.company&&x.company.toLowerCase()===res.company.toLowerCase();});
    if(existing>=0){res._id=DB[existing]._id;DB[existing]=res;}else{res._id='id'+Date.now();DB.unshift(res);}
    save();renderAll();
  }).catch(function(e){var el=document.getElementById('err');el.textContent='Error: '+e.message;el.style.display='block';})
  .finally(function(){clearInterval(ti);document.getElementById('ldg').style.display='none';document.getElementById('rb').disabled=false;document.getElementById('ci').disabled=false;busy=false;if(callback)setTimeout(callback,400);});
}


// ── FETCH / INBOX FLOW ───────────────────────────────────────────────────────

function fetchLeads() {
  var btn=document.getElementById('fetch-btn');
  var ldg=document.getElementById('fetch-ldg');
  var errEl=document.getElementById('fetch-err');
  var res=document.getElementById('fetch-results');
  btn.disabled=true; errEl.style.display='none'; res.style.display='none'; ldg.style.display='flex';
  var srcNames=activeSources.map(function(s){
    return s==='techcrunch'?'TechCrunch':s==='blockworks'?'Blockworks':s==='theblock'?'The Block':
           s==='producthunt'?'Product Hunt':s==='linkedinjobs'?'LinkedIn Jobs':'crypto-fundraising.info';
  }).join(', ');
  var extraInstructions = '';
  if(activeSources.indexOf('producthunt')>=0) extraInstructions += ' Also search Product Hunt for recently launched startups (last 30 days) that appear to have no CMO or marketing team yet.';
  if(activeSources.indexOf('linkedinjobs')>=0) extraInstructions += ' Also search LinkedIn job postings for companies actively hiring a CMO, VP Marketing, Head of Marketing, or Head of Growth - these are prime fractional CMO prospects.';
  var prompt='Search '+srcNames+' for startup funding announcements and leads from the last 14 days. Focus on AI, SaaS, fintech, web3. Return a JSON array of companies.'+extraInstructions;
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:'',company:prompt,system:FETCH_SYS,mode:'fetch'})})
  .then(function(r){return r.json();}).then(function(d){
    if(d.error)throw new Error(d.error);
    var t=d.text||'';t=t.replace(/```json/g,'').replace(/```/g,'').trim();
    var a=t.indexOf('['),b=t.lastIndexOf(']');if(a<0||b<0)throw new Error('No results found');
    var cos=JSON.parse(t.slice(a,b+1));
    // Filter out error messages or non-company results
    var badWords=['insufficient','unable','error','no data','no results','no companies','n/a','unknown','failed'];
    cos=cos.filter(function(co){
      if(!co.company||typeof co.company!=='string')return false;
      var lower=co.company.toLowerCase();
      return !badWords.some(function(w){return lower.indexOf(w)>=0;});
    });
    if(!cos.length)throw new Error('No valid companies found in results');
    var list=document.getElementById('fetch-list');list.innerHTML='';
    cos.forEach(function(co){
      var item=document.createElement('div');item.className='fetch-item sel';
      item.innerHTML='<input type="checkbox" checked data-co="'+encodeURIComponent(JSON.stringify(co))+'"><div><div class="fetch-item-name">'+(co.company||'?')+'</div><div class="fetch-item-meta">'+[co.sector,co.funding,co.stage,co.source].filter(Boolean).join(' · ')+'</div></div>';
      item.onclick=function(e){if(e.target.type==='checkbox')return;var cb=item.querySelector('input');cb.checked=!cb.checked;item.classList.toggle('sel',cb.checked);updateCount();};
      item.querySelector('input').onchange=function(){item.classList.toggle('sel',this.checked);updateCount();};
      list.appendChild(item);
    });
    updateCount();ldg.style.display='none';res.style.display='block';btn.disabled=false;
  }).catch(function(e){ldg.style.display='none';errEl.textContent='Error: '+e.message;errEl.style.display='block';btn.disabled=false;});
}


function updateCount(){var n=document.querySelectorAll('#fetch-list input:checked').length;document.getElementById('fetch-count').textContent=n+' selected';}


function researchSelected(){
  closeFetchModal();
  var cbs=document.querySelectorAll('#fetch-list input:checked');
  var names=[];
  cbs.forEach(function(cb){
    try{var co=JSON.parse(decodeURIComponent(cb.getAttribute('data-co')));if(co.company)names.push(co.company);}catch(e){}
  });
  if(!names.length)return;
  document.getElementById('fetch-results').style.display='none';
  // Research each and add to INBOX for review
  var i=0;
  function next(){
    if(i>=names.length)return;
    var name=names[i++];
    runToInbox(name, next);
  }
  next();
}

function runToInbox(company, callback){
  var ind=document.getElementById('save-ind');
  if(ind){ind.textContent='researching '+company+'...';ind.style.color='var(--tx3)';}
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:'',company:company,system:SYS})})
  .then(function(r){return r.json();}).then(function(d){
    if(d.error)throw new Error(d.error);
    var t=(d.text||'').replace(/```json/g,'').replace(/```/g,'').trim();
    var a=t.indexOf('{'),b=t.lastIndexOf('}');if(a<0||b<0)throw new Error('No JSON');
    var res=JSON.parse(t.slice(a,b+1));
    if(!res.company)throw new Error('Missing company');
    res._id='id'+Date.now()+Math.floor(Math.random()*9999);
    res._inbox=true;
    res._open=false;
    INBOX.unshift(res);
    save();updateBadges();
    if(currentPage==='inbox') renderInbox();
    if(ind){ind.textContent='added to inbox';ind.style.color='var(--pip)';}
    setTimeout(function(){if(ind)ind.textContent='';},2000);
  }).catch(function(e){
    if(ind){ind.textContent='error: '+e.message;ind.style.color='var(--red)';}
    setTimeout(function(){if(ind)ind.textContent='';},3000);
  }).finally(function(){
    if(callback) setTimeout(callback, 300);
  });
}

function approveInboxCard(id){
  var idx=INBOX.findIndex(function(x){return x._id===id;});
  if(idx<0)return;
  var card=INBOX.splice(idx,1)[0];
  card._inbox=false;
  card.outreach_status='not_contacted';
  DB.unshift(card);
  save();updateBadges();renderInbox();
}

function dismissInboxCard(id){
  INBOX=INBOX.filter(function(x){return x._id!==id;});
  save();updateBadges();renderInbox();
}

// ── RENDER: SAVED LEADS (3-col open cards) ───────────────────────────────────
function renderLeads(){
  var shown=fil==='all'?DB:DB.filter(function(r){
    return r.gtm_label===(fil==='hot'?'Hot Lead':fil==='warm'?'Warm Lead':'Cold Lead');
  });
  var cont=document.getElementById('leads-grid');
  if(!cont)return;
  cont.innerHTML='';
  if(!shown.length){
    cont.innerHTML='<div class="empty" style="grid-column:1/-1"><div class="empty-title">No saved leads yet</div><p>Research companies on the Search page or approve leads from your Inbox.</p></div>';
    return;
  }
  shown.forEach(function(r){
    var n=r.gtm_readiness_score||0,c=sc(n),s=r.socials||{},g=r.gtm_signals||{},ff=Array.isArray(r.founders)?r.founders:[],id=r._id,site=su(r.website);
    var card=document.createElement('div');card.className='lead-card';
    var statusColors={'not_contacted':'var(--tx3)','contacted':'var(--amb)','in_talks':'var(--pip)','closed':'var(--grn)'};
    var statusLabels={'not_contacted':'Not Contacted','contacted':'Contacted','in_talks':'In Talks','closed':'Closed ✓'};
    var curStatus=r.outreach_status||'not_contacted';
    var remoteBadge=r.hiring_remote?'<span class="hiring-badge">hiring remotely</span>':'';
    var inv=[r.lead_investor,r.other_investors].filter(function(v){return v&&v!=='null';}).join(', ');

    // Signals
    var sigsHtml='';
    [['recently_funded','Recently funded'],['no_cmo','No CMO'],['pre_launch_or_early','Pre-launch'],['has_product','Has product'],['small_team','Small team'],['marketing_gap_visible','Marketing gap'],['active_community','Active community']].forEach(function(x){
      var v=g[x[0]],cls=v===true?'sy':v===false?'sn':'su',t=v===true?'Yes':v===false?'No':'?';
      sigsHtml+='<div class="sig-row"><span style="color:var(--tx2);font-size:12px">'+x[1]+'</span><span class="'+cls+'">'+t+'</span></div>';
    });

    // Founders
    var fndHtml='';
    if(ff.length){ff.forEach(function(f){var ini=String(f.name||'?').split(' ').map(function(w){return w[0]||'';}).slice(0,2).join('').toUpperCase();fndHtml+='<div class="founder-row"><div class="fav">'+ini+'</div><div><div class="fname">'+(f.name||'')+'</div><div class="frole">'+(f.role||'')+(f.background?' · '+f.background:'')+'</div></div></div>';});}
    else fndHtml='<div class="lc-text dim">Unknown</div>';

    // Social links
    var tw=s.twitter?'https://twitter.com/'+String(s.twitter).replace('@',''):'';
    var socHtml='<div class="social-links">';
    [[tw,'Twitter'],[s.linkedin,'LinkedIn'],[s.discord,'Discord'],[s.telegram,'Telegram'],[s.github,'GitHub']].forEach(function(x){var u=su(x[0]);if(u)socHtml+='<a href="'+u+'" target="_blank">'+x[1]+'</a>';});
    socHtml+='</div>';

    card.innerHTML=
      '<div class="lead-card-header">'+
        '<div class="lead-card-top">'+
          '<div><div class="lead-card-name">'+(r.company||'')+(site?'&nbsp;<a href="'+site+'" target="_blank" style="font-size:10px;color:var(--pip);border:1px solid var(--pip-bor);padding:1px 7px;border-radius:999px;text-decoration:none;font-weight:700">visit</a>':'')+'</div>'+
          '<div class="lead-card-meta" style="margin-top:4px">'+remoteBadge+'<span class="lead-card-sector">'+(r.sector||'')+(r.stage?' · '+r.stage:'')+'</span></div></div>'+
          '<div style="text-align:right"><div class="lead-card-score" style="color:'+c+'">'+n+'</div><div class="lead-card-tag" style="color:'+c+';border-color:'+c+';font-size:9px;padding:2px 8px;border-radius:999px;border:1px solid;display:inline-block;margin-top:4px">'+(r.gtm_label||'')+'</div></div>'+
        '</div>'+
      '</div>'+
      '<div class="lead-card-body">'+
        '<div class="lc-sec">Profile</div>'+
        '<div class="lc-grid">'+
          '<div class="lc-cell"><div class="lc-key">HQ</div><div class="lc-val'+(r.hq?'':' dim')+'">'+(r.hq||'—')+'</div></div>'+
          '<div class="lc-cell"><div class="lc-key">Founded</div><div class="lc-val'+(r.founded?'':' dim')+'">'+(r.founded||'—')+'</div></div>'+
          '<div class="lc-cell"><div class="lc-key">Team</div><div class="lc-val'+(r.employee_count?'':' dim')+'">'+(r.employee_count||'—')+'</div></div>'+
          '<div class="lc-cell"><div class="lc-key">Funding</div><div class="lc-val'+(r.funding_amount?'':' dim')+'">'+(r.funding_amount||'—')+'</div></div>'+
        '</div>'+
        (inv?'<div class="lc-sec">Investors</div><div class="lc-text">'+inv+'</div>':'') +
        '<div class="lc-sec">Socials</div>'+socHtml+
        '<div class="lc-sec">Founders</div>'+fndHtml+
        '<div class="lc-sec">GTM Signals</div><div>'+sigsHtml+'</div>'+
        '<div class="lc-sec">Why They Fit</div><div class="lc-text">'+(r.why_fit||'—')+'</div>'+
        '<div class="lc-sec">Reach Out To</div><div class="lc-text" style="color:var(--pip)">'+
          (r.best_contact_name&&r.best_contact_title?r.best_contact_name+' — '+r.best_contact_title:r.best_contact_title||r.decision_maker||'—')+
        '</div>'+
        '<div class="pitch-box"><div class="pitch-label">Pitch Opener</div><div class="pitch-text" id="pt'+id+'">'+(r.pitch_opener||'—')+'</div></div>'+
        '<div class="lc-sec" style="margin-top:12px">Notes</div>'+
        '<textarea class="notes-area" id="note'+id+'" placeholder="Add notes...">'+(r._notes||'')+'</textarea>'+
      '</div>'+
      '<div class="lead-card-actions" id="act'+id+'"></div>';

    // Wire notes
    card.querySelector('.notes-area').addEventListener('input', function(e){
      r._notes=e.target.value;
      clearTimeout(r._nt);
      r._nt=setTimeout(function(){save();},800);
    });

    // Build action buttons
    var acts=card.querySelector('.lead-card-actions');

    var cpBtn=document.createElement('button');cpBtn.className='abtn g';cpBtn.textContent='Copy Pitch';
    (function(cid){cpBtn.onclick=function(){var el=document.getElementById('pt'+cid);if(el)navigator.clipboard.writeText(el.textContent);cpBtn.textContent='Copied!';setTimeout(function(){cpBtn.textContent='Copy Pitch';},1800);};})(id);
    acts.appendChild(cpBtn);

    // LinkedIn search
    var liQ=encodeURIComponent(((r.best_contact_name||'')+' '+(r.best_contact_title||r.decision_maker||'')+' '+(r.company||'')).trim());
    var liBtn=document.createElement('button');liBtn.className='abtn';liBtn.textContent='Find on LinkedIn';
    liBtn.onclick=function(){window.open('https://www.linkedin.com/search/results/people/?keywords='+liQ,'_blank');};
    acts.appendChild(liBtn);

    // Status button
    var stBtn=document.createElement('button');stBtn.className='abtn';
    stBtn.textContent=statusLabels[curStatus]||'Not Contacted';
    stBtn.style.color=statusColors[curStatus]||'var(--tx3)';
    stBtn.style.borderColor=statusColors[curStatus]||'var(--bor2)';
    (function(rec){stBtn.onclick=function(){
      var order=['not_contacted','contacted','in_talks','closed'];
      var cur=rec.outreach_status||'not_contacted';
      rec.outreach_status=order[(order.indexOf(cur)+1)%order.length];
      save();renderLeads();
    };})(r);
    acts.appendChild(stBtn);

    // Follow-up date
    var fuWrap=document.createElement('div');fuWrap.style.cssText='display:flex;align-items:center;gap:5px';
    var fuLabel=document.createElement('span');fuLabel.style.cssText='font-size:10px;color:var(--tx3)';fuLabel.textContent='Follow-up:';
    var fuInput=document.createElement('input');fuInput.type='date';
    fuInput.style.cssText='background:var(--bg);border:1px solid var(--bor2);color:var(--tx2);font-family:Nunito,sans-serif;font-size:11px;padding:4px 8px;outline:none;border-radius:6px';
    fuInput.value=r._followup||'';
    (function(rec){fuInput.onchange=function(){rec._followup=fuInput.value;save();};})(r);
    fuWrap.appendChild(fuLabel);fuWrap.appendChild(fuInput);acts.appendChild(fuWrap);

    // Re-research
    var rrBtn=document.createElement('button');rrBtn.className='abtn';rrBtn.textContent='↺ Re-research';
    (function(rec){rrBtn.onclick=function(){
      rrBtn.textContent='Researching...';rrBtn.disabled=true;
      fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:'',company:rec.company,system:SYS})})
      .then(function(r){return r.json();}).then(function(d){
        if(d.error)throw new Error(d.error);
        var t=(d.text||'').replace(/```json/g,'').replace(/```/g,'').trim();
        var a=t.indexOf('{'),b=t.lastIndexOf('}');
        var fresh=JSON.parse(t.slice(a,b+1));
        fresh._id=rec._id;fresh._open=true;fresh._notes=rec._notes;fresh._followup=rec._followup;fresh.outreach_status=rec.outreach_status;
        var idx=DB.findIndex(function(x){return x._id===rec._id;});
        if(idx>=0)DB[idx]=fresh;
        save();renderLeads();
      }).catch(function(e){rrBtn.textContent='↺ Re-research';rrBtn.disabled=false;});
    };})(r);
    acts.appendChild(rrBtn);

    // Remove
    var rmBtn=document.createElement('button');rmBtn.className='abtn ghost';rmBtn.textContent='Remove';
    (function(cid){rmBtn.onclick=function(){if(confirm('Remove this lead?')){DB=DB.filter(function(x){return x._id!==cid;});save();updateBadges();renderLeads();}};})(id);
    acts.appendChild(rmBtn);

    cont.appendChild(card);
  });
}

// ── RENDER: PIPELINE (kanban) ─────────────────────────────────────────────────
function renderPipelinePage(){
  var cont=document.getElementById('pipeline-board');
  if(!cont)return;
  cont.innerHTML='';
  var stages=['not_contacted','contacted','in_talks','closed'];
  var labels={'not_contacted':'Not Contacted','contacted':'Contacted','in_talks':'In Talks','closed':'Closed'};
  var colors={'not_contacted':'var(--tx3)','contacted':'var(--amb)','in_talks':'var(--pip)','closed':'var(--grn)'};
  var icons={'not_contacted':'○','contacted':'◎','in_talks':'◉','closed':'●'};
  stages.forEach(function(stage){
    var col=document.createElement('div');col.className='pipeline-col';
    var items=DB.filter(function(r){return(r.outreach_status||'not_contacted')===stage;});
    var hdr=document.createElement('div');hdr.className='pipeline-col-header';
    hdr.innerHTML='<span style="color:'+colors[stage]+'">'+icons[stage]+' '+labels[stage]+'</span>'+
      '<span style="background:var(--bor2);color:var(--tx3);font-size:10px;padding:2px 8px;border-radius:999px">'+items.length+'</span>';
    col.appendChild(hdr);
    if(!items.length){
      var empty=document.createElement('div');empty.className='pipeline-empty';empty.textContent='No leads';col.appendChild(empty);
    }
    items.forEach(function(r){
      var score=r.gtm_readiness_score||0,c=sc(score);
      var item=document.createElement('div');item.className='pipeline-card';
      item.innerHTML=
        '<div style="display:flex;justify-content:space-between;align-items:flex-start">'+
          '<div class="pipeline-card-name">'+(r.company||'')+'</div>'+
          '<span style="font-size:14px;font-weight:800;color:'+c+'">'+score+'</span>'+
        '</div>'+
        '<div class="pipeline-card-meta">'+(r.sector||'')+(r.stage?' · '+r.stage:'')+'</div>'+
        (r._followup?'<div class="pipeline-card-date">📅 '+r._followup+'</div>':'')+
        (r._notes?'<div class="pipeline-card-note">'+(r._notes.slice(0,80))+(r._notes.length>80?'...':'')+'</div>':'')+
        '<div style="margin-top:8px;font-size:11px;color:var(--pip)">'+(r.best_contact_title||r.decision_maker||'')+'</div>';
      (function(rec){item.onclick=function(){
        var order=['not_contacted','contacted','in_talks','closed'];
        var cur=rec.outreach_status||'not_contacted';
        rec.outreach_status=order[(order.indexOf(cur)+1)%order.length];
        save();renderPipelinePage();
      };})(r);
      col.appendChild(item);
    });
    cont.appendChild(col);
  });
}

// ── RENDER: INBOX ─────────────────────────────────────────────────────────────
function renderInbox(){
  var cont=document.getElementById('inbox-grid');
  if(!cont)return;
  cont.innerHTML='';
  updateBadges();
  if(!INBOX.length){
    cont.innerHTML='<div class="inbox-empty" style="grid-column:1/-1"><div class="inbox-empty-title">Inbox is empty</div><p style="color:var(--tx3);font-size:13px">Fetch leads from the Search page and they will appear here for review.</p></div>';
    return;
  }
  // Event delegation for approve/dismiss
  cont.addEventListener('click',function(e){
    var a=e.target.closest('.btn-approve');
    var d=e.target.closest('.btn-dismiss');
    if(a)approveInboxCard(a.getAttribute('data-id'));
    if(d)dismissInboxCard(d.getAttribute('data-id'));
  });
  INBOX.forEach(function(r){
    var n=r.gtm_readiness_score||0,c=sc(n),id=r._id;
    var inv=[r.lead_investor,r.other_investors].filter(function(v){return v&&v!=='null';}).join(', ');
    var card=document.createElement('div');card.className='inbox-card';
    var whyFit=r.why_fit?'<div style="margin-bottom:8px;font-size:12px;color:var(--tx2)">'+r.why_fit+'</div>':'';
    var pitch=r.pitch_opener?'<div style="font-size:11px;color:var(--pip-light);font-style:italic;padding:10px;background:var(--pip-dim);border-radius:8px;border:1px solid var(--pip-bor)">'+r.pitch_opener+'</div>':'';
    var contact=(r.best_contact_title||r.decision_maker)?'<div style="margin-top:8px;font-size:11px;color:var(--pip)">Contact: '+(r.best_contact_name?r.best_contact_name+' - ':''+(r.best_contact_title||r.decision_maker||''))+'</div>':'';
    var investors=inv?'<div style="margin-top:6px;font-size:11px;color:var(--tx3)">Investors: '+inv+'</div>':'';
    card.innerHTML=
      '<div class="inbox-card-header">'+
        '<div style="display:flex;justify-content:space-between;align-items:flex-start">'+
          '<div>'+
            '<div class="inbox-card-name">'+(r.company||'')+'</div>'+
            '<div class="inbox-card-meta">'+(r.sector||'')+(r.stage?' - '+r.stage:'')+(r.hq?' - '+r.hq:'')+'</div>'+
          '</div>'+
          '<div style="text-align:right">'+
            '<div style="font-size:20px;font-weight:800;color:'+c+'">'+n+'</div>'+
            '<div style="font-size:9px;font-weight:700;color:'+c+';border:1px solid '+c+';padding:2px 8px;border-radius:999px;display:inline-block;margin-top:3px">'+(r.gtm_label||'')+'</div>'+
          '</div>'+
        '</div>'+
      '</div>'+
      '<div class="inbox-card-body">'+whyFit+pitch+contact+investors+'</div>'+
      '<div class="inbox-card-actions">'+
        '<button class="btn-approve" data-id="'+id+'">Save to Pipeline</button>'+
        '<button class="btn-dismiss" data-id="'+id+'">Dismiss</button>'+
      '</div>';
    cont.appendChild(card);
  });
}

// ── PIP HUNT ─────────────────────────────────────────────────────────────────
var PH_JOBS = [];
var PH_SAVED = [];
var phCategory = 'cmo';
var phFilters = {remote: false, startup: false, week: false};

var PH_SYS_CMO = "You are a job search assistant. Search the web for currently open job postings for CMO, VP Marketing, Head of Marketing, VP Growth, Head of Growth, Director of Marketing roles at tech and AI startups. Focus on companies that are Series A, Series B, or recently funded. For each job found return a JSON array. Each item must have: {role, company, location, remote (bool), salary (string or null), posted (string - how long ago), apply_method (one of: 'link', 'email', 'linkedin'), apply_url (direct URL or email address), description (2 sentences max about the role), sector}. Return max 15 results. Only real current openings.";

var PH_SYS_DESIGN = "You are a job search assistant. Search the web for currently open job postings for Head of Design, VP Design, Creative Director, Brand Director, Director of Brand, Head of Brand roles at tech and AI startups. Focus on companies that are Series A, Series B, or recently funded. For each job found return a JSON array. Each item must have: {role, company, location, remote (bool), salary (string or null), posted (string - how long ago), apply_method (one of: 'link', 'email', 'linkedin'), apply_url (direct URL or email address), description (2 sentences max about the role), sector}. Return max 15 results. Only real current openings.";

function phSetCategory(cat){
  phCategory = cat;
  document.querySelectorAll('.ph-tab').forEach(function(t){
    t.classList.toggle('active', t.getAttribute('data-cat')===cat);
  });
  phRenderJobs();
}

function phToggleFilter(f){
  phFilters[f] = !phFilters[f];
  document.querySelector('[data-filter="'+f+'"]').classList.toggle('on', phFilters[f]);
  phRenderJobs();
}

function phFetch(){
  var btn = document.getElementById('ph-fetch-btn');
  var status = document.getElementById('ph-status');
  btn.disabled = true;
  status.textContent = 'Searching job boards...';
  var sys = phCategory === 'cmo' ? PH_SYS_CMO : PH_SYS_DESIGN;
  var query = phCategory === 'cmo'
    ? 'Search job boards (LinkedIn, Greenhouse, Lever, AngelList, Wellfound, Indeed) for open CMO VP Marketing Head of Marketing roles at funded tech AI startups right now.'
    : 'Search job boards (LinkedIn, Greenhouse, Lever, AngelList, Wellfound, Indeed) for open Head of Design VP Design Creative Director Brand Director roles at funded tech AI startups right now.';
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({key:'',company:query,system:sys,mode:'fetch'})})
  .then(function(r){return r.json();})
  .then(function(d){
    if(d.error) throw new Error(d.error);
    var t=(d.text||'').replace(/```json/g,'').replace(/```/g,'').trim();
    var a=t.indexOf('['),b=t.lastIndexOf(']');
    if(a<0||b<0) throw new Error('No results found');
    var jobs=JSON.parse(t.slice(a,b+1));
    // Filter out bad results
    var bad=['error','unable','insufficient','no results','no jobs'];
    jobs=jobs.filter(function(j){
      if(!j.company||!j.role) return false;
      var lower=(j.company+j.role).toLowerCase();
      return !bad.some(function(w){return lower.indexOf(w)>=0;});
    });
    // Tag with category and id
    jobs.forEach(function(j){
      j._id='ph'+Date.now()+Math.floor(Math.random()*9999);
      j._cat=phCategory;
    });
    // Add to top, remove dupes by company+role
    jobs.forEach(function(j){
      var exists=PH_JOBS.some(function(x){
        return x.company===j.company&&x.role===j.role;
      });
      if(!exists) PH_JOBS.unshift(j);
    });
    phSave();
    phRenderJobs();
    status.textContent=jobs.length+' jobs found';
    setTimeout(function(){status.textContent='';},4000);
  })
  .catch(function(e){
    status.textContent='Error: '+e.message;
    setTimeout(function(){status.textContent='';},5000);
  })
  .finally(function(){btn.disabled=false;});
}

function phSave(){
  var all = DB.concat(INBOX).concat([{_ph_jobs:PH_JOBS,_ph_saved:PH_SAVED}]);
  // Save PH data separately in gist as second file - for now just use localStorage fallback
  try{localStorage.setItem('ph_jobs',JSON.stringify(PH_JOBS));}catch(e){}
  try{localStorage.setItem('ph_saved',JSON.stringify(PH_SAVED));}catch(e){}
}

function phLoad(){
  try{var j=localStorage.getItem('ph_jobs');if(j)PH_JOBS=JSON.parse(j);}catch(e){}
  try{var s=localStorage.getItem('ph_saved');if(s)PH_SAVED=JSON.parse(s);}catch(e){}
}

function phSaveJob(id){
  var job=PH_JOBS.find(function(j){return j._id===id;});
  if(!job)return;
  var already=PH_SAVED.some(function(j){return j._id===id;});
  if(!already){PH_SAVED.unshift(job);}
  phSave();
  phRenderJobs();
}

function phRemoveSaved(id){
  PH_SAVED=PH_SAVED.filter(function(j){return j._id!==id;});
  phSave();
  phRenderJobs();
}

function phResearchInScout(company){
  setPage('search');
  var ci=document.getElementById('ci');
  if(ci){ci.value=company;ci.focus();}
}

function phCopyApply(val){
  navigator.clipboard.writeText(val);
}

function phRenderJobs(){
  var cont=document.getElementById('ph-jobs-grid');
  if(!cont)return;
  cont.innerHTML='';
  var jobs=PH_JOBS.filter(function(j){return j._cat===phCategory;});
  if(phFilters.remote) jobs=jobs.filter(function(j){return j.remote;});
  if(phFilters.startup) jobs=jobs.filter(function(j){
    var s=(j.sector||'').toLowerCase();
    return s.indexOf('ai')>=0||s.indexOf('tech')>=0||s.indexOf('saas')>=0||s.indexOf('fintech')>=0;
  });
  if(phFilters.week) jobs=jobs.filter(function(j){
    var p=(j.posted||'').toLowerCase();
    return p.indexOf('day')>=0||p.indexOf('hour')>=0||p.indexOf('today')>=0||p.indexOf('1 week')>=0;
  });

  if(!jobs.length){
    cont.innerHTML='<div class="ph-empty" style="grid-column:1/-1"><div class="ph-empty-title">No jobs yet</div><p>Click "Search Jobs" to find open '+(phCategory==='cmo'?'marketing leadership':'design leadership')+' roles.</p></div>';
    return;
  }

  jobs.forEach(function(job){
    var id=job._id;
    var isSaved=PH_SAVED.some(function(j){return j._id===id;});
    var card=document.createElement('div');
    card.className='ph-card'+(isSaved?' saved':'');

    var applyHtml='';
    if(job.apply_url){
      var isEmail=job.apply_method==='email'||job.apply_url.indexOf('@')>=0;
      var isLinkedIn=job.apply_method==='linkedin'||(job.apply_url||'').indexOf('linkedin')>=0;
      var methodLabel=isEmail?'Email':isLinkedIn?'LinkedIn':'Apply';
      var displayUrl=isEmail?job.apply_url:(job.apply_url.replace(/^https?:\/\//,'').slice(0,50)+(job.apply_url.length>55?'...':''));
      applyHtml='<div class="ph-apply">'+
        '<span class="ph-apply-method">'+methodLabel+'</span>'+
        (isEmail
          ? '<span class="ph-apply-link">'+job.apply_url+'</span>'
          : '<a class="ph-apply-link" href="'+job.apply_url+'" target="_blank">'+displayUrl+'</a>')+
        '</div>';
    }

    card.innerHTML=
      '<div class="ph-card-header">'+
        '<div class="ph-card-role">'+(job.role||'')+'</div>'+
        '<div class="ph-card-company">'+(job.company||'')+'</div>'+
        '<div class="ph-card-meta">'+
          (job.location?'<span class="ph-tag">'+(job.location)+'</span>':'')+
          (job.remote?'<span class="ph-tag remote">Remote</span>':'')+
          (job.salary?'<span class="ph-tag salary">'+(job.salary)+'</span>':'')+
          (job.posted?'<span class="ph-tag new">'+(job.posted)+'</span>':'')+
        '</div>'+
      '</div>'+
      '<div class="ph-card-body">'+
        (job.description?'<div class="ph-desc">'+(job.description)+'</div>':'')+
        applyHtml+
      '</div>'+
      '<div class="ph-card-actions" id="pha-'+id+'"></div>';

    // Wire action buttons
    var acts=card.querySelector('.ph-card-actions');

    // Apply / Copy button
    if(job.apply_url){
      var applyBtn=document.createElement('button');
      applyBtn.className='abtn g';
      var isEmail=job.apply_method==='email'||job.apply_url.indexOf('@')>=0;
      applyBtn.textContent=isEmail?'Copy Email':'Open Application';
      (function(url,isEm){
        applyBtn.onclick=function(){
          if(isEm){navigator.clipboard.writeText(url);applyBtn.textContent='Copied!';setTimeout(function(){applyBtn.textContent='Copy Email';},1800);}
          else{window.open(url,'_blank');}
        };
      })(job.apply_url, isEmail);
      acts.appendChild(applyBtn);
    }

    // Save / unsave
    var saveBtn=document.createElement('button');
    saveBtn.className='abtn'+(isSaved?' g':'');
    saveBtn.textContent=isSaved?'Saved ✓':'Save';
    (function(jid,saved){
      saveBtn.onclick=function(){
        if(saved){phRemoveSaved(jid);}
        else{phSaveJob(jid);}
      };
    })(id, isSaved);
    acts.appendChild(saveBtn);

    // Research company in Scout
    var rBtn=document.createElement('button');rBtn.className='abtn';
    rBtn.textContent='Research in Scout';
    (function(co){rBtn.onclick=function(){phResearchInScout(co);};})(job.company);
    acts.appendChild(rBtn);

    // Remove from list
    var rmBtn=document.createElement('button');rmBtn.className='abtn ghost';
    rmBtn.textContent='Remove';
    (function(jid){rmBtn.onclick=function(){
      PH_JOBS=PH_JOBS.filter(function(j){return j._id!==jid;});
      phSave();phRenderJobs();
    };})(id);
    acts.appendChild(rmBtn);

    cont.appendChild(card);
  });

  // Render saved section
  var savedCont=document.getElementById('ph-saved-grid');
  if(!savedCont)return;
  savedCont.innerHTML='';
  var savedJobs=PH_SAVED.filter(function(j){return j._cat===phCategory;});
  if(!savedJobs.length){
    document.getElementById('ph-saved-section').style.display='none';
    return;
  }
  document.getElementById('ph-saved-section').style.display='block';
  savedJobs.forEach(function(job){
    var id=job._id;
    var mini=document.createElement('div');mini.className='ph-card saved';
    mini.innerHTML=
      '<div class="ph-card-header">'+
        '<div class="ph-card-role">'+(job.role||'')+'</div>'+
        '<div class="ph-card-company">'+(job.company||'')+'</div>'+
        '<div class="ph-card-meta">'+
          (job.remote?'<span class="ph-tag remote">Remote</span>':'')+
          (job.salary?'<span class="ph-tag salary">'+(job.salary)+'</span>':'')+
        '</div>'+
      '</div>'+
      '<div class="ph-card-actions"></div>';
    var acts=mini.querySelector('.ph-card-actions');
    if(job.apply_url){
      var isEmail=job.apply_method==='email'||job.apply_url.indexOf('@')>=0;
      var ab=document.createElement('button');ab.className='abtn g';
      ab.textContent=isEmail?'Copy Email':'Open Application';
      (function(url,isEm){ab.onclick=function(){
        if(isEm){navigator.clipboard.writeText(url);ab.textContent='Copied!';setTimeout(function(){ab.textContent='Copy Email';},1800);}
        else window.open(url,'_blank');
      };})(job.apply_url,isEmail);
      acts.appendChild(ab);
    }
    var unBtn=document.createElement('button');unBtn.className='abtn ghost';unBtn.textContent='Remove';
    (function(jid){unBtn.onclick=function(){phRemoveSaved(jid);phRenderJobs();};})(id);
    acts.appendChild(unBtn);
    savedCont.appendChild(mini);
  });
}
// ── DOM READY ─────────────────────────────────────────────────────────────────
function openFetchModal(){
  document.getElementById('fetch-modal').classList.add('open');
  document.getElementById('fetch-results').style.display='none';
  document.getElementById('fetch-err').style.display='none';
}
function closeFetchModal(){
  document.getElementById('fetch-modal').classList.remove('open');
}

document.addEventListener('DOMContentLoaded',function(){
  load();

  // Nav tabs
  document.getElementById('tab-search').onclick=function(){setPage('search');};
  document.getElementById('tab-leads').onclick=function(){setPage('leads');};
  document.getElementById('tab-pipeline').onclick=function(){setPage('pipeline');};
  document.getElementById('tab-inbox').onclick=function(){setPage('inbox');};
  document.getElementById('tab-piphunt').onclick=function(){setPage('piphunt');};

  // Search page
  document.getElementById('rb').onclick=go;
  document.getElementById('ci').addEventListener('keydown',function(e){if(e.key==='Enter')go();});
  document.getElementById('btog').onclick=function(){showPanel('bpanel');};
  document.getElementById('itog').onclick=function(){showPanel('ipanel');};
  document.getElementById('brb').onclick=bulk;
  document.getElementById('iib').onclick=importJSON;

  // Fetch
  document.getElementById('fetch-btn').onclick=fetchLeads;
  document.getElementById('res-sel-btn').onclick=researchSelected;
  document.querySelectorAll('.src-pill').forEach(function(p){
    p.onclick=function(){
      var s=p.getAttribute('data-src');
      var i=activeSources.indexOf(s);
      if(i>=0){activeSources.splice(i,1);p.classList.remove('on');}
      else{activeSources.push(s);p.classList.add('on');}
    };
  });

  // Leads toolbar
  document.querySelectorAll('.fb').forEach(function(b){
    b.onclick=function(){
      fil=b.getAttribute('data-f');
      document.querySelectorAll('.fb').forEach(function(x){x.classList.remove('on');});
      b.classList.add('on');
      renderLeads();
    };
  });

  // CSV export
  document.getElementById('csvbtn').onclick=function(){
    var h=['Company','Sector','Stage','Funding','HQ','Score','Label','Status','Why Fit','Pitch','Contact'];
    var rows=DB.map(function(r){
      function e(v){var s=String(v==null?'':v).replace(/"/g,'""');return s.indexOf(',')>=0?'"'+s+'"':s;}
      return[r.company,r.sector,r.stage,r.funding_amount,r.hq,r.gtm_readiness_score,r.gtm_label,r.outreach_status,r.why_fit,r.pitch_opener,r.best_contact_title||r.decision_maker].map(e).join(',');
    });
    var csv=[h.join(',')].concat(rows).join(String.fromCharCode(10));var blob=new Blob([csv],{type:'text/csv'});
    var a=document.createElement('a');
    a.href=URL.createObjectURL(blob);
    a.download='scout-leads.csv';
    a.click();
  };

  document.getElementById('clrbtn').onclick=function(){
    if(confirm('Clear all saved leads?')){DB=[];save();updateBadges();renderLeads();}
  };
});

"""

HTML = ("<!DOCTYPE html>\n<html>\n<head>\n"
  "<meta charset='UTF-8'>\n"
  "<meta name='viewport' content='width=device-width,initial-scale=1'>\n"
  "<title>Scout</title>\n"
  "<link href='https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800&display=swap' rel='stylesheet'>\n"
  "<link rel='icon' type='image/png' href='data:image/png;base64,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'>\n"
  "<style>" + CSS + "</style>\n"
  "</head>\n<body>\n"

  "<div class='topbar'>"
    "<div class='topbar-brand'>"
      "<div class='logo-mark'><img src='data:image/png;base64,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' style='width:32px;height:32px;object-fit:contain'></div>"
      "<span class='logo-text'>Scout</span>"
    "</div>"
    "<nav class='nav'>"
      "<button class='nav-tab active' id='tab-search'>Search</button>"
      "<button class='nav-tab' id='tab-leads'>Saved Leads <span class='badge' id='leads-badge'>0</span></button>"
      "<button class='nav-tab' id='tab-pipeline'>Pipeline</button>"
      "<button class='nav-tab' id='tab-inbox'>Inbox <span class='badge amber' id='inbox-badge' style='display:none'>0</span></button>"
      "<button class='nav-tab' id='tab-piphunt'>🐾 Pip Hunt</button>"
    "</nav>"
    "<div class='topbar-right'><span class='save-ind' id='save-ind'></span></div>"
  "</div>\n"

  "<div class='page active' id='page-search'>"
    "<div class='search-hero'>"
      "<h1>Find your next client</h1>"
      "<p>Research any company or fetch recently funded startups looking for marketing leadership.</p>"
    "</div>"
    "<div class='search-box'>"
      "<input id='ci' type='text' placeholder='Company name, e.g. Privy, Alchemy, Listen Labs...'>"
      "<button id='rb'>Research →</button>"
      "<button id='fetch-modal-btn' onclick='openFetchModal()' style='background:none;border:1px solid var(--pip-bor);color:var(--pip);font-weight:700;font-size:12px;padding:12px 16px;cursor:pointer;white-space:nowrap;font-family:Nunito,sans-serif;border-radius:var(--r);transition:all .2s'>⚡ Fetch Leads</button>"
    "</div>"
    "<div id='ldg'><div class='spinner'></div><span>Researching <b id='lname'></b>... <span id='ltimer'>0s</span></span></div>"
    "<div id='err'></div>"
    "<div class='search-actions'>"
      "<button class='tlink' id='btog'>+ Bulk</button>"
      "<button class='tlink blu' id='itog'>+ Import JSON</button>"
    "</div>"
    "<div class='panel-extra' id='bpanel'>"
      "<div class='panel-label'>One company per line</div>"
      "<textarea id='bi' placeholder='Privy&#10;Alchemy&#10;EigenLayer'></textarea>"
      "<button class='sub-btn' id='brb'>Research All →</button>"
    "</div>"
    "<div class='panel-extra' id='ipanel'>"
      "<div class='panel-label'>Paste JSON array</div>"
      "<textarea id='ii' placeholder='[{&quot;company&quot;:&quot;Privy&quot;,...}]'></textarea>"
      "<div id='ierr'></div>"
      "<button class='sub-btn' id='iib'>Import</button>"
    "</div>"

          "<div class='src-pills'>"
        "<div class='src-pill on' data-src='techcrunch'>TechCrunch</div>"
        "<div class='src-pill on' data-src='blockworks'>Blockworks</div>"
        "<div class='src-pill on' data-src='theblock'>The Block</div>"
        "<div class='src-pill' data-src='cryptofunding'>crypto-fundraising.info</div>"
        "<div class='src-pill on' data-src='producthunt'>ProductHunt</div>"
        "<div class='src-pill on' data-src='linkedinjobs'>LinkedIn Jobs</div>"
      "</div>"
      "<div id='fetch-ldg'><div class='spinner'></div><span>Searching funding news...</span></div>"
      "<div id='fetch-err'></div>"
      "<div id='fetch-results'>"
        "<div style='font-size:11px;color:var(--tx3);margin-bottom:10px'>Select companies to research → they go to your Inbox:</div>"
        "<div class='fetch-list' id='fetch-list'></div>"
        "<div style='display:flex;align-items:center'>"
          "<button id='res-sel-btn'>Research Selected →</button>"
          "<span id='fetch-count'></span>"
        "</div>"
      "</div>"
    "</div>"
  "</div>\n"

  "<div class='page' id='page-leads'>"
    "<div class='leads-header'>"
      "<h2>Saved Leads</h2>"
      "<div class='tb-right'>"
        "<button class='tb-btn' id='csvbtn'>↓ Export CSV</button>"
        "<button class='tb-btn danger' id='clrbtn'>Clear All</button>"
      "</div>"
    "</div>"
    "<div class='leads-toolbar'>"
      "<button class='fb on' data-f='all'>All</button>"
      "<button class='fb' data-f='hot'>🔥 Hot</button>"
      "<button class='fb' data-f='warm'>⚡ Warm</button>"
      "<button class='fb' data-f='cold'>🧊 Cold</button>"
    "</div>"
    "<div class='cards-grid' id='leads-grid'></div>"
  "</div>\n"

  "<div class='page' id='page-pipeline'>"
    "<div class='pipeline-header'>"
      "<h2>Pipeline</h2>"
      "<span style='font-size:12px;color:var(--tx3)'>Click any card to advance to next stage</span>"
    "</div>"
    "<div class='pipeline-board' id='pipeline-board'></div>"
  "</div>\n"

  "<div class='page' id='page-inbox'>"
    "<div class='inbox-header'>"
      "<h2>Inbox</h2>"
      "<span style='font-size:12px;color:var(--tx3)'>Review fetched leads — save to Pipeline or dismiss</span>"
    "</div>"
    "<div class='inbox-grid' id='inbox-grid'></div>"
  "</div>\n"

  "<div class='page' id='page-piphunt'>"
    "<div class='ph-header'><h2>🐾 Pip Hunt</h2><span style='font-size:13px;color:var(--tx3)'>Find companies actively hiring marketing & design leadership</span></div>"
    "<div class='ph-tabs'>"
      "<button class='ph-tab active' data-cat='cmo' onclick='phSetCategory(\"cmo\")'>CMO & Marketing</button>"
      "<button class='ph-tab' data-cat='design' onclick='phSetCategory(\"design\")'>Design & Creative</button>"
    "</div>"
    "<div class='ph-controls'>"
      "<button class='ph-filter' data-filter='remote' onclick='phToggleFilter(\"remote\")'>Remote only</button>"
      "<button class='ph-filter' data-filter='startup' onclick='phToggleFilter(\"startup\")'>AI / Tech</button>"
      "<button class='ph-filter' data-filter='week' onclick='phToggleFilter(\"week\")'>This week</button>"
      "<button class='ph-fetch-btn' id='ph-fetch-btn' onclick='phFetch()'>🔍 Search Jobs</button>"
      "<span class='ph-status' id='ph-status'></span>"
    "</div>"
    "<div class='ph-grid' id='ph-jobs-grid'></div>"
    "<div id='ph-saved-section' style='display:none'>"
      "<div class='ph-saved-list'><h3>Saved Jobs</h3></div>"
      "<div class='ph-grid' id='ph-saved-grid'></div>"
    "</div>"
  "</div>\n"


  "<div class='modal-overlay' id='fetch-modal' onclick='if(event.target===this)closeFetchModal()'>"
    "<div class='modal' style='position:relative'>"
      "<button class='modal-close' onclick='closeFetchModal()'>✕</button>"
      "<div class='modal-title'>⚡ Fetch New Leads</div>"
      "<div class='modal-sub'>Pull recently funded companies — researched and sent to your Inbox</div>"
      "<div class='src-pills' style='margin-bottom:14px'>"
        "<div class='src-pill on' data-src='techcrunch'>TechCrunch</div>"
        "<div class='src-pill on' data-src='blockworks'>Blockworks</div>"
        "<div class='src-pill on' data-src='theblock'>The Block</div>"
        "<div class='src-pill' data-src='cryptofunding'>Crypto Funding</div>"
        "<div class='src-pill on' data-src='producthunt'>ProductHunt</div>"
        "<div class='src-pill on' data-src='linkedinjobs'>LinkedIn Jobs</div>"
      "</div>"
      "<div id='fetch-ldg' style='margin-top:0;padding-top:0;border-top:none'><div class='spinner'></div><span>Searching funding news...</span></div>"
      "<div id='fetch-err'></div>"
      "<div id='fetch-results' style='margin-top:0;padding-top:0;border-top:none'>"
        "<div style='font-size:11px;color:var(--tx3);margin-bottom:8px'>Select to research → sent to Inbox:</div>"
        "<div class='fetch-list' id='fetch-list'></div>"
        "<div style='display:flex;align-items:center;gap:8px;margin-top:8px'>"
          "<button id='res-sel-btn' class='modal-btn primary'>Research Selected →</button>"
          "<span id='fetch-count' style='font-size:11px;color:var(--tx3)'></span>"
        "</div>"
      "</div>"
      "<div class='modal-footer'>"
        "<button class='modal-btn secondary' onclick='closeFetchModal()'>Cancel</button>"
        "<button class='modal-btn primary' id='fetch-btn'>Search Funding News →</button>"
      "</div>"
    "</div>"
  "</div>\n"

  "<script>" + JS + "</script>\n"
  "</body>\n</html>\n")


PIN_HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scout</title>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#07090f;color:#dde4f0;font-family:'JetBrains Mono',monospace;display:flex;align-items:center;justify-content:center;min-height:100vh}
.box{background:#0e1119;border:1px solid #1d2333;padding:40px;width:320px;text-align:center}
.logo{width:36px;height:36px;background:#00e676;color:#000;font-weight:800;font-size:16px;display:flex;align-items:center;justify-content:center;margin:0 auto 20px}
h2{font-size:16px;font-weight:700;margin-bottom:6px;letter-spacing:-0.02em}
p{font-size:10px;color:#4a5570;margin-bottom:24px;text-transform:uppercase;letter-spacing:.1em}
.dots{display:flex;gap:12px;justify-content:center;margin-bottom:24px}
.dot{width:14px;height:14px;border-radius:50%;border:2px solid #1d2333;background:transparent;transition:background 0.15s}
.dot.filled{background:#00e676;border-color:#00e676}
.numpad{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:16px}
.key{background:#141824;border:1px solid #1d2333;color:#dde4f0;font-family:'JetBrains Mono',monospace;font-size:16px;font-weight:700;padding:14px;cursor:pointer;transition:background 0.1s}
.key:hover{background:#1d2333}
.key:active{background:#252d3f}
.key.del{color:#4a5570;font-size:12px}
#err{color:#ff5252;font-size:11px;min-height:16px;margin-top:4px}
</style>
</head>
<body>
<div class="box">
  <img src="data:image/png;base64,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" style="width:36px;height:36px;object-fit:contain;display:block;margin:0 auto 20px;">
  <h2>Scout</h2>
  <p>Enter PIN to continue</p>
  <div class="dots" id="dots">
    <div class="dot" id="d0"></div>
    <div class="dot" id="d1"></div>
    <div class="dot" id="d2"></div>
    <div class="dot" id="d3"></div>
  </div>
  <div class="numpad">
    <button class="key" onclick="press(1)">1</button>
    <button class="key" onclick="press(2)">2</button>
    <button class="key" onclick="press(3)">3</button>
    <button class="key" onclick="press(4)">4</button>
    <button class="key" onclick="press(5)">5</button>
    <button class="key" onclick="press(6)">6</button>
    <button class="key" onclick="press(7)">7</button>
    <button class="key" onclick="press(8)">8</button>
    <button class="key" onclick="press(9)">9</button>
    <button class="key" onclick="press(0)" style="grid-column:2">0</button>
    <button class="key del" onclick="del()">⌫</button>
  </div>
  <div id="err"></div>
</div>
<script>
var entered = '';
var correct = '__PIN__';
function press(n) {
  if (entered.length >= 4) return;
  entered += n;
  update();
  if (entered.length === 4) {
    setTimeout(check, 150);
  }
}
function del() {
  entered = entered.slice(0,-1);
  update();
  document.getElementById('err').textContent = '';
}
function update() {
  for (var i=0;i<4;i++) {
    document.getElementById('d'+i).classList.toggle('filled', i < entered.length);
  }
}
function check() {
  if (entered === correct) {
    window.location.href = '/app';
  } else {
    entered = '';
    update();
    document.getElementById('err').textContent = 'Incorrect PIN';
    for(var i=0;i<4;i++) document.getElementById('d'+i).style.borderColor='#ff5252';
    setTimeout(function(){for(var i=0;i<4;i++) document.getElementById('d'+i).style.borderColor='';},800);
  }
}
document.addEventListener('keydown', function(e) {
  if (e.key >= '0' && e.key <= '9') press(parseInt(e.key));
  if (e.key === 'Backspace') del();
});
</script>
</body>
</html>'''

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def do_GET(self):
        if self.path == '/dbtest':
            result = {'gist_id': bool(GIST_ID), 'gist_token': bool(GIST_TOKEN), 'records': 0, 'error': None}
            try:
                req = urllib.request.Request(
                    'https://api.github.com/gists/' + GIST_ID,
                    headers={'Authorization': 'token ' + GIST_TOKEN, 'Accept': 'application/vnd.github.v3+json', 'User-Agent': 'Scout-App'},
                    method='GET'
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    gist_data = json.loads(resp.read())
                    content = gist_data['files']['scout_db.json']['content']
                    data = json.loads(content)
                    result['records'] = len(data) if isinstance(data, list) else -1
                    result['preview'] = 'gist ok'
            except Exception as e:
                result['error'] = str(e)
            out = json.dumps(result).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(out)))
            self.end_headers()
            self.wfile.write(out)
            return
        if self.path == '/db':
            data = json.dumps(load_db()).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        # Serve PIN page if PIN is set
        app_pin = os.environ.get('APP_PIN', '')
        if app_pin and self.path == '/':
            content = PIN_HTML.replace('__PIN__', app_pin).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if self.path not in ('/', '/app', ''):
            self.send_response(404); self.end_headers(); return
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
        mode = body.get('mode', 'research')
        actual_key = os.environ.get('ANTHROPIC_API_KEY', key)

        if not actual_key: self.respond({'error': 'No API key configured'}); return
        if not company: self.respond({'error': 'Missing company name'}); return

        if mode == 'fetch':
            messages = [{'role': 'user', 'content': 'Search the web and complete this task: ' + company}]
            final_text = ''
            for _ in range(10):
                payload = json.dumps({'model': 'claude-sonnet-4-20250514', 'max_tokens': 1500, 'system': system,
                    'tools': [{'type': 'web_search_20250305', 'name': 'web_search'}], 'messages': messages}).encode('utf-8')
                req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=payload,
                    headers={'Content-Type': 'application/json', 'x-api-key': actual_key, 'anthropic-version': '2023-06-01'}, method='POST')
                try:
                    with urllib.request.urlopen(req, timeout=90) as resp:
                        data = json.loads(resp.read())
                except urllib.error.HTTPError as e:
                    self.respond({'error': 'API error ' + str(e.code) + ': ' + e.read().decode()[:300]}); return
                except Exception as e:
                    self.respond({'error': str(e)}); return
                content = data.get('content', [])
                stop_reason = data.get('stop_reason', '')
                for block in content:
                    if block.get('type') == 'text': final_text = block.get('text', '')
                if stop_reason == 'end_turn': break
                elif stop_reason == 'tool_use':
                    messages.append({'role': 'assistant', 'content': content})
                    messages.append({'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': b['id'], 'content': [{'type': 'text', 'text': 'ok'}]} for b in content if b.get('type') == 'tool_use']})
                else: break
            self.respond({'text': final_text})
        else:
            payload = json.dumps({'model': 'claude-sonnet-4-20250514', 'max_tokens': 1200, 'system': system,
                'messages': [{'role': 'user', 'content': 'Research this company and return the JSON profile: "' + company + '"'}]}).encode('utf-8')
            req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=payload,
                headers={'Content-Type': 'application/json', 'x-api-key': actual_key, 'anthropic-version': '2023-06-01'}, method='POST')
            try:
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = json.loads(resp.read())
                text = ''.join(b.get('text','') for b in data.get('content',[]) if b.get('type')=='text')
                self.respond({'text': text})
            except urllib.error.HTTPError as e:
                self.respond({'error': 'API error ' + str(e.code) + ': ' + e.read().decode()[:300]})
            except Exception as e:
                self.respond({'error': str(e)})

    def respond(self, obj):
        data = json.dumps(obj).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def monday_autofetch():
    """Runs every Monday at 8am UTC, auto-fetches leads and saves to DB"""
    import threading, datetime
    def schedule():
        while True:
            now = datetime.datetime.utcnow()
            # Check if it's Monday (weekday 0) and 8am UTC
            if now.weekday() == 0 and now.hour == 8 and now.minute == 0:
                print('  [Auto-fetch] Running Monday morning lead fetch...')
                try:
                    key = os.environ.get('ANTHROPIC_API_KEY','')
                    if not key:
                        time.sleep(60); continue
                    FETCH_SYS = 'You are a funding news analyst. Search the web for startup funding announcements from the last 7 days. Focus on AI, web3, crypto, blockchain, DeFi, fintech. Return ONLY a valid JSON array, no markdown. Each item: {"company":"Name","sector":"AI/Web3/etc","funding":"$XM","stage":"Seed/Series A/etc","source":"publication"}. Max 15 companies. Only include real recent raises.'
                    messages = [{'role':'user','content':'Search TechCrunch, Blockworks, and The Block for startup funding announcements from the last 7 days. Return a JSON array of recently funded companies.'}]
                    final_text = ''
                    for _ in range(10):
                        payload = json.dumps({'model':'claude-sonnet-4-20250514','max_tokens':1500,'system':FETCH_SYS,'tools':[{'type':'web_search_20250305','name':'web_search'}],'messages':messages}).encode('utf-8')
                        req = urllib.request.Request('https://api.anthropic.com/v1/messages',data=payload,headers={'Content-Type':'application/json','x-api-key':key,'anthropic-version':'2023-06-01'},method='POST')
                        with urllib.request.urlopen(req,timeout=90) as resp:
                            data = json.loads(resp.read())
                        content = data.get('content',[])
                        stop_reason = data.get('stop_reason','')
                        for block in content:
                            if block.get('type')=='text': final_text=block.get('text','')
                        if stop_reason=='end_turn': break
                        elif stop_reason=='tool_use':
                            messages.append({'role':'assistant','content':content})
                            messages.append({'role':'user','content':[{'type':'tool_result','tool_use_id':b['id'],'content':[{'type':'text','text':'ok'}]} for b in content if b.get('type')=='tool_use']})
                        else: break
                    # Parse and save companies
                    t = final_text.replace('```json','').replace('```','').strip()
                    a,b2 = t.find('['),t.rfind(']')
                    if a>=0 and b2>=0:
                        companies = json.loads(t[a:b2+1])
                        db = load_db()
                        existing = set(r.get('company','').lower() for r in db)
                        added = 0
                        for co in companies:
                            if co.get('company') and co['company'].lower() not in existing:
                                co['_id'] = 'auto_'+str(int(time.time()))+'_'+co['company'].replace(' ','_')
                                co['_open'] = False
                                co['outreach_status'] = 'not_contacted'
                                co['gtm_label'] = 'Warm Lead'
                                co['gtm_readiness_score'] = 60
                                co['auto_fetched'] = True
                                db.insert(0, co)
                                existing.add(co['company'].lower())
                                added += 1
                        if added:
                            save_db(db)
                            print(f'  [Auto-fetch] Added {added} new companies to DB')
                except Exception as e:
                    print(f'  [Auto-fetch] Error: {e}')
                time.sleep(60)  # sleep 1 min after running to avoid double-trigger
            else:
                time.sleep(30)  # check every 30 seconds
    threading.Thread(target=schedule, daemon=True).start()

if __name__ == '__main__':
    server = http.server.HTTPServer(('0.0.0.0', PORT), Handler)
    monday_autofetch()
    print('\n  Scout running at http://localhost:' + str(PORT))
    print('  Monday auto-fetch: enabled (8am UTC)')
    print('  Press Ctrl+C to stop.\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Stopped.')
        sys.exit(0)
