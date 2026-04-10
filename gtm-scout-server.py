# Scout v3.3 | 2026-04-10 12:41
# Scout v3.0 | 2026-04-10 10:58
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

def load_db(user_key=None):
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
                _gf = gist_data['files'].get(('scout_db_'+user_key.replace('@','_').replace('.','_')+'.json') if user_key else 'scout_db.json'); content = _gf['content'] if _gf else '[]'
                data = json.loads(content)
                if isinstance(data, list):
                    if len(data) == 1 and data[0].get('init') == True:
                        data = []
                    if user_key:
                        _def = gist_data['files'].get('scout_db.json')
                        if _def:
                            try:
                                _def_data = json.loads(_def['content'])
                                if isinstance(_def_data, list):
                                    existing_ids = {r.get('_id') for r in data}
                                    merged = [r for r in _def_data if r.get('_id') not in existing_ids and not r.get('init')]
                                    if merged:
                                        data = data + merged
                                        print('[DB] Merged', len(merged), 'default records')
                            except Exception as me: print('[DB] Merge error:', me)
                    if len(data) > 0:
                        print('[DB] Loaded', len(data), 'records from Gist')
                        return data
                else:
                    print('[DB] Gist empty or invalid')
        except Exception as e:
            print('[DB] Gist load error:', e)
    else:
        print('[DB] No Gist credentials - GIST_ID:', bool(GIST_ID), 'GIST_TOKEN:', bool(GIST_TOKEN))
    # Fallback to local file
    try:
        db_file = '/tmp/scout_db_' + (user_key.replace('@','_').replace('.','_') if user_key else 'default') + '.json'
        if os.path.exists(db_file):
            with open(db_file) as f:
                data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                print('[DB] Loaded', len(data), 'records from local file')
                return data
    except Exception as e:
        print('[DB] Local load error:', e)
    return []

def save_db(data, user_key=None):
    # Always save to local file first
    try:
        db_file = '/tmp/scout_db_' + (user_key.replace('@','_').replace('.','_') if user_key else 'default') + '.json'
        with open(db_file, 'w') as f:
            json.dump(data, f)
        print('[DB] Saved', len(data), 'records to local file')
    except Exception as e:
        print('[DB] Local save error:', e)
    # Save to GitHub Gist
    if GIST_ID and GIST_TOKEN:
        try:
            _gist_fname = ('scout_db_' + user_key.replace('@','_').replace('.','_') + '.json') if user_key else 'scout_db.json'
            payload = json.dumps({
                'files': {
                    _gist_fname: {
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
.page,.sidebar{position:relative;z-index:1}
.topbar{position:relative;z-index:9999}

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
.page.active{display:block}
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

/* ── LEAD CARDS - glow on hover ── */
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
.ph-card{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);overflow:hidden;padding:16px 18px;transition:all .2s}
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
.tier-features li::before{content:'-';color:var(--pip2);font-weight:700;flex-shrink:0}
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
/* SCOUT LOGO */
.ndot{width:7px;height:7px;border-radius:50%;background:var(--pip);box-shadow:0 0 10px var(--pip);animation:ndot 2s ease-in-out infinite;flex-shrink:0}
@keyframes ndot{0%,100%{box-shadow:0 0 8px var(--pip)}50%{box-shadow:0 0 22px var(--pip2),0 0 40px rgba(45,157,232,0.3)}}
.logo-text{font-size:12px;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:var(--tx);font-family:'Outfit',sans-serif}
.logo-btn{display:flex;align-items:center;gap:8px;background:none;border:none;cursor:pointer;padding:0}
/* CRM DASHBOARD */
.page-dashboard{padding:0}
.dash-header{padding:24px 24px 0}
.dash-title{font-size:22px;font-weight:700;letter-spacing:-.03em;color:var(--tx);margin-bottom:4px}
.dash-sub{font-size:13px;color:var(--tx3)}
.stat-cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;padding:20px 24px}
.stat-card{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);padding:16px 18px;cursor:pointer;transition:border-color .15s}
.stat-card:hover{border-color:var(--bor2)}
.stat-card-n{font-size:28px;font-weight:800;color:var(--tx);font-family:'JetBrains Mono',monospace;letter-spacing:-.04em;line-height:1}
.stat-card-l{font-size:11px;color:var(--tx3);margin-top:4px;text-transform:uppercase;letter-spacing:.1em;font-weight:600}
.stat-card-accent{height:2px;border-radius:1px;margin-top:12px}
.dash-grid{display:grid;grid-template-columns:1fr 340px;gap:16px;padding:0 24px 24px}
.dash-panel{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r)}
.dash-panel-header{padding:14px 18px;border-bottom:1px solid var(--bor);display:flex;align-items:center;justify-content:space-between}
.dash-panel-title{font-size:13px;font-weight:700;color:var(--tx);letter-spacing:.01em}
.dash-panel-action{font-size:11px;color:var(--pip2);cursor:pointer;background:none;border:none;font-family:'Outfit',sans-serif;padding:0}
.crm-row{display:flex;align-items:center;padding:12px 18px;border-bottom:1px solid var(--bor);cursor:pointer;transition:background .12s;gap:12px}
.crm-row:last-child{border-bottom:none}
.crm-row:hover{background:var(--sur2)}
.crm-co{font-size:13px;font-weight:600;color:var(--tx);flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.crm-meta{font-size:11px;color:var(--tx3)}
.crm-score{font-size:14px;font-weight:800;font-family:'JetBrains Mono',monospace;min-width:28px;text-align:right}
.crm-status{font-size:9px;font-weight:700;padding:2px 8px;border-radius:999px;border:1px solid;white-space:nowrap;text-transform:uppercase;letter-spacing:.06em}
.kanban-mini{display:flex;gap:8px;padding:14px 18px;overflow-x:auto}
.kb-col-mini{flex:1;min-width:80px}
.kb-col-mini-label{font-size:9px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:var(--tx3);margin-bottom:8px;display:flex;align-items:center;justify-content:space-between}
.kb-card-mini{background:var(--sur2);border:1px solid var(--bor);border-radius:4px;padding:8px 10px;margin-bottom:6px;cursor:pointer;transition:border-color .12s;font-size:11px;color:var(--tx2);line-height:1.4}
.kb-card-mini:hover{border-color:var(--bor2)}
.inbox-preview{padding:0}
.inbox-row{display:flex;align-items:center;gap:12px;padding:12px 18px;border-bottom:1px solid var(--bor);cursor:pointer;transition:background .12s}
.inbox-row:last-child{border-bottom:none}
.inbox-row:hover{background:var(--sur2)}
.inbox-badge-dot{width:6px;height:6px;border-radius:50%;background:var(--pip);flex-shrink:0}
/* SEARCH PAGE REDESIGN */
.search-wrap{padding:24px}
.search-eyebrow{font-size:10px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--pip2);margin-bottom:12px;display:flex;align-items:center;gap:8px}
.search-heading{font-size:26px;font-weight:800;letter-spacing:-.03em;color:var(--tx);margin-bottom:6px}
.search-sub{font-size:13px;color:var(--tx3);margin-bottom:20px;line-height:1.6}
.search-input-row{display:flex;gap:10px;margin-bottom:24px}
.search-input-row input{flex:1;font-size:15px;padding:13px 18px}
.search-input-row button{padding:13px 24px;font-size:14px;font-weight:700;white-space:nowrap}
.recent-label{font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--tx3);margin-bottom:12px}
.recent-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:24px}
.recent-card{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);padding:14px;cursor:pointer;transition:all .15s}
.recent-card:hover{border-color:var(--bor2);transform:translateY(-1px)}
.recent-card-name{font-size:13px;font-weight:700;color:var(--tx);margin-bottom:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.recent-card-meta{font-size:11px;color:var(--tx3);margin-bottom:8px}
.recent-card-score{font-size:20px;font-weight:800;font-family:'JetBrains Mono',monospace}
.fetch-panel{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);padding:20px;margin-top:8px}
.fetch-panel-title{font-size:13px;font-weight:700;color:var(--tx);margin-bottom:4px;display:flex;align-items:center;gap:8px}
.fetch-panel-sub{font-size:12px;color:var(--tx3);margin-bottom:14px}
/* LEAD DETAIL PAGE */
.lead-detail{padding:0 24px 24px}
.ld-back{display:flex;align-items:center;gap:8px;font-size:13px;color:var(--tx3);cursor:pointer;padding:20px 0 16px;background:none;border:none;font-family:'Outfit',sans-serif}
.ld-back:hover{color:var(--pip2)}
.ld-header{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:24px}
.ld-name{font-size:28px;font-weight:800;letter-spacing:-.04em;color:var(--tx);margin-bottom:4px}
.ld-meta{font-size:13px;color:var(--tx3)}
.ld-score{font-size:64px;font-weight:800;font-family:'JetBrains Mono',monospace;line-height:1;letter-spacing:-.04em}
.ld-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.ld-section{background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);padding:18px}
.ld-section-title{font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--tx3);margin-bottom:14px}
#ob-splash{display:none;opacity:0;position:fixed;top:0;left:0;width:100%;height:100%;background:#020408;z-index:99999;flex-direction:column;align-items:center;justify-content:center;transition:opacity .5s ease;padding:24px;overflow-y:auto;}
#ob-splash.active{display:flex;}
.sourcer-search-card{background:var(--sur2);border:1px solid var(--bor);border-radius:8px;padding:14px 16px;margin-bottom:8px;display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.sourcer-search-str{font-size:12px;color:var(--tx2);font-family:'JetBrains Mono',monospace;line-height:1.5;flex:1;word-break:break-all}
.sourcer-copy-btn{background:var(--pip);color:#fff;border:none;font-size:10px;font-weight:700;padding:5px 12px;border-radius:4px;cursor:pointer;font-family:Outfit,sans-serif;white-space:nowrap;flex-shrink:0}
.candidate-card{background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r);padding:16px;margin-bottom:10px}
.candidate-inmail{font-size:12px;color:var(--tx2);line-height:1.6;margin-top:10px;padding:10px;background:var(--sur);border-radius:6px;border:1px solid var(--bor)}
/* Full-width dashboard kanban */
.kanban-board{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;min-height:400px}
.kanban-col{background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r);padding:12px;min-height:300px;display:flex;flex-direction:column}
.kanban-col-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
.kanban-col-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--tx3)}
.kanban-col-count{font-size:10px;font-weight:700;color:var(--tx3);background:var(--sur3);padding:2px 7px;border-radius:999px}
.kanban-card{background:var(--sur);border:1px solid var(--bor);border-radius:8px;padding:10px 12px;margin-bottom:8px;cursor:grab;transition:transform .15s,box-shadow .15s;user-select:none}
.kanban-card:hover{transform:translateY(-1px);box-shadow:0 4px 16px rgba(0,0,0,0.3)}
.kanban-card.dragging{opacity:.5;transform:scale(.97)}
.kanban-col.drag-over{border-color:var(--pip);background:rgba(45,157,232,0.05)}
.kanban-card-name{font-size:13px;font-weight:700;color:var(--tx);margin-bottom:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.kanban-card-meta{font-size:11px;color:var(--tx3)}
.kanban-card-score{font-size:18px;font-weight:800;font-family:'JetBrains Mono',monospace;letter-spacing:-.04em;line-height:1}
.kanban-empty{font-size:12px;color:var(--tx3);text-align:center;padding:24px 0;opacity:.5}
/* App loading state - hide content until ready */


#app-loading {
  display: none;
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: var(--bg);
  z-index: 9998;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 16px;
}
#app-loading-dot {
  width: 10px; height: 10px;
  border-radius: 50%;
  background: var(--pip);
  box-shadow: 0 0 20px var(--pip);
  animation: ndot 1.5s ease-in-out infinite;
}
"""

JS = """
function goHome(){window.location.href='/';}
function safeOrigin(){
  try{
    var o=window.location.origin;
    if(o&&o!=='null'&&o.indexOf('http')===0)return o;
  }catch(e){}
  return 'https://scout-ai.io';
}

