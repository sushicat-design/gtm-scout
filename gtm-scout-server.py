#!/usr/bin/env python3
#V29
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

/* ── RESET & BASE ── */
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#060810;
  --sur:#0a0d16;
  --sur2:#0f1220;
  --sur3:#141829;
  --bor:rgba(255,255,255,0.06);
  --bor2:rgba(255,255,255,0.1);
  --bor3:rgba(255,255,255,0.15);
  --pip:#3b9eff;
  --pip-dim:rgba(59,158,255,0.07);
  --pip-bor:rgba(59,158,255,0.18);
  --pip-deep:#1a6fd4;
  --pip-light:#7ec8ff;
  --pip-glow:rgba(59,158,255,0.35);
  --amb:#f5a623;
  --amb-dim:rgba(245,166,35,0.08);
  --red:#ff5a5a;
  --grn:#2ecc8a;
  --grn-dim:rgba(46,204,138,0.08);
  --tx:#f0f4ff;
  --tx2:#8b96b0;
  --tx3:#3d4560;
  --r:14px;
  --r-sm:9px;
  --r-pill:999px;
  --shadow-sm:0 1px 3px rgba(0,0,0,0.4);
  --shadow:0 4px 24px rgba(0,0,0,0.5);
  --shadow-lg:0 12px 48px rgba(0,0,0,0.6);
  --glow:0 0 40px rgba(59,158,255,0.12);
}

/* Subtle noise grain texture on bg */
body{
  background:var(--bg);
  color:var(--tx);
  font-family:'Nunito',sans-serif;
  font-size:14px;
  line-height:1.7;
  font-weight:500;
  -webkit-font-smoothing:antialiased;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.025'/%3E%3C/svg%3E");
  min-height:100vh;
}

/* ── TOPBAR ── */
.topbar{
  display:flex;align-items:center;padding:0 24px;height:56px;
  border-bottom:1px solid var(--bor);
  position:sticky;top:0;
  background:rgba(6,8,16,0.88);
  backdrop-filter:blur(24px) saturate(180%);
  -webkit-backdrop-filter:blur(24px) saturate(180%);
  z-index:100;
  gap:12px;
}
.logo-btn{display:flex;align-items:center;gap:9px;background:none;border:none;cursor:pointer;padding:0;font-family:'Nunito',sans-serif;transition:opacity .2s}
.logo-btn:hover{opacity:.8}
.logo-mark{width:30px;height:30px;display:flex;align-items:center;justify-content:center}
.logo-text{font-size:17px;font-weight:900;letter-spacing:-.04em;color:var(--tx);font-family:'Nunito',sans-serif}
.topbar-right{display:flex;align-items:center;gap:10px;margin-left:auto}
.save-ind{font-size:11px;color:var(--tx3);min-width:56px;text-align:right;font-weight:600}

/* Hamburger */
.hamburger{background:none;border:1px solid var(--bor);cursor:pointer;padding:7px 9px;display:flex;flex-direction:column;gap:4px;border-radius:var(--r-sm);transition:all .2s}
.hamburger:hover{border-color:var(--bor2);background:var(--sur2)}
.hamburger span{width:18px;height:1.5px;background:var(--tx2);border-radius:2px;display:block;transition:all .2s}

/* ── SIDEBAR ── */
.sidebar-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:200;backdrop-filter:blur(4px)}
.sidebar-overlay.open{display:block}
.sidebar{
  position:fixed;top:0;right:0;height:100vh;width:276px;
  background:var(--sur);
  border-left:1px solid var(--bor2);
  z-index:201;
  transform:translateX(100%);
  transition:transform .28s cubic-bezier(.4,0,.2,1);
  display:flex;flex-direction:column;
  box-shadow:-24px 0 80px rgba(0,0,0,0.5);
}
.sidebar.open{transform:translateX(0)}
.sidebar-header{display:flex;align-items:center;justify-content:space-between;padding:18px 20px;border-bottom:1px solid var(--bor)}
.sidebar-title{font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.14em;color:var(--tx3)}
.sidebar-close{background:none;border:none;cursor:pointer;color:var(--tx3);font-size:20px;line-height:1;padding:2px 4px;border-radius:6px;transition:all .2s}
.sidebar-close:hover{color:var(--tx);background:var(--sur2)}
.sidebar-nav{display:flex;flex-direction:column;padding:8px 0;flex:1}
.sidebar-item{
  display:flex;align-items:center;gap:13px;
  padding:13px 20px;cursor:pointer;border:none;
  background:none;font-family:'Nunito',sans-serif;
  font-size:13px;font-weight:700;color:var(--tx2);
  text-align:left;transition:all .18s;
  border-left:2px solid transparent;width:100%;
  letter-spacing:-.01em;
}
.sidebar-item:hover{background:var(--sur2);color:var(--tx);border-left-color:var(--bor2)}
.sidebar-item.active{color:var(--pip);border-left-color:var(--pip);background:var(--pip-dim)}
.sidebar-item .si-icon{font-size:16px;width:22px;text-align:center;flex-shrink:0;opacity:.8}
.sidebar-item .si-badge{background:var(--amb);color:#000;font-size:9px;font-weight:800;padding:2px 7px;border-radius:var(--r-pill);margin-left:auto;letter-spacing:.02em}
.sidebar-pip{padding:16px 20px;border-top:1px solid var(--bor);margin-top:auto}
.sidebar-pip-row{display:flex;align-items:center;gap:10px}
.sidebar-pip-name{font-size:13px;font-weight:800;color:var(--tx);letter-spacing:-.02em}
.sidebar-pip-sub{font-size:10px;color:var(--tx3);margin-top:1px}

/* ── PAGES ── */
.page{display:none;padding:36px 28px 80px;max-width:1180px;margin:0 auto;animation:fadeUp .3s ease}
.page.active{display:block}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

/* ── CREDITS BAR ── */
.credits-bar{
  background:linear-gradient(135deg,var(--sur),var(--sur2));
  border:1px solid var(--bor);
  border-radius:var(--r-sm);
  padding:8px 16px;
  display:none;
  align-items:center;
  gap:10px;
  max-width:1180px;
  margin:12px auto 0;
}
.credits-label{font-size:10px;color:var(--tx3);font-weight:700;text-transform:uppercase;letter-spacing:.08em}
.credits-track{flex:1;height:4px;background:var(--bor2);border-radius:2px;overflow:hidden}
.credits-fill{height:100%;background:linear-gradient(90deg,var(--pip),var(--pip-light));border-radius:2px;transition:width .4s ease}
.credits-count{font-size:11px;font-weight:800;color:var(--pip);white-space:nowrap}

/* ── SEARCH PAGE ── */
.search-hero{text-align:center;padding:56px 0 40px;position:relative}
.search-hero::before{
  content:'';position:absolute;top:-60px;left:50%;transform:translateX(-50%);
  width:600px;height:300px;
  background:radial-gradient(ellipse at center,rgba(59,158,255,0.08) 0%,transparent 70%);
  pointer-events:none;
}
.search-hero h1{
  font-size:52px;font-weight:900;letter-spacing:-.05em;
  margin-bottom:14px;line-height:1.05;
  background:linear-gradient(135deg,#f0f4ff 0%,#8bc4ff 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  background-clip:text;
}
.search-hero p{font-size:16px;color:var(--tx2);line-height:1.7;max-width:420px;margin:0 auto}
.search-box{display:flex;gap:8px;max-width:640px;margin:32px auto 0}
#ci{
  flex:1;background:var(--sur);
  border:1px solid var(--bor2);
  color:var(--tx);font-family:'Nunito',sans-serif;
  font-size:15px;font-weight:500;
  padding:14px 20px;outline:none;
  border-radius:var(--r);
  transition:all .2s;
  box-shadow:var(--shadow-sm);
}
#ci:focus{border-color:var(--pip);box-shadow:0 0 0 3px rgba(59,158,255,0.12),var(--shadow)}
#ci::placeholder{color:var(--tx3)}
#rb{
  background:linear-gradient(135deg,var(--pip),var(--pip-deep));
  color:#fff;border:none;font-weight:800;
  font-size:14px;padding:14px 28px;
  cursor:pointer;white-space:nowrap;
  font-family:'Nunito',sans-serif;
  border-radius:var(--r);
  transition:all .2s;
  box-shadow:0 4px 20px rgba(59,158,255,0.25);
  letter-spacing:-.01em;
}
#rb:hover{transform:translateY(-1px);box-shadow:0 8px 30px rgba(59,158,255,0.35)}
#rb:active{transform:translateY(0)}
#rb:disabled{opacity:.4;cursor:not-allowed;transform:none;box-shadow:none}
.search-actions{display:flex;gap:8px;justify-content:center;margin-top:12px}
.tlink{
  background:none;border:1px solid var(--bor2);color:var(--tx3);
  font-size:12px;cursor:pointer;font-family:'Nunito',sans-serif;
  padding:6px 16px;border-radius:var(--r-pill);
  transition:all .2s;font-weight:700;letter-spacing:-.01em;
}
.tlink:hover{border-color:var(--pip);color:var(--pip)}
.tlink.blu{color:var(--pip);border-color:var(--pip-bor);background:var(--pip-dim)}
#ldg{display:none;align-items:center;justify-content:center;gap:10px;margin-top:16px;font-size:13px;color:var(--tx3);font-weight:600}
.spinner{
  width:16px;height:16px;
  border:2px solid var(--bor2);
  border-top-color:var(--pip);
  border-radius:50%;
  animation:spin .65s linear infinite;
}
@keyframes spin{to{transform:rotate(360deg)}}
#err{
  display:none;margin:12px auto;padding:12px 18px;
  background:rgba(255,90,90,0.06);
  border:1px solid rgba(255,90,90,0.18);
  color:var(--red);font-size:12px;border-radius:var(--r);
  max-width:640px;font-weight:600;
}
.panel-extra{
  display:none;
  background:var(--sur);border:1px solid var(--bor);
  padding:18px;margin:12px auto;border-radius:var(--r);
  max-width:640px;
  animation:fadeUp .2s ease;
}
.panel-label{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.14em;margin-bottom:8px;font-weight:800}
#bi,#ii{
  width:100%;background:var(--bg);
  border:1px solid var(--bor2);color:var(--tx);
  font-family:'Nunito',sans-serif;font-size:13px;
  padding:10px 14px;min-height:90px;resize:vertical;
  outline:none;line-height:1.7;border-radius:var(--r-sm);
  transition:border-color .2s;
}
#bi:focus,#ii:focus{border-color:var(--pip)}
.sub-btn{
  background:linear-gradient(135deg,var(--pip),var(--pip-deep));
  color:#fff;border:none;font-weight:800;
  font-size:12px;padding:9px 20px;cursor:pointer;
  margin-top:10px;font-family:'Nunito',sans-serif;
  border-radius:var(--r-sm);
  box-shadow:0 4px 16px rgba(59,158,255,0.2);
  transition:all .2s;
}
.sub-btn:hover{transform:translateY(-1px);box-shadow:0 6px 22px rgba(59,158,255,0.3)}
#ierr{display:none;color:var(--red);font-size:12px;margin-top:6px;font-weight:600}

/* ── FETCH HERO ── */
.fetch-hero{
  text-align:center;
  margin:56px auto 0;
  padding:52px 40px;
  border:1px solid var(--bor);
  border-radius:var(--r);
  background:linear-gradient(160deg,var(--sur) 0%,var(--sur2) 100%);
  max-width:580px;
  position:relative;
  overflow:hidden;
}
.fetch-hero::before{
  content:'';position:absolute;top:-60px;left:50%;transform:translateX(-50%);
  width:400px;height:200px;
  background:radial-gradient(ellipse,rgba(59,158,255,0.07) 0%,transparent 70%);
  pointer-events:none;
}
.fetch-hero-title{font-size:24px;font-weight:900;letter-spacing:-.03em;margin-bottom:10px;color:var(--tx)}
.fetch-hero-sub{font-size:14px;color:var(--tx2);margin-bottom:32px;line-height:1.7;max-width:400px;margin-left:auto;margin-right:auto}
.fetch-hero-btn{
  background:linear-gradient(135deg,var(--pip),var(--pip-deep));
  color:#fff;border:none;font-weight:900;
  font-size:16px;padding:16px 52px;
  cursor:pointer;font-family:'Nunito',sans-serif;
  border-radius:var(--r);
  box-shadow:0 8px 32px rgba(59,158,255,0.3);
  transition:all .25s;letter-spacing:-.02em;
}
.fetch-hero-btn:hover{transform:translateY(-2px);box-shadow:0 12px 40px rgba(59,158,255,0.45)}
.fetch-hero-btn:active{transform:translateY(0)}
.fetch-hero-btn:disabled{opacity:.4;cursor:not-allowed;transform:none;box-shadow:none}

