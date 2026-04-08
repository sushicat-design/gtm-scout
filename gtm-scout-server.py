#!/usr/bin/env python3
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
                if isinstance(data, list) and len(data) > 0:
                    # Only skip if it's literally just the init placeholder
                    if len(data) == 1 and data[0].get('init') == True:
                        print('[DB] Gist has placeholder data, returning empty')
                    else:
                        print('[DB] Loaded', len(data), 'records from GitHub Gist')
                        return data
                else:
                    print('[DB] Gist empty or invalid')
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

/* ── RESET ── */
*{box-sizing:border-box;margin:0;padding:0}

/* ── DESIGN TOKENS ── */
:root{
  --bg:#020408;
  --sur:#060c14;
  --sur2:#0a1220;
  --sur3:#0f1a2e;
  --bor:rgba(45,157,232,0.1);
  --bor2:rgba(45,157,232,0.18);
  --bor3:rgba(45,157,232,0.3);
  --pip:#2d9de8;
  --pip2:#5bc4f5;
  --pip-dim:rgba(45,157,232,0.06);
  --pip-bor:rgba(45,157,232,0.22);
  --pip-glow:rgba(45,157,232,0.4);
  --pip-deep:#1565c0;
  --amb:#f59e0b;
  --red:#ef4444;
  --grn:#10b981;
  --tx:#e8f4fd;
  --tx2:#7da8c8;
  --tx3:#2a4a6a;
  --r:10px;
  --r-sm:6px;
  --r-pill:4px;
  --glow-sm:0 0 16px rgba(45,157,232,0.15);
  --glow-md:0 0 32px rgba(45,157,232,0.2);
  --glow-lg:0 0 64px rgba(45,157,232,0.25);
  --shadow:0 4px 24px rgba(0,0,0,0.6);
  --shadow-lg:0 12px 48px rgba(0,0,0,0.8);
}

/* ── BODY with animated gradient mesh ── */
body{
  background:var(--bg);
  color:var(--tx);
  font-family:'Outfit',sans-serif;
  font-size:13px;
  line-height:1.65;
  font-weight:400;
  -webkit-font-smoothing:antialiased;
  min-height:100vh;
  position:relative;
  overflow-x:hidden;
}

/* Animated ambient orbs */
body::before{
  content:'';
  position:fixed;top:-20vh;left:-10vw;
  width:60vw;height:60vh;
  background:radial-gradient(ellipse,rgba(45,157,232,0.07) 0%,transparent 65%);
  pointer-events:none;z-index:0;
  animation:orb1 12s ease-in-out infinite alternate;
}
body::after{
  content:'';
  position:fixed;bottom:-20vh;right:-10vw;
  width:50vw;height:50vh;
  background:radial-gradient(ellipse,rgba(91,196,245,0.05) 0%,transparent 65%);
  pointer-events:none;z-index:0;
  animation:orb2 15s ease-in-out infinite alternate;
}
@keyframes orb1{
  0%{transform:translate(0,0) scale(1);}
  100%{transform:translate(5vw,3vh) scale(1.1);}
}
@keyframes orb2{
  0%{transform:translate(0,0) scale(1);}
  100%{transform:translate(-4vw,-2vh) scale(1.08);}
}

/* ── SCANLINE TEXTURE overlay ── */
.page,.topbar,.sidebar{position:relative;z-index:1}

/* ── TOPBAR ── */
.topbar{
  display:flex;align-items:center;padding:0 24px;height:52px;
  border-bottom:1px solid var(--bor);
  position:sticky;top:0;z-index:100;
  background:rgba(2,4,8,0.9);
  backdrop-filter:blur(20px) saturate(160%);
  -webkit-backdrop-filter:blur(20px) saturate(160%);
  gap:12px;
}
.logo-btn{
  display:flex;align-items:center;gap:9px;
  background:none;border:none;cursor:pointer;
  padding:0;font-family:'Outfit',sans-serif;
  transition:opacity .2s;
}
.logo-btn:hover{opacity:.7}
.logo-mark{width:28px;height:28px;display:flex;align-items:center;justify-content:center}
.logo-text{
  font-size:13px;font-weight:700;
  letter-spacing:.2em;color:var(--tx);
  text-transform:uppercase;
}
.topbar-right{display:flex;align-items:center;gap:8px;margin-left:auto}
.save-ind{font-size:11px;color:var(--tx3);font-family:'JetBrains Mono',monospace;letter-spacing:.04em}

/* Hamburger */
.hamburger{
  background:none;border:1px solid var(--bor);
  cursor:pointer;padding:8px 10px;
  display:flex;flex-direction:column;gap:4px;
  border-radius:var(--r-sm);
  transition:all .2s;
}
.hamburger:hover{border-color:var(--pip);box-shadow:var(--glow-sm)}
.hamburger span{width:16px;height:1px;background:var(--tx2);display:block;transition:background .2s}
.hamburger:hover span{background:var(--pip2)}

/* ── SIDEBAR ── */
.sidebar-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.8);z-index:200;backdrop-filter:blur(4px)}
.sidebar-overlay.open{display:block}
.sidebar{
  position:fixed;top:0;right:0;height:100vh;width:256px;
  background:var(--sur);
  border-left:1px solid var(--bor2);
  z-index:201;transform:translateX(100%);
  transition:transform .24s cubic-bezier(.4,0,.2,1);
  display:flex;flex-direction:column;
  box-shadow:-24px 0 80px rgba(45,157,232,0.08);
}
.sidebar.open{transform:translateX(0)}
.sidebar-header{
  display:flex;align-items:center;justify-content:space-between;
  padding:16px 20px;border-bottom:1px solid var(--bor);
}
.sidebar-title{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.2em;color:var(--tx3)}
.sidebar-close{background:none;border:none;cursor:pointer;color:var(--tx3);font-size:18px;line-height:1;transition:color .2s;padding:2px 6px}
.sidebar-close:hover{color:var(--pip2)}
.sidebar-nav{display:flex;flex-direction:column;padding:8px 0;flex:1}
.sidebar-item{
  display:flex;align-items:center;justify-content:space-between;
  padding:12px 20px;cursor:pointer;border:none;
  background:none;font-family:'Outfit',sans-serif;
  font-size:13px;font-weight:500;color:var(--tx2);
  text-align:left;
  border-left:2px solid transparent;
  width:100%;transition:all .18s;
}
.sidebar-item:hover{color:var(--tx);background:var(--pip-dim)}
.sidebar-item.active{
  color:var(--pip2);
  border-left-color:var(--pip);
  background:var(--pip-dim);
}
.si-badge{
  background:var(--pip);color:#fff;
  font-size:9px;font-weight:700;
  padding:2px 7px;border-radius:var(--r-pill);
  font-family:'JetBrains Mono',monospace;
}
.leads-badge-count{font-size:10px;color:var(--tx3);font-family:'JetBrains Mono',monospace}
.sidebar-pip{padding:14px 20px;border-top:1px solid var(--bor);margin-top:auto}
.sidebar-pip-row{display:flex;align-items:center;gap:10px}
.sidebar-pip-name{font-size:13px;font-weight:600;color:var(--tx);letter-spacing:-.01em}
.sidebar-pip-sub{font-size:10px;color:var(--tx3);margin-top:1px}

/* ── PAGES ── */
.page{display:none;padding:40px 28px 80px;max-width:1160px;margin:0 auto;position:relative;z-index:1}
.page.active{display:block;animation:pageIn .3s ease}
@keyframes pageIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}

/* ── CREDITS BAR ── */
.credits-bar{
  background:var(--sur);border:1px solid var(--bor);
  border-radius:var(--r-sm);padding:8px 16px;
  display:none;align-items:center;gap:10px;
  max-width:1160px;margin:10px auto 0;position:relative;z-index:1;
}
.credits-label{font-size:10px;color:var(--tx3);font-weight:700;text-transform:uppercase;letter-spacing:.1em}
.credits-track{flex:1;height:2px;background:var(--bor2);border-radius:2px;overflow:hidden}
.credits-fill{height:100%;background:linear-gradient(90deg,var(--pip),var(--pip2));border-radius:2px;transition:width .4s ease}
.credits-count{font-size:11px;font-weight:600;color:var(--pip2);white-space:nowrap;font-family:'JetBrains Mono',monospace}

/* ── SEARCH HERO ── */
.search-hero{text-align:center;padding:40px 0 28px;position:relative}
.search-hero h1{
  font-size:48px;font-weight:700;letter-spacing:-.04em;
  margin-bottom:14px;line-height:.98;color:var(--tx);
  font-family:'Outfit',sans-serif;
}
.search-hero h1 span{
  background:linear-gradient(135deg,var(--pip2) 0%,var(--pip) 50%,#a8d8ff 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  display:inline-block;
}
.search-hero p{font-size:14px;color:var(--tx2);line-height:1.6;max-width:380px;margin:0 auto;font-weight:400}
.search-box{display:flex;gap:6px;max-width:580px;margin:24px auto 0}
#ci{
  flex:1;
  background:rgba(6,12,20,0.9);
  border:1px solid var(--bor2);color:var(--tx);
  font-family:'Outfit',sans-serif;font-size:14px;font-weight:400;
  padding:13px 20px;outline:none;border-radius:var(--r);
  transition:all .2s;
  box-shadow:inset 0 1px 0 rgba(45,157,232,0.06);
}
#ci:focus{
  border-color:var(--pip);
  box-shadow:0 0 0 3px rgba(45,157,232,0.08),var(--glow-sm);
}
#ci::placeholder{color:var(--tx3)}
#rb{
  background:var(--pip);color:#fff;border:none;
  font-weight:600;font-size:13px;padding:13px 26px;
  cursor:pointer;white-space:nowrap;
  font-family:'Outfit',sans-serif;border-radius:var(--r);
  transition:all .2s;letter-spacing:.02em;
  box-shadow:var(--glow-sm);
}
#rb:hover{background:var(--pip2);box-shadow:var(--glow-md);transform:translateY(-1px)}
#rb:active{transform:translateY(0)}
#rb:disabled{opacity:.3;cursor:not-allowed;transform:none;box-shadow:none}
.search-actions{display:none!important}
#bpanel,#ipanel,.panel-extra{display:none!important}
#ldg{display:none;align-items:center;justify-content:center;gap:10px;margin-top:18px;font-size:13px;color:var(--tx3)}
.spinner{
  width:14px;height:14px;
  border:1.5px solid var(--bor2);
  border-top-color:var(--pip);
  border-radius:50%;
  animation:spin .6s linear infinite;
}
@keyframes spin{to{transform:rotate(360deg)}}
#err{display:none;margin:12px auto;padding:12px 16px;background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.2);color:var(--red);font-size:12px;border-radius:var(--r);max-width:580px}
#ierr{display:none;color:var(--red);font-size:12px;margin-top:6px}
.sub-btn{background:var(--pip);color:#fff;border:none;font-weight:600;font-size:12px;padding:9px 18px;cursor:pointer;margin-top:8px;font-family:'Outfit',sans-serif;border-radius:var(--r-sm);box-shadow:var(--glow-sm);transition:all .2s}
.sub-btn:hover{background:var(--pip2);box-shadow:var(--glow-md)}

/* ── FETCH HERO ── */
.fetch-hero{
  text-align:center;margin:40px auto 0;
  padding:56px 44px;border:1px solid var(--bor2);
  border-radius:var(--r);background:var(--sur);
  max-width:500px;position:relative;overflow:hidden;
}
.fetch-hero::before{
  content:'';position:absolute;
  top:-60px;left:50%;transform:translateX(-50%);
  width:300px;height:200px;
  background:radial-gradient(ellipse,rgba(45,157,232,0.1) 0%,transparent 70%);
  pointer-events:none;
  animation:pulse 4s ease-in-out infinite;
}
@keyframes pulse{
  0%,100%{opacity:1;transform:translateX(-50%) scale(1);}
  50%{opacity:.6;transform:translateX(-50%) scale(1.15);}
}
.fetch-hero-title{font-size:24px;font-weight:700;letter-spacing:-.03em;margin-bottom:10px;color:var(--tx)}
.fetch-hero-sub{font-size:14px;color:var(--tx2);margin-bottom:36px;line-height:1.7}
.fetch-hero-btn{
  background:var(--pip);color:#fff;border:none;
  font-weight:700;font-size:14px;padding:13px 40px;
  cursor:pointer;font-family:'Outfit',sans-serif;
  border-radius:var(--r);transition:all .22s;
  box-shadow:var(--glow-sm);letter-spacing:.02em;
  position:relative;overflow:hidden;
}
.fetch-hero-btn::after{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,rgba(255,255,255,0.1) 0%,transparent 60%);
  opacity:0;transition:opacity .2s;
}
.fetch-hero-btn:hover{
  background:var(--pip2);
  box-shadow:var(--glow-lg);
  transform:translateY(-2px);
}
.fetch-hero-btn:hover::after{opacity:1}
.fetch-hero-btn:disabled{opacity:.3;cursor:not-allowed;transform:none;box-shadow:none}
#fetch-ldg{display:none;align-items:center;gap:8px;font-size:12px;color:var(--tx3);margin-top:16px;justify-content:center}
#fetch-err{display:none;margin-top:12px;padding:10px 14px;background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.2);color:var(--red);font-size:12px;border-radius:var(--r-sm)}
#fetch-results{display:none;margin-top:20px;padding-top:20px;border-top:1px solid var(--bor);text-align:left}
.fetch-list{display:flex;flex-direction:column;gap:3px;margin-bottom:12px;max-height:260px;overflow-y:auto}
.fetch-item{display:flex;align-items:center;gap:10px;padding:10px 14px;background:var(--sur2);border:1px solid var(--bor);cursor:pointer;border-radius:var(--r-sm);transition:all .15s}
.fetch-item:hover{border-color:var(--pip-bor);background:var(--pip-dim)}
.fetch-item.sel{border-color:var(--pip);background:var(--pip-dim);box-shadow:var(--glow-sm)}
.fetch-item input{accent-color:var(--pip);width:14px;height:14px;cursor:pointer;flex-shrink:0}
.fetch-item-name{font-size:13px;font-weight:500;color:var(--tx)}
.fetch-item-meta{font-size:10px;color:var(--tx3);margin-top:1px}
#res-sel-btn{background:var(--pip);color:#fff;border:none;font-weight:600;font-size:12px;padding:9px 18px;cursor:pointer;font-family:'Outfit',sans-serif;border-radius:var(--r-sm);box-shadow:var(--glow-sm);transition:all .2s}
#res-sel-btn:hover{background:var(--pip2);box-shadow:var(--glow-md)}
#fetch-count{font-size:11px;color:var(--tx3);margin-left:10px;font-family:'JetBrains Mono',monospace}

/* ── TOOLBAR ── */
.leads-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
.leads-header h2{font-size:20px;font-weight:600;letter-spacing:-.03em;color:var(--tx)}
.leads-toolbar{display:flex;align-items:center;gap:6px;margin-bottom:20px;flex-wrap:wrap}
.fb{font-size:11px;padding:5px 12px;background:none;border:1px solid var(--bor);color:var(--tx3);cursor:pointer;font-family:'Outfit',sans-serif;border-radius:var(--r-pill);transition:all .15s;font-weight:500}
.fb:hover{border-color:var(--pip-bor);color:var(--tx2)}
.fb.on{border-color:var(--pip);color:var(--pip2);background:var(--pip-dim);box-shadow:var(--glow-sm)}
.tb-right{margin-left:auto;display:flex;gap:6px}
.tb-btn{font-size:11px;padding:5px 12px;background:none;border:1px solid var(--bor);color:var(--tx2);cursor:pointer;font-family:'Outfit',sans-serif;border-radius:var(--r-sm);transition:all .15s;font-weight:500}
.tb-btn:hover{border-color:var(--pip-bor);color:var(--pip2)}
.tb-btn.danger{color:var(--red);border-color:rgba(239,68,68,0.15)}

