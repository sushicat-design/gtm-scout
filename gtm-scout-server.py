#!/usr/bin/env python3
import http.server, json, urllib.request, urllib.error, threading, time, sys, os, socket

def find_port():
    for p in range(8765, 8800):
        try:
            s = socket.socket(); s.bind(('', p)); s.close(); return p
        except: continue
    return 8765

PORT = int(os.environ.get('PORT', find_port()))

HTML = ""
HTML += "<!DOCTYPE html>\n"
HTML += "<html>\n<head>\n"
HTML += "<meta charset='UTF-8'>\n"
HTML += "<title>GTM Scout</title>\n"
HTML += "<link rel='icon' href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎯</text></svg>\">\n"
HTML += "<style>\n"
HTML += "*{box-sizing:border-box;margin:0;padding:0}\n"
HTML += ":root{--bg:#07090f;--sur:#0e1119;--sur2:#141824;--bor:#1d2333;--bor2:#252d3f;--grn:#00e676;--amb:#ffb300;--red:#ff5252;--blu:#448aff;--tx:#dde4f0;--tx2:#8492aa;--tx3:#4a5570}\n"
HTML += "body{background:var(--bg);color:var(--tx);font-family:monospace;font-size:13px;min-height:100vh}\n"
HTML += ".topbar{display:flex;align-items:center;justify-content:space-between;padding:13px 24px;border-bottom:1px solid var(--bor);position:sticky;top:0;background:var(--bg);z-index:10}\n"
HTML += ".logo{color:var(--grn);font-weight:bold;font-size:16px}\n"
HTML += ".stats{display:flex;gap:20px}\n"
HTML += ".stat-n{font-size:20px;font-weight:bold;color:var(--grn);text-align:right}\n"
HTML += ".stat-l{font-size:9px;color:var(--tx3);text-transform:uppercase;text-align:right}\n"
HTML += ".main{max-width:960px;margin:0 auto;padding:24px}\n"
HTML += ".panel{background:var(--sur);border:1px solid var(--bor);padding:16px;margin-bottom:12px}\n"
HTML += ".irow{display:flex;gap:8px}\n"
HTML += "#ci{flex:1;background:var(--bg);border:1px solid var(--bor2);color:var(--tx);font-family:monospace;font-size:13px;padding:10px 14px;outline:none}\n"
HTML += "#ci:focus{border-color:var(--grn)}\n"
HTML += "#ci:disabled{opacity:.5}\n"
HTML += "#rb{background:var(--grn);color:#000;border:none;font-weight:bold;font-size:13px;padding:0 20px;cursor:pointer;white-space:nowrap}\n"
HTML += "#rb:disabled{opacity:.35;cursor:not-allowed}\n"
HTML += ".tlink{background:none;border:none;color:var(--tx3);font-size:10px;cursor:pointer;text-decoration:underline;font-family:monospace;padding:0}\n"
HTML += ".tlink.blu{color:var(--blu)}\n"
HTML += ".panel-extra{display:none;margin-top:12px;padding-top:12px;border-top:1px solid var(--bor)}\n"
HTML += "#bi,#ii{width:100%;background:var(--bg);border:1px solid var(--bor2);color:var(--tx);font-family:monospace;font-size:12px;padding:8px 12px;min-height:80px;resize:vertical;outline:none;line-height:1.6}\n"
HTML += "#ldg{display:none;margin-top:12px;color:var(--tx3);font-size:12px}\n"
HTML += "#err{display:none;margin-top:10px;padding:10px;background:rgba(255,82,82,.1);border:1px solid rgba(255,82,82,.3);color:var(--red);font-size:12px;word-break:break-all}\n"
HTML += "#ierr{display:none;margin-top:6px;color:var(--red);font-size:11px}\n"
HTML += ".tb{display:none;align-items:center;gap:6px;margin-bottom:10px;flex-wrap:wrap}\n"
HTML += ".fb{font-size:9px;padding:3px 10px;background:none;border:1px solid var(--bor);color:var(--tx3);cursor:pointer;font-family:monospace;text-transform:uppercase}\n"
HTML += ".fb.on{border-color:var(--grn);color:var(--grn)}\n"
HTML += ".cbtn{margin-left:auto;font-size:10px;padding:5px 12px;background:none;border:1px solid var(--bor2);color:var(--tx2);cursor:pointer;font-family:monospace}\n"
HTML += ".xbtn{font-size:10px;padding:5px 12px;background:none;border:1px solid rgba(255,82,82,.3);color:var(--red);cursor:pointer;font-family:monospace}\n"
HTML += ".card{background:var(--sur);border:1px solid var(--bor);margin-bottom:4px}\n"
HTML += ".ctop{display:flex;align-items:center;gap:12px;padding:12px 16px;cursor:pointer}\n"
HTML += ".ctop:hover{background:rgba(255,255,255,.02)}\n"
HTML += ".cname{font-size:15px;font-weight:bold;flex:1}\n"
HTML += ".cscore{font-size:20px;font-weight:bold}\n"
HTML += ".clbl{font-size:10px;padding:2px 8px;border:1px solid;text-transform:uppercase}\n"
HTML += ".cbody{display:none;border-top:1px solid var(--bor)}\n"
HTML += ".cbody.open{display:flex;flex-wrap:wrap}\n"
HTML += ".cleft{flex:1 1 280px;padding:16px;border-right:1px solid var(--bor)}\n"
HTML += ".cright{flex:1 1 220px;padding:16px;background:var(--sur2)}\n"
HTML += ".grid{display:grid;grid-template-columns:1fr 1fr;gap:4px;margin-bottom:14px}\n"
HTML += ".cell{background:var(--bg);border:1px solid var(--bor);padding:6px 8px}\n"
HTML += ".ck{font-size:9px;color:var(--tx3);text-transform:uppercase;margin-bottom:2px}\n"
HTML += ".cv{font-size:11px}\n"
HTML += ".cv a{color:var(--blu);text-decoration:none}\n"
HTML += ".sec{font-size:9px;color:var(--tx3);text-transform:uppercase;margin:12px 0 6px}\n"
HTML += ".lks{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:12px}\n"
HTML += ".lks a{font-size:10px;padding:3px 8px;border:1px solid var(--bor);color:var(--tx2);text-decoration:none}\n"
HTML += ".sr{display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid var(--bor);font-size:11px}\n"
HTML += ".sy{color:var(--grn);font-weight:bold}\n"
HTML += ".sn{color:var(--red);font-weight:bold}\n"
HTML += ".su{color:var(--tx3)}\n"
HTML += ".pb{background:rgba(0,230,118,.07);border:1px solid rgba(0,230,118,.2);padding:12px;margin-top:12px}\n"
HTML += ".pb p{font-size:9px;color:var(--grn);text-transform:uppercase;margin-bottom:6px}\n"
HTML += ".pb div{font-size:11px;color:#c8ffe0;line-height:1.75;font-style:italic}\n"
HTML += ".cact{display:flex;gap:6px;padding:10px 16px;background:var(--bg);border-top:1px solid var(--bor);flex-wrap:wrap}\n"
HTML += ".cact button{font-size:10px;padding:5px 10px;background:none;border:1px solid var(--bor2);color:var(--tx2);cursor:pointer;font-family:monospace}\n"
HTML += ".cact button.g{border-color:rgba(0,230,118,.3);color:var(--grn)}\n"
HTML += ".empty{text-align:center;padding:60px 20px;color:var(--tx3);font-size:12px;line-height:2}\n"
HTML += "</style>\n"
HTML += "</head>\n<body>\n"
HTML += "<div class='topbar'>\n"
HTML += "  <span class='logo'>GTM Scout</span>\n"
HTML += "  <div class='stats'>\n"
HTML += "    <div><div class='stat-n' id='stt'>0</div><div class='stat-l'>Total</div></div>\n"
HTML += "    <div><div class='stat-n' id='sth'>0</div><div class='stat-l'>Hot Leads</div></div>\n"
HTML += "  </div>\n"
HTML += "</div>\n"
HTML += "<div class='main'>\n"
HTML += "  <div class='panel'>\n"
HTML += "    <div class='irow'>\n"
HTML += "      <input id='ci' type='text' placeholder='Company name, e.g. Privy, Alchemy, EigenLayer...'>\n"
HTML += "      <button id='rb'>Research</button>\n"
HTML += "    </div>\n"
HTML += "    <div id='ldg'>Searching for <span id='lname'></span>... <span id='ltimer'>0s</span></div>\n"
HTML += "    <div id='err'></div>\n"
HTML += "    <div style='display:flex;gap:16px;margin-top:10px'>\n"
HTML += "      <button class='tlink' id='btog'>+ Bulk research</button>\n"
HTML += "      <button class='tlink blu' id='itog'>+ Import JSON</button>\n"
HTML += "    </div>\n"
HTML += "    <div class='panel-extra' id='bpanel'>\n"
HTML += "      <div style='font-size:9px;color:var(--tx3);text-transform:uppercase;margin-bottom:6px'>One company per line</div>\n"
HTML += "      <textarea id='bi' placeholder='Privy&#10;Alchemy&#10;EigenLayer'></textarea>\n"
HTML += "      <button id='brb' style='margin-top:8px;background:var(--grn);color:#000;border:none;font-weight:bold;font-size:12px;padding:8px 18px;cursor:pointer'>Research All</button>\n"
HTML += "    </div>\n"
HTML += "    <div class='panel-extra' id='ipanel'>\n"
HTML += "      <div style='font-size:9px;color:var(--blu);text-transform:uppercase;margin-bottom:6px'>Paste JSON array or single company object</div>\n"
HTML += "      <textarea id='ii' style='border-color:rgba(68,138,255,0.3)' placeholder='[{&quot;company&quot;:&quot;Privy&quot;,...}]'></textarea>\n"
HTML += "      <div id='ierr'></div>\n"
HTML += "      <button id='iib' style='margin-top:8px;background:var(--blu);color:#fff;border:none;font-weight:bold;font-size:12px;padding:8px 18px;cursor:pointer'>Import</button>\n"
HTML += "    </div>\n"
HTML += "  </div>\n"
HTML += "  <div class='tb' id='tb'>\n"
HTML += "    <button class='fb on' data-f='all'>All</button>\n"
HTML += "    <button class='fb' data-f='hot'>Hot</button>\n"
HTML += "    <button class='fb' data-f='warm'>Warm</button>\n"
HTML += "    <button class='fb' data-f='cold'>Cold</button>\n"
HTML += "    <button class='cbtn' id='csvbtn'>Export CSV</button>\n"
HTML += "    <button class='xbtn' id='clrbtn'>Clear All</button>\n"
HTML += "  </div>\n"
HTML += "  <div id='cards'></div>\n"
HTML += "  <div class='empty' id='empty'>Type a company name and hit Research.<br>Results save automatically and persist across visits.</div>\n"
HTML += "</div>\n"