/* fetch results inside hero */
.fetch-list{display:flex;flex-direction:column;gap:4px;margin-bottom:14px;max-height:280px;overflow-y:auto;text-align:left}
.fetch-item{
  display:flex;align-items:center;gap:10px;
  padding:10px 14px;background:var(--bg);
  border:1px solid var(--bor);cursor:pointer;
  border-radius:var(--r-sm);transition:all .15s;
}
.fetch-item:hover{border-color:var(--pip-bor);background:var(--pip-dim)}
.fetch-item.sel{border-color:var(--pip);background:var(--pip-dim)}
.fetch-item input{accent-color:var(--pip);width:15px;height:15px;cursor:pointer;flex-shrink:0}
.fetch-item-name{font-size:13px;font-weight:700;color:var(--tx)}
.fetch-item-meta{font-size:10px;color:var(--tx3);margin-top:1px}
#res-sel-btn{
  background:linear-gradient(135deg,var(--pip),var(--pip-deep));
  color:#fff;border:none;font-weight:800;
  font-size:12px;padding:10px 20px;cursor:pointer;
  font-family:'Nunito',sans-serif;border-radius:var(--r-sm);
  box-shadow:0 4px 16px rgba(59,158,255,0.2);
}
#fetch-count{font-size:11px;color:var(--tx3);margin-left:10px;font-weight:600}
#fetch-ldg{display:none;align-items:center;gap:8px;font-size:12px;color:var(--tx3);margin-top:14px;justify-content:center;font-weight:600}
#fetch-err{display:none;margin-top:12px;padding:10px 14px;background:rgba(255,90,90,0.06);border:1px solid rgba(255,90,90,0.18);color:var(--red);font-size:12px;border-radius:var(--r-sm);font-weight:600}
#fetch-results{display:none;margin-top:20px;padding-top:20px;border-top:1px solid var(--bor);text-align:left}