/* ── LEAD CARDS — glow on hover ── */
.cards-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.lead-card{
  background:var(--sur);
  border:1px solid var(--bor);
  border-radius:var(--r);overflow:hidden;
  transition:border-color .2s,box-shadow .2s,transform .2s;
}
.lead-card:hover{
  border-color:var(--pip-bor);
  box-shadow:var(--glow-sm),0 8px 32px rgba(0,0,0,0.5);
  transform:translateY(-2px);
}
.lead-card-header{padding:16px 18px 12px;border-bottom:1px solid var(--bor)}
.lead-card-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:8px}
.lead-card-name{font-size:15px;font-weight:600;letter-spacing:-.02em;color:var(--tx);line-height:1.2}
.lead-card-score{font-size:24px;font-weight:700;letter-spacing:-.03em;line-height:1;font-family:'JetBrains Mono',monospace}
.lead-card-meta{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-top:6px}
.lead-card-tag{font-size:9px;font-weight:700;padding:2px 9px;border-radius:var(--r-pill);border:1px solid;text-transform:uppercase;letter-spacing:.08em}
.lead-card-sector{font-size:11px;color:var(--tx3)}
.lead-card-body{padding:16px 18px}
.lc-sec{font-size:8px;color:var(--tx3);text-transform:uppercase;letter-spacing:.18em;margin:12px 0 8px;display:flex;align-items:center;gap:8px;font-weight:700}
.lc-sec::after{content:'';flex:1;height:1px;background:var(--bor)}
.lc-grid{display:grid;grid-template-columns:1fr 1fr;gap:3px;margin-bottom:3px}
.lc-cell{background:var(--sur2);border:1px solid var(--bor);padding:7px 10px;border-radius:var(--r-sm)}
.lc-key{font-size:8px;color:var(--tx3);text-transform:uppercase;letter-spacing:.1em;margin-bottom:2px;font-weight:700}
.lc-val{font-size:12px;color:var(--tx)}
.lc-val a{color:var(--pip2);text-decoration:none}
.lc-val.dim{color:var(--tx3);font-style:italic}
.lc-text{font-size:12px;color:var(--tx2);line-height:1.75;margin-bottom:4px}
.sig-row{display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid var(--bor);font-size:12px}
.sig-row:last-child{border-bottom:none}
.sy{font-size:10px;font-weight:700;color:var(--grn)}
.sn{font-size:10px;font-weight:700;color:var(--red)}
.su{font-size:10px;color:var(--tx3)}
.pitch-box{
  background:var(--sur2);
  border:1px solid var(--bor2);
  border-left:2px solid var(--pip);
  padding:14px;margin-top:8px;
  border-radius:0 var(--r-sm) var(--r-sm) 0;
  position:relative;
}
.pitch-box::before{
  content:'';position:absolute;
  left:-2px;top:0;bottom:0;width:2px;
  background:linear-gradient(180deg,var(--pip),var(--pip2));
  border-radius:2px;
}
.pitch-label{font-size:8px;color:var(--pip2);text-transform:uppercase;letter-spacing:.16em;margin-bottom:8px;font-weight:700}
.pitch-text{font-size:11px;color:var(--tx2);line-height:1.85;font-family:'JetBrains Mono',monospace}
.founder-row{display:flex;gap:10px;align-items:flex-start;padding:8px 10px;background:var(--sur2);border:1px solid var(--bor);margin-bottom:4px;border-radius:var(--r-sm)}
.fav{width:28px;height:28px;border-radius:50%;background:var(--pip-dim);border:1px solid var(--pip-bor);display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:var(--pip2);flex-shrink:0;margin-top:1px}
.fname{font-size:12px;font-weight:600;color:var(--tx)}
.frole{font-size:10px;color:var(--tx3);line-height:1.5}
.social-links{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px}
.social-links a{font-size:10px;padding:3px 9px;border:1px solid var(--bor);color:var(--tx2);text-decoration:none;border-radius:var(--r-pill);transition:all .15s}
.social-links a:hover{border-color:var(--pip-bor);color:var(--pip2);box-shadow:var(--glow-sm)}
.notes-area{width:100%;background:var(--sur2);border:1px solid var(--bor);color:var(--tx);font-family:'Outfit',sans-serif;font-size:12px;padding:9px 12px;min-height:56px;resize:none;outline:none;line-height:1.6;border-radius:var(--r-sm);margin-top:4px;transition:border-color .2s}
.notes-area:focus{border-color:var(--pip-bor);box-shadow:0 0 0 2px rgba(45,157,232,0.08)}
.lead-card-actions{display:flex;gap:5px;padding:11px 16px;background:rgba(6,12,20,0.6);border-top:1px solid var(--bor);flex-wrap:wrap;align-items:center}
.abtn{font-size:11px;padding:5px 11px;background:none;border:1px solid var(--bor);color:var(--tx2);cursor:pointer;font-family:'Outfit',sans-serif;border-radius:var(--r-pill);transition:all .15s;font-weight:500}
.abtn:hover{border-color:var(--pip-bor);color:var(--pip2);box-shadow:var(--glow-sm)}
.abtn.g{border-color:var(--pip-bor);color:var(--pip2);background:var(--pip-dim)}
.abtn.g:hover{background:rgba(45,157,232,0.12);box-shadow:var(--glow-sm)}
.abtn.ghost{margin-left:auto;color:var(--tx3);border-color:transparent}
.abtn.ghost:hover{color:var(--red)}
.hiring-badge{font-size:9px;color:var(--pip2);border:1px solid var(--pip-bor);padding:2px 7px;font-weight:700;border-radius:var(--r-pill)}
.empty{text-align:center;padding:80px 20px;color:var(--tx3)}
.empty-title{font-size:18px;font-weight:600;color:var(--tx2);margin-bottom:10px;letter-spacing:-.02em}
.empty p{font-size:13px;line-height:2}

/* ── PIPELINE ── */
.pipeline-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px}
.pipeline-header h2{font-size:20px;font-weight:600;letter-spacing:-.02em;color:var(--tx)}
.pipeline-board{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;align-items:start}
.pipeline-col{background:var(--sur);border:1px solid var(--bor);padding:12px;border-radius:var(--r)}
.pipeline-col-header{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.16em;padding-bottom:10px;border-bottom:1px solid var(--bor);margin-bottom:8px;display:flex;align-items:center;justify-content:space-between}
.pipeline-card{background:var(--sur2);border:1px solid var(--bor);padding:12px 13px;margin-bottom:6px;cursor:pointer;transition:all .2s;border-radius:var(--r-sm)}
.pipeline-card:hover{border-color:var(--pip-bor);box-shadow:var(--glow-sm);transform:translateY(-1px)}
.pipeline-card-name{font-size:12px;font-weight:600;margin-bottom:3px;color:var(--tx);letter-spacing:-.01em}
.pipeline-card-meta{font-size:10px;color:var(--tx3)}
.pipeline-card-note{font-size:10px;color:var(--tx3);font-style:italic;margin-top:5px;line-height:1.5}
.pipeline-card-date{font-size:10px;color:var(--amb);margin-top:3px;font-weight:600}
.pipeline-empty{font-size:11px;color:var(--tx3);text-align:center;padding:24px 0}

/* ── INBOX ── */
.inbox-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:24px}
.inbox-header h2{font-size:20px;font-weight:600;letter-spacing:-.02em;color:var(--tx)}
.inbox-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.inbox-card{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);overflow:hidden;transition:all .2s}
.inbox-card:hover{border-color:var(--pip-bor);box-shadow:var(--glow-sm);transform:translateY(-1px)}
.inbox-card-header{padding:16px 18px 12px}
.inbox-card-name{font-size:15px;font-weight:600;letter-spacing:-.02em;margin-bottom:4px;color:var(--tx)}
.inbox-card-meta{font-size:11px;color:var(--tx3);margin-bottom:8px}
.inbox-card-body{padding:0 18px 14px;font-size:12px;color:var(--tx2);line-height:1.75}
.inbox-card-actions{display:flex;gap:8px;padding:12px 16px;background:rgba(6,12,20,0.5);border-top:1px solid var(--bor)}
.btn-approve{flex:1;background:var(--pip);color:#fff;border:none;font-weight:700;font-size:12px;padding:10px;cursor:pointer;font-family:'Outfit',sans-serif;border-radius:var(--r-sm);transition:all .2s;box-shadow:var(--glow-sm)}
.btn-approve:hover{background:var(--pip2);box-shadow:var(--glow-md);transform:translateY(-1px)}
.btn-dismiss{flex:1;background:none;color:var(--tx3);border:1px solid var(--bor);font-weight:500;font-size:12px;padding:10px;cursor:pointer;font-family:'Outfit',sans-serif;border-radius:var(--r-sm);transition:all .2s}
.btn-dismiss:hover{border-color:rgba(239,68,68,0.3);color:var(--red)}
.inbox-empty{text-align:center;padding:80px 20px;color:var(--tx3)}
.inbox-empty-title{font-size:18px;font-weight:600;color:var(--tx2);margin-bottom:10px}

/* ── PROFILE ── */
.profile-layout{display:grid;grid-template-columns:280px 1fr;gap:20px;align-items:start}
.profile-sidebar{display:flex;flex-direction:column;gap:14px}
.profile-card{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);padding:24px}
.profile-avatar-wrap{position:relative;width:80px;height:80px;margin:0 auto 16px}
.profile-avatar{width:80px;height:80px;border-radius:50%;background:var(--sur2);border:1px solid var(--pip-bor);display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:700;color:var(--pip2);box-shadow:var(--glow-sm)}
.profile-avatar img{width:100%;height:100%;border-radius:50%;object-fit:cover}
.profile-avatar-edit{position:absolute;bottom:0;right:0;width:22px;height:22px;background:var(--pip);border:none;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:10px;color:#fff;transition:all .2s}
.profile-avatar-edit:hover{background:var(--pip2);box-shadow:var(--glow-sm)}
.profile-name{font-size:18px;font-weight:600;letter-spacing:-.02em;text-align:center;margin-bottom:4px;color:var(--tx)}
.profile-tagline{font-size:12px;color:var(--tx3);text-align:center;line-height:1.6;margin-bottom:14px}
.profile-socials{display:flex;gap:5px;justify-content:center;flex-wrap:wrap;margin-bottom:16px}
.profile-social-link{font-size:11px;padding:3px 10px;border:1px solid var(--bor);color:var(--tx2);text-decoration:none;border-radius:var(--r-pill);transition:all .15s}
.profile-social-link:hover{border-color:var(--pip-bor);color:var(--pip2);box-shadow:var(--glow-sm)}
.profile-stat-row{display:flex;justify-content:space-around;padding:12px 0;border-top:1px solid var(--bor)}
.profile-stat{text-align:center}
.profile-stat-n{font-size:22px;font-weight:700;color:var(--pip2);letter-spacing:-.02em;line-height:1;font-family:'JetBrains Mono',monospace}
.profile-stat-l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.12em;margin-top:3px;font-weight:700}
.profile-edit-btn{width:100%;background:none;border:1px solid var(--bor2);color:var(--tx2);font-family:'Outfit',sans-serif;font-size:12px;font-weight:500;padding:9px;border-radius:var(--r-sm);cursor:pointer;transition:all .2s}
.profile-edit-btn:hover{border-color:var(--pip-bor);color:var(--pip2);box-shadow:var(--glow-sm)}
.profile-share-btn{width:100%;background:var(--pip);color:#fff;border:none;font-family:'Outfit',sans-serif;font-size:12px;font-weight:600;padding:9px;border-radius:var(--r-sm);cursor:pointer;transition:all .2s;margin-top:6px;box-shadow:var(--glow-sm)}
.profile-share-btn:hover{background:var(--pip2);box-shadow:var(--glow-md);transform:translateY(-1px)}
.service-item{display:flex;align-items:center;gap:10px;padding:9px 12px;background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r-sm);transition:all .2s}
.service-item:hover{border-color:var(--pip-bor);box-shadow:var(--glow-sm)}
.service-icon{font-size:16px;flex-shrink:0}
.service-name{font-size:12px;font-weight:600;color:var(--tx)}
.service-desc{font-size:11px;color:var(--tx3);margin-top:1px}
.profile-main{display:flex;flex-direction:column;gap:16px}
.profile-section{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);padding:24px}
.profile-section-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px}
.profile-section-title{font-size:14px;font-weight:600;letter-spacing:-.01em;color:var(--tx)}
.profile-add-btn{background:none;border:1px solid var(--pip-bor);color:var(--pip2);font-family:'Outfit',sans-serif;font-size:11px;font-weight:600;padding:5px 12px;border-radius:var(--r-pill);cursor:pointer;transition:all .2s}
.profile-add-btn:hover{background:var(--pip-dim);box-shadow:var(--glow-sm)}
.case-studies-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.case-card{background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r-sm);padding:16px;transition:all .2s;cursor:pointer}
.case-card:hover{border-color:var(--pip-bor);box-shadow:var(--glow-sm);transform:translateY(-1px)}
.case-card-client{font-size:10px;color:var(--pip2);font-weight:700;text-transform:uppercase;letter-spacing:.12em;margin-bottom:6px}
.case-card-title{font-size:13px;font-weight:600;letter-spacing:-.01em;margin-bottom:7px;color:var(--tx)}
.case-card-result{font-size:12px;color:var(--tx2);line-height:1.65;margin-bottom:10px}
.case-metrics{display:flex;gap:5px;flex-wrap:wrap}
.case-metric{background:var(--pip-dim);border:1px solid var(--pip-bor);border-radius:var(--r-pill);padding:2px 9px;font-size:11px;font-weight:700;color:var(--pip2)}
.case-card-add{background:none;border:1px dashed var(--bor2);color:var(--tx3);display:flex;align-items:center;justify-content:center;gap:8px;font-family:'Outfit',sans-serif;font-size:12px;font-weight:500;padding:32px;border-radius:var(--r-sm);cursor:pointer;transition:all .2s;width:100%}
.case-card-add:hover{border-color:var(--pip-bor);color:var(--pip2);box-shadow:var(--glow-sm)}

