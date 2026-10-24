/* Rustic Earth Tea & Spice Co. — redesign · concept by Stephen Fehon */
(function () {
  var html = document.documentElement;
  html.classList.add('js');

  /* header state */
  var head = document.getElementById('siteHead');
  function onScroll() {
    if (head) head.classList.toggle('scrolled', window.scrollY > 40);
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* scroll reveals: CSS view-timeline where supported, IO fallback elsewhere */
  var reveals = [].slice.call(document.querySelectorAll('.reveal'));
  if (reveals.length) {
    var supported = false;
    try { supported = CSS.supports('animation-timeline', 'view()'); } catch (e) {}
    if (!supported && 'IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) {
            en.target.classList.add('done');
            io.unobserve(en.target);
          }
        });
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
      reveals.forEach(function (el) { io.observe(el); });
    } else if (!supported) {
      reveals.forEach(function (el) { el.classList.add('done'); });
    }
  }

  /* category sub-filter chips */
  var chips = [].slice.call(document.querySelectorAll('.chip[data-sub]'));
  if (chips.length) {
    var cards = [].slice.call(document.querySelectorAll('[data-subcat]'));
    var count = document.getElementById('resultCount');
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        chips.forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
        var sub = chip.getAttribute('data-sub');
        var shown = 0;
        cards.forEach(function (card) {
          var show = sub === 'all' || card.getAttribute('data-subcat') === sub;
          card.style.display = show ? '' : 'none';
          if (show) shown++;
        });
        if (count) count.textContent = shown + ' item' + (shown === 1 ? '' : 's');
      });
    });
  }

  /* open-now badges. Hours data attr: JSON list of {d:[days],o:start,h:end} in 24h */
  document.querySelectorAll('[data-hours]').forEach(function (el) {
    try {
      var spec = JSON.parse(el.getAttribute('data-hours'));
      var now = new Date();
      var day = now.getDay();           /* 0 Sun .. 6 Sat */
      var mins = now.getHours() * 60 + now.getMinutes();
      var today = null;
      for (var i = 0; i < spec.length; i++) {
        if (spec[i].d.indexOf(day) !== -1) { today = spec[i]; break; }
      }
      var open = false, nextTxt = '';
      if (today && mins >= today.o && mins < today.c) {
        open = true;
      } else if (today && mins < today.o) {
        nextTxt = 'Opens today at ' + fmt(today.o);
      } else {
        /* find next open day */
        for (var k = 1; k <= 7; k++) {
          var d2 = (day + k) % 7;
          for (var j = 0; j < spec.length; j++) {
            if (spec[j].d.indexOf(d2) !== -1) {
              var names = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
              nextTxt = (k === 1 ? 'Opens tomorrow' : 'Opens ' + names[d2]) + ' at ' + fmt(spec[j].o);
              k = 8; break;
            }
          }
        }
      }
      var badge = document.createElement('span');
      badge.className = 'open-badge ' + (open ? 'open' : 'closed');
      badge.textContent = open ? 'Open now' : (nextTxt || 'Closed today');
      var host = el.getAttribute('data-badge-host');
      if (host) {
        var t = el.matches(host) ? el : el.querySelector(host);
        if (!t && el.parentElement) t = el.parentElement.querySelector(host);
        if (t) t.appendChild(badge); else el.appendChild(badge);
      } else {
        el.appendChild(badge);
      }
      if (today) {
        var rows = el.querySelectorAll ? el.querySelectorAll('[data-dow]') : [];
        for (var r = 0; r < rows.length; r++) {
          var dows = (rows[r].getAttribute('data-dow') || '').split(',').map(Number);
          if (dows.indexOf(day) !== -1) rows[r].classList.add('today');
        }
      }
    } catch (e) {}
    function fmt(m) {
      var h = Math.floor(m / 60), mm = m % 60, ap = h >= 12 ? 'pm' : 'am';
      h = h % 12; if (h === 0) h = 12;
      return h + (mm ? ':' + ('0' + mm).slice(-2) : '') + ap;
    }
  });
})();