/* ── TOOLBAR (leads page) ── */
.leads-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
.leads-header h2{font-size:24px;font-weight:900;letter-spacing:-.04em;background:linear-gradient(135deg,#f0f4ff,#8bc4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.leads-toolbar{display:flex;align-items:center;gap:7px;margin-bottom:22px;flex-wrap:wrap}
.fb{
  font-size:11px;padding:6px 14px;
  background:none;border:1px solid var(--bor);
  color:var(--tx3);cursor:pointer;
  font-family:'Nunito',sans-serif;
  border-radius:var(--r-pill);transition:all .18s;font-weight:700;
}
.fb:hover{border-color:var(--bor2);color:var(--tx2)}
.fb.on{border-color:var(--pip);color:var(--pip);background:var(--pip-dim);box-shadow:0 0 12px rgba(59,158,255,0.12)}
.tb-right{margin-left:auto;display:flex;gap:8px}
.tb-btn{
  font-size:11px;padding:6px 14px;
  background:none;border:1px solid var(--bor);
  color:var(--tx2);cursor:pointer;
  font-family:'Nunito',sans-serif;
  border-radius:var(--r-sm);font-weight:700;transition:all .18s;
}
.tb-btn:hover{border-color:var(--pip);color:var(--pip)}
.tb-btn.danger{color:var(--red);border-color:rgba(255,90,90,0.15)}
.tb-btn.danger:hover{border-color:var(--red)}

/* ── SAVED LEADS GRID ── */
.cards-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.lead-card{
  background:linear-gradient(160deg,var(--sur) 0%,var(--sur2) 100%);
  border:1px solid var(--bor);
  border-radius:var(--r);overflow:hidden;
  transition:all .22s;
  box-shadow:var(--shadow-sm);
}
.lead-card:hover{
  border-color:var(--bor2);
  box-shadow:var(--shadow),0 0 0 1px rgba(59,158,255,0.06);
  transform:translateY(-2px);
}
.lead-card-header{
  padding:18px 20px 14px;
  border-bottom:1px solid var(--bor);
  background:linear-gradient(135deg,rgba(59,158,255,0.03),transparent);
}
.lead-card-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:8px}
.lead-card-name{font-size:17px;font-weight:900;letter-spacing:-.03em;color:var(--tx);line-height:1.2}
.lead-card-score{font-size:26px;font-weight:900;letter-spacing:-.04em;line-height:1}
.lead-card-meta{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-top:6px}
.lead-card-tag{font-size:9px;font-weight:800;padding:3px 10px;border-radius:var(--r-pill);border:1px solid;text-transform:uppercase;letter-spacing:.07em}
.lead-card-sector{font-size:11px;color:var(--tx3);font-weight:600}
.lead-card-body{padding:18px 20px}
.lc-sec{
  font-size:8px;color:var(--tx3);text-transform:uppercase;
  letter-spacing:.16em;margin:14px 0 8px;
  display:flex;align-items:center;gap:8px;font-weight:800;
}
.lc-sec::after{content:'';flex:1;height:1px;background:var(--bor)}
.lc-grid{display:grid;grid-template-columns:1fr 1fr;gap:4px;margin-bottom:4px}
.lc-cell{
  background:var(--bg);border:1px solid var(--bor);
  padding:8px 11px;border-radius:var(--r-sm);
  transition:border-color .15s;
}
.lc-cell:hover{border-color:var(--bor2)}
.lc-key{font-size:8px;color:var(--tx3);text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px;font-weight:800}
.lc-val{font-size:12px;color:var(--tx);font-weight:600}
.lc-val a{color:var(--pip);text-decoration:none}
.lc-val.dim{color:var(--tx3);font-style:italic}
.lc-text{font-size:12px;color:var(--tx2);line-height:1.8;margin-bottom:4px;font-weight:500}
.sig-row{display:flex;justify-content:space-between;align-items:center;padding:6px 0;border-bottom:1px solid var(--bor);font-size:12px;font-weight:600}
.sig-row:last-child{border-bottom:none}
.sy{font-size:10px;font-weight:800;color:var(--pip)}
.sn{font-size:10px;font-weight:800;color:var(--red)}
.su{font-size:10px;color:var(--tx3);font-weight:600}
.pitch-box{
  background:linear-gradient(135deg,rgba(59,158,255,0.06),rgba(26,111,212,0.04));
  border:1px solid var(--pip-bor);
  padding:16px;margin-top:8px;border-radius:var(--r-sm);
  position:relative;overflow:hidden;
}
.pitch-box::before{content:'';position:absolute;top:-20px;right:-20px;width:80px;height:80px;background:radial-gradient(circle,rgba(59,158,255,0.08),transparent);pointer-events:none}
.pitch-label{font-size:8px;color:var(--pip);text-transform:uppercase;letter-spacing:.14em;margin-bottom:10px;font-weight:800}
.pitch-text{font-size:12px;color:#c0deff;line-height:1.85;font-style:italic;font-weight:500}
.founder-row{
  display:flex;gap:11px;align-items:flex-start;
  padding:9px 11px;background:var(--bg);
  border:1px solid var(--bor);margin-bottom:5px;
  border-radius:var(--r-sm);transition:border-color .15s;
}
.founder-row:hover{border-color:var(--bor2)}
.fav{
  width:30px;height:30px;border-radius:50%;
  background:linear-gradient(135deg,var(--pip-dim),rgba(59,158,255,0.15));
  border:1px solid var(--pip-bor);
  display:flex;align-items:center;justify-content:center;
  font-size:10px;font-weight:800;color:var(--pip);flex-shrink:0;margin-top:1px;
}
.fname{font-size:13px;font-weight:800;letter-spacing:-.01em}
.frole{font-size:10px;color:var(--tx3);line-height:1.5;font-weight:500}
.social-links{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px}
.social-links a{
  font-size:10px;padding:3px 10px;
  border:1px solid var(--bor);color:var(--tx2);
  text-decoration:none;border-radius:var(--r-pill);
  transition:all .18s;font-weight:700;
}
.social-links a:hover{border-color:var(--pip);color:var(--pip);background:var(--pip-dim)}
.notes-area{
  width:100%;background:var(--bg);border:1px solid var(--bor2);
  color:var(--tx);font-family:'Nunito',sans-serif;
  font-size:12px;padding:10px 14px;min-height:58px;
  resize:none;outline:none;line-height:1.6;
  border-radius:var(--r-sm);margin-top:4px;
  transition:border-color .2s;font-weight:500;
}
.notes-area:focus{border-color:var(--pip);box-shadow:0 0 0 3px rgba(59,158,255,0.08)}
.lead-card-actions{
  display:flex;gap:5px;padding:12px 18px;
  background:rgba(0,0,0,0.2);
  border-top:1px solid var(--bor);flex-wrap:wrap;align-items:center;
}
.abtn{
  font-size:11px;padding:5px 13px;
  background:none;border:1px solid var(--bor);
  color:var(--tx2);cursor:pointer;
  font-family:'Nunito',sans-serif;
  border-radius:var(--r-pill);transition:all .18s;font-weight:700;
}
.abtn:hover{border-color:var(--pip);color:var(--pip);background:var(--pip-dim)}
.abtn.g{
  border-color:var(--pip-bor);color:var(--pip);
  background:var(--pip-dim);
}
.abtn.g:hover{background:rgba(59,158,255,0.14);box-shadow:0 0 12px rgba(59,158,255,0.15)}
.abtn.ghost{margin-left:auto;color:var(--tx3);border-color:transparent}
.abtn.ghost:hover{border-color:rgba(255,90,90,0.2);color:var(--red);background:transparent}
.hiring-badge{font-size:9px;color:var(--pip-light);border:1px solid rgba(59,158,255,0.2);padding:2px 8px;font-weight:800;border-radius:var(--r-pill);letter-spacing:.04em}

/* ── PIPELINE PAGE ── */
.pipeline-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:28px}
.pipeline-header h2{font-size:24px;font-weight:900;letter-spacing:-.04em;background:linear-gradient(135deg,#f0f4ff,#8bc4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.pipeline-board{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;align-items:start}
.pipeline-col{
  background:linear-gradient(160deg,var(--sur) 0%,var(--sur2) 100%);
  border:1px solid var(--bor);padding:14px;
  border-radius:var(--r);
}
.pipeline-col-header{
  font-size:9px;font-weight:800;text-transform:uppercase;
  letter-spacing:.14em;padding-bottom:12px;
  border-bottom:1px solid var(--bor);margin-bottom:10px;
  display:flex;align-items:center;justify-content:space-between;
}
.pipeline-card{
  background:var(--bg);border:1px solid var(--bor);
  padding:13px 14px;margin-bottom:7px;cursor:pointer;
  transition:all .2s;border-radius:var(--r-sm);
}
.pipeline-card:hover{
  border-color:var(--pip-bor);
  box-shadow:0 4px 20px rgba(59,158,255,0.1);
  transform:translateY(-1px);
}
.pipeline-card-name{font-family:'Nunito',sans-serif;font-size:13px;font-weight:800;margin-bottom:3px;color:var(--tx);letter-spacing:-.02em}
.pipeline-card-meta{font-size:10px;color:var(--tx3);margin-bottom:3px;font-weight:600}
.pipeline-card-note{font-size:10px;color:var(--tx3);font-style:italic;margin-top:5px;line-height:1.5}
.pipeline-card-date{font-size:10px;color:var(--amb);margin-top:3px;font-weight:700}
.pipeline-empty{font-size:11px;color:var(--tx3);text-align:center;padding:24px 0;font-style:italic}

/* ── INBOX PAGE ── */
.inbox-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px}
.inbox-header h2{font-size:24px;font-weight:900;letter-spacing:-.04em;background:linear-gradient(135deg,#f0f4ff,#8bc4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.inbox-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.inbox-card{
  background:linear-gradient(160deg,var(--sur) 0%,var(--sur2) 100%);
  border:1px solid var(--bor);border-radius:var(--r);
  overflow:hidden;transition:all .22s;box-shadow:var(--shadow-sm);
}
.inbox-card:hover{border-color:var(--bor2);box-shadow:var(--shadow);transform:translateY(-2px)}
.inbox-card-header{padding:18px 20px 14px}
.inbox-card-name{font-size:16px;font-weight:900;letter-spacing:-.03em;margin-bottom:4px}
.inbox-card-meta{font-size:11px;color:var(--tx3);margin-bottom:8px;font-weight:600}
.inbox-card-body{padding:0 20px 16px;font-size:12px;color:var(--tx2);line-height:1.8}
.inbox-card-actions{display:flex;gap:8px;padding:14px 18px;background:rgba(0,0,0,0.2);border-top:1px solid var(--bor)}
.btn-approve{
  flex:1;background:linear-gradient(135deg,var(--pip),var(--pip-deep));
  color:#fff;border:none;font-weight:800;
  font-size:12px;padding:10px;cursor:pointer;
  font-family:'Nunito',sans-serif;border-radius:var(--r-sm);
  transition:all .2s;box-shadow:0 4px 16px rgba(59,158,255,0.2);
  letter-spacing:-.01em;
}
.btn-approve:hover{transform:translateY(-1px);box-shadow:0 6px 22px rgba(59,158,255,0.35)}
.btn-dismiss{
  flex:1;background:none;color:var(--tx3);
  border:1px solid var(--bor);font-weight:700;
  font-size:12px;padding:10px;cursor:pointer;
  font-family:'Nunito',sans-serif;border-radius:var(--r-sm);
  transition:all .2s;
}
.btn-dismiss:hover{border-color:rgba(255,90,90,0.3);color:var(--red)}
.inbox-empty{text-align:center;padding:80px 20px;color:var(--tx3)}
.inbox-empty-title{font-size:20px;font-weight:900;color:var(--tx2);margin-bottom:10px;letter-spacing:-.03em}

/* ── EMPTY STATE ── */
.empty{text-align:center;padding:80px 20px;color:var(--tx3)}
.empty-title{font-size:20px;font-weight:900;color:var(--tx2);margin-bottom:10px;letter-spacing:-.03em}
.empty p{font-size:13px;line-height:2;font-weight:500}

/* ── PROFILE PAGE ── */
.profile-layout{display:grid;grid-template-columns:300px 1fr;gap:24px;align-items:start}
.profile-sidebar{display:flex;flex-direction:column;gap:16px}
.profile-card{
  background:linear-gradient(160deg,var(--sur) 0%,var(--sur2) 100%);
  border:1px solid var(--bor);border-radius:var(--r);padding:26px;
  box-shadow:var(--shadow-sm);
}
.profile-avatar-wrap{position:relative;width:88px;height:88px;margin:0 auto 18px}
.profile-avatar{
  width:88px;height:88px;border-radius:50%;
  background:linear-gradient(135deg,var(--pip-dim),rgba(59,158,255,0.18));
  border:2px solid var(--pip-bor);
  display:flex;align-items:center;justify-content:center;
  font-size:28px;font-weight:900;color:var(--pip);
  box-shadow:0 0 0 4px rgba(59,158,255,0.08),var(--shadow);
}
.profile-avatar img{width:100%;height:100%;border-radius:50%;object-fit:cover}
.profile-avatar-edit{
  position:absolute;bottom:2px;right:2px;
  width:24px;height:24px;
  background:linear-gradient(135deg,var(--pip),var(--pip-deep));
  border:none;border-radius:50%;cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  font-size:10px;color:#fff;
  box-shadow:0 2px 8px rgba(59,158,255,0.3);
  transition:all .2s;
}
.profile-avatar-edit:hover{transform:scale(1.1)}
.profile-name{font-size:20px;font-weight:900;letter-spacing:-.03em;text-align:center;margin-bottom:5px}
.profile-tagline{font-size:13px;color:var(--tx3);text-align:center;line-height:1.6;margin-bottom:16px;font-weight:500}
.profile-socials{display:flex;gap:6px;justify-content:center;flex-wrap:wrap;margin-bottom:18px}
.profile-social-link{font-size:11px;padding:4px 12px;border:1px solid var(--bor2);color:var(--tx2);text-decoration:none;border-radius:var(--r-pill);transition:all .2s;font-weight:700}
.profile-social-link:hover{border-color:var(--pip);color:var(--pip);background:var(--pip-dim)}
.profile-stat-row{display:flex;justify-content:space-around;padding:14px 0;border-top:1px solid var(--bor)}
.profile-stat{text-align:center}
.profile-stat-n{font-size:24px;font-weight:900;color:var(--pip);letter-spacing:-.04em;line-height:1}
.profile-stat-l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.1em;margin-top:4px;font-weight:700}
.profile-edit-btn{
  width:100%;background:none;border:1px solid var(--bor2);
  color:var(--tx2);font-family:'Nunito',sans-serif;
  font-size:12px;font-weight:800;padding:10px;
  border-radius:var(--r-sm);cursor:pointer;transition:all .2s;
}
.profile-edit-btn:hover{border-color:var(--pip);color:var(--pip);background:var(--pip-dim)}
.profile-share-btn{
  width:100%;background:linear-gradient(135deg,var(--pip),var(--pip-deep));
  color:#fff;border:none;font-family:'Nunito',sans-serif;
  font-size:12px;font-weight:800;padding:10px;
  border-radius:var(--r-sm);cursor:pointer;
  transition:all .2s;margin-top:8px;
  box-shadow:0 4px 16px rgba(59,158,255,0.2);
}
.profile-share-btn:hover{transform:translateY(-1px);box-shadow:0 6px 22px rgba(59,158,255,0.3)}
.service-item{
  display:flex;align-items:center;gap:11px;
  padding:11px 14px;
  background:var(--bg);border:1px solid var(--bor);
  border-radius:var(--r-sm);transition:border-color .2s;
}
.service-item:hover{border-color:var(--bor2)}
.service-icon{font-size:18px;flex-shrink:0}
.service-name{font-size:13px;font-weight:800;color:var(--tx);letter-spacing:-.01em}
.service-desc{font-size:11px;color:var(--tx3);margin-top:2px;font-weight:500}
.profile-main{display:flex;flex-direction:column;gap:20px}
.profile-section{
  background:linear-gradient(160deg,var(--sur) 0%,var(--sur2) 100%);
  border:1px solid var(--bor);border-radius:var(--r);padding:26px;
  box-shadow:var(--shadow-sm);
}
.profile-section-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
.profile-section-title{font-size:15px;font-weight:900;letter-spacing:-.02em}
.profile-add-btn{
  background:none;border:1px solid var(--pip-bor);color:var(--pip);
  font-family:'Nunito',sans-serif;font-size:11px;font-weight:800;
  padding:5px 14px;border-radius:var(--r-pill);cursor:pointer;transition:all .2s;
}
.profile-add-btn:hover{background:var(--pip-dim)}
.case-studies-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
.case-card{
  background:var(--bg);border:1px solid var(--bor);
  border-radius:var(--r-sm);padding:18px;
  transition:all .22s;cursor:pointer;
}
.case-card:hover{border-color:var(--pip-bor);box-shadow:0 4px 20px rgba(59,158,255,0.1);transform:translateY(-1px)}
.case-card-client{font-size:10px;color:var(--pip);font-weight:800;text-transform:uppercase;letter-spacing:.1em;margin-bottom:7px}
.case-card-title{font-size:14px;font-weight:900;letter-spacing:-.02em;margin-bottom:8px;color:var(--tx)}
.case-card-result{font-size:12px;color:var(--tx2);line-height:1.7;margin-bottom:12px;font-weight:500}
.case-metrics{display:flex;gap:6px;flex-wrap:wrap}
.case-metric{
  background:var(--pip-dim);border:1px solid var(--pip-bor);
  border-radius:var(--r-pill);padding:3px 10px;
  font-size:11px;font-weight:800;color:var(--pip-light);
}
.case-card-add{
  background:none;border:1px dashed var(--bor2);color:var(--tx3);
  display:flex;align-items:center;justify-content:center;gap:8px;
  font-family:'Nunito',sans-serif;font-size:13px;font-weight:700;
  padding:40px;border-radius:var(--r-sm);cursor:pointer;
  transition:all .2s;width:100%;
}
.case-card-add:hover{border-color:var(--pip);color:var(--pip);background:var(--pip-dim)}

/* ── PIP HUNT ── */
.ph-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:22px}
.ph-header h2{font-size:24px;font-weight:900;letter-spacing:-.04em;display:flex;align-items:center;gap:10px;background:linear-gradient(135deg,#f0f4ff,#8bc4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.ph-tabs{display:flex;gap:4px;margin-bottom:22px;border-bottom:1px solid var(--bor);padding-bottom:0}
.ph-tab{
  padding:9px 22px;font-size:13px;font-weight:800;color:var(--tx3);
  cursor:pointer;border:none;background:none;
  font-family:'Nunito',sans-serif;
  border-bottom:2px solid transparent;
  transition:all .2s;margin-bottom:-1px;letter-spacing:-.01em;
}
.ph-tab:hover{color:var(--tx2)}
.ph-tab.active{color:var(--pip);border-bottom-color:var(--pip)}
.ph-controls{display:flex;align-items:center;gap:8px;margin-bottom:22px;flex-wrap:wrap}
.ph-filter{
  font-size:11px;padding:5px 14px;background:none;
  border:1px solid var(--bor);color:var(--tx3);
  cursor:pointer;font-family:'Nunito',sans-serif;
  border-radius:var(--r-pill);transition:all .2s;font-weight:700;
}
.ph-filter:hover{border-color:var(--pip);color:var(--pip)}
.ph-filter.on{border-color:var(--pip);color:var(--pip);background:var(--pip-dim);box-shadow:0 0 12px rgba(59,158,255,0.1)}
.ph-fetch-btn{
  background:linear-gradient(135deg,var(--pip),var(--pip-deep));
  color:#fff;border:none;font-weight:800;font-size:12px;
  padding:9px 22px;cursor:pointer;
  font-family:'Nunito',sans-serif;border-radius:var(--r);
  transition:all .2s;margin-left:auto;
  box-shadow:0 4px 16px rgba(59,158,255,0.2);
}
.ph-fetch-btn:hover{transform:translateY(-1px);box-shadow:0 6px 22px rgba(59,158,255,0.35)}
.ph-fetch-btn:disabled{opacity:.4;cursor:not-allowed;transform:none;box-shadow:none}
.ph-status{font-size:11px;color:var(--tx3);margin-left:8px;font-weight:600}
.ph-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.ph-card{
  background:linear-gradient(160deg,var(--sur) 0%,var(--sur2) 100%);
  border:1px solid var(--bor);border-radius:var(--r);
  overflow:hidden;transition:all .22s;box-shadow:var(--shadow-sm);
}
.ph-card:hover{border-color:var(--bor2);box-shadow:var(--shadow);transform:translateY(-2px)}
.ph-card.saved{border-color:var(--pip-bor);background:linear-gradient(160deg,var(--pip-dim),rgba(59,158,255,0.04))}
.ph-card-header{padding:18px 20px 14px}
.ph-card-role{font-size:15px;font-weight:900;letter-spacing:-.02em;color:var(--tx);margin-bottom:5px}
.ph-card-company{font-size:13px;font-weight:800;color:var(--pip);margin-bottom:4px}
.ph-card-meta{display:flex;gap:6px;flex-wrap:wrap;margin-top:8px}
.ph-tag{font-size:9px;font-weight:700;padding:3px 9px;border-radius:var(--r-pill);border:1px solid var(--bor2);color:var(--tx3)}
.ph-tag.remote{border-color:var(--pip-bor);color:var(--pip-light)}
.ph-tag.salary{border-color:rgba(245,166,35,0.25);color:var(--amb)}
.ph-tag.new{border-color:rgba(46,204,138,0.25);color:var(--grn)}
.ph-card-body{padding:0 20px 16px}
.ph-desc{font-size:12px;color:var(--tx2);line-height:1.8;margin-bottom:12px;font-weight:500}
.ph-apply{
  display:flex;align-items:center;gap:8px;
  padding:10px 13px;
  background:var(--bg);border:1px solid var(--bor);
  border-radius:var(--r-sm);margin-bottom:8px;
}
.ph-apply-method{font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.1em;color:var(--tx3);min-width:50px}
.ph-apply-link{font-size:12px;color:var(--pip);text-decoration:none;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:600}
.ph-apply-link:hover{text-decoration:underline}
.ph-card-actions{display:flex;gap:5px;padding:12px 18px;background:rgba(0,0,0,0.2);border-top:1px solid var(--bor);flex-wrap:wrap}
.ph-saved-list{margin-top:36px}
.ph-saved-list h3{font-size:15px;font-weight:900;letter-spacing:-.02em;margin-bottom:16px;color:var(--tx2)}
.ph-empty{text-align:center;padding:80px 20px;color:var(--tx3)}
.ph-empty-title{font-size:20px;font-weight:900;color:var(--tx2);margin-bottom:8px;letter-spacing:-.03em}

/* ── MODALS ── */
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.8);z-index:1000;align-items:center;justify-content:center;backdrop-filter:blur(8px)}
.modal-overlay.open{display:flex}
.modal{
  background:linear-gradient(160deg,var(--sur) 0%,var(--sur2) 100%);
  border:1px solid var(--bor2);border-radius:var(--r);
  padding:32px;width:100%;max-width:540px;
  max-height:88vh;overflow-y:auto;
  box-shadow:var(--shadow-lg),0 0 80px rgba(59,158,255,0.08);
  animation:fadeUp .25s ease;
}
.modal-title{font-size:20px;font-weight:900;letter-spacing:-.03em;margin-bottom:22px;color:var(--tx)}
.modal-field{margin-bottom:14px}
.modal-label{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.14em;font-weight:800;margin-bottom:6px;display:block}
.modal-input{
  width:100%;background:var(--bg);
  border:1px solid var(--bor2);color:var(--tx);
  font-family:'Nunito',sans-serif;font-size:13px;font-weight:500;
  padding:11px 15px;outline:none;border-radius:var(--r-sm);
  transition:all .2s;
}
.modal-input:focus{border-color:var(--pip);box-shadow:0 0 0 3px rgba(59,158,255,0.1)}
.modal-textarea{min-height:88px;resize:vertical}
.modal-actions{display:flex;gap:8px;margin-top:22px;justify-content:flex-end}
.modal-save{
  background:linear-gradient(135deg,var(--pip),var(--pip-deep));
  color:#fff;border:none;font-family:'Nunito',sans-serif;
  font-weight:800;font-size:13px;padding:11px 26px;
  border-radius:var(--r-sm);cursor:pointer;
  box-shadow:0 4px 16px rgba(59,158,255,0.2);
  transition:all .2s;
}
.modal-save:hover{transform:translateY(-1px);box-shadow:0 6px 22px rgba(59,158,255,0.3)}
.modal-cancel{
  background:none;border:1px solid var(--bor2);color:var(--tx2);
  font-family:'Nunito',sans-serif;font-weight:700;
  font-size:13px;padding:11px 26px;border-radius:var(--r-sm);
  cursor:pointer;transition:all .2s;
}
.modal-cancel:hover{border-color:var(--pip);color:var(--pip)}

/* ── PRICING MODAL ── */
.pricing-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.85);z-index:300;align-items:center;justify-content:center;backdrop-filter:blur(10px)}
.pricing-overlay.open{display:flex}
.pricing-modal{
  background:linear-gradient(160deg,var(--sur) 0%,var(--sur2) 100%);
  border:1px solid var(--bor2);border-radius:var(--r);
  padding:40px 36px;width:100%;max-width:800px;
  max-height:90vh;overflow-y:auto;
  box-shadow:var(--shadow-lg),0 0 100px rgba(59,158,255,0.1);
  animation:fadeUp .3s ease;
}
.pricing-title{font-size:30px;font-weight:900;letter-spacing:-.05em;text-align:center;margin-bottom:8px;background:linear-gradient(135deg,#f0f4ff,#8bc4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.pricing-sub{font-size:14px;color:var(--tx3);text-align:center;margin-bottom:36px;font-weight:500}
.pricing-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:28px}
.tier-card{
  background:var(--bg);border:1px solid var(--bor);
  border-radius:var(--r);padding:26px;position:relative;
  transition:all .22s;
}
.tier-card:hover{border-color:var(--bor2);transform:translateY(-2px);box-shadow:var(--shadow)}
.tier-card.featured{
  border-color:var(--pip-bor);
  background:linear-gradient(160deg,rgba(59,158,255,0.06),rgba(26,111,212,0.03));
  box-shadow:0 0 40px rgba(59,158,255,0.1);
}
.tier-badge{
  position:absolute;top:-12px;left:50%;transform:translateX(-50%);
  background:linear-gradient(135deg,var(--pip),var(--pip-deep));
  color:#fff;font-size:9px;font-weight:900;
  padding:4px 14px;border-radius:var(--r-pill);
  text-transform:uppercase;letter-spacing:.1em;white-space:nowrap;
  box-shadow:0 4px 16px rgba(59,158,255,0.3);
}
.tier-name{font-size:11px;font-weight:800;color:var(--tx3);text-transform:uppercase;letter-spacing:.12em;margin-bottom:14px}
.tier-price{font-size:40px;font-weight:900;letter-spacing:-.05em;color:var(--tx);line-height:1;margin-bottom:5px}
.tier-price span{font-size:14px;font-weight:500;color:var(--tx3)}
.tier-desc{font-size:12px;color:var(--tx3);margin-bottom:22px;line-height:1.7;min-height:38px;font-weight:500}
.tier-features{list-style:none;margin-bottom:26px;display:flex;flex-direction:column;gap:9px}
.tier-features li{font-size:12px;color:var(--tx2);display:flex;align-items:flex-start;gap:9px;line-height:1.5;font-weight:600}
.tier-features li::before{content:'✓';color:var(--pip);font-weight:900;flex-shrink:0;margin-top:1px}
.tier-features li.dim{color:var(--tx3)}
.tier-features li.dim::before{content:'—';color:var(--tx3)}
.tier-cta{
  width:100%;background:linear-gradient(135deg,var(--pip),var(--pip-deep));
  color:#fff;border:none;font-family:'Nunito',sans-serif;
  font-weight:800;font-size:13px;padding:13px;
  border-radius:var(--r-sm);cursor:pointer;transition:all .2s;
  box-shadow:0 4px 16px rgba(59,158,255,0.2);
  letter-spacing:-.01em;
}
.tier-cta:hover{transform:translateY(-1px);box-shadow:0 6px 24px rgba(59,158,255,0.35)}
.tier-cta.outline{background:none;border:1px solid var(--bor2);color:var(--tx2);box-shadow:none}
.tier-cta.outline:hover{border-color:var(--pip);color:var(--pip);transform:none;background:var(--pip-dim)}
.pricing-note{font-size:11px;color:var(--tx3);text-align:center;line-height:2;font-weight:500}
.pricing-note a{color:var(--pip);text-decoration:none}

/* ── ONBOARDING ── */
.ob-type-btn.selected{border-color:var(--pip)!important;background:var(--pip-dim)!important;box-shadow:0 0 20px rgba(59,158,255,0.12)!important}
.ob-type-btn.selected div:nth-child(2){color:var(--pip)!important}
.ob-type-btn:hover{border-color:var(--bor2)!important;background:var(--sur2)!important}

/* ── FOOTER ── */
footer{
  border-top:1px solid var(--bor);
  padding:22px 28px;
  display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:12px;margin-top:40px;
  background:rgba(0,0,0,0.15);
}
footer a,footer span,footer button{font-size:11px;color:var(--tx3);font-weight:600}
footer a:hover,footer button:hover{color:var(--pip)}

"""

JS = """

var DB = [];
var INBOX = [];
var busy = false;
var activeSources = ['techcrunch','blockworks','theblock','producthunt','linkedinjobs'];
var currentPage = 'search';
var fil = 'all';

var SYS = "Return ONLY a valid JSON object, no markdown, no backticks, no text before or after. Fields: company, tagline, website, sector, hq, founded, stage, funding_amount, funding_date, lead_investor, other_investors, employee_count, socials (object: twitter, linkedin, discord, telegram, github), founders (array of: name/role/background), has_cmo (bool), has_marketing_hire (bool), marketing_notes, product_status, community_size, hiring_remote (bool - true if they have open remote job listings especially marketing/growth/comms roles), gtm_readiness_score (integer 0-100), gtm_label (exactly Hot Lead if 80+, Warm Lead if 50-79, Cold Lead if below 50), gtm_signals (object of booleans: recently_funded, no_cmo, pre_launch_or_early, active_community, has_product, small_team, marketing_gap_visible), why_fit, risks, pitch_opener, decision_maker, outreach_status (always set to not_contacted), best_contact_title (the exact title of the best person to reach out to for fractional CMO services - prefer CMO, VP Marketing, Head of Growth, Head of Marketing, Co-founder if no marketing hire, or CEO as last resort), best_contact_name (their name if known, else null). Use null for unknown. IMPORTANT: Only research companies that are likely to need fractional CMO services — recently funded startups WITHOUT an established CMO or marketing team. If a company clearly has a mature marketing org, set gtm_readiness_score below 40.";
var FETCH_SYS = "You are a funding news analyst. Search the web for startup funding announcements from the last 14 days. Focus on AI, web3, crypto, blockchain, DeFi, fintech. Return ONLY a valid JSON array, no markdown. Each item: {company:Name,sector:AI/Web3/etc,funding:$XM,stage:Seed/Series A/etc,source:publication}. Max 15 companies. Only include real recent raises.";

function load() {
  fetch('/db').then(function(r){return r.json();}).then(function(d){
    if(Array.isArray(d)){
      DB = d.filter(function(x){return !x._inbox;});
      INBOX = d.filter(function(x){return x._inbox;});
      updateBadges();
      if(currentPage==='profile'){profileLoad();renderProfile();}
      else if(currentPage==='leads') renderLeads();
      else if(currentPage==='pipeline') renderPipelinePage();
      else if(currentPage==='inbox') renderInbox();
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

function openSidebar(){
  document.getElementById('sidebar').classList.add('open');
  document.getElementById('sidebar-overlay').classList.add('open');
}
function closeSidebar(){
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-overlay').classList.remove('open');
}
function navTo(page){closeSidebar();setPage(page);}
function setPage(page) {
  currentPage = page;
  document.querySelectorAll('.page').forEach(function(p){p.classList.remove('active');});
  var pg = document.getElementById('page-'+page);
  if(pg) pg.classList.add('active');
  ['profile','inbox','pipeline','leads','piphunt','search'].forEach(function(p){
    var el = document.getElementById('si-'+p);
    if(el) el.classList.toggle('active', p===page);
  });
  if(page==='leads') renderLeads();
  if(page==='pipeline') renderPipelinePage();
  if(page==='inbox') renderInbox();
  if(page==='piphunt'){phLoad();phRenderJobs();}
  if(page==='profile'){profileLoad();renderProfile();}
}

// ── HELPERS ──────────────────────────────────────────────────────────────────
function sc(n){return n>=80?'var(--pip)':n>=50?'var(--amb)':'var(--tx3)';}
function su(v){if(!v||v==='null'||v==='undefined')return '';return String(v).indexOf('http')===0?v:'https://'+v;}

// ── SEARCH PAGE ──────────────────────────────────────────────────────────────
function go(){var v=document.getElementById('ci').value.trim();if(!v||busy)return;if(!tierCanResearch())return;document.getElementById('ci').value='';run(v);}

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
  closeFetchModal();
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
    // Skip cold leads and companies that already have a CMO
    var score = res.gtm_readiness_score || 0;
    var hasCmo = res.has_cmo === true;
    if(score < 50 || hasCmo){
      if(ind){ind.textContent='skipped '+res.company+' (not a fit)';ind.style.color='var(--tx3)';}
      setTimeout(function(){if(ind)ind.textContent='';},2000);
      if(callback) setTimeout(callback, 300);
      return;
    }
    // Skip cold leads - not worth pursuing
    var score = res.gtm_readiness_score || 0;
    if(score < 50){
      if(ind){ind.textContent='Skipped '+res.company+' (cold lead, score '+score+')';ind.style.color='var(--tx3)';}
      if(callback) setTimeout(callback, 300);
      return;
    }
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

var PH_SYS_CMO = "You are a JSON API. Search the web for open job postings right now. Return ONLY a raw JSON array with no other text, no markdown, no explanation, no backticks. Start your response with [ and end with ]. Each object must have these exact keys: role, company, location, remote (true/false), salary (string or null), posted (e.g. 2 days ago), apply_method (link or email or linkedin), apply_url (full URL or email), description (one sentence), sector. Search for: CMO, VP Marketing, Head of Marketing, Head of Growth, VP Growth at funded tech and AI startups. Return 6-8 real current openings only.";

var PH_SYS_DESIGN = "You are a JSON API. Search the web for open job postings right now. Return ONLY a raw JSON array with no other text, no markdown, no explanation, no backticks. Start your response with [ and end with ]. Each object must have these exact keys: role, company, location, remote (true/false), salary (string or null), posted (e.g. 2 days ago), apply_method (link or email or linkedin), apply_url (full URL or email), description (one sentence), sector. Search for: Head of Design, VP Design, Creative Director, Brand Director, Head of Brand at funded tech and AI startups. Return 6-8 real current openings only.";

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
  if(!tierCanPipHunt())return;
  var btn = document.getElementById('ph-fetch-btn');
  var status = document.getElementById('ph-status');
  btn.disabled = true;
  status.textContent = 'Searching job boards...';
  var sys = phCategory === 'cmo' ? PH_SYS_CMO : PH_SYS_DESIGN;
  var query = phCategory === 'cmo' ? 'site:linkedin.com/jobs OR site:greenhouse.io OR site:lever.co CMO VP Marketing Head of Marketing startup 2025 2026' : 'site:linkedin.com/jobs OR site:greenhouse.io OR site:lever.co Head of Design VP Design Creative Director startup 2025 2026';
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:'',company:query,system:sys,mode:'fetch'})})
  .then(function(r){return r.json();})
  .then(function(d){
    if(d.error) throw new Error(d.error);
    var t=(d.text||'');
    // Try to extract JSON array - be very permissive
    t = t.replace(/```json/g,'').replace(/```/g,'');
    var a=t.indexOf('['), b=t.lastIndexOf(']');
    var jobs = [];
    if(a>=0 && b>a){
      try{ jobs=JSON.parse(t.slice(a,b+1)); }catch(e){
        // Try to find any JSON objects
        var objs=[];
        var re=/{[^{}]+}/g, m;
        while((m=re.exec(t))!==null){
          try{var o=JSON.parse(m[0]);if(o.company||o.role)objs.push(o);}catch(e){}
        }
        jobs=objs;
      }
    }
    if(!Array.isArray(jobs)||!jobs.length){
      // Last resort: ask Claude to convert the text to JSON
      status.textContent='Reformatting results...';
      fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({key:'',company:'Convert this job listing text to a JSON array. Return ONLY the JSON array starting with [. Each item needs: role, company, location, remote, salary, posted, apply_method, apply_url, description, sector. Text: '+t.slice(0,3000),
        system:'Return ONLY a valid JSON array starting with [. No explanation, no markdown.'})})
      .then(function(r2){return r2.json();})
      .then(function(d2){
        var t2=(d2.text||'').replace(/```json/g,'').replace(/```/g,'').trim();
        var a2=t2.indexOf('['),b2=t2.lastIndexOf(']');
        if(a2>=0&&b2>a2){
          try{
            jobs=JSON.parse(t2.slice(a2,b2+1));
            jobs.forEach(function(j){
              j._id='ph'+Date.now()+Math.floor(Math.random()*9999);
              j._cat=phCategory;
              j.role=j.role||j.title||'Open Role';
              j.company=j.company||'Unknown';
            });
            jobs=jobs.filter(function(j){return j.company&&j.role;});
            PH_JOBS=PH_JOBS.concat(jobs);
            phSave();phRenderJobs();
            status.textContent=jobs.length+' jobs found';
          }catch(e2){status.textContent='Could not parse results. Try again.';}
        } else {
          status.textContent='No structured results. Try again.';
        }
        setTimeout(function(){status.textContent='';},4000);
        btn.disabled=false;
      }).catch(function(){
        status.textContent='Parse failed. Try again.';
        setTimeout(function(){status.textContent='';},3000);
        btn.disabled=false;
      });
      return;
    }
    // Filter junk
    var bad=['error','unable','insufficient','no results','no jobs','n/a'];
    jobs=jobs.filter(function(j){
      if(!j.company&&!j.role) return false;
      var lower=((j.company||'')+(j.role||'')).toLowerCase();
      return !bad.some(function(w){return lower.indexOf(w)>=0;});
    });
    // Normalize fields
    jobs.forEach(function(j){
      j._id='ph'+Date.now()+Math.floor(Math.random()*9999);
      j._cat=phCategory;
      j.role=j.role||j.title||j.position||'Open Role';
      j.company=j.company||j.employer||'Unknown';
      j.apply_url=j.apply_url||j.url||j.link||j.application_url||null;
      j.apply_method=j.apply_method||(j.apply_url&&j.apply_url.indexOf('@')>=0?'email':j.apply_url?'link':null);
      j.remote=j.remote||j.is_remote||(j.location&&j.location.toLowerCase().indexOf('remote')>=0)||false;
    });
    // Dedupe
    jobs.forEach(function(j){
      var exists=PH_JOBS.some(function(x){return x.company===j.company&&x.role===j.role;});
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

function openFetchModal(){
  var m=document.getElementById('fetch-modal');
  if(m){m.style.display='flex';}
  // Wire src pills if not already
  document.querySelectorAll('#fetch-modal .src-pill').forEach(function(p){
    p.onclick=function(){
      var s=p.getAttribute('data-src');
      var i=activeSources.indexOf(s);
      if(i>=0){activeSources.splice(i,1);p.classList.remove('on');}
      else{activeSources.push(s);p.classList.add('on');}
    };
  });
}
function closeFetchModal(){
  var m=document.getElementById('fetch-modal');
  if(m){m.style.display='none';}
}


function onboardingSave(){
  var name = document.getElementById('ob-name').value.trim();
  if(!name){document.getElementById('ob-name').focus();return;}
  var p = {};
  try{var ps=localStorage.getItem('scout_profile');if(ps)p=JSON.parse(ps);}catch(e){}
  p.name = name;
  p.tagline = document.getElementById('ob-tagline').value.trim();
  p.linkedin = document.getElementById('ob-linkedin').value.trim();
  try{localStorage.setItem('scout_profile',JSON.stringify(p));}catch(e){}
  document.getElementById('onboarding-modal').classList.remove('open');
  // Reload profile data
  try{PROFILE=p;}catch(e){}
}
function onboardingSkip(){
  document.getElementById('onboarding-modal').classList.remove('open');
}

document.addEventListener('DOMContentLoaded',function(){
  setPage('search');
  updateCreditsBar();
  load();
  // Show onboarding modal on first visit
  setTimeout(function(){
    var p = {};
    try{var ps=localStorage.getItem('scout_profile');if(ps)p=JSON.parse(ps);}catch(e){}
    if(!p.name){
      document.getElementById('onboarding-modal').classList.add('open');
    }
  }, 400);

  // Nav via sidebar hamburger menu


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

// ── PROFILE ──────────────────────────────────────────────────────────────────
var PROFILE = {
  name: '', tagline: '', bio: '',
  linkedin: '', twitter: '', website: '',
  avatar: null,
  services: [],
  cases: []
};

function profileLoad(){
  try{var p=localStorage.getItem('scout_profile');if(p)PROFILE=JSON.parse(p);}catch(e){}
}

function profileSave(){
  try{localStorage.setItem('scout_profile',JSON.stringify(PROFILE));}catch(e){}
  renderProfile();
}

function renderProfile(){
  profileLoad();
  var cont = document.getElementById('profile-root');
  if(!cont) return;

  var initials = PROFILE.name ? PROFILE.name.split(' ').map(function(w){return w[0]||'';}).slice(0,2).join('').toUpperCase() : 'ME';
  var avatarHtml = PROFILE.avatar
    ? '<img src="'+PROFILE.avatar+'" alt="avatar">'
    : '<span style="font-size:32px;font-weight:800;color:var(--pip)">'+initials+'</span>';

  var socialLinks = '';
  if(PROFILE.linkedin) socialLinks += '<a class="profile-social-link" href="'+PROFILE.linkedin+'" target="_blank">LinkedIn</a>';
  if(PROFILE.twitter) socialLinks += '<a class="profile-social-link" href="'+PROFILE.twitter+'" target="_blank">Twitter</a>';
  if(PROFILE.website) socialLinks += '<a class="profile-social-link" href="'+PROFILE.website+'" target="_blank">Website</a>';

  var servicesHtml = '';
  (PROFILE.services||[]).forEach(function(s,i){
    servicesHtml += '<div class="service-item">'
      +'<span class="service-icon">'+(s.icon||'⚡')+'</span>'
      +'<div><div class="service-name">'+s.name+'</div>'
      +(s.desc?'<div class="service-desc">'+s.desc+'</div>':'')
      +'</div>'
      +'<button onclick="profileRemoveService('+i+')" style="margin-left:auto;background:none;border:none;color:var(--tx3);cursor:pointer;font-size:16px">×</button>'
      +'</div>';
  });

  var casesHtml = '';
  (PROFILE.cases||[]).forEach(function(c,i){
    var metrics = (c.metrics||[]).map(function(m){return '<span class="case-metric">'+m+'</span>';}).join('');
    casesHtml += '<div class="case-card" onclick="profileEditCase('+i+')">'
      +'<div class="case-card-client">'+(c.client||'Client')+'</div>'
      +'<div class="case-card-title">'+(c.title||'')+'</div>'
      +'<div class="case-card-result">'+(c.result||'')+'</div>'
      +(metrics?'<div class="case-metrics">'+metrics+'</div>':'')
      +'</div>';
  });
  casesHtml += '<button class="case-card-add" onclick="profileAddCase()">+ Add Case Study</button>';

  cont.innerHTML =
    '<div class="profile-layout">'
      +'<div class="profile-sidebar">'
        // Identity card
        +'<div class="profile-card">'
          +'<div class="profile-avatar-wrap">'
            +'<div class="profile-avatar">'+avatarHtml+'</div>'
            +'<button class="profile-avatar-edit" onclick="profileUploadAvatar()" title="Change photo">✏</button>'
          +'</div>'
          +'<input type="file" id="avatar-input" accept="image/*" style="display:none" onchange="profileHandleAvatar(this)">'
          +(PROFILE.name?'<div class="profile-name">'+PROFILE.name+'</div>':'<div class="profile-name" style="color:var(--tx3)">Your Name</div>')
          +(PROFILE.tagline?'<div class="profile-tagline">'+PROFILE.tagline+'</div>':'<div class="profile-tagline">Add a tagline...</div>')
          +(socialLinks?'<div class="profile-socials">'+socialLinks+'</div>':'')
          +'<div class="profile-stat-row">'
            +'<div class="profile-stat"><div class="profile-stat-n">'+DB.length+'</div><div class="profile-stat-l">Leads</div></div>'
            +'<div class="profile-stat"><div class="profile-stat-n">'+(PROFILE.cases||[]).length+'</div><div class="profile-stat-l">Cases</div></div>'
            +'<div class="profile-stat"><div class="profile-stat-n">'+(PROFILE.services||[]).length+'</div><div class="profile-stat-l">Services</div></div>'
          +'</div>'
          +'<button class="profile-edit-btn" onclick="profileEditInfo()">✏ Edit Profile</button>'
          +'<button class="profile-share-btn" onclick="profileCopyShare()">🔗 Copy Share Link</button>'
        +'</div>'
        // Services card
        +'<div class="profile-card">'
          +'<div class="profile-section-header" style="margin-bottom:14px">'
            +'<div class="profile-section-title">Services</div>'
            +'<button class="profile-add-btn" onclick="profileAddService()">+ Add</button>'
          +'</div>'
          +(servicesHtml||'<div style="font-size:12px;color:var(--tx3);text-align:center;padding:12px 0">Add your services to show prospects what you offer</div>')
        +'</div>'
      +'</div>'
      // Main column
      +'<div class="profile-main">'
        // Bio
        +'<div class="profile-section">'
          +'<div class="profile-section-header">'
            +'<div class="profile-section-title">About</div>'
            +'<button class="profile-add-btn" onclick="profileEditInfo()">Edit</button>'
          +'</div>'
          +(PROFILE.bio
            ?'<div style="font-size:14px;color:var(--tx2);line-height:1.8">'+PROFILE.bio+'</div>'
            :'<div style="font-size:13px;color:var(--tx3);text-align:center;padding:20px 0">Add a bio to tell prospects who you are and what you do best.</div>')
        +'</div>'
        // Case studies
        +'<div class="profile-section">'
          +'<div class="profile-section-header">'
            +'<div class="profile-section-title">Case Studies</div>'
            +'<button class="profile-add-btn" onclick="profileAddCase()">+ Add</button>'
          +'</div>'
          +'<div class="case-studies-grid">'+casesHtml+'</div>'
        +'</div>'
      +'</div>'
    +'</div>';
}

function profileUploadAvatar(){
  document.getElementById('avatar-input').click();
}

function profileHandleAvatar(input){
  if(!input.files||!input.files[0])return;
  var reader=new FileReader();
  reader.onload=function(e){PROFILE.avatar=e.target.result;profileSave();};
  reader.readAsDataURL(input.files[0]);
}

function profileEditInfo(){
  var m=document.getElementById('profile-modal');
  document.getElementById('pm-name').value=PROFILE.name||'';
  document.getElementById('pm-tagline').value=PROFILE.tagline||'';
  document.getElementById('pm-bio').value=PROFILE.bio||'';
  document.getElementById('pm-linkedin').value=PROFILE.linkedin||'';
  document.getElementById('pm-twitter').value=PROFILE.twitter||'';
  document.getElementById('pm-website').value=PROFILE.website||'';
  m.classList.add('open');
}

function profileSaveInfo(){
  PROFILE.name=document.getElementById('pm-name').value.trim();
  PROFILE.tagline=document.getElementById('pm-tagline').value.trim();
  PROFILE.bio=document.getElementById('pm-bio').value.trim();
  PROFILE.linkedin=document.getElementById('pm-linkedin').value.trim();
  PROFILE.twitter=document.getElementById('pm-twitter').value.trim();
  PROFILE.website=document.getElementById('pm-website').value.trim();
  document.getElementById('profile-modal').classList.remove('open');
  profileSave();
}

function profileAddService(){
  var name=prompt('Service name (e.g. GTM Strategy):');
  if(!name)return;
  var desc=prompt('Short description (optional):');
  var icons=['⚡','🎯','📊','🚀','💡','📣','🔥','✨'];
  var icon=icons[Math.floor(Math.random()*icons.length)];
  PROFILE.services=PROFILE.services||[];
  PROFILE.services.push({name:name.trim(),desc:(desc||'').trim(),icon:icon});
  profileSave();
}

function profileRemoveService(i){
  PROFILE.services.splice(i,1);
  profileSave();
}

function profileAddCase(){
  openCaseModal(-1,{client:'',title:'',result:'',metrics:[]});
}

function profileEditCase(i){
  openCaseModal(i,PROFILE.cases[i]);
}

function openCaseModal(idx,c){
  document.getElementById('cm-idx').value=idx;
  document.getElementById('cm-client').value=c.client||'';
  document.getElementById('cm-title').value=c.title||'';
  document.getElementById('cm-result').value=c.result||'';
  document.getElementById('cm-metrics').value=(c.metrics||[]).join(', ');
  document.getElementById('case-modal').classList.add('open');
}

function profileSaveCase(){
  var idx=parseInt(document.getElementById('cm-idx').value);
  var c={
    client:document.getElementById('cm-client').value.trim(),
    title:document.getElementById('cm-title').value.trim(),
    result:document.getElementById('cm-result').value.trim(),
    metrics:document.getElementById('cm-metrics').value.split(',').map(function(s){return s.trim();}).filter(Boolean)
  };
  PROFILE.cases=PROFILE.cases||[];
  if(idx>=0)PROFILE.cases[idx]=c;
  else PROFILE.cases.unshift(c);
  document.getElementById('case-modal').classList.remove('open');
  profileSave();
}

function profileDeleteCase(){
  var idx=parseInt(document.getElementById('cm-idx').value);
  if(idx>=0){
    if(!confirm('Delete this case study?'))return;
    PROFILE.cases.splice(idx,1);
    document.getElementById('case-modal').classList.remove('open');
    profileSave();
  }
}

function profileCopyShare(){
  var url=window.location.origin+'?profile='+encodeURIComponent(PROFILE.name||'me');
  navigator.clipboard.writeText(url);
  var btn=document.querySelector('.profile-share-btn');
  if(btn){btn.textContent='Copied!';setTimeout(function(){btn.textContent='Share Profile';},2000);}
}

var obStep = 1; // 1=type select, 2=details

function obSelectType(type){
  PROFILE.accountType = type;
  // Highlight selected
  document.querySelectorAll('.ob-type-btn').forEach(function(b){
    b.classList.toggle('selected', b.getAttribute('data-type')===type);
  });
  document.getElementById('ob-details').style.display = 'block';
  // Update labels based on type
  var nameLbl = document.getElementById('ob-name-label');
  var tLbl = document.getElementById('ob-tagline-label');
  var lookLbl = document.getElementById('ob-looking-label');
  if(type==='agency'||type==='freelance'){
    nameLbl.textContent = 'Your name or agency';
    tLbl.textContent = 'What you specialise in';
    lookLbl.textContent = 'What type of clients are you looking for?';
  } else if(type==='hiring'){
    nameLbl.textContent = 'Company name';
    tLbl.textContent = 'Industry / sector';
    lookLbl.textContent = 'What marketing role are you hiring for?';
  } else {
    nameLbl.textContent = 'Your name';
    tLbl.textContent = 'Your current role / title';
    lookLbl.textContent = 'What kind of opportunities are you looking for?';
  }
}

function onboardingSave(){
  var name = document.getElementById('ob-name').value.trim();
  if(!name){ document.getElementById('ob-name').focus(); return; }
  PROFILE.name = name;
  PROFILE.tagline = document.getElementById('ob-tagline').value.trim();
  PROFILE.linkedin = document.getElementById('ob-linkedin').value.trim();
  PROFILE.looking = document.getElementById('ob-looking').value.trim();
  // Save without calling renderProfile (page not active yet)
  try{ localStorage.setItem('scout_profile', JSON.stringify(PROFILE)); }catch(e){}
  document.getElementById('onboarding-overlay').classList.remove('open');
  // Update save indicator
  var ind = document.getElementById('save-ind');
  if(ind){ ind.textContent = 'Profile saved'; ind.style.color='var(--pip)'; setTimeout(function(){ind.textContent='';},2000); }
}
function onboardingSkip(){
  document.getElementById('onboarding-overlay').classList.remove('open');
}

// ── TIER / CREDITS SYSTEM ─────────────────────────────────────────────────────
var TIER_LIMITS = {free:{research:5,fetch:2,piphunt:0}, pro:{research:999,fetch:20,piphunt:999}, agency:{research:9999,fetch:100,piphunt:9999}};
var TIER_LABELS = {free:'Free',pro:'Pro',agency:'Agency'};

function tierLoad(){
  try{
    var t=localStorage.getItem('scout_tier');
    if(t) return JSON.parse(t);
  }catch(e){}
  return {plan:'free', research_used:0, fetch_used:0, period: new Date().toISOString().slice(0,7)};
}

function tierSave(t){ try{localStorage.setItem('scout_tier',JSON.stringify(t));}catch(e){} }

function tierReset(t){
  // Reset monthly usage if new month
  var thisMonth = new Date().toISOString().slice(0,7);
  if(t.period !== thisMonth){ t.research_used=0; t.fetch_used=0; t.period=thisMonth; tierSave(t); }
  return t;
}

function tierCanResearch(){
  var t = tierReset(tierLoad());
  var limit = TIER_LIMITS[t.plan||'free'].research;
  if(t.research_used >= limit){
    showPricing('You have used your '+limit+' free research credits this month.');
    return false;
  }
  return true;
}

function tierCanFetch(){
  var t = tierReset(tierLoad());
  var limit = TIER_LIMITS[t.plan||'free'].fetch;
  if(t.fetch_used >= limit){
    showPricing('You have used your '+limit+' free fetch credits this month.');
    return false;
  }
  return true;
}

function tierCanPipHunt(){
  var t = tierReset(tierLoad());
  if(t.plan==='free'){
    showPricing('Pip Hunt is available on Pro and Agency plans.');
    return false;
  }
  return true;
}

function tierUseResearch(){
  var t = tierReset(tierLoad());
  t.research_used = (t.research_used||0) + 1;
  tierSave(t);
  updateCreditsBar();
}

function tierUseFetch(){
  var t = tierReset(tierLoad());
  t.fetch_used = (t.fetch_used||0) + 1;
  tierSave(t);
  updateCreditsBar();
}

function updateCreditsBar(){
  var t = tierReset(tierLoad());
  var plan = t.plan||'free';
  var lim = TIER_LIMITS[plan];
  var barEl = document.getElementById('credits-bar');
  var upBtn = document.getElementById('upgrade-btn');
  if(plan !== 'free'){
    if(barEl) barEl.style.display='none';
    if(upBtn) upBtn.style.display='none';
    return;
  }
  if(barEl) barEl.style.display='flex';
  if(upBtn) upBtn.style.display='';
  var used = t.research_used||0;
  var pct = Math.min(100, Math.round(used/lim.research*100));
  document.getElementById('credits-fill').style.width = pct+'%';
  document.getElementById('credits-count').textContent = (lim.research-used)+' research credits left';
  document.getElementById('credits-fill').style.background = pct>=80?'var(--red)':'var(--pip)';
}

function showPricing(msg){
  if(msg) document.getElementById('pricing-msg').textContent = msg;
  document.getElementById('pricing-overlay').classList.add('open');
}

function closePricing(){
  document.getElementById('pricing-overlay').classList.remove('open');
}

function selectTier(plan){
  if(plan === 'free'){
    var t = tierLoad();
    t.plan = 'free';
    tierSave(t);
    closePricing();
    updateCreditsBar();
    return;
  }
  // Redirect to Stripe checkout
  var urls = {
    pro: 'https://buy.stripe.com/00wdR90wGc4Cd52gyCbjW01',
    agency: 'https://buy.stripe.com/8x2dR993c3y6aWU0zEbjW00'
  };
  window.open(urls[plan], '_blank');
  closePricing();
}

// Earn free credits by tagging a company hiring
function earnCredit(){
  var t = tierReset(tierLoad());
  if(t.plan !== 'free') return;
  t.research_used = Math.max(0, (t.research_used||0) - 1);
  tierSave(t);
  updateCreditsBar();
  var ind = document.getElementById('save-ind');
  if(ind){ind.textContent='+1 credit earned!';ind.style.color='var(--pip)';setTimeout(function(){ind.textContent='';},2500);}
}

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
    "<button class='logo-btn' onclick='setPage(\"search\")'>"
      "<div class='logo-mark'><img src='data:image/png;base64,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' style='width:32px;height:32px;object-fit:contain'></div>"
      "<span class='logo-text'>Scout</span>"
    "</button>"
    "<div class='topbar-right'>"
      "<button onclick='showPricing()' id='upgrade-btn' style='background:none;border:1px solid var(--pip-bor);color:var(--pip);font-size:11px;font-weight:700;padding:5px 14px;border-radius:999px;cursor:pointer;font-family:Nunito,sans-serif'>&#9889; Upgrade</button>"
    "<span class='save-ind' id='save-ind'></span>"
      "<button class='hamburger' onclick='openSidebar()' title='Menu'>"
        "<span></span><span></span><span></span>"
      "</button>"
    "</div>"
  "</div>\n"

  "<div class='sidebar-overlay' id='sidebar-overlay' onclick='closeSidebar()'></div>\n"
  "<div class='sidebar' id='sidebar'>"
    "<div class='sidebar-header'>"
      "<span class='sidebar-title'>Menu</span>"
      "<button class='sidebar-close' onclick='closeSidebar()'>&#215;</button>"
    "</div>"
    "<div class='sidebar-nav'>"
      "<button class='sidebar-item' id='si-profile' onclick='navTo(\"profile\")'><span class='si-icon'>&#128100;</span>Profile</button>"
      "<button class='sidebar-item' id='si-inbox' onclick='navTo(\"inbox\")'><span class='si-icon'>&#128235;</span>Inbox<span class='si-badge' id='inbox-badge' style='display:none'>0</span></button>"
      "<button class='sidebar-item' id='si-pipeline' onclick='navTo(\"pipeline\")'><span class='si-icon'>&#9646;</span>Pipeline</button>"
      "<button class='sidebar-item' id='si-leads' onclick='navTo(\"leads\")'><span class='si-icon'>&#11088;</span>Saved Leads<span style='margin-left:auto;font-size:11px;color:var(--tx3)' id='leads-badge'>0</span></button>"
    "</div>"
    "<div class='sidebar-pip'>"
      "<div class='sidebar-pip-row'>"
        "<img src='data:image/png;base64,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' style='width:32px;height:32px;object-fit:contain'>"
        "<div><div class='sidebar-pip-name'>Pip Hunt</div><div class='sidebar-pip-sub'>Find open roles</div></div>"
        "<button onclick='navTo(\"piphunt\")' style='margin-left:auto;background:var(--pip);color:#fff;border:none;font-size:11px;font-weight:700;padding:5px 12px;border-radius:var(--r-pill);cursor:pointer;font-family:Nunito,sans-serif'>Open</button>"
      "</div>"
    "</div>"
  "</div>\n"

  "<div class='page active' id='page-search'>"
    "<div class='search-hero'>"
      "<h1>Find your next client</h1>"
      "<p>Research any company to get a full GTM profile, score and pitch opener.</p>"
    "</div>"
    "<div class='search-box'>"
      "<input id='ci' type='text' placeholder='Company name, e.g. Privy, Alchemy, Listen Labs...'>"
      "<button id='rb'>Research →</button>"
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
    "<div class='fetch-hero'>"
      "<div class='fetch-hero-title'>&#9889; Fetch New Leads</div>"
      "<div class='fetch-hero-sub'>Pull recently funded companies from the web — they land in your Inbox for review</div>"
      "<button id='fetch-btn' class='fetch-hero-btn'>Fetch Leads</button>"
      "<div id='fetch-ldg' style='display:none;align-items:center;justify-content:center;gap:10px;margin-top:16px;font-size:13px;color:var(--tx3)'><div class='spinner'></div><span>Searching funding news...</span></div>"
      "<div id='fetch-err'></div>"
      "<div id='fetch-results'>"
        "<div style='font-size:12px;color:var(--tx3);margin-bottom:12px;text-align:center'>Select companies to research — they go to your Inbox:</div>"
        "<div class='fetch-list' id='fetch-list'></div>"
        "<div style='display:flex;align-items:center;justify-content:center;margin-top:12px'>"
          "<button id='res-sel-btn'>Research Selected →</button>"
          "<span id='fetch-count' style='margin-left:12px'></span>"
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

  "<div class='page' id='page-profile'>"
    "<div id='profile-root' style='padding:4px 0'></div>"
  "</div>\n"

  "<div class='page' id='page-piphunt'>"
    "<div class='ph-header'><h2><img src='data:image/png;base64,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' style='width:28px;height:28px;object-fit:contain;vertical-align:middle;margin-right:8px'>Pip Hunt</h2><span style='font-size:13px;color:var(--tx3)'>Find companies actively hiring marketing & design leadership</span></div>"
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

  "<div id='fetch-modal' style='display:none;position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:200;align-items:center;justify-content:center'>"
    "<div style='background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);padding:28px;width:560px;max-width:90vw;max-height:80vh;overflow-y:auto'>"
      "<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:16px'>"
        "<div><div style='font-size:15px;font-weight:800;color:var(--pip)'>Fetch Funded Startups</div>"
        "<div style='font-size:12px;color:var(--tx3);margin-top:2px'>Pull recent raises → research → send to Inbox</div></div>"
        "<button onclick='closeFetchModal()' style='background:none;border:none;color:var(--tx3);font-size:18px;cursor:pointer;padding:4px 8px'>✕</button>"
      "</div>"
      "<div class='src-pills' style='margin-bottom:16px'>"
        "<div class='src-pill on' data-src='techcrunch'>TechCrunch</div>"
        "<div class='src-pill on' data-src='blockworks'>Blockworks</div>"
        "<div class='src-pill on' data-src='theblock'>The Block</div>"
        "<div class='src-pill' data-src='cryptofunding'>Crypto-fundraising</div>"
        "<div class='src-pill on' data-src='producthunt'>ProductHunt</div>"
        "<div class='src-pill on' data-src='linkedinjobs'>LinkedIn Jobs</div>"
      "</div>"
      "<button id='fetch-btn' style='background:var(--pip);color:#fff;border:none;font-weight:700;font-size:13px;padding:10px 24px;cursor:pointer;font-family:Nunito,sans-serif;border-radius:var(--r);width:100%;transition:opacity .2s'>Search Funding News →</button>"
      "<div id='fetch-ldg' style='display:none;align-items:center;gap:8px;font-size:12px;color:var(--tx3);margin-top:12px'><div class='spinner'></div><span>Searching...</span></div>"
      "<div id='fetch-err' style='display:none;margin-top:10px;padding:10px;background:rgba(248,81,73,0.06);border:1px solid rgba(248,81,73,0.2);color:var(--red);font-size:12px;border-radius:8px'></div>"
      "<div id='fetch-results' style='display:none;margin-top:14px'>"
        "<div style='font-size:11px;color:var(--tx3);margin-bottom:8px'>Select companies to research → Inbox:</div>"
        "<div class='fetch-list' id='fetch-list'></div>"
        "<div style='display:flex;align-items:center;margin-top:10px'>"
          "<button id='res-sel-btn' style='background:var(--pip);color:#fff;border:none;font-weight:700;font-size:12px;padding:9px 18px;cursor:pointer;font-family:Nunito,sans-serif;border-radius:8px'>Research Selected →</button>"
          "<span id='fetch-count' style='font-size:11px;color:var(--tx3);margin-left:10px'></span>"
        "</div>"
      "</div>"
    "</div>"
  "</div>\n"

  "<div class='modal-overlay' id='onboarding-modal'>"
    "<div class='modal' style='max-width:480px'>"
      "<div style='text-align:center;margin-bottom:24px'>"
        "<img src='data:image/png;base64,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' style='width:56px;height:56px;object-fit:contain;margin-bottom:12px'>"
        "<div style='font-size:24px;font-weight:800;letter-spacing:-.03em;margin-bottom:6px'>Welcome to Scout</div>"
        "<div style='font-size:13px;color:var(--tx3)'>Your AI-powered client acquisition tool. Set up your profile to get started.</div>"
      "</div>"
      "<div class='modal-field'><label class='modal-label'>Your Name / Agency ✳</label><input class='modal-input' id='ob-name' placeholder='e.g. Jane Smith or Acme Marketing'></div>"
      "<div class='modal-field'><label class='modal-label'>Tagline</label><input class='modal-input' id='ob-tagline' placeholder='Fractional CMO for AI-first startups'></div>"
      "<div class='modal-field'><label class='modal-label'>LinkedIn URL</label><input class='modal-input' id='ob-linkedin' placeholder='https://linkedin.com/in/yourname'></div>"
      "<div class='modal-actions'>"
        "<button class='modal-cancel' onclick='onboardingSkip()'>Skip for now</button>"
        "<button class='modal-save' onclick='onboardingSave()'>Enter Scout &#8594;</button>"
      "</div>"
    "</div>"
  "</div>\n"

  "<div class='modal-overlay' id='onboarding-overlay'>"
    "<div class='modal' style='max-width:500px'>"
      "<div style='text-align:center;margin-bottom:20px'>"
        "<img src='data:image/png;base64,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' style='width:52px;height:52px;object-fit:contain;margin-bottom:12px'>"
        "<div class='modal-title' style='text-align:center;font-size:22px;margin-bottom:6px'>Welcome to Scout</div>"
        "<div style='font-size:13px;color:var(--tx3);line-height:1.7'>Your AI-powered client research tool. How are you using Scout?</div>"
      "</div>"
      "<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:20px'>"
        "<button class='ob-type-btn' data-type='agency' onclick='obSelectType(\"agency\")' style='background:var(--bg);border:1px solid var(--bor2);border-radius:var(--r);padding:16px 10px;cursor:pointer;text-align:center;transition:all .2s;font-family:Nunito,sans-serif'>"
          "<div style='font-size:24px;margin-bottom:8px'>🏢</div>"
          "<div style='font-size:12px;font-weight:800;color:var(--tx);margin-bottom:4px'>Agency / Freelance</div>"
          "<div style='font-size:10px;color:var(--tx3)'>Finding clients</div>"
        "</button>"
        "<button class='ob-type-btn' data-type='personal' onclick='obSelectType(\"personal\")' style='background:var(--bg);border:1px solid var(--bor2);border-radius:var(--r);padding:16px 10px;cursor:pointer;text-align:center;transition:all .2s;font-family:Nunito,sans-serif'>"
          "<div style='font-size:24px;margin-bottom:8px'>👤</div>"
          "<div style='font-size:12px;font-weight:800;color:var(--tx);margin-bottom:4px'>Personal</div>"
          "<div style='font-size:10px;color:var(--tx3)'>Finding opportunities</div>"
        "</button>"
        "<button class='ob-type-btn' data-type='hiring' onclick='obSelectType(\"hiring\")' style='background:var(--bg);border:1px solid var(--bor2);border-radius:var(--r);padding:16px 10px;cursor:pointer;text-align:center;transition:all .2s;font-family:Nunito,sans-serif'>"
          "<div style='font-size:24px;margin-bottom:8px'>📋</div>"
          "<div style='font-size:12px;font-weight:800;color:var(--tx);margin-bottom:4px'>Hiring</div>"
          "<div style='font-size:10px;color:var(--tx3)'>Finding candidates</div>"
        "</button>"
      "</div>"
      "<div id='ob-details' style='display:none'>"
        "<div class='modal-field'><label class='modal-label' id='ob-name-label'>Your name or agency</label><input class='modal-input' id='ob-name' placeholder='e.g. Cara Moschetti'></div>"
        "<div class='modal-field'><label class='modal-label' id='ob-tagline-label'>What you specialise in</label><input class='modal-input' id='ob-tagline' placeholder='e.g. Fractional CMO for AI startups'></div>"
        "<div class='modal-field'><label class='modal-label'>LinkedIn URL</label><input class='modal-input' id='ob-linkedin' placeholder='https://linkedin.com/in/yourname'></div>"
        "<div class='modal-field'><label class='modal-label' id='ob-looking-label'>What type of clients are you looking for?</label><input class='modal-input' id='ob-looking' placeholder='e.g. Series A-B AI startups, no CMO'></div>"
        "<div style='display:flex;gap:10px;margin-top:20px'>"
          "<button class='modal-cancel' onclick='onboardingSkip()' style='flex:1'>Skip for now</button>"
          "<button class='modal-save' onclick='onboardingSave()' style='flex:2'>Enter Scout &#8594;</button>"
        "</div>"
      "</div>"
      "<div id='ob-skip-row' style='text-align:center;margin-top:16px'>"
        "<button onclick='onboardingSkip()' style='background:none;border:none;color:var(--tx3);font-size:12px;cursor:pointer;font-family:Nunito,sans-serif;text-decoration:underline'>Skip for now</button>"
      "</div>"
    "</div>"
  "</div>\n"
  "</div>\n"

  "<div class='pricing-overlay' id='pricing-overlay'>"
    "<div class='pricing-modal'>"
      "<div id='pricing-msg' style='font-size:13px;color:var(--amb);text-align:center;margin-bottom:12px;min-height:18px'></div>"
      "<div class='pricing-title'>Choose your plan</div>"
      "<div class='pricing-sub'>Start free. Upgrade when Scout starts paying for itself.</div>"
      "<div class='pricing-grid'>"
        "<div class='tier-card'>"
          "<div class='tier-name'>Free</div>"
          "<div class='tier-price'>$0<span>/mo</span></div>"
          "<div class='tier-desc'>Try Scout and see if it fits your workflow</div>"
          "<ul class='tier-features'>"
            "<li>5 company researches/month</li>"
            "<li>2 lead fetches/month</li>"
            "<li>Inbox &amp; Pipeline</li>"
            "<li class='dim'>Pip Hunt job search</li>"
            "<li class='dim'>CSV export</li>"
            "<li class='dim'>Team access</li>"
            "<li>+1 credit per company you tag as hiring</li>"
          "</ul>"
          "<button class='tier-cta outline' onclick='selectTier(\"free\")'>Current plan</button>"
        "</div>"
        "<div class='tier-card featured'>"
          "<div class='tier-badge'>Most Popular</div>"
          "<div class='tier-name'>Pro</div>"
          "<div class='tier-price'>$29<span>/mo</span></div>"
          "<div class='tier-desc'>For freelancers and fractional CMOs actively prospecting</div>"
          "<ul class='tier-features'>"
            "<li>Unlimited research</li>"
            "<li>20 lead fetches/month</li>"
            "<li>Pip Hunt job search</li>"
            "<li>CSV export</li>"
            "<li>Inbox, Pipeline, Profile</li>"
            "<li class='dim'>Team access</li>"
            "<li>Priority support</li>"
          "</ul>"
          "<button class='tier-cta' onclick='selectTier(\"pro\")'>Get Pro &#8594;</button>"
        "</div>"
        "<div class='tier-card'>"
          "<div class='tier-name'>Agency</div>"
          "<div class='tier-price'>$99<span>/mo</span></div>"
          "<div class='tier-desc'>For agencies managing multiple clients and team pipelines</div>"
          "<ul class='tier-features'>"
            "<li>Everything in Pro</li>"
            "<li>Up to 5 team members</li>"
            "<li>Shared pipeline &amp; inbox</li>"
            "<li>100 lead fetches/month</li>"
            "<li>White-label pitch openers</li>"
            "<li>Client workspace</li>"
            "<li>Dedicated support</li>"
          "</ul>"
          "<button class='tier-cta' onclick='selectTier(\"agency\")'>Get Agency &#8594;</button>"
        "</div>"
      "</div>"
      "<div class='pricing-note'>"
        "Cancel anytime &nbsp;&#183;&nbsp; Secure payments via Stripe &nbsp;&#183;&nbsp; "
        "<a href='#' onclick='closePricing()'>Maybe later</a>"
      "</div>"
    "</div>"
  "</div>\n"

  "<footer style='border-top:1px solid var(--bor);padding:20px 28px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-top:40px'>"
  "<span style='font-size:11px;color:var(--tx3)'>&#169; 2026 Scout · Sushicat Ventures LLC</span>"
  "<div style='display:flex;gap:20px;align-items:center'>"
    "<a href='/legal#terms' target='_blank' style='font-size:11px;color:var(--tx3);text-decoration:none' onmouseover=\"this.style.color='var(--pip)'\" onmouseout=\"this.style.color='var(--tx3)'\">Terms of Service</a>"
    "<a href='/legal#privacy' target='_blank' style='font-size:11px;color:var(--tx3);text-decoration:none' onmouseover=\"this.style.color='var(--pip)'\" onmouseout=\"this.style.color='var(--tx3)'\">Privacy Policy</a>"
    "<a href='mailto:hello@scout.so' style='font-size:11px;color:var(--tx3);text-decoration:none' onmouseover=\"this.style.color='var(--pip)'\" onmouseout=\"this.style.color='var(--tx3)'\">Contact</a>"
    "<button onclick='showPricing()' style='font-size:11px;color:var(--pip);background:none;border:none;cursor:pointer;font-family:Nunito,sans-serif;font-weight:700;padding:0'>&#9889; Upgrade</button>"
  "</div>"
"</footer>\n"
  "<script>" + JS + "</script>\n"
  "</body>\n</html>\n")

LEGAL_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scout — Terms of Service & Privacy Policy</title>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--pip:#2d9de8;--bg:#07090f;--sur:#0c1018;--bor:#1c2333;--tx:#e2e8f0;--tx2:#8896aa;--tx3:#445566;}
body{background:var(--bg);color:var(--tx);font-family:'Nunito',sans-serif;font-size:15px;line-height:1.8}
.wrap{max-width:780px;margin:0 auto;padding:60px 32px}
.topbar{background:rgba(7,9,15,0.97);border-bottom:1px solid var(--bor);padding:14px 32px;display:flex;align-items:center;gap:10px;position:sticky;top:0;z-index:10}
.topbar-logo{font-size:18px;font-weight:800;letter-spacing:-.03em;color:var(--tx)}
.topbar-logo span{color:var(--pip)}
nav{display:flex;gap:24px;margin-left:auto}
nav a{font-size:13px;color:var(--tx3);text-decoration:none;font-weight:600}
nav a:hover{color:var(--pip)}
h1{font-size:38px;font-weight:800;letter-spacing:-.04em;margin-bottom:8px;color:var(--tx)}
.meta{font-size:12px;color:var(--tx3);margin-bottom:48px;padding-bottom:24px;border-bottom:1px solid var(--bor)}
h2{font-size:20px;font-weight:800;letter-spacing:-.02em;margin:40px 0 14px;color:var(--tx)}
h3{font-size:16px;font-weight:700;margin:24px 0 10px;color:var(--tx2)}
p{color:var(--tx2);margin-bottom:14px}
ul,ol{color:var(--tx2);padding-left:24px;margin-bottom:14px}
li{margin-bottom:6px}
a{color:var(--pip);text-decoration:none}
a:hover{text-decoration:underline}
.divider{border:none;border-top:1px solid var(--bor);margin:64px 0}
.highlight{background:rgba(45,157,232,0.08);border:1px solid rgba(45,157,232,0.2);border-radius:8px;padding:16px 20px;margin:20px 0}
.highlight p{margin:0;font-size:13px;color:var(--tx2)}
strong{color:var(--tx);font-weight:700}
.toc{background:var(--sur);border:1px solid var(--bor);border-radius:10px;padding:24px;margin-bottom:40px}
.toc h3{margin:0 0 12px;font-size:14px;text-transform:uppercase;letter-spacing:.1em;color:var(--tx3)}
.toc ol{margin:0}
.toc li{font-size:13px;margin-bottom:4px}
</style>
</head>
<body>

<div class="topbar">
  <span class="topbar-logo">Scout<span>.</span></span>
  <nav>
    <a href="#terms">Terms of Service</a>
    <a href="#privacy">Privacy Policy</a>
  </nav>
</div>

<div class="wrap">

<!-- TERMS OF SERVICE -->
<div id="terms">
<h1>Terms of Service</h1>
<div class="meta">Last updated: April 7, 2026 &nbsp;·&nbsp; Effective immediately</div>

<div class="toc">
  <h3>Contents</h3>
  <ol>
    <li><a href="#t1">Acceptance of Terms</a></li>
    <li><a href="#t2">Description of Service</a></li>
    <li><a href="#t3">Account Registration</a></li>
    <li><a href="#t4">Subscription Plans and Billing</a></li>
    <li><a href="#t5">Free Tier and Credits</a></li>
    <li><a href="#t6">Acceptable Use</a></li>
    <li><a href="#t7">Intellectual Property</a></li>
    <li><a href="#t8">AI-Generated Content</a></li>
    <li><a href="#t9">Data and Privacy</a></li>
    <li><a href="#t10">Termination</a></li>
    <li><a href="#t11">Disclaimers and Limitation of Liability</a></li>
    <li><a href="#t12">Governing Law</a></li>
    <li><a href="#t13">Contact</a></li>
  </ol>
</div>

<h2 id="t1">1. Acceptance of Terms</h2>
<p>By accessing or using Scout ("the Service", "Scout", "we", "us"), operated by Sushicat Ventures, you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use the Service.</p>
<p>We may update these terms at any time. Continued use of the Service after changes constitutes acceptance of the updated terms. We will notify active subscribers of material changes by email.</p>

<h2 id="t2">2. Description of Service</h2>
<p>Scout is a SaaS platform that provides AI-powered company research, lead scoring, pitch generation, and pipeline management tools for marketing professionals. Scout also includes Pip Hunt, a job intelligence feature that surfaces open marketing and design leadership roles.</p>
<p>The Service uses artificial intelligence to generate research, scores, and content. All AI-generated content is provided for informational purposes and should be independently verified before use.</p>

<h2 id="t3">3. Account Registration</h2>
<p>You must provide accurate information when creating an account. You are responsible for maintaining the security of your account and for all activity under your account. Notify us immediately at <a href="mailto:hello@scout.so">hello@scout.so</a> if you suspect unauthorised access.</p>
<p>You must be at least 18 years old to use the Service. By registering, you confirm you meet this requirement.</p>

<h2 id="t4">4. Subscription Plans and Billing</h2>
<p>Scout offers the following subscription plans:</p>
<ul>
  <li><strong>Free:</strong> Limited usage as described on the pricing page, no charge</li>
  <li><strong>Pro:</strong> $29.00 USD per month, billed monthly</li>
  <li><strong>Agency:</strong> $99.00 USD per month, billed monthly</li>
</ul>
<p>Payments are processed by Stripe. By subscribing, you authorise us to charge your payment method on a recurring monthly basis until you cancel. All prices are in USD and exclude applicable taxes.</p>
<p><strong>Cancellation:</strong> You may cancel your subscription at any time via your account settings or by contacting us. Cancellation takes effect at the end of your current billing period. We do not offer refunds for partial months.</p>
<p><strong>Price changes:</strong> We will give at least 30 days' notice before changing subscription prices. Your continued use after the change date constitutes acceptance.</p>

<h2 id="t5">5. Free Tier and Credits</h2>
<p>Free tier users receive 5 company research credits per calendar month. Credits reset on the first of each month and do not roll over.</p>
<p>Additional credits may be earned by contributing to the community job board (e.g. tagging companies known to be hiring). Earned credits expire at end of month and are subject to fair use limits. We reserve the right to modify the credits earning system at any time.</p>

<h2 id="t6">6. Acceptable Use</h2>
<p>You agree not to use Scout to:</p>
<ul>
  <li>Scrape, harvest, or systematically collect data for resale or redistribution</li>
  <li>Send unsolicited commercial messages (spam) using content generated by Scout</li>
  <li>Misrepresent your identity or affiliation when using AI-generated pitch content</li>
  <li>Attempt to reverse engineer, decompile, or extract the underlying AI prompts or systems</li>
  <li>Use the Service for any illegal purpose or in violation of any applicable law</li>
  <li>Share your account credentials with others (Agency plan users may add up to 5 team members via the designated team feature)</li>
</ul>
<p>We reserve the right to suspend or terminate accounts that violate these terms without notice.</p>

<h2 id="t7">7. Intellectual Property</h2>
<p>Scout and its original content, features, and functionality are owned by Sushicat Ventures and protected by intellectual property laws. You may not reproduce, distribute, or create derivative works without our written permission.</p>
<p>Content you create using Scout (notes, case studies, profile information) remains yours. You grant us a limited licence to store and process this content to provide the Service.</p>
<p>AI-generated research, scores, and pitch content produced by Scout is provided to you for your personal business use. You may use this content in your own outreach and communications.</p>

<h2 id="t8">8. AI-Generated Content</h2>
<div class="highlight">
  <p><strong>Important:</strong> Scout uses AI to generate company research, GTM scores, and pitch openers. This content is automatically generated and may contain inaccuracies, outdated information, or errors. It should not be relied upon as professional advice. Always verify AI-generated information before acting on it.</p>
</div>
<p>We do not guarantee the accuracy, completeness, or fitness for purpose of any AI-generated content. Scores and assessments are indicators only and do not constitute financial, legal, or business advice.</p>

<h2 id="t9">9. Data and Privacy</h2>
<p>Your use of the Service is also governed by our Privacy Policy below. By using Scout, you consent to the collection and use of information as described therein.</p>
<p>Company data researched through Scout is sourced from publicly available information and AI training data. We do not sell your personal data to third parties.</p>

<h2 id="t10">10. Termination</h2>
<p>We may suspend or terminate your account at any time for violations of these Terms. You may delete your account at any time. Upon termination, your data will be retained for 30 days before deletion, except where we are required by law to retain it longer.</p>

<h2 id="t11">11. Disclaimers and Limitation of Liability</h2>
<p>The Service is provided "as is" without warranties of any kind, express or implied. We do not warrant that the Service will be uninterrupted, error-free, or free of viruses.</p>
<p>To the maximum extent permitted by law, Sushicat Ventures shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of the Service, even if we have been advised of the possibility of such damages.</p>
<p>Our total liability to you for any claims arising from use of the Service shall not exceed the amount you paid us in the 3 months preceding the claim.</p>

<h2 id="t12">12. Governing Law</h2>
<p>These Terms are governed by the laws of Spain, without regard to conflict of law principles. Any disputes shall be subject to the exclusive jurisdiction of the courts of Madrid, Spain.</p>

<h2 id="t13">13. Contact</h2>
<p>For questions about these Terms, contact us at: <a href="mailto:hello@scout.so">hello@scout.so</a></p>
</div>

<hr class="divider">

<!-- PRIVACY POLICY -->
<div id="privacy">
<h1>Privacy Policy</h1>
<div class="meta">Last updated: April 7, 2026 &nbsp;·&nbsp; Effective immediately</div>

<p>This Privacy Policy explains how Scout, operated by Sushicat Ventures ("we", "us", "our"), collects, uses, and protects your personal information when you use our Service.</p>

<div class="highlight">
  <p>The short version: We collect only what we need to run the Service. We don't sell your data. We use Stripe for payments (they have their own privacy policy). You can delete your data at any time.</p>
</div>

<h2>1. Information We Collect</h2>

<h3>Information you provide directly</h3>
<ul>
  <li>Name and agency/company name</li>
  <li>Email address (at signup and payment)</li>
  <li>Profile information (tagline, LinkedIn URL, bio, services, case studies)</li>
  <li>Notes and pipeline data you enter about prospects</li>
  <li>Account type preference (Agency/Freelance, Personal, or Hiring)</li>
</ul>

<h3>Information collected automatically</h3>
<ul>
  <li>Usage data (which features you use, research queries submitted)</li>
  <li>Browser type and approximate location (for service delivery)</li>
  <li>Session data stored in your browser's localStorage</li>
</ul>

<h3>Payment information</h3>
<p>We use Stripe to process payments. We do not store your card details. Stripe's privacy policy governs payment data: <a href="https://stripe.com/privacy" target="_blank">stripe.com/privacy</a></p>

<h2>2. How We Use Your Information</h2>
<ul>
  <li>To provide, operate, and improve the Service</li>
  <li>To process payments and manage your subscription</li>
  <li>To personalise your experience (e.g. profile information shown in the app)</li>
  <li>To send you service-related emails (account updates, billing notifications)</li>
  <li>To enforce our Terms of Service</li>
  <li>To comply with legal obligations</li>
</ul>
<p>We do not use your data to train AI models. Your company research queries are sent to Anthropic's Claude API solely for the purpose of generating your research results.</p>

<h2>3. Data Storage</h2>
<p>Your lead data and profile information is stored in a private GitHub Gist associated with your Scout deployment. Profile preferences are stored in your browser's localStorage. We use Railway for application hosting.</p>
<p>All data is stored in the United States (Railway's us-west2 region). If you are located in the EU/EEA, your data is transferred to the US under standard data processing terms.</p>

<h2>4. Third-Party Services</h2>
<p>Scout uses the following third-party services:</p>
<ul>
  <li><strong>Anthropic (Claude API)</strong> — AI research generation. <a href="https://www.anthropic.com/privacy" target="_blank">Privacy policy</a></li>
  <li><strong>Stripe</strong> — Payment processing. <a href="https://stripe.com/privacy" target="_blank">Privacy policy</a></li>
  <li><strong>Railway</strong> — Application hosting. <a href="https://railway.app/legal/privacy" target="_blank">Privacy policy</a></li>
  <li><strong>GitHub</strong> — Data persistence (private Gist). <a href="https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement" target="_blank">Privacy policy</a></li>
  <li><strong>Google Fonts</strong> — Typography. <a href="https://policies.google.com/privacy" target="_blank">Privacy policy</a></li>
</ul>

<h2>5. Your Rights (GDPR)</h2>
<p>If you are in the EU/EEA, you have the following rights:</p>
<ul>
  <li><strong>Access:</strong> Request a copy of your personal data</li>
  <li><strong>Rectification:</strong> Correct inaccurate data</li>
  <li><strong>Erasure:</strong> Request deletion of your data ("right to be forgotten")</li>
  <li><strong>Portability:</strong> Receive your data in a portable format</li>
  <li><strong>Objection:</strong> Object to processing of your data</li>
  <li><strong>Restriction:</strong> Request restriction of processing</li>
</ul>
<p>To exercise any of these rights, email <a href="mailto:hello@scout.so">hello@scout.so</a>. We will respond within 30 days.</p>

<h2>6. Cookies</h2>
<p>Scout does not use tracking cookies. We use browser localStorage for storing your session preferences and lead data. This data is stored locally on your device and is not transmitted to advertising networks.</p>

<h2>7. Data Retention</h2>
<p>We retain your personal data for as long as your account is active. If you delete your account, we will delete your personal data within 30 days, except where we are required by law to retain it (e.g. billing records, which are retained for 7 years for tax purposes).</p>

<h2>8. Children's Privacy</h2>
<p>Scout is not directed at children under 18. We do not knowingly collect personal information from children. If you believe a child has provided us with personal information, contact us and we will delete it.</p>

<h2>9. Changes to This Policy</h2>
<p>We may update this Privacy Policy periodically. We will notify active subscribers of material changes by email at least 14 days before they take effect. Continued use of the Service constitutes acceptance.</p>

<h2>10. Contact &amp; Data Controller</h2>
<p><strong>Data Controller:</strong> Sushicat Ventures<br>
<strong>Email:</strong> <a href="mailto:hello@scout.so">hello@scout.so</a><br>
<strong>Location:</strong> Madrid, Spain</p>

</div>

<div style="margin-top:64px;padding-top:32px;border-top:1px solid var(--bor);font-size:12px;color:var(--tx3);text-align:center">
  Scout · Sushicat Ventures · Madrid, Spain · <a href="mailto:hello@scout.so">hello@scout.so</a>
</div>

</div>
</body>
</html>
'''


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