/* ── PIP HUNT ── */
.ph-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.ph-header h2{font-size:20px;font-weight:600;letter-spacing:-.02em;color:var(--tx);display:flex;align-items:center;gap:8px}
.ph-tabs{display:flex;gap:2px;margin-bottom:20px;border-bottom:1px solid var(--bor)}
.ph-tab{padding:8px 18px;font-size:12px;font-weight:500;color:var(--tx3);cursor:pointer;border:none;background:none;font-family:'Outfit',sans-serif;border-bottom:2px solid transparent;transition:all .18s;margin-bottom:-1px}
.ph-tab:hover{color:var(--tx2)}
.ph-tab.active{color:var(--pip2);border-bottom-color:var(--pip)}
.ph-controls{display:flex;align-items:center;gap:6px;margin-bottom:20px;flex-wrap:wrap}
.ph-filter{font-size:11px;padding:5px 12px;background:none;border:1px solid var(--bor);color:var(--tx3);cursor:pointer;font-family:'Outfit',sans-serif;border-radius:var(--r-pill);transition:all .18s;font-weight:500}
.ph-filter:hover{border-color:var(--pip-bor);color:var(--tx2)}
.ph-filter.on{border-color:var(--pip);color:var(--pip2);background:var(--pip-dim);box-shadow:var(--glow-sm)}
.ph-fetch-btn{background:var(--pip);color:#fff;border:none;font-weight:600;font-size:12px;padding:8px 18px;cursor:pointer;font-family:'Outfit',sans-serif;border-radius:var(--r);transition:all .2s;margin-left:auto;box-shadow:var(--glow-sm)}
.ph-fetch-btn:hover{background:var(--pip2);box-shadow:var(--glow-md);transform:translateY(-1px)}
.ph-fetch-btn:disabled{opacity:.3;cursor:not-allowed;transform:none;box-shadow:none}
.ph-status{font-size:11px;color:var(--tx3);margin-left:8px}
.ph-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.ph-card{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);overflow:hidden;transition:all .2s}
.ph-card:hover{border-color:var(--pip-bor);box-shadow:var(--glow-sm);transform:translateY(-1px)}
.ph-card.saved{border-color:var(--pip-bor);background:var(--pip-dim)}
.ph-card-header{padding:16px 18px 12px}
.ph-card-role{font-size:14px;font-weight:600;letter-spacing:-.01em;color:var(--tx);margin-bottom:4px}
.ph-card-company{font-size:12px;font-weight:600;color:var(--pip2);margin-bottom:4px}
.ph-card-meta{display:flex;gap:5px;flex-wrap:wrap;margin-top:6px}
.ph-tag{font-size:9px;font-weight:600;padding:2px 8px;border-radius:var(--r-pill);border:1px solid var(--bor);color:var(--tx3)}
.ph-tag.remote{border-color:var(--pip-bor);color:var(--pip2)}
.ph-tag.salary{border-color:rgba(245,158,11,0.25);color:var(--amb)}
.ph-tag.new{border-color:rgba(16,185,129,0.25);color:var(--grn)}
.ph-card-body{padding:0 18px 14px}
.ph-desc{font-size:12px;color:var(--tx2);line-height:1.75;margin-bottom:10px}
.ph-apply{display:flex;align-items:center;gap:8px;padding:9px 12px;background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r-sm);margin-bottom:7px}
.ph-apply-method{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--tx3);min-width:44px}
.ph-apply-link{font-size:11px;color:var(--pip2);text-decoration:none;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.ph-card-actions{display:flex;gap:5px;padding:11px 16px;background:rgba(6,12,20,0.5);border-top:1px solid var(--bor);flex-wrap:wrap}
.ph-saved-list h3{font-size:14px;font-weight:600;letter-spacing:-.01em;margin-bottom:14px;color:var(--tx2)}
.ph-empty{text-align:center;padding:80px 20px;color:var(--tx3)}
.ph-empty-title{font-size:18px;font-weight:600;color:var(--tx2);margin-bottom:8px}

/* ── MODALS ── */
.modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.88);z-index:1000;align-items:center;justify-content:center;backdrop-filter:blur(8px)}
.modal-overlay.open{display:flex}
.modal{background:var(--sur);border:1px solid var(--bor2);border-radius:var(--r);padding:28px;width:100%;max-width:520px;max-height:88vh;overflow-y:auto;box-shadow:var(--shadow-lg),var(--glow-sm);animation:pageIn .22s ease}
.modal-title{font-size:17px;font-weight:600;letter-spacing:-.02em;margin-bottom:20px;color:var(--tx)}
.modal-field{margin-bottom:13px}
.modal-label{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.16em;font-weight:700;margin-bottom:5px;display:block}
.modal-input{width:100%;background:var(--sur2);border:1px solid var(--bor2);color:var(--tx);font-family:'Outfit',sans-serif;font-size:13px;padding:10px 14px;outline:none;border-radius:var(--r-sm);transition:all .2s}
.modal-input:focus{border-color:var(--pip);box-shadow:0 0 0 2px rgba(45,157,232,0.1)}
.modal-textarea{min-height:80px;resize:vertical}
.modal-actions{display:flex;gap:7px;margin-top:20px;justify-content:flex-end}
.modal-save{background:var(--pip);color:#fff;border:none;font-family:'Outfit',sans-serif;font-weight:600;font-size:13px;padding:10px 22px;border-radius:var(--r-sm);cursor:pointer;transition:all .2s;box-shadow:var(--glow-sm)}
.modal-save:hover{background:var(--pip2);box-shadow:var(--glow-md)}
.modal-cancel{background:none;border:1px solid var(--bor2);color:var(--tx2);font-family:'Outfit',sans-serif;font-weight:500;font-size:13px;padding:10px 22px;border-radius:var(--r-sm);cursor:pointer;transition:all .2s}
.modal-cancel:hover{border-color:var(--pip-bor);color:var(--pip2)}

/* ── PRICING ── */
.pricing-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.92);z-index:300;align-items:center;justify-content:center;backdrop-filter:blur(10px)}
.pricing-overlay.open{display:flex}
.pricing-modal{background:var(--sur);border:1px solid var(--bor2);border-radius:var(--r);padding:36px 32px;width:100%;max-width:780px;max-height:90vh;overflow-y:auto;box-shadow:var(--shadow-lg),var(--glow-sm);animation:pageIn .25s ease}
.pricing-title{font-size:26px;font-weight:700;letter-spacing:-.04em;text-align:center;margin-bottom:8px;color:var(--tx)}
.pricing-sub{font-size:14px;color:var(--tx3);text-align:center;margin-bottom:32px}
.pricing-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:24px}
.tier-card{background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r);padding:24px;position:relative;transition:all .2s}
.tier-card:hover{border-color:var(--pip-bor);box-shadow:var(--glow-sm)}
.tier-card.featured{border-color:var(--pip-bor);box-shadow:var(--glow-sm)}
.tier-badge{position:absolute;top:-10px;left:50%;transform:translateX(-50%);background:var(--pip);color:#fff;font-size:9px;font-weight:700;padding:3px 12px;border-radius:var(--r-pill);text-transform:uppercase;letter-spacing:.1em;white-space:nowrap;box-shadow:var(--glow-sm)}
.tier-name{font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.16em;margin-bottom:12px}
.tier-price{font-size:38px;font-weight:700;letter-spacing:-.04em;color:var(--tx);line-height:1;margin-bottom:4px;font-family:'JetBrains Mono',monospace}
.tier-price span{font-size:13px;font-weight:400;color:var(--tx3);font-family:'Outfit',sans-serif}
.tier-desc{font-size:12px;color:var(--tx3);margin-bottom:20px;line-height:1.65;min-height:36px}
.tier-features{list-style:none;margin-bottom:22px;display:flex;flex-direction:column;gap:8px}
.tier-features li{font-size:12px;color:var(--tx2);display:flex;align-items:flex-start;gap:8px;line-height:1.5}
.tier-features li::before{content:'—';color:var(--pip2);font-weight:700;flex-shrink:0}
.tier-features li.dim{color:var(--tx3)}
.tier-features li.dim::before{color:var(--tx3)}
.tier-cta{width:100%;background:var(--pip);color:#fff;border:none;font-family:'Outfit',sans-serif;font-weight:600;font-size:13px;padding:11px;border-radius:var(--r-sm);cursor:pointer;transition:all .2s;box-shadow:var(--glow-sm)}
.tier-cta:hover{background:var(--pip2);box-shadow:var(--glow-md)}
.tier-cta.outline{background:none;border:1px solid var(--bor2);color:var(--tx2);box-shadow:none}
.tier-cta.outline:hover{border-color:var(--pip-bor);color:var(--pip2);background:var(--pip-dim);box-shadow:var(--glow-sm)}
.pricing-note{font-size:11px;color:var(--tx3);text-align:center;line-height:2}
.pricing-note a{color:var(--pip2);text-decoration:none}

/* ── ONBOARDING ── */
.ob-type-btn.selected{border-color:var(--pip)!important;background:var(--pip-dim)!important;box-shadow:var(--glow-sm)!important}
.ob-type-btn:hover{border-color:var(--bor2)!important;background:var(--sur2)!important}

/* ── FOOTER ── */
footer{border-top:1px solid var(--bor);padding:20px 28px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-top:40px;position:relative;z-index:1}
footer span,footer a,footer button{font-size:11px;color:var(--tx3);text-decoration:none;font-weight:400;background:none;border:none;cursor:pointer;font-family:'Outfit',sans-serif;transition:color .15s}
footer a:hover,footer button:hover{color:var(--pip2)}

/* ── PROFILE PAGE REBUILD ── */
.prof-wrap{display:grid;grid-template-columns:260px 1fr;gap:20px;align-items:start}
.prof-left{display:flex;flex-direction:column;gap:14px}
.prof-card{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);padding:24px}
.prof-avatar-wrap{position:relative;width:80px;height:80px;margin:0 auto 16px}
.prof-avatar{width:80px;height:80px;border-radius:50%;background:var(--sur2);border:1px solid var(--pip-bor);display:flex;align-items:center;justify-content:center;overflow:hidden;box-shadow:0 0 20px rgba(45,157,232,0.15)}
.prof-avatar-btn{position:absolute;bottom:0;right:0;width:22px;height:22px;background:var(--pip);border:none;border-radius:50%;cursor:pointer;color:#fff;font-size:14px;display:flex;align-items:center;justify-content:center;transition:background .2s;line-height:1}
.prof-avatar-btn:hover{background:var(--pip2)}
.prof-name{font-size:17px;font-weight:700;letter-spacing:-.02em;text-align:center;color:var(--tx);margin-bottom:4px}
.prof-tagline{font-size:12px;color:var(--tx3);text-align:center;line-height:1.5;margin-bottom:8px}
.prof-plan-badge{font-size:10px;font-weight:700;text-align:center;text-transform:uppercase;letter-spacing:.12em;margin-bottom:14px}
.prof-socials{display:flex;gap:5px;justify-content:center;flex-wrap:wrap;margin-bottom:16px}
.prof-social{font-size:11px;padding:3px 10px;border:1px solid var(--bor);color:var(--tx2);text-decoration:none;border-radius:var(--r-pill);transition:all .15s}
.prof-social:hover{border-color:var(--pip-bor);color:var(--pip2)}
.prof-stats{display:flex;justify-content:space-around;padding:14px 0;border-top:1px solid var(--bor);border-bottom:1px solid var(--bor);margin-bottom:14px}
.prof-stat{text-align:center}
.prof-stat-n{font-size:20px;font-weight:700;color:var(--pip2);font-family:'JetBrains Mono',monospace;line-height:1}
.prof-stat-l{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.1em;margin-top:3px;font-weight:600}
.prof-edit-btn{width:100%;background:none;border:1px solid var(--bor2);color:var(--tx2);font-family:'Outfit',sans-serif;font-size:12px;font-weight:500;padding:9px;border-radius:var(--r-sm);cursor:pointer;transition:all .2s;margin-bottom:6px}
.prof-edit-btn:hover{border-color:var(--pip-bor);color:var(--pip2)}
.prof-upgrade-btn{width:100%;background:var(--pip);color:#fff;border:none;font-family:'Outfit',sans-serif;font-size:12px;font-weight:600;padding:9px;border-radius:var(--r-sm);cursor:pointer;transition:all .2s;box-shadow:0 0 16px rgba(45,157,232,0.2)}
.prof-upgrade-btn:hover{background:var(--pip2);box-shadow:0 0 24px rgba(45,157,232,0.35)}
.prof-right{display:flex;flex-direction:column;gap:14px}
.prof-section{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);padding:20px 22px}
.prof-section-title{font-size:13px;font-weight:600;color:var(--tx);margin-bottom:14px;letter-spacing:-.01em}
.prof-bio{font-size:13px;color:var(--tx2);line-height:1.75}
.prof-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.prof-field{background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r-sm);padding:10px 13px}
.prof-field-label{font-size:9px;color:var(--tx3);text-transform:uppercase;letter-spacing:.12em;margin-bottom:4px;font-weight:700}
.prof-field-val{font-size:13px;color:var(--tx);font-weight:400}
.prof-tags{display:flex;flex-wrap:wrap;gap:6px}
.prof-tag{font-size:11px;color:var(--pip2);border:1px solid var(--pip-bor);background:var(--pip-dim);padding:4px 12px;border-radius:var(--r-pill);font-weight:600}
.prof-tag-add{font-size:11px;color:var(--tx3);border:1px dashed var(--bor2);background:none;padding:4px 12px;border-radius:var(--r-pill);cursor:pointer;font-family:'Outfit',sans-serif;transition:all .2s}
.prof-tag-add:hover{border-color:var(--pip-bor);color:var(--pip2)}

/* ── MOBILE ─────────────────────────────────────────────────────── */
@media(max-width:900px){
  .sidebar{transform:translateX(-100%);position:fixed;top:0;left:0;height:100vh;width:260px;z-index:300;transition:transform .25s}
  .sidebar.open{transform:translateX(0)}
  .sidebar-overlay{display:block!important}
  .app-main{margin-left:0!important;padding:16px}
  .topbar{padding:0 16px}
  .pipeline-board{grid-template-columns:1fr!important;gap:16px}
  .leads-grid{grid-template-columns:1fr!important}
  .ph-grid{grid-template-columns:1fr!important}
  .modal{max-height:90vh;overflow-y:auto;width:95vw!important;max-width:95vw!important}
  .pricing-modal{width:95vw!important;max-height:90vh;overflow-y:auto}
  .pricing-grid{grid-template-columns:1fr!important}
  .prof-wrap{grid-template-columns:1fr!important}
  .prof-grid{grid-template-columns:1fr!important}
  #rb{width:100%}
}
@media(max-width:480px){
  .lead-card-top{flex-direction:column;gap:8px}
  .topbar-title{font-size:13px}
  .sidebar{width:100vw}
}
"""

JS = """
function goHome(){window.location.href='/';}

function openProfileModal(){
  profileLoad();
  var m = document.getElementById('profile-modal');
  if(!m){ alert('Profile editor not found — please refresh.'); return; }
  var fields = ['name','email','tagline','bio','agency','role','location','experience',
    'client_size','availability','industries','funding_stage','company_size','deal_size',
    'linkedin','twitter','website','calendly','min_score'];
  fields.forEach(function(f){
    var el = document.getElementById('pm-'+f);
    if(el) el.value = PROFILE[f]||'';
  });
  m.style.cssText = 'display:flex!important;position:fixed;inset:0;background:rgba(0,0,0,0.88);z-index:9999;align-items:center;justify-content:center;backdrop-filter:blur(8px)';
}

function closeProfileModal(){
  var m = document.getElementById('profile-modal');
  if(m) m.style.cssText = 'display:none';
}

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




function saveAll() {
  var all = DB.concat(INBOX);
  fetch('/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(all)})
  .then(function(r){return r.json();})
  .then(function(d){
    var ind=document.getElementById('save-ind');
    if(ind){ind.textContent=d.ok?'saved':'save error';ind.style.color=d.ok?'var(--pip)':'var(--red)';}
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
function renderAll(){
  if(currentPage==='leads') renderLeads();
  else if(currentPage==='pipeline') renderPipelinePage();
  else if(currentPage==='inbox') renderInbox();
  else if(currentPage==='profile'){ profileLoad(); renderProfile(); }
  updateBadges();
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
    fuInput.style.cssText='background:var(--bg);border:1px solid var(--bor2);color:var(--tx2);font-family:Outfit,sans-serif;font-size:11px;padding:4px 8px;outline:none;border-radius:4px';
    fuInput.value=r._followup||'';
    (function(rec){fuInput.onchange=function(){rec._followup=fuInput.value;save();};})(r);
    fuWrap.appendChild(fuLabel);fuWrap.appendChild(fuInput);acts.appendChild(fuWrap);

    // Re-research
    var rrBtn=document.createElement('button');rrBtn.className='abtn';rrBtn.textContent='↻ Re-research';
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
      }).catch(function(e){rrBtn.textContent='↻ Re-research';rrBtn.disabled=false;});
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
        (r._followup?'<div class="pipeline-card-date"> '+r._followup+'</div>':'')+
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
  var n = (document.getElementById("ob-name")||{value:""}).value.trim();
  if(!n){ if(document.getElementById("ob-name")) document.getElementById("ob-name").focus(); return; }
  PROFILE.name = n;
  PROFILE.tagline = (document.getElementById("ob-tagline")||{value:""}).value.trim();
  PROFILE.linkedin = (document.getElementById("ob-linkedin")||{value:""}).value.trim();
  try{ localStorage.setItem("scout_profile", JSON.stringify(PROFILE)); }catch(e){}
  var sp = document.getElementById("ob-splash");
  if(sp){ sp.style.opacity="0"; setTimeout(function(){ sp.style.display="none"; },400); }
  var ov = document.getElementById("onboarding-overlay");
  if(ov) ov.classList.remove("open");
}
function onboardingSkip(){
  var sp = document.getElementById("ob-splash");
  if(sp){ sp.style.opacity="0"; setTimeout(function(){ sp.style.display="none"; },400); }
  var ov = document.getElementById("onboarding-overlay");
  if(ov) ov.classList.remove("open");
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
      var sp = document.getElementById("ob-splash");
      if(sp){ sp.style.display="flex"; setTimeout(function(){ sp.style.opacity="1"; },50); }
      var ov = document.getElementById("onboarding-overlay");
      if(ov) ov.classList.add("open");
    }
  }, 400);

  // Profile root event delegation
  document.addEventListener('click', function(e){
    if(e.target && e.target.getAttribute('data-action')==='edit-profile'){
      openProfileModal();
    }
  });
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
  var initials = PROFILE.name ? PROFILE.name.split(' ').map(function(w){return w[0]||'';}).slice(0,2).join('').toUpperCase() : '?';
  var avatarHtml = PROFILE.avatar
    ? '<img src="'+PROFILE.avatar+'" alt="avatar" style="width:100%;height:100%;border-radius:50%;object-fit:cover">'
    : '<span style="font-size:28px;font-weight:700;color:var(--pip)">'+initials+'</span>';
  var plan = (tierLoad().plan||'free');
  var planLabel = {free:'Free',pro:'Pro',agency:'Agency'}[plan]||'Free';
  var planColor = plan==='free' ? 'var(--tx3)' : 'var(--pip2)';
  var socials = '';
  if(PROFILE.linkedin) socials += '<a class="prof-social" href="'+PROFILE.linkedin+'" target="_blank">LinkedIn</a>';
  if(PROFILE.twitter) socials += '<a class="prof-social" href="'+PROFILE.twitter+'" target="_blank">Twitter/X</a>';
  if(PROFILE.website) socials += '<a class="prof-social" href="'+PROFILE.website+'" target="_blank">Website</a>';
  if(PROFILE.calendly) socials += '<a class="prof-social" href="'+PROFILE.calendly+'" target="_blank">Book a call</a>';
  var servicesHtml = (PROFILE.services_list||[]).map(function(s){
    return '<span class="prof-tag">'+s+'</span>';
  }).join('') + '<button class="prof-tag-add" onclick="profileAddService()">+ Add</button>';
  var casesHtml = (PROFILE.cases||[]).map(function(c,i){
    var metrics = (c.metrics||[]).map(function(m){return '<span class="case-metric">'+m+'</span>';}).join('');
    return '<div class="case-card" onclick="profileEditCase('+i+')">'
      +'<div class="case-card-client">'+(c.client||'Client')+'</div>'
      +'<div class="case-card-title">'+(c.title||'')+'</div>'
      +'<div class="case-card-result">'+(c.result||'')+'</div>'
      +(metrics?'<div class="case-metrics">'+metrics+'</div>':'')
      +'</div>';
  }).join('') + '<button class="case-card-add" onclick="profileAddCase()">+ Add Case Study</button>';
  cont.innerHTML =
    '<div class="prof-wrap">'+
    '<div class="prof-left">'+
      '<div class="prof-card">'+
        '<div class="prof-avatar-wrap">'+
          '<div class="prof-avatar">'+avatarHtml+'</div>'+
          '<button class="prof-avatar-btn" onclick="profileUploadAvatar()" title="Change photo">+</button>'+
          '<input type="file" id="avatar-input" accept="image/*" style="display:none" onchange="profileHandleAvatar(this)">'+
        '</div>'+
        '<div class="prof-name">'+(PROFILE.name||'Your Name')+'</div>'+
        '<div class="prof-tagline">'+(PROFILE.tagline||'Add your tagline')+'</div>'+
        '<div class="prof-plan-badge" style="color:'+planColor+'">'+planLabel+' plan</div>'+
        (socials?'<div class="prof-socials">'+socials+'</div>':'')+
        '<div class="prof-stats">'+
          '<div class="prof-stat"><div class="prof-stat-n">'+DB.length+'</div><div class="prof-stat-l">Leads</div></div>'+
          '<div class="prof-stat"><div class="prof-stat-n">'+(PROFILE.cases||[]).length+'</div><div class="prof-stat-l">Cases</div></div>'+
          '<div class="prof-stat"><div class="prof-stat-n">'+(PROFILE.services_list||[]).length+'</div><div class="prof-stat-l">Services</div></div>'+
        '</div>'+
        '<button class="prof-edit-btn" data-action="edit-profile">Edit Profile</button>'+
        '<button class="prof-edit-btn" onclick="profileCopyShare()" style="margin-top:8px;background:none;border:1px solid var(--bor2);color:var(--tx2)">Copy Share Link</button>'+
        (plan==='free'?'<button class="prof-upgrade-btn" onclick="showPricing()">Upgrade to Pro</button>':'')+
      '</div>'+
      '<div class="prof-card">'+
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:14px">'+
          '<div class="prof-section-title">Services</div>'+
        '</div>'+
        servicesHtml+
      '</div>'+
    '</div>'+
    '<div class="prof-right">'+
      '<div class="prof-section">'+
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">'+
          '<div class="prof-section-title">About</div>'+
          '<button onclick="openProfileModal()" style="background:none;border:1px solid var(--bor2);color:var(--tx2);font-size:11px;padding:4px 12px;border-radius:4px;cursor:pointer;font-family:Outfit,sans-serif">Edit</button>'+
        '</div>'+
        (PROFILE.bio?'<div style="font-size:14px;color:var(--tx2);line-height:1.8">'+PROFILE.bio+'</div>':'<div style="font-size:13px;color:var(--tx3)">Add a bio to tell prospects who you are.</div>')+
      '</div>'+
      '<div class="prof-section">'+
        '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:12px">'+
          '<div class="prof-section-title">Case Studies</div>'+
          '<button onclick="profileAddCase()" style="background:none;border:1px solid var(--bor2);color:var(--tx2);font-size:11px;padding:4px 12px;border-radius:4px;cursor:pointer;font-family:Outfit,sans-serif">+ Add</button>'+
        '</div>'+
        '<div class="case-studies-grid">'+casesHtml+'</div>'+
      '</div>'+
      '<div class="prof-section">'+
        '<div class="prof-section-title" style="margin-bottom:12px">Business Details</div>'+
        '<div class="prof-grid">'+
          '<div class="prof-field"><div class="prof-field-label">Role</div><div class="prof-field-val">'+(PROFILE.role||'—')+'</div></div>'+
          '<div class="prof-field"><div class="prof-field-label">Location</div><div class="prof-field-val">'+(PROFILE.location||'—')+'</div></div>'+
          '<div class="prof-field"><div class="prof-field-label">Industries</div><div class="prof-field-val">'+(PROFILE.industries||'—')+'</div></div>'+
          '<div class="prof-field"><div class="prof-field-label">Ideal Stage</div><div class="prof-field-val">'+(PROFILE.funding_stage||'—')+'</div></div>'+
          '<div class="prof-field"><div class="prof-field-label">Deal Size</div><div class="prof-field-val">'+(PROFILE.deal_size||'—')+'</div></div>'+
          '<div class="prof-field"><div class="prof-field-label">Availability</div><div class="prof-field-val">'+(PROFILE.availability||'—')+'</div></div>'+
        '</div>'+
      '</div>'+
    '</div>'+
    '</div>';
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
  profileLoad();
  var m=document.getElementById('profile-modal');
  if(!m){console.error('profile-modal not found');return;}
  var map={
    'pm-name':PROFILE.name,'pm-email':PROFILE.email,'pm-tagline':PROFILE.tagline,
    'pm-bio':PROFILE.bio,'pm-agency':PROFILE.agency,'pm-role':PROFILE.role,
    'pm-location':PROFILE.location,'pm-experience':PROFILE.experience,
    'pm-client_size':PROFILE.client_size,'pm-availability':PROFILE.availability,
    'pm-industries':PROFILE.industries,'pm-funding_stage':PROFILE.funding_stage,
    'pm-company_size':PROFILE.company_size,'pm-deal_size':PROFILE.deal_size,
    'pm-linkedin':PROFILE.linkedin,'pm-twitter':PROFILE.twitter,
    'pm-website':PROFILE.website,'pm-calendly':PROFILE.calendly,
    'pm-min_score':PROFILE.min_score
  };
  Object.keys(map).forEach(function(id){
    var el=document.getElementById(id);
    if(el) el.value=map[id]||'';
  });
  m.classList.add('open');
  m.style.display='flex';
}

