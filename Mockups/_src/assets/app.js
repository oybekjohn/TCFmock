/* =====================================================================
   app.js — mockup interaktivligi (barcha sahifalar uchun umumiy)
   ===================================================================== */
(function () {
  'use strict';
  var LANGS = ['uz', 'ru', 'fr', 'en'];
  var DICT = window.I18N || null;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  /* ---------- 1. Til (UZ / RU / FR / EN) ---------- */
  function applyLang(l) {
    if (!DICT) return;
    if (LANGS.indexOf(l) < 0) l = 'uz';
    var d = DICT[l] || {};
    document.documentElement.lang = l;
    $$('[data-i18n]').forEach(function (el) {
      var v = d[el.getAttribute('data-i18n')]; if (v === undefined) return;
      var a = el.getAttribute('data-i18n-attr');
      if (a) el.setAttribute(a, v); else if (el.tagName === 'TITLE') document.title = v; else el.textContent = v;
    });
    $$('[data-i18n-html]').forEach(function (el) {
      var v = d[el.getAttribute('data-i18n-html')]; if (v !== undefined) el.innerHTML = v;
    });
    $$('.lang__code').forEach(function (el) { el.textContent = l.toUpperCase(); });
    $$('.lang__menu button').forEach(function (b) { b.classList.toggle('is-active', b.dataset.lang === l); });
    store('tcf_lang', l);
  }
  if (DICT) {
    var saved = store('tcf_lang');
    var nav = (navigator.language || '').slice(0, 2).toLowerCase();
    applyLang(LANGS.indexOf(saved) >= 0 ? saved : (LANGS.indexOf(nav) >= 0 ? nav : 'uz'));
  }
  document.addEventListener('click', function (e) {
    var t = e.target;
    var langBtn = t.closest('.lang__btn');
    $$('.lang.is-open').forEach(function (x) { if (!langBtn || !x.contains(langBtn)) x.classList.remove('is-open'); });
    if (langBtn) { langBtn.parentNode.classList.toggle('is-open'); return; }
    var pick = t.closest('.lang__menu button[data-lang]');
    if (pick) { applyLang(pick.dataset.lang); return; }

    /* ---------- 2. Menyu (burger) ---------- */
    if (t.closest('#burger')) { $('#nav').classList.toggle('is-open'); return; }
    if (t.closest('#admBurger')) { $('.adm').classList.toggle('is-menu'); return; }
    if (t.closest('#nav .nav__links a')) $('#nav').classList.remove('is-open');

    /* ---------- 3. Modal oynalar ---------- */
    var op = t.closest('[data-open]');
    if (op) { e.preventDefault(); var m = document.getElementById(op.dataset.open); if (m) m.classList.add('is-open'); return; }
    if (t.closest('[data-close]') || t.classList.contains('modal')) {
      var mm = t.closest('.modal'); if (mm) mm.classList.remove('is-open'); return;
    }

    /* ---------- 4. Javob variantlari ---------- */
    var opt = t.closest('.opt, .x-img-opt');
    if (opt) {
      $$('.opt, .x-img-opt', opt.parentNode).forEach(function (o) { o.classList.remove('is-sel'); });
      opt.classList.add('is-sel');
      var nx = $('[data-needs-answer]'); if (nx) nx.disabled = false;
      return;
    }

    /* ---------- 5. Tablar, segmentlar, tez tanlov ---------- */
    var tab = t.closest('[data-tab]');
    if (tab) {
      var box = tab.closest('[data-tabs]');
      var own = function (el) { return el.closest('[data-tabs]') === box; };
      $$('[data-tab]', box).filter(own).forEach(function (b) { b.classList.toggle('is-active', b === tab); });
      $$('[data-pane]', box).filter(own).forEach(function (p) { p.hidden = p.dataset.pane !== tab.dataset.tab; });
      return;
    }
    var seg = t.closest('.seg button, .quick button');
    if (seg) {
      $$('button', seg.parentNode).forEach(function (b) { b.classList.toggle('is-active', b === seg); });
      if (seg.dataset.val && seg.parentNode.dataset.target) { var inp = document.getElementById(seg.parentNode.dataset.target); if (inp) inp.value = seg.dataset.val; }
      return;
    }

    /* ---------- 6. Parolni ko'rsatish ---------- */
    var pw = t.closest('.pw button');
    if (pw) { var i = $('input', pw.parentNode); i.type = i.type === 'password' ? 'text' : 'password'; return; }

    /* ---------- 7. Ovoz tekshiruvi ---------- */
    var snd = t.closest('[data-sound-test]');
    if (snd) { snd.classList.add('is-disabled'); setTimeout(function () { snd.classList.remove('is-disabled'); var ok = $('#soundOk'); if (ok) ok.hidden = false; }, 1600); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') $$('.modal.is-open, .lang.is-open').forEach(function (m) { m.classList.remove('is-open'); });
  });

  /* ---------- 8. Mock formalar (serverga yubormaydi) ---------- */
  $$('form[data-mock]').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var msg = $('.alert[data-msg]', f); if (msg) msg.hidden = false;
      var go = f.dataset.mock; if (go && go !== 'stay') setTimeout(function () { location.href = go; }, 700);
    });
  });

  /* ---------- 9. Telefon maskasi: +998 XX XXX XX XX ---------- */
  $$('input[type=tel]').forEach(function (inp) {
    inp.addEventListener('input', function () {
      var d = inp.value.replace(/\D/g, ''); if (!d) { inp.value = ''; return; }
      if (d.indexOf('998') === 0) d = d.slice(3); d = d.slice(0, 9);
      var o = '+998'; if (d.length) o += ' ' + d.slice(0, 2); if (d.length > 2) o += ' ' + d.slice(2, 5);
      if (d.length > 5) o += ' ' + d.slice(5, 7); if (d.length > 7) o += ' ' + d.slice(7, 9);
      inp.value = o;
    });
    inp.addEventListener('focus', function () { if (!inp.value) inp.value = '+998 '; });
  });

  /* ---------- 10. Imtihon taymeri (teskari sanoq) ---------- */
  $$('.x-timer[data-sec]').forEach(function (el) {
    var s = +el.dataset.sec, out = $('b', el);
    function tick() {
      var m = Math.floor(s / 60), r = s % 60;
      out.textContent = (m < 10 ? '0' : '') + m + ':' + (r < 10 ? '0' : '') + r;
      el.classList.toggle('is-warn', s <= 300 && s > 60); el.classList.toggle('is-danger', s <= 60);
      if (s > 0) { s--; return; }
      var tu = document.getElementById('timeUp');
      if (tu && !tu.dataset.shown) { tu.dataset.shown = '1'; tu.classList.add('is-open'); }
    }
    tick(); setInterval(tick, 1000);
  });

  /* ---------- 11. CO: audio bir marta o'ynaydi (simulyatsiya) ---------- */
  function initAudio(root) {
    $$('.x-audio[data-dur]', root).forEach(function (box) {
      var dur = +box.dataset.dur, pos = +(box.dataset.pos || 0), bar = $('.x-audio__bar i', box), cur = $('[data-cur]', box);
      function fmt(x) { return '0:' + (x < 10 ? '0' : '') + x; }
      var id = setInterval(function () {
        pos++; if (bar) bar.style.width = Math.min(100, pos / dur * 100) + '%'; if (cur) cur.textContent = fmt(Math.min(pos, dur));
        if (pos >= dur) { clearInterval(id); box.classList.add('is-done'); }
      }, 1000);
    });
  }
  initAudio(document);

  /* ---------- 11b. Savollar ketma-ketligi (orqaga qaytib bo'lmaydi) ---------- */
  var quiz = $('[data-quiz]');
  if (quiz) {
    var slot = $('[data-q-slot]', quiz), tpls = $$('template[data-q]', quiz), step = 0;
    var total = +quiz.dataset.total, first = +quiz.dataset.first;
    var dots = $('.x-dots');
    function paintDots(n) {
      if (!dots) return; var h = '';
      for (var i = 1; i <= total; i++) h += '<i class="' + (i < n ? 'done' : i === n ? 'cur' : '') + '"></i>';
      dots.innerHTML = h;
    }
    paintDots(first);
    var confirmBtn = $('[data-confirm]');
    if (confirmBtn) confirmBtn.addEventListener('click', function () {
      if (step >= tpls.length) { location.href = quiz.dataset.end; return; }
      var t = tpls[step++];
      slot.innerHTML = t.innerHTML;
      var n = +t.dataset.q;
      $$('[data-qn]').forEach(function (el) { el.textContent = n; });
      paintDots(n);
      confirmBtn.disabled = true;
      if (DICT) applyLang(document.documentElement.lang);
      initAudio(slot);
      window.scrollTo(0, 0);
    });
  }

  /* ---------- 12. Joriy yil ---------- */
  $$('[data-year]').forEach(function (y) { y.textContent = new Date().getFullYear(); });
})();
