/* Cart, add-to-cart and footer signup — Rustic Earth Tea & Spice Co. redesign.
   Concept by Stephen Fehon. */
(function () {
  'use strict';
  var KEY = 're-cart-v1';
  var ROOT = (document.body && document.body.dataset.root) || '';
  var SHOP = window.RE_SHOP || { email: 'rusticearthcompany@gmail.com', phone: '856-259-3498', freeAt: 75 };
  var FREE = SHOP.freeAt || 75;

  function load() {
    try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch (e) { return []; }
  }
  function save(c) {
    try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) {}
    sync();
  }
  function count(c) {
    c = c || load();
    return c.reduce(function (n, i) { return n + i.qty; }, 0);
  }
  function subtotal(c) {
    c = c || load();
    return c.reduce(function (n, i) { return n + i.qty * i.price; }, 0);
  }
  function money(n) { return '$' + n.toFixed(2); }

  /* ---------- header badge ---------- */
  function sync() {
    var n = count();
    document.querySelectorAll('[data-cart-count]').forEach(function (el) {
      el.textContent = n;
      el.hidden = n === 0;
    });
  }

  function add(item) {
    var c = load();
    var ex = null;
    for (var k = 0; k < c.length; k++) if (c[k].id === item.id) ex = c[k];
    if (ex) ex.qty += item.qty; else c.push(item);
    save(c);
    return c;
  }

  /* ---------- product page ---------- */
  function initProduct() {
    var form = document.querySelector('[data-buyform]');
    if (!form || !window.RE_VARIANTS || !window.RE_VARIANTS.length) return;
    var vs = window.RE_VARIANTS;
    var sel = form.querySelector('[data-variant]');
    var qty = form.querySelector('[data-qty]');
    var addBtn = form.querySelector('[data-add]');
    var priceEl = form.querySelector('[data-addprice]');
    var pagePrice = document.querySelector('[data-price]');

    function current() {
      var id = sel ? sel.value : vs[0].id;
      for (var k = 0; k < vs.length; k++) if (vs[k].id === id) return vs[k];
      return vs[0];
    }
    function refresh() {
      var v = current();
      var out = v.soldOut;
      if (addBtn) {
        addBtn.disabled = out;
        if (priceEl) priceEl.textContent = out ? 'Sold out' : v.fmt;
      }
    }
    if (sel) {
      sel.addEventListener('change', function () {
        refresh();
        var v = current();
        if (pagePrice && vs.length > 1) pagePrice.textContent = v.fmt;
      });
    }
    form.querySelectorAll('[data-q]').forEach(function (b) {
      b.addEventListener('click', function () {
        var n = Math.max(1, (parseInt(qty.value, 10) || 1) + parseInt(b.dataset.q, 10));
        qty.value = n;
      });
    });
    qty.addEventListener('change', function () {
      var n = parseInt(qty.value, 10);
      if (!n || n < 1) qty.value = 1;
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var v = current();
      if (v.soldOut) return;
      var item = {
        id: v.id, slug: window.RE_ITEM.slug, name: window.RE_ITEM.name,
        variant: vs.length > 1 ? v.name : '', sku: v.sku,
        price: v.price, qty: Math.max(1, parseInt(qty.value, 10) || 1),
        img: window.RE_ITEM.img
      };
      add(item);
      openDrawer();
    });
    refresh();
  }

  /* ---------- drawer ---------- */
  function buildDrawer() {
    if (document.getElementById('reDrawer')) return;
    var w = document.createElement('div');
    w.id = 'reDrawer';
    w.className = 'drawer-wrap';
    w.hidden = true;
    w.innerHTML =
      '<div class="drawer-backdrop" data-dclose></div>' +
      '<div class="drawer" role="dialog" aria-label="Your cart">' +
      '  <div class="drawer-head"><h2>Your cart</h2>' +
      '    <button class="drawer-close" data-dclose aria-label="Close cart">&times;</button></div>' +
      '  <div class="drawer-lines" data-dlines></div>' +
      '  <div class="drawer-foot">' +
      '    <div class="drawer-sub"><span>Subtotal</span><strong data-dsub>$0.00</strong></div>' +
      '    <p class="drawer-note" data-dnote></p>' +
      '    <a class="btn btn-primary drawer-go" href="' + ROOT + 'cart.html">Go to cart</a>' +
      '    <button class="drawer-keep" data-dclose>Keep shopping</button>' +
      '  </div>' +
      '</div>';
    document.body.appendChild(w);
    w.addEventListener('click', function (e) {
      if (e.target.closest('[data-dclose]')) closeDrawer();
      var rm = e.target.closest('[data-drm]');
      if (rm) { var c = load(); var id = rm.getAttribute('data-drm'); c = c.filter(function (i) { return i.id !== id; }); save(c); draw(); }
      var minus = e.target.closest('[data-dminus]');
      if (minus) { bump(minus.getAttribute('data-dminus'), -1); }
      var plus = e.target.closest('[data-dplus]');
      if (plus) { bump(plus.getAttribute('data-dplus'), 1); }
    });
  }
  function bump(id, d) {
    var c = load();
    for (var k = 0; k < c.length; k++) {
      if (c[k].id === id) {
        c[k].qty += d;
        if (c[k].qty < 1) c.splice(k, 1);
        break;
      }
    }
    save(c); draw();
  }
  function lineHTML(i, page) {
    var opt = i.variant ? ' <span class="line-var">(' + esc(i.variant) + ')</span>' : '';
    var img = i.img ? '<img src="' + ROOT + i.img + '" alt="" loading="lazy">' : '';
    return '<div class="line">' +
      '<a class="line-thumb" href="' + ROOT + 'products/' + i.slug + '/">' + img + '</a>' +
      '<div class="line-main"><a class="line-name" href="' + ROOT + 'products/' + i.slug + '/">' + esc(i.name) + opt + '</a>' +
      '<span class="line-price">' + money(i.price) + (i.sku ? ' &middot; sku ' + esc(i.sku) : '') + '</span>' +
      '<div class="line-qty"><button data-dminus="' + i.id + '" aria-label="Decrease">&minus;</button>' +
      '<span>' + i.qty + '</span>' +
      '<button data-dplus="' + i.id + '" aria-label="Increase">+</button>' +
      (page ? '<button class="line-rm" data-drm="' + i.id + '">Remove</button>' : '') +
      '</div></div>' +
      '<strong class="line-total">' + money(i.price * i.qty) + '</strong></div>';
  }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (m) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]; }); }
  function draw() {
    var lines = document.querySelector('[data-dlines]');
    if (lines) {
      var c = load();
      lines.innerHTML = c.length ? c.map(function (i) { return lineHTML(i, false); }).join('')
        : '<p class="drawer-empty">Your cart is empty.</p>';
      var sub = document.querySelector('[data-dsub]');
      if (sub) sub.textContent = money(subtotal(c));
      var note = document.querySelector('[data-dnote]');
      if (note) {
        var t = subtotal(c);
        note.textContent = t >= FREE ? 'Free shipping unlocked.' : (money(FREE - t) + ' away from free shipping.');
      }
    }
  }
  function openDrawer() {
    buildDrawer(); draw();
    var w = document.getElementById('reDrawer');
    w.hidden = false;
    requestAnimationFrame(function () { w.classList.add('open'); });
    document.body.style.overflow = 'hidden';
  }
  function closeDrawer() {
    var w = document.getElementById('reDrawer');
    if (!w) return;
    w.classList.remove('open');
    document.body.style.overflow = '';
    setTimeout(function () { w.hidden = true; }, 260);
  }

  /* ---------- cart page ---------- */
  function initCartPage() {
    var root = document.getElementById('cartRoot');
    if (!root) return;
    var side = document.getElementById('cartSide');
    function render() {
      var c = load();
      if (!c.length) {
        root.innerHTML = '<p class="cart-empty">Your cart is empty. <a href="' + ROOT + 'shop/all-items.html">Browse the shelves</a> and fill it up.</p>';
        if (side) side.hidden = true;
        var st = document.querySelector('[data-shiptrack]');
        if (st) st.hidden = true;
        return;
      }
      root.innerHTML = c.map(function (i) { return lineHTML(i, true); }).join('');
      c.forEach(function (i) {
        var btn = root.querySelector('[data-drm="' + i.id + '"]');
        var lineEl = btn && btn.closest('.line');
        if (lineEl) sqForLine(lineEl, i);
      });
      if (side) {
        side.hidden = false;
        var subEl = document.querySelector('[data-subtotal]');
        if (subEl) subEl.textContent = money(subtotal(c));
        var t = subtotal(c);
        var track = document.querySelector('[data-shiptrack]');
        if (track) {
          track.hidden = false;
          var bar = document.querySelector('[data-shipbar]');
          var msg = document.querySelector('[data-shipmsg]');
          var pct = Math.min(100, Math.round(t / FREE * 100));
          if (bar) bar.style.width = pct + '%';
          if (msg) msg.textContent = t >= FREE ? 'You have unlocked free shipping.' : money(FREE - t) + ' more for free shipping.';
        }
      }
    }
    root.addEventListener('click', function (e) {
      var rm = e.target.closest('[data-drm]');
      if (rm) { save(load().filter(function (i) { return i.id !== rm.getAttribute('data-drm'); })); render(); }
      var minus = e.target.closest('[data-dminus]');
      if (minus) { bump(minus.getAttribute('data-dminus'), -1); render(); }
      var plus = e.target.closest('[data-dplus]');
      if (plus) { bump(plus.getAttribute('data-dplus'), 1); render(); }
    });
    var place = document.querySelector('[data-place]');
    if (place) place.addEventListener('click', placeOrder);
    render();
  }

  function placeOrder() {
    var c = load();
    if (!c.length) return;
    var name = (document.querySelector('[data-cname]') || {}).value || '';
    var contact = (document.querySelector('[data-ccontact]') || {}).value || '';
    var rows = c.map(function (i, k) {
      return (k + 1) + '. ' + i.qty + ' x ' + i.name + (i.variant ? ' (' + i.variant + ')' : '') +
        (i.sku ? ' [sku ' + i.sku + ']' : '') + ' - ' + money(i.price * i.qty);
    });
    var body =
      'Hello Rustic Earth,\n\n' +
      'I would like to place this order from your website:\n\n' +
      rows.join('\n') + '\n\n' +
      'Subtotal: ' + money(subtotal(c)) + '\n' +
      (subtotal(c) >= FREE ? 'Qualifies for free shipping (over $75).\n' : '') + '\n' +
      (name ? 'Name: ' + name + '\n' : '') +
      (contact ? 'Phone or email: ' + contact + '\n' : '') +
      '\nPlease reply to confirm stock and arrange payment and pickup or shipping.\n\nThank you!';
    var subject = 'Web order' + (name ? ' from ' + name : '') + ' - ' + money(subtotal(c));
    var href = 'mailto:' + SHOP.email + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
    window.location.href = href;
  }

  /* ---------- footer signup ---------- */
  function initLoop() {
    document.querySelectorAll('[data-loop]').forEach(function (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        var email = (form.querySelector('input[name="email"]') || {}).value || '';
        if (!email) return;
        var note = document.querySelector('[data-loop-note]');
        var href = 'mailto:' + SHOP.email +
          '?subject=' + encodeURIComponent('Newsletter signup: ' + email) +
          '&body=' + encodeURIComponent('Please add ' + email + ' to the shop newsletter. Thanks!');
        window.location.href = href;
        if (note) note.hidden = false;
        form.reset();
      });
    });
  }


  /* ---------- Square checkout links ---------- */
  var SQ = window.RE_SQUARE_LINKS || {};
  function initSquare() {
    var box = document.querySelector('.buy-box');
    if (box) {
      var btn = document.createElement('button');
      btn.className = 'btn btn-ghost sq-buy';
      btn.hidden = true;
      btn.type = 'button';
      btn.addEventListener('click', function () {
        if (btn.dataset.href) window.open(btn.dataset.href, '_blank', 'noopener');
      });
      box.appendChild(btn);
      function upd() {
        var sel = box.querySelector('[data-variant]');
        var v = sel ? (RE_VARIANTS || []).filter(function (x) { return x.id === sel.value; })[0] : (RE_VARIANTS || [])[0];
        var link = v && SQ[v.sku];
        if (link) { btn.hidden = false; btn.dataset.href = link; btn.textContent = 'Buy with Square'; }
        else { btn.hidden = true; }
      }
      box.addEventListener('change', upd);
      upd();
    }
  }
  function sqForLine(rootEl, item) {
    var link = SQ[item.sku];
    if (!link) return;
    var anchor = document.createElement('a');
    anchor.className = 'sq-pay';
    anchor.href = link;
    anchor.target = '_blank';
    anchor.rel = 'noopener';
    anchor.textContent = 'Pay with Square';
    var total = rootEl.querySelector('.line-total');
    if (total) total.parentNode.insertBefore(anchor, total);
  }
  function init() {
    document.documentElement.classList.remove('no-js');
    sync();
    initProduct();
    initSquare();
    initCartPage();
    initLoop();
    buildDrawer();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

/* fly-to-cart polish - item thumbnail arcs into the cart button (concept by Stephen Fehon) */
(function () {
  'use strict';
  document.addEventListener('click', function (e) {
    var b = e.target.closest('.buy-box button');
    if (!b || b.classList.contains('sq-buy') || !b.querySelector('[data-addprice]')) return;
    var cart = document.querySelector('.cart-btn'); if (!cart) return;
    var src = document.querySelector('.pd-media img') || document.querySelector('.pd-media .cat-art svg');
    var r = (src ? src.getBoundingClientRect() : b.getBoundingClientRect());
    var c = cart.getBoundingClientRect();
    var fly = document.createElement('div'); fly.className = 'fly';
    if (src && src.tagName === 'IMG') {
      var im = document.createElement('img'); im.src = src.currentSrc || src.src; im.alt = '';
      fly.appendChild(im);
    }
    fly.style.left = (r.left + r.width / 2 - 28) + 'px';
    fly.style.top = (r.top + r.height / 2 - 28) + 'px';
    document.body.appendChild(fly);
    requestAnimationFrame(function () { requestAnimationFrame(function () {
      fly.style.transform = 'translate(' + (c.left + c.width / 2 - (r.left + r.width / 2)) + 'px,' + (c.top + c.height / 2 - (r.top + r.height / 2)) + 'px) scale(.18)';
      fly.style.opacity = '.25';
    }); });
    setTimeout(function () {
      fly.remove();
      document.querySelectorAll('[data-cart-count]').forEach(function (el) {
        el.classList.remove('pop'); void el.offsetWidth; el.classList.add('pop');
      });
    }, 650);
  });
})();
