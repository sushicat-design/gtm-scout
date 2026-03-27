#!/usr/bin/env python3
import http.server, json, urllib.request, urllib.error, threading, time, sys, os

import os
PORT = int(os.environ.get('PORT', 8765))

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>GTM Scout</title>
<style>
body { margin: 0; background: #07090f; color: #dde4f0; font-family: monospace; font-size: 14px; }
#setup { display: flex; align-items: center; justify-content: center; min-height: 100vh; }
.box { background: #0e1119; border: 1px solid #1d2333; padding: 40px; width: 440px; }
h2 { font-size: 22px; margin-bottom: 24px; color: #00e676; }
label { display: block; font-size: 11px; color: #4a5570; text-transform: uppercase; margin-bottom: 6px; }
input { display: block; width: 100%; padding: 10px 12px; background: #07090f; border: 1px solid #252d3f; color: #dde4f0; font-family: monospace; font-size: 13px; margin-bottom: 16px; }
button { display: block; width: 100%; padding: 12px; background: #00e676; color: #000; border: none; font-size: 14px; font-weight: bold; cursor: pointer; }
#app { display: none; }
.topbar { background: #07090f; border-bottom: 1px solid #1d2333; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; }
.main { max-width: 960px; margin: 0 auto; padding: 24px; }
.panel { background: #0e1119; border: 1px solid #1d2333; padding: 16px; margin-bottom: 12px; }
.row { display: flex; gap: 8px; }
.row input { margin-bottom: 0; flex: 1; }
.row button { width: auto; padding: 0 20px; }
#loading { display: none; margin-top: 12px; color: #4a5570; font-size: 12px; }
#error { display: none; margin-top: 10px; padding: 10px; background: rgba(255,82,82,0.1); border: 1px solid rgba(255,82,82,0.3); color: #ff5252; font-size: 12px; word-break: break-all; }
.card { background: #0e1119; border: 1px solid #1d2333; margin-bottom: 4px; }
.card-top { display: flex; align-items: center; gap: 12px; padding: 12px 16px; cursor: pointer; }
.card-top:hover { background: rgba(255,255,255,0.02); }
.card-name { font-size: 15px; font-weight: bold; flex: 1; }
.score { font-size: 20px; font-weight: bold; }
.label { font-size: 10px; padding: 2px 8px; border: 1px solid; text-transform: uppercase; }
.card-body { display: none; border-top: 1px solid #1d2333; }
.card-body.open { display: flex; flex-wrap: wrap; }
.left { flex: 1 1 280px; padding: 16px; border-right: 1px solid #1d2333; }
.right { flex: 1 1 220px; padding: 16px; background: #141824; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-bottom: 14px; }
.cell { background: #07090f; border: 1px solid #1d2333; padding: 6px 8px; }
.cell-key { font-size: 9px; color: #4a5570; text-transform: uppercase; margin-bottom: 2px; }
.cell-val { font-size: 11px; }
.cell-val a { color: #448aff; text-decoration: none; }
.sec { font-size: 9px; color: #4a5570; text-transform: uppercase; margin: 12px 0 6px; }
.links { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 12px; }
.links a { font-size: 10px; padding: 3px 8px; border: 1px solid #1d2333; color: #8492aa; text-decoration: none; }
.sig-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid #1d2333; font-size: 11px; }
.yes { color: #00e676; font-weight: bold; }
.no { color: #ff5252; font-weight: bold; }
.unk { color: #4a5570; }
.pitch-box { background: rgba(0,230,118,0.07); border: 1px solid rgba(0,230,118,0.2); padding: 12px; margin-top: 12px; }
.pitch-box p { font-size: 9px; color: #00e676; text-transform: uppercase; margin-bottom: 6px; }
.pitch-box div { font-size: 11px; color: #c8ffe0; line-height: 1.75; font-style: italic; }
.actions { display: flex; gap: 6px; padding: 10px 16px; background: #07090f; border-top: 1px solid #1d2333; flex-wrap: wrap; }
.actions button { font-size: 10px; padding: 5px 10px; background: none; border: 1px solid #252d3f; color: #8492aa; cursor: pointer; font-family: monospace; }
.actions button.g { border-color: rgba(0,230,118,0.3); color: #00e676; }
.toolbar { display: none; align-items: center; gap: 6px; margin-bottom: 10px; flex-wrap: wrap; }
.fb { font-size: 9px; padding: 3px 10px; background: none; border: 1px solid #1d2333; color: #4a5570; cursor: pointer; font-family: monospace; text-transform: uppercase; }
.fb.on { border-color: #00e676; color: #00e676; }
.csv-btn { margin-left: auto; font-size: 10px; padding: 5px 12px; background: none; border: 1px solid #252d3f; color: #8492aa; cursor: pointer; font-family: monospace; }
.empty { text-align: center; padding: 60px 20px; color: #4a5570; font-size: 12px; line-height: 2; }
.stats { display: flex; gap: 20px; }
.stat-n { font-size: 20px; font-weight: bold; color: #00e676; text-align: right; }
.stat-l { font-size: 9px; color: #4a5570; text-transform: uppercase; text-align: right; }
</style>
</head>
<body>

<div id="setup">
  <div class="box">
    <h2>GTM Scout</h2>
    <label>Anthropic API Key</label>
    <input id="apikey" type="text" placeholder="sk-ant-api03-...">
    <p style="font-size:11px;color:#4a5570;margin-bottom:16px;line-height:1.8">Get your key: console.anthropic.com &rarr; API Keys &rarr; Create Key<br>Stored in your browser only. ~$0.01 per company.</p>
    <button id="launch-btn">Launch GTM Scout</button>
    <p id="setup-err" style="color:#ff5252;font-size:11px;margin-top:10px"></p>
  </div>
</div>

<div id="app">
  <div class="topbar">
    <span style="color:#00e676;font-weight:bold;font-size:15px">GTM Scout</span>
    <div class="stats">
      <div><div class="stat-n" id="stat-total">0</div><div class="stat-l">Total</div></div>
      <div><div class="stat-n" id="stat-hot">0</div><div class="stat-l">Hot</div></div>
    </div>
  </div>
  <div class="main">
    <div class="panel">
      <div class="row">
        <input id="company-input" type="text" placeholder="Company name, e.g. Privy, Alchemy, EigenLayer...">
        <button id="research-btn">Research</button>
      </div>
      <div id="loading">Researching... <span id="timer">0s</span></div>
      <div id="error"></div>
    </div>
    <div class="toolbar" id="toolbar">
      <button class="fb on" data-f="all">All</button>
      <button class="fb" data-f="hot">Hot</button>
      <button class="fb" data-f="warm">Warm</button>
      <button class="fb" data-f="cold">Cold</button>
      <button class="csv-btn" id="csv-btn">Export CSV</button>
    </div>
    <div id="cards"></div>
    <div class="empty" id="empty">Type a company name above and hit Research.<br>Full profile with GTM score, socials, founders, and pitch opener.<br>Export to CSV for Google Sheets or Notion.</div>
  </div>
</div>

<script>
var DB = [];
var API_KEY = '';
var busy = false;
var filter = 'all';
var timerInterval = null;

var SYSTEM = 'Return ONLY a valid JSON object, no markdown, no backticks, no text before or after the JSON. Fields required: company (string), tagline (string), website (string or null), sector (string), hq (string or null), founded (string or null), stage (string), funding_amount (string), funding_date (string), lead_investor (string or null), other_investors (string or null), employee_count (string or null), socials (object with keys: twitter, linkedin, discord, telegram, github - all strings or null), founders (array of objects with keys: name, role, background), has_cmo (boolean), has_marketing_hire (boolean), marketing_notes (string), product_status (string), community_size (string or null), gtm_readiness_score (integer 0-100), gtm_label (string, must be exactly "Hot Lead" if score 80 or above, "Warm Lead" if 50-79, "Cold Lead" if below 50), gtm_signals (object with boolean keys: recently_funded, no_cmo, pre_launch_or_early, active_community, has_product, small_team, marketing_gap_visible), why_fit (string), risks (string), pitch_opener (string), decision_maker (string).';

window.onload = function() {
  var saved = '';
  try { saved = localStorage.getItem('gtm_api_key') || ''; } catch(e) {}
  if (saved) document.getElementById('apikey').value = saved;

  document.getElementById('launch-btn').onclick = function() {
    var k = document.getElementById('apikey').value.trim();
    if (!k) {
      document.getElementById('setup-err').textContent = 'Please enter your API key';
      return;
    }
    API_KEY = k;
    try { localStorage.setItem('gtm_api_key', k); } catch(e) {}
    document.getElementById('setup').style.display = 'none';
    document.getElementById('app').style.display = 'block';
  };

  document.getElementById('company-input').onkeydown = function(e) {
    if (e.key === 'Enter') doResearch();
  };

  document.getElementById('research-btn').onclick = doResearch;

  document.getElementById('csv-btn').onclick = exportCSV;

  document.querySelectorAll('.fb').forEach(function(btn) {
    btn.onclick = function() {
      filter = btn.getAttribute('data-f');
      document.querySelectorAll('.fb').forEach(function(b) { b.classList.remove('on'); });
      btn.classList.add('on');
      renderCards();
    };
  });
};

function doResearch() {
  var name = document.getElementById('company-input').value.trim();
  if (!name || busy) return;
  document.getElementById('company-input').value = '';
  runResearch(name);
}

async function runResearch(company) {
  busy = true;
  document.getElementById('research-btn').disabled = true;
  document.getElementById('company-input').disabled = true;
  document.getElementById('error').style.display = 'none';
  document.getElementById('loading').style.display = 'block';
  var secs = 0;
  document.getElementById('timer').textContent = '0s';
  timerInterval = setInterval(function() {
    secs++;
    document.getElementById('timer').textContent = secs + 's';
  }, 1000);

  try {
    var resp = await fetch('/api', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ key: API_KEY, company: company, system: SYSTEM })
    });
    var data = await resp.json();
    if (data.error) throw new Error(data.error);
    var text = data.text || '';
    text = text.replace(/```json/g, '').replace(/```/g, '').trim();
    var start = text.indexOf('{');
    var end = text.lastIndexOf('}');
    if (start < 0 || end < 0) throw new Error('No JSON returned. Got: ' + text.slice(0, 100));
    var result = JSON.parse(text.slice(start, end + 1));
    result._id = 'id' + Date.now();
    result._open = true;
    DB.unshift(result);
    renderAll();
  } catch(err) {
    var el = document.getElementById('error');
    el.textContent = 'Error: ' + err.message;
    el.style.display = 'block';
  }

  clearInterval(timerInterval);
  document.getElementById('loading').style.display = 'none';
  document.getElementById('research-btn').disabled = false;
  document.getElementById('company-input').disabled = false;
  busy = false;
}

function scoreColor(n) {
  return n >= 80 ? '#00e676' : n >= 50 ? '#ffb300' : '#888';
}

function safeUrl(v) {
  if (!v || v === 'null') return '';
  return String(v).startsWith('http') ? v : 'https://' + v;
}

function renderAll() {
  document.getElementById('stat-total').textContent = DB.length;
  document.getElementById('stat-hot').textContent = DB.filter(function(r) { return r.gtm_label === 'Hot Lead'; }).length;
  document.getElementById('empty').style.display = DB.length ? 'none' : 'block';
  document.getElementById('toolbar').style.display = DB.length ? 'flex' : 'none';
  renderCards();
}

function renderCards() {
  var shown = filter === 'all' ? DB : DB.filter(function(r) {
    return r.gtm_label === (filter === 'hot' ? 'Hot Lead' : filter === 'warm' ? 'Warm Lead' : 'Cold Lead');
  });
  var container = document.getElementById('cards');
  container.innerHTML = '';
  shown.forEach(function(r) {
    var sc = r.gtm_readiness_score || 0;
    var c = scoreColor(sc);
    var s = r.socials || {};
    var g = r.gtm_signals || {};
    var founders = Array.isArray(r.founders) ? r.founders : [];
    var id = r._id;
    var open = r._open;
    var site = safeUrl(r.website);

    var card = document.createElement('div');
    card.className = 'card';

    // Top bar
    var top = document.createElement('div');
    top.className = 'card-top';
    top.innerHTML =
      '<span class="score" style="color:' + c + '">' + sc + '</span>' +
      '<div class="card-name">' + (r.company || '') +
        (site ? ' <a href="' + site + '" target="_blank" style="font-size:10px;color:#448aff;font-weight:normal;border:1px solid #1d2333;padding:1px 5px;text-decoration:none;margin-left:4px">visit</a>' : '') +
        '<div style="font-size:10px;color:#4a5570;margin-top:2px">' +
          [r.sector, r.funding_amount, r.stage].filter(function(v) { return v && v !== 'Unknown'; }).join(' &bull; ') +
        '</div>' +
      '</div>' +
      '<span class="label" style="color:' + c + ';border-color:' + c + '">' + (r.gtm_label || '') + '</span>';
    top.onclick = function() { r._open = !r._open; renderCards(); };
    card.appendChild(top);

    if (open) {
      var body = document.createElement('div');
      body.className = 'card-body open';

      // Left column
      var left = document.createElement('div');
      left.className = 'left';

      var profileHtml = '<div class="grid">';
      [['Website', r.website, true], ['HQ', r.hq], ['Founded', r.founded], ['Team', r.employee_count], ['Stage', r.stage], ['Product', r.product_status], ['Funding', r.funding_amount], ['Investor', r.lead_investor]].forEach(function(x) {
        var u = x[2] ? safeUrl(x[1]) : '';
        profileHtml += '<div class="cell"><div class="cell-key">' + x[0] + '</div><div class="cell-val">';
        if (u) profileHtml += '<a href="' + u + '" target="_blank">' + String(x[1]).replace(/^https?:\/\//, '') + '</a>';
        else profileHtml += (x[1] && x[1] !== 'Unknown') ? x[1] : '<span style="color:#4a5570">—</span>';
        profileHtml += '</div></div>';
      });
      profileHtml += '</div>';

      var linksHtml = '<div class="links">';
      var linkDefs = [
        [s.twitter ? 'https://twitter.com/' + String(s.twitter).replace('@','') : '', 'Twitter'],
        [s.linkedin, 'LinkedIn'], [s.discord, 'Discord'], [s.telegram, 'Telegram'], [s.github, 'GitHub']
      ];
      linkDefs.forEach(function(x) {
        var u = safeUrl(x[0]);
        if (u) linksHtml += '<a href="' + u + '" target="_blank">' + x[1] + '</a>';
      });
      linksHtml += '</div>';

      var foundersHtml = '<div style="margin-bottom:12px">';
      if (founders.length) {
        founders.forEach(function(f) {
          var ini = String(f.name || '?').split(' ').map(function(w) { return w[0]; }).slice(0,2).join('').toUpperCase();
          foundersHtml += '<div style="display:flex;gap:8px;align-items:center;padding:6px 8px;background:#07090f;border:1px solid #1d2333;margin-bottom:3px">' +
            '<div style="width:24px;height:24px;border-radius:50%;background:#1d2333;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:bold;color:#00e676;flex-shrink:0">' + ini + '</div>' +
            '<div><div style="font-size:12px;font-weight:500">' + (f.name||'') + '</div>' +
            '<div style="font-size:10px;color:#4a5570">' + (f.role||'') + (f.background ? ' - ' + f.background : '') + '</div></div></div>';
        });
      } else {
        foundersHtml += '<div style="font-size:11px;color:#4a5570">Unknown</div>';
      }
      foundersHtml += '</div>';

      left.innerHTML =
        '<div class="sec">Profile</div>' + profileHtml +
        (r.other_investors ? '<div class="sec">Investors</div><div style="font-size:11px;color:#8492aa;margin-bottom:12px">' + [r.lead_investor, r.other_investors].filter(Boolean).join(', ') + '</div>' : '') +
        '<div class="sec">Socials</div>' + linksHtml +
        '<div class="sec">Founders</div>' + foundersHtml +
        '<div class="sec">Community</div><div style="font-size:11px;color:#8492aa;margin-bottom:12px">' + (r.community_size || 'Unknown') + '</div>' +
        '<div class="sec">Marketing</div><div style="font-size:11px;color:#8492aa">' + (r.marketing_notes || '—') + '</div>';

      // Right column
      var right = document.createElement('div');
      right.className = 'right';
      var sigDefs = [
        ['recently_funded','Recently funded'], ['no_cmo','No CMO'],
        ['pre_launch_or_early','Pre-launch / early GTM'], ['has_product','Has product'],
        ['small_team','Small team'], ['marketing_gap_visible','Marketing gap visible'], ['active_community','Active community']
      ];
      var sigsHtml = '<div class="sec" style="margin-top:0">GTM Signals</div>';
      sigDefs.forEach(function(x) {
        var v = g[x[0]];
        var cls = v === true ? 'yes' : v === false ? 'no' : 'unk';
        var t = v === true ? 'Yes' : v === false ? 'No' : '?';
        sigsHtml += '<div class="sig-row"><span>' + x[1] + '</span><span class="' + cls + '">' + t + '</span></div>';
      });
      right.innerHTML = sigsHtml +
        '<div class="sec">Why They Fit</div><div style="font-size:11px;color:#8492aa;line-height:1.7;margin-bottom:12px">' + (r.why_fit||'—') + '</div>' +
        '<div class="sec">Risks</div><div style="font-size:11px;color:#ffb300;line-height:1.7;margin-bottom:12px">' + (r.risks||'—') + '</div>' +
        '<div class="sec">Reach Out To</div><div style="font-size:11px;color:#448aff;margin-bottom:12px">' + (r.decision_maker||'—') + '</div>' +
        '<div class="pitch-box"><p>Pitch Opener</p><div id="pitch-' + id + '">' + (r.pitch_opener||'—') + '</div></div>';

      body.appendChild(left);
      body.appendChild(right);
      card.appendChild(body);

      // Actions
      var actions = document.createElement('div');
      actions.className = 'actions';

      var cpBtn = document.createElement('button');
      cpBtn.className = 'g';
      cpBtn.textContent = 'Copy Pitch';
      cpBtn.onclick = function() {
        var el = document.getElementById('pitch-' + id);
        if (el) navigator.clipboard.writeText(el.textContent);
        cpBtn.textContent = 'Copied!';
        setTimeout(function() { cpBtn.textContent = 'Copy Pitch'; }, 1800);
      };
      actions.appendChild(cpBtn);

      if (site) {
        var siteBtn = document.createElement('button');
        siteBtn.textContent = 'Visit Site';
        siteBtn.onclick = function() { window.open(site, '_blank'); };
        actions.appendChild(siteBtn);
      }
      var liUrl = safeUrl(s.linkedin);
      if (liUrl) {
        var liBtn = document.createElement('button');
        liBtn.textContent = 'LinkedIn';
        liBtn.onclick = function() { window.open(liUrl, '_blank'); };
        actions.appendChild(liBtn);
      }
      if (s.twitter && s.twitter !== 'null') {
        var twBtn = document.createElement('button');
        twBtn.textContent = 'Twitter';
        twBtn.onclick = function() { window.open('https://twitter.com/' + String(s.twitter).replace('@',''), '_blank'); };
        actions.appendChild(twBtn);
      }

      var rmBtn = document.createElement('button');
      rmBtn.textContent = 'Remove';
      rmBtn.style.marginLeft = 'auto';
      rmBtn.onclick = function() {
        DB = DB.filter(function(x) { return x._id !== id; });
        renderAll();
      };
      actions.appendChild(rmBtn);
      card.appendChild(actions);
    }

    container.appendChild(card);
  });
}

function exportCSV() {
  var headers = ['Company','Tagline','Website','Sector','HQ','Founded','Stage','Funding','Date','Lead Investor','Other Investors','Employees','Twitter','LinkedIn','Discord','Telegram','GitHub','Founders','Has CMO','Marketing Notes','Product','Community','Score','Label','Funded Signal','No CMO Signal','Pre-launch','Has Product','Small Team','Mktg Gap','Why Fit','Risks','Pitch','Decision Maker'];
  function esc(v) {
    var str = String(v == null ? '' : v).replace(/"/g, '""');
    return (str.indexOf(',') >= 0 || str.indexOf('\\n') >= 0) ? '"' + str + '"' : str;
  }
  var rows = DB.map(function(r) {
    var s = r.socials || {};
    var g = r.gtm_signals || {};
    var founders = (r.founders || []).map(function(f) { return f.name + ' (' + f.role + ')'; }).join('; ');
    return [r.company, r.tagline, r.website, r.sector, r.hq, r.founded, r.stage, r.funding_amount, r.funding_date, r.lead_investor, r.other_investors, r.employee_count, s.twitter, s.linkedin, s.discord, s.telegram, s.github, founders, r.has_cmo, r.marketing_notes, r.product_status, r.community_size, r.gtm_readiness_score, r.gtm_label, g.recently_funded, g.no_cmo, g.pre_launch_or_early, g.has_product, g.small_team, g.marketing_gap_visible, r.why_fit, r.risks, r.pitch_opener, r.decision_maker].map(esc).join(',');
  });
  var csv = [headers.join(',')].concat(rows).join('\\n');
  var a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv], {type: 'text/csv'}));
  a.download = 'gtm-leads.csv';
  a.click();
}
</script>
</body>
</html>"""

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
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get('Content-Length', 0))
        try:
            body = json.loads(self.rfile.read(length))
        except:
            self.respond({'error': 'Invalid JSON body'})
            return

        key = body.get('key', '').strip()
        company = body.get('company', '').strip()
        system = body.get('system', '')

        if not key:
            self.respond({'error': 'Missing API key'})
            return
        if not company:
            self.respond({'error': 'Missing company name'})
            return

        payload = json.dumps({
            'model': 'claude-haiku-4-5-20251001',
            'max_tokens': 1200,
            'system': system,
            'tools': [{'type': 'web_search_20250305', 'name': 'web_search'}],
            'messages': [{'role': 'user', 'content': 'Search the web and research this company thoroughly, then return the JSON profile: "' + company + '". Search for their website, funding, founders, team size, socials (Twitter, LinkedIn, Discord, GitHub), and whether they have a CMO.'}]
        }).encode('utf-8')

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': key,
                'anthropic-version': '2023-06-01'
            },
            method='POST'
        )
        try:
            messages = [{'role': 'user', 'content': 'Search the web and research this company thoroughly, then return the JSON profile: "' + company + '". Search for their website, funding, founders, team size, socials (Twitter, LinkedIn, Discord, GitHub), and whether they have a CMO.'}]
            final_text = ''
            for _ in range(10):  # agentic loop for web search
                req2 = urllib.request.Request(
                    'https://api.anthropic.com/v1/messages',
                    data=json.dumps({
                        'model': 'claude-haiku-4-5-20251001',
                        'max_tokens': 1200,
                        'system': system,
                        'tools': [{'type': 'web_search_20250305', 'name': 'web_search'}],
                        'messages': messages
                    }).encode('utf-8'),
                    headers={
                        'Content-Type': 'application/json',
                        'x-api-key': key,
                        'anthropic-version': '2023-06-01'
                    },
                    method='POST'
                )
                with urllib.request.urlopen(req2, timeout=90) as resp2:
                    data = json.loads(resp2.read())
                content = data.get('content', [])
                stop_reason = data.get('stop_reason', '')
                # collect any text
                for block in content:
                    if block.get('type') == 'text':
                        final_text = block.get('text', '')
                if stop_reason == 'end_turn':
                    break
                if stop_reason == 'tool_use':
                    # feed tool results back
                    messages.append({'role': 'assistant', 'content': content})
                    tool_results = []
                    for block in content:
                        if block.get('type') == 'tool_use':
                            tool_results.append({
                                'type': 'tool_result',
                                'tool_use_id': block['id'],
                                'content': [{'type': 'text', 'text': 'Search completed.'}]
                            })
                    messages.append({'role': 'user', 'content': tool_results})
                else:
                    break
            self.respond({'text': final_text})
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
    url = 'http://localhost:' + str(PORT)
    print('')
    print('  GTM Scout running at ' + url)
    print('  Press Ctrl+C to stop.')
    print('')
    # auto-open removed for web deployment
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Stopped.')
        sys.exit(0)