function profileSaveInfo(){
  var fields=["name","email","tagline","bio","agency","role","location","experience",
    "client_size","availability","industries","funding_stage","company_size","deal_size",
    "linkedin","twitter","website","calendly","min_score"];
  fields.forEach(function(f){
    var el=document.getElementById("pm-"+f);
    if(el) PROFILE[f]=el.value.trim();
  });
  closeProfileModal();
  profileSave();
}





function profileAddService(){
  var name=prompt('Service name (e.g. GTM Strategy):');
  if(!name)return;
  var desc=prompt('Short description (optional):');
  var icons=['','','','','','','',''];
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

function closeCaseModal(){ document.getElementById("case-modal").classList.remove("open"); }

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
  maybeShowUpsell();
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

// Smart upsell - show after every 3rd research for free users
function showUpsellToast(msg){
  var existing = document.getElementById("upsell-toast");
  if(existing) existing.remove();
  var toast = document.createElement("div");
  toast.id = "upsell-toast";
  toast.style.cssText = "position:fixed;bottom:24px;right:24px;background:var(--sur);border:1px solid var(--pip-bor);border-radius:var(--r);padding:14px 18px;max-width:300px;z-index:500;font-size:12px;color:var(--tx2);display:flex;flex-direction:column;gap:8px";
  var span = document.createElement("span"); span.textContent = msg;
  var btn = document.createElement("button");
  btn.textContent = "Upgrade to Pro";
  btn.style.cssText = "background:var(--pip);color:#fff;border:none;font-size:11px;font-weight:700;padding:6px 12px;border-radius:4px;cursor:pointer;font-family:Outfit,sans-serif";
  btn.onclick = function(){ showPricing(); toast.remove(); };
  toast.appendChild(span); toast.appendChild(btn);
  document.body.appendChild(toast);
  setTimeout(function(){ if(toast.parentNode) toast.remove(); }, 8000);
}

function maybeShowUpsell(){
  var t = tierLoad();
  if(t.plan !== 'free') return;
  var used = t.research_used||0;
  if(used > 0 && used % 3 === 0){
    var msgs = [
      'You have used '+used+' of your 5 free researches this month.',
      'Enjoying Scout? Pro gives you unlimited research for $29/month.',
      'Running low on credits? Upgrade to Pro for unlimited access.'
    ];
    var msg = msgs[Math.min(Math.floor(used/3)-1, msgs.length-1)];
    // Show subtle toast instead of full modal
    showUpsellToast(msg);
  }
}



"""

HTML = ("<!DOCTYPE html>\n<html>\n<head>\n"
  "<meta charset='UTF-8'>\n"
  "<meta name='viewport' content='width=device-width,initial-scale=1'>\n"
  "<title>Scout</title>\n"
  "<link href='https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap' rel='stylesheet'>\n"
  "<link rel='icon' type='image/png' href='data:image/png;base64,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'>\n"
  "<style>" + CSS + "</style>\n"
  "</head>\n<body>\n"

  "<div class='topbar'>"
    "<button class='logo-btn' onclick='goHome()'>" 
      "<div class='logo-mark'><img src='data:image/png;base64,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' style='width:32px;height:32px;object-fit:contain'></div>"
      "<span class='logo-text'>Scout</span>"
    "</button>"
    "<div class='topbar-right'>"
      "<button onclick='showPricing()' id='upgrade-btn' style='background:none;border:1px solid var(--pip-bor);color:var(--pip);font-size:11px;font-weight:700;padding:5px 14px;border-radius:999px;cursor:pointer;font-family:Nunito,sans-serif'> Upgrade</button>"
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
      "<button class='sidebar-item' id='si-profile' onclick='navTo(\"profile\")'>Profile</button>"
      "<button class='sidebar-item' id='si-inbox' onclick='navTo(\"inbox\")'>Inbox<span class='si-badge' id='inbox-badge' style='display:none'>0</span></button>"
      "<button class='sidebar-item' id='si-pipeline' onclick='navTo(\"pipeline\")'>Pipeline</button>"
      "<button class='sidebar-item' id='si-leads' onclick='navTo(\"leads\")'>Saved Leads<span style='margin-left:auto;font-size:10px;color:var(--tx3);font-family:JetBrains Mono,monospace' id='leads-badge'>0</span></button>"
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
        "<div class='fetch-hero'>"
      "<div class='fetch-hero-title'> Fetch New Leads</div>"
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
      "<button class='fb' data-f='hot'> Hot</button>"
      "<button class='fb' data-f='warm'> Warm</button>"
      "<button class='fb' data-f='cold'> Cold</button>"
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
    "<div class='ph-header'><h2><img src='data:image/png;base64,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' style='width:28px;height:28px;object-fit:contain;vertical-align:middle;margin-right:8px'>Pip Hunt</h2><span style='font-size:13px;color:var(--tx3)'>Spot hiring signals. Research the company. Land the client or the role.</span></div>"
    "<div class='ph-tabs'>"
      "<button class='ph-tab active' data-cat='cmo' onclick='phSetCategory(\"cmo\")'>Client Leads — CMO Roles</button>"
      "<button class='ph-tab' data-cat='design' onclick='phSetCategory(\"design\")'>Design Leadership Roles</button>"
    "</div>"
    "<div style='background:var(--sur2);border:1px solid var(--bor2);border-radius:var(--r);padding:18px 20px;margin-bottom:20px;display:grid;grid-template-columns:1fr 1fr;gap:16px'>"
    "<div>"
      "<div style='font-size:10px;font-weight:700;color:var(--pip2);text-transform:uppercase;letter-spacing:.14em;margin-bottom:6px'>Find clients</div>"
      "<div style='font-size:13px;color:var(--tx);font-weight:600;margin-bottom:4px'>Companies hiring marketing leadership</div>"
      "<div style='font-size:12px;color:var(--tx3)'>A company posting for a CMO or Head of Marketing is a warm lead. They know they need help. Research them in Scout and pitch before someone else does.</div>"
    "</div>"
    "<div style='border-left:1px solid var(--bor);padding-left:16px'>"
      "<div style='font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.14em;margin-bottom:6px'>Find your next role</div>"
      "<div style='font-size:13px;color:var(--tx);font-weight:600;margin-bottom:4px'>CMO & marketing leader openings</div>"
      "<div style='font-size:12px;color:var(--tx3)'>Looking for your next full-time or fractional role? Pip Hunt surfaces real openings at funded companies. Save jobs, track applications, and research the company before you apply.</div>"
    "</div>"
  "</div>"
  "<div class='ph-controls'>"
      "<button class='ph-filter' data-filter='remote' onclick='phToggleFilter(\"remote\")'>Remote only</button>"
      "<button class='ph-filter' data-filter='startup' onclick='phToggleFilter(\"startup\")'>AI / Tech</button>"
      "<button class='ph-filter' data-filter='week' onclick='phToggleFilter(\"week\")'>This week</button>"
      "<button class='ph-fetch-btn' id='ph-fetch-btn' onclick='phFetch()'> Search Jobs</button>"
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
      "<div class='modal-title'> Fetch New Leads</div>"
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
          "<div style='font-size:24px;margin-bottom:8px'></div>"
          "<div style='font-size:12px;font-weight:800;color:var(--tx);margin-bottom:4px'>Agency / Freelance</div>"
          "<div style='font-size:10px;color:var(--tx3)'>Finding clients</div>"
        "</button>"
        "<button class='ob-type-btn' data-type='personal' onclick='obSelectType(\"personal\")' style='background:var(--bg);border:1px solid var(--bor2);border-radius:var(--r);padding:16px 10px;cursor:pointer;text-align:center;transition:all .2s;font-family:Nunito,sans-serif'>"
          "<div style='font-size:24px;margin-bottom:8px'></div>"
          "<div style='font-size:12px;font-weight:800;color:var(--tx);margin-bottom:4px'>Personal</div>"
          "<div style='font-size:10px;color:var(--tx3)'>Finding opportunities</div>"
        "</button>"
        "<button class='ob-type-btn' data-type='hiring' onclick='obSelectType(\"hiring\")' style='background:var(--bg);border:1px solid var(--bor2);border-radius:var(--r);padding:16px 10px;cursor:pointer;text-align:center;transition:all .2s;font-family:Nunito,sans-serif'>"
          "<div style='font-size:24px;margin-bottom:8px'></div>"
          "<div style='font-size:12px;font-weight:800;color:var(--tx);margin-bottom:4px'>Hiring</div>"
          "<div style='font-size:10px;color:var(--tx3)'>Finding candidates</div>"
        "</button>"
      "</div>"
      "<div id='ob-details' style='display:none'>"
        "<div class='modal-field'><label class='modal-label' id='ob-name-label'>Your name or agency</label><input class='modal-input' id='ob-name' placeholder='e.g. Jane Smith'></div>"
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
        "<br><a href='https://buy.stripe.com/fZu8wP4MW2u2c0Y96abjW04' target='_blank' style='font-size:10px;color:var(--tx3)'>$1 test payment</a>"
      "</div>\n"

  "<footer style='border-top:1px solid var(--bor);padding:20px 28px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-top:40px'>"
  "<span style='font-size:11px;color:var(--tx3)'>&#169; 2026 Scout</span>"
  "<div style='display:flex;gap:20px;align-items:center'>"
    "<a href='/legal#terms' target='_blank' style='font-size:11px;color:var(--tx3);text-decoration:none' onmouseover=\"this.style.color='var(--pip)'\" onmouseout=\"this.style.color='var(--tx3)'\">Terms of Service</a>"
    "<a href='/legal#privacy' target='_blank' style='font-size:11px;color:var(--tx3);text-decoration:none' onmouseover=\"this.style.color='var(--pip)'\" onmouseout=\"this.style.color='var(--tx3)'\">Privacy Policy</a>"
    "<a href='mailto:hello@scout-ai.io' style='font-size:11px;color:var(--tx3);text-decoration:none' onmouseover=\"this.style.color='var(--pip)'\" onmouseout=\"this.style.color='var(--tx3)'\">Contact</a>"
  "</div>"
"</footer>\n"
  "<div class='modal-overlay' id='profile-modal'>"
    "<div class='modal' style='max-width:600px'>"
      "<div class='modal-title'>Edit Profile</div>"
      "<div style='font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.14em;margin-bottom:12px;margin-top:4px'>Identity</div>"
      "<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px'>"
        "<div class='modal-field'><label class='modal-label'>Full Name</label><input class='modal-input' id='pm-name' placeholder='e.g. Jane Smith'></div>"
        "<div class='modal-field'><label class='modal-label'>Email</label><input class='modal-input' id='pm-email' placeholder='you@yoursite.com'></div>"
        "<div class='modal-field'><label class='modal-label'>Agency / Company</label><input class='modal-input' id='pm-agency' placeholder='Scout'></div>"
        "<div class='modal-field'><label class='modal-label'>Your Role</label><input class='modal-input' id='pm-role' placeholder='Fractional CMO'></div>"
        "<div class='modal-field'><label class='modal-label'>Location</label><input class='modal-input' id='pm-location' placeholder='New York, USA'></div>"
        "<div class='modal-field'><label class='modal-label'>Years Experience</label><input class='modal-input' id='pm-experience' placeholder='10+'></div>"
      "</div>"
      "<div class='modal-field' style='margin-top:4px'><label class='modal-label'>Tagline</label><input class='modal-input' id='pm-tagline' placeholder='Fractional CMO for AI-first startups'></div>"
      "<div class='modal-field'><label class='modal-label'>Bio</label><textarea class='modal-input modal-textarea' id='pm-bio' placeholder='Tell prospects who you are and what you do...'></textarea></div>"
      "<div style='font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.14em;margin-bottom:12px;margin-top:16px'>Ideal Client</div>"
      "<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px'>"
        "<div class='modal-field'><label class='modal-label'>Target Industries</label><input class='modal-input' id='pm-industries' placeholder='AI, SaaS, Fintech'></div>"
        "<div class='modal-field'><label class='modal-label'>Ideal Funding Stage</label><input class='modal-input' id='pm-funding_stage' placeholder='Seed – Series B'></div>"
        "<div class='modal-field'><label class='modal-label'>Ideal Company Size</label><input class='modal-input' id='pm-company_size' placeholder='10–100 employees'></div>"
        "<div class='modal-field'><label class='modal-label'>Deal Size / Rate</label><input class='modal-input' id='pm-deal_size' placeholder='$5k–$15k/mo'></div>"
        "<div class='modal-field'><label class='modal-label'>Typical Engagement</label><input class='modal-input' id='pm-client_size' placeholder='3–6 month retainers'></div>"
        "<div class='modal-field'><label class='modal-label'>Availability</label><input class='modal-input' id='pm-availability' placeholder='2 spots open Q2 2026'></div>"
      "</div>"
      "<div style='font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.14em;margin-bottom:12px;margin-top:16px'>Links</div>"
      "<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px'>"
        "<div class='modal-field'><label class='modal-label'>LinkedIn</label><input class='modal-input' id='pm-linkedin' placeholder='https://linkedin.com/in/you'></div>"
        "<div class='modal-field'><label class='modal-label'>Twitter / X</label><input class='modal-input' id='pm-twitter' placeholder='https://x.com/yourhandle'></div>"
        "<div class='modal-field'><label class='modal-label'>Website</label><input class='modal-input' id='pm-website' placeholder='https://yoursite.com'></div>"
        "<div class='modal-field'><label class='modal-label'>Book a Call (Calendly)</label><input class='modal-input' id='pm-calendly' placeholder='https://calendly.com/you'></div>"
      "</div>"
      "<div style='font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.14em;margin-bottom:12px;margin-top:16px'>Scout Settings</div>"
      "<div class='modal-field'><label class='modal-label'>Min GTM Score to show in leads (0 = show all)</label><input class='modal-input' id='pm-min_score' placeholder='0' type='number' min='0' max='100'></div>"
      "<div class='modal-actions'>"
        "<button class=\'modal-cancel\' onclick=\'closeProfileModal()\'>Cancel</button>"
        "<button class='modal-save' onclick='profileSaveInfo()'>Save changes</button>"
      "</div>"
    "</div>"
  "</div>\n"
  "<div class='modal-overlay' id='case-modal'>"
    "<div class='modal'>"
      "<input type='hidden' id='cm-idx' value='-1'>"
      "<div class='modal-title'>Case Study</div>"
      "<div class='modal-field'><label class='modal-label'>Client Name</label><input class='modal-input' id='cm-client' placeholder='Acme Inc (or keep anonymous)'></div>"
      "<div class='modal-field'><label class='modal-label'>What you did</label><input class='modal-input' id='cm-title' placeholder='Built GTM from zero to Series B'></div>"
      "<div class='modal-field'><label class='modal-label'>Result / Impact</label><textarea class='modal-input modal-textarea' id='cm-result' placeholder='Describe the outcome...'></textarea></div>"
      "<div class='modal-field'><label class='modal-label'>Key Metrics (comma separated)</label><input class='modal-input' id='cm-metrics' placeholder='3x pipeline, $2M ARR, 40% CAC reduction'></div>"
      "<div class='modal-actions'>"
        "<button class='modal-cancel' onclick=\"document.getElementById('case-modal').classList.remove('open')\">Cancel</button>"
        "<button class='modal-cancel' onclick='profileDeleteCase()' style='color:var(--red);border-color:rgba(239,68,68,0.2)'>Delete</button>"
        "<button class='modal-save' onclick='profileSaveCase()'>Save</button>"
      "</div>"
    "</div>"
  "</div>\n"

  "<script>" + JS + "</script>\n"
  "</body>\n</html>\n")

LANDING_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scout — Find your next client</title>
<link rel="icon" type="image/png" href="data:image/png;base64,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">
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#020408;--sur:#060c14;--sur2:#0a1220;--pip:#2d9de8;--pip2:#5bc4f5;--pip3:#a8d8ff;--bor:rgba(45,157,232,0.1);--bor2:rgba(45,157,232,0.2);--tx:#eef4ff;--tx2:#7da8c8;--tx3:#2a4a6a;--grn:#10b981;--amb:#f59e0b;--red:#ef4444}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--tx);font-family:'Outfit',sans-serif;overflow-x:hidden;-webkit-font-smoothing:antialiased}
.orb{position:fixed;border-radius:50%;pointer-events:none;z-index:0;filter:blur(60px)}
.o1{width:800px;height:600px;top:-200px;left:-200px;background:radial-gradient(ellipse,rgba(45,157,232,0.08) 0%,transparent 70%);animation:o1 14s ease-in-out infinite alternate}
.o2{width:600px;height:500px;bottom:-150px;right:-150px;background:radial-gradient(ellipse,rgba(91,196,245,0.06) 0%,transparent 70%);animation:o2 18s ease-in-out infinite alternate}
@keyframes o1{to{transform:translate(80px,50px) scale(1.12)}}
@keyframes o2{to{transform:translate(-60px,-40px) scale(1.08)}}
.grid{position:fixed;inset:0;z-index:0;opacity:.025;background-image:linear-gradient(var(--pip) 1px,transparent 1px),linear-gradient(90deg,var(--pip) 1px,transparent 1px);background-size:64px 64px}
nav{position:fixed;top:0;left:0;right:0;z-index:200;height:60px;display:flex;align-items:center;padding:0 48px;border-bottom:1px solid var(--bor);background:rgba(2,4,8,0.88);backdrop-filter:blur(20px)}
.nlogo{font-size:12px;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:var(--tx);display:flex;align-items:center;gap:10px;text-decoration:none}
.ndot{width:7px;height:7px;border-radius:50%;background:var(--pip);animation:ndot 2s ease-in-out infinite}
@keyframes ndot{0%,100%{box-shadow:0 0 8px var(--pip)}50%{box-shadow:0 0 22px var(--pip2),0 0 40px rgba(45,157,232,0.3)}}
.nlinks{display:flex;gap:32px;margin-left:auto;align-items:center}
.nlink{font-size:13px;color:var(--tx2);text-decoration:none;transition:color .18s}.nlink:hover{color:var(--tx)}
.ncta{background:var(--pip);color:#fff;border:none;font-family:'Outfit',sans-serif;font-size:13px;font-weight:600;padding:9px 22px;border-radius:6px;cursor:pointer;text-decoration:none;display:inline-flex;letter-spacing:.02em;transition:all .18s}
.ncta:hover{background:var(--pip2);transform:translateY(-1px)}
.hero{position:relative;z-index:1;min-height:100vh;display:grid;grid-template-columns:1fr 500px;align-items:center;padding:100px 48px 60px;gap:60px;max-width:1240px;margin:0 auto}
.eyebrow{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--bor2);border-radius:4px;padding:6px 14px;font-size:10px;font-weight:700;color:var(--pip2);letter-spacing:.14em;text-transform:uppercase;margin-bottom:28px;background:rgba(45,157,232,0.05)}
h1{font-size:76px;font-weight:800;letter-spacing:-.05em;line-height:.9;color:var(--tx);margin-bottom:24px}
h1 em{font-style:normal;background:linear-gradient(135deg,var(--pip2),var(--pip),var(--pip3));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.sub{font-size:17px;color:var(--tx2);line-height:1.65;max-width:460px;margin-bottom:40px}
.actions{display:flex;gap:12px;margin-bottom:56px;flex-wrap:wrap}
.btnp{background:var(--pip);color:#fff;border:none;font-family:'Outfit',sans-serif;font-size:15px;font-weight:600;padding:15px 34px;border-radius:8px;cursor:pointer;text-decoration:none;display:inline-flex;box-shadow:0 0 32px rgba(45,157,232,0.3);transition:all .2s}
.btnp:hover{background:var(--pip2);box-shadow:0 0 56px rgba(45,157,232,0.5);transform:translateY(-2px)}
.btng{background:none;color:var(--tx2);border:1px solid var(--bor2);font-family:'Outfit',sans-serif;font-size:15px;font-weight:500;padding:15px 34px;border-radius:8px;cursor:pointer;text-decoration:none;display:inline-flex;transition:all .2s}
.btng:hover{border-color:var(--pip);color:var(--tx)}
.stats{display:flex;gap:40px}
.stat{border-left:1px solid var(--bor2);padding-left:20px}
.stn{font-size:28px;font-weight:700;color:var(--tx);font-family:'JetBrains Mono',monospace;line-height:1}
.stn span{color:var(--pip2)}
.stl{font-size:11px;color:var(--tx3);margin-top:4px;font-weight:500;text-transform:uppercase;letter-spacing:.1em}
/* Demo widget */
.dw{background:#060c14;border-radius:14px;overflow:hidden;border:1px solid rgba(45,157,232,0.2);box-shadow:0 0 80px rgba(45,157,232,0.08),0 24px 64px rgba(0,0,0,0.6)}
.dw-bar{background:#0a1220;padding:13px 18px;display:flex;align-items:center;gap:7px;border-bottom:1px solid rgba(45,157,232,0.08)}
.dw-dot{width:10px;height:10px;border-radius:50%}
.dw-lbl{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx3);margin-left:8px;letter-spacing:.04em}
.dw-search{padding:16px 20px;display:flex;align-items:center;gap:12px;border-bottom:1px solid rgba(45,157,232,0.07)}
.dw-icon{width:16px;height:16px;border:1.5px solid var(--pip);border-radius:50%;position:relative;flex-shrink:0}
.dw-icon::after{content:'';position:absolute;bottom:-4px;right:-3px;width:5px;height:1.5px;background:var(--pip);transform:rotate(45deg);border-radius:1px}
.dw-input{font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--tx);flex:1}
.dw-cur{display:inline-block;width:2px;height:13px;background:var(--pip);margin-left:1px;vertical-align:middle;animation:cur .8s step-end infinite}
@keyframes cur{0%,100%{opacity:1}50%{opacity:0}}
.dw-scanning{padding:12px 20px;border-bottom:1px solid rgba(45,157,232,0.07)}
.dw-scan-row{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.dw-scan-dot{width:6px;height:6px;border-radius:50%;background:var(--pip);animation:sdot 1.2s ease-in-out infinite;flex-shrink:0}
@keyframes sdot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.3;transform:scale(.6)}}
.dw-scan-txt{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx3)}
.dw-prog{height:2px;background:rgba(45,157,232,0.08);border-radius:1px;overflow:hidden}
.dw-prog-fill{height:100%;background:linear-gradient(90deg,var(--pip),var(--pip2));border-radius:1px;width:0;transition:width .35s ease}
.dw-res{padding:20px}
.dw-res-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:12px}
.dw-name{font-size:17px;font-weight:700;color:var(--tx);letter-spacing:-.02em;margin-bottom:3px}
.dw-meta{font-size:11px;color:var(--tx3)}
.dw-score{font-family:'JetBrains Mono',monospace;font-size:52px;font-weight:700;color:var(--pip2);line-height:1;letter-spacing:-.04em;text-align:right}
.dw-tag{font-size:9px;font-weight:700;color:var(--pip2);letter-spacing:.12em;text-transform:uppercase;text-align:right;margin-top:2px}
.dw-scorebar{height:2px;background:rgba(45,157,232,0.1);border-radius:1px;margin-bottom:16px;overflow:hidden}
.dw-scorebar-fill{height:100%;background:linear-gradient(90deg,var(--pip),var(--pip2));border-radius:1px;width:0;transition:width 1.2s cubic-bezier(.4,0,.2,1)}
.dw-sigs{display:flex;flex-direction:column;gap:7px;margin-bottom:14px}
.dw-sig{display:flex;align-items:center;gap:9px;font-size:12px;color:var(--tx2);font-family:'Outfit',sans-serif;opacity:0;transform:translateX(-5px);transition:opacity .35s,transform .35s}
.dw-sig.on{opacity:1;transform:translateX(0)}
.dw-sigdot{width:5px;height:5px;border-radius:50%;flex-shrink:0}
.g{background:var(--grn)}.a{background:var(--amb)}
.dw-pitch{background:var(--sur2);border-left:2px solid var(--pip);padding:12px 14px;border-radius:0 6px 6px 0;opacity:0;transform:translateY(4px);transition:opacity .4s,transform .4s}
.dw-pitch.on{opacity:1;transform:translateY(0)}
.dw-pitch-lbl{font-family:'JetBrains Mono',monospace;font-size:9px;color:var(--pip2);letter-spacing:.16em;text-transform:uppercase;margin-bottom:6px}
.dw-pitch-txt{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--tx2);line-height:1.75;min-height:52px}
/* Marquee */
.mq{border-top:1px solid var(--bor);border-bottom:1px solid var(--bor);overflow:hidden;background:rgba(6,12,20,0.7);padding:14px 0;position:relative;z-index:1}
.mqt{display:flex;animation:mq 24s linear infinite;white-space:nowrap}
.mqi{font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--tx3);flex-shrink:0;padding:0 32px;display:flex;align-items:center;gap:10px;border-right:1px solid var(--bor)}
.mqd{width:4px;height:4px;border-radius:50%;background:var(--pip);flex-shrink:0}
@keyframes mq{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}
/* Sections */
.sec{position:relative;z-index:1;padding:120px 48px;max-width:1240px;margin:0 auto}
.slbl{font-size:10px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--pip2);margin-bottom:14px}
h2{font-size:52px;font-weight:700;letter-spacing:-.04em;line-height:.98;color:var(--tx);max-width:580px;margin-bottom:16px}
.ssub{font-size:16px;color:var(--tx2);line-height:1.7;max-width:460px;margin-bottom:64px}
/* Feature grid */
.fg{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--bor)}
.fc{background:var(--bg);padding:40px 32px;transition:background .2s;position:relative;overflow:hidden;cursor:default}
.fc::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--pip),transparent);transform:scaleX(0);transition:transform .5s;transform-origin:center}
.fc:hover{background:var(--sur)}.fc:hover::before{transform:scaleX(1)}
.fn{font-size:11px;font-weight:700;color:var(--tx3);letter-spacing:.12em;font-family:'JetBrains Mono',monospace;margin-bottom:20px}
.ft{font-size:20px;font-weight:600;letter-spacing:-.02em;color:var(--tx);margin-bottom:10px}
.fd{font-size:14px;color:var(--tx2);line-height:1.7}
/* Demo card */
.dw2{position:relative;z-index:1;padding:0 48px 120px;max-width:1240px;margin:0 auto}
.dc{background:var(--sur);border:1px solid var(--bor2);border-radius:12px;padding:48px;display:grid;grid-template-columns:1fr 1fr;gap:56px;align-items:start;position:relative;overflow:hidden}
.dc::before{content:'';position:absolute;top:-100px;left:50%;transform:translateX(-50%);width:400px;height:400px;background:radial-gradient(circle,rgba(45,157,232,0.06) 0%,transparent 70%);pointer-events:none}
.de{font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.16em;margin-bottom:8px}
.dn{font-size:24px;font-weight:700;letter-spacing:-.03em;color:var(--tx);margin-bottom:4px}
.dm{font-size:13px;color:var(--tx3);margin-bottom:28px}
.sc{font-size:96px;font-weight:800;letter-spacing:-.06em;line-height:1;font-family:'JetBrains Mono',monospace;background:linear-gradient(135deg,var(--pip),var(--pip2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.stag{display:inline-block;background:rgba(45,157,232,0.1);border:1px solid var(--bor2);color:var(--pip2);font-size:11px;font-weight:700;padding:4px 12px;border-radius:4px;letter-spacing:.08em;text-transform:uppercase;margin-top:4px}
.sbar{height:3px;background:var(--bor);border-radius:2px;margin:20px 0;overflow:hidden}
.sf{height:100%;background:linear-gradient(90deg,var(--pip),var(--pip2));width:87%;border-radius:2px}
.pl{font-size:9px;font-weight:700;color:var(--pip2);text-transform:uppercase;letter-spacing:.18em;margin-bottom:10px;margin-top:24px}
.pb{background:var(--sur2);border-left:2px solid var(--pip);padding:14px 16px;border-radius:0 6px 6px 0;font-size:12px;color:var(--tx2);font-family:'JetBrains Mono',monospace;line-height:1.85}
.sgl{font-size:9px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.18em;margin-bottom:14px}
.sg{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--bor);font-size:13px}.sg:last-of-type{border:none}
.sn2{color:var(--tx2)}.sgy{color:var(--grn);font-size:10px;font-weight:700;font-family:'JetBrains Mono',monospace}.sgn{color:var(--tx3);font-size:10px;font-family:'JetBrains Mono',monospace}
.fl2{font-size:9px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.18em;margin:20px 0 12px}
.fr{display:flex;gap:12px;align-items:center;background:var(--sur2);border:1px solid var(--bor);border-radius:6px;padding:10px 14px;margin-bottom:6px}
.fa{width:30px;height:30px;border-radius:50%;background:rgba(45,157,232,0.1);border:1px solid var(--bor2);display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:var(--pip2);flex-shrink:0}
/* Who its for */
.for-pills{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:24px}
.for-pill{border:1px solid var(--bor2);border-radius:6px;padding:10px 20px;font-size:13px;color:var(--tx2);background:var(--sur)}
/* Waitlist */
.wl{position:relative;z-index:1;padding:0 48px 80px;max-width:1240px;margin:0 auto}
.wl-card{background:var(--sur);border:1px solid var(--bor2);border-radius:12px;padding:56px 48px;display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center}
.wl-input{width:100%;background:var(--sur2);border:1px solid var(--bor2);color:var(--tx);font-family:'Outfit',sans-serif;font-size:14px;padding:13px 18px;outline:none;border-radius:8px;transition:border-color .2s}
.wl-input:focus{border-color:rgba(45,157,232,0.5)}
.wl-row{display:flex;gap:8px;margin-bottom:10px}
.wl-btn{background:var(--pip);color:#fff;border:none;font-family:'Outfit',sans-serif;font-size:13px;font-weight:600;padding:13px 24px;border-radius:8px;cursor:pointer;white-space:nowrap;transition:all .2s}
.wl-btn:hover{background:var(--pip2)}
/* Pricing */
.ps{position:relative;z-index:1;padding:0 48px 120px;max-width:1240px;margin:0 auto}
.pg{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.prc{background:var(--sur);border:1px solid var(--bor);border-radius:10px;padding:32px;position:relative;transition:all .2s}
.prc:hover{border-color:var(--bor2);transform:translateY(-2px)}
.prc.hot{border-color:var(--bor2);box-shadow:0 0 40px rgba(45,157,232,0.08)}
.pbdg{position:absolute;top:-10px;left:50%;transform:translateX(-50%);background:var(--pip);color:#fff;font-size:9px;font-weight:700;padding:3px 14px;border-radius:4px;letter-spacing:.1em;text-transform:uppercase;box-shadow:0 0 16px rgba(45,157,232,0.4);white-space:nowrap}
.pn{font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.16em;margin-bottom:14px}
.pp{font-size:44px;font-weight:700;color:var(--tx);letter-spacing:-.04em;line-height:1;font-family:'JetBrains Mono',monospace}
.pper{font-size:14px;color:var(--tx3);font-family:'Outfit',sans-serif;font-weight:400}
.pd{font-size:13px;color:var(--tx3);margin:12px 0 22px;line-height:1.6}
.pb2{width:100%;background:var(--pip);color:#fff;border:none;font-family:'Outfit',sans-serif;font-size:13px;font-weight:600;padding:12px;border-radius:6px;cursor:pointer;transition:all .2s;box-shadow:0 0 20px rgba(45,157,232,0.2)}
.pb2:hover{background:var(--pip2);box-shadow:0 0 32px rgba(45,157,232,0.4)}
.pb2.out{background:none;border:1px solid var(--bor2);color:var(--tx2);box-shadow:none}
.pb2.out:hover{border-color:var(--pip);color:var(--pip2)}
.pfl{list-style:none;margin-top:20px;display:flex;flex-direction:column;gap:9px}
.pfl li{font-size:13px;color:var(--tx2);display:flex;gap:8px;align-items:baseline;line-height:1.4}
.pfl li::before{content:'—';color:var(--pip2);font-weight:700;flex-shrink:0}
/* CTA */
.ctaw{position:relative;z-index:1;padding:0 48px 120px;max-width:1240px;margin:0 auto}
.ctac{background:var(--sur);border:1px solid var(--bor2);border-radius:12px;padding:80px 48px;text-align:center;position:relative;overflow:hidden}
.ctac::before{content:'';position:absolute;inset:0;background:radial-gradient(ellipse 80% 60% at 50% 50%,rgba(45,157,232,0.06) 0%,transparent 70%);pointer-events:none}
.cpip{width:90px;height:90px;object-fit:contain;margin:0 auto 24px;display:block;animation:pf 5s ease-in-out infinite;transform:translateZ(0);will-change:transform}
@keyframes pf{0%,100%{transform:translateY(0) rotate(-2deg)}50%{transform:translateY(-14px) rotate(2deg)}}
.ch2{font-size:52px;font-weight:700;letter-spacing:-.04em;line-height:.98;color:var(--tx);margin-bottom:16px}
.cs{font-size:17px;color:var(--tx2);margin-bottom:36px;line-height:1.6}
.cn{font-size:12px;color:var(--tx3);margin-top:14px}
footer{position:relative;z-index:1;padding:32px 48px;border-top:1px solid var(--bor);display:flex;align-items:center;justify-content:space-between}
.flo{font-size:11px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--tx2)}
.fls{display:flex;gap:24px}
.fl{font-size:12px;color:var(--tx3);text-decoration:none;transition:color .15s}
.fl:hover{color:var(--pip2)}

/* ── MOBILE / TABLET ───────────────────────────────────────────────── */
@media(max-width:900px){
  nav{padding:0 20px}
  .nlinks .nlink{display:none}
  .hero{grid-template-columns:1fr;padding:80px 24px 48px;gap:32px;min-height:auto}
  h1{font-size:52px}
  .sub{font-size:15px}
  .stats{gap:24px}
  .hr{display:none}
  .mq{display:none}
  .sec{padding:64px 24px}
  h2{font-size:36px}
  .fg{grid-template-columns:1fr}
  .dc{grid-template-columns:1fr;padding:28px 24px;gap:28px}
  .wl-card{grid-template-columns:1fr;padding:32px 24px;gap:24px}
  .wl-row{flex-direction:column}
  .wl-btn{width:100%}
  .pg{grid-template-columns:1fr;gap:12px}
  .ctac{padding:48px 24px}
  .ch2{font-size:36px}
  footer{flex-direction:column;gap:16px;text-align:center;padding:24px}
  .fls{flex-wrap:wrap;justify-content:center}
  .ps{padding:0 24px 64px}
  .dw2{padding:0 24px 64px}
  .wl{padding:0 24px 48px}
  .ctaw{padding:0 24px 64px}
  .for-pills{gap:8px}
  .for-pill{font-size:12px;padding:8px 14px}
}
@media(max-width:480px){
  h1{font-size:40px}
  .actions{flex-direction:column}
  .btnp,.btng{width:100%;justify-content:center}
  .stats{flex-direction:column;gap:16px}
  .ch2{font-size:28px}
}
</style>

<link rel="manifest" href="/manifest.json">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Scout">
<meta name="theme-color" content="#020408">
<link rel="apple-touch-icon" href="data:image/png;base64,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">
</head>
<body>
<div class="orb o1"></div><div class="orb o2"></div>
<div class="grid"></div>
<nav>
  <a href="/" class="nlogo"><div class="ndot"></div>Scout</a>
  <div class="nlinks">
    <a href="#features" class="nlink">Features</a>
    <a href="#pricing" class="nlink">Pricing</a>
    <a href="#waitlist" class="nlink">Early access</a>
    <a href="/app" class="ncta">Start free</a>
  </div>
</nav>

<section class="hero">
  <div>
    <div class="eyebrow"><div class="ndot" style="width:6px;height:6px;flex-shrink:0"></div>AI-powered client acquisition</div>
    <h1>Your next<br><em>best lead</em></h1>
    <p class="sub">Turn any company name into a qualified lead. Scout researches, scores, and writes your pitch opener in 8 seconds — so you spend time closing, not researching.</p>
    <div class="actions">
      <a href="/app" class="btnp">Get started free</a>
      <a href="https://calendar.app.google/xFhe41V2HMXNBzw29" target="_blank" class="btng">Book a call</a>
    </div>
    <div class="stats">
      <div class="stat"><div class="stn">8<span>s</span></div><div class="stl">To full GTM profile</div></div>
      <div class="stat"><div class="stn">0<span>–100</span></div><div class="stl">GTM Score</div></div>
      <div class="stat"><div class="stn">3<span> tiers</span></div><div class="stl">From free</div></div>
    </div>
  </div>
  <div>
    <div class="dw">
      <div class="dw-bar">
        <div class="dw-dot" style="background:#ff5f57"></div>
        <div class="dw-dot" style="background:#febc2e"></div>
        <div class="dw-dot" style="background:#28c840"></div>
        <span class="dw-lbl">scout — research</span>
      </div>
      <div class="dw-search">
        <div class="dw-icon"></div>
        <div class="dw-input"><span id="tp"></span><span class="dw-cur" id="cr"></span></div>
      </div>
      <div id="sc-wrap" style="display:none">
        <div class="dw-scanning">
          <div class="dw-scan-row"><div class="dw-scan-dot"></div><span class="dw-scan-txt" id="sc-txt">Scanning funding data...</span></div>
          <div class="dw-prog"><div class="dw-prog-fill" id="pf2"></div></div>
        </div>
      </div>
      <div class="dw-res" id="res" style="display:none">
        <div class="dw-res-top">
          <div><div class="dw-name" id="rn"></div><div class="dw-meta" id="rm"></div></div>
          <div><div class="dw-score" id="rs">0</div><div class="dw-tag" id="rt">Hot Lead</div></div>
        </div>
        <div class="dw-scorebar"><div class="dw-scorebar-fill" id="rb2"></div></div>
        <div class="dw-sigs">
          <div class="dw-sig" id="sig0"><div class="dw-sigdot g"></div><span></span></div>
          <div class="dw-sig" id="sig1"><div class="dw-sigdot g"></div><span></span></div>
          <div class="dw-sig" id="sig2"><div class="dw-sigdot g"></div><span></span></div>
          <div class="dw-sig" id="sig3"><div class="dw-sigdot a"></div><span></span></div>
        </div>
        <div class="dw-pitch" id="pt">
          <div class="dw-pitch-lbl">AI pitch opener</div>
          <div class="dw-pitch-txt" id="ptx"></div>
        </div>
      </div>
    </div>
  </div>
</section>

<div class="mq">
  <div class="mqt">
    <span class="mqi"><span class="mqd"></span>GTM Readiness Score</span><span class="mqi"><span class="mqd"></span>AI Pitch Openers</span><span class="mqi"><span class="mqd"></span>Founder Intelligence</span><span class="mqi"><span class="mqd"></span>Pipeline Kanban</span><span class="mqi"><span class="mqd"></span>Lead Fetch</span><span class="mqi"><span class="mqd"></span>Pip Hunt Jobs</span><span class="mqi"><span class="mqd"></span>Inbox Review</span><span class="mqi"><span class="mqd"></span>CSV Export</span><span class="mqi"><span class="mqd"></span>GTM Readiness Score</span><span class="mqi"><span class="mqd"></span>AI Pitch Openers</span><span class="mqi"><span class="mqd"></span>Founder Intelligence</span><span class="mqi"><span class="mqd"></span>Pipeline Kanban</span><span class="mqi"><span class="mqd"></span>Lead Fetch</span><span class="mqi"><span class="mqd"></span>Pip Hunt Jobs</span><span class="mqi"><span class="mqd"></span>Inbox Review</span><span class="mqi"><span class="mqd"></span>CSV Export</span>
  </div>
</div>

<section style="position:relative;z-index:1;padding:80px 48px 0;max-width:1240px;margin:0 auto;text-align:center">
  <p style="font-size:12px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--tx3);margin-bottom:24px">Built for</p>
  <div class="for-pills">
    <div class="for-pill">Fractional CMOs</div>
    <div class="for-pill">Marketing Agencies</div>
    <div class="for-pill">Growth Consultants</div>
    <div class="for-pill">B2B Sales Teams</div>
    <div class="for-pill">Freelance Marketers</div>
  </div>
</section>

<section class="sec" id="features">
  <div class="slbl">What Scout does</div>
  <h2>Stop researching.<br>Start closing.</h2>
  <p class="ssub">Scout does the research, scores the opportunity, and writes the opener. You just decide whether to send it.</p>
  <div class="fg">
    <div class="fc"><div class="fn">01</div><div class="ft">Know before you pitch</div><p class="fd">0–100 score based on funding stage, team gaps, hiring signals, and growth velocity. Filter time-wasters before you write a word.</p></div>
    <div class="fc"><div class="fn">02</div><div class="ft">Write itself</div><p class="fd">Scout reads the room — funding news, team gaps, recent hires — and writes a pitch opener that references something real.</p></div>
    <div class="fc"><div class="fn">03</div><div class="ft">Pipeline on autopilot</div><p class="fd">Scout scans funding databases daily. Hot companies land in your Inbox automatically — just approve or dismiss.</p></div>
    <div class="fc"><div class="fn">04</div><div class="ft">Never lose track</div><p class="fd">Kanban from Not Contacted to Closed. Every prospect in one place, every deal visible at a glance.</p></div>
    <div class="fc"><div class="fn">05</div><div class="ft">Two businesses, one tool</div><p class="fd">Pip Hunt finds companies hiring fractional CMOs and marketing leaders right now. Built right into Scout.</p></div>
    <div class="fc"><div class="fn">06</div><div class="ft">Your digital pitch deck</div><p class="fd">Build a profile with your services and case studies. Share a link with prospects before you get on a call.</p></div>
  </div>
</section>

<div class="dw2" id="demo">
  <div class="dc">
    <div>
      <div class="de">Live example</div>
      <div class="dn">Ambience Healthcare</div>
      <div class="dm">Series B · Healthcare AI · San Francisco</div>
      <div class="sc">87</div><div class="stag">Hot Lead</div>
      <div class="sbar"><div class="sf"></div></div>
      <div class="pl">AI Pitch Opener</div>
      <div class="pb">Saw the Series B — congrats. Most companies at your stage skip the CMO hire until C, but the pipeline pressure is real now. I’ve helped 3 similar healthcare SaaS teams bridge that gap and hit ARR targets within 6 months...</div>
    </div>
    <div>
      <div class="sgl">GTM Signals</div>
      <div class="sg"><span class="sn2">Recently funded</span><span class="sgy">YES</span></div>
      <div class="sg"><span class="sn2">No CMO on team</span><span class="sgy">YES</span></div>
      <div class="sg"><span class="sn2">Hiring marketing roles</span><span class="sgy">YES</span></div>
      <div class="sg"><span class="sn2">Pre-launch or early stage</span><span class="sgn">NO</span></div>
      <div class="sg"><span class="sn2">Has agency already</span><span class="sgn">NO</span></div>
      <div class="fl2">Founders</div>
      <div class="fr"><div class="fa">JK</div><div><div style="font-size:13px;font-weight:600;color:var(--tx)">James Kim</div><div style="font-size:10px;color:var(--tx3);margin-top:1px">CEO &amp; Co-founder</div></div></div>
      <div class="fr"><div class="fa">SR</div><div><div style="font-size:13px;font-weight:600;color:var(--tx)">Sara Reyes</div><div style="font-size:10px;color:var(--tx3);margin-top:1px">CTO &amp; Co-founder</div></div></div>
    </div>
  </div>

<div style="height:80px"></div>
<div class="wl" id="waitlist">
  <div class="wl-card">
    <div>
      <div class="slbl">Early access</div>
      <h2 style="font-size:40px;max-width:100%;margin-bottom:12px">Join the waitlist</h2>
      <p style="font-size:15px;color:var(--tx2);line-height:1.7">Be first to know when new features drop. No spam — just Scout updates and GTM tips from Pip.</p>
    </div>
    <div>
      <div class="wl-row">
        <input type="email" id="wl-email" class="wl-input" placeholder="you@agency.com">
        <button class="wl-btn" onclick="joinWaitlist()">Join waitlist</button>
      </div>
      <div id="wl-msg" style="font-size:12px;color:var(--pip2);min-height:18px;font-family:'Outfit',sans-serif"></div>
      <p style="font-size:11px;color:var(--tx3);margin-top:10px">Already 140+ fractional CMOs and agencies signed up.</p>
    </div>
  </div>
</div>

<div class="ps" id="pricing">
  <div style="text-align:center;margin-bottom:56px">
    <div class="slbl" style="text-align:center">Pricing</div>
    <h2 style="font-size:48px;max-width:100%;text-align:center;margin:0 auto 12px">Simple, transparent pricing</h2>
    <p style="font-size:16px;color:var(--tx2)">Start free. Upgrade when Scout starts paying for itself.</p>
  </div>
  <div class="pg">
    <div class="prc"><div class="pn">Free</div><div class="pp">$0<span class="pper">/mo</span></div><div class="pd">Try Scout and see if it fits.</div><button class="pb2 out" onclick="location.href='/app'">Get started</button><ul class="pfl"><li>5 researches/month</li><li>2 lead fetches</li><li>Inbox &amp; Pipeline</li></ul></div>
    <div class="prc hot"><div class="pbdg">Most popular</div><div class="pn">Pro</div><div class="pp">$29<span class="pper">/mo</span></div><div class="pd">For freelancers actively prospecting.</div><button class="pb2" onclick="location.href='https://buy.stripe.com/00wdR90wGc4Cd52gyCbjW01'">Get Pro</button><ul class="pfl"><li>Unlimited research</li><li>20 lead fetches/month</li><li>Pip Hunt job search</li><li>CSV export</li></ul></div>
    <div class="prc"><div class="pn">Agency</div><div class="pp">$99<span class="pper">/mo</span></div><div class="pd">For agencies managing multiple clients.</div><button class="pb2" onclick="location.href='https://buy.stripe.com/8x2dR993c3y6aWU0zEbjW00'">Get Agency</button><ul class="pfl"><li>Everything in Pro</li><li>5 team members</li><li>100 lead fetches</li><li>White-label pitches</li></ul></div>
  </div>

<!-- Top-up credits -->
  <div style="margin-top:24px;background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r);padding:28px 32px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:20px">
    <div>
      <div style="font-size:13px;font-weight:600;color:var(--tx);margin-bottom:4px">Just need a few more credits?</div>
      <div style="font-size:12px;color:var(--tx3)">Top up without a subscription. Credits never expire.</div>
    </div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
      <a href="https://buy.stripe.com/3cI5kDfrA9WufdabeibjW02" target="_blank" style="display:inline-flex;flex-direction:column;align-items:center;background:var(--sur);border:1px solid var(--bor2);border-radius:var(--r);padding:14px 24px;text-decoration:none;transition:border-color .2s;cursor:pointer" onmouseover="this.style.borderColor='rgba(45,157,232,0.4)'" onmouseout="this.style.borderColor='rgba(45,157,232,0.2)'">
        <span style="font-size:18px;font-weight:700;color:var(--tx);font-family:'JetBrains Mono',monospace">$9</span>
        <span style="font-size:11px;color:var(--tx2);margin-top:2px;font-weight:600">20 credits</span>
        <span style="font-size:10px;color:var(--tx3);margin-top:1px">$0.45 each</span>
      </a>
      <a href="https://buy.stripe.com/5kQ3cvbbk0lUc0Y4PUbjW03" target="_blank" style="display:inline-flex;flex-direction:column;align-items:center;background:var(--sur);border:1px solid var(--pip-bor,rgba(45,157,232,0.22));border-radius:var(--r);padding:14px 24px;text-decoration:none;transition:border-color .2s;position:relative" onmouseover="this.style.borderColor='rgba(45,157,232,0.5)'" onmouseout="this.style.borderColor='rgba(45,157,232,0.22)'">
        <span style="position:absolute;top:-9px;left:50%;transform:translateX(-50%);background:var(--pip);color:#fff;font-size:8px;font-weight:700;padding:2px 10px;border-radius:4px;text-transform:uppercase;letter-spacing:.08em;white-space:nowrap">Best value</span>
        <span style="font-size:18px;font-weight:700;color:var(--tx);font-family:'JetBrains Mono',monospace">$19</span>
        <span style="font-size:11px;color:var(--tx2);margin-top:2px;font-weight:600">50 credits</span>
        <span style="font-size:10px;color:var(--tx3);margin-top:1px">$0.38 each</span>
      </a>
    </div>
  </div>
</div>
</div>

<div style="text-align:center;padding:0 48px 24px;position:relative;z-index:1"><a href="https://buy.stripe.com/fZu8wP4MW2u2c0Y96abjW04" target="_blank" style="font-size:11px;color:var(--tx3);text-decoration:none;border-bottom:1px solid var(--bor2)">$1 test payment</a></div>
<div class="ctaw">
  <div class="ctac">
    <img class="cpip" src="data:image/png;base64,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" alt="Pip">
    <div class="ch2">Your next client<br>is already funded.</div>
    <p class="cs">They just raised. They have no CMO. They need you.<br>Scout finds them before your competitors do.</p>
    <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
      <a href="/app" class="btnp" style="font-size:16px;padding:16px 44px">Start researching free</a>
      <a href="https://calendar.app.google/xFhe41V2HMXNBzw29" target="_blank" class="btng" style="font-size:16px;padding:16px 44px">Book a call</a>
    </div>
    <div class="cn">No credit card required · Free forever tier available</div>
  </div>
</div>

<footer>
  <div class="flo">Scout · scout-ai.io</div>
  <div class="fls">
    <a href="/legal#terms" class="fl">Terms</a>
    <a href="/legal#privacy" class="fl">Privacy</a>
    <a href="mailto:hello@scout-ai.io" class="fl">hello@scout-ai.io</a>
    <a href="/app" class="fl">Go to app</a>
  </div>
</footer>

<script>
var cos=[
  {n:'Ambience Healthcare',m:'Series B · Healthcare AI · SF',s:87,
   sigs:['Recently funded — $70M Series B','No CMO listed on LinkedIn','3 open marketing roles','Has PR agency, no growth lead'],
   dots:['g','g','g','a'],
   p:"Saw the Series B — congrats. Most companies at your stage skip the CMO hire until C, but the pipeline pressure is real now. I’ve helped 3 similar healthcare SaaS teams bridge that gap..."},
  {n:'Fathom Video',m:'Series A · AI Productivity · New York',s:79,
   sigs:['Raised $46M 8 weeks ago','Marketing team of 2','Actively hiring demand gen','No head of growth'],
   dots:['g','g','g','a'],
   p:"Noticed Fathom just closed the Series A — impressive traction. With a 2-person marketing team and demand gen role open, the timing for fractional support is usually right about now..."},
  {n:'Cohere',m:'Series C · Enterprise AI · Toronto',s:61,
   sigs:['$270M raised, 18 months ago','CMO hired 6 months back','Growing marketing team','Strong content presence'],
   dots:['a','a','g','g'],
   p:"Cohere’s been building out the marketing org since the Series C — strong moves. If there’s a gap in the enterprise GTM motion, happy to share what’s worked for similar API-first companies..."}
];
var ci=0;

function run(c){
  var tp=document.getElementById('tp');
  var cr=document.getElementById('cr');
  var scw=document.getElementById('sc-wrap');
  var res=document.getElementById('res');
  var pf2=document.getElementById('pf2');
  var rs=document.getElementById('rs');
  var rb2=document.getElementById('rb2');
  var ptx=document.getElementById('ptx');
  var pt=document.getElementById('pt');
  var sct=document.getElementById('sc-txt');
  if(!tp)return;
  // reset
  tp.textContent='';cr.style.display='inline-block';
  scw.style.display='none';res.style.display='none';
  pf2.style.transition='none';pf2.style.width='0';
  setTimeout(function(){pf2.style.transition='width .35s ease';},50);
  rs.textContent='0';
  rb2.style.transition='none';rb2.style.width='0';
  setTimeout(function(){rb2.style.transition='width 1.2s cubic-bezier(.4,0,.2,1)';},50);
  ptx.textContent='';pt.classList.remove('on');
  [0,1,2,3].forEach(function(i){
    var el=document.getElementById('sig'+i);
    el.classList.remove('on');
    el.querySelector('.dw-sigdot').className='dw-sigdot '+c.dots[i];
    el.querySelector('span').textContent=c.sigs[i];
  });
  document.getElementById('rn').textContent=c.n;
  document.getElementById('rm').textContent=c.m;
  document.getElementById('rt').textContent=c.s>=75?'Hot Lead':c.s>=55?'Warm Lead':'Cold Lead';
  // type
  var i=0;
  var tt=setInterval(function(){
    tp.textContent=c.n.substring(0,i+1);i++;
    if(i>=c.n.length){
      clearInterval(tt);cr.style.display='none';
      setTimeout(function(){
        scw.style.display='block';
        var labs=['Scanning funding data...','Checking LinkedIn team...','Analysing hiring signals...','Writing pitch opener...'];
        var li=0;sct.textContent=labs[0];
        var prog=0;
        var pt2=setInterval(function(){
          prog+=2.2;pf2.style.width=Math.min(prog,96)+'%';
          if(prog>22&&li===0){li=1;sct.textContent=labs[1];}
          if(prog>50&&li===1){li=2;sct.textContent=labs[2];}
          if(prog>78&&li===2){li=3;sct.textContent=labs[3];}
          if(prog>=100){
            clearInterval(pt2);pf2.style.width='100%';
            setTimeout(function(){
              scw.style.display='none';res.style.display='block';
              var cnt=0;
              var st=setInterval(function(){cnt+=3;if(cnt>=c.s){cnt=c.s;clearInterval(st);}rs.textContent=cnt;},22);
              setTimeout(function(){rb2.style.width=c.s+'%';},80);
              [0,1,2,3].forEach(function(i){setTimeout(function(){document.getElementById('sig'+i).classList.add('on');},300+i*200);});
              setTimeout(function(){
                pt.classList.add('on');
                var txt=c.p;var j=0;
                var wt=setInterval(function(){j+=3;ptx.textContent=txt.substring(0,j);if(j>=txt.length){clearInterval(wt);setTimeout(function(){ci=(ci+1)%cos.length;run(cos[ci]);},3500);}},20);
              },1300);
            },280);
          }
        },38);
      },500);
    }
  },52);
}

run(cos[0]);

function joinWaitlist(){
  var e=document.getElementById('wl-email').value.trim();
  var m=document.getElementById('wl-msg');
  if(!e||!e.includes('@')){m.style.color='#ef4444';m.textContent='Please enter a valid email.';return;}
  m.style.color='#5bc4f5';m.textContent="You’re on the list! We’ll be in touch.";
  document.getElementById('wl-email').value='';
  fetch('/waitlist',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e})}).catch(function(){});
}
document.addEventListener('keydown',function(e){if(e.key==='Enter'&&document.activeElement===document.getElementById('wl-email'))joinWaitlist();});
</script>
</body>
</html>'''

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
<p>By accessing or using Scout ("the Service", "Scout", "we", "us"), operated by Scout, you agree to be bound by these Terms of Service. If you do not agree to these terms, please do not use the Service.</p>
<p>We may update these terms at any time. Continued use of the Service after changes constitutes acceptance of the updated terms. We will notify active subscribers of material changes by email.</p>

<h2 id="t2">2. Description of Service</h2>
<p>Scout is a SaaS platform that provides AI-powered company research, lead scoring, pitch generation, and pipeline management tools for marketing professionals. Scout also includes Pip Hunt, a job intelligence feature that surfaces open marketing and design leadership roles.</p>
<p>The Service uses artificial intelligence to generate research, scores, and content. All AI-generated content is provided for informational purposes and should be independently verified before use.</p>

<h2 id="t3">3. Account Registration</h2>
<p>You must provide accurate information when creating an account. You are responsible for maintaining the security of your account and for all activity under your account. Notify us immediately at <a href="mailto:hello@scout-ai.io">hello@scout-ai.io</a> if you suspect unauthorised access.</p>
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
<p>Scout and its original content, features, and functionality are owned by Scout and protected by intellectual property laws. You may not reproduce, distribute, or create derivative works without our written permission.</p>
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
<p>To the maximum extent permitted by law, Scout shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of the Service, even if we have been advised of the possibility of such damages.</p>
<p>Our total liability to you for any claims arising from use of the Service shall not exceed the amount you paid us in the 3 months preceding the claim.</p>

<h2 id="t12">12. Governing Law</h2>
<p>These Terms are governed by the laws of Spain, without regard to conflict of law principles. Any disputes shall be subject to the exclusive jurisdiction of the courts of Madrid, Spain.</p>

<h2 id="t13">13. Contact</h2>
<p>For questions about these Terms, contact us at: <a href="mailto:hello@scout-ai.io">hello@scout-ai.io</a></p>
</div>

<hr class="divider">

<!-- PRIVACY POLICY -->
<div id="privacy">
<h1>Privacy Policy</h1>
<div class="meta">Last updated: April 7, 2026 &nbsp;·&nbsp; Effective immediately</div>

<p>This Privacy Policy explains how Scout, operated by Scout ("we", "us", "our"), collects, uses, and protects your personal information when you use our Service.</p>

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
<p>To exercise any of these rights, email <a href="mailto:hello@scout-ai.io">hello@scout-ai.io</a>. We will respond within 30 days.</p>

<h2>6. Cookies</h2>
<p>Scout does not use tracking cookies. We use browser localStorage for storing your session preferences and lead data. This data is stored locally on your device and is not transmitted to advertising networks.</p>

<h2>7. Data Retention</h2>
<p>We retain your personal data for as long as your account is active. If you delete your account, we will delete your personal data within 30 days, except where we are required by law to retain it (e.g. billing records, which are retained for 7 years for tax purposes).</p>

<h2>8. Children's Privacy</h2>
<p>Scout is not directed at children under 18. We do not knowingly collect personal information from children. If you believe a child has provided us with personal information, contact us and we will delete it.</p>

<h2>9. Changes to This Policy</h2>
<p>We may update this Privacy Policy periodically. We will notify active subscribers of material changes by email at least 14 days before they take effect. Continued use of the Service constitutes acceptance.</p>

<h2>10. Contact &amp; Data Controller</h2>
<p><strong>Data Controller:</strong> Scout<br>
<strong>Email:</strong> <a href="mailto:hello@scout-ai.io">hello@scout-ai.io</a><br>
<strong>Location:</strong> Madrid, Spain</p>

</div>

<div style="margin-top:64px;padding-top:32px;border-top:1px solid var(--bor);font-size:12px;color:var(--tx3);text-align:center">
  Scout · Madrid, Spain · <a href="mailto:hello@scout-ai.io">hello@scout-ai.io</a>
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
  <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAABCGlDQ1BJQ0MgUHJvZmlsZQAAeJxjYGA8wQAELAYMDLl5JUVB7k4KEZFRCuwPGBiBEAwSk4sLGHADoKpv1yBqL+viUYcLcKakFicD6Q9ArFIEtBxopAiQLZIOYWuA2EkQtg2IXV5SUAJkB4DYRSFBzkB2CpCtkY7ETkJiJxcUgdT3ANk2uTmlyQh3M/Ck5oUGA2kOIJZhKGYIYnBncAL5H6IkfxEDg8VXBgbmCQixpJkMDNtbGRgkbiHEVBYwMPC3MDBsO48QQ4RJQWJRIliIBYiZ0tIYGD4tZ2DgjWRgEL7AwMAVDQsIHG5TALvNnSEfCNMZchhSgSKeDHkMyQx6QJYRgwGDIYMZAKbWPz9HbOBQAAAP80lEQVR42u1aaXQVVbb+9jlVd8ocEhKGMBpAJoGAgogJo2grDpioTUvb+FQQu/WJU2u3IY7t6laaBiccHg7PIXmKiDjShsgkkGgACcpomIkhuRnvvVV1zu4fdRPR9d5rQEKv98yXVatWUpU65+yzh2/vfYB2tKMd7WjHzxf0f23C+fn5YiVyBAB0HPAdF+XlqZ/9Jubns/h/v8r8/HwBAHcXbRh6xcub/nbNK+X3PLdqZ5ZftDw/OSGcpOT49JoOM1VggAEAzbaTvTvIv/3yqHx0wVcozX6qdPU7a8qHFhSQzuc21gR3F6KLLyyUp1sLcgsLJTPLd9dvHb+0dEfenMIv/9rzkTX26Kc32a+t3jb8ZDSBTvBdNgDYzJKITpvz+eij8phqCnaeNilnxx1vfH5bcV3yvIbaaj28a+yLvx0aeHv6J+HnO3ssXjkrZTAho5YBEBGfMhOISpVf+/uXAyYtKiseteCLihmvlj3KzAbz/2AOzMQ/8couLjYA4J1aNfvZb1O/XPjxpvF94qz3z+3svbdHetrjG4K+f7u/pOau2/pG5h/SsV1ufqN6Bog4Z+5Kecp8ADNTwVwwM/sXV4SK1tXG5Gyt0X1WBxPumfX6l9OIiLPz3Ym2qCnABCKmn3iVjH2KubBQbjvcdGFpFcW8UmEt69LvHO++S7ovoucvPXxh/OH5O8KxOaYpu6fomuAXR5zLTAAlyNHHKwDj+JSf+PChnXH7mnGG1Ry0feTo75ps2uJEBvzgvcJCWZSXp3wAQlzox5p6A3aYYfq+15JQvNgVkF7DG5ABBMA+zV59MJJQH3LgixdH7GSfMptVfGIH0bHP6CrKK0Lmg596/dLibXXsL1hesdYaPyEcPLAnZbr89spikXDr8t0Rf6zXWHOgXmVbzERE2vVV/9wMjH++dmLks0hPR3Va4EhxtZkyKdTUaHcJkDkgSZatAZADAPnFRkneWOexZRsvKgkm/H7IM+hOWnmZhAZDQADk7osgyR6DYLAGSBAr7hLRgANmYRL7tGJlGALnv7Rjx8XpjXe+8lWostr2jPLYIfubo4hNHHZD7PlDvi741bTpb02Y/9kWj/R97nGsdOHXfQBIgNXxujc6vijERER4b/36tLkfHHjz0Hd15+WNGTD/iatG3A3AobkrJQrGOnOKymZ+WJ3w9P6vt8Kp+Ds40ggS0h2GqHU0ZgCs3TsAEgIEAlhDaw3BDBgmPIMmIK3PAJ2V0LT/k2+dbsphJmJW0s8DUn3BGZmhKTPHD1vrAFDMHmCrh2hgY4vDPqVRIDs72ygpKXHOGtRzdkjJP2+v2BkAgKwbnzXLF91kzylcf9/SmvSHDn1apK237mVLWYKjs6D/ZWA+5k4/eu4hYt/F94qEcdNg1VWhWXkBQTAE2w5M2b+DUTOph39qwcV9Vx3vgn8SEWJmcmJSY2xhIP8/in1gFl8susm+s7A0f1lt54cOvLfIaS66gyLaljBMImmQMEwi00NwDZIIIMPwkelPIMMTQ1FDJQBEpofIMAnSIBgmRYhE3bKHuX75U2z5OiIpwEj2gaU/wfR5PaIy4k/ZurfqZWb25eezaGGLJwLjhEgDEZ85fIjWykFyfYiJSM96dd2cJcHOcw998LwTeu9hqUm42qwcd7mawczwJneFd+ilMHsOg4hPBXljAGWBg4dh71qPcPlyhI/uc7VASLBWIGZIbyzVrViIJMPQNOVWcU7M0ZLmxuCbEaKUnsnW4az0xDUAIgUFYKCA21QAACCEgJTSuPXWiyKPLt3wq/88mPqXg+8tVOHlj0otJREA1hpEAlorSCERN2EWvGOuhWg+DL1zNdQ3y8B2M1h6ITtkIGZoDmLG3wBr/duoff8JOHYIRITE8TfBP/oa1L/3OIIf/lU4kYgqnXLLmLxu1t8emTrqmZY53fATSNYJq4wpBUgamjlfrKjyzz5Qvoablz/CjiCiqIcjIcCsYfoTkHLTYvhHXQH1/h+AN2Yi8btS9OrZFZlDhqNnr+5IC+2GXPZ72EvvhLf/aHSc9RK8sSkAMzyZ58LuPhS+Lv2hQGgofhp1m1bJTw7H55fe+KyZ9Wyp+VP5/wlrgIYAK62wrt5bZflS7a3FpAAhpAEoBwCBAQhhIOW6JyGTkqBen4GkjAFIvflFxPceCh8pCG3D4/EC0oPqygrsXzoPwVd/DTN3HlJnvYTDC65GcMmDCGz5GA2bPgIJgmaIUPn7aBw6rsu2MRn+smuHN/VaUUinUwDStiNkO5b9esWApIgVTtJ2CASQa+sACQBKIWnSbIjUTrAXX4uErMlIzX0QZsMR7F+2AM27NoLsJkhvLHu7DkTH8/Nwxk3P0OH3nsChd++GuPo5JF50O6rfLkD4yE7XQ0oDrB1yQg0s4aRU+vx9AJQWFeXBjf04qdzkuDlzjx49RGVlperavceoSKh+cvH60ilNGedlqMpyjuzfQiTdT7FW8CV2RcK0x8ArHoUvPglJUx+EtWMdqt68D01ffwrdXAM73IBw8BBZB76imi8+Jn9CGgJn56JpXwXCZW/DnDgHavs6OI1HQUK6MY41fJ36Qp8xBl+9cPtFvbvEd8y54JI9W8rLa062unW89iNKSkqcoaPPntHQWHeXjk01bXb6kbIBZVNL3Cbhfs6fdSlUzW4Yh8oRd8G/I9xQi6PvPoZw9W6Ijv2APheAu46O/Oa6W754csFzxYP7dv96V9GDOPptBfvH3gJfuBpUvR3ekdeAtPoBRyACQUWoOdLY9QjH3rOhbO2mkeefe68Qgk/Gp4njfEefd+GFfYK11S80DZ7WMTLxIQjDp4U0wccKnhUkAG//bKgdK4GkDDipmWje+BbQeADeXiPBw6/iGn8asoYMrr3/d9cv6pXRte6+u/7QyceRprp1b5BO6wuj2xA4FR9DZgyAEC6zjbpY18lCg4TB1th8p2HEzbHVdcGHR44bMxyAzs3NladUALm5uQQAzcHqng5Mdnpmq4j0E7EWwvCASLRyN1Ya0hsDSkwHaveCOg2G1dAAe/c6wBMDs984KE8AFGlCc0MwLhKxKjt1SPyscv+R9+ENCBzczE7wCMJpg6GrdkDGdYCMTQH09zrAYDAJEAlypNdQvcc6YXh03aEDnQCgqK2coAQcEBEiTURMUI4NrblV7VvprMcPhgDZIdixadDhMCgUBJuxUNIHxwqRLxBA2bbdvl/fP/+FwZk9qpYUrz2jydJ+n93A4dpq2DGpEGyBpQR8MeD6Yy1cACShtQLbYXC4gQAWWttOm0YBNyECSBCgKFoYc1neD1i9bbl2SwI6VA8FE17TD4o0QNkRwPCBQDC8Pln85fbOK0orOnsMgVhTgMggmzxAqN41LaUA22oZP+oDBACCYIDZJVxggiNlmzpBOOwQM2kWEpAShuGBEK5nbpkgEUGFG2CHGoHEDIgj38DxJsLp2B+I1EHvLYPQDtjwgALx8MUlcGxcAntVI8hqhJPcG1ZcZ8ije8AJXaBDTdANVaDWFNIdj6BBUriZpjDclD0SaVsmaJDPEnCEJK0oJpE1Aay5VQAgAgkJDYazdwtE5hiYNd+AGr+D1Ws8FAtgz1p4KkvhMb0w4lJAcckEq46Mpv1QtgOrZw4QaYBxoBQycyx01W5oxwKkPCbV09EfBvxJLASUJIdi4pPaRgBFRUUaAPUcNqwsxiO3eFc/bvq2vkXa0cplfj9mikBkQyEo9UzYRgByw/NQXbKgB+WCtAWx5zPILUtBO4sh966DJ/g1yGkG+k+BPmMCPBtehtMYBLqPRGTjf0EBILdaEC3IE0hpQGnlrXib/CvmegKC9w0ccV4pAII731NOhKhi40Zr8sSrCpsPVxDv23iGAxmnB10Gp3IzIvs2u+rIGpACTu1BeDtmQvTLhljzJCixG6yzroH2JoNqKiHq90M0HQFZjVD+ZNhDpsMacT3MvWshV80DZ98OVVeL4McLXFVvyS+0hi+9D4z+Y1lUvCviqzc1dhCRxYOHjfrNq88+e/BECiEnzAQB0ObNG5sPHaz65Mrp1y9WWh4N9508tmHbGrL2byEi6TqlaC7gVG6Gf9xsIKkzzFVPQCgNp/d4OL3GQXcZAdVzNOzMybAHXg3q0Bfere/AWP0XOCOuA/pMRv3Lt8EO14Egol8kMGsYKb118tmXUA9nz59zzp1w/ZKit14p37ix7mQWf1J9uKysLBMAYv1eDFyw7Ujg7GsYIC2k0VrNFVIyARzTLYvT5n7Ona+fx116deUu/Qdy2qW3ccrMlzj5tiWcPPs1Tpv6e+48aBh36p7O6dMe4E4PbOCYzNFMAB/7TZIGA2Bvvwl68MLtupy5JwBkZd1onnyH68STIS4rK7MBUMNdU8xBrI7KhLSOURfdGoZYa5CUaN5bBrUgD3FXFED+8mXw9k9A+zbCs/tTCGVDSw9UIBlOn7EQfSeB62pQ/+Qv0XxkJ4Q0wFr9sCsDsJGYRoJ108GVK223AjRXlZUt0ie9oyfZo5KiKE9NeK7s7dJtVZc3zL/Mcdg2iER00u50SUho5UAACAy9HN5zcmF06ArWEZAdgTa9gAyAaw/AKluCpg1FUNqBkBKsj1kTCYAAobSTOPtN2btv5oqyW4dOUlcWShT9C9rjudG+4NMfrpvY96k9HHvRH20PoAlgktJV3Za7YTJFTUIC7EtI40C3szgm81z298hib1Jnlq7tMkmDyTCYhPzh5f6vDuTcYvV6ch/f8dqqy4+dx7+oXe1WYq59pfSeHgsr2f+L+x1PbEdbAo4AFAFaABztprbe8d9cLc9b3on+rgWgJOB4Akl2YPzvnO7zd/HUFzfOEz+hHX5KT4hk5xcbqwvGOjPfKH1gbUPSH/cfDCJycDsQaoCQ5KquVtEM7vviN5MACze8cfR562RIAEKAoaGVBvnj4UnvjU6dUjEqpvrpxdPPvtl6s1AiL1cfT+enTQXgqgILUUB62frNw1/ZZUw86ngnsaCEvVs+79V09FACGEzMxNBu4tTSKHG9RNS18fc2H22geGOTmzKGZm8TioMJpr32krTGD2dOzFrnuC0vnKqQR6fIHgQKCjQAeACYAhiUk7Nof4N9vWRtk5Bmazp/zNKJyN19ciM9MwNaO1oYRppPLP/qs5IpDgP29wMJoECf0rh+ynwCsyiYu1LgUBxh0XAn/5O9FyzdHflgV62CgIq2wzhaNXY3kZldBYhWkwQEbGZ0S/Lh0ozIjD/94szFyC80s5Gq2+pAFLWNg8wXDz9QoOcs2Tpj5QFnVtiyUgW7/o1IIOyoJsVwfIaIIWKDSMJxtKUZHBcTsEem4+WFUwf+6b77WRQUkG5LZ97mZ328BIQ1e3/0Z8snicOKj2VxTnQ+Knq647RQ2zbmCyxPRsinM76fntNePz5GQ63lJPox12191o52tKMd7WhHO9rRjna0ox3taEcbJalM7VL4mYIAYMOGDRn/AE1W062rTF8gAAAAAElFTkSuQmCC" style="width:36px;height:36px;object-fit:contain;display:block;margin:0 auto 20px;">
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
        if self.path == '/manifest.json':
            import re as _re
            b64_match = _re.search(r'data:image/png;base64,([A-Za-z0-9+/=]{100,})', LANDING_HTML)
            pip_b64 = b64_match.group(1) if b64_match else ''
            manifest = {
                "name": "Scout",
                "short_name": "Scout",
                "description": "AI-powered lead generation for marketing pros",
                "start_url": "/app",
                "display": "standalone",
                "background_color": "#020408",
                "theme_color": "#020408",
                "orientation": "portrait-primary",
                "icons": [
                    {"src": "data:image/png;base64," + pip_b64, "sizes": "192x192", "type": "image/png"},
                    {"src": "data:image/png;base64," + pip_b64, "sizes": "512x512", "type": "image/png"}
                ],
                "categories": ["business", "productivity"],
                "screenshots": []
            }
            import json as _json
            out = _json.dumps(manifest).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/manifest+json')
            self.send_header('Content-Length', str(len(out)))
            self.end_headers()
            self.wfile.write(out)
            return
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
        if self.path in ('/', ''):
            content = LANDING_HTML.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if self.path in ('/app', '/app/'):
            content = HTML.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        self.send_response(404); self.end_headers(); return

    def do_POST(self):
        if self.path == '/stripe-webhook':
            length = int(self.headers.get('Content-Length', 0))
            try:
                payload = self.rfile.read(length)
                event = json.loads(payload)
                etype = event.get('type','')
                print('[Stripe]', etype)
                if etype in ('checkout.session.completed','customer.subscription.created','customer.subscription.updated'):
                    sess = event.get('data',{}).get('object',{})
                    customer_email = sess.get('customer_email') or sess.get('customer_details',{}).get('email','')
                    amount = sess.get('amount_total',0) or sess.get('plan',{}).get('amount',0)
                    plan = 'pro' if amount <= 3000 else 'agency'
                    if customer_email:
                        print(f'[Stripe] Upgrading {customer_email} to {plan}')
                        # Log upgrade for manual processing until Supabase auth is added
                        with open('/tmp/scout_upgrades.txt','a') as f:
                            import datetime
                            f.write(f"{datetime.datetime.utcnow().isoformat()} | {customer_email} | {plan}\n")
                self.respond({'ok': True})
            except Exception as e:
                print('[Stripe webhook error]', e)
                self.respond({'error': str(e)})
            return
        if self.path == '/waitlist':
            length = int(self.headers.get('Content-Length', 0))
            try:
                data = json.loads(self.rfile.read(length))
                email = data.get('email', '').strip()
                if email:
                    wl_file = '/tmp/scout_waitlist.txt'
                    with open(wl_file, 'a') as f:
                        f.write(email + '\n')
                    print('[Waitlist]', email)
                self.respond({'ok': True})
            except Exception as e:
                self.respond({'error': str(e)})
            return
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
