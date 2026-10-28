/* Rustic Earth Tea & Spice Co. — redesign · concept by Stephen Fehon */
(function () {
  var html = document.documentElement;
  html.classList.add('js');
  html.classList.remove('no-js');

  /* header state + scroll progress (CSS-driven where supported, JS fallback) */
  var head = document.getElementById('siteHead');
  var cssScroll = false;
  try { cssScroll = window.CSS && CSS.supports('animation-timeline', 'scroll()'); } catch (e) {}
  var bar = document.createElement('div');
  bar.id = 'scrollBar'; document.body.appendChild(bar);
  var lastY = window.scrollY;
  function onScroll() {
    var y = window.scrollY;
    var max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    if (!cssScroll) bar.style.transform = 'scaleX(' + Math.min(1, y / max) + ')';
    if (head) {
      head.classList.toggle('scrolled', y > 40);
      if (y > 160 && y > lastY + 2) head.classList.add('hid');
      else if (y < lastY - 2 || y <= 160) head.classList.remove('hid');
    }
    lastY = y;
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* scroll reveals: modern browsers run them as per-element CSS
     scroll-driven animations (no JS); elsewhere an IO pass does it.
     .settled drops the fallback transition once the settle has run so
     hover transitions take back over */
  var reveals = [].slice.call(document.querySelectorAll('.reveal'));
  if (reveals.length && 'IntersectionObserver' in window) {
    var seen = new Map();
    reveals.forEach(function (el) {
      var p = el.parentElement, n = seen.get(p) || 0;
      seen.set(p, n + 1);
      el.style.setProperty('--di', Math.min(n - 1, 6));
    });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add('done');
          var di = parseFloat(en.target.style.getPropertyValue('--di')) || 0;
          setTimeout(function () { en.target.classList.add('settled'); }, 750 + di * 70);
          io.unobserve(en.target);
        }
      });
    }, { rootMargin: '0px 0px 10% 0px', threshold: 0 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add('done', 'settled'); });
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
        var shown = 0, si = 0;
        var calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        cards.forEach(function (card) {
          var show = sub === 'all' || card.getAttribute('data-subcat') === sub;
          card.style.display = show ? '' : 'none';
          if (show) {
            if (!calm && card.animate) {
              card.animate(
                [{ opacity: 0, transform: 'translateY(14px)' }, { opacity: 1, transform: 'none' }],
                { duration: 420, delay: Math.min(si, 8) * 45, easing: 'cubic-bezier(.2,.75,.25,1.05)', fill: 'backwards' }
              );
            }
            si++; shown++;
          }
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

/* motion polish - stagger reveals and fade product images in (concept by Stephen Fehon) */
(function () {
  var run = function () {
    document.querySelectorAll('.p-thumb img, .pd-photo img').forEach(function (im) {
      if (im.complete && im.naturalWidth > 0) { im.classList.add('ld'); return; }
      im.addEventListener('load', function () { im.classList.add('ld'); });
      im.addEventListener('error', function () { im.classList.add('ld'); });
    });
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
  else run();
})();

/* motion pass two - ingredients ribbon, condensed header, magnetic buttons (concept by Stephen Fehon) */
(function () {
  var fine = window.matchMedia && window.matchMedia('(pointer: fine)').matches;
  var calm = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var run = function () {
    var hero = document.querySelector('.hero');
    if (hero && !document.querySelector('.ribbon')) {
      var words = ['Loose-leaf tea', 'House spice blends', 'Flavored sea salts', 'Aged balsamic', 'Local raw honey', 'Small-batch coffee', 'Craft snack sticks'];
      var leaf = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21c-5-6-8-9-8-13a8 8 0 0 1 16 0c0 4-3 7-8 13Z" fill="none" stroke="#A6472E" stroke-width="2"/></svg>';
      var group = '';
      for (var i = 0; i < words.length; i++) group += leaf + '<em>' + words[i] + '</em>';
      var ribbon = document.createElement('div');
      ribbon.className = 'ribbon'; ribbon.setAttribute('aria-hidden', 'true');
      ribbon.innerHTML = '<div class="ribbon-track">' + group + group + '</div>';
      hero.parentNode.insertBefore(ribbon, hero.nextSibling);
    }
    if (fine && !calm) {
      document.querySelectorAll('.btn-primary').forEach(function (btn) {
        btn.addEventListener('mousemove', function (e) {
          var r = btn.getBoundingClientRect();
          var dx = (e.clientX - r.left - r.width / 2) * 0.12;
          var dy = (e.clientY - r.top - r.height / 2) * 0.25;
          btn.style.transform = 'translate(' + Math.max(-6, Math.min(6, dx)) + 'px,' + Math.max(-4, Math.min(4, dy)) + 'px)';
        });
        btn.addEventListener('mouseleave', function () { btn.style.transform = ''; });
      });
    }
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', run);
  else run();
})();

/* failsafe: a reveal element may never stay invisible while in view. The
   observer reveals elements just before they enter, so this only fires if
   the observer itself stalled, so content can never be lost to a quirk. */
(function(){
  try{
    if(window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    var quiet=0, timer=setInterval(function(){
      var pending=document.querySelectorAll('.reveal:not(.rvforce):not(.done)');
      if(!pending.length){ if(++quiet>=3) clearInterval(timer); return; }
      quiet=0;
      pending.forEach(function(el){
        var r=el.getBoundingClientRect();
        if(r.top<innerHeight*0.7 && r.bottom>0 &&
           parseFloat(getComputedStyle(el).opacity)<0.05){
          el.classList.add('rvforce');
        }
      });
    },800);
  }catch(e){}
})();