# JavaScript - built as a string to avoid any escaping issues
JS = """
var DB = [];
var busy = false;
var fil = 'all';
var ti = null;
var SYS = 'Return ONLY a valid JSON object, no markdown, no backticks, no text before or after. Fields: company, tagline, website, sector, hq, founded, stage, funding_amount, funding_date, lead_investor, other_investors, employee_count, socials (object: twitter, linkedin, discord, telegram, github), founders (array of: name/role/background), has_cmo (bool), has_marketing_hire (bool), marketing_notes, product_status, community_size, gtm_readiness_score (integer 0-100), gtm_label (exactly "Hot Lead" if 80+, "Warm Lead" if 50-79, "Cold Lead" if below 50), gtm_signals (object of booleans: recently_funded, no_cmo, pre_launch_or_early, active_community, has_product, small_team, marketing_gap_visible), why_fit, risks, pitch_opener, decision_maker. Use null for unknown.';

function load() {
  try { var s = localStorage.getItem('gtm_db'); if (s) DB = JSON.parse(s); } catch(e) { DB = []; }
}
function save() {
  try { localStorage.setItem('gtm_db', JSON.stringify(DB)); } catch(e) {}
}

function showPanel(id) {
  var ids = ['bpanel', 'ipanel'];
  ids.forEach(function(pid) {
    document.getElementById(pid).style.display = (pid === id && document.getElementById(pid).style.display !== 'block') ? 'block' : 'none';
  });
  document.getElementById('btog').textContent = document.getElementById('bpanel').style.display === 'block' ? '- Bulk research' : '+ Bulk research';
  document.getElementById('itog').textContent = document.getElementById('ipanel').style.display === 'block' ? '- Import JSON' : '+ Import JSON';
}

function go() {
  var v = document.getElementById('ci').value.trim();
  if (!v || busy) return;
  document.getElementById('ci').value = '';
  run(v);
}

function bulk() {
  if (busy) return;
  var raw = document.getElementById('bi').value.trim();
  var names = raw.split('\\n').map(function(s) { return s.trim(); }).filter(function(s) { return s.length > 0; });
  if (!names.length) return;
  document.getElementById('bi').value = '';
  var i = 0;
  function next() {
    if (i >= names.length) return;
    var name = names[i++];
    run(name, next);
  }
  next();
}

function importJSON() {
  var raw = document.getElementById('ii').value.trim();
  var errEl = document.getElementById('ierr');
  errEl.style.display = 'none';
  try {
    var clean = raw.replace(/```json/g, '').replace(/```/g, '').trim();
    var parsed;
    if (clean.charAt(0) === '[') {
      parsed = JSON.parse(clean);
    } else {
      var a = clean.indexOf('{'), b = clean.lastIndexOf('}');
      parsed = [JSON.parse(clean.slice(a, b + 1))];
    }
    var added = 0;
    for (var i = 0; i < parsed.length; i++) {
      var r = parsed[i];
      if (r && r.company) {
        r._id = 'id' + Date.now() + Math.floor(Math.random() * 10000);
        r._open = true;
        DB.unshift(r);
        added++;
      }
    }
    if (!added) throw new Error('No valid company objects found');
    save();
    renderAll();
    document.getElementById('ii').value = '';
    document.getElementById('ipanel').style.display = 'none';
    document.getElementById('itog').textContent = '+ Import JSON';
  } catch(e) {
    errEl.textContent = 'Error: ' + e.message;
    errEl.style.display = 'block';
  }
}

function run(company, callback) {
  busy = true;
  document.getElementById('rb').disabled = true;
  document.getElementById('ci').disabled = true;
  document.getElementById('err').style.display = 'none';
  document.getElementById('lname').textContent = company;
  document.getElementById('ldg').style.display = 'block';
  var secs = 0;
  document.getElementById('ltimer').textContent = '0s';
  ti = setInterval(function() { document.getElementById('ltimer').textContent = (++secs) + 's'; }, 1000);

  fetch('/api', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ key: '', company: company, system: SYS })
  }).then(function(resp) {
    return resp.json();
  }).then(function(d) {
    if (d.error) throw new Error(d.error);
    var t = d.text || '';
    t = t.replace(/```json/g, '').replace(/```/g, '').trim();
    var a = t.indexOf('{'), b = t.lastIndexOf('}');
    if (a < 0 || b < 0) throw new Error('No JSON returned');
    var res = JSON.parse(t.slice(a, b + 1));
    res._id = 'id' + Date.now();
    res._open = true;
    DB.unshift(res);
    save();
    renderAll();
  }).catch(function(e) {
    var el = document.getElementById('err');
    el.textContent = 'Error: ' + e.message;
    el.style.display = 'block';
  }).finally(function() {
    clearInterval(ti);
    document.getElementById('ldg').style.display = 'none';
    document.getElementById('rb').disabled = false;
    document.getElementById('ci').disabled = false;
    busy = false;
    if (callback) callback();
  });
}

function sc(n) { return n >= 80 ? '#00e676' : n >= 50 ? '#ffb300' : '#888'; }
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
    var c = sc(n);
    var s = r.socials || {};
    var g = r.gtm_signals || {};
    var ff = Array.isArray(r.founders) ? r.founders : [];
    var id = r._id;
    var open = r._open;
    var site = su(r.website);

    var card = document.createElement('div');
    card.className = 'card';

    var top = document.createElement('div');
    top.className = 'ctop';
    var nameHtml = '<div class="cname">' + (r.company || '');
    if (site) nameHtml += ' <a href="' + site + '" target="_blank" style="font-size:10px;color:#448aff;font-weight:normal;border:1px solid #1d2333;padding:1px 5px;text-decoration:none;margin-left:4px">visit</a>';
    nameHtml += '<div style="font-size:10px;color:#4a5570;margin-top:2px">' + [r.sector, r.funding_amount, r.stage].filter(function(v) { return v && v !== 'Unknown'; }).join(' · ') + '</div></div>';
    top.innerHTML = '<span class="cscore" style="color:' + c + '">' + n + '</span>' + nameHtml + '<span class="clbl" style="color:' + c + ';border-color:' + c + '">' + (r.gtm_label || '') + '</span>';
    top.onclick = function() { r._open = !r._open; save(); renderCards(); };
    card.appendChild(top);

    if (open) {
      var body = document.createElement('div');
      body.className = 'cbody open';

      var left = document.createElement('div');
      left.className = 'cleft';

      var pg = '<div class="grid">';
      var profileFields = [['Website',r.website,true],['HQ',r.hq],['Founded',r.founded],['Team',r.employee_count],['Stage',r.stage],['Product',r.product_status],['Funding',r.funding_amount],['Investor',r.lead_investor]];
      profileFields.forEach(function(x) {
        var u = x[2] ? su(x[1]) : '';
        pg += '<div class="cell"><div class="ck">' + x[0] + '</div><div class="cv">';
        if (u) pg += '<a href="' + u + '" target="_blank">' + String(x[1]).replace('https://','').replace('http://','') + '</a>';
        else pg += (x[1] && x[1] !== 'Unknown') ? x[1] : '<span style="color:#4a5570">—</span>';
        pg += '</div></div>';
      });
      pg += '</div>';

      var lks = '<div class="lks">';
      var tw = s.twitter ? 'https://twitter.com/' + String(s.twitter).replace('@','') : '';
      var linkDefs = [[tw,'Twitter'],[s.linkedin,'LinkedIn'],[s.discord,'Discord'],[s.telegram,'Telegram'],[s.github,'GitHub']];
      linkDefs.forEach(function(x) { var u = su(x[0]); if (u) lks += '<a href="' + u + '" target="_blank">' + x[1] + '</a>'; });
      lks += '</div>';

      var fnd = '<div style="margin-bottom:12px">';
      if (ff.length) {
        ff.forEach(function(f) {
          var ini = String(f.name || '?').split(' ').map(function(w) { return w[0]; }).slice(0,2).join('').toUpperCase();
          fnd += '<div style="display:flex;gap:8px;align-items:center;padding:6px 8px;background:#07090f;border:1px solid #1d2333;margin-bottom:3px">';
          fnd += '<div style="width:24px;height:24px;border-radius:50%;background:#1d2333;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:bold;color:#00e676;flex-shrink:0">' + ini + '</div>';
          fnd += '<div><div style="font-size:12px;font-weight:500">' + (f.name||'') + '</div><div style="font-size:10px;color:#4a5570">' + (f.role||'') + (f.background ? ' - ' + f.background : '') + '</div></div></div>';
        });
      } else {
        fnd += '<div style="font-size:11px;color:#4a5570">Unknown</div>';
      }
      fnd += '</div>';

      var inv = [r.lead_investor, r.other_investors].filter(function(v) { return v && v !== 'null'; }).join(', ');
      left.innerHTML = '<div class="sec">Profile</div>' + pg +
        (inv ? '<div class="sec">Investors</div><div style="font-size:11px;color:#8492aa;margin-bottom:12px">' + inv + '</div>' : '') +
        '<div class="sec">Socials</div>' + lks +
        '<div class="sec">Founders</div>' + fnd +
        '<div class="sec">Community</div><div style="font-size:11px;color:#8492aa;margin-bottom:12px">' + (r.community_size||'Unknown') + '</div>' +
        '<div class="sec">Marketing</div><div style="font-size:11px;color:#8492aa">' + (r.marketing_notes||'—') + '</div>';

      var right = document.createElement('div');
      right.className = 'cright';
      var sigs = '<div class="sec" style="margin-top:0">GTM Signals</div>';
      var sigDefs = [['recently_funded','Recently funded'],['no_cmo','No CMO'],['pre_launch_or_early','Pre-launch / early GTM'],['has_product','Has product'],['small_team','Small team'],['marketing_gap_visible','Marketing gap'],['active_community','Active community']];
      sigDefs.forEach(function(x) {
        var v = g[x[0]];
        var cls = v === true ? 'sy' : v === false ? 'sn' : 'su';
        var t = v === true ? 'Yes' : v === false ? 'No' : '?';
        sigs += '<div class="sr"><span>' + x[1] + '</span><span class="' + cls + '">' + t + '</span></div>';
      });
      right.innerHTML = sigs +
        '<div class="sec">Why They Fit</div><div style="font-size:11px;color:#8492aa;line-height:1.7;margin-bottom:12px">' + (r.why_fit||'—') + '</div>' +
        '<div class="sec">Risks</div><div style="font-size:11px;color:#ffb300;line-height:1.7;margin-bottom:12px">' + (r.risks||'—') + '</div>' +
        '<div class="sec">Reach Out To</div><div style="font-size:11px;color:#448aff;margin-bottom:12px">' + (r.decision_maker||'—') + '</div>' +
        '<div class="pb"><p>Pitch Opener</p><div id="pt' + id + '">' + (r.pitch_opener||'—') + '</div></div>';

      body.appendChild(left);
      body.appendChild(right);
      card.appendChild(body);

      var acts = document.createElement('div');
      acts.className = 'cact';

      var cp = document.createElement('button');
      cp.className = 'g';
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

      if (site) {
        var sb = document.createElement('button');
        sb.textContent = 'Visit Site';
        (function(u) { sb.onclick = function() { window.open(u, '_blank'); }; })(site);
        acts.appendChild(sb);
      }

      var liu = su(s.linkedin);
      if (liu) {
        var lb = document.createElement('button');
        lb.textContent = 'LinkedIn';
        (function(u) { lb.onclick = function() { window.open(u, '_blank'); }; })(liu);
        acts.appendChild(lb);
      }

      if (s.twitter && s.twitter !== 'null') {
        var twb = document.createElement('button');
        twb.textContent = 'Twitter';
        (function(h) { twb.onclick = function() { window.open('https://twitter.com/' + h.replace('@',''), '_blank'); }; })(s.twitter);
        acts.appendChild(twb);
      }

      var rm = document.createElement('button');
      rm.textContent = 'Remove';
      rm.style.marginLeft = 'auto';
      (function(cardId) {
        rm.onclick = function() {
          DB = DB.filter(function(x) { return x._id !== cardId; });
          save();
          renderAll();
        };
      })(id);
      acts.appendChild(rm);
      card.appendChild(acts);
    }
    cont.appendChild(card);
  });
}

function doCSV() {
  var headers = ['Company','Tagline','Website','Sector','HQ','Founded','Stage','Funding','Date','Lead Investor','Other Investors','Employees','Twitter','LinkedIn','Discord','Telegram','GitHub','Founders','Has CMO','Mktg Notes','Product','Community','Score','Label','Funded','No CMO','Pre-launch','Has Product','Small Team','Mktg Gap','Why Fit','Risks','Pitch','Decision Maker'];
  function esc(v) {
    var str = String(v == null ? '' : v).replace(/"/g, '""');
    return (str.indexOf(',') >= 0 || str.indexOf('\\n') >= 0) ? '"' + str + '"' : str;
  }
  var rows = DB.map(function(r) {
    var s = r.socials || {};
    var g = r.gtm_signals || {};
    var f = (r.founders || []).map(function(x) { return x.name + ' (' + x.role + ')'; }).join('; ');
    return [r.company,r.tagline,r.website,r.sector,r.hq,r.founded,r.stage,r.funding_amount,r.funding_date,r.lead_investor,r.other_investors,r.employee_count,s.twitter,s.linkedin,s.discord,s.telegram,s.github,f,r.has_cmo,r.marketing_notes,r.product_status,r.community_size,r.gtm_readiness_score,r.gtm_label,g.recently_funded,g.no_cmo,g.pre_launch_or_early,g.has_product,g.small_team,g.marketing_gap_visible,r.why_fit,r.risks,r.pitch_opener,r.decision_maker].map(esc).join(',');
  });
  var csv = [headers.join(',')].concat(rows).join('\\n');
  var a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
  a.download = 'gtm-leads.csv';
  a.click();
}

// Wire up all buttons after DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  load();
  renderAll();

  document.getElementById('rb').onclick = go;
  document.getElementById('ci').addEventListener('keydown', function(e) { if (e.key === 'Enter') go(); });
  document.getElementById('btog').onclick = function() { showPanel('bpanel'); };
  document.getElementById('itog').onclick = function() { showPanel('ipanel'); };
  document.getElementById('brb').onclick = bulk;
  document.getElementById('iib').onclick = importJSON;
  document.getElementById('csvbtn').onclick = doCSV;
  document.getElementById('clrbtn').onclick = function() {
    if (confirm('Clear all saved companies?')) { DB = []; save(); renderAll(); }
  };
  document.querySelectorAll('.fb').forEach(function(btn) {
    btn.onclick = function() {
      fil = btn.getAttribute('data-f');
      document.querySelectorAll('.fb').forEach(function(b) { b.classList.remove('on'); });
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
        content = HTML.encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_POST(self):
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

        messages = [{'role': 'user', 'content': 'Search the web and research this company, then return the JSON profile: "' + company + '". Find their website, funding, founders, team size, socials (Twitter, LinkedIn, Discord, GitHub), and whether they have a CMO.'}]
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
                tool_results = []
                for block in content:
                    if block.get('type') == 'tool_use':
                        tool_results.append({'type': 'tool_result', 'tool_use_id': block['id'], 'content': [{'type': 'text', 'text': 'ok'}]})
                messages.append({'role': 'user', 'content': tool_results})
            else:
                break

        self.respond({'text': final_text})

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