function openProfileModal(){
  profileLoad();
  var m = document.getElementById('profile-modal');
  if(!m){ alert('Profile editor not found - please refresh.'); return; }
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
var currentPage = 'dashboard';
var fil = 'all';

var SYS = "Return ONLY a valid JSON object. No markdown, no extra text. Fields: company, tagline, sector, hq, stage, funding_amount, founded, has_cmo (bool), gtm_readiness_score (0-100 integer; only score above 30 - a score below 30 means the company is not a good lead), gtm_label (Hot Lead/Warm Lead/Cold Lead), why_fit (1 sentence), pitch_opener (2-3 sentences), decision_maker, best_contact_title, best_contact_name, outreach_status (always: not_contacted), gtm_signals (object: recently_funded bool, no_cmo bool, marketing_gap_visible bool). Use null for unknown.";
var FETCH_SYS = "You are a funding news API. Search for startup funding news from the last 14 days. YOU MUST respond with ONLY a raw JSON array starting with [ and ending with ]. No text before, no text after, no markdown, no explanation. Each element: {company,sector,funding,stage,source}. Return BETWEEN 8 AND 15 items. NEVER include mega-brands or well-known companies like OpenAI, Anthropic, Google, Meta, Apple, Microsoft, Amazon, Salesforce, Stripe, Ramp, Notion, Figma - only return genuine startups that recently raised funding. Start your response with [ immediately.";

function load(onDone) {
  var userEmail = SUPA_USER && SUPA_USER.email ? SUPA_USER.email : (authGetUser() && authGetUser().email ? authGetUser().email : '');
  var url = userEmail ? '/db?user=' + encodeURIComponent(userEmail) : '/db';
  fetch(url).then(function(r){return r.json();}).then(function(d){
    if(Array.isArray(d)){
      DB = d.filter(function(x){return !x._inbox;});
      INBOX = d.filter(function(x){return x._inbox;});
      updateBadges();
      if(typeof onDone==='function'){onDone();}
      else if(currentPage==='dashboard') renderDashboard();
      if(currentPage==='profile'){profileLoad();renderProfile();}
      else if(currentPage==='leads') renderLeads();
      else if(currentPage==='pipeline') renderPipelinePage();
      else if(currentPage==='inbox') renderInbox();
    }
  }).catch(function(){DB=[];INBOX=[];if(typeof onDone==='function')onDone();});
}




function saveAll() {
  var all = DB.concat(INBOX);
  var userEmail = SUPA_USER && SUPA_USER.email ? SUPA_USER.email : (authGetUser() && authGetUser().email ? authGetUser().email : '');
  fetch('/save',{method:'POST',headers:{'Content-Type':'application/json','X-User-Email': userEmail},body:JSON.stringify(all)})
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
  var ibd = document.getElementById('inbox-badge-dash');
  if(ibd) ibd.textContent = INBOX.length ? INBOX.length + ' new' : '';
  var ibsi = document.getElementById('inbox-badge-si');
  if(ibsi){ ibsi.textContent=INBOX.length; ibsi.style.display=INBOX.length?'':'none'; }
}
function renderAll(){
  if(currentPage==='dashboard') renderDashboard();
  else if(currentPage==='leads') renderLeads();
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
function navTo(page){
  closeSidebar();
  var t=tierLoad();
  if(page==='inbox'&&t.plan!=='agency'&&!t._master){showUpsellToast('Inbox is an Agency feature');return;}
  if(page==='piphunt'&&!tierCanPipHunt()){showUpsellToast('Upgrade to use Pip Hunt');return;}
  if(page==='teams'&&t.plan!=='agency'&&!t._master){showUpsellToast('Teams is an Agency feature');return;}
  setPage(page);
}
function setPage(page, addToHistory) {
  if(addToHistory!==false && currentPage && currentPage!==page){
    PAGE_HISTORY.push(currentPage);
    if(PAGE_HISTORY.length>10) PAGE_HISTORY.shift();
  }
  currentPage = page;
  document.querySelectorAll('.page').forEach(function(p){p.classList.remove('active');});
  renderSidebarTier();
  var pg = document.getElementById('page-'+page);
  if(pg) pg.classList.add('active');
  // Hide inbox sidebar item for non-agency
  (function(){
    var t=tierLoad();
    var inboxSi=document.getElementById('si-inbox');
    if(inboxSi) inboxSi.style.display=(t.plan==='agency'||t._master)?'':'none';
  })();
  var bb=document.getElementById('page-back-btn');
  if(bb){ var showBack=['search','inbox','leads','pipeline','piphunt','profile','teams'].indexOf(page)>=0; bb.style.display=showBack?'flex':'none'; }
  // Show inbox sidebar item only for agency
  var _inboxSi=document.getElementById('si-inbox');
  if(_inboxSi){ var _t=tierLoad(); _inboxSi.style.display=(_t.plan==='agency'||_t._master)?'':'none'; }
  var _inboxBadgeSi=document.getElementById('inbox-badge-si');
  if(_inboxBadgeSi&&INBOX.length){ _inboxBadgeSi.textContent=INBOX.length; _inboxBadgeSi.style.display=''; }
  ['dashboard','search','piphunt','profile','leads','inbox','pipeline','teams'].forEach(function(p){
    var el = document.getElementById('si-'+p);
    if(el) el.classList.toggle('active', p===page);
  });
  if(page==='dashboard') renderDashboard();
  if(page==='leads') renderLeads();
  if(page==='piphunt')    {
    phLoad();
    phRenderJobs();
    // Restore last candidate search if any
    setTimeout(function(){
      var lastSrc=PH_HISTORY.filter(function(h){return h.type==='source'&&h.candidates&&h.candidates.length;})[0];
      if(lastSrc){
        phSetMode('source');
        renderCandidateCards(lastSrc.candidates);
      }
    },50);
  }
  if(page==='inbox') renderInbox();
  if(page==='profile'){profileLoad();renderProfile();}
  if(page==='teams'){renderTeams();if(window.location.search.indexOf('seat=paid')>-1){var _s=document.getElementById('teams-invite-section');if(_s)_s.style.display='block';history.replaceState(null,'','/app');}}
}

// ── HELPERS ──────────────────────────────────────────────────────────────────
function sc(n){return n>=80?'var(--pip)':n>=50?'var(--amb)':'var(--tx3)';}
function su(v){if(!v||v==='null'||v==='undefined')return '';return String(v).indexOf('http')===0?v:'https://'+v;}

// ── SEARCH PAGE ──────────────────────────────────────────────────────────────
function go(){var v=document.getElementById('ci').value.trim();if(!v||busy)return;if(!tierCanResearch())return;document.getElementById('ci').value='';run(v);}





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
    var _js=t.slice(a,b+1),res;
    try{res=JSON.parse(_js);}catch(e){
      var _r=_js.replace(/,\s*"[^"]*"\s*:[^,}]*$/,'').replace(/,$/,'');
      if(_r.slice(-1)!=='}')_r+='}';
      try{res=JSON.parse(_r);}catch(e2){throw new Error('Parse failed: '+e2.message);}
    }
    if(!res.company)throw new Error('Missing company data');
    res._open=true;
    tierUseResearch();
    // Update existing or add new
    var existing=DB.findIndex(function(x){return x.company&&x.company.toLowerCase()===res.company.toLowerCase();});
    // Skip cold leads (score < 30) on auto-research
    var score=res.gtm_readiness_score||0;
    if(score<30 && existing<0){ if(callback)callback(); return; }
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
  var prompt='Search '+srcNames+' for startup funding announcements from the last 14 days. Focus on AI, SaaS, fintech, web3. Return AT LEAST 8 genuine startups that recently raised funding. EXCLUDE well-known mega-brands like OpenAI, Anthropic, Google, Stripe, Ramp, Notion - only real emerging startups.'+extraInstructions;
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:'',company:prompt,system:FETCH_SYS,mode:'fetch'})})
  .then(function(r){return r.json();}).then(function(d){
    if(d.error)throw new Error(d.error);
    var t=d.text||'';t=t.replace(/```json/g,'').replace(/```/g,'').trim();
    // Try to find array in response
    var a=t.indexOf('['),b=t.lastIndexOf(']');
    var _arr,cos;
    if(a>=0&&b>a){
      _arr=t.slice(a,b+1);
    } else {
      // No brackets - try to wrap content in array
      // Sometimes AI returns objects without wrapping []
      var _ob=t.indexOf('{'),_cb=t.lastIndexOf('}');
      if(_ob>=0&&_cb>_ob){ _arr='['+t.slice(_ob,_cb+1)+']'; }
      else{ throw new Error('No results returned - try again'); }
    }
    try{cos=JSON.parse(_arr);}catch(e){
      // Strip last incomplete entry
      var _lc=_arr.lastIndexOf(',{');
      if(_lc>0)_arr=_arr.slice(0,_lc)+']';
      try{cos=JSON.parse(_arr);}catch(e2){
        // Last resort: extract individual objects
        var _objs=[],_m,_re=/{[^{}]+}/g;
        while((_m=_re.exec(_arr))!==null){try{_objs.push(JSON.parse(_m[0]));}catch(ex){}}
        if(_objs.length){cos=_objs;}
        else{throw new Error('Could not parse results - try again');}
      }
    }
    // Filter out error messages or non-company results
    var badWords=['insufficient','unable','error','no data','no results','no companies','n/a','unknown','failed'];
    cos=cos.filter(function(co){
      if(!co.company||typeof co.company!=='string')return false;
      var lower=co.company.toLowerCase();
      return !badWords.some(function(w){return lower.indexOf(w)>=0;});
    });
    if(!cos.length)throw new Error('No valid companies found in results');
    // Dedup against existing DB + INBOX
    var existingNames=DB.concat(INBOX).map(function(x){return (x.company||'').toLowerCase();});
    cos=cos.filter(function(co){return existingNames.indexOf(co.company.toLowerCase())<0;});
    if(!cos.length)throw new Error('All companies already in your pipeline - try a different source');
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
  setPage('inbox');
  renderInbox();
  // Show persistent progress bar at top of inbox
  var prog=document.createElement('div');
  prog.id='inbox-progress';
  prog.style.cssText='position:fixed;top:52px;left:0;right:0;z-index:9000;background:var(--pip);color:#fff;font-family:Outfit,sans-serif;font-size:13px;font-weight:600;padding:10px 20px;display:flex;align-items:center;gap:12px;box-shadow:0 2px 12px rgba(0,0,0,.3)';
  prog.innerHTML='<div style="width:18px;height:18px;border:2px solid rgba(255,255,255,0.4);border-top-color:#fff;border-radius:50%;animation:spin .7s linear infinite;flex-shrink:0"></div><span id="inbox-progress-txt">Researching leads... (0/'+names.length+')</span>';
  document.body.appendChild(prog);
  var i=0;var added=0;
  function next(){
    if(i>=names.length){
      save();updateBadges();renderInbox();
      var p=document.getElementById('inbox-progress');if(p)p.remove();
      showInfoToast('Done! '+added+' lead'+(added!==1?'s':'')+' added to Inbox ✓');
      return;
    }
    var name=names[i++];
    var txt=document.getElementById('inbox-progress-txt');
    if(txt)txt.textContent='Researching '+name+'... ('+i+'/'+names.length+')';
    runToInbox(name,function(wasAdded){if(wasAdded)added++;next();});
  }
  setTimeout(next,0);
}

function runToInbox(company, callback){
  var ind=document.getElementById('save-ind');
  var _wasAdded=false;
  if(ind){ind.textContent='Researching '+company+'...';ind.style.color='var(--tx3)';}
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:'',company:company,system:SYS,mode:'research'})})
  .then(function(r){return r.json();}).then(function(d){
    if(d.error)throw new Error(d.error);
    var t=(d.text||'').replace(/```json/g,'').replace(/```/g,'').trim();
    var a=t.indexOf('{'),b=t.lastIndexOf('}');
    if(a<0||b<0)throw new Error('No JSON');
    var _s=t.slice(a,b+1),res;
    try{res=JSON.parse(_s);}catch(e){
      var _f=_s.replace(/,\s*"[^"]*"\s*:[^,}]*$/,'').replace(/,$/,'');
      if(_f.slice(-1)!=='}')_f+='}';
      try{res=JSON.parse(_f);}catch(e2){throw new Error('Parse error: '+e2.message);}
    }
    if(!res.company)throw new Error('Missing company');
    res._id='id'+Date.now()+Math.floor(Math.random()*9999);
    res._inbox=true;
    res._open=false;
    // Dedup: skip if already in DB or INBOX
    var alreadyInDb=DB.some(function(x){return x.company&&res.company&&x.company.toLowerCase()===res.company.toLowerCase();});
    var alreadyInInbox=INBOX.some(function(x){return x.company&&res.company&&x.company.toLowerCase()===res.company.toLowerCase();});
    if(alreadyInDb||alreadyInInbox){ if(callback){setTimeout(function(){callback(false);},1500);} return; }
    INBOX.unshift(res);
    updateBadges();renderInbox();
    if(ind){ind.textContent='Added '+res.company+' ✓';ind.style.color='var(--pip)';}
    setTimeout(function(){if(ind)ind.textContent='';},2000);
    _wasAdded=true;
  }).catch(function(e){
    if(ind){ind.textContent='Error: '+e.message;ind.style.color='var(--red)';}
    setTimeout(function(){if(ind)ind.textContent='';},3000);
  }).finally(function(){
    if(callback)setTimeout(function(){callback(_wasAdded);},4000); // 4s between calls avoids rate limit
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

function renderDashboard(){
  // Stat cards
  var stats=document.getElementById('dash-stats');
  if(!stats)return;
  var hot=DB.filter(function(r){return(r.gtm_readiness_score||0)>=75;}).length;
  var contacted=DB.filter(function(r){return r.outreach_status==='contacted'||r.outreach_status==='in_talks';}).length;
  var won=DB.filter(function(r){return r.outreach_status==='closed';}).length;
  var refused=DB.filter(function(r){return r.outreach_status==='refused';}).length;
    stats.innerHTML=
    '<div class="stat-card" data-action="hot-leads">'+
      '<div class="stat-card-n" style="color:var(--pip2)">'+hot+'</div>'+
      '<div class="stat-card-l">Hot Leads</div>'+
      '<div class="stat-card-accent" style="background:var(--pip2)"></div>'+
    '</div>'+
    '<div class="stat-card" data-action="warm-leads" style="cursor:pointer">'+
      '<div class="stat-card-n" style="color:var(--amb)">'+contacted+'</div>'+
      '<div class="stat-card-l">In Progress</div>'+
      '<div class="stat-card-accent" style="background:var(--amb)"></div>'+
    '</div>'+
    '<div class="stat-card" data-action="won-leads" style="cursor:pointer">'+
      '<div class="stat-card-n" style="color:var(--grn)">'+won+'</div>'+
      '<div class="stat-card-l">Won</div>'+
      '<div class="stat-card-accent" style="background:var(--grn)"></div>'+
    '</div>'+
    '<div class="stat-card" data-action="cold-leads" style="cursor:pointer">'+
      '<div class="stat-card-n" style="color:rgba(239,68,68,0.8)">'+refused+'</div>'+
      '<div class="stat-card-l">Closed Lost</div>'+
      '<div class="stat-card-accent" style="background:rgba(239,68,68,0.5)"></div>'+
    '</div>';

  // Show inbox button only for agency
  var t=tierLoad();
  var inboxBtn=document.getElementById('inbox-agency-btn');
  if(inboxBtn){
    if(t.plan==='agency'||t._master){
      var cnt=INBOX.length?(' <b style="color:var(--pip2)">'+INBOX.length+'</b>'):'';
      inboxBtn.innerHTML='<button id="inbox-nav-btn" style="background:none;border:1px solid var(--bor2);color:var(--tx2);font-size:11px;font-weight:700;padding:6px 14px;border-radius:6px;cursor:pointer;font-family:Outfit,sans-serif">Inbox'+cnt+'</button>';
      setTimeout(function(){var b=document.getElementById('inbox-nav-btn');if(b)b.onclick=function(){navTo('inbox');};},10);
    } else {
      inboxBtn.innerHTML='';
    }
  }

  // Saved leads link
  var recentDiv = document.getElementById('dash-recent-leads');
  if(recentDiv){
    var saved = DB.filter(function(x){return x.outreach_status && x.outreach_status !== 'not_contacted';});
    var total = DB.length;
    recentDiv.innerHTML = '';
    var wrap = document.createElement('div');
    wrap.style.cssText = 'display:flex;align-items:center;justify-content:space-between;padding:12px 16px;background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r);cursor:pointer;transition:border-color .15s';
    wrap.onmouseover = function(){ this.style.borderColor='var(--pip-bor)'; };
    wrap.onmouseout  = function(){ this.style.borderColor='var(--bor)'; };
    wrap.onclick     = function(){ navTo('leads'); };
    var left = document.createElement('div');
    var title = document.createElement('div');
    title.style.cssText = 'font-size:13px;font-weight:700;color:var(--tx)';
    title.textContent = 'Saved Leads';
    var sub = document.createElement('div');
    sub.style.cssText = 'font-size:11px;color:var(--tx3);margin-top:2px';
    sub.textContent = total + ' total · ' + saved.length + ' in progress';
    left.appendChild(title); left.appendChild(sub);
    var arrow = document.createElement('div');
    arrow.style.cssText = 'font-size:18px;color:var(--tx3)';
    arrow.textContent = '›';
    wrap.appendChild(left); wrap.appendChild(arrow);
    recentDiv.appendChild(wrap);
  }

    renderKanbanBoard();
  // Wire stat card clicks
  setTimeout(function(){
    var sc=document.getElementById('dash-stats');
    if(sc) sc.addEventListener('click',function(e){
      var card=e.target.closest('[data-nav]');
      if(card) navTo(card.getAttribute('data-nav'));
      var act=e.target.closest('[data-action]');
      if(act && act.getAttribute('data-action')==='hot-leads') filterAndGoToLeads('hot');
    });
  },50);
}



function renderKanbanBoard(){
  var board=document.getElementById('dash-kanban-board');
  if(!board)return;
  var stages=[
    {id:'not_contacted',label:'Not Contacted',color:'var(--tx3)'},
    {id:'contacted',    label:'Contacted',    color:'var(--amb)'},
    {id:'in_talks',     label:'In Talks',     color:'var(--pip)'},
    {id:'closed',       label:'Won',          color:'var(--grn)'},
    {id:'refused',      label:'Closed Lost',  color:'rgba(239,68,68,0.7)'}
  ];
  board.innerHTML='';
  stages.forEach(function(stage){
    var leads=DB.filter(function(r){return(r.outreach_status||'not_contacted')===stage.id;});
    var col=document.createElement('div');
    col.className='kanban-col';
    col.setAttribute('data-stage',stage.id);

    var hdr=document.createElement('div');
    hdr.className='kanban-col-header';
    hdr.innerHTML='<span class="kanban-col-title" style="color:'+stage.color+'">'+stage.label+'</span><span class="kanban-col-count">'+leads.length+'</span>';
    col.appendChild(hdr);

    if(!leads.length){
      var emp=document.createElement('div');
      emp.className='kanban-empty';
      emp.textContent='Drop here';
      col.appendChild(emp);
    }

    leads.forEach(function(r){
      var score=r.gtm_readiness_score||0;
      var scol=score>=75?'var(--pip2)':score>=50?'var(--amb)':'var(--tx3)';
      var card=document.createElement('div');
      card.className='kanban-card';
      card.draggable=true;
      card.setAttribute('data-id',r._id);

      var inner=document.createElement('div');
      inner.style.cssText='display:flex;align-items:flex-start;justify-content:space-between;gap:6px';

      var left=document.createElement('div');
      left.style.cssText='min-width:0';
      var name=document.createElement('div');
      name.className='kanban-card-name';
      name.textContent=r.company||'Unknown';
      var meta=document.createElement('div');
      meta.className='kanban-card-meta';
      meta.textContent=r.sector||r.stage||'';
      left.appendChild(name);
      left.appendChild(meta);

      var scoreEl=document.createElement('div');
      scoreEl.className='kanban-card-score';
      scoreEl.style.color=scol;
      scoreEl.textContent=score;

      inner.appendChild(left);
      inner.appendChild(scoreEl);
      card.appendChild(inner);

      card.addEventListener('dragstart',function(e){
        e.dataTransfer.setData('text/plain',r._id);
        card.classList.add('dragging');
        e.stopPropagation();
      });
      card.addEventListener('dragend',function(){card.classList.remove('dragging');});
      card.addEventListener('click',function(e){e.stopPropagation();openLeadDetail(r._id);});
      col.appendChild(card);
    });

    col.addEventListener('dragover',function(e){e.preventDefault();col.classList.add('drag-over');});
    col.addEventListener('dragleave',function(){col.classList.remove('drag-over');});
    col.addEventListener('drop',function(e){
      e.preventDefault();col.classList.remove('drag-over');
      var id=e.dataTransfer.getData('text/plain');
      var lead=DB.find(function(r){return r._id===id;});
      if(lead){lead.outreach_status=stage.id;save();renderKanbanBoard();}
    });

    board.appendChild(col);
  });
}

function renderDashStats(){
  renderDashboard();
}

function filterAndGoToLeads(filter){
  fil = filter;
  navTo('leads');
}

function openLeadDetail(id){
  var r = DB.find(function(x){return x._id===id;});
  if(!r) return;
  setPage('lead-detail');
  renderLeadDetail(r);
}

function renderLeadDetail(r){
  var cont = document.getElementById('lead-detail-content');
  if(!cont) return;
  var n = r.gtm_readiness_score||0;
  var c = sc(n);
  var g = r.gtm_signals||{};
  var ff = Array.isArray(r.founders)?r.founders:[];
  var site = r.website?(String(r.website).indexOf('http')===0?r.website:'https://'+r.website):'';
  var statusColors = {not_contacted:'var(--tx3)',contacted:'var(--amb)',in_talks:'var(--pip)',closed:'var(--grn)'};
  var statusLabels = {not_contacted:'Not Contacted',contacted:'Contacted',in_talks:'In Talks',closed:'Closed'};
  var curStatus = r.outreach_status||'not_contacted';
  var signals = [['recently_funded','Recently funded'],['no_cmo','No CMO'],
    ['pre_launch_or_early','Pre-launch'],['has_product','Has product'],
    ['small_team','Small team'],['marketing_gap_visible','Marketing gap']];
  var sigsHtml = signals.map(function(x){
    var v=g[x[0]],cls=v===true?'sy':v===false?'sn':'su',t=v===true?'Yes':v===false?'No':'?';
    return '<div class="sig-row"><span style="color:var(--tx2);font-size:12px">'+x[1]+'</span><span class="'+cls+'">'+t+'</span></div>';
  }).join('');
  var foundersHtml = ff.length ? ff.map(function(f){
    var ini=String(f.name||'?').split(' ').map(function(w){return w[0]||'';}).slice(0,2).join('').toUpperCase();
    return '<div class="founder-row"><div class="fav">'+ini+'</div><div><div class="fname">'+(f.name||'')+'</div><div class="frole">'+(f.role||'')+'</div></div></div>';
  }).join('') : '<span style="color:var(--tx3);font-size:13px">Unknown</span>';
  var detailPairs = [['Funding',r.funding_amount],['Stage',r.stage],['Team',r.employee_count],['HQ',r.hq]];
  var detailHtml = detailPairs.filter(function(x){return x[1];}).map(function(x){
    return '<div><div style="font-size:10px;color:var(--tx3);text-transform:uppercase;letter-spacing:.1em">'+x[0]+'</div><div style="font-size:13px;color:var(--tx);font-weight:600;margin-top:2px">'+x[1]+'</div></div>';
  }).join('');
  var statusBtns = ['not_contacted','contacted','in_talks','closed'].map(function(s){
    var active=curStatus===s;
    var col=statusColors[s];
    return '<button data-action="set-status" data-id="'+r._id+'" data-status="'+s+'" style="font-size:11px;font-weight:700;padding:6px 12px;border-radius:4px;cursor:pointer;font-family:Outfit,sans-serif;border:1px solid '+col+';color:'+col+';background:'+(active?col+'22':'none')+'">'+statusLabels[s]+'</button>';
  }).join('');
  var companyLink = site ? ' <a href="'+site+'" target="_blank" style="font-size:12px;color:var(--pip);text-decoration:none;border:1px solid var(--bor2);padding:2px 8px;border-radius:4px">visit</a>' : '';
  cont.innerHTML =
    '<div class="ld-header">'+
      '<div>'+
        '<div class="ld-name">'+(r.company||'')+companyLink+'</div>'+
        '<div class="ld-meta">'+(r.sector||'')+(r.stage?' · '+r.stage:'')+(r.hq?' · '+r.hq:'')+'</div>'+
      '</div>'+
      '<div style="text-align:right">'+
        '<div class="ld-score" style="color:'+c+'">'+n+'</div>'+
        '<div style="font-size:11px;font-weight:700;color:'+c+';text-transform:uppercase;letter-spacing:.1em">'+(r.gtm_label||'')+'</div>'+
      '</div>'+
    '</div>'+
    '<div class="ld-grid">'+
      '<div class="ld-section">'+
        '<div class="ld-section-title">Pitch Opener</div>'+
        '<div id="ld-pitch-text" style="font-size:13px;color:var(--tx2);line-height:1.7;margin-bottom:12px">'+(r.pitch_opener||'-')+'</div>'+
        '<button data-action="copy-pitch" style="background:var(--pip);color:#fff;border:none;font-size:12px;font-weight:700;padding:8px 18px;border-radius:var(--r);cursor:pointer;font-family:Outfit,sans-serif">Copy pitch</button>'+
      '</div>'+
      '<div>'+
        '<div class="ld-section" style="margin-bottom:12px">'+
          '<div class="ld-section-title">Status</div>'+
          '<div style="display:flex;gap:6px;flex-wrap:wrap">'+statusBtns+'</div>'+
        '</div>'+
        '<div class="ld-section">'+
          '<div class="ld-section-title">Details</div>'+
          '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">'+detailHtml+'</div>'+
        '</div>'+
      '</div>'+
      '<div class="ld-section">'+
        '<div class="ld-section-title">GTM Signals</div>'+sigsHtml+
      '</div>'+
      '<div class="ld-section">'+
        '<div class="ld-section-title">Founders</div>'+foundersHtml+
      '</div>'+
    '</div>'+
    '<div class="ld-section" style="margin:12px 0;display:flex;gap:8px;flex-wrap:wrap">'+
      '<button onclick="findOnLinkedIn()" style="display:flex;align-items:center;gap:6px;background:none;border:1px solid #0a66c2;color:#0a66c2;font-size:12px;font-weight:600;padding:7px 14px;border-radius:6px;cursor:pointer;font-family:Outfit,sans-serif">'+
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="#0a66c2"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'+
        'LinkedIn'+
      '</button>'+
      '<button onclick="exportToHubspot(window._currentLead)" style="display:flex;align-items:center;gap:6px;background:none;border:1px solid #ff7a59;color:#ff7a59;font-size:12px;font-weight:600;padding:7px 14px;border-radius:6px;cursor:pointer;font-family:Outfit,sans-serif">'+
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="#ff7a59"><path d="M18.164 7.93V5.084a2.198 2.198 0 001.267-1.978V3.04A2.198 2.198 0 0017.236.845h-.066a2.198 2.198 0 00-2.195 2.195v.066a2.198 2.198 0 001.267 1.978V7.93a6.232 6.232 0 00-2.967 1.297L7.21 5.038a2.438 2.438 0 10-1.168 1.439l5.95 4.116a6.232 6.232 0 000 2.814l-5.95 4.116a2.437 2.437 0 101.168 1.439l6.066-4.192a6.232 6.232 0 009.53-5.207 6.232 6.232 0 00-4.642-5.633z"/></svg>'+
        'HubSpot'+
      '</button>'+
      '<button onclick="exportToNotion(window._currentLead)" style="display:flex;align-items:center;gap:6px;background:none;border:1px solid var(--tx3);color:var(--tx2);font-size:12px;font-weight:600;padding:7px 14px;border-radius:6px;cursor:pointer;font-family:Outfit,sans-serif">'+
        '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M4.459 4.208c.746.606 1.026.56 2.428.466l13.215-.793c.28 0 .047-.28-.046-.326L17.86 1.968c-.42-.326-.981-.7-2.055-.607L3.01 2.295c-.466.046-.56.28-.374.466zm.793 3.08v13.904c0 .747.373 1.027 1.214.98l14.523-.84c.841-.046.935-.56.935-1.167V6.354c0-.606-.233-.933-.748-.887l-15.177.887c-.56.047-.747.327-.747.934zm14.337.745c.093.42 0 .84-.42.888l-.7.14v10.264c-.608.327-1.168.514-1.635.514-.748 0-.935-.234-1.495-.933l-4.577-7.186v6.952L12.21 19s0 .84-1.168.84l-3.222.186c-.093-.186 0-.653.327-.746l.84-.233V9.854L7.822 9.76c-.094-.42.14-1.026.793-1.073l3.456-.233 4.764 7.279v-6.44l-1.215-.14c-.093-.514.28-.887.747-.933zM1.936 1.035l13.31-.98c1.634-.14 2.055-.047 3.082.7l4.249 2.986c.7.513.934.653.934 1.213v16.378c0 1.026-.373 1.634-1.68 1.726l-15.458.934c-.98.047-1.448-.093-1.962-.747l-3.129-4.06c-.56-.747-.793-1.306-.793-1.96V2.667c0-.839.374-1.54 1.447-1.632z"/></svg>'+
        'Notion'+
      '</button>'+
      '<button onclick="openProposalModal(window._currentLead)" style="display:flex;align-items:center;gap:6px;background:var(--pip);color:#fff;font-size:12px;font-weight:600;padding:7px 16px;border-radius:6px;cursor:pointer;font-family:Outfit,sans-serif"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>Proposal</button>'+
    '</div>'+
    '<div class="ld-section" style="margin:12px 0;padding-top:8px;border-top:1px solid var(--bor)">'+
      '<button onclick="deleteCurrentLead()" style="background:none;border:1px solid rgba(239,68,68,0.4);color:rgba(239,68,68,0.8);font-size:12px;font-weight:600;padding:7px 16px;border-radius:6px;cursor:pointer;font-family:Outfit,sans-serif">Delete lead</button>'+
    '</div>'+
    '<div class="ld-section" style="margin:12px 0">'+
      '<div class="ld-section-title">Notes</div>'+
      '<textarea id="ld-notes" placeholder="Add notes..." style="width:100%;min-height:80px;background:var(--sur2);border:1px solid var(--bor2);color:var(--tx);font-family:Outfit,sans-serif;font-size:13px;padding:10px;border-radius:var(--r);resize:vertical;outline:none">'+(r._notes||'')+'</textarea>'+
    '</div>';
  // Wire notes
  setTimeout(function(){
    var ta = document.getElementById('ld-notes');
    if(ta) ta.addEventListener('input',function(){
      r._notes=ta.value; clearTimeout(r._nt);
      r._nt=setTimeout(function(){save();},800);
    });
  },50);
  // Store current lead for delegation
  window._currentLead = r;
}

function updateLeadStatus(id, status){
  var r = DB.find(function(x){return x._id===id;});
  if(!r) return;
  r.outreach_status = status;
  save();
  renderLeadDetail(r);
}




function renderLeads(){
  var shown=fil==='all'?DB:DB.filter(function(r){
    if(fil==='hot') return r.gtm_label==='Hot Lead';
    if(fil==='warm') return r.gtm_label==='Warm Lead';
    if(fil==='cold') return r.gtm_label==='Cold Lead';
    if(fil==='won') return r.outreach_status==='closed';
    return true;
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
          '<div class="lc-cell"><div class="lc-key">HQ</div><div class="lc-val'+(r.hq?'':' dim')+'">'+(r.hq||'-')+'</div></div>'+
          '<div class="lc-cell"><div class="lc-key">Founded</div><div class="lc-val'+(r.founded?'':' dim')+'">'+(r.founded||'-')+'</div></div>'+
          '<div class="lc-cell"><div class="lc-key">Team</div><div class="lc-val'+(r.employee_count?'':' dim')+'">'+(r.employee_count||'-')+'</div></div>'+
          '<div class="lc-cell"><div class="lc-key">Funding</div><div class="lc-val'+(r.funding_amount?'':' dim')+'">'+(r.funding_amount||'-')+'</div></div>'+
        '</div>'+
        (inv?'<div class="lc-sec">Investors</div><div class="lc-text">'+inv+'</div>':'') +
        '<div class="lc-sec">Socials</div>'+socHtml+
        '<div class="lc-sec">Founders</div>'+fndHtml+
        '<div class="lc-sec">GTM Signals</div><div>'+sigsHtml+'</div>'+
        '<div class="lc-sec">Why They Fit</div><div class="lc-text">'+(r.why_fit||'-')+'</div>'+
        '<div class="lc-sec">Reach Out To</div><div class="lc-text" style="color:var(--pip)">'+
          (r.best_contact_name&&r.best_contact_title?r.best_contact_name+' - '+r.best_contact_title:r.best_contact_title||r.decision_maker||'-')+
        '</div>'+
        '<div class="pitch-box"><div class="pitch-label">Pitch Opener</div><div class="pitch-text" id="pt'+id+'">'+(r.pitch_opener||'-')+'</div></div>'+
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
  // Group leads by stage
  var groups={};
  stages.forEach(function(s){ groups[s]=[]; });
  DB.forEach(function(r){ var s=r.outreach_status||'not_contacted'; if(groups[s]) groups[s].push(r); });
  // Render each stage as a compact section
  stages.forEach(function(stage){
    var leads=groups[stage];
    if(!leads.length) return;
    var section=document.createElement('div');
    section.style.cssText='margin-bottom:20px';
    var hdr=document.createElement('div');
    hdr.style.cssText='display:flex;align-items:center;gap:8px;margin-bottom:8px';
    var dot=document.createElement('div');
    dot.style.cssText='width:8px;height:8px;border-radius:50%;background:'+colors[stage]+';flex-shrink:0';
    var lbl=document.createElement('span');
    lbl.style.cssText='font-size:12px;font-weight:700;color:'+colors[stage]+';text-transform:uppercase;letter-spacing:.08em';
    lbl.textContent=labels[stage]+' ('+leads.length+')';
    hdr.appendChild(dot); hdr.appendChild(lbl);
    section.appendChild(hdr);
    leads.forEach(function(r){
      var row=document.createElement('div');
      row.style.cssText='display:flex;align-items:center;justify-content:space-between;padding:10px 14px;background:var(--sur2);border:1px solid var(--bor);border-radius:8px;margin-bottom:6px;cursor:pointer;transition:border-color .15s';
      row.onmouseover=function(){this.style.borderColor='var(--pip-bor)';};
      row.onmouseout=function(){this.style.borderColor='var(--bor)';};
      row.onclick=function(){ openLeadDetail(r._id); };
      var left=document.createElement('div');left.style.minWidth='0';
      var name=document.createElement('div');name.style.cssText='font-size:13px;font-weight:700;color:var(--tx);white-space:nowrap;overflow:hidden;text-overflow:ellipsis';name.textContent=r.company||'';
      var meta=document.createElement('div');meta.style.cssText='font-size:11px;color:var(--tx3);margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis';meta.textContent=(r.sector||'')+(r.stage?' · '+r.stage:'');
      left.appendChild(name);left.appendChild(meta);
      var right=document.createElement('div');right.style.cssText='display:flex;align-items:center;gap:8px;flex-shrink:0;margin-left:12px';
      var score=document.createElement('div');
      var sc=r.gtm_readiness_score||0;
      var scol=sc>=75?'var(--pip2)':sc>=50?'var(--amb)':'var(--tx3)';
      score.style.cssText='font-size:18px;font-weight:800;color:'+scol+';font-family:JetBrains Mono,monospace;letter-spacing:-.04em';
      score.textContent=sc;
      var del=document.createElement('button');
      del.style.cssText='background:none;border:none;color:rgba(239,68,68,0.5);font-size:16px;cursor:pointer;padding:2px 6px;border-radius:4px;line-height:1';
      del.textContent='×';
      del.title='Delete';
      del.onclick=function(e){
        e.stopPropagation();
        if(!confirm('Delete '+( r.company||'this lead')+'?'))return;
        DB=DB.filter(function(x){return x._id!==r._id;});
        save();updateBadges();renderPipelinePage();
        showUpsellToast((r.company||'Lead')+' deleted');
      };
      right.appendChild(score);right.appendChild(del);
      row.appendChild(left);row.appendChild(right);
      section.appendChild(row);
    });
    cont.appendChild(section);
  });
  if(!DB.length){
    cont.innerHTML='<div style="text-align:center;padding:40px 0;color:var(--tx3);font-size:13px">No leads in pipeline yet.</div>';
  }
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
            '<div class="inbox-card-meta" style="max-width:200px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">'+(r.sector||'')+((r.sector&&r.stage)?' · ':'')+( r.stage||'')+'</div>'+
          '</div>'+
          '<div style="text-align:right;flex-shrink:0;min-width:60px">'+
            '<div style="font-size:22px;font-weight:800;color:'+c+';line-height:1">'+n+'</div>'+
            '<div style="font-size:9px;font-weight:700;color:'+c+';border:1px solid '+c+';padding:2px 8px;border-radius:999px;display:inline-block;margin-top:4px;white-space:nowrap">'+(r.gtm_label||'')+'</div>'+
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
var PH_HISTORY = []; // Array of {type, query, results, ts}
var PH_JOBS = [];
var PH_SAVED = [];
var PH_APPLIED = [];
var PH_SAVED_CANDIDATES = [];
var PH_TRASH_CANDIDATES = [];
var phBottomTab = 'saved';
var phCategory = 'cmo';
var phFilters = {remote: false, startup: false, week: false};

var PH_SYS_CMO = "You are a JSON API. Search the web for open job postings right now. Return ONLY a raw JSON array with no other text, no markdown, no explanation, no backticks. Start your response with [ and end with ]. Each object must have these exact keys: role, company, location, remote (true/false), salary (string or null), posted (e.g. 2 days ago), apply_method (link or email or linkedin), apply_url (full URL or email), description (one sentence), sector. Search for: CMO, VP Marketing, Head of Marketing, Head of Growth, VP Growth at funded tech and AI startups. Return 6-8 real current openings only.";

var PH_SYS_DESIGN = "You are a JSON API. Search the web for open job postings right now. Return ONLY a raw JSON array with no other text, no markdown, no explanation, no backticks. Start your response with [ and end with ]. Each object must have these exact keys: role, company, location, remote (true/false), salary (string or null), posted (e.g. 2 days ago), apply_method (link or email or linkedin), apply_url (full URL or email), description (one sentence), sector. Search for: Head of Design, VP Design, Creative Director, Brand Director, Head of Brand at funded tech and AI startups. Return 6-8 real current openings only.";

function phSetCategory(cat){
  phCategory=cat;
  document.querySelectorAll('.ph-tab').forEach(function(b){
    var on=b.getAttribute('data-cat')===cat;
    b.style.cssText='background:'+(on?'var(--pip)':'var(--sur2)')+';color:'+(on?'#fff':'var(--tx3)')+';border:1px solid '+(on?'var(--pip)':'var(--bor2)')+';font-size:12px;font-weight:600;padding:7px 16px;border-radius:999px;cursor:pointer;font-family:Outfit,sans-serif';
  });
  phRenderJobs();
}

function phToggleFilter(f){
  phFilters[f]=!phFilters[f];
  var btn=document.getElementById('ph-filter-'+f);
  if(btn){btn.style.background=phFilters[f]?'var(--pip)':'var(--sur2)';btn.style.color=phFilters[f]?'#fff':'var(--tx3)';btn.style.borderColor=phFilters[f]?'var(--pip)':'var(--bor)';}
  phRenderJobs();
}


function phFetch(){
  if(!tierCanPipHunt())return;
  var btn=document.getElementById('ph-fetch-btn');
  var status=document.getElementById('ph-status');
  if(btn)btn.disabled=true;
  if(status)status.textContent='Searching...';
  // Use custom search input if filled, otherwise use category
  var inp=document.getElementById('ph-search-input');
  var customQ=inp?inp.value.trim():'';
  var sites='site:linkedin.com/jobs OR site:indeed.com OR site:glassdoor.com OR site:ziprecruiter.com OR site:monster.com OR site:dice.com OR site:flexjobs.com OR site:upwork.com';
  var sys, query;
  if(customQ){
    sys='You are a JSON API. Search the web for real open job postings matching: "'+customQ+'". Only search these sites: '+sites+'. Return ONLY a raw JSON array starting with [. Each object: role, company, location, remote(bool), salary, posted, apply_method, apply_url, description(1 sentence), sector. Use null for unknown. No markdown.';
    query=sites+' "'+customQ+'" 2026';
  } else if(phCategory==='cmo'){
    sys=PH_SYS_CMO; query=sites+' (CMO OR "VP Marketing" OR "Head of Marketing" OR "Head of Growth") startup 2026';
  } else if(phCategory==='design'){
    sys=PH_SYS_DESIGN; query=sites+' ("Head of Design" OR "VP Design" OR "Creative Director") startup 2026';
  } else {
    sys=PH_SYS_FRACTIONAL; query=sites+' ("fractional CMO" OR "fractional VP Marketing" OR "fractional marketing" OR "interim CMO" OR "part-time CMO") 2026';
  }
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({key:'',company:query,system:sys,mode:'fetch'})})
  .then(function(r){return r.json();})
  .then(function(d){
    if(d.error)throw new Error(d.error);
    var t=(d.text||'').replace(/```json/g,'').replace(/```/g,'').trim();
    var a=t.indexOf('['),b=t.lastIndexOf(']');
    var jobs=[];
    if(a>=0&&b>a){try{jobs=JSON.parse(t.slice(a,b+1));}catch(e){}}
    if(!jobs.length){if(status)status.textContent='No results - try again';setTimeout(function(){if(status)status.textContent='';},3000);return;}
    jobs=jobs.filter(function(j){return j.company||j.role;});
    jobs.forEach(function(j){
      j._id='ph'+Date.now()+Math.floor(Math.random()*9999);
      j._cat=customQ?phCategory:phCategory;
      j.role=j.role||j.title||j.position||'Open Role';
      j.company=j.company||j.employer||'Unknown';
      j.apply_url=j.apply_url||j.url||j.link||null;
      j.remote=j.remote||j.is_remote||(j.location&&j.location.toLowerCase().indexOf('remote')>=0)||false;
    });
    // Replace results for this category
    PH_JOBS=PH_JOBS.filter(function(j){return j._cat!==phCategory;}).concat(jobs);
    phSave();phRenderJobs();
    if(inp)inp.value='';
    if(status){status.textContent=jobs.length+' jobs found';setTimeout(function(){status.textContent='';},3000);}
  })
  .catch(function(e){if(status){status.textContent='Error: '+e.message;setTimeout(function(){status.textContent='';},4000);}})
  .finally(function(){if(btn)btn.disabled=false;});
}



function phSave(){
  try{localStorage.setItem('ph_jobs',JSON.stringify(PH_JOBS));}catch(e){}
  try{localStorage.setItem('ph_saved',JSON.stringify(PH_SAVED));}catch(e){}
  try{localStorage.setItem('ph_applied',JSON.stringify(PH_APPLIED));}catch(e){}
  try{localStorage.setItem('ph_saved_candidates',JSON.stringify(PH_SAVED_CANDIDATES));}catch(e){}
  try{localStorage.setItem('ph_trash_candidates',JSON.stringify(PH_TRASH_CANDIDATES));}catch(e){}
  try{localStorage.setItem('ph_history',JSON.stringify(PH_HISTORY));}catch(e){}
}

function phLoad(){
  try{var j=localStorage.getItem('ph_jobs');if(j)PH_JOBS=JSON.parse(j);}catch(e){}
  try{var s=localStorage.getItem('ph_saved');if(s)PH_SAVED=JSON.parse(s);}catch(e){}
  try{var ap=localStorage.getItem('ph_applied');if(ap)PH_APPLIED=JSON.parse(ap);}catch(e){}
  try{var sc2=localStorage.getItem('ph_saved_candidates');if(sc2)PH_SAVED_CANDIDATES=JSON.parse(sc2);}catch(e){}
  try{var tr=localStorage.getItem('ph_trash_candidates');if(tr){PH_TRASH_CANDIDATES=JSON.parse(tr);pruneTrash();}}catch(e){}
  try{var ph=localStorage.getItem('ph_history');if(ph){PH_HISTORY=JSON.parse(ph);}}catch(e){}
}

function phSaveJob(id){
  var job=PH_JOBS.find(function(j){return j._id===id;});
  if(!job)return;
  if(!PH_SAVED.some(function(j){return j._id===id;}))PH_SAVED.unshift(job);
  PH_JOBS=PH_JOBS.filter(function(j){return j._id!==id;});
  phSave();phRenderJobs();
  showInfoToast('Saved to Saved Jobs ✓');
}


function phRemoveSaved(id){
  PH_SAVED=PH_SAVED.filter(function(j){return j._id!==id;});
  phSave();
  phRenderJobs();
}

function phResearchInScout(company){
  setPage('dashboard');
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
  var savedIds=PH_SAVED.map(function(j){return j._id;});
  var appliedIds=PH_APPLIED.map(function(j){return j._id;});
  var jobs=PH_JOBS.filter(function(j){return savedIds.indexOf(j._id)<0&&appliedIds.indexOf(j._id)<0;});
  if(phFilters.remote)jobs=jobs.filter(function(j){return j.remote;});
  if(phFilters.startup)jobs=jobs.filter(function(j){var s=(j.sector||j.description||'').toLowerCase();return s.indexOf('ai')>=0||s.indexOf('tech')>=0||s.indexOf('saas')>=0||s.indexOf('fintech')>=0;});
  if(phFilters.week)jobs=jobs.filter(function(j){var p=(j.posted||'').toLowerCase();return p.indexOf('day')>=0||p.indexOf('hour')>=0||p.indexOf('today')>=0;});
  if(!jobs.length&&!PH_SAVED.length&&!PH_APPLIED.length){
    cont.innerHTML='<div style="grid-column:1/-1;text-align:center;padding:40px 0;color:var(--tx3);font-size:13px">Search for a role above to find open positions</div>';
  } else if(!jobs.length){
    cont.innerHTML='<div style="grid-column:1/-1;text-align:center;padding:20px 0;color:var(--tx3);font-size:13px">No results matching filters</div>';
  }
  jobs.forEach(function(job){
    var id=job._id;
    var card=document.createElement('div');card.className='ph-card';
    var applyHtml='';
    if(job.apply_url){
      var isEmail2=job.apply_method==='email'||job.apply_url.indexOf('@')>=0;
      var isLI2=(job.apply_url||'').indexOf('linkedin')>=0;
      var methodLabel=isEmail2?'Email':isLI2?'LinkedIn':'Apply';
      var displayUrl=job.apply_url.replace(/^https?:\/\//,'').slice(0,50);
      applyHtml='<div class="ph-apply"><span class="ph-apply-method">'+methodLabel+'</span>'+(isEmail2?'<span class="ph-apply-link">'+job.apply_url+'</span>':'<a class="ph-apply-link" href="'+job.apply_url+'" target="_blank">'+displayUrl+'</a>')+'</div>';
    }
    card.innerHTML='<div class="ph-card-header"><div class="ph-card-role">'+(job.role||'')+'</div><div class="ph-card-company">'+(job.company||'')+'</div><div class="ph-card-meta">'+(job.location?'<span class="ph-tag">'+job.location+'</span>':'')+(job.remote?'<span class="ph-tag remote">Remote</span>':'')+(job.salary?'<span class="ph-tag salary">'+job.salary+'</span>':'')+(job.posted?'<span class="ph-tag new">'+job.posted+'</span>':'')+'</div></div><div class="ph-card-body">'+(job.description?'<div class="ph-desc">'+job.description+'</div>':'')+applyHtml+'</div><div class="ph-card-actions" id="pha-'+id+'"></div>';
    var acts=card.querySelector('.ph-card-actions');
    var applyBtn=document.createElement('button');applyBtn.className='abtn g';applyBtn.textContent=job.apply_url?(job.apply_url.indexOf('@')>=0?'Copy & Apply':'Apply'):'Mark Applied';
    (function(jid){applyBtn.onclick=function(){phApplyJob(jid);};})(id);acts.appendChild(applyBtn);
    var saveBtn=document.createElement('button');saveBtn.className='abtn';saveBtn.textContent='Save';
    (function(jid){saveBtn.onclick=function(){phSaveJob(jid);};})(id);acts.appendChild(saveBtn);
    var rBtn=document.createElement('button');rBtn.className='abtn';rBtn.textContent='Research';
    (function(co){rBtn.onclick=function(){phResearchInScout(co);};})(job.company);acts.appendChild(rBtn);
    var rmBtn=document.createElement('button');rmBtn.className='abtn ghost';rmBtn.textContent='Remove';
    (function(jid){rmBtn.onclick=function(){PH_JOBS=PH_JOBS.filter(function(j){return j._id!==jid;});phSave();phRenderJobs();};})(id);acts.appendChild(rmBtn);
    cont.appendChild(card);
  });
  // Bottom section
  var bs=document.getElementById('ph-bottom-section');
  if(bs)bs.style.display=(PH_SAVED.length||PH_APPLIED.length)?'block':'none';
  // Saved grid
  var sg=document.getElementById('ph-saved-grid');
  if(sg){
    sg.style.display=phBottomTab==='saved'?'block':'none';
    sg.innerHTML='';
    if(!PH_SAVED.length){sg.innerHTML='<div style="padding:16px 0;color:var(--tx3);font-size:12px">No saved jobs yet</div>';}
    else{PH_SAVED.forEach(function(job){
      var id=job._id;var mini=document.createElement('div');mini.className='ph-card saved';
      mini.innerHTML='<div class="ph-card-header"><div class="ph-card-role">'+(job.role||'')+'</div><div class="ph-card-company">'+(job.company||'')+'</div><div class="ph-card-meta">'+(job.location?'<span class="ph-tag">'+job.location+'</span>':'')+(job.remote?'<span class="ph-tag remote">Remote</span>':'')+(job.salary?'<span class="ph-tag salary">'+job.salary+'</span>':'')+(job.posted?'<span class="ph-tag new">'+job.posted+'</span>':'')+'</div></div>'+(job.description?'<div class="ph-card-body"><div class="ph-desc">'+job.description+'</div>'+(job.apply_url&&job.apply_url.indexOf('@')<0?'<div class="ph-apply"><a class="ph-apply-link" href="'+job.apply_url+'" target="_blank">'+job.apply_url.replace(/^https?:\/\//,'').slice(0,50)+'</a></div>':'')+'</div>':'')+'<div class="ph-card-actions"></div>';
      var acts=mini.querySelector('.ph-card-actions');
      var ab=document.createElement('button');ab.className='abtn g';ab.textContent=job.apply_url?'Apply':'Mark Applied';
      (function(jid){ab.onclick=function(){phApplyJob(jid);};})(id);acts.appendChild(ab);
      if(job.apply_url&&job.apply_url.indexOf('@')<0){var oa=document.createElement('a');oa.href=job.apply_url;oa.target='_blank';oa.className='abtn';oa.style.textDecoration='none';oa.textContent='Open';acts.appendChild(oa);}
      var unBtn=document.createElement('button');unBtn.className='abtn ghost';unBtn.textContent='Remove';
      (function(jid){unBtn.onclick=function(){PH_SAVED=PH_SAVED.filter(function(j){return j._id!==jid;});phSave();phRenderJobs();};})(id);acts.appendChild(unBtn);
      sg.appendChild(mini);
    });}
  }
  // Applied grid
  var ag=document.getElementById('ph-applied-grid');
  if(ag){
    ag.style.display=phBottomTab==='applied'?'block':'none';
    ag.innerHTML='';
    if(!PH_APPLIED.length){ag.innerHTML='<div style="padding:16px 0;color:var(--tx3);font-size:12px">No applications yet - click Apply on any job to track it here</div>';}
    else{PH_APPLIED.forEach(function(job){
      var id=job._id;var mini=document.createElement('div');mini.className='ph-card saved';
      mini.innerHTML='<div class="ph-card-header"><div class="ph-card-role">'+(job.role||'')+'</div><div class="ph-card-company">'+(job.company||'')+'</div><div class="ph-card-meta">'+(job._applied_at?'<span class="ph-tag">Applied '+job._applied_at+'</span>':'')+(job.location?'<span class="ph-tag">'+job.location+'</span>':'')+(job.remote?'<span class="ph-tag remote">Remote</span>':'')+(job.salary?'<span class="ph-tag salary">'+job.salary+'</span>':'')+'</div></div>'+(job.description?'<div class="ph-card-body"><div class="ph-desc">'+job.description+'</div></div>':'')+'<div class="ph-card-actions"></div>';
      var acts=mini.querySelector('.ph-card-actions');
      if(job.apply_url&&job.apply_url.indexOf('@')<0){var oa2=document.createElement('a');oa2.href=job.apply_url;oa2.target='_blank';oa2.className='abtn g';oa2.style.textDecoration='none';oa2.textContent='Open Application';acts.appendChild(oa2);}
      var rmBtn2=document.createElement('button');rmBtn2.className='abtn ghost';rmBtn2.textContent='Remove';
      (function(jid){rmBtn2.onclick=function(){PH_APPLIED=PH_APPLIED.filter(function(j){return j._id!==jid;});phSave();phRenderJobs();};})(id);acts.appendChild(rmBtn2);
      ag.appendChild(mini);
    });}
  }
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





// ── PROFILE ──────────────────────────────────────────────────────────────────
var PROFILE = {
  name: '', tagline: '', bio: '',
  linkedin: '', twitter: '', website: '',
  avatar: null,
  services: [],
  cases: [],
  wl_logo: null
};

function profileLoad(){
  try{var p=localStorage.getItem('scout_profile');if(p)PROFILE=JSON.parse(p);}catch(e){}
}

function profileSave(){
  try{localStorage.setItem('scout_profile',JSON.stringify(PROFILE));}catch(e){}
  renderProfile();
}

function teamsLoad(){try{var t=localStorage.getItem('scout_team');return t?JSON.parse(t):{members:[]};}catch(e){return{members:[]};}}
function teamsSave(t){try{localStorage.setItem('scout_team',JSON.stringify(t));}catch(e){}}
function renderTeams(){
  var root=document.getElementById('teams-root');if(!root)return;
  var tier=tierLoad();var isAgency=tier.plan==='agency'||tier._master;
  var team=teamsLoad();var members=team.members||[];
  var user=authGetUser();var ownerEmail=user?user.email:'you';
  if(!isAgency){
    root.innerHTML='<div style="text-align:center;padding:32px"><div style="font-size:32px;margin-bottom:12px">&#128101;</div><div style="font-size:16px;font-weight:700;color:var(--tx);margin-bottom:8px">Teams is an Agency feature</div><div style="font-size:13px;color:var(--tx3);margin-bottom:20px">Upgrade to Agency ($179/mo) for 5 seats. Extra seats $20/seat/mo.</div><button onclick="showPricing()" style="background:var(--pip);color:#fff;border:none;font-family:Outfit,sans-serif;font-size:13px;font-weight:700;padding:11px 28px;border-radius:8px;cursor:pointer">Upgrade to Agency</button></div>';
    return;
  }
  var maxSeats=5;var usedSeats=members.length;var pct=Math.round(((usedSeats+1)/maxSeats)*100);
  var html='<div style="background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);padding:20px;margin-bottom:16px"><div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px"><div style="font-size:14px;font-weight:700;color:var(--tx)">Seats used</div><div style="font-size:13px;font-weight:700;color:var(--pip2)">'+(usedSeats+1)+' / '+maxSeats+'</div></div><div style="height:6px;background:var(--bor2);border-radius:3px;overflow:hidden"><div style="height:100%;background:var(--pip);border-radius:3px;width:'+pct+'%"></div></div></div>';
  html+='<div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--tx3);margin-bottom:10px">Members</div>';
  html+='<div style="background:var(--sur);border:1px solid var(--bor2);border-radius:var(--r);overflow:hidden;margin-bottom:16px">';
  html+='<div style="display:flex;align-items:center;gap:14px;padding:16px 20px;border-bottom:1px solid var(--bor)"><div style="width:40px;height:40px;border-radius:50%;background:var(--pip);display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;color:#fff">'+(ownerEmail[0]||'?').toUpperCase()+'</div><div style="flex:1"><div style="font-size:14px;font-weight:600;color:var(--tx)">'+ownerEmail+'</div><div style="font-size:12px;color:var(--tx3)">Owner</div></div><div style="font-size:11px;font-weight:700;color:var(--pip2);padding:3px 10px;background:var(--pip-dim);border-radius:4px">OWNER</div></div>';
  members.forEach(function(m,i){html+='<div style="display:flex;align-items:center;gap:14px;padding:16px 20px;border-bottom:1px solid var(--bor)"><div style="width:40px;height:40px;border-radius:50%;background:var(--sur2);border:1px solid var(--bor2);display:flex;align-items:center;justify-content:center;font-size:15px;font-weight:700;color:var(--tx2)">'+(m.email?m.email[0].toUpperCase():'?')+'</div><div style="flex:1"><div style="font-size:14px;font-weight:600;color:var(--tx)">'+m.email+'</div><div style="font-size:12px;color:var(--tx3)">'+(m.status==='pending'?'Invite pending':'Member')+'</div></div><div style="display:flex;gap:8px">'+(m.status==='pending'?'<div style="font-size:11px;font-weight:700;color:var(--amb);padding:3px 8px;background:rgba(245,158,11,0.1);border-radius:4px">PENDING</div>':'<div style="font-size:11px;font-weight:700;color:var(--grn);padding:3px 8px;background:rgba(16,185,129,0.1);border-radius:4px">ACTIVE</div>')+'<button onclick="teamsRemoveMember('+i+')" style="background:none;border:1px solid rgba(239,68,68,0.3);color:rgba(239,68,68,0.7);font-size:12px;font-weight:600;padding:4px 10px;border-radius:4px;cursor:pointer;font-family:Outfit,sans-serif">Remove</button></div></div>';});
  html+='</div>';
  if(usedSeats<maxSeats-1){html+='<div style="background:var(--sur);border:1px solid var(--bor2);border-radius:var(--r);padding:24px"><div style="font-size:16px;font-weight:700;color:var(--tx);margin-bottom:6px">Add a team member</div><div style="font-size:13px;color:var(--tx3);line-height:1.7;margin-bottom:18px">Each additional seat is <strong style="color:var(--tx)">$20/seat/mo</strong>. Purchase first, then enter their email to send an invite.</div><div style="display:flex;flex-direction:column;gap:12px"><a href="https://buy.stripe.com/3cIdR9djs9Wufda5TYbjW06" target="_blank" style="display:flex;align-items:center;justify-content:center;gap:8px;background:var(--pip);color:#fff;font-family:Outfit,sans-serif;font-size:14px;font-weight:700;padding:13px 24px;border-radius:8px;text-decoration:none;text-align:center">+ Add seat — $20/mo</a><div style="border-top:1px solid var(--bor);padding-top:14px;display:none" id="teams-invite-section"><div style="font-size:12px;color:var(--tx3);margin-bottom:10px">Once payment is confirmed, enter their email:</div><div style="display:flex;gap:10px"><input id="teams-invite-email" class="modal-input" type="email" placeholder="colleague@company.com" style="flex:1;font-size:14px;padding:12px 16px"><button onclick="teamsInvite()" style="background:var(--sur2);color:var(--tx2);border:1px solid var(--bor2);font-family:Outfit,sans-serif;font-size:14px;font-weight:700;padding:12px 22px;border-radius:8px;cursor:pointer">Send invite</button></div></div></div></div>';}
  else{html+='<div style="padding:16px;text-align:center;font-size:13px;color:var(--tx3)">All '+maxSeats+' seats filled. <a href="https://buy.stripe.com/3cIdR9djs9Wufda5TYbjW06" target="_blank" style="color:var(--pip2);font-weight:700">Buy extra seat</a></div>';}
  root.innerHTML=html;
}
function teamsInvite(){
  var email=(document.getElementById('teams-invite-email')||{value:''}).value.trim().toLowerCase();
  if(!email||email.indexOf('@')<0){showInfoToast('Enter a valid email');return;}
  var team=teamsLoad();var members=team.members||[];var user=authGetUser();
  if(user&&email===user.email){showInfoToast('That is your own email');return;}
  if(members.some(function(m){return m.email===email;})){showInfoToast('Already in team');return;}
  var cost=members.length>=4?'This will cost $20/mo extra.':'Included in your plan.';
  if(!confirm('Invite '+email+'? '+cost))return;
  members.push({email:email,status:'pending',invited:new Date().toISOString()});
  team.members=members;teamsSave(team);showInfoToast('Invite sent to '+email+' checked');renderTeams();
}
function teamsRemoveMember(idx){
  var team=teamsLoad();var members=team.members||[];var removed=members[idx];
  if(!removed)return;
  if(!confirm('Remove '+removed.email+'?'))return;
  members.splice(idx,1);team.members=members;teamsSave(team);showInfoToast(removed.email+' removed');renderTeams();
}
function renderProfile(){
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
  var servicesHtml = (PROFILE.services||[]).map(function(s,i){
    var sobj=typeof s==='object'?s:{name:s,desc:'',price:''};
    return '<div style="display:flex;align-items:flex-start;justify-content:space-between;background:var(--sur2);border:1px solid var(--bor);border-radius:6px;padding:10px 12px;margin-bottom:6px">'+
      '<div style="min-width:0"><div style="font-size:13px;font-weight:700;color:var(--tx)">'+(sobj.name||'')+'</div>'+
      (sobj.desc?'<div style="font-size:11px;color:var(--tx3);margin-top:2px">'+(sobj.desc||'')+'</div>':'')+
      '</div>'+
      '<div style="display:flex;align-items:center;gap:8px;flex-shrink:0;margin-left:8px">'+
      (sobj.price?'<span style="font-size:11px;color:var(--pip2);font-weight:700">'+sobj.price+'</span>':'')+
      '<button onclick="profileRemoveService('+i+')" style="background:none;border:none;color:var(--tx3);cursor:pointer;font-size:16px;line-height:1;padding:0">&times;</button>'+
      '</div></div>';
  }).join('') + '<button class="prof-tag-add" onclick="profileAddService()">+ Add service</button>';
  var casesHtml = (PROFILE.cases||[]).map(function(c,i){
    var metrics = (c.metrics||[]).map(function(m){return '<span class="case-metric">'+m+'</span>';}).join('');
    return '<div class="case-card" onclick="profileEditCase('+i+')">'
      +'<div class="case-card-client">'+(c.client||'Client')+'</div>'
      +'<div class="case-card-title">'+(c.title||'')+'</div>'
      +'<div class="case-card-result">'+(c.result||'')+'</div>'
      +(metrics?'<div class="case-metrics">'+metrics+'</div>':'')
      +'</div>';
  }).join('') + ((PROFILE.cases&&PROFILE.cases.length)?'':'<button class="case-card-add" onclick="profileAddCase()">+ Add Case Study</button>');
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
        (plan==='free'||plan==='starter'||plan==='pro'?'<button class="prof-upgrade-btn" onclick="showPricing()">'+(plan==='pro'?'Upgrade to Agency':plan==='starter'?'Upgrade to Pro':'Upgrade')+'</button>':'')+
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
          '<div class="prof-field"><div class="prof-field-label">Role</div><div class="prof-field-val">'+(PROFILE.role||'-')+'</div></div>'+
          '<div class="prof-field"><div class="prof-field-label">Location</div><div class="prof-field-val">'+(PROFILE.location||'-')+'</div></div>'+
          '<div class="prof-field"><div class="prof-field-label">Industries</div><div class="prof-field-val">'+(PROFILE.industries||'-')+'</div></div>'+
          '<div class="prof-field"><div class="prof-field-label">Ideal Stage</div><div class="prof-field-val">'+(PROFILE.funding_stage||'-')+'</div></div>'+
          '<div class="prof-field"><div class="prof-field-label">Deal Size</div><div class="prof-field-val">'+(PROFILE.deal_size||'-')+'</div></div>'+
          '<div class="prof-field"><div class="prof-field-label">Availability</div><div class="prof-field-val">'+(PROFILE.availability||'-')+'</div></div>'+
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
    "linkedin","twitter","website","calendly","phone","min_score"];
  fields.forEach(function(f){
    var el=document.getElementById("pm-"+f);
    if(el) PROFILE[f]=el.value.trim();
  });
  // Save directly to localStorage first, then close, then re-render
  try{localStorage.setItem('scout_profile',JSON.stringify(PROFILE));}catch(e){}
  closeProfileModal();
  renderProfile();
}





function closeServiceModal(){var m=document.getElementById('add-service-modal');if(m)m.remove();}
function profileAddService(){
  // Remove any existing modal
  var ex=document.getElementById('add-service-modal');if(ex)ex.remove();
  var overlay=document.createElement('div');
  overlay.id='add-service-modal';
  overlay.style.cssText='position:fixed;inset:0;background:rgba(0,0,0,0.7);z-index:1000;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px)';
  overlay.innerHTML='<div style="background:var(--sur);border:1px solid var(--bor2);border-radius:var(--r);padding:28px;width:380px;max-width:95vw;display:flex;flex-direction:column;gap:14px">'
    +'<div style="font-size:15px;font-weight:700;color:var(--tx);margin-bottom:4px">Add service</div>'
    +'<input id="asvc-name" class="modal-input" placeholder="Service name (e.g. GTM Strategy)" style="font-size:13px;padding:11px 14px">'
    +'<input id="asvc-desc" class="modal-input" placeholder="Short description (1 sentence)" style="font-size:13px;padding:11px 14px">'
    +'<input id="asvc-price" class="modal-input" placeholder="Price range (e.g. $3k–$8k/mo)" style="font-size:13px;padding:11px 14px">'
    +'<div style="display:flex;gap:10px;margin-top:4px">'
    +'<button onclick="saveServiceModal()" style="flex:1;background:var(--pip);color:#fff;border:none;font-family:Outfit,sans-serif;font-size:13px;font-weight:700;padding:11px;border-radius:8px;cursor:pointer">Save service</button>'
    +'<button onclick="closeServiceModal()" style="flex:1;background:none;border:1px solid var(--bor2);color:var(--tx2);font-family:Outfit,sans-serif;font-size:13px;padding:11px;border-radius:8px;cursor:pointer">Cancel</button>'
    +'</div></div>';
  document.body.appendChild(overlay);
  overlay.addEventListener('click',function(e){if(e.target===overlay)closeServiceModal();});
  setTimeout(function(){var n=document.getElementById('asvc-name');if(n)n.focus();},50);
}
function saveServiceModal(){
  var name=(document.getElementById('asvc-name')||{}).value||'';
  var desc=(document.getElementById('asvc-desc')||{}).value||'';
  var price=(document.getElementById('asvc-price')||{}).value||'';
  if(!name.trim()){var n=document.getElementById('asvc-name');if(n)n.style.borderColor='var(--red)';return;}
  if(!PROFILE.services)PROFILE.services=[];
  PROFILE.services.push({name:name.trim(),desc:desc,price:price});
  try{localStorage.setItem('scout_profile',JSON.stringify(PROFILE));}catch(e){}
  closeServiceModal();
  renderProfile();
  showInfoToast('Service added ✓');
}
function profileRemoveService(idx){
  if(!PROFILE.services)return;
  PROFILE.services.splice(idx,1);
  try{localStorage.setItem('scout_profile',JSON.stringify(PROFILE));}catch(e){}
  renderProfile();
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
  var url=safeOrigin()+'?profile='+encodeURIComponent(PROFILE.name||'me');
  navigator.clipboard.writeText(url);
  var btn=document.querySelector('.profile-share-btn');
  if(btn){btn.textContent='Copied!';setTimeout(function(){btn.textContent='Share Profile';},2000);}
}






// ── TIER / CREDITS SYSTEM ─────────────────────────────────────────────────────
var TIER_LIMITS = {free:{research:5,fetch:2,piphunt:5}, starter:{research:50,fetch:5,piphunt:20}, pro:{research:300,fetch:30,piphunt:999}, agency:{research:750,fetch:100,piphunt:9999}};
var TIER_LABELS = {free:'Free',starter:'Starter',pro:'Pro',agency:'Agency'};

function tierLoad(){
  var _u=authGetUser();
  var _masters=['cara@sushicat.info','scott@cndtlabs.io'];
  if(_u&&_masters.indexOf(_u.email)>=0){
    return {plan:'agency',research_used:0,fetch_used:0,piphunt_used:0,period:new Date().toISOString(),_master:true};
  }

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
  var u=authGetUser();if(u&&['cara@sushicat.info','scott@cndtlabs.io'].indexOf(u.email)>=0)return true;
  var t=tierReset(tierLoad());
  var limit=TIER_LIMITS[t.plan||'free'].research;
  if(t.research_used>=limit){
    var plan=t.plan||'free';
    if(plan==='agency'||t._master){
      showLimitToast('You\u2019ve used all '+limit+' researches this month. <a href="https://buy.stripe.com/3cI5kDfrA9WufdabeibjW02" target="_blank" style="color:var(--pip);font-weight:700">Top up →</a>');
    } else {
      var upMsg=smartUpgradeMsg()||'';
      showLimitToast('You\u2019ve used all '+limit+' researches. <a href="https://buy.stripe.com/3cI5kDfrA9WufdabeibjW02" target="_blank" style="color:var(--pip);font-weight:700">Top up</a>'+(upMsg?' or '+upMsg:''));
    }
    return false;
  }
  return true;
}


function tierCanFetch(){
  var u=authGetUser();if(u&&['cara@sushicat.info','scott@cndtlabs.io'].indexOf(u.email)>=0)return true;
  var t=tierReset(tierLoad());
  var limit=TIER_LIMITS[t.plan||'free'].fetch;
  if(t.fetch_used>=limit){
    var plan=t.plan||'free';
    if(plan==='agency'||t._master){
      showLimitToast('You\u2019ve used all '+limit+' fetches this month. <a href="https://buy.stripe.com/3cI5kDfrA9WufdabeibjW02" target="_blank" style="color:var(--pip);font-weight:700">Top up →</a>');
    } else {
      var upMsg=smartUpgradeMsg()||'';
      showLimitToast('You\u2019ve used all '+limit+' fetches.'+(upMsg?' '+upMsg:''));
    }
    return false;
  }
  return true;
}


function tierCanPipHunt(){
  var u=authGetUser();if(u&&u.email==='cara@sushicat.info')return true;
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
  var fillEl = document.getElementById('credits-fill');
  var countEl = document.getElementById('credits-count');
  if(fillEl){ fillEl.style.width = pct+'%'; fillEl.style.background = pct>=80?'var(--red)':'var(--pip)'; }
  if(countEl) countEl.textContent = (lim.research-used)+' research credits left';
}

function showPricing(msg){
  if(msg) document.getElementById('pricing-msg').textContent = msg;
  document.getElementById('pricing-overlay').classList.add('open');
}

function closePricing(){
  document.getElementById('pricing-overlay').classList.remove('open');
}
function selectTier(plan){
  if(plan==='free'){
    var t=tierLoad();t.plan='free';tierSave(t);
    closePricing();updateCreditsBar();renderTopbar();
    return;
  }
  var urls={starter:'https://buy.stripe.com/8x28wPfrA9WughedmqbjW05',pro:'https://buy.stripe.com/00wdR90wGc4Cd52gyCbjW01',agency:'https://buy.stripe.com/8x2dR993c3y6aWU0zEbjW00'};
  if(urls[plan])window.open(urls[plan],'_blank');
  closePricing();
}
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
function showLimitToast(msg){
  var t=document.createElement('div');
  t.style.cssText='position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:var(--sur);border:1px solid var(--pip-bor);color:var(--tx);font-size:13px;font-weight:600;padding:14px 24px;border-radius:10px;z-index:99999;box-shadow:0 4px 32px rgba(0,0,0,0.5);font-family:Outfit,sans-serif;max-width:360px;text-align:center;line-height:1.5';
  t.innerHTML=msg;
  document.body.appendChild(t);
  setTimeout(function(){t.style.transition='opacity .3s';t.style.opacity='0';setTimeout(function(){t.remove();},300);},5000);
}
function showInfoToast(msg){
  var ex=document.getElementById('info-toast');if(ex)ex.remove();
  var t=document.createElement('div');t.id='info-toast';
  t.style.cssText='position:fixed;bottom:24px;right:24px;background:var(--sur);border:1px solid var(--bor2);border-radius:var(--r);padding:12px 18px;max-width:280px;z-index:500;font-size:12px;color:var(--tx2);font-family:Outfit,sans-serif;line-height:1.4';
  t.textContent=msg;document.body.appendChild(t);
  setTimeout(function(){t.style.transition='opacity .3s';t.style.opacity='0';setTimeout(function(){t.remove();},300);},3000);
}
function showUpsellToast(msg){
  var _t=tierLoad();
  if(_t._master||_t.plan==='agency'){showInfoToast(msg);return;}
  var ex=document.getElementById('upsell-toast');if(ex)ex.remove();
  var toast=document.createElement('div');toast.id='upsell-toast';
  toast.style.cssText='position:fixed;bottom:24px;right:24px;background:var(--sur);border:1px solid var(--bor2);border-radius:var(--r);padding:14px 18px;max-width:300px;z-index:500;font-size:12px;color:var(--tx2);display:flex;flex-direction:column;gap:8px';
  var span=document.createElement('span');span.textContent=msg;
  var btn=document.createElement('button');
  var ul=_t.plan==='pro'?'Upgrade to Agency':_t.plan==='starter'?'Upgrade to Pro':'Upgrade';
  btn.textContent=ul;
  btn.style.cssText='background:var(--pip);color:#fff;border:none;font-size:11px;font-weight:700;padding:6px 12px;border-radius:4px;cursor:pointer;font-family:Outfit,sans-serif;align-self:flex-start';
  btn.onclick=function(){showPricing();toast.remove();};
  toast.appendChild(span);toast.appendChild(btn);document.body.appendChild(toast);
  setTimeout(function(){if(toast.parentNode){toast.style.transition='opacity .3s';toast.style.opacity='0';setTimeout(function(){toast.remove();},300);}},8000);
}


function smartUpgradeMsg(){
  var t=tierLoad();var plan=t.plan||'free';
  if(plan==='agency'||t._master) return null;
  if(plan==='pro') return 'Upgrade to Agency for more capacity. <a onclick="showPricing()" style="color:var(--pip);font-weight:700;cursor:pointer">Upgrade →</a>';
  if(plan==='starter') return 'Upgrade to Pro for more power. <a onclick="showPricing()" style="color:var(--pip);font-weight:700;cursor:pointer">Upgrade →</a>';
  return 'Upgrade your plan. <a onclick="showPricing()" style="color:var(--pip);font-weight:700;cursor:pointer">Upgrade →</a>';
}
function maybeShowUpsell(){
  var t=tierLoad();if(t._master)return;
  var plan=t.plan||'free';
  if(plan==='agency')return;
  var used=t.research_used||0;
  if(used>0&&used%3===0){
    var upMsg=smartUpgradeMsg();if(!upMsg)return;
    showLimitToast('You have used '+used+' researches this month. '+upMsg);
  }
}










var PAGE_HISTORY = [];
var SOURCER_MODE = 'hunt';
var SOURCER_JD = '';
var SOURCER_CANDIDATES = [];

function phSetMode(mode){
  SOURCER_MODE=mode;
  var act='background:var(--pip);color:#fff;border:none;font-family:Outfit,sans-serif;font-size:12px;font-weight:700;padding:7px 16px;border-radius:5px;cursor:pointer';
  var inact='background:none;color:var(--tx3);border:none;font-family:Outfit,sans-serif;font-size:12px;font-weight:700;padding:7px 16px;border-radius:5px;cursor:pointer';
  var hb=document.getElementById('ph-mode-hunt'),sb=document.getElementById('ph-mode-source');
  if(hb)hb.style.cssText=mode==='hunt'?act:inact;
  if(sb)sb.style.cssText=mode==='source'?act:inact;
  var hd=document.getElementById('ph-hunt-mode'),sd=document.getElementById('ph-source-mode');
  if(hd)hd.style.display=mode==='hunt'?'block':'none';
  if(sd)sd.style.display=mode==='source'?'block':'none';
  var t=document.getElementById('ph-mode-title'),s=document.getElementById('ph-mode-sub');
  if(t)t.textContent=mode==='hunt'?'Find your next role':'Source candidates';
  if(s)s.textContent=mode==='hunt'?'Spot open positions at funded startups. Research before you apply.':'Paste a JD, get LinkedIn search strings, score candidates, write InMails.';
}

function sourcerRun(){
  var jd=(document.getElementById('sourcer-jd')||{value:''}).value.trim();
  if(!jd){alert('Please enter a job description or requirements.');return;}
  SOURCER_JD=jd;
  var jdEl=document.getElementById('sourcer-jd');if(jdEl)jdEl.value='';
  var status=document.getElementById('sourcer-status');
  if(status){status.textContent='Finding candidates...';status.style.color='var(--tx3)';}
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({key:'',company:jd,system:'',mode:'source'})})
  .then(function(r){return r.json();})
  .then(function(d){
    if(d.error){if(status)status.textContent='Error: '+d.error;return;}
    var t=(d.text||'').replace(/```json/g,'').replace(/```/g,'').trim();
    var a=t.indexOf('['),b=t.lastIndexOf(']');
    var candidates=[];
    if(a>=0&&b>a){try{candidates=JSON.parse(t.slice(a,b+1));}catch(e){}}
    if(!candidates.length){if(status)status.textContent='No candidates found - try again';return;}
    if(status){status.textContent=candidates.length+' candidates found';setTimeout(function(){status.textContent='';},3000);}
    PH_HISTORY.unshift({type:'source',query:jd,candidates:candidates,ts:Date.now()});
    if(PH_HISTORY.length>20)PH_HISTORY.pop();
    try{localStorage.setItem('ph_history',JSON.stringify(PH_HISTORY));}catch(e){}
    phSave();
    // Make sure source mode and candidate section are visible
    var srcSection=document.getElementById('sourcer-search-section');
    if(srcSection)srcSection.style.display='block';
    renderCandidateCards(candidates);
    // Scroll to candidates
    setTimeout(function(){
      var wrap=document.getElementById('sourcer-candidates-section');
      if(wrap)wrap.scrollIntoView({behavior:'smooth',block:'nearest'});
    },100);
  }).catch(function(e){if(status)status.textContent='Error: '+e.message;});
}


function sourcerScore(){
  var paste=(document.getElementById('sourcer-paste')||{value:''}).value.trim();
  if(!paste){alert('Paste candidate names and roles first.');return;}
  if(!SOURCER_JD){alert('Run a search first so I have the JD context.');return;}
  var status=document.getElementById('sourcer-status');
  if(status)status.textContent='Scoring candidates...';
  var sys='You are a recruiting AI. Score each candidate 0-100 for fit and write a personalised 3-sentence LinkedIn InMail. Return ONLY a JSON array. Each object: name, role, company, score (number), fit_reason (1 sentence), inmail (3 sentences, personalised). No markdown.';
  fetch('/api',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({key:'',company:'JD:'+String.fromCharCode(10)+SOURCER_JD+String.fromCharCode(10)+String.fromCharCode(10)+'Candidates:'+String.fromCharCode(10)+paste,system:sys,mode:'fetch'})})
  .then(function(r){return r.json();})
  .then(function(d){
    var t=(d.text||'').replace(/```json/g,'').replace(/```/g,'').trim();
    var a=t.indexOf('['),b=t.lastIndexOf(']');
    if(a>=0&&b>a){try{SOURCER_CANDIDATES=JSON.parse(t.slice(a,b+1));}catch(e){}}
    sourcerRenderCandidates();
    if(status){status.textContent=SOURCER_CANDIDATES.length+' candidates scored';setTimeout(function(){status.textContent='';},3000);}
  }).catch(function(e){if(status)status.textContent='Error: '+e.message;});
}

function sourcerRenderCandidates(){
  var cont=document.getElementById('sourcer-results');
  if(!cont||!SOURCER_CANDIDATES.length)return;
  var sorted=SOURCER_CANDIDATES.slice().sort(function(a,b){return(b.score||0)-(a.score||0);});
  cont.innerHTML=sorted.map(function(c){
    var n=c.score||0;
    var col=n>=75?'var(--pip2)':n>=50?'var(--amb)':'var(--tx3)';
    var enc=encodeURIComponent(c.inmail||'');
    return '<div class="candidate-card">'+
      '<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px">'+
        '<div style="flex:1">'+
          '<div style="font-size:14px;font-weight:700;color:var(--tx);margin-bottom:2px">'+(c.name||'')+'</div>'+
          '<div style="font-size:12px;color:var(--tx3);margin-bottom:6px">'+(c.role||'')+(c.company?' at '+c.company:'')+'</div>'+
          '<div style="font-size:12px;color:var(--tx2)">'+(c.fit_reason||'')+'</div>'+
        '</div>'+
        '<div style="text-align:right;flex-shrink:0">'+
          '<div style="font-size:28px;font-weight:800;font-family:JetBrains Mono,monospace;letter-spacing:-.04em;line-height:1;color:'+col+'">'+n+'</div>'+
          '<div style="font-size:10px;color:var(--tx3)">fit</div>'+
        '</div>'+
      '</div>'+
      '<div class="candidate-inmail">'+(c.inmail||'')+'</div>'+
      '<button data-action="copy-inmail" data-inmail="'+enc+'" style="margin-top:8px;background:none;border:1px solid var(--bor2);color:var(--tx2);font-size:11px;font-weight:700;padding:5px 14px;border-radius:4px;cursor:pointer;font-family:Outfit,sans-serif">Copy InMail</button>'+
    '</div>';
  }).join('');
}


var SUPA_URL = 'https://lisamrtqlpjpkftncfzg.supabase.co';
var SUPA_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imxpc2FtcnRxbHBqcGtmdG5jZnpnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU2NzQ1MzYsImV4cCI6MjA5MTI1MDUzNn0.QM4Yl9oTt2nfUqmdpboPk9Xbr_qCYPHIUYSgz6E_2HE';
var SUPA_USER = null;

function supaPost(path, body) {
  var token = localStorage.getItem('sb_token');
  var h = {'apikey':SUPA_KEY,'Content-Type':'application/json','Accept':'application/json'};
  if(token) h['Authorization'] = 'Bearer '+token;
  var controller = typeof AbortController!=='undefined' ? new AbortController() : null;
  var timer = controller ? setTimeout(function(){controller.abort();}, 15000) : null;
  var opts = {method:'POST', headers:h, body:JSON.stringify(body), mode:'cors', credentials:'omit'};
  if(controller) opts.signal = controller.signal;
  return fetch(SUPA_URL+path, opts).then(function(r){
    if(timer) clearTimeout(timer);
    return r.json();
  }).catch(function(err){
    if(timer) clearTimeout(timer);
    var msg = (err && err.name==='AbortError') ? 'Request timed out' : 'Network error';
    throw {error:{message: msg}};
  });
}
function authGetUser(){var u=localStorage.getItem('sb_user');if(u){try{return JSON.parse(u);}catch(e){}}return null;}
function authSignOut(){
  var h={'apikey':SUPA_KEY};var t=localStorage.getItem('sb_token');if(t)h['Authorization']='Bearer '+t;
  fetch(SUPA_URL+'/auth/v1/logout',{method:'POST',headers:h});
  localStorage.removeItem('sb_token');localStorage.removeItem('sb_user');SUPA_USER=null;
  showAuthScreen('login');
}
function showAuthScreen(mode){
  mode=mode||'signup';var old=document.getElementById('auth-screen');if(old)old.remove();
  var sc=document.createElement('div');sc.id='auth-screen';
  sc.style.cssText='position:fixed;top:0;left:0;width:100%;height:100%;background:#020408;z-index:99999;display:flex;align-items:center;justify-content:center;padding:24px;box-sizing:border-box;overflow-y:auto';
  var isS=mode==='signup';
  sc.innerHTML='<div style="width:100%;max-width:400px">'+
    '<div style="display:flex;align-items:center;gap:10px;justify-content:center;margin-bottom:40px">'+
      '<div style="width:8px;height:8px;border-radius:50%;background:#2d9de8;box-shadow:0 0 16px #2d9de8"></div>'+
      '<span style="font-size:13px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:#eef4ff;font-family:Outfit,sans-serif">Scout</span>'+
    '</div>'+
    '<div style="display:flex;background:rgba(255,255,255,0.05);border-radius:8px;padding:3px;margin-bottom:28px">'+
      '<button data-auth="login" style="flex:1;padding:9px;border:none;border-radius:6px;font-family:Outfit,sans-serif;font-size:13px;font-weight:700;cursor:pointer;background:'+(isS?'none':'#2d9de8')+';color:'+(isS?'#4a7a9a':'#fff')+'">Sign in</button>'+
      '<button data-auth="signup" style="flex:1;padding:9px;border:none;border-radius:6px;font-family:Outfit,sans-serif;font-size:13px;font-weight:700;cursor:pointer;background:'+(isS?'#2d9de8':'none')+';color:'+(isS?'#fff':'#4a7a9a')+'">Create account</button>'+
    '</div>'+
    (isS?'<input id="auth-name" placeholder="Your name" autocomplete="name" style="width:100%;background:#0a1220;border:1px solid rgba(45,157,232,0.2);color:#eef4ff;font-family:Outfit,sans-serif;font-size:14px;padding:13px 16px;border-radius:8px;outline:none;display:block;margin-bottom:10px;box-sizing:border-box">':'')+
    '<input id="auth-email" type="email" placeholder="Email address" autocomplete="email" style="width:100%;background:#0a1220;border:1px solid rgba(45,157,232,0.2);color:#eef4ff;font-family:Outfit,sans-serif;font-size:14px;padding:13px 16px;border-radius:8px;outline:none;display:block;margin-bottom:10px;box-sizing:border-box">'+
    '<input id="auth-pass" type="password" placeholder="Password (min 6 chars)" autocomplete="'+(isS?'new-password':'current-password')+'" style="width:100%;background:#0a1220;border:1px solid rgba(45,157,232,0.2);color:#eef4ff;font-family:Outfit,sans-serif;font-size:14px;padding:13px 16px;border-radius:8px;outline:none;display:block;margin-bottom:6px;box-sizing:border-box">'+
    '<div id="auth-error" style="font-size:12px;color:#f87171;min-height:18px;margin-bottom:10px;padding-left:2px"></div>'+
    '<button id="auth-btn"  style="width:100%;background:#2d9de8;color:#fff;border:none;font-family:Outfit,sans-serif;font-size:15px;font-weight:700;padding:14px;border-radius:8px;cursor:pointer;box-shadow:0 0 24px rgba(45,157,232,0.3)">'+
      (isS?'Create my account &rarr;':'Sign in &rarr;')+
    '</button>'+
    '<div style="margin-top:20px;text-align:center;font-size:12px;color:#2a4a6a">'+
      (isS?'Already have an account? <button data-auth="login" style="background:none;border:none;color:#2d9de8;cursor:pointer;font-family:Outfit,sans-serif;font-size:12px">Sign in</button>':
           'No account? <button data-auth="signup" style="background:none;border:none;color:#2d9de8;cursor:pointer;font-family:Outfit,sans-serif;font-size:12px">Create one free</button>')+
    '</div></div>';
  document.body.appendChild(sc);
  sc.addEventListener('click',function(e){
    var authMode=e.target.getAttribute('data-auth');
    if(authMode) showAuthScreen(authMode);
  });
  setTimeout(function(){
    var first=document.getElementById(isS?'auth-name':'auth-email');if(first)first.focus();
    ['auth-name','auth-email','auth-pass'].forEach(function(id){
      var el=document.getElementById(id);if(el)el.addEventListener('keydown',function(e){if(e.key==='Enter')authSubmit(mode);});
    });
    var authBtn=document.getElementById('auth-btn');
    if(authBtn) authBtn.onclick=function(){authSubmit(mode);};
  },50);
}
function authSubmit(mode){
  var email=(document.getElementById('auth-email')||{value:''}).value.trim();
  var pass=(document.getElementById('auth-pass')||{value:''}).value;
  var errEl=document.getElementById('auth-error'),btn=document.getElementById('auth-btn');
  if(!email||!pass){if(errEl)errEl.textContent='Please fill in all fields';return;}
  if(btn){btn.disabled=true;btn.textContent=mode==='signup'?'Creating...':'Signing in...';}
  if(errEl)errEl.textContent='';
  if(mode==='signup'){
    var name=(document.getElementById('auth-name')||{value:''}).value.trim()||email.split('@')[0];
    supaPost('/auth/v1/signup',{email:email,password:pass,data:{name:name}}).then(function(d){
      if(d.error){if(errEl)errEl.textContent=d.error.message;if(btn){btn.disabled=false;btn.textContent='Create my account';}return;}
      if(d.access_token){
        localStorage.setItem('sb_token',d.access_token);localStorage.setItem('sb_user',JSON.stringify(d.user));
        SUPA_USER=d.user;PROFILE.name=name;PROFILE.email=email;
        try{localStorage.setItem('scout_profile',JSON.stringify(PROFILE));}catch(e){}
        authSuccess();
      } else {
        var sc=document.getElementById('auth-screen');
        if(sc)sc.innerHTML='<div style="text-align:center;color:#eef4ff;font-family:Outfit,sans-serif;padding:40px 24px;max-width:400px"><div style="font-size:48px;margin-bottom:16px">&#9993;</div><div style="font-size:20px;font-weight:700;margin-bottom:10px">Check your email</div><div style="font-size:14px;color:#7da8c8;line-height:1.6">Confirmation sent to <b>'+email+'</b>. Click it then sign in.</div><button data-auth="login" style="margin-top:24px;background:#2d9de8;color:#fff;border:none;font-family:Outfit,sans-serif;font-size:14px;font-weight:700;padding:12px 32px;border-radius:8px;cursor:pointer">Sign in</button></div>';
      }
    }).catch(function(err){
      var msg=(err&&err.error&&err.error.message)||'Connection error — check your network';
      var e2=document.getElementById('auth-error');if(e2)e2.textContent=msg;else alert(msg);
      if(btn){btn.disabled=false;btn.textContent='Create my account';}
    });
  } else {
    supaPost('/auth/v1/token?grant_type=password',{email:email,password:pass}).then(function(d){
      if(d.error){
        var e2=document.getElementById('auth-error');
        var msg=d.error.message||'Invalid credentials';
        if(e2)e2.textContent=msg;else alert(msg);
        if(btn){btn.disabled=false;btn.textContent='Sign in';}return;
      }
      localStorage.setItem('sb_token',d.access_token);localStorage.setItem('sb_user',JSON.stringify(d.user));
      SUPA_USER=d.user;
      PROFILE.email=d.user.email||email;if(d.user&&d.user.user_metadata&&d.user.user_metadata.name){PROFILE.name=d.user.user_metadata.name;}try{localStorage.setItem('scout_profile',JSON.stringify(PROFILE));}catch(e){}
      authSuccess();
    }).catch(function(err){
      var msg=(err&&err.error&&err.error.message)||'Connection error — check your network';
      var e2=document.getElementById('auth-error');if(e2)e2.textContent=msg;else alert(msg);
      if(btn){btn.disabled=false;btn.textContent='Sign in';}
    });
  }
}
function authSuccess(){
  var sc=document.getElementById('auth-screen');
  if(sc)sc.remove();
  initApp();
}
function renderTopbar(){
  var right=document.getElementById('topbar-right');
  if(!right)return;
  profileLoad();
  var _tier=tierLoad();
  var plan=_tier.plan||'free';
  var initials=PROFILE.name?PROFILE.name.split(' ').map(function(w){return w[0]||'';}).slice(0,2).join('').toUpperCase():'ME';
  right.innerHTML=
    '<div id="credits-bar" style="display:none;align-items:center;gap:8px">'+
      '<div style="width:70px;height:4px;background:var(--sur3);border-radius:2px;overflow:hidden">'+
        '<div id="credits-fill" style="height:100%;background:var(--pip);width:0%;border-radius:2px;transition:width .3s"></div>'+
      '</div>'+
      '<span id="credits-count" style="font-size:10px;color:var(--tx3)"></span>'+
    '</div>'+
    (!_tier._master&&plan==='free'?'<button onclick="showPricing()" id="upgrade-btn" style="background:none;border:1px solid var(--pip-bor);color:var(--pip);font-size:11px;font-weight:700;padding:5px 14px;border-radius:999px;cursor:pointer;font-family:Outfit,sans-serif">Upgrade</button>':'')+
    '<div style="position:relative" id="profile-menu-wrap">'+
      '<button id="profile-avatar-btn" style="width:32px;height:32px;border-radius:50%;background:var(--pip);color:#fff;border:none;font-size:11px;font-weight:700;cursor:pointer;font-family:Outfit,sans-serif;display:flex;align-items:center;justify-content:center" title="Account">'+initials+'</button>'+
      '<div id="profile-dropdown" style="display:none;position:absolute;top:42px;right:0;background:var(--sur);border:1px solid var(--bor2);border-radius:var(--r);min-width:180px;z-index:9999;box-shadow:0 8px 32px rgba(0,0,0,0.5);overflow:hidden">'+
        '<div style="padding:12px 16px;border-bottom:1px solid var(--bor)">'+
          '<div style="font-size:13px;font-weight:700;color:var(--tx)">'+(PROFILE.name||'My account')+'</div>'+
          '<div style="font-size:11px;color:var(--tx3);margin-top:2px">'+(PROFILE.email||'')+'</div>'+
        '</div>'+
        '<button data-nav="dashboard" style="width:100%;text-align:left;padding:10px 16px;background:none;border:none;color:var(--tx2);font-size:13px;cursor:pointer;font-family:Outfit,sans-serif;display:block">&#9783; Dashboard</button>'+
        '<button data-nav="profile" style="width:100%;text-align:left;padding:10px 16px;background:none;border:none;color:var(--tx2);font-size:13px;cursor:pointer;font-family:Outfit,sans-serif;border-top:1px solid var(--bor);display:block">&#9881; Profile</button>'+
        '<button id="signout-btn" style="width:100%;text-align:left;padding:10px 16px;background:none;border:none;color:var(--tx3);font-size:12px;cursor:pointer;font-family:Outfit,sans-serif;border-top:1px solid var(--bor);display:block">Sign out</button>'+
      '</div>'+
    '</div>'+
    '<button class="hamburger" id="hamburger-btn" title="Menu" style="margin-left:8px">'+
      '<span></span><span></span><span></span>'+
    '</button>';

  updateCreditsBar();

  setTimeout(function(){
    // Avatar button toggles dropdown
    var avatarBtn=document.getElementById('profile-avatar-btn');
    if(avatarBtn) avatarBtn.onclick=function(e){
      e.stopPropagation();
      var dd=document.getElementById('profile-dropdown');
      if(dd) dd.style.display=dd.style.display==='none'?'block':'none';
    };
    // Hamburger opens sidebar
    var hb=document.getElementById('hamburger-btn');
    if(hb) hb.onclick=function(e){ e.stopPropagation(); openSidebar(); };
    // Dropdown nav items
    var wrap=document.getElementById('profile-menu-wrap');
    if(wrap) wrap.addEventListener('click',function(e){
      var btn=e.target.closest('[data-nav]');
      if(btn){ closeProfileMenu(); navTo(btn.getAttribute('data-nav')); return; }
      var so=e.target.closest('#signout-btn');
      if(so){ closeProfileMenu(); authSignOut(); }
    });
    // Close dropdown on outside click
    document.addEventListener('click',function(){
      var dd=document.getElementById('profile-dropdown');
      if(dd) dd.style.display='none';
    });
  },50);
}

function closeProfileMenu(){
  var dd=document.getElementById('profile-dropdown');
  if(dd) dd.style.display='none';
}
function showSplash(){
  var sp=document.getElementById('ob-splash');
  if(!sp)return;
  sp.style.display='flex';
  setTimeout(function(){sp.style.opacity='1';},30);
  scoutStep(1);
}
function scoutStep(n){
  [1,2,3].forEach(function(i){
    var el=document.getElementById('ob-step'+i);
    if(el)el.style.display=(i===n?'block':'none');
  });
}
function obChoosePlan(plan){
  ['free','pro','agency'].forEach(function(p){
    var el=document.getElementById('opc-'+p);
    if(el)el.classList.toggle('selected',p===plan);
  });
  var btn=document.getElementById('ob-enter-btn');
  if(btn)btn.setAttribute('data-ob-plan',plan);
}
function obSkip(){
  try{localStorage.setItem('scout_ob_done','1');}catch(e){}
  var sp=document.getElementById('ob-splash');
  if(sp){sp.style.opacity='0';setTimeout(function(){sp.style.display='none';},500);}
}
function obFinish(){
  var nm=(document.getElementById('ob-name')||{}).value||'';
  var tg=(document.getElementById('ob-tagline')||{}).value||'';
  var li=(document.getElementById('ob-linkedin')||{}).value||'';
  if(nm.trim()){PROFILE.name=nm.trim();}
  if(tg.trim()){PROFILE.tagline=tg.trim();}
  if(li.trim()){PROFILE.linkedin=li.trim();}
  if(nm.trim()||tg.trim()||li.trim()){
    try{localStorage.setItem('scout_profile',JSON.stringify(PROFILE));}catch(e){}
  }
  var btn=document.getElementById('ob-enter-btn');
  var plan=btn?btn.getAttribute('data-ob-plan'):'free';
  if(plan&&plan!=='free'){
    var t=tierLoad();
    t.plan=plan;
    try{localStorage.setItem('scout_tier',JSON.stringify(t));}catch(e){}
  }
  try{localStorage.setItem('scout_ob_done','1');}catch(e){}
  obSkip();
  renderProfile();
  updateCreditsBar();
}
function initApp(){
  profileLoad();phLoad();updateCreditsBar();renderTopbar();initIdleTimer();
  document.body.classList.add('app-ready');
  load(function(){
    setPage('dashboard');
    updateCreditsBar();
    if(!PROFILE.name&&!localStorage.getItem('scout_ob_done')){
      setTimeout(showSplash,800);
    }
  });
  document.addEventListener('click',function(e){
    var t=e.target.closest('[data-action]')||e.target;
    var a=t?t.getAttribute('data-action'):null;if(!a)return;
    if(a==='open-lead'){var id=t.getAttribute('data-id');if(id)openLeadDetail(id);return;}
    if(a==='approve-inbox'){var id=t.getAttribute('data-id');if(id)approveInboxCard(id);return;}
    if(a==='set-status'){var id=t.getAttribute('data-id');var st=t.getAttribute('data-status');if(id&&st)updateLeadStatus(id,st);return;}
    if(a==='copy-pitch'){var el=document.getElementById('ld-pitch-text');if(el){navigator.clipboard.writeText(el.textContent);t.textContent='Copied!';setTimeout(function(){t.textContent='Copy pitch';},1800);}return;}
    if(a==='edit-profile'){openProfileModal();return;}
    if(a==='open-profile'){navTo('profile');return;}
    if(a==='data-nav' || e.target.hasAttribute && e.target.hasAttribute('data-nav')){
      var nav=t.getAttribute('data-nav')||e.target.getAttribute('data-nav');
      if(nav) navTo(nav); return;
    }
    if(a==='copy-search'){var c=t.closest('[data-search]');if(c){navigator.clipboard.writeText(decodeURIComponent(c.getAttribute('data-search')));t.textContent='Copied!';setTimeout(function(){t.textContent='Copy';},1500);}return;}
    if(a==='copy-inmail'){var enc=t.getAttribute('data-inmail');if(enc){navigator.clipboard.writeText(decodeURIComponent(enc));t.textContent='Copied!';setTimeout(function(){t.textContent='Copy InMail';},1500);}return;}
    var nav=e.target.getAttribute('data-nav');if(nav){var dd=document.getElementById('profile-dropdown');if(dd)dd.style.display='none';navTo(nav);return;}
    if(!e.target.closest('#profile-menu-wrap')){var dd2=document.getElementById('profile-dropdown');if(dd2)dd2.style.display='none';}
  });
  var rb=document.getElementById('rb');if(rb)rb.onclick=go;
  var ci=document.getElementById('ci');if(ci)ci.addEventListener('keydown',function(e){if(e.key==='Enter')go();});
  var brb=document.getElementById('brb');if(brb)brb.onclick=bulk;
  var fb=document.getElementById('fetch-btn');if(fb)fb.onclick=fetchLeads;
  var rsb=document.getElementById('res-sel-btn');if(rsb)rsb.onclick=researchSelected;
  var btog=document.getElementById('btog');if(btog)btog.onclick=function(){showPanel('bpanel');};
}

function phRenderHistory(){
  var cont = document.getElementById('ph-history-list');
  if(!cont || !PH_HISTORY.length) return;
  cont.innerHTML = '';
  PH_HISTORY.forEach(function(item, idx){
    var card = document.createElement('div');
    card.style.cssText = 'background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r);margin-bottom:8px;overflow:hidden';
    var header = document.createElement('div');
    header.style.cssText = 'display:flex;align-items:center;justify-content:space-between;padding:12px 14px;cursor:pointer';
    var left = document.createElement('div');
    var title = document.createElement('div');
    title.style.cssText = 'font-size:13px;font-weight:700;color:var(--tx);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:280px';
    title.textContent = item.query.slice(0,80) + (item.query.length>80?'...':'');
    var meta = document.createElement('div');
    meta.style.cssText = 'font-size:11px;color:var(--tx3);margin-top:2px';
    meta.textContent = (item.type==='source'?'Candidate sourcing':'Job search') + ' · ' + (item.searches?item.searches.length:0) + ' searches' + (item.candidates&&item.candidates.length?' · '+item.candidates.length+' scored':'');
    left.appendChild(title);left.appendChild(meta);
    var toggle = document.createElement('span');
    toggle.style.cssText = 'font-size:18px;color:var(--tx3);transition:transform .2s;flex-shrink:0';
    toggle.textContent = '›';
    header.appendChild(left);header.appendChild(toggle);
    var body = document.createElement('div');
    body.style.cssText = 'display:none;padding:0 14px 12px;border-top:1px solid var(--bor)';
    if(item.candidates && item.candidates.length){
      var ct=document.createElement('div');ct.style.cssText='font-size:11px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.1em;margin-top:12px;margin-bottom:8px';
      ct.textContent=item.candidates.length+' Candidates';body.appendChild(ct);
      item.candidates.forEach(function(c){
        var sc3=c.fit_score||0;var scol3=sc3>=75?'var(--pip2)':sc3>=50?'var(--amb)':'var(--tx3)';
        var cr=document.createElement('div');cr.style.cssText='background:var(--sur);border:1px solid var(--bor);border-radius:6px;padding:10px 12px;margin-bottom:6px;display:flex;align-items:center;justify-content:space-between;gap:8px';
        var cl=document.createElement('div');cl.style.minWidth='0';
        var cn2=document.createElement('div');cn2.style.cssText='font-size:12px;font-weight:700;color:var(--tx);white-space:nowrap;overflow:hidden;text-overflow:ellipsis';cn2.textContent=c.name||'';
        var cr2=document.createElement('div');cr2.style.cssText='font-size:11px;color:var(--tx3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis';cr2.textContent=(c.current_title||'')+(c.current_company?' at '+c.current_company:'');
        cl.appendChild(cn2);cl.appendChild(cr2);
        var cright=document.createElement('div');cright.style.cssText='display:flex;align-items:center;gap:8px;flex-shrink:0';
        var cscore=document.createElement('div');cscore.style.cssText='font-size:18px;font-weight:800;font-family:JetBrains Mono,monospace;color:'+scol3;cscore.textContent=sc3;
        cright.appendChild(cscore);
        var la2=document.createElement('a');var liUrl2=c.linkedin_url||('https://www.linkedin.com/search/results/people/?keywords='+encodeURIComponent((c.name||'')+' '+(c.current_title||'')));
        la2.href=liUrl2;la2.target='_blank';la2.style.cssText='font-size:10px;color:#0a66c2;font-weight:700;text-decoration:none';la2.textContent=c.linkedin_url?'LinkedIn':'Find';
        cright.appendChild(la2);cr.appendChild(cl);cr.appendChild(cright);body.appendChild(cr);
      });
    }
    if(item.candidates && item.candidates.length){
      var candTitle = document.createElement('div');
      candTitle.style.cssText = 'font-size:11px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.1em;margin-top:12px;margin-bottom:8px';
      candTitle.textContent = 'Scored Candidates';
      body.appendChild(candTitle);
      item.candidates.forEach(function(c){
        var crow = document.createElement('div');
        crow.style.cssText = 'background:var(--sur);border:1px solid var(--bor);border-radius:6px;padding:10px 12px;margin-bottom:6px;display:flex;align-items:center;gap:10px';
        var cn = document.createElement('div');cn.style.flex='1';
        var cname = document.createElement('div');cname.style.cssText='font-size:12px;font-weight:700;color:var(--tx)';cname.textContent=c.name||'';
        var crole = document.createElement('div');crole.style.cssText='font-size:11px;color:var(--tx3)';crole.textContent=(c.role||'')+(c.company?' at '+c.company:'');
        cn.appendChild(cname);cn.appendChild(crole);
        var cscore = document.createElement('div');cscore.style.cssText='font-size:20px;font-weight:800;font-family:JetBrains Mono,monospace;color:'+(c.score>=75?'var(--pip2)':c.score>=50?'var(--amb)':'var(--tx3)');cscore.textContent=c.score||0;
        crow.appendChild(cn);crow.appendChild(cscore);
        body.appendChild(crow);
      });
    }
    var expanded = false;
    header.onclick = function(){
      expanded = !expanded;
      body.style.display = expanded ? 'block' : 'none';
      toggle.style.transform = expanded ? 'rotate(90deg)' : '';
    };
    card.appendChild(header);card.appendChild(body);
    cont.appendChild(card);
  });
  var wrap = document.getElementById('ph-history-wrap');
  if(wrap) wrap.style.display = PH_HISTORY.length ? 'block' : 'none';
}

function goBack(){
  if(PAGE_HISTORY.length>0){ var prev=PAGE_HISTORY.pop(); setPage(prev,false); }
  else{ setPage('dashboard',false); }
}

function renderSidebarTier(){
  var wrap=document.getElementById('sb-tier-features');
  var items=document.getElementById('sb-tier-items');
  var label=document.getElementById('sb-tier-label');
  if(!wrap||!items)return;
  var t=tierLoad();
  var plan=t.plan||'free';
  var features={
    free:[],
    starter:[],
    pro:[
      {label:'CSV Export',action:function(){var b=document.getElementById('csvbtn');if(b)b.click();}},
      {label:'Priority Support',action:function(){window.open('mailto:support@scout-ai.io','_blank');}}
    ],
    agency:[
      {label:'Proposal Generator',action:function(){openProposalModal(window._currentLead);}},
      {label:'Dedicated Support',action:function(){window.open('mailto:support@scout-ai.io','_blank');}}
    ]
  };
  var list=features[plan]||[];
  if(!list.length){wrap.style.display='none';return;}
  wrap.style.display='block';
  if(label) label.textContent=(plan==='pro'?'Pro Plan':'Agency Plan');
  items.innerHTML='';
  list.forEach(function(f){
    var btn=document.createElement('button');
    btn.style.cssText='display:flex;align-items:center;gap:8px;width:100%;padding:9px 0;background:none;border:none;border-bottom:1px solid var(--bor);color:var(--tx2);font-size:12px;cursor:pointer;font-family:Outfit,sans-serif;text-align:left';
    btn.innerHTML='<span style="color:var(--pip2);font-size:10px">&#10003;</span>'+f.label;
    btn.onclick=function(){closeSidebar();f.action();};
    items.appendChild(btn);
  });
}


function exportToHubspot(r){
  if(!r){showUpsellToast('No lead selected');return;}
  var rows = [
    ['First Name','Last Name','Email','Company','Phone','Website','Industry','Description'],
    [r.best_contact_name||'','',' ',r.company||'','',r.website||'',r.sector||'',
     (r.why_fit||'')+(r.pitch_opener?' | '+r.pitch_opener:'')]
  ];
  var csv = rows.map(function(row){
    return row.map(function(v){
      var s = String(v==null?'':v).replace(/"/g,'""');
      return s.indexOf(',')>=0||s.indexOf('"')>=0?'"'+s+'"':s;
    }).join(',');
  }).join(String.fromCharCode(10));
  var blob = new Blob([csv],{type:'text/csv'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = (r.company||'lead').replace(/[^a-z0-9]/gi,'-')+'-hubspot.csv';
  a.click();
  showInfoToast('HubSpot CSV downloaded ✓');
}

function exportToNotion(r){
  if(!r){showUpsellToast('No lead selected');return;}
  var text = [
    '# '+( r.company||'Lead'),
    '',
    '**Sector:** '+(r.sector||'-'),
    '**Stage:** '+(r.stage||'-'),
    '**HQ:** '+(r.hq||'-'),
    '**Funding:** '+(r.funding_amount||'-'),
    '**GTM Score:** '+(r.gtm_readiness_score||'-')+' ('+( r.gtm_label||'-')+')',
    '',
    '## Why They Need You',
    r.why_fit||'-',
    '',
    '## Pitch Opener',
    r.pitch_opener||'-',
    '',
    '## Contact',
    (r.best_contact_name?r.best_contact_name+' - ':'')+( r.best_contact_title||r.decision_maker||'-'),
    '',
    '## Status',
    r.outreach_status||'not_contacted'
  ].join(String.fromCharCode(10));
  navigator.clipboard.writeText(text).then(function(){
    showUpsellToast('Copied for Notion ✓ Paste with Ctrl/Cmd+V');
  }).catch(function(){
    showUpsellToast('Could not copy - try again');
  });
}


function closeProposalModal(){var m=document.getElementById('proposal-modal');if(m)m.remove();}

function openProposalModal(r){
  closeProposalModal();
  profileLoad();
  var overlay=document.createElement('div');
  overlay.id='proposal-modal';
  overlay.style.cssText='position:fixed;inset:0;background:rgba(0,0,0,0.8);z-index:1000;display:flex;align-items:flex-start;justify-content:center;overflow-y:auto;padding:24px;backdrop-filter:blur(4px)';
  var co=PROFILE.wl_color||PROFILE.color||'#2d9de8';
  overlay.innerHTML=
    '<div style="background:var(--sur);border:1px solid var(--bor2);border-radius:var(--r);padding:28px;width:100%;max-width:560px;margin:auto;display:flex;flex-direction:column;gap:0">'+
      '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px">'+
        '<div style="font-size:16px;font-weight:700;color:var(--tx)">Custom Proposal Generator</div>'+
        '<button onclick="closeProposalModal()" style="background:none;border:none;color:var(--tx3);font-size:20px;cursor:pointer;line-height:1;padding:0 4px">&#215;</button>'+
      '</div>'+
      // SECTION: Your brand
      '<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--tx3);margin-bottom:10px">Your brand</div>'+
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">'+
        '<input id="pm-name" class="modal-input" placeholder="Your name" value="'+(PROFILE.name||'')+'" style="font-size:13px;padding:10px 13px">'+
        '<input id="pm-agency" class="modal-input" placeholder="Agency name (optional)" value="'+(PROFILE.agency||'')+'" style="font-size:13px;padding:10px 13px">'+
      '</div>'+
      '<input id="pm-role" class="modal-input" placeholder="Your role (e.g. Fractional CMO)" value="'+(PROFILE.role||'Fractional CMO')+'" style="font-size:13px;padding:10px 13px;margin-bottom:10px;display:block;width:100%">'+
      '<input id="pm-tagline" class="modal-input" placeholder="Tagline (1 line)" value="'+(PROFILE.tagline||'')+'" style="font-size:13px;padding:10px 13px;margin-bottom:10px;display:block;width:100%">'+
      '<textarea id="pm-bio" class="modal-input" placeholder="Short bio (2–3 sentences)" rows="2" style="font-size:13px;padding:10px 13px;margin-bottom:10px;resize:vertical;width:100%;line-height:1.5">'+(PROFILE.bio||'')+'</textarea>'+
      '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:16px">'+
        '<input id="pm-email" class="modal-input" placeholder="Email" value="'+(PROFILE.email||'')+'" style="font-size:12px;padding:9px 12px">'+
        '<input id="pm-phone" class="modal-input" placeholder="Phone" value="'+(PROFILE.phone||'')+'" style="font-size:12px;padding:9px 12px">'+
        '<input id="pm-calendly" class="modal-input" placeholder="Calendly / booking URL" value="'+(PROFILE.calendly||'')+'" style="font-size:12px;padding:9px 12px">'+
      '</div>'+
      // SECTION: Branding
      '<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--tx3);margin-bottom:10px">Branding</div>'+
      '<div style="display:grid;grid-template-columns:1fr auto;gap:10px;align-items:center;margin-bottom:10px">'+
        '<input id="pm-logo" class="modal-input" placeholder="Your logo URL" value="'+(PROFILE.wl_logo||'')+'" style="font-size:13px;padding:10px 13px">'+
        '<div style="display:flex;align-items:center;gap:8px">'+
          '<input type="color" id="pm-color" value="'+co+'" style="width:36px;height:36px;border:1px solid var(--bor);border-radius:6px;background:var(--sur2);cursor:pointer;padding:2px;flex-shrink:0">'+
          '<span id="pm-color-hex" style="font-size:12px;color:var(--tx3);white-space:nowrap">'+co+'</span>'+
        '</div>'+
      '</div>'+
      // SECTION: Prospect
      '<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--tx3);margin-bottom:10px;margin-top:6px">Prospect</div>'+
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px">'+
        '<input id="pm-prospect-co" class="modal-input" placeholder="Company name" value="'+(r?r.company||'':'')+'" style="font-size:13px;padding:10px 13px">'+
        '<input id="pm-prospect-logo" class="modal-input" placeholder="Prospect logo URL (optional)" value="'+(r?r.prospect_logo||'':'')+'" style="font-size:13px;padding:10px 13px">'+
      '</div>'+
      // SECTION: Proposal content
      '<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--tx3);margin-bottom:10px">Proposal content</div>'+
      '<textarea id="pm-why" class="modal-input" placeholder="Why this company needs you now (pulled from lead data — edit freely)" rows="3" style="font-size:13px;padding:10px 13px;margin-bottom:10px;resize:vertical;width:100%;line-height:1.5">'+(r?r.why_fit||r.pitch_opener||'':'')+'</textarea>'+
      '<textarea id="pm-approach" class="modal-input" placeholder="Your approach / what you would do first" rows="2" style="font-size:13px;padding:10px 13px;margin-bottom:16px;resize:vertical;width:100%;line-height:1.5">'+(r?r.pitch_opener||'':'')+'</textarea>'+
      // SECTION: Terms
      '<div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--tx3);margin-bottom:10px">Engagement terms</div>'+
      '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:20px">'+
        '<input id="pm-deal" class="modal-input" placeholder="Investment (e.g. $5k/mo)" value="'+(PROFILE.deal_size||'')+'" style="font-size:12px;padding:9px 12px">'+
        '<input id="pm-engagement" class="modal-input" placeholder="Engagement type" value="'+(PROFILE.client_size||'')+'" style="font-size:12px;padding:9px 12px">'+
        '<input id="pm-avail" class="modal-input" placeholder="Availability" value="'+(PROFILE.availability||'')+'" style="font-size:12px;padding:9px 12px">'+
      '</div>'+
      // Submit
      '<div style="display:flex;gap:10px">'+
        '<button onclick="submitProposalModal()" style="flex:1;background:var(--pip);color:#fff;border:none;font-family:Outfit,sans-serif;font-size:14px;font-weight:700;padding:13px;border-radius:8px;cursor:pointer;box-shadow:0 0 20px rgba(45,157,232,0.25)">Generate proposal &#8594;</button>'+
        '<button onclick="closeProposalModal()" style="background:none;border:1px solid var(--bor2);color:var(--tx2);font-family:Outfit,sans-serif;font-size:13px;padding:13px 20px;border-radius:8px;cursor:pointer">Cancel</button>'+
      '</div>'+
    '</div>';
  document.body.appendChild(overlay);
  overlay.addEventListener('click',function(e){if(e.target===overlay)closeProposalModal();});
  setTimeout(function(){
    var col=document.getElementById('pm-color');
    var hex=document.getElementById('pm-color-hex');
    if(col&&hex)col.oninput=function(){hex.textContent=col.value;};
  },50);
}

function submitProposalModal(){
  var g=function(id){return(document.getElementById(id)||{value:''}).value.trim();};
  var ta=function(id){return(document.getElementById(id)||{value:''}).value.trim();};
  profileLoad();
  var consultant={
    name:g('pm-name')||PROFILE.name||'',
    agency:g('pm-agency')||PROFILE.agency||'',
    role:g('pm-role')||'Fractional CMO',
    tagline:g('pm-tagline')||PROFILE.tagline||'',
    bio:ta('pm-bio')||PROFILE.bio||'',
    email:g('pm-email')||PROFILE.email||'',
    phone:g('pm-phone')||PROFILE.phone||'',
    calendly:g('pm-calendly')||PROFILE.calendly||'',
    logo:g('pm-logo')||PROFILE.wl_logo||'',
    color:g('pm-color')||PROFILE.wl_color||PROFILE.color||'#2d9de8',
    deal_size:g('pm-deal')||PROFILE.deal_size||'',
    client_size:g('pm-engagement')||PROFILE.client_size||'',
    availability:g('pm-avail')||PROFILE.availability||''
  };
  var lead=window._currentLead||{};
  var data={
    consultant:consultant,
    lead:{
      company:g('pm-prospect-co')||lead.company||'',
      prospect_logo:g('pm-prospect-logo')||lead.prospect_logo||'',
      sector:lead.sector||'',stage:lead.stage||'',hq:lead.hq||'',
      funding_amount:lead.funding_amount||'',
      score:lead.gtm_readiness_score||0,
      label:lead.gtm_label||'',
      why_fit:ta('pm-why')||lead.why_fit||'',
      pitch_opener:ta('pm-approach')||lead.pitch_opener||'',
      gtm_signals:lead.gtm_signals||{}
    },
    services:PROFILE.services||[],
    cases:PROFILE.case_studies||[]
  };
  var encoded=btoa(unescape(encodeURIComponent(JSON.stringify(data))));
  closeProposalModal();
  window.open(safeOrigin()+'/proposal/'+encoded,'_blank');
  showInfoToast('Proposal opening\u2026');
}

function findOnLinkedIn(){
  var r = window._currentLead;
  if(!r) return;
  var url = 'https://www.linkedin.com/search/results/companies/?keywords=' + encodeURIComponent(r.company||'');
  window.open(url, '_blank');
}

function deleteCurrentLead(){
  var r = window._currentLead;
  if(!r) return;
  if(!confirm('Delete ' + (r.company||'this lead') + '? This cannot be undone.')) return;
  DB = DB.filter(function(x){ return x._id !== r._id; });
  INBOX = INBOX.filter(function(x){ return x._id !== r._id; });
  save(); updateBadges();
  showUpsellToast((r.company||'Lead') + ' deleted');
  setPage('leads');
}

function renderCandidateCards(candidates){
  var wrap=document.getElementById('sourcer-candidates-section');
  if(!wrap)return;
  wrap.style.display='block';
  wrap.innerHTML='';

  // ── Results ────────────────────────────────────────────────────
  if(candidates&&candidates.length){
    var resTitle=document.createElement('div');
    resTitle.style.cssText='font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--tx3);margin-bottom:10px';
    resTitle.textContent='Results ('+candidates.length+')';
    wrap.appendChild(resTitle);

    candidates.forEach(function(c){
      var score=c.fit_score||0;
      var scol=score>=75?'var(--pip2)':score>=50?'var(--amb)':'var(--tx3)';
      var isSaved=PH_SAVED_CANDIDATES.some(function(x){return x.name===c.name&&x.current_company===c.current_company;});
      var isTrash=PH_TRASH_CANDIDATES.some(function(x){return x.name===c.name&&x.current_company===c.current_company;});
      if(isTrash) return;
      var card=document.createElement('div');card.className='ph-card';card.style.marginBottom='12px';
      // Score badge + name
      var hdr=document.createElement('div');hdr.style.cssText='display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:10px';
      var nb=document.createElement('div');nb.style.flex='1';nb.style.minWidth='0';
      var ne=document.createElement('div');ne.style.cssText='font-size:14px;font-weight:700;color:var(--tx);margin-bottom:2px';ne.textContent=c.name||'Unknown';
      var re2=document.createElement('div');re2.style.cssText='font-size:12px;color:var(--tx3)';
      re2.textContent=(c.current_title||'')+(c.current_company?' at '+c.current_company:'');
      nb.appendChild(ne);nb.appendChild(re2);
      if(c.location){var lo=document.createElement('div');lo.style.cssText='font-size:11px;color:var(--tx3);margin-top:2px';lo.textContent=c.location;nb.appendChild(lo);}
      var se=document.createElement('div');se.style.cssText='text-align:right;flex-shrink:0;margin-left:12px';
      var sn=document.createElement('div');sn.style.cssText='font-size:24px;font-weight:800;color:'+scol+';font-family:JetBrains Mono,monospace;line-height:1';sn.textContent=score;
      var sl=document.createElement('div');sl.style.cssText='font-size:9px;color:'+scol+';font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-top:2px';
      sl.textContent=score>=75?'Strong fit':score>=50?'Good fit':'Weak fit';
      se.appendChild(sn);se.appendChild(sl);hdr.appendChild(nb);hdr.appendChild(se);card.appendChild(hdr);
      // Why fit
      if(c.why_fit){var wf=document.createElement('div');wf.style.cssText='font-size:12px;color:var(--tx2);margin-bottom:10px;line-height:1.5;padding:8px 10px;background:var(--sur2);border-radius:6px;border-left:3px solid '+scol;wf.textContent=c.why_fit;card.appendChild(wf);}
      // InMail toggle
      if(c.inmail){
        var iw=document.createElement('div');iw.style.cssText='margin-bottom:10px';
        var it=document.createElement('button');it.style.cssText='font-size:11px;font-weight:700;color:var(--pip);background:none;border:none;cursor:pointer;font-family:Outfit,sans-serif;padding:0';it.textContent='Show InMail draft ▾';
        var ib=document.createElement('div');ib.style.cssText='display:none;font-size:12px;color:var(--tx2);line-height:1.6;padding:10px 12px;background:var(--sur2);border:1px solid var(--bor);border-radius:6px;margin-top:6px;font-style:italic';ib.textContent=c.inmail;
        var _im=c.inmail;var exp=false;
        var cp2=document.createElement('button');cp2.style.cssText='font-size:10px;color:#fff;background:var(--pip);border:none;cursor:pointer;font-family:Outfit,sans-serif;padding:3px 10px;border-radius:4px;margin-left:8px';cp2.textContent='Copy';
        cp2.onclick=function(){navigator.clipboard.writeText(_im);cp2.textContent='Copied!';setTimeout(function(){cp2.textContent='Copy';},1500);};
        it.onclick=function(){exp=!exp;ib.style.display=exp?'block':'none';it.textContent=exp?'Hide InMail draft ▴':'Show InMail draft ▾';};
        it.appendChild(cp2);iw.appendChild(it);iw.appendChild(ib);card.appendChild(iw);
      }
      // Buttons
      var btns=document.createElement('div');btns.style.cssText='display:flex;gap:8px;flex-wrap:wrap;align-items:center';
      var liUrl=c.linkedin_url||('https://www.linkedin.com/search/results/people/?keywords='+encodeURIComponent((c.name||'')+' '+(c.current_title||'')));
      var la=document.createElement('a');la.href=liUrl;la.target='_blank';la.rel='noopener';
      la.style.cssText='display:inline-flex;align-items:center;gap:5px;border:1px solid #0a66c2;color:#0a66c2;font-size:11px;font-weight:700;padding:5px 12px;border-radius:6px;text-decoration:none;font-family:Outfit,sans-serif;background:none';
      la.innerHTML='<svg width="11" height="11" viewBox="0 0 24 24" fill="#0a66c2"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>'+(c.linkedin_url?'View':'Find');
      btns.appendChild(la);
      // Save → moves card to Saved section
      if(!isSaved){
        var saveBtn=document.createElement('button');saveBtn.className='abtn';
        saveBtn.style.cssText='font-size:11px;padding:5px 12px;border-radius:6px;cursor:pointer;font-family:Outfit,sans-serif';
        saveBtn.textContent='Save';
        (function(_c,_card){saveBtn.onclick=function(){
          if(!PH_SAVED_CANDIDATES.some(function(x){return x.name===_c.name&&x.current_company===_c.current_company;}))
            PH_SAVED_CANDIDATES.unshift(_c);
          phSave();
          _card.style.opacity='0';_card.style.transition='opacity .2s';
          setTimeout(function(){if(_card.parentNode)_card.parentNode.removeChild(_card);renderCandidateBottomSections();},200);
          showInfoToast('Candidate saved ✓');
        };})(c,card);
        btns.appendChild(saveBtn);
      }
      // Remove → goes to trash
      var rmBtn=document.createElement('button');
      rmBtn.style.cssText='font-size:11px;padding:5px 12px;border-radius:6px;cursor:pointer;font-family:Outfit,sans-serif;border:1px solid var(--bor);background:none;color:var(--tx3)';
      rmBtn.textContent='Remove';
      (function(_c,_card){rmBtn.onclick=function(){
        _c._trashed_at=Date.now();
        PH_TRASH_CANDIDATES.unshift(_c);
        phSave();
        _card.style.opacity='0';_card.style.transition='opacity .2s';
        setTimeout(function(){if(_card.parentNode)_card.parentNode.removeChild(_card);renderCandidateBottomSections();},200);
      };})(c,card);
      btns.appendChild(rmBtn);
      card.appendChild(btns);
      wrap.appendChild(card);
    });
  } else {
    var empty=document.createElement('div');empty.style.cssText='padding:20px 0;text-align:center;color:var(--tx3);font-size:12px';empty.textContent='No candidates yet - paste a JD and click Find Candidates';
    wrap.appendChild(empty);
  }

  // Render saved + trash sections below
  renderCandidateBottomSections();
}

function renderCandidateBottomSections(){
  var wrap=document.getElementById('sourcer-candidates-section');
  if(!wrap) return;
  // Remove old saved/trash sections if present
  var old=wrap.querySelector('.cand-bottom-sections');
  if(old) old.remove();
  var bottom=document.createElement('div');bottom.className='cand-bottom-sections';

  // ── Saved Candidates ──────────────────────────────────────
  if(PH_SAVED_CANDIDATES.length){
    var savedWrap=document.createElement('div');savedWrap.style.cssText='margin-top:24px';
    var savedTitle=document.createElement('div');savedTitle.style.cssText='font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--tx3);margin-bottom:10px;padding-bottom:8px;border-bottom:1px solid var(--bor)';
    savedTitle.textContent='Saved ('+PH_SAVED_CANDIDATES.length+')';
    savedWrap.appendChild(savedTitle);
    PH_SAVED_CANDIDATES.forEach(function(c){
      var score=c.fit_score||0;var scol=score>=75?'var(--pip2)':score>=50?'var(--amb)':'var(--tx3)';
      var mini=document.createElement('div');mini.className='ph-card';mini.style.cssText='margin-bottom:10px;border-left:3px solid var(--pip)';
      var row=document.createElement('div');row.style.cssText='display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:8px';
      var nb=document.createElement('div');nb.style.flex='1';
      var ne=document.createElement('div');ne.style.cssText='font-size:13px;font-weight:700;color:var(--tx)';ne.textContent=c.name||'';
      var re2=document.createElement('div');re2.style.cssText='font-size:11px;color:var(--tx3)';re2.textContent=(c.current_title||'')+(c.current_company?' at '+c.current_company:'');
      nb.appendChild(ne);nb.appendChild(re2);
      var sn=document.createElement('div');sn.style.cssText='font-size:20px;font-weight:800;color:'+scol+';font-family:JetBrains Mono,monospace;margin-left:10px;flex-shrink:0';sn.textContent=score;
      row.appendChild(nb);row.appendChild(sn);mini.appendChild(row);
      var btns=document.createElement('div');btns.style.cssText='display:flex;gap:8px';
      var liUrl=c.linkedin_url||('https://www.linkedin.com/search/results/people/?keywords='+encodeURIComponent((c.name||'')+' '+(c.current_title||'')));
      var la=document.createElement('a');la.href=liUrl;la.target='_blank';la.rel='noopener';la.style.cssText='font-size:11px;font-weight:700;color:#0a66c2;border:1px solid #0a66c2;padding:4px 10px;border-radius:5px;text-decoration:none;font-family:Outfit,sans-serif;background:none';la.textContent=c.linkedin_url?'View':'Find';
      btns.appendChild(la);
      var unBtn=document.createElement('button');unBtn.style.cssText='font-size:11px;padding:4px 10px;border-radius:5px;cursor:pointer;font-family:Outfit,sans-serif;border:1px solid var(--bor);background:none;color:var(--tx3)';unBtn.textContent='Remove';
      (function(_c){unBtn.onclick=function(){PH_SAVED_CANDIDATES=PH_SAVED_CANDIDATES.filter(function(x){return !(x.name===_c.name&&x.current_company===_c.current_company);});phSave();renderCandidateBottomSections();};})(c);
      btns.appendChild(unBtn);mini.appendChild(btns);savedWrap.appendChild(mini);
    });
    bottom.appendChild(savedWrap);
  }

  // ── Trash ─────────────────────────────────────────────────
  pruneTrash();
  if(PH_TRASH_CANDIDATES.length){
    var trashWrap=document.createElement('div');trashWrap.style.cssText='margin-top:20px';
    var trashTitle=document.createElement('div');trashTitle.style.cssText='font-size:11px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--tx3);margin-bottom:8px;padding-bottom:6px;border-bottom:1px solid var(--bor)';
    trashTitle.textContent='Trash ('+PH_TRASH_CANDIDATES.length+') \u00b7 auto-deletes in 7 days';
    trashWrap.appendChild(trashTitle);
    PH_TRASH_CANDIDATES.forEach(function(c){
      var mini=document.createElement('div');mini.style.cssText='display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--bor);opacity:.5';
      var nl=document.createElement('div');nl.style.cssText='font-size:12px;color:var(--tx3)';nl.textContent=(c.name||'')+(c.current_company?' \u00b7 '+c.current_company:'');
      var rb=document.createElement('button');rb.style.cssText='font-size:10px;padding:3px 8px;border-radius:4px;cursor:pointer;font-family:Outfit,sans-serif;border:1px solid var(--bor);background:none;color:var(--tx3)';rb.textContent='Restore';
      (function(_c){rb.onclick=function(){PH_TRASH_CANDIDATES=PH_TRASH_CANDIDATES.filter(function(x){return !(x.name===_c.name&&x.current_company===_c.current_company);});if(!PH_SAVED_CANDIDATES.some(function(x){return x.name===_c.name&&x.current_company===_c.current_company;})){delete _c._trashed_at;PH_SAVED_CANDIDATES.unshift(_c);}phSave();renderCandidateBottomSections();};})(c);
      mini.appendChild(nl);mini.appendChild(rb);trashWrap.appendChild(mini);
    });
    bottom.appendChild(trashWrap);
  }

  wrap.appendChild(bottom);
}



function phApplyJob(id){
  var job=PH_JOBS.find(function(j){return j._id===id;})||PH_SAVED.find(function(j){return j._id===id;});
  if(!job)return;
  if(job.apply_url){
    var isEmail=job.apply_method==='email'||job.apply_url.indexOf('@')>=0;
    if(isEmail){navigator.clipboard.writeText(job.apply_url);showUpsellToast('Email copied: '+job.apply_url);}
    else{window.open(job.apply_url,'_blank');}
  }
  PH_JOBS=PH_JOBS.filter(function(j){return j._id!==id;});
  PH_SAVED=PH_SAVED.filter(function(j){return j._id!==id;});
  if(!PH_APPLIED.some(function(j){return j._id===id;})){
    job._applied_at=new Date().toLocaleDateString();PH_APPLIED.unshift(job);
  }
  phSave();phRenderJobs();
  showInfoToast('Moved to Applied To ✓');
}

function phShowBottomTab(tab){
  phBottomTab=tab;
  var sg=document.getElementById('ph-saved-grid');var ag=document.getElementById('ph-applied-grid');
  var st=document.getElementById('ph-tab-saved');var at2=document.getElementById('ph-tab-applied');
  if(sg)sg.style.display=tab==='saved'?'block':'none';
  if(ag)ag.style.display=tab==='applied'?'block':'none';
  if(st){st.style.borderBottomColor=tab==='saved'?'var(--pip)':'transparent';st.style.color=tab==='saved'?'var(--tx)':'var(--tx3)';}
  if(at2){at2.style.borderBottomColor=tab==='applied'?'var(--pip)':'transparent';at2.style.color=tab==='applied'?'var(--tx)':'var(--tx3)';}
}

var _idleTimer = null;
var IDLE_TIMEOUT = 30 * 60 * 1000; // 30 minutes

function resetIdleTimer(){
  clearTimeout(_idleTimer);
  _idleTimer = setTimeout(function(){
    // Auto sign out after 30 min idle
    var u = authGetUser();
    if(u){
      authSignOut();
      showAuthScreen('login');
      showLimitToast('You have been signed out after 30 minutes of inactivity.');
    }
  }, IDLE_TIMEOUT);
}

function initIdleTimer(){
  ['mousemove','keydown','click','scroll','touchstart'].forEach(function(ev){
    document.addEventListener(ev, resetIdleTimer, {passive:true});
  });
  resetIdleTimer();
}

function pruneTrash(){
  var week=7*24*60*60*1000;
  var now=Date.now();
  PH_TRASH_CANDIDATES=PH_TRASH_CANDIDATES.filter(function(c){return c._trashed_at&&(now-c._trashed_at)<week;});
}

// ── SECURITY ──────────────────────────────────────────────
(function(){
  // Disable right-click context menu
  document.addEventListener('contextmenu',function(e){e.preventDefault();return false;});
  // Disable common keyboard shortcuts for viewing source/dev tools
  document.addEventListener('keydown',function(e){
    // F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+Shift+C, Ctrl+U, Ctrl+S
    if(e.key==='F12'||(e.ctrlKey&&e.shiftKey&&['I','J','C','i','j','c'].indexOf(e.key)>=0)||
       (e.ctrlKey&&['U','u','S','s'].indexOf(e.key)>=0)){
      e.preventDefault();e.stopPropagation();return false;
    }
  });
  // Disable text selection on UI (but allow inputs)
  document.addEventListener('selectstart',function(e){
    if(e.target.tagName==='INPUT'||e.target.tagName==='TEXTAREA')return;
    e.preventDefault();
  });
  // Disable drag
  document.addEventListener('dragstart',function(e){
    if(e.target.tagName!=='INPUT')e.preventDefault();
  });
})();
// ── END SECURITY ──────────────────────────────────────────

function generateProposal(r){
  if(!r){showInfoToast('No lead selected');return;}
  profileLoad();
  var user=authGetUser();
  var data={
    consultant:{
      name:PROFILE.name||'',agency:PROFILE.agency||'',role:PROFILE.role||'Fractional CMO',
      tagline:PROFILE.tagline||'',bio:PROFILE.bio||'',
      email:PROFILE.show_email===false?'':(PROFILE.email||(user&&user.email)||''),
      phone:PROFILE.phone||'',linkedin:PROFILE.linkedin||'',
      website:PROFILE.website||'',calendly:PROFILE.calendly||'',
      logo:PROFILE.wl_logo||null,color:PROFILE.wl_color||PROFILE.color||'#2d9de8',
      deal_size:PROFILE.deal_size||'',client_size:PROFILE.client_size||'',availability:PROFILE.availability||''
    },
    lead:{
      company:r.company||'',sector:r.sector||'',stage:r.stage||'',hq:r.hq||'',
      funding_amount:r.funding_amount||'',score:r.gtm_readiness_score||0,
      label:r.gtm_label||'',why_fit:r.why_fit||'',pitch_opener:r.pitch_opener||'',
      gtm_signals:r.gtm_signals||{},prospect_logo:r.prospect_logo||''
    },
    services:PROFILE.services||[],
    cases:PROFILE.case_studies||[]
  };
  var encoded=btoa(unescape(encodeURIComponent(JSON.stringify(data))));
  window.open(safeOrigin()+'/proposal/'+encoded,'_blank');
  showInfoToast('Proposal opening\u2026');
}

document.addEventListener('DOMContentLoaded',function(){
  console.log('SCOUT v6 loaded');

  // Handle Supabase email confirmation redirect (hash fragment)
  var hash = window.location.hash;
  if(hash && hash.indexOf('access_token=') >= 0){
    var params = {};
    hash.replace(/^#/,'').split('&').forEach(function(p){
      var kv = p.split('='); params[kv[0]] = decodeURIComponent(kv[1]||'');
    });
    if(params.access_token){
      // Store the token and fetch user
      localStorage.setItem('sb_token', params.access_token);
      if(params.refresh_token) localStorage.setItem('sb_refresh', params.refresh_token);
      // Clean the URL
      window.history.replaceState(null,'',window.location.pathname);
      // Fetch user info
      var h = {'apikey': SUPA_KEY, 'Authorization': 'Bearer '+params.access_token, 'Content-Type':'application/json'};
      fetch(SUPA_URL+'/auth/v1/user',{headers:h}).then(function(r){return r.json();}).then(function(u){
        if(u && u.id){
          localStorage.setItem('sb_user', JSON.stringify(u));
          SUPA_USER = u;
          if(u.user_metadata && u.user_metadata.name) PROFILE.name = u.user_metadata.name;
          if(u.email) PROFILE.email = u.email;
          try{localStorage.setItem('scout_profile',JSON.stringify(PROFILE));}catch(e){}
        }
        initApp();
      }).catch(function(){ initApp(); });
      return;
    }
  }

  var token=localStorage.getItem('sb_token'),user=authGetUser();
  if(token&&user){SUPA_USER=user;if(user.email)PROFILE.email=user.email;if(user.user_metadata&&user.user_metadata.name)PROFILE.name=user.user_metadata.name;initApp();}
  else{showAuthScreen('signup');}
});
"""

HTML = ("<!DOCTYPE html>\n<html>\n<head>\n"
  "<meta charset='UTF-8'>\n"
  "<meta name='viewport' content='width=device-width,initial-scale=1'>\n"
  "<title>Scout</title>\n"
  "<link href='https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap' rel='stylesheet'>\n"
  "<link rel='icon' type='image/png' href='data:image/png;base64,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'>\n"
  "<style>" + CSS + "</style>\n"
  "</head>\n<body>\n"

  "<div id='app-loading' style='position:fixed;inset:0;background:#020408;z-index:9999;display:none;align-items:center;justify-content:center'><div style='width:28px;height:28px;border:2px solid rgba(45,157,232,0.15);border-top-color:#2d9de8;border-radius:50%;animation:spin .7s linear infinite'></div><style>@keyframes spin{to{transform:rotate(360deg)}}</style></div>"

  "<div id='ob-splash' style='display:none;opacity:0;position:fixed;inset:0;background:#020408;z-index:99990;flex-direction:column;align-items:center;justify-content:center;transition:opacity .5s ease;padding:24px;overflow-y:auto'>"
    "<div id='ob-step1' style='text-align:center;width:100%;max-width:420px'>"
      "<div style='display:flex;align-items:center;gap:8px;justify-content:center;margin-bottom:32px'><div style='width:8px;height:8px;border-radius:50%;background:#2d9de8;box-shadow:0 0 16px #2d9de8'></div><span style='font-size:13px;font-weight:700;letter-spacing:.28em;text-transform:uppercase;color:#eef4ff;font-family:Outfit,sans-serif'>Scout</span></div>"
      "<div style='font-size:28px;font-weight:800;letter-spacing:-.04em;color:#eef4ff;margin-bottom:10px;font-family:Outfit,sans-serif'>Find your next client.</div>"
      "<div style='font-size:14px;color:#7da8c8;max-width:340px;line-height:1.65;margin-bottom:32px'>AI lead generation for fractional CMOs and marketing agencies.</div>"
      "<button onclick='scoutStep(2)' style='background:#2d9de8;color:#fff;border:none;font-family:Outfit,sans-serif;font-size:15px;font-weight:700;padding:14px 48px;border-radius:8px;cursor:pointer;box-shadow:0 0 32px rgba(45,157,232,0.3)'>Get started &#8594;</button>"
      "<div style='margin-top:14px'><button onclick='obSkip()' style='background:none;border:none;color:#2a4a6a;font-size:12px;cursor:pointer;font-family:Outfit,sans-serif;text-decoration:underline'>Skip for now</button></div>"
    "</div>"
    "<div id='ob-step2' style='display:none;width:100%;max-width:420px'>"
      "<div style='font-size:22px;font-weight:800;letter-spacing:-.03em;color:#eef4ff;margin-bottom:6px;font-family:Outfit,sans-serif;text-align:center'>Set up your profile</div>"
      "<div style='font-size:13px;color:#7da8c8;margin-bottom:20px;text-align:center'>Personalises your pitch openers.</div>"
      "<div style='display:flex;flex-direction:column;gap:10px;width:100%'>"
        "<input class='modal-input' id='ob-name' placeholder='Your name or agency' style='font-size:15px;padding:14px 18px'>"
        "<input class='modal-input' id='ob-tagline' placeholder='What you specialise in' style='font-size:14px;padding:13px 18px'>"
        "<button onclick='scoutStep(3)' style='background:#2d9de8;color:#fff;border:none;font-family:Outfit,sans-serif;font-size:15px;font-weight:700;padding:14px;border-radius:8px;cursor:pointer;margin-top:4px'>Continue &#8594;</button>"
        "<button onclick='obSkip()' style='background:none;border:none;color:#2a4a6a;font-size:12px;cursor:pointer;font-family:Outfit,sans-serif;text-decoration:underline;padding:4px'>Skip for now</button>"
      "</div>"
    "</div>"
    "<div id='ob-step3' style='display:none;width:100%;max-width:540px'>"
      "<div style='font-size:22px;font-weight:800;letter-spacing:-.03em;color:#eef4ff;margin-bottom:6px;font-family:Outfit,sans-serif;text-align:center'>Choose your plan</div>"
      "<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:16px;width:100%'>"
        "<div onclick='obChoosePlan(\"free\")' class='ob-plan-card' id='opc-free'><div class='ob-plan-name'>Free</div><div class='ob-plan-price'>$0</div><div class='ob-plan-desc'>5 researches/mo</div></div>"
        "<div onclick='obChoosePlan(\"pro\")' class='ob-plan-card ob-plan-hot selected' id='opc-pro'><div class='ob-plan-badge'>Popular</div><div class='ob-plan-name'>Pro</div><div class='ob-plan-price'>$29<span>/mo</span></div><div class='ob-plan-desc'>Unlimited research</div></div>"
        "<div onclick='obChoosePlan(\"agency\")' class='ob-plan-card' id='opc-agency'><div class='ob-plan-name'>Agency</div><div class='ob-plan-price'>$99<span>/mo</span></div><div class='ob-plan-desc'>5 team members</div></div>"
      "</div>"
      "<button id='ob-enter-btn' onclick='obFinish()' style='width:100%;background:#2d9de8;color:#fff;border:none;font-family:Outfit,sans-serif;font-size:15px;font-weight:700;padding:14px;border-radius:8px;cursor:pointer;box-shadow:0 0 24px rgba(45,157,232,0.3)'>Enter Scout &#8594;</button>"
    "</div>"
  "</div>"

  "<div class='topbar'>"
    "<button class='logo-btn' onclick='goHome()'>"
      "<div class='ndot'></div>"
      "<span class='logo-text'>Scout</span>"
    "</button>"
    "<button id='page-back-btn' onclick='goBack()' style='display:none;align-items:center;gap:6px;background:none;border:none;color:var(--tx3);font-size:12px;font-weight:600;cursor:pointer;padding:6px 10px;border-radius:6px;font-family:Outfit,sans-serif'>&#8592; Back</button>"
    "<div id='topbar-right' class='topbar-right'>"
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

  "<button class='sidebar-item' id='si-search' onclick='navTo(\"search\")'>Research</button>"
    "<button class='sidebar-item' id='si-inbox' onclick='navTo(\"inbox\")' style='display:none'>Inbox<span id='inbox-badge-si' style='display:none;margin-left:auto;background:var(--pip2);color:#fff;font-size:9px;font-weight:700;padding:1px 6px;border-radius:999px'>0</span></button>"

  "<button class='sidebar-item' id='si-profile' onclick='navTo(\"profile\")' style='display:none'>Profile</button>"
  "<button class='sidebar-item' id='si-teams' onclick='navTo(\"teams\")'>Team</button>"
"</div>"
    "<div class='sidebar-pip'>"
      "<div class='sidebar-pip-row'>"
        "<img src='data:image/png;base64,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' style='width:32px;height:32px;object-fit:contain'>"
        "<div><div class='sidebar-pip-name'>Pip Hunt</div><div class='sidebar-pip-sub'>Find open roles</div></div>"
        "<button onclick='navTo(\"piphunt\")' style='margin-left:auto;background:var(--pip);color:#fff;border:none;font-size:11px;font-weight:700;padding:5px 12px;border-radius:var(--r-pill);cursor:pointer;font-family:Nunito,sans-serif'>Open</button>"
      "</div>"
    "</div>"

    "<div id='sb-tier-features' style='display:none;padding:12px 16px;border-top:1px solid var(--bor)'>"
    "<div id='sb-tier-label' style='font-size:9px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--tx3);margin-bottom:8px'></div>"
    "<div id='sb-tier-items'></div>"
    "</div>"  "</div>\n"

  "<div class='page' id='page-search'>"
    "<div class='search-hero'>"
      "<h1>Find your next client</h1>"
      "<p>Research any company to get a full GTM profile, score and pitch opener.</p>"
    "</div>"
    "<div class='search-box'>"
      "<input id='ci' type='text' placeholder='Company name'>"
      "<button id='rb'>Research →</button>"
    "</div>"
    "<div id='ldg'><div class='spinner'></div><span>Researching <b id='lname'></b>... <span id='ltimer'>0s</span></span></div>"
    "<div id='err'></div>"
        "<div class='fetch-hero'>"
      "<div class='fetch-hero-title'> Fetch New Leads</div>"
      "<div class='fetch-hero-sub'>Pull recently funded companies from the web - they land in your Inbox for review</div>"
      "<button id='fetch-btn' class='fetch-hero-btn'>Fetch Leads</button>"
      "<div id='fetch-ldg' style='display:none;align-items:center;justify-content:center;gap:10px;margin-top:16px;font-size:13px;color:var(--tx3)'><div class='spinner'></div><span>Searching funding news...</span></div>"
      "<div id='fetch-err'></div>"
      "<div id='fetch-results'>"
        "<div style='font-size:12px;color:var(--tx3);margin-bottom:12px;text-align:center'>Select companies to research - they go to your Inbox:</div>"
        "<div class='fetch-list' id='fetch-list'></div>"
        "<div style='display:flex;align-items:center;justify-content:center;margin-top:12px'>"
          "<button id='res-sel-btn'>Research Selected →</button>"
          "<span id='fetch-count' style='margin-left:12px'></span>"
        "</div>"
      "</div>"
    "</div>"
  "</div>\n"

 
  "<div class='page' id='page-dashboard'>"
  "<div style='padding:20px 24px 0'><div class='stat-cards' id='dash-stats'></div></div>"
  "<div style='padding:12px 24px 24px'>"
    "<div style='margin-bottom:20px'>"
  "<div style='font-size:14px;font-weight:700;color:var(--tx);margin-bottom:10px'>Recent Leads</div>"
  "<div id='dash-recent-leads'></div>"
  "</div>"
"<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:14px'>"
  "<div style='font-size:16px;font-weight:700;color:var(--tx)'>Pipeline</div>"
  "<div style='display:flex;gap:8px;align-items:center'>"
  "<button onclick=\"navTo('search')\" style='background:var(--pip);color:#fff;border:none;font-family:Outfit,sans-serif;font-size:11px;font-weight:700;padding:6px 14px;border-radius:6px;cursor:pointer'>+ Research</button>"
  "<div id='inbox-agency-btn'></div>"
  "</div>"
  "</div>"
  "<div class='kanban-board' id='dash-kanban-board'></div>"
  "</div>"
  "</div>"

  "<div class='page' id='page-lead-detail'>"
  "<button class='ld-back' onclick=\"setPage('dashboard')\">&#8592; Back to Dashboard</button>"
  "<div id='lead-detail-content'></div>"
  "</div>"
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
      "<span style='font-size:12px;color:var(--tx3)'>Review fetched leads - save to Pipeline or dismiss</span>"
    "</div>"
    "<div class='inbox-grid' id='inbox-grid'></div>"
  "</div>\n"

  "<div class='page' id='page-profile'>"
    "<div id='profile-root' style='padding:4px 0'></div>"
  "</div>\n"

  "<div class='page' id='page-teams'>"
    "<div style='padding:28px 24px 0;max-width:760px;margin:0 auto'>"
      "<div style='font-size:24px;font-weight:700;color:var(--tx);margin-bottom:6px'>Team</div>"
      "<div style='font-size:14px;color:var(--tx3);margin-bottom:28px'>Manage team members. Everyone shares your lead database and credit pool.</div>"
      "<div id='teams-root'></div>"
    "</div>"
  "</div>\n"

  "<div class='page' id='page-piphunt'>"
  "<div style='padding:20px 24px 0'>"
  "<div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap;gap:12px'>"
  "<div>"
  "<div id='ph-mode-title' style='font-size:22px;font-weight:800;letter-spacing:-.03em;color:var(--tx)'>Find your next role</div>"
  "<div id='ph-mode-sub' style='font-size:13px;color:var(--tx3);margin-top:3px'>Spot open positions at funded startups. Research before you apply.</div>"
  "</div>"
  "<div style='display:flex;background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r);padding:3px;gap:2px'>"
  "<button id='ph-mode-hunt' onclick='phSetMode(\"hunt\")' style='background:var(--pip);color:#fff;border:none;font-family:Outfit,sans-serif;font-size:12px;font-weight:700;padding:7px 16px;border-radius:5px;cursor:pointer'>Find Jobs</button>"
  "<button id='ph-mode-source' onclick='phSetMode(\"source\")' style='background:none;color:var(--tx3);border:none;font-family:Outfit,sans-serif;font-size:12px;font-weight:700;padding:7px 16px;border-radius:5px;cursor:pointer'>Source Candidates</button>"
  "</div>"
  "</div>"
  "</div>"
  "<div id='ph-hunt-mode' style='padding:0 24px 24px'>"
  "<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px'>"
  "  <button class='ph-tab active' data-cat='cmo' onclick='phSetCategory(\"cmo\")' style='background:var(--pip);color:#fff;border:1px solid var(--pip);font-size:12px;font-weight:600;padding:7px 16px;border-radius:999px;cursor:pointer;font-family:Outfit,sans-serif'>CMO / VP Marketing</button>"
  "  <button class='ph-tab' data-cat='design' onclick='phSetCategory(\"design\")' style='background:var(--sur2);color:var(--tx3);border:1px solid var(--bor2);font-size:12px;font-weight:600;padding:7px 16px;border-radius:999px;cursor:pointer;font-family:Outfit,sans-serif'>Design Leadership</button>"
  "  <button class='ph-tab' data-cat='fractional' onclick='phSetCategory(\"fractional\")' style='background:var(--sur2);color:var(--tx3);border:1px solid var(--bor2);font-size:12px;font-weight:600;padding:7px 16px;border-radius:999px;cursor:pointer;font-family:Outfit,sans-serif'>Fractional Roles</button>"
  "</div>"
  "<div style='display:flex;gap:8px;margin-bottom:12px;align-items:center'>"
  "  <input id='ph-search-input' type='text' placeholder='Search a specific role... (optional)' style='flex:1;background:var(--sur2);border:1px solid var(--bor2);color:var(--tx);font-family:Outfit,sans-serif;font-size:13px;padding:9px 14px;border-radius:8px;outline:none' onkeydown='if(event.key===\"Enter\")phFetch()'>"
  "  <button id='ph-fetch-btn' onclick='phFetch()' style='background:var(--pip);color:#fff;border:none;font-family:Outfit,sans-serif;font-size:13px;font-weight:700;padding:9px 20px;border-radius:8px;cursor:pointer;white-space:nowrap'>Search Jobs</button>"
  "  <span id='ph-status' style='font-size:12px;color:var(--tx3);white-space:nowrap'></span>"
  "</div>"
  "<div style='display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap'>"
  "  <button class='ph-filter' id='ph-filter-remote' onclick='phToggleFilter(\"remote\")' style='background:var(--sur2);border:1px solid var(--bor);color:var(--tx3);font-size:11px;font-weight:600;padding:5px 14px;border-radius:999px;cursor:pointer;font-family:Outfit,sans-serif'>Remote only</button>"
  "  <button class='ph-filter' id='ph-filter-startup' onclick='phToggleFilter(\"startup\")' style='background:var(--sur2);border:1px solid var(--bor);color:var(--tx3);font-size:11px;font-weight:600;padding:5px 14px;border-radius:999px;cursor:pointer;font-family:Outfit,sans-serif'>AI / Tech</button>"
  "  <button class='ph-filter' id='ph-filter-week' onclick='phToggleFilter(\"week\")' style='background:var(--sur2);border:1px solid var(--bor);color:var(--tx3);font-size:11px;font-weight:600;padding:5px 14px;border-radius:999px;cursor:pointer;font-family:Outfit,sans-serif'>This week</button>"
  "</div>"
  "<div class='ph-grid' id='ph-jobs-grid'></div>"
  "<div id='ph-bottom-section' style='margin-top:28px;display:none'>"
  "  <div style='display:flex;gap:0;border-bottom:1px solid var(--bor);margin-bottom:16px'>"
  "    <button id='ph-tab-saved' onclick='phShowBottomTab(\"saved\")' style='background:none;border:none;border-bottom:2px solid var(--pip);color:var(--tx);font-family:Outfit,sans-serif;font-size:12px;font-weight:700;padding:8px 16px;cursor:pointer;margin-bottom:-1px'>Saved Jobs</button>"
  "    <button id='ph-tab-applied' onclick='phShowBottomTab(\"applied\")' style='background:none;border:none;border-bottom:2px solid transparent;color:var(--tx3);font-family:Outfit,sans-serif;font-size:12px;font-weight:700;padding:8px 16px;cursor:pointer;margin-bottom:-1px'>Applied To</button>"
  "  </div>"
  "  <div id='ph-saved-grid'></div>"
  "  <div id='ph-applied-grid' style='display:none'></div>"
  "</div>"
  "</div>"
  "<div id='ph-source-mode' style='display:none;padding:0 24px 24px'>"
  "<div style='background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);padding:20px;margin-bottom:14px'>"
  "<div style='font-size:14px;font-weight:700;color:var(--tx);margin-bottom:4px'>Describe the role</div>"
  "<div style='font-size:12px;color:var(--tx3);margin-bottom:12px'>Paste a job description or describe the role. Scout finds candidates on LinkedIn, scores their fit, and writes personalised InMail drafts.</div>"
  "<textarea id='sourcer-jd' placeholder='Senior Product Designer, 5yr, B2B SaaS, Figma, remote OK' style='width:100%;min-height:110px;background:var(--sur2);border:1px solid var(--bor2);color:var(--tx);font-family:Outfit,sans-serif;font-size:13px;padding:12px;border-radius:8px;resize:vertical;outline:none;box-sizing:border-box'></textarea>"
  "<div style='display:flex;gap:10px;margin-top:10px;align-items:center'>"
  "<button onclick='sourcerRun()' style='background:var(--pip);color:#fff;border:none;font-family:Outfit,sans-serif;font-size:13px;font-weight:700;padding:10px 24px;border-radius:8px;cursor:pointer'>Find Candidates</button>"
  "<span id='sourcer-status' style='font-size:12px;color:var(--tx3)'></span>"
  "</div>"
  "</div>"
  "<div id='sourcer-search-section' style='display:none;background:var(--sur);border:1px solid var(--bor);border-radius:var(--r);padding:20px;margin-bottom:14px'>"
  "<div style='font-size:14px;font-weight:700;color:var(--tx);margin-bottom:4px'>LinkedIn X-Ray Searches</div>"
  "<div style='font-size:12px;color:var(--tx3);margin-bottom:14px'>Copy each into Google to find LinkedIn profiles. Paste candidates below to score them.</div>"
  "<div id='sourcer-searches'></div>"
  "</div>"
  "<div id='sourcer-candidates-section' style='display:none;margin-top:14px'></div>"
  "<div id='sourcer-results'></div>"
  "</div>"
  "</div>"
  "<div id='ph-history-wrap' style='display:none;margin-top:8px'>"
  "<div style='font-size:13px;font-weight:700;color:var(--tx);margin-bottom:10px'>Search History</div>"
  "<div id='ph-history-list'></div>"
  "</div>"
  "</div>"
  "<div class='modal-overlay' id='profile-modal'><div class='modal' style='max-width:600px'><div class='modal-title'>Edit Profile</div><div style='font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.14em;margin-bottom:12px;margin-top:4px'>Identity</div><div style='display:grid;grid-template-columns:1fr 1fr;gap:10px'><div class='modal-field'><label class='modal-label'>Full Name</label><input class='modal-input' id='pm-name' placeholder='e.g. Jane Smith' type='text'></div><div class='modal-field'><label class='modal-label'>Email</label><input class='modal-input' id='pm-email' placeholder='you@yoursite.com' type='text'></div><div class='modal-field'><label class='modal-label'>Agency / Company</label><input class='modal-input' id='pm-agency' placeholder='Scout' type='text'></div><div class='modal-field'><label class='modal-label'>Your Role</label><input class='modal-input' id='pm-role' placeholder='Fractional CMO' type='text'></div><div class='modal-field'><label class='modal-label'>Location</label><input class='modal-input' id='pm-location' placeholder='New York, USA' type='text'></div><div class='modal-field'><label class='modal-label'>Years Experience</label><input class='modal-input' id='pm-experience' placeholder='10+' type='text'></div></div><div class='modal-field' style='margin-top:4px'><label class='modal-label'>Tagline</label><input class='modal-input' id='pm-tagline' placeholder='Fractional CMO for AI-first startups'></div><div class='modal-field'><label class='modal-label'>Bio</label><textarea class='modal-input modal-textarea' id='pm-bio' placeholder='Tell prospects who you are...'></textarea></div><div style='font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.14em;margin-bottom:12px;margin-top:16px'>Ideal Client</div><div style='display:grid;grid-template-columns:1fr 1fr;gap:10px'><div class='modal-field'><label class='modal-label'>Target Industries</label><input class='modal-input' id='pm-industries' placeholder='AI, SaaS, Fintech' type='text'></div><div class='modal-field'><label class='modal-label'>Ideal Funding Stage</label><input class='modal-input' id='pm-funding_stage' placeholder='Seed – Series B' type='text'></div><div class='modal-field'><label class='modal-label'>Ideal Company Size</label><input class='modal-input' id='pm-company_size' placeholder='10–100 employees' type='text'></div><div class='modal-field'><label class='modal-label'>Deal Size / Rate</label><input class='modal-input' id='pm-deal_size' placeholder='$5k–$15k/mo' type='text'></div><div class='modal-field'><label class='modal-label'>Typical Engagement</label><input class='modal-input' id='pm-client_size' placeholder='3–6 month retainers' type='text'></div><div class='modal-field'><label class='modal-label'>Availability</label><input class='modal-input' id='pm-availability' placeholder='2 spots open Q2 2026' type='text'></div></div><div style='font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.14em;margin-bottom:12px;margin-top:16px'>Links</div><div style='display:grid;grid-template-columns:1fr 1fr;gap:10px'><div class='modal-field'><label class='modal-label'>LinkedIn</label><input class='modal-input' id='pm-linkedin' placeholder='https://linkedin.com/in/you' type='text'></div><div class='modal-field'><label class='modal-label'>Twitter / X</label><input class='modal-input' id='pm-twitter' placeholder='https://x.com/yourhandle' type='text'></div><div class='modal-field'><label class='modal-label'>Website</label><input class='modal-input' id='pm-website' placeholder='https://yoursite.com' type='text'></div><div class='modal-field'><label class='modal-label'>Book a Call</label><input class='modal-input' id='pm-calendly' placeholder='https://calendly.com/you' type='text'></div></div><div style='font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.14em;margin-bottom:12px;margin-top:16px'>Settings</div><div class='modal-field'><label class='modal-label'>Min GTM Score to show (0 = show all)</label><input class='modal-input' id='pm-min_score' placeholder='0' type='number' min='0' max='100'></div><div class='modal-actions'><button class='modal-cancel' onclick='closeProfileModal()'>Cancel</button><button class='modal-save' onclick='profileSaveInfo()'>Save changes</button></div></div></div>"
  "<div class='modal-overlay' id='pricing-overlay'><div class='pricing-modal'><div class='modal-title'>Upgrade Scout</div><div id='pricing-msg' style='font-size:13px;color:var(--tx3);margin-bottom:20px;text-align:center'></div><div class='pricing-grid' style='display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px'><div style='background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r);padding:20px;text-align:center'><div style='font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:var(--tx3);margin-bottom:8px'>Starter</div><div style='font-size:28px;font-weight:800;color:var(--tx);font-family:JetBrains Mono,monospace;line-height:1'>$19<span style='font-size:13px;color:var(--tx3);font-family:Outfit,sans-serif'>/mo</span></div><div style='font-size:12px;color:var(--tx3);margin:8px 0 16px'>50 researches/mo</div><button onclick='selectTier(\"starter\")' style='width:100%;background:none;border:1px solid var(--bor2);color:var(--tx2);font-size:12px;font-weight:700;padding:9px;border-radius:6px;cursor:pointer;font-family:Outfit,sans-serif'>Choose Starter</button></div><div style='background:var(--sur2);border:2px solid var(--pip);border-radius:var(--r);padding:20px;text-align:center;position:relative'><div style='position:absolute;top:-10px;left:50%;transform:translateX(-50%);background:var(--pip);color:#fff;font-size:9px;font-weight:700;padding:2px 12px;border-radius:4px;white-space:nowrap;text-transform:uppercase;letter-spacing:.08em'>Popular</div><div style='font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:var(--tx3);margin-bottom:8px'>Pro</div><div style='font-size:28px;font-weight:800;color:var(--tx);font-family:JetBrains Mono,monospace;line-height:1'>$49<span style='font-size:13px;color:var(--tx3);font-family:Outfit,sans-serif'>/mo</span></div><div style='font-size:12px;color:var(--tx3);margin:8px 0 16px'>300 researches/mo</div><button onclick='selectTier(\"pro\")' style='width:100%;background:var(--pip);color:#fff;border:none;font-size:12px;font-weight:700;padding:9px;border-radius:6px;cursor:pointer;font-family:Outfit,sans-serif'>Choose Pro</button></div><div style='background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r);padding:20px;text-align:center'><div style='font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:var(--tx3);margin-bottom:8px'>Agency</div><div style='font-size:28px;font-weight:800;color:var(--tx);font-family:JetBrains Mono,monospace;line-height:1'>$179<span style='font-size:13px;color:var(--tx3);font-family:Outfit,sans-serif'>/mo</span></div><div style='font-size:12px;color:var(--tx3);margin:8px 0 16px'>750 researches/mo</div><button onclick='selectTier(\"agency\")' style='width:100%;background:none;border:1px solid var(--bor2);color:var(--tx2);font-size:12px;font-weight:700;padding:9px;border-radius:6px;cursor:pointer;font-family:Outfit,sans-serif'>Choose Agency</button></div></div><div style='text-align:center'><button onclick='selectTier(\"free\")' style='background:none;border:none;color:var(--tx3);font-size:12px;cursor:pointer;font-family:Outfit,sans-serif;text-decoration:underline'>Stay on free plan (5 researches/mo)</button></div><div style='text-align:center;margin-top:12px'><button onclick='closePricing()' style='background:none;border:none;color:var(--tx3);font-size:12px;cursor:pointer;font-family:Outfit,sans-serif'>Maybe later</button></div></div></div>"
  "<div class='modal-overlay' id='case-modal'><div class='modal' style='max-width:500px'><div class='modal-title'>Case Study</div><input type='hidden' id='cm-idx'><div class='modal-field'><label class='modal-label'>Client</label><input class='modal-input' id='cm-client' placeholder='Acme Corp'></div><div class='modal-field'><label class='modal-label'>Title</label><input class='modal-input' id='cm-title' placeholder='GTM strategy for Series A launch'></div><div class='modal-field'><label class='modal-label'>Result</label><input class='modal-input' id='cm-result' placeholder='3x pipeline in 90 days'></div><div class='modal-field'><label class='modal-label'>Metrics (comma separated)</label><input class='modal-input' id='cm-metrics' placeholder='3x pipeline, $2M ARR, 6 months'></div><div class='modal-actions'><button class='modal-cancel' onclick='closeCaseModal()'>Cancel</button><button class='modal-cancel' onclick='profileDeleteCase()' style='color:var(--red);border-color:rgba(239,68,68,0.2)'>Delete</button><button class='modal-save' onclick='profileSaveCase()'>Save</button></div></div></div>"
"<script>" + JS + "</script>\n"
  "</body>\n</html>\n")

LANDING_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scout - Find your next client</title>
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
.pfl li::before{content:'-';color:var(--pip2);font-weight:700;flex-shrink:0}
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
  nav{padding:0 20px;overflow:visible}
  .ncta{touch-action:manipulation;-webkit-tap-highlight-color:transparent;min-height:44px;display:flex;align-items:center}
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
    <a href="#features" class="nlink" id="t-nav1">Features</a>
    <a href="#pricing" class="nlink" id="t-nav2">Pricing</a>
    <a href="#waitlist" class="nlink" id="t-nav3">Early access</a>
  </div>
  <div style="display:flex;gap:8px;align-items:center;margin-left:24px">
    <a href="/app" id="nav-cta" class="ncta">Start free</a>
<button id="lang-toggle" onclick="toggleLang()" style="background:none;border:1px solid rgba(45,157,232,0.3);color:var(--tx2);font-family:Outfit,sans-serif;font-size:12px;font-weight:700;padding:6px 14px;border-radius:6px;cursor:pointer;margin-left:8px">ES</button>
<script>try{
  var _t=localStorage.getItem('sb_token');
  var _u=localStorage.getItem('sb_user');
  var _nc=document.getElementById('nav-cta');
  var _c1=document.getElementById('t-cta1');
  if(_t&&_u){
    if(_nc){_nc.textContent='Dashboard';_nc.style.background='var(--pip,#2d9de8)';}
    if(_c1){_c1.textContent='Go to Dashboard';}
  }
}catch(e){}</script>
  </div></nav>

<section class="hero">
  <div>
    <div class="eyebrow"><div class="ndot" style="width:6px;height:6px;flex-shrink:0"></div><span id="t-eyebrow">AI client acquisition</span></div>
    <h1 id="t-h1">Your next<br><em>best lead</em></h1>
    <p class="sub" id="t-sub">Turn any company name into a qualified lead. Scout researches, scores, and writes your pitch opener in 8 seconds - so you spend time closing, not researching.</p>
    <div class="actions">
      <a href="/app" class="btnp" id="t-cta1">Discover Scout</a>
      <a href="https://calendar.app.google/xFhe41V2HMXNBzw29" target="_blank" class="btng" id="t-cta2">Book a call</a>
    </div>
    <div class="stats">
      <div class="stat"><div class="stn">8<span>s</span></div><div class="stl" id="t-stat1">To full GTM profile</div></div>
      <div class="stat"><div class="stn">0<span>–100</span></div><div class="stl" id="t-stat2">GTM Score</div></div>
      <div class="stat"><div class="stn">3<span> tiers</span></div><div class="stl" id="t-stat3">From free</div></div>
    </div>
  </div>
  <div>
    <div class="dw">
      <div class="dw-bar">
        <div class="dw-dot" style="background:#ff5f57"></div>
        <div class="dw-dot" style="background:#febc2e"></div>
        <div class="dw-dot" style="background:#28c840"></div>
        <span class="dw-lbl">scout - research</span>
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
  <p id="t-builtfor" style="font-size:12px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--tx3);margin-bottom:24px">Built for</p>
  <div class="for-pills">
    <div class="for-pill">Fractional CMOs</div>
    <div class="for-pill">Marketing Agencies</div>
    <div class="for-pill">Growth Consultants</div>
    <div class="for-pill">B2B Sales Teams</div>
    <div class="for-pill">Freelance Marketers</div>
  </div>
</section>

<section class="sec" id="features">
  <div class="slbl" id="t-feat-eyebrow">What Scout does</div>
  <h2 id="t-feat-h2">Stop researching.<br>Start closing.</h2>
  <p class="ssub" id="t-feat-sub">Scout does the research, scores the opportunity, and writes the opener. You just decide whether to send it.</p>
  <div class="fg">
    <div class="fc"><div class="fn">01</div><div class="ft" id="t-ft1">Know before you pitch</div><p class="fd" id="t-fd1">0–100 score based on funding stage, team gaps, hiring signals, and growth velocity. Filter time-wasters before you write a word.</p></div>
    <div class="fc"><div class="fn">02</div><div class="ft" id="t-ft2">Write itself</div><p class="fd" id="t-fd2">Scout reads the room - funding news, team gaps, recent hires - and writes a pitch opener that references something real.</p></div>
    <div class="fc"><div class="fn">03</div><div class="ft" id="t-ft3">Pipeline on autopilot</div><p class="fd" id="t-fd3">Scout scans funding databases daily. Hot companies land in your Inbox automatically - just approve or dismiss.</p></div>
    <div class="fc"><div class="fn">04</div><div class="ft" id="t-ft4">Never lose track</div><p class="fd" id="t-fd4">Kanban from Not Contacted to Closed. Every prospect in one place, every deal visible at a glance.</p></div>
    <div class="fc"><div class="fn">05</div><div class="ft" id="t-ft5">Two businesses, one tool</div><p class="fd" id="t-fd5">Pip Hunt finds companies hiring fractional CMOs and marketing leaders right now. Built right into Scout.</p></div>
    <div class="fc"><div class="fn">06</div><div class="ft" id="t-ft6">Your digital pitch deck</div><p class="fd" id="t-fd6">Build a profile with your services and case studies. Share a link with prospects before you get on a call.</p></div>
  </div>
</section>


<div class="ps" id="pricing">
  <div style="text-align:center;margin-bottom:40px">
    <div class="slbl" id="t-price-eyebrow" style="text-align:center">Pricing</div>
    <h2 id="t-price-h2" style="font-size:48px;max-width:100%;text-align:center;margin:0 auto 12px">Pay for what you use</h2>
    <p style="font-size:16px;color:var(--tx2)">Start free. Upgrade when Scout starts paying for itself.</p>
  </div>

  <!-- Free tier - full width banner above paid plans -->
  <div style="background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r);padding:24px 32px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:20px;margin-bottom:16px">
    <div>
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
        <span style="font-size:20px;font-weight:800;color:var(--tx);font-family:'JetBrains Mono',monospace">Free</span>
        <span style="font-size:28px;font-weight:800;color:var(--tx);font-family:'JetBrains Mono',monospace">$0</span>
        <span style="font-size:13px;color:var(--tx3)">forever</span>
      </div>
      <div style="display:flex;gap:24px;flex-wrap:wrap">
        <span style="font-size:13px;color:var(--tx2)">&#10003; 5 researches/month</span>
        <span style="font-size:13px;color:var(--tx2)">&#10003; 2 lead fetches</span>
        <span style="font-size:13px;color:var(--tx2)">&#10003; Dashboard &amp; Pipeline</span>
        <span style="font-size:13px;color:var(--tx2)">&#10003; 5 Pip Hunt searches</span>
      </div>
    </div>
    <button class="pb2 out" onclick="location.href='/app'" style="white-space:nowrap">Start for free</button>
  </div>

  <!-- Paid plans - 3 columns -->
  <div class="pg">
    <div class="prc">
      <div class="pn">Starter</div>
      <div class="pp">$19<span class="pper">/mo</span></div>
      <div class="pd">For consultants testing the waters.</div>
      <button class="pb2 out" onclick="location.href='https://buy.stripe.com/8x28wPfrA9WughedmqbjW05'">Get Starter</button>
      <ul class="pfl">
        <li>50 researches/month</li>
        <li>5 lead fetches</li>
        <li>Dashboard &amp; Pipeline</li>
        <li>20 Pip Hunt searches</li>
      </ul>
    </div>
    <div class="prc hot">
      <div class="pbdg">Most popular</div>
      <div class="pn">Pro</div>
      <div class="pp">$49<span class="pper">/mo</span></div>
      <div class="pd">For active prospectors closing deals.</div>
      <button class="pb2" onclick="location.href='https://buy.stripe.com/00wdR90wGc4Cd52gyCbjW01'">Get Pro</button>
      <ul class="pfl">
        <li>300 researches/month</li>
        <li>30 lead fetches/month</li>
        <li>Pip Hunt - jobs &amp; candidate sourcing</li>
        <li>CSV export</li>
        <li>Priority support</li>
      </ul>
    </div>
    <div class="prc">
      <div class="pn">Agency</div>
      <div class="pp">$179<span class="pper">/mo</span></div>
      <div class="pd">For teams running multiple client pipelines.</div>
      <button class="pb2" onclick="location.href='https://buy.stripe.com/8x2dR993c3y6aWU0zEbjW00'">Get Agency</button>
      <ul class="pfl">
        <li>750 researches/month</li>
        <li>5 team members</li>
        <li>100 lead fetches</li>
        <li>Custom proposal generator</li>
        <li>Dedicated support</li>
      </ul>
    </div>
  </div>

  <!-- Top-up credits -->
  <div style="margin-top:16px;background:var(--sur2);border:1px solid var(--bor);border-radius:var(--r);padding:24px 32px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:20px">
    <div>
      <div style="font-size:13px;font-weight:600;color:var(--tx);margin-bottom:4px">Need more credits?</div>
      <div style="font-size:12px;color:var(--tx3)">Top up without a subscription. Credits never expire.</div>
    </div>
    <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
      <a href="https://buy.stripe.com/3cI5kDfrA9WufdabeibjW02" target="_blank" style="display:inline-flex;flex-direction:column;align-items:center;background:var(--sur);border:1px solid var(--bor2);border-radius:var(--r);padding:14px 24px;text-decoration:none;cursor:pointer">
        <span style="font-size:18px;font-weight:700;color:var(--tx);font-family:'JetBrains Mono',monospace">$9</span>
        <span style="font-size:11px;color:var(--tx2);margin-top:2px;font-weight:600">20 credits</span>
        <span style="font-size:10px;color:var(--tx3);margin-top:1px">$0.45 each</span>
      </a>
      <a href="https://buy.stripe.com/5kQ3cvbbk0lUc0Y4PUbjW03" target="_blank" style="display:inline-flex;flex-direction:column;align-items:center;background:var(--sur);border:1px solid var(--pip-bor,rgba(45,157,232,0.22));border-radius:var(--r);padding:14px 24px;text-decoration:none;position:relative">
        <span style="position:absolute;top:-9px;left:50%;transform:translateX(-50%);background:var(--pip);color:#fff;font-size:8px;font-weight:700;padding:2px 10px;border-radius:4px;text-transform:uppercase;letter-spacing:.08em;white-space:nowrap">Best value</span>
        <span style="font-size:18px;font-weight:700;color:var(--tx);font-family:'JetBrains Mono',monospace">$19</span>
        <span style="font-size:11px;color:var(--tx2);margin-top:2px;font-weight:600">50 credits</span>
        <span style="font-size:10px;color:var(--tx3);margin-top:1px">$0.38 each</span>
      </a>
    </div>
  </div>
</div>


<div style="height:80px"></div>
<div class="wl" id="waitlist">
  <div class="wl-card">
    <div>
      <div class="slbl" id="t-wl-eyebrow">Early access</div>
      <h2 id="t-wl-h2" style="font-size:40px;max-width:100%;margin-bottom:12px">Join the waitlist</h2>
      <p id="t-wl-sub" style="font-size:15px;color:var(--tx2);line-height:1.7">Be first to know when new features drop. No spam - just Scout updates and GTM tips from Pip.</p>
    </div>
    <div>
      <div class="wl-row">
        <input type="email" id="wl-email" class="wl-input" placeholder="you@agency.com">
        <button class="wl-btn" id="t-wl-btn" onclick="joinWaitlist()">Join waitlist</button>
      </div>
      <div id="wl-msg" style="font-size:12px;color:var(--pip2);min-height:18px;font-family:'Outfit',sans-serif"></div>
      <p id="t-wl-note" style="font-size:11px;color:var(--tx3);margin-top:10px">Already 140+ fractional CMOs and agencies signed up.</p>
    </div>
  </div>
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
   sigs:['Recently funded - $70M Series B','No CMO listed on LinkedIn','3 open marketing roles','Has PR agency, no growth lead'],
   dots:['g','g','g','a'],
   p:"Saw the Series B - congrats. Most companies at your stage skip the CMO hire until C, but the pipeline pressure is real now. I’ve helped 3 similar healthcare SaaS teams bridge that gap..."},
  {n:'Fathom Video',m:'Series A · AI Productivity · New York',s:79,
   sigs:['Raised $46M 8 weeks ago','Marketing team of 2','Actively hiring demand gen','No head of growth'],
   dots:['g','g','g','a'],
   p:"Noticed Fathom just closed the Series A - impressive traction. With a 2-person marketing team and demand gen role open, the timing for fractional support is usually right about now..."},
  {n:'Cohere',m:'Series C · Enterprise AI · Toronto',s:61,
   sigs:['$270M raised, 18 months ago','CMO hired 6 months back','Growing marketing team','Strong content presence'],
   dots:['a','a','g','g'],
   p:"Cohere’s been building out the marketing org since the Series C - strong moves. If there’s a gap in the enterprise GTM motion, happy to share what’s worked for similar API-first companies..."}
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

<script>
var LANG='en';
var T={
  en:{
    eyebrow:'AI client acquisition',h1:'Your next<br><em>best lead</em>',
    sub:'Turn any company name into a qualified lead. Scout researches, scores, and writes your pitch opener in 8 seconds - so you spend time closing, not researching.',
    cta1:'Discover Scout',cta2:'Book a call',
    stat1:'To full GTM profile',stat2:'GTM Score',stat3:'From free',
    'feat-eyebrow':'What Scout does','feat-h2':'Stop researching.<br>Start closing.',
    'feat-sub':'Scout does the research, scores the opportunity, and writes the opener. You just decide whether to send it.',
    ft1:'Know before you pitch',fd1:'0–100 score based on funding stage, team gaps, hiring signals, and growth velocity. Filter time-wasters before you write a word.',
    ft2:'Write itself',fd2:'Scout reads the room - funding news, team gaps, recent hires - and writes a pitch opener that references something real.',
    ft3:'Pipeline on autopilot',fd3:'Scout scans funding databases daily. Hot companies land in your Inbox automatically - just approve or dismiss.',
    ft4:'Never lose track',fd4:'Kanban from Not Contacted to Closed. Every prospect in one place, every deal visible at a glance.',
    ft5:'Two businesses, one tool',fd5:'Pip Hunt finds companies hiring fractional CMOs and marketing leaders right now. Built right into Scout.',
    ft6:'Your digital pitch deck',fd6:'Build a profile with your services and case studies. Share a link with prospects before you get on a call.',
    'price-eyebrow':'Pricing','price-h2':'Pay for what you use',
    'wl-eyebrow':'Early access','wl-h2':'Join the waitlist',
    'wl-sub':'Be first to know when new features drop. No spam - just Scout updates and GTM tips from Pip.',
    'wl-btn':'Join waitlist','wl-note':'Already 140+ fractional CMOs and agencies signed up.',
    nav1:'Features',nav2:'Pricing',nav3:'Early access',
    builtfor:'Built for',lang:'ES'
  },
  es:{
    eyebrow:'Captación de clientes con IA',h1:'Tu próximo<br><em>mejor cliente</em>',
    sub:'Convierte cualquier empresa en un lead cualificado. Scout investiga, puntaúa y escribe tu opener en 8 segundos — para que cierres, no investigues.',
    cta1:'Descubrir Scout',cta2:'Reservar llamada',
    stat1:'Para perfil GTM completo',stat2:'Puntuación GTM',stat3:'Desde gratis',
    'feat-eyebrow':'Qué hace Scout','feat-h2':'Deja de investigar.<br>Empieza a cerrar.',
    'feat-sub':'Scout hace la investigación, puntaúa la oportunidad y escribe el opener. Tú solo decides si enviarlo.',
    ft1:'Sabe antes de presentarte',fd1:'Puntuación 0–100 basada en fase de financiación, gaps del equipo y señales de crecimiento.',
    ft2:'Se escribe solo',fd2:'Scout lee el contexto — noticias de financiación, contrataciones recientes — y escribe un opener que referencia algo real.',
    ft3:'Pipeline en piloto automático',fd3:'Scout escanea bases de datos diariamente. Las empresas calientes llegan a tu bandeja automáticamente.',
    ft4:'Nunca pierdas el hilo',fd4:'Kanban de No Contactado a Cerrado. Cada prospecto en un solo lugar.',
    ft5:'Dos negocios, una herramienta',fd5:'Pip Hunt encuentra empresas que buscan CMOs fraccionales ahora mismo.',
    ft6:'Tu dossier digital',fd6:'Crea un perfil con tus servicios y casos de éxito. Compártelo antes de una llamada.',
    'price-eyebrow':'Precios','price-h2':'Paga por lo que usas',
    'wl-eyebrow':'Acceso anticipado','wl-h2':'Uúnete a la lista de espera',
    'wl-sub':'Sé el primero en conocer las nuevas funciones. Sin spam.',
    'wl-btn':'Unirse a la lista','wl-note':'Ya más de 140 CMOs fraccionales y agencias apuntados.',
    nav1:'Funciones',nav2:'Precios',nav3:'Acceso anticipado',
    builtfor:'Para',lang:'EN'
  }
};
function toggleLang(){LANG=LANG==='en'?'es':'en';applyLang();}
function applyLang(){
  var t=T[LANG];
  var ids=['eyebrow','h1','sub','cta1','cta2','stat1','stat2','stat3',
    'feat-eyebrow','feat-h2','feat-sub',
    'ft1','fd1','ft2','fd2','ft3','fd3','ft4','fd4','ft5','fd5','ft6','fd6',
    'price-eyebrow','price-h2','wl-eyebrow','wl-h2','wl-sub','wl-btn','wl-note',
    'nav1','nav2','nav3','builtfor'];
  ids.forEach(function(id){
    var el=document.getElementById('t-'+id);
    if(!el)return;
    var v=t[id];
    if(!v)return;
    if(v.indexOf('<')>=0)el.innerHTML=v;
    else el.textContent=v;
  });
  var lb=document.getElementById('lang-toggle');if(lb)lb.textContent=t.lang;
  document.documentElement.lang=LANG;
  document.title=LANG==='es'?'Scout - Encuentra tu próximo cliente':'Scout - Find your next client';
}
</script>
</body>
</html>'''

LEGAL_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scout - Terms of Service & Privacy Policy</title>
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
<p>Scout is a SaaS platform that provides AI company research, lead scoring, pitch generation, and pipeline management tools for marketing professionals. Scout also includes Pip Hunt, a job intelligence feature that surfaces open marketing and design leadership roles.</p>
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
  <li><strong>Anthropic (Claude API)</strong> - AI research generation. <a href="https://www.anthropic.com/privacy" target="_blank">Privacy policy</a></li>
  <li><strong>Stripe</strong> - Payment processing. <a href="https://stripe.com/privacy" target="_blank">Privacy policy</a></li>
  <li><strong>Railway</strong> - Application hosting. <a href="https://railway.app/legal/privacy" target="_blank">Privacy policy</a></li>
  <li><strong>GitHub</strong> - Data persistence (private Gist). <a href="https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement" target="_blank">Privacy policy</a></li>
  <li><strong>Google Fonts</strong> - Typography. <a href="https://policies.google.com/privacy" target="_blank">Privacy policy</a></li>
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
        if self.path == '/manifest.json':
            import re as _re
            b64_match = _re.search(r'data:image/png;base64,([A-Za-z0-9+/=]{100,})', LANDING_HTML)
            pip_b64 = b64_match.group(1) if b64_match else ''
            manifest = {
                "name": "Scout",
                "short_name": "Scout",
                "description": "AI lead generation for marketing pros",
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
        if self.path.startswith('/proposal/'):
            encoded = self.path[len('/proposal/'):]
            out = self.build_proposal_page(encoded).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(out)))
            self.end_headers()
            self.wfile.write(out)
            return
        if self.path.startswith('/p/'):
            encoded = self.path[3:]
            wl_html = self.build_pitch_page(encoded)
            self.send_response(200)
            self.send_header('Content-Type','text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(wl_html.encode('utf-8'))
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
        if self.path.startswith('/db'):
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(self.path).query)
            user_key = qs.get('user', [None])[0]
            data = json.dumps(load_db(user_key)).encode('utf-8')
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


    def build_proposal_page(self, encoded):
        import base64, json as _json, html as _html
        try:
            data = _json.loads(base64.b64decode(encoded + '==').decode('utf-8'))
        except Exception:
            return '<html><body style="font-family:sans-serif;padding:40px">Invalid proposal link</body></html>'

        c = data.get('consultant', {})
        lead = data.get('lead', {})
        services = data.get('services', [])
        cases = data.get('cases', [])

        def esc(v):
            return _html.escape(str(v)) if v else ''

        color = esc(c.get('color', '#2d9de8'))
        name = esc(c.get('name', ''))
        agency = esc(c.get('agency', ''))
        role = esc(c.get('role', 'Fractional CMO'))
        tagline = esc(c.get('tagline', ''))
        bio = esc(c.get('bio', ''))
        email = esc(c.get('email', ''))
        phone = esc(c.get('phone', ''))
        linkedin = esc(c.get('linkedin', ''))
        website = esc(c.get('website', ''))
        calendly = esc(c.get('calendly', ''))
        deal_size = esc(c.get('deal_size', ''))
        client_size = esc(c.get('client_size', ''))
        availability = esc(c.get('availability', ''))
        logo = c.get('logo', '')

        company = esc(lead.get('company', ''))
        prospect_logo_raw = lead.get('prospect_logo', '')
        sector = esc(lead.get('sector', ''))
        stage = esc(lead.get('stage', ''))
        hq = esc(lead.get('hq', ''))
        funding = esc(lead.get('funding_amount', ''))
        score = int(lead.get('score', 0))
        label = esc(lead.get('label', ''))
        why_fit = esc(lead.get('why_fit', ''))
        pitch = esc(lead.get('pitch_opener', ''))
        signals = lead.get('gtm_signals', {})

        score_color = '#5bc4f5' if score >= 75 else '#f59e0b' if score >= 50 else '#6b7280'
        meta_parts = [x for x in [sector, stage, hq, funding] if x]
        meta = ' &middot; '.join(meta_parts)
        logo_html = '<img src="' + logo + '" style="height:48px;object-fit:contain;margin-bottom:8px;display:block"/>' if logo else ''

        signal_items = []
        if signals.get('recently_funded'): signal_items.append('Recently funded')
        if signals.get('no_cmo'): signal_items.append('No CMO on team')
        if signals.get('marketing_gap_visible'): signal_items.append('Marketing gap visible')
        signals_html = ''
        for s in signal_items:
            signals_html += '<div style="display:flex;align-items:center;gap:10px;padding:10px 0;border-bottom:1px solid #f1f5f9"><div style="width:8px;height:8px;border-radius:50%;background:' + color + ';flex-shrink:0"></div><span style="font-size:14px;color:#334155">' + s + '</span></div>'

        services_html = ''
        for svc in services:
            sn = esc(svc.get('name', ''))
            sd = esc(svc.get('desc', ''))
            sp = esc(svc.get('price', ''))
            if not sn: continue
            price_tag = '<div style="font-size:12px;font-weight:700;color:' + color + ';white-space:nowrap;margin-left:12px">' + sp + '</div>' if sp else ''
            desc_tag = '<div style="font-size:13px;color:#64748b;line-height:1.6;margin-top:4px">' + sd + '</div>' if sd else ''
            services_html += '<div style="background:#f8fafc;border-radius:10px;padding:20px 22px;border:1px solid #e2e8f0"><div style="display:flex;justify-content:space-between;align-items:flex-start"><div style="font-size:15px;font-weight:700;color:#0f1923">' + sn + '</div>' + price_tag + '</div>' + desc_tag + '</div>'

        cases_html = ''
        for cs in cases:
            cl = esc(cs.get('client', ''))
            ct = esc(cs.get('title', ''))
            cr = esc(cs.get('result', ''))
            cm = esc(cs.get('metrics', ''))
            if not cl: continue
            metrics_tags = ''.join('<span style="background:' + color + '20;color:' + color + ';font-size:11px;font-weight:700;padding:3px 10px;border-radius:999px;border:1px solid ' + color + '40">' + m.strip() + '</span>' for m in cm.split(',') if m.strip()) if cm else ''
            result_tag = '<div style="font-size:13px;color:#10b981;font-weight:600;margin-bottom:8px">' + cr + '</div>' if cr else ''
            metrics_div = '<div style="display:flex;gap:6px;flex-wrap:wrap">' + metrics_tags + '</div>' if metrics_tags else ''
            cases_html += '<div style="background:#f8fafc;border-radius:10px;padding:20px 22px;border:1px solid #e2e8f0"><div style="font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#94a3b8;margin-bottom:6px">' + cl + '</div><div style="font-size:15px;font-weight:700;color:#0f1923;margin-bottom:6px">' + ct + '</div>' + result_tag + metrics_div + '</div>'

        contact_items = []
        if email: contact_items.append('<a href="mailto:' + email + '" style="color:' + color + ';text-decoration:none">' + email + '</a>')
        if phone: contact_items.append('<a href="tel:' + phone + '" style="color:' + color + ';text-decoration:none">' + phone + '</a>')
        if linkedin: contact_items.append('<a href="' + linkedin + '" target="_blank" style="color:' + color + ';text-decoration:none">LinkedIn</a>')
        if website: contact_items.append('<a href="' + website + '" target="_blank" style="color:' + color + ';text-decoration:none">' + website + '</a>')
        if calendly: contact_items.append('<a href="' + calendly + '" target="_blank" style="background:' + color + ';color:#fff;padding:10px 24px;border-radius:6px;text-decoration:none;font-weight:700;display:inline-block;margin-top:6px">Book a call &rarr;</a>')
        contact_html = ''.join('<div style="margin-bottom:8px">' + item + '</div>' for item in contact_items)

        terms_html = ''
        if deal_size or client_size or availability:
            terms_html = '<div style="display:flex;gap:24px;flex-wrap:wrap;margin-top:4px">'
            if deal_size: terms_html += '<div><div style="font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#94a3b8;margin-bottom:2px">Investment</div><div style="font-size:14px;color:#334155;font-weight:600">' + deal_size + '</div></div>'
            if client_size: terms_html += '<div><div style="font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#94a3b8;margin-bottom:2px">Engagement</div><div style="font-size:14px;color:#334155;font-weight:600">' + client_size + '</div></div>'
            if availability: terms_html += '<div><div style="font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#94a3b8;margin-bottom:2px">Availability</div><div style="font-size:14px;color:#334155;font-weight:600">' + availability + '</div></div>'
            terms_html += '</div>'

        agency_line = (' &middot; ' + agency) if agency else ''
        tagline_line = '<div style="font-size:13px;color:rgba(255,255,255,.65);margin-top:4px">' + tagline + '</div>' if tagline else ''

        sections = []
        # Why now
        if why_fit or signals_html:
            s = '<div><div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:#94a3b8;margin-bottom:12px">Why ' + company + ' needs this now</div>'
            if why_fit: s += '<div style="background:#f8fafc;border-radius:10px;padding:20px;border-left:3px solid ' + color + ';font-size:14px;color:#334155;line-height:1.75">' + why_fit + '</div>'
            if signals_html: s += '<div style="margin-top:12px">' + signals_html + '</div>'
            s += '</div>'
            sections.append(s)
        # Pitch
        if pitch:
            sections.append('<div><div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:#94a3b8;margin-bottom:12px">How I would approach this</div><div style="background:#f8fafc;border-radius:10px;padding:20px;font-size:14px;color:#334155;line-height:1.75;font-style:italic">' + pitch + '</div></div>')
        # About
        if bio:
            sections.append('<div><div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:#94a3b8;margin-bottom:12px">About me</div><div style="font-size:14px;color:#334155;line-height:1.75">' + bio + '</div></div>')
        # Services
        if services_html:
            sections.append('<div><div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:#94a3b8;margin-bottom:14px">What I offer</div><div style="display:flex;flex-direction:column;gap:10px">' + services_html + '</div></div>')
        # Cases
        if cases_html:
            sections.append('<div><div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:#94a3b8;margin-bottom:14px">Proof of work</div><div style="display:flex;flex-direction:column;gap:10px">' + cases_html + '</div></div>')
        # Terms
        if terms_html:
            sections.append('<div><div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:#94a3b8;margin-bottom:12px">Engagement terms</div>' + terms_html + '</div>')
        # Contact
        if contact_html:
            sections.append('<div style="background:' + color + '12;border:1px solid ' + color + '30;border-radius:12px;padding:28px 32px"><div style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:#94a3b8;margin-bottom:14px">Get in touch</div><div style="font-size:14px;line-height:1.8">' + contact_html + '</div></div>')

        body_html = ''.join('<div style="margin-bottom:32px">' + s + '</div>' for s in sections)

        prospect_logo = lead.get('prospect_logo', '')
        prospect_logo_html = '<img src="' + prospect_logo + '" style="height:56px;object-fit:contain;display:block"/>' if prospect_logo else ''

        # ── Title page (landscape, full-bleed dark) ─────────────────────
        title_page = (
            '<div class="page title-page" style="background:linear-gradient(135deg,#020408 0%,#0a1220 60%,#0f1a2e 100%);min-height:100vh;display:flex;flex-direction:column;position:relative;overflow:hidden;page-break-after:always">'
            # Background orb
            '<div style="position:absolute;top:-15%;right:-10%;width:55%;height:75%;border-radius:50%;background:radial-gradient(ellipse,' + color + '18 0%,transparent 65%);pointer-events:none"></div>'
            '<div style="position:absolute;bottom:-20%;left:-10%;width:45%;height:60%;border-radius:50%;background:radial-gradient(ellipse,' + color + '10 0%,transparent 65%);pointer-events:none"></div>'
            # Top bar with logos
            '<div style="display:flex;align-items:center;justify-content:space-between;padding:40px 64px 0;position:relative;z-index:1">'
              + (('<img src="' + logo + '" style="height:44px;object-fit:contain;display:block"/>') if logo else '<div style="font-size:14px;font-weight:800;letter-spacing:.18em;text-transform:uppercase;color:#fff">' + name + '</div>')
              + '<div style="display:flex;align-items:center;gap:12px">'
              + ('<div style="width:1px;height:40px;background:rgba(255,255,255,.15)"></div>' if prospect_logo_html else '')
              + prospect_logo_html
              + '</div>'
            '</div>'
            # Center content
            '<div style="flex:1;display:flex;flex-direction:column;align-items:flex-start;justify-content:center;padding:60px 64px;position:relative;z-index:1">'
              '<div style="font-size:11px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:' + color + ';margin-bottom:20px;display:flex;align-items:center;gap:10px">'
              '<div style="width:28px;height:2px;background:' + color + '"></div>Marketing Proposal</div>'
              '<div style="font-size:72px;font-weight:900;letter-spacing:-.05em;color:#fff;line-height:.92;margin-bottom:28px">' + company + '</div>'
              + ('<div style="font-size:16px;color:rgba(255,255,255,.55);margin-bottom:48px">' + meta + '</div>' if meta else '<div style="margin-bottom:48px"></div>')
              + '<div style="display:flex;align-items:center;gap:16px">'
              '<div style="background:' + color + ';border-radius:6px;padding:6px 16px">'
              '<div style="font-size:13px;font-weight:700;color:#fff;text-transform:uppercase;letter-spacing:.1em">GTM Score</div>'
              '<div style="font-size:40px;font-weight:900;color:#fff;line-height:1;letter-spacing:-.04em">' + str(score) + '</div>'
              '</div>'
              + ('<div style="height:60px;width:1px;background:rgba(255,255,255,.15)"></div><div style="font-size:13px;color:rgba(255,255,255,.5);line-height:1.5"><div style="font-weight:700;color:rgba(255,255,255,.8);font-size:14px">' + label + '</div>' + meta + '</div>' if label else '')
              + '</div>'
            '</div>'
            # Footer bar
            '<div style="display:flex;align-items:center;justify-content:space-between;padding:24px 64px;border-top:1px solid rgba(255,255,255,.08);position:relative;z-index:1">'
            '<div style="font-size:12px;color:rgba(255,255,255,.35)">'
              + name + ((' &middot; ' + agency) if agency else '') + ((' &middot; ' + role) if role else '')
            + '</div>'
            '<div style="font-size:11px;color:rgba(255,255,255,.2)">Prepared with Scout</div>'
            '</div>'
            '</div>'
        )

        # ── Content pages ────────────────────────────────────────────────
        content_page = (
            '<div class="page content-page" style="background:#fff;min-height:100vh;display:flex;flex-direction:column">'
            # Colored top strip
            '<div style="background:' + color + ';height:6px;width:100%"></div>'
            # Header
            '<div style="display:flex;align-items:center;justify-content:space-between;padding:28px 64px 20px;border-bottom:1px solid #f1f5f9">'
              + (('<img src="' + logo + '" style="height:32px;object-fit:contain;display:block"/>') if logo else '<div style="font-size:12px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#0f1923">' + name + '</div>')
              + '<div style="font-size:12px;color:#94a3b8">Proposal for ' + company + '</div>'
            '</div>'
            # Body
            '<div style="flex:1;padding:48px 64px">' + body_html + '</div>'
            # Footer
            '<div style="display:flex;align-items:center;justify-content:space-between;padding:20px 64px;border-top:1px solid #f1f5f9">'
            '<div style="font-size:11px;color:#cbd5e1">' + name + ' &middot; Prepared for ' + company + '</div>'
            '<div style="font-size:11px;color:#cbd5e1">Powered by Scout</div>'
            '</div>'
            '</div>'
        )

        return (
            '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Proposal for ' + company + ' \u00b7 ' + name + '</title>'
            '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&display=swap" rel="stylesheet">'
            '<style>'
            '*{box-sizing:border-box;margin:0;padding:0}'
            'body{background:#020408;font-family:Outfit,sans-serif;color:#1a2332;-webkit-print-color-adjust:exact;print-color-adjust:exact}'
            '.page{break-inside:avoid}'
            '@page{size:A4 landscape;margin:0}'
            '@media print{'
              '.no-print{display:none!important}'
              'body{background:#020408}'
              '.title-page{min-height:100vh!important}'
              '.content-page{background:#fff!important;min-height:100vh!important}'
            '}'
            '.modal-section-title{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.14em;color:#94a3b8;margin-bottom:12px}'
            '</style>'
            '</head><body>'
            '<div class="no-print" style="position:fixed;top:16px;right:16px;z-index:100;display:flex;gap:8px">'
            '<button onclick="window.print()" style="background:' + color + ';color:#fff;border:none;font-family:Outfit,sans-serif;font-size:13px;font-weight:700;padding:10px 22px;border-radius:8px;cursor:pointer;box-shadow:0 2px 12px rgba(0,0,0,.3)">\u2193 Download PDF</button>'
            '</div>'
            + title_page
            + content_page
            + '</body></html>'
        )

    def build_pitch_page(self, encoded):
        import base64, json as _json, html as _html
        try:
            data = _json.loads(base64.b64decode(encoded + '==').decode('utf-8'))
            lead = data.get('lead', {})
            brand = data.get('brand', {})
        except:
            return '<html><body>Invalid link</body></html>'

        color = _html.escape(brand.get('color','#2d9de8'))
        bname = _html.escape(brand.get('name','Scout'))
        btagline = _html.escape(brand.get('tagline',''))
        bcta = _html.escape(brand.get('cta',''))
        logo = brand.get('logo','')

        company = _html.escape(lead.get('company',''))
        sector = _html.escape(lead.get('sector',''))
        stage = _html.escape(lead.get('stage',''))
        hq = _html.escape(lead.get('hq',''))
        funding = _html.escape(lead.get('funding_amount',''))
        score = str(lead.get('gtm_readiness_score',0))
        label = _html.escape(lead.get('gtm_label',''))
        why_fit = _html.escape(lead.get('why_fit',''))
        pitch = _html.escape(lead.get('pitch_opener',''))
        contact_title = _html.escape(lead.get('best_contact_title',''))
        contact_name = _html.escape(lead.get('best_contact_name',''))

        label_color = '#f59e0b' if 'Warm' in label else ('#10b981' if 'Hot' in label else '#6b7280')

        logo_html = f'<img src="{logo}" style="height:40px;object-fit:contain;margin-bottom:8px" />' if logo else ''

        meta_parts = [x for x in [sector, stage, hq, funding] if x]
        meta_str = ' &middot; '.join(meta_parts)

        cta_html = f'<a href="{bcta}" style="display:inline-block;background:{color};color:#fff;font-family:sans-serif;font-size:15px;font-weight:700;padding:14px 36px;border-radius:8px;text-decoration:none;margin-top:8px" target="_blank">Get in touch &rarr;</a>' if bcta else ''

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{company} - GTM Pitch by {bname}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#1a2332;padding:0}}
.header{{background:{color};padding:20px 32px;display:flex;align-items:center;gap:16px}}
.header-name{{color:#fff;font-size:20px;font-weight:800;letter-spacing:-.02em}}
.header-tag{{color:rgba(255,255,255,0.8);font-size:13px;margin-top:2px}}
.wrap{{max-width:680px;margin:0 auto;padding:32px 20px}}
.card{{background:#fff;border-radius:12px;padding:28px;margin-bottom:20px;box-shadow:0 1px 4px rgba(0,0,0,.07)}}
.company-name{{font-size:28px;font-weight:800;letter-spacing:-.03em;color:#0f1923;margin-bottom:6px}}
.meta{{font-size:13px;color:#64748b;margin-bottom:14px}}
.score-row{{display:flex;align-items:center;gap:12px;margin-bottom:0}}
.score-num{{font-size:36px;font-weight:900;color:{color};font-variant-numeric:tabular-nums}}
.score-label{{display:inline-block;background:{label_color}22;color:{label_color};font-size:11px;font-weight:700;padding:3px 10px;border-radius:999px;border:1px solid {label_color}44;text-transform:uppercase;letter-spacing:.06em}}
.section-title{{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:#94a3b8;margin-bottom:10px}}
.why-fit{{font-size:15px;color:#334155;line-height:1.65}}
.pitch-box{{background:#f1f5f9;border-left:3px solid {color};border-radius:0 8px 8px 0;padding:16px 18px;font-size:14px;color:#334155;line-height:1.7;font-style:italic}}
.contact-row{{display:flex;align-items:center;gap:10px;font-size:14px;color:#475569}}
.contact-dot{{width:8px;height:8px;border-radius:50%;background:{color}}}
.footer{{text-align:center;padding:24px 20px;font-size:12px;color:#94a3b8}}
</style>
</head>
<body>
<div class="header">
  {logo_html}
  <div>
    <div class="header-name">{bname}</div>
    {f'<div class="header-tag">{btagline}</div>' if btagline else ''}
  </div>
</div>
<div class="wrap">
  <div class="card">
    <div class="company-name">{company}</div>
    <div class="meta">{meta_str}</div>
    <div class="score-row">
      <div class="score-num">{score}</div>
      <div class="score-label">{label}</div>
    </div>
  </div>

  <div class="card">
    <div class="section-title">Why they need you now</div>
    <div class="why-fit">{why_fit}</div>
  </div>

  <div class="card">
    <div class="section-title">Your opening pitch</div>
    <div class="pitch-box">{pitch}</div>
  </div>

  {'<div class="card"><div class="section-title">Best contact</div><div class="contact-row"><div class="contact-dot"></div><div>' + (contact_name + (' - ' if contact_name else '') + contact_title) + '</div></div></div>' if contact_title or contact_name else ''}

  <div style="text-align:center;margin-top:8px">
    {cta_html}
  </div>
</div>
<div class="footer">Generated by {bname} &middot; Powered by Scout</div>
</body>
</html>"""

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
                user_email = self.headers.get('X-User-Email', None)
                user_key = user_email if user_email else None
                save_db(data, user_key)
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
            for _ in range(5):
                payload = json.dumps({'model': 'claude-sonnet-4-20250514', 'max_tokens': 1500, 'system': system,
                    'tools': [{'type': 'web_search_20250305', 'name': 'web_search'}], 'messages': messages}).encode('utf-8')
                req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=payload,
                    headers={'Content-Type': 'application/json', 'x-api-key': actual_key, 'anthropic-version': '2023-06-01'}, method='POST')
                try:
                    with urllib.request.urlopen(req, timeout=90) as resp:
                        data = json.loads(resp.read())
                except urllib.error.HTTPError as e:
                    if e.code in (429, 529):
                        import time; time.sleep(15); continue
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
        elif mode == 'source':
            source_sys = (
                "You are a talent sourcing expert. Given a job description:\n"
                "1. Generate 3 LinkedIn X-Ray search strings (site:linkedin.com/in format)\n"
                "2. Search the web using each string to find real candidate profiles\n"
                "3. For each candidate found, extract: name, current_title, current_company, location, linkedin_url, summary\n"
                "4. Score each 0-100 based on fit for the job description\n"
                "5. Write a 2-sentence personalised LinkedIn InMail for each\n"
                "Return ONLY a valid JSON array. Each object: name, current_title, current_company, location, linkedin_url, fit_score, why_fit, inmail. "
                "Use null for unknown. Start with [ immediately."
            )
            messages = [{'role': 'user', 'content': 'Job description: ' + company}]
            final_text = ''
            for _ in range(15):
                payload = json.dumps({'model': 'claude-sonnet-4-20250514', 'max_tokens': 4000, 'system': source_sys,
                    'tools': [{'type': 'web_search_20250305', 'name': 'web_search'}], 'messages': messages}).encode('utf-8')
                req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=payload,
                    headers={'Content-Type': 'application/json', 'x-api-key': actual_key, 'anthropic-version': '2023-06-01'}, method='POST')
                try:
                    with urllib.request.urlopen(req, timeout=120) as resp:
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
        elif mode == 'research':
            messages = [{'role': 'user', 'content': 'Research this company and return ONLY a JSON object with the profile. Company: "' + company + '"'}]
            final_text = ''
            for _ in range(3):
                payload = json.dumps({'model': 'claude-haiku-4-5-20251001', 'max_tokens': 1500, 'system': system,
                    'tools': [{'type': 'web_search_20250305', 'name': 'web_search'}], 'messages': messages}).encode('utf-8')
                req = urllib.request.Request('https://api.anthropic.com/v1/messages', data=payload,
                    headers={'Content-Type': 'application/json', 'x-api-key': actual_key, 'anthropic-version': '2023-06-01'}, method='POST')
                try:
                    with urllib.request.urlopen(req, timeout=90) as resp:
                        data = json.loads(resp.read())
                except urllib.error.HTTPError as e:
                    if e.code in (429, 529):
                        import time; time.sleep(10); continue
                    self.respond({'error': 'API error ' + str(e.code) + ': ' + e.read().decode()[:200]}); return
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
            payload = json.dumps({'model': 'claude-haiku-4-5-20251001', 'max_tokens': 1000, 'system': system,
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
