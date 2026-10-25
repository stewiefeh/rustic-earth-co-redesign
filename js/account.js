/* Account: sign in with just a phone number, order history, reorder.
   Rustic Earth Tea & Spice Co. redesign - concept by Stephen Fehon.
   Demo build: the account lives in this browser's storage. Live, the
   shop's platform sends the code by text and holds the orders. */
(function () {
  'use strict';
  var KEY = 're-account-v1';
  var ROOT = (document.body && document.body.dataset.root) || '';
  var user = load();
  var code = '';
  var pendingPhone = '';
  var modal = null;
  var lastFocus = null;

  var REG = 're-account-registry-v1';
  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || null; } catch (e) { return null; }
  }
  function registry() {
    try { return JSON.parse(localStorage.getItem(REG)) || {}; } catch (e) { return {}; }
  }
  function save() {
    try {
      if (user) {
        localStorage.setItem(KEY, JSON.stringify(user));
        var r = registry();
        r[user.phone] = user;
        localStorage.setItem(REG, JSON.stringify(r));
      } else {
        localStorage.removeItem(KEY);
      }
    } catch (e) {}
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; });
  }
  function digits(s) { return (s || '').replace(/\D/g, '').slice(0, 10); }
  function fmtPhone(d) {
    if (d.length <= 3) return d.length ? '(' + d : '';
    if (d.length <= 6) return '(' + d.slice(0, 3) + ') ' + d.slice(3);
    return '(' + d.slice(0, 3) + ') ' + d.slice(3, 6) + '-' + d.slice(6);
  }
  function fmtLong(p) {
    var d = (p || '').replace(/\D/g, '').replace(/^1/, '');
    return fmtPhone(d);
  }

  /* ---------- header button ---------- */
  function syncBtn() {
    document.querySelectorAll('[data-acct-btn]').forEach(function (b) {
      b.textContent = user ? 'Account' : 'Sign in';
    });
  }

  /* ---------- record an order (called by cart.js) ---------- */
  function recordOrder(items, total) {
    if (!user) return null;
    var o = {
      id: 'R' + Date.now().toString(36).toUpperCase(),
      placed: new Date().toISOString(),
      items: items.map(function (i) { return { id: i.id, name: i.name, variant: i.variant || '', price: i.price, sku: i.sku || '', qty: i.qty }; }),
      total: total,
      status: 'Waiting for confirmation'
    };
    user.orders.unshift(o);
    save();
    return o;
  }

  /* ---------- modal ---------- */
  function ensure() {
    if (modal) return modal;
    modal = document.createElement('div');
    modal.className = 'acct-wrap';
    modal.hidden = true;
    modal.innerHTML =
      '<div class="acct-backdrop"></div>' +
      '<div class="acct-modal" role="dialog" aria-modal="true" aria-label="Your account">' +
        '<img class="acct-mark" src="' + ROOT + 'images/logo-mark.png" alt="" width="44" height="44">' +
        '<button class="acct-x" type="button" aria-label="Close account">&times;</button>' +
        '<div class="acct-body"></div>' +
      '</div>';
    document.body.appendChild(modal);
    modal.querySelector('.acct-x').addEventListener('click', close);
    modal.querySelector('.acct-backdrop').addEventListener('click', close);
    modal.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { close(); return; }
      if (e.key !== 'Tab') return;
      var f = modal.querySelectorAll('button, input, a[href]');
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { last.focus(); e.preventDefault(); }
      else if (!e.shiftKey && document.activeElement === last) { first.focus(); e.preventDefault(); }
    });
    return modal;
  }

  function open(step) {
    ensure();
    lastFocus = document.activeElement;
    modal.hidden = false;
    document.documentElement.style.overflow = 'hidden';
    render(step || (user ? 'account' : 'welcome'));
  }
  function close() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    document.documentElement.style.overflow = '';
    if (lastFocus) lastFocus.focus();
  }

  var check = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="m8.2 12.3 2.5 2.6 5.1-5.6"/></svg>';

  function render(step) {
    var b = modal.querySelector('.acct-body');
    if (step === 'welcome') {
      b.innerHTML =
        '<h2>Sign in with just your phone number</h2>' +
        '<p class="acct-sub">No passwords. Your orders and details stay together.</p>' +
        '<ul class="acct-benefits">' +
          '<li>' + check + 'Your order history in one place</li>' +
          '<li>' + check + 'Reorder favorites in one tap</li>' +
          '<li>' + check + 'Contact details saved for faster checkout</li>' +
        '</ul>' +
        '<button class="acct-pill" type="button" data-act="to-phone">Sign in or sign up</button>' +
        '<p class="acct-demo">Demo sign-in: everything stays in this browser. Live, the shop\u2019s platform sends the code by text.</p>';
      b.querySelector('[data-act="to-phone"]').addEventListener('click', function () { render('phone'); });
    } else if (step === 'phone') {
      b.innerHTML =
        '<h2>Enter your phone number</h2>' +
        '<p class="acct-sub" id="acct-phone-help">We use it to tie your orders together.</p>' +
        '<div class="acct-phoneline"><span class="acct-cc">+1 (US)</span>' +
          '<input class="acct-input" type="tel" inputmode="tel" autocomplete="tel" placeholder="(555) 123-4567" aria-label="Phone number" aria-describedby="acct-phone-help"></div>' +
        '<div class="acct-row"><button class="acct-pill" type="button" data-act="send" disabled>Next</button>' +
        '<button class="acct-link" type="button" data-act="cancel">Cancel</button></div>';
      var inp = b.querySelector('.acct-input');
      var next = b.querySelector('[data-act="send"]');
      inp.focus();
      inp.addEventListener('input', function () {
        inp.value = fmtPhone(digits(inp.value));
        next.disabled = digits(inp.value).length !== 10;
      });
      inp.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !next.disabled) next.click(); });
      next.addEventListener('click', function () {
        pendingPhone = '+1' + digits(inp.value);
        code = String(Math.floor(100000 + Math.random() * 900000));
        render('code');
      });
      b.querySelector('[data-act="cancel"]').addEventListener('click', function () { render('welcome'); });
    } else if (step === 'code') {
      b.innerHTML =
        '<h2>Enter your code</h2>' +
        '<p class="acct-sub">Six digits to finish signing in.</p>' +
        '<input class="acct-input acct-code" type="text" inputmode="numeric" maxlength="6" autocomplete="one-time-code" aria-label="Six digit code" aria-describedby="acct-code-err">' +
        '<p class="acct-err" id="acct-code-err" role="alert" hidden>That code doesn\u2019t match. Try again.</p>' +
        '<p class="acct-demo">Demo mode shows your code here: <strong>' + code + '</strong>. Live, it arrives by text.</p>' +
        '<div class="acct-row"><button class="acct-pill" type="button" data-act="verify" disabled>Verify</button>' +
        '<button class="acct-link" type="button" data-act="back">Back</button></div>';
      var ci = b.querySelector('.acct-code');
      var ver = b.querySelector('[data-act="verify"]');
      var err = b.querySelector('.acct-err');
      ci.focus();
      ci.addEventListener('input', function () {
        ci.value = ci.value.replace(/\D/g, '').slice(0, 6);
        ver.disabled = ci.value.length !== 6;
        err.hidden = true;
      });
      ci.addEventListener('keydown', function (e) { if (e.key === 'Enter' && !ver.disabled) ver.click(); });
      ver.addEventListener('click', function () {
        if (ci.value !== code) { err.hidden = false; ci.setAttribute('aria-invalid', 'true'); ci.value = ''; ver.disabled = true; ci.focus(); return; }
        ci.removeAttribute('aria-invalid');
        var r = registry();
        user = r[pendingPhone] || { phone: pendingPhone, since: new Date().toISOString(), orders: [] };
        save(); syncBtn();
        render('account');
      });
      b.querySelector('[data-act="back"]').addEventListener('click', function () { render('phone'); });
    } else {
      var d = (user.phone || '').replace(/\D/g, '').replace(/^1/, '');
      var since = user.since ? new Date(user.since) : null;
      var months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
      var rows = (user.orders || []).map(function (o, k) {
        var dd = new Date(o.placed);
        var day = months[dd.getMonth()] + ' ' + dd.getDate() + ', ' + dd.getFullYear();
        var lead = o.items[0] ? esc(o.items[0].name) + (o.items[0].variant ? ' (' + esc(o.items[0].variant) + ')' : '') : '';
        var more = o.items.length > 1 ? ' +' + (o.items.length - 1) + ' more' : '';
        return '<div class="acct-order">' +
          '<div class="acct-omain"><strong>' + day + '</strong><span>' + lead + more + '</span></div>' +
          '<div class="acct-oside"><span class="acct-status">' + esc(o.status) + '</span>' +
          '<span class="acct-total">$' + o.total.toFixed(2) + '</span>' +
          '<button class="acct-pill acct-small" type="button" data-reorder="' + k + '">Reorder</button></div></div>';
      }).join('');
      b.innerHTML =
        '<h2>Your account</h2>' +
        '<p class="acct-sub">' + fmtLong(user.phone) + (since ? ' \u00b7 with the shop since ' + months[since.getMonth()] + ' ' + since.getFullYear() : '') + '</p>' +
        '<h3>Order history</h3>' +
        (rows || '<p class="acct-empty">No orders yet. Place one and it lands here.</p>') +
        '<button class="acct-link acct-out" type="button" data-act="out">Sign out</button>';
      b.querySelectorAll('[data-reorder]').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var o = user.orders[+btn.getAttribute('data-reorder')];
          if (!o) return;
          (o.items || []).forEach(function (it) { if (window.RE_CART) window.RE_CART.add(it); });
          close();
        });
      });
      b.querySelector('[data-act="out"]').addEventListener('click', function () {
        user = null; save(); syncBtn(); render('welcome');
      });
    }
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-acct-btn]');
    if (btn) open();
  });

  window.RE_ACCT = { user: function () { return user; }, recordOrder: recordOrder };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', syncBtn);
  else syncBtn();
})();
