// Wavu scrape, browser half. tools/wavu_snapshot.py is the offline half.
//
// Wavu sits behind Anubis, so this runs inside a real wavu.wiki tab (Claude in
// Chrome): open any wavu.wiki page, wait for the challenge to clear, paste this
// file into the page, then
//
//     await TK8.grab('Bob'); await TK8.grab('Roger_Jr.');   // Wavu page names
//     TK8.button();   // click the red button: copies TK8.data to the clipboard
//     await TK8.grabTens('Paul'); TK8.button('tens');   // ten-string wikitables
//
// and save the clipboard (PowerShell `Get-Clipboard -Raw`) as RAW.json for
// `python tools/wavu_snapshot.py RAW.json Bob=bob ...`. The clipboard is the
// only exit that works: Chrome blocks a localhost POST from the page, and a
// second automatic download trips the multiple-downloads prompt. Copying needs
// a real click (user activation), hence the button. Do not navigate the tab
// between grabs -- everything lives on `window`.
//
// Fields are kept raw (lead/tail split, zero-width characters stripped); the
// Python half owns every decision about joining, glued chains and duplicates.
(() => {
  const ZW = /[​‌‍﻿]/g;
  const clean = s => (s || '').replace(ZW, '').replace(/\s+/g, ' ').trim();
  const noUrl = s => (s || '').replace(/https?:\/\/\S+/g, '');
  const txt = (root, sel) => { const e = root.querySelector(sel); return e ? clean(e.textContent) : ''; };
  const headingText = h => clean((h.querySelector('.mw-headline') || h).textContent).replace(/\[edit\]$/, '').trim();

  async function fetchDoc(path) {
    const r = await fetch(path, { credentials: 'same-origin' });
    if (!r.ok) throw new Error(path + ' ' + r.status);
    return new DOMParser().parseFromString(await r.text(), 'text/html');
  }

  // movedata cards in document order; section = nearest h2/h3 (throw
  // sub-sections such as "Command Throws" are h3)
  function movelist(doc) {
    const out = [];
    let section = '';
    for (const el of doc.querySelectorAll('h2, h3, .movedata')) {
      if (el.tagName === 'H2' || el.tagName === 'H3') { section = headingText(el); continue; }
      if (!el.id) continue; // the column-legend card has no id
      const altEl = el.querySelector('.movedata-alt');
      const alt = altEl ? clean(altEl.textContent) : '';
      out.push({
        id: el.id,
        section,
        name: txt(el, '.movedata-name'),
        alt: alt ? [alt] : [],
        number: txt(el, '.movedata-num'),
        inputLead: txt(el, '.movedata-inputLead'),
        displayed_input: txt(el, '.movedata-input'),
        targetLead: txt(el, '.movedata-targetLead'),
        targetTail: txt(el, '.movedata-target'),
        damageLead: txt(el, '.movedata-damageLead'),
        damageTail: txt(el, '.movedata-damage'),
        range: txt(el, '.movedata-range'),
        block: txt(el, '.movedata-block'),
        hit: txt(el, '.movedata-hit'),
        counter_hit: txt(el, '.movedata-ch'),
        startupRoot: txt(el, '.movedata-startupRoot'),
        startup: txt(el, '.movedata-startup'),
        states: txt(el, '.movedata-crush'),
        recovery: txt(el, '.movedata-recv-ctn'),
        notes: txt(el, '.movedata-notes'),
        alias: txt(el, '.movedata-alias'),
      });
    }
    return out;
  }

  // combo pages are definition lists: dt = starter, dd = route; a dd takes the
  // most recent dt of its own dl (or none). Bare URLs from video links are
  // stripped -- they used to land in route text as unbreakable literals.
  function combos(doc) {
    const root = doc.querySelector('.mw-parser-output') || doc.body;
    const out = [];
    let cur = null;
    for (const el of root.querySelectorAll('h2, h3, h4, dl')) {
      if (/^H[234]$/.test(el.tagName)) {
        cur = { section: headingText(el), level: el.tagName, dls: [] };
        out.push(cur);
        continue;
      }
      if (!cur || (el.parentElement && el.parentElement.closest('dl'))) continue;
      cur.dls.push([...el.querySelectorAll(':scope > dt, :scope > dd')]
        .map(x => [x.tagName.toLowerCase(), clean(noUrl(x.textContent))]));
    }
    return out;
  }

  window.TK8 = window.TK8 || { data: {} };
  window.TK8.grab = async page => {
    const ml = await fetchDoc('/t/' + page + '_movelist');
    await new Promise(r => setTimeout(r, 1300));
    const cb = await fetchDoc('/t/' + page + '_combos');
    window.TK8.data[page] = { page, moves: movelist(ml), combos2: combos(cb) };
    return [page, window.TK8.data[page].moves.length, window.TK8.data[page].combos2.length];
  };
  // Ten-strings moved from move cards into wikitables on most pages (2026-11).
  // The tables only exist on the movelist page; keep them raw per section.
  window.TK8.tens = window.TK8.tens || {};
  window.TK8.grabTens = async page => {
    const doc = await fetchDoc('/t/' + page + '_movelist');
    const tables = [];
    let section = '';
    for (const el of doc.querySelectorAll('h2, h3, table.wikitable')) {
      if (el.tagName !== 'TABLE') { section = headingText(el); continue; }
      tables.push({ section, rows: [...el.querySelectorAll('tr')].map(tr =>
        [...tr.querySelectorAll('th, td')].map(c => [c.tagName.toLowerCase(), clean(c.textContent)])) });
    }
    window.TK8.tens[page] = tables;
    return [page, tables.length];
  };
  window.TK8.button = (what = 'data') => {
    let b = document.getElementById('tk8copy');
    if (!b) {
      b = document.createElement('button');
      b.id = 'tk8copy';
      b.style.cssText = 'position:fixed;top:10px;left:10px;z-index:999999;font-size:28px;padding:20px 40px;background:#c00;color:#fff';
      b.onclick = async () => {
        const json = JSON.stringify(window.TK8[b.dataset.what]);
        await navigator.clipboard.writeText(json);
        b.textContent = 'COPIED ' + json.length;
      };
      document.body.appendChild(b);
    }
    b.dataset.what = what;
    b.textContent = 'COPY TK8.' + what;
    return 'button ready';
  };
  return 'TK8 ready';
})();
