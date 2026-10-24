#!/usr/bin/env python3
"""Generate the Rustic Earth Tea & Spice Co. redesign site. Concept: Stephen Fehon."""
import json, os, re, html as H, urllib.parse as U

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
M = json.load(open('/tmp/merged.json'))
BY_SLUG = {p['slug']: p for p in M.values()}

def esc(s): return H.escape(str(s or ''), quote=True)

def tag_icon(cls=""):
    return ('<svg class="%s" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true">'
            '<path d="M20.6 13.4 11 3.8H4v7l9.6 9.6a2 2 0 0 0 2.8 0l4.2-4.2a2 2 0 0 0 0-2.8Z"/>'
            '<circle cx="7.5" cy="7.5" r="1.3" fill="currentColor" stroke="none"/></svg>' % cls)

CHECK = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
         '<path d="M20 6 9 17l-5-5"/></svg>')

# ---------- product image extensions on disk ----------
IMG_EXT = {}
pdir = 'images/products'
if os.path.isdir(pdir):
    for f in os.listdir(pdir):
        IMG_EXT[os.path.splitext(f)[0]] = f
def img_path(p, prefix=''):
    f = IMG_EXT.get(p['slug'])
    return (prefix + 'images/products/' + f) if f else None

CATS = [
  ('tea', 'Tea', 'Loose-leaf black, green, herbal and white teas, scooped to order.'),
  ('spice', 'Spice', 'House spice blends and rubs for the grill, the oven and the stovetop.'),
  ('gourmet-salt', 'Gourmet Salt', 'Flavored sea salts finished over smoke, espresso and truffle.'),
  ('vinegar', 'Vinegar', 'White and dark balsamics, infused and aged, for dressings and glazes.'),
  ('olive-oil', 'Olive Oil', 'Extra virgin olive oils, from Greek koroneiki to blood orange.'),
  ('honey', 'Honey', "Raw New Jersey honey from ABB-Bee's, plus infused wellness honey."),
  ('coffee', 'Coffee', 'Small-batch JavAroma roasts and mushroom coffee blends.'),
  ('health-wellness', 'Health & Wellness', 'Bitters, balms, supplements and small-batch self-care.'),
  ('shop-all', 'Snacks & More', 'Mythical Meats snack sticks, mugs, whisks and other finds.'),
]
CAT_NAMES = dict((c[0], c[1]) for c in CATS)
SUBS = {
 'tea': [('herbal-fruit', 'Herbal & Fruit'), ('black', 'Black'), ('green', 'Green'), ('oolong', 'Oolong'), ('white', 'White')],
 'vinegar': [('white-balsamic', 'White Balsamic'), ('dark-balsamic', 'Dark Balsamic')],
 'coffee': [('mushroom-coffee', 'Mushroom Coffee')],
 'health-wellness': [('dental', 'Dental Care')],
}
CAT_LEADS = {
 'tea': 'Sixty-six teas on the wall, from everyday black blends to rare gyokuro. Tell the counter what you like and they scoop it in front of you.',
 'spice': 'Blends mixed for real cooking: burger night, ribs, jerk chicken, bread dipping. Most come in jar or refill sizes.',
 'gourmet-salt': 'A short, punchy shelf of flavored sea salts. Sprinkle finishers for steaks, fries, corn and chocolate desserts.',
 'vinegar': 'Balsamics worth tasting before you buy. White balsamics stay bright and fruity; the dark ones bring depth and molasses.',
 'olive-oil': 'Single-estate Greek and Italian oils plus flavored EVOOs that double as finishing drizzles and bread dip.',
 'honey': "Raw honey from a South Jersey beekeeper, sold by the jar. Flavored wellness honeys blend honey with mushrooms and herbs.",
 'coffee': 'JavAroma small-batch roasts ground to order, and a full mushroom-coffee shelf for the low-caffeine curious.',
 'health-wellness': 'Bitters, tallow balms, sea moss and supplements from small makers Buhem, Magnum Solace, Naturacentric, Sanura Well and Yunani.',
 'shop-all': 'The gift-shelf picks that live outside the main categories: Mythical Meats snack sticks, an infuser mug, a matcha whisk and more.',
}
SUB_LABELS = dict(kv for lst in SUBS.values() for kv in lst)

PHONE = '856-259-3498'
EMAIL = 'rusticearthcompany@gmail.com'
GIFT = 'https://squareup.com/gift/CBV15A5FB9AYA/order'

LOCS = {
 'dennis': {
   'name': 'Woodland Village Store', 'town': 'Dennisville',
   'street': '1943 U.S. 9', 'unit': 'Store #14', 'city': 'Dennis', 'zip': '08210',
   'phone': PHONE, 'email': EMAIL,
   'lat': '39.14796', 'lng': '-74.76436',
   'hours_json': '[{"d":[5,6,0],"o":600,"c":1020}]',
   'oh': 'Fr-Su 10:00-17:00',
   'hours_rows': [('Friday', '10am to 5pm', '5'), ('Saturday', '10am to 5pm', '6'), ('Sunday', '10am to 5pm', '0'),
                  ('Monday', 'Closed', '1'), ('Tuesday', 'Closed', '2'), ('Wednesday', 'Closed', '3'), ('Thursday', 'Closed', '4')],
   'hours_note': 'Fall off-season hours, Friday through Sunday.',
   'map_q': '1943 U.S. 9, Dennis, NJ 08210',
 },
 'berlin': {
   'name': 'Berlin Farmers Market', 'town': 'Berlin',
   'street': '41 Clementon Road', 'unit': 'Store #206', 'city': 'Berlin', 'zip': '08009',
   'phone': PHONE, 'email': EMAIL,
   'lat': '39.80000', 'lng': '-74.94037',
   'hours_json': '[{"d":[4],"o":660,"c":1080},{"d":[5,6],"o":600,"c":1080},{"d":[0],"o":600,"c":1020}]',
   'oh': 'Th 11:00-18:00; Fr-Sa 10:00-18:00; Su 10:00-17:00',
   'hours_rows': [('Thursday', '11am to 6pm', '4'), ('Friday', '10am to 6pm', '5'), ('Saturday', '10am to 6pm', '6'),
                  ('Sunday', '10am to 5pm', '0'), ('Monday', 'Closed', '1'), ('Tuesday', 'Closed', '2'), ('Wednesday', 'Closed', '3')],
   'hours_note': 'Inside the Berlin Farmers Market, Thursday through Sunday.',
   'map_q': '41 Clementon Road, Berlin, NJ 08009',
 },
}

def prefix_for(depth): return '../' * depth

def head(title, desc, prefix, extra=''):
    return f'''<!DOCTYPE html>
<html lang="en" class="no-js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="icon" type="image/png" href="{prefix}images/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,560;9..144,640&family=Karla:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}css/style.css">
{extra}</head>
<body>
'''

def header(prefix, active=''):
    nav = [('Home', 'index.html')]
    for slug, name, _ in CATS[:8]:
        nav.append((name, f'shop/{slug}.html'))
    nav += [('Locations', 'locations/index.html'), ('Jobs', 'jobs/index.html'), ('Gift Card', GIFT)]
    nav = [(l, h if h.startswith('http') else prefix + h) for l, h in nav]
    links = ''
    for label, href in nav:
        cur = ' aria-current="page"' if label == active else ''
        ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
        links += f'<a href="{href}"{cur}{ext}>{label}</a>\n'
    return f'''<a class="visually-hidden" href="#main">Skip to content</a>
<div class="promo"><strong>Free shipping</strong> on all orders over $75 &middot; two shops in South Jersey</div>
<header class="site-head" id="siteHead">
  <div class="head-inner">
    <a class="brand" href="{prefix}index.html" aria-label="Rustic Earth Tea &amp; Spice Co. home">
      <img src="{prefix}images/logo-mark.png" alt="Rustic Earth Tea &amp; Spice Co. stamp logo" width="56" height="56">
      <span class="wordmark">Rustic Earth<small>Tea &amp; Spice Co.</small></span>
    </a>
    <nav class="nav-row" aria-label="Primary">
{links}    </nav>
  </div>
</header>
<main id="main" class="pagein">
'''

def footer(prefix):
    catlinks = ''.join(f'<a href="{prefix}shop/{s}.html">{n}</a>' for s, n, _ in CATS)
    return f'''</main>
<footer class="site-foot">
  <div class="wrap foot-grid">
    <div>
      <div class="foot-brand">
        <img src="{prefix}images/logo-mark.png" alt="" width="48" height="48">
        <span class="wordmark">Rustic Earth<small>Tea &amp; Spice Co.</small></span>
      </div>
      <p style="font-size:.93rem;max-width:34ch">A family shop for loose-leaf tea, house spice blends, flavored sea salts, balsamics, olive oils and raw local honey.</p>
      <p style="margin-top:12px;font-size:.93rem"><a href="mailto:{EMAIL}" style="display:inline;padding:0">{EMAIL}</a><br>
      <a href="tel:+1{PHONE.replace('-','')}" style="display:inline;padding:0">{PHONE}</a></p>
    </div>
    <div>
      <h4>Browse</h4>
      {catlinks}
    </div>
    <div>
      <h4>Visit</h4>
      <a href="{prefix}locations/dennis.html">Dennis, NJ</a>
      <a href="{prefix}locations/berlin.html">Berlin, NJ</a>
      <a href="{prefix}jobs/index.html">Work with us</a>
      <a href="{GIFT}" target="_blank" rel="noopener">Gift cards</a>
    </div>
    <div>
      <h4>Stay in the loop</h4>
      <p style="font-size:.93rem">Ask about new arrivals, tastings and restocks:</p>
      <p style="margin-top:8px"><a class="btn btn-primary" href="mailto:{EMAIL}?subject=Keep%20me%20in%20the%20loop" style="display:inline-flex">Email the shop</a></p>
    </div>
  </div>
  <div class="wrap fineprint">
    <span>&copy; 2026 Rustic Earth Tea &amp; Spice Co. All rights reserved.</span>
    <span>Site concept by Stephen Fehon.</span>
  </div>
</footer>
<script src="{prefix}js/main.js" defer></script>
</body>
</html>
'''

def price_html(price):
    if not price: return ''
    parts = [q.strip() for q in price.replace('$','').split('-')]
    if len(parts) == 2:
        return f'<span class="price">$ {esc(parts[0].strip())} &ndash; {esc(parts[1].strip())}</span>'
    return f'<span class="price">{esc(price)}</span>'

def stock_badge(stock):
    s = (stock or '').strip()
    if not s: return ''
    cls = 'out' if 'Out' in s else 'low'
    return f'<span class="stock {cls}">{esc(s)}</span>'

def prod_card(p, prefix, subval=None):
    ip = img_path(p, prefix)
    thumb = (f'<img src="{ip}" alt="{esc(p["name"])}" loading="lazy">' if ip
             else f'<span class="nophoto-wrap">{tag_icon()}</span>')
    nophoto = '' if ip else ' nophoto'
    subattr = f' data-subcat="{esc(subval)}"' if subval else ''
    return f'''<a class="p-card"{subattr} href="{prefix}products/{p['slug']}/">
  <span class="p-thumb{nophoto}">{stock_badge(p['stock'])}{thumb}</span>
  <span class="p-info"><span class="name">{esc(p['name'])}</span>{price_html(p['price'])}</span>
</a>
'''

# placeholder thumb needs svg inside .p-thumb.nophoto
def prod_card_fix(p, prefix, subval=None):
    c = prod_card(p, prefix, subval)
    if not img_path(p, prefix):
        c = c.replace('<span class="nophoto-wrap">', '').replace('</span>\n  <span class="p-info">', '\n  <span class="p-info">', 1)
    return c

def cat_page(cat, depth=1):
    prefix = prefix_for(depth)
    name, lead = CAT_NAMES[cat], CAT_LEADS[cat]
    items = sorted([p for p in M.values() if p['cat'] == cat], key=lambda x: x['name'])
    chips = ''
    subs = SUBS.get(cat, [])
    if subs:
        chips += '<div class="chip-row" role="group" aria-label="Filter by type">'
        chips += f'<button class="chip" aria-pressed="true" data-sub="all">All ({len(items)})</button>'
        for s, lab in subs:
            n = sum(1 for p in items if p['sub'] == s)
            if n: chips += f'<button class="chip" aria-pressed="false" data-sub="{s}">{esc(lab)} ({n})</button>'
        chips += '</div>'
    grid = ''.join(prod_card_fix(p, prefix, subval=(p['sub'] or 'other')) for p in items)
    return head(f'{name} | Rustic Earth Tea & Spice Co.', f'Shop {name.lower()} at Rustic Earth Tea & Spice Co. {lead}', prefix) + \
        header(prefix, active=name) + f'''<div class="wrap page-head">
  <p class="crumbs"><a href="{prefix}index.html">Home</a> &rsaquo; {esc(name)}</p>
  <h1>{esc(name)}</h1>
  <p class="result-count" id="resultCount">{len(items)} items</p>
</div>
<div class="wrap">{chips}
  <div class="prod-grid">{grid}</div>
</div>
''' + footer(prefix)

# ---------- product page ----------
def product_page(p, depth=2):
    prefix = prefix_for(depth)
    cat_name = CAT_NAMES.get(p['cat'], 'Shop')
    cat_href = (prefix + 'shop/' + p['cat'] + '.html') if p['cat'] != 'shop-all' else (prefix + 'shop/all-items.html')
    ip = img_path(p, prefix)
    photo = (f'<img src="{ip}" alt="{esc(p["name"])}">' if ip
             else tag_icon())
    nophoto = '' if ip else ' nophoto'
    desc_paras = ''.join(f'<p>{esc(s.strip())}</p>' for s in re.split(r'\n+', p['desc'] or '') if s.strip())
    stock = (p['stock'] or '').strip()
    if not stock: scls, stxt = 'in', 'In stock'
    elif 'Out' in stock: scls, stxt = 'out', 'Out of stock'
    else: scls, stxt = 'low', 'Low stock'
    ld = {
      "@context": "https://schema.org", "@type": "Product",
      "name": p['name'], "description": p['desc'],
      "brand": {"@type": "Brand", "name": "Rustic Earth Tea & Spice Co."},
    }
    if ip: ld["image"] = "https://stewiefeh.github.io/rustic-earth-co-redesign/" + img_path(p, '')
    if p['price']:
        lo = p['price'].split('-')[0].strip().replace('$','').strip()
        ld["offers"] = {"@type": "Offer", "price": lo, "priceCurrency": "USD",
          "availability": "https://schema.org/InStock" if scls != 'out' else "https://schema.org/OutOfStock"}
    extra = '<script type="application/ld+json">' + json.dumps(ld) + '</script>'
    related = [q for q in M.values() if q['cat'] == p['cat'] and q['id'] != p['id']]
    related.sort(key=lambda x: x['name'])
    rel_pick = related[:8]
    if len(rel_pick) > 4:
        step = len(rel_pick) // 4
        rel_pick = rel_pick[::step][:4]
    rel_html = ''.join(prod_card_fix(q, prefix) for q in rel_pick)
    return head(f"{p['name']} | Rustic Earth Tea & Spice Co.", (p['desc'] or '')[:155], prefix, extra) + \
      header(prefix) + f'''<div class="wrap product-page">
  <p class="crumbs"><a href="{prefix}index.html">Home</a> &rsaquo; <a href="{cat_href}">{esc(cat_name)}</a> &rsaquo; {esc(p['name'])}</p>
  <div class="pd-grid">
    <div class="pd-photo{nophoto}">{photo}</div>
    <div class="pd-info">
      <p class="cat-tag"><a href="{cat_href}" style="color:inherit">{esc(cat_name)}</a></p>
      <h1>{esc(p['name'])}</h1>
      <p class="pd-price">{esc(p['price']) if p['price'] else 'Ask in store'}</p>
      <span class="pd-stock {scls}">{stxt}</span>
      <div class="pd-desc">{desc_paras}</div>
      <div class="get-box">
        <h3>How to get it</h3>
        <ul>
          <li>{CHECK}<span><strong>Free shipping</strong> on all orders over $75</span></li>
          <li>{CHECK}<span>Order by phone: <a href="tel:+1{PHONE.replace('-','')}" style="text-decoration:underline">{PHONE}</a></span></li>
          <li>{CHECK}<span>Or visit either shop and we'll set you up</span></li>
        </ul>
        <div class="get-cta">
          <a class="btn btn-dark" href="tel:+1{PHONE.replace('-','')}">Call {PHONE}</a>
          <a class="btn btn-ghost" style="color:var(--bark);border-color:rgba(42,32,24,.4)" href="{prefix}locations/index.html">Plan a visit</a>
        </div>
      </div>
      <div class="ship-note"><strong>Two shops:</strong>&nbsp;Dennis on U.S. 9 and the Berlin Farmers Market. Hours on the visit page.</div>
    </div>
  </div>
  <div class="related">
    <h2>More from {esc(cat_name)}</h2>
    <div class="prod-grid">{rel_html}</div>
  </div>
</div>
''' + footer(prefix)

# ---------- all items ----------
def all_items_page(depth=1):
    prefix = prefix_for(depth)
    items = sorted(M.values(), key=lambda x: (x['cat'], x['name']))
    chips = '<div class="chip-row" role="group" aria-label="Filter by category"><button class="chip" aria-pressed="true" data-sub="all">Everything</button>'
    for s, n, _ in CATS:
        cnt = sum(1 for p in items if p['cat'] == s)
        chips += f'<button class="chip" aria-pressed="false" data-sub="{s}">{esc(n)} ({cnt})</button>'
    chips += '</div>'
    grid = ''.join(prod_card_fix(p, prefix, subval=p['cat']) for p in items)
    return head('All Items | Rustic Earth Tea & Spice Co.', 'Browse everything on the shelves: tea, spice, gourmet salt, vinegar, olive oil, honey, coffee, health and wellness.', prefix) + \
      header(prefix, active='Shop All') + f'''<div class="wrap page-head">
  <p class="crumbs"><a href="{prefix}index.html">Home</a> &rsaquo; All items</p>
  <h1>All items</h1>
  <p class="result-count" id="resultCount">{len(items)} items</p>
</div>
<div class="wrap">{chips}
  <div class="prod-grid" data-all>{grid}</div>
</div>
''' + footer(prefix)

# ---------- locations ----------
LOC_HEROS = {
 'dennis': "The original counter on U.S. 9 in Dennisville, open Friday through Sunday in the off-season.",
 'berlin': "The weekend stall inside the Berlin Farmers Market, Thursday through Sunday.",
}
def locations_index(depth=1):
    prefix = prefix_for(depth)
    cards = ''
    for key, L in LOCS.items():
        addr = f"{L['street']}, {L['city']}, NJ {L['zip']}"
        cards += f'''<article class="loc-card reveal">
  <div class="loc-body" data-hours='{esc(L["hours_json"])}' data-badge-host=".loc-body">
    <h3><a href="{prefix}locations/{key}.html">{esc(L["name"])}</a></h3>
    <p class="loc-line"><strong>{esc(L["town"])}, NJ</strong></p>
    <p class="loc-line">{esc(L["street"])} {esc(L["unit"])}<br>{esc(L["city"])}, NJ {esc(L["zip"])}</p>
    <p class="loc-line">{esc(L["phone"])}</p>
  </div>
  <div class="loc-foot">
    <a class="btn btn-dark" href="{prefix}locations/{key}.html">Hours &amp; map</a>
    <a class="btn btn-ghost" style="color:var(--bark);border-color:rgba(42,32,24,.4)" target="_blank" rel="noopener" href="https://www.google.com/maps/dir/?api=1&destination={U.quote(L['map_q'])}">Directions</a>
  </div>
</article>
'''
    return head('Visit Us | Rustic Earth Tea & Spice Co.', 'Two South Jersey shops: the Woodland Village Store in Dennisville and the Berlin Farmers Market. Hours, maps and directions.', prefix) + \
      header(prefix, active='Locations') + f'''<div class="wrap page-head">
  <p class="crumbs"><a href="{prefix}index.html">Home</a> &rsaquo; Locations</p>
  <h1>Two shops, one shelf</h1>
  <p class="result-count" style="max-width:60ch">Scoop-your-own tea, spice blends by the jar, tasting spoons for oils and balsamics, and raw local honey. Pick the shop that's closest and check its hours.</p>
</div>
<div class="wrap"><div class="loc-grid">{cards}</div></div>
''' + footer(prefix)

def location_page(key, depth=2):
    prefix = prefix_for(depth)
    L = LOCS[key]
    other = 'berlin' if key == 'dennis' else 'dennis'
    OL = LOCS[other]
    title = f"{L['name']}, {L['town']} NJ"
    rows = ''.join(
      f'<tr data-dow="{d}"><td>{esc(day)}</td><td>{esc(hr)}</td></tr>' for day, hr, d in L['hours_rows'])
    ld = {
      "@context": "https://schema.org", "@type": "Store",
      "name": f"Rustic Earth Tea & Spice Co. ({L['name']})",
      "address": {"@type": "PostalAddress", "streetAddress": f"{L['street']} {L['unit']}",
                  "addressLocality": L['city'], "addressRegion": "NJ", "postalCode": L['zip'], "addressCountry": "US"},
      "telephone": "+1-" + PHONE, "email": EMAIL,
      "geo": {"@type": "GeoCoordinates", "latitude": L['lat'], "longitude": L['lng']},
      "openingHours": L['oh'],
    }
    extra = '<script type="application/ld+json">' + json.dumps(ld) + '</script>'
    return head(title + ' | Rustic Earth Tea & Spice Co.',
      f"Rustic Earth Tea & Spice Co. at {L['street']} {L['unit']}, {L['city']}, NJ {L['zip']}. Hours, phone, directions and what to expect.", prefix, extra) + \
      header(prefix, active='Locations') + f'''<div class="wrap page-head">
  <p class="crumbs"><a href="{prefix}index.html">Home</a> &rsaquo; <a href="{prefix}locations/index.html">Locations</a> &rsaquo; {esc(L['town'])}</p>
  <h1>{esc(L['name'])}</h1>
  <p class="result-count" style="max-width:62ch">{esc(LOC_HEROS[key])}</p>
</div>
<div class="wrap" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:26px">
  <div class="jobs-panel reveal" style="box-shadow:none">
    <h3 style="margin-bottom:4px">Address</h3>
    <p class="loc-line">{esc(L['street'])} {esc(L['unit'])}<br>{esc(L['city'])}, NJ {esc(L['zip'])}</p>
    <p class="loc-line" style="margin-top:10px">Phone: <a href="tel:+1{PHONE.replace('-','')}" style="text-decoration:underline">{esc(PHONE)}</a><br>
    Email: <a href="mailto:{EMAIL}" style="text-decoration:underline">{esc(EMAIL)}</a></p>
    <h3 style="margin:20px 0 0">Hours <span data-hours='{esc(L["hours_json"])}'></span></h3>
    <table class="hours-table">{rows}</table>
    <p style="font-size:.85rem;color:#7a6f60;margin-top:10px">{esc(L['hours_note'])}</p>
    <div class="get-cta" style="margin-top:18px">
      <a class="btn btn-dark" target="_blank" rel="noopener" href="https://www.google.com/maps/dir/?api=1&destination={U.quote(L['map_q'])}">Get directions</a>
      <a class="btn btn-ghost" style="color:var(--bark);border-color:rgba(42,32,24,.4)" href="tel:+1{PHONE.replace('-','')}">Call the shop</a>
    </div>
  </div>
  <div class="reveal">
    <div class="map-embed">
      <iframe title="Map to {esc(title)}" loading="lazy"
        src="https://www.google.com/maps?q={U.quote(L['map_q'])}&amp;output=embed"></iframe>
    </div>
    <div class="jobs-panel" style="margin-top:18px;box-shadow:none">
      <h3>What you'll find</h3>
      <p style="color:#4c443a;font-size:.95rem">The tea wall with over sixty loose-leaf blends scooped to order, house spice rubs by the jar, a tasting counter for olive oils and balsamics, flavored sea salts, and raw ABB-Bee's honey from right here in South Jersey.</p>
      <p style="color:#4c443a;font-size:.95rem;margin-top:10px">Free shipping on all orders over $75 if you'd rather shop from the couch.</p>
    </div>
  </div>
</div>
<div class="wrap" style="margin-top:34px">
  <p class="crumbs" style="margin:0">Our other shop: <a href="{prefix}locations/{other}.html">{esc(OL['name'])}, {esc(OL['town'])}</a></p>
</div>
''' + footer(prefix)

# ---------- jobs ----------
def jobs_page(depth=1):
    prefix = prefix_for(depth)
    return head('Work With Us | Rustic Earth Tea & Spice Co.', 'Apply to work at Rustic Earth Tea & Spice Co. Download the job application and drop it off at either shop, or email it back.', prefix) + \
      header(prefix, active='Jobs') + f'''<div class="jobs-hero">
  <div class="wrap">
    <p class="hero-kicker">Work with us</p>
    <h1>Join the counter crew</h1>
    <p>Days here mean scooping tea, blending spices, and talking honey with regulars. If that sounds like a good Saturday, we'd like to meet you.</p>
  </div>
</div>
<div class="wrap section" style="padding-top:48px">
  <div class="jobs-panel reveal" style="max-width:760px;margin:0 auto">
    <h2 style="font-size:1.5rem">How to apply</h2>
    <ol class="steps">
      <li><span><strong>Download the application</strong> below. It's a plain PDF, works best printed, but you can fill it on your computer too.</span></li>
      <li><span><strong>Fill it out</strong> with your availability. Weekend availability helps: both shops run Friday to Sunday in the off-season, and the Berlin stall runs Thursday to Sunday.</span></li>
      <li><span><strong>Bring it in</strong> to either shop and hand it across the counter, or email it to <a href="mailto:{EMAIL}" style="text-decoration:underline">{EMAIL}</a> with the subject line "Job application".</span></li>
    </ol>
    <div class="get-cta" style="margin-top:22px">
      <a class="btn btn-primary" href="{prefix}docs/job-application.pdf" download>Rustic Earth application (PDF)</a>
      <a class="btn btn-dark" href="mailto:{EMAIL}?subject=Job%20application">Email it instead</a>
    </div>
    <p style="margin-top:18px;font-size:.9rem;color:#7a6f60">Questions first? Call the shop at <a href="tel:+1{PHONE.replace('-','')}" style="text-decoration:underline">{PHONE}</a>.</p>
  </div>
</div>
''' + footer(prefix)

# ---------- homepage ----------
FEATURED_SLUGS = ['chipotle-honey-rub','tuscany-bread-dipping-seasoning','smoked-bacon-onion-sea-salt',
 'espresso-sea-salt','blood-orange-white-balsamic','mango-white-balsamic','greek-koroneiki',
 'abb-bee-s-wildflower-12oz','milky-earl-grey','vanilla-chai','good-time-earth-mushroom-coffee',
 'javaroma-stomping-grounds']
CAT_THUMBS = {
 'tea':['milky-earl-grey','ur-jasmine-dragon','vanilla-chai'],
 'spice':['chipotle-honey-rub','tuscany-bread-dipping-seasoning','sweet-whiskey-rub'],
 'gourmet-salt':['smoked-bacon-onion-sea-salt','espresso-sea-salt','smoked-garlic-onion-sea-salt'],
 'vinegar':['blood-orange-white-balsamic','mango-white-balsamic','strawberry-dark-balsamic'],
 'olive-oil':['greek-koroneiki','savory-siciliano','black-truffle-evoo'],
 'honey':['abb-bee-s-wildflower-12oz','abb-bee-s-blueberry-12oz','abb-bee-s-bamboo-honey-12oz'],
 'coffee':['good-time-earth-mushroom-coffee','javaroma-stomping-grounds','good-time-dark-mushroom-coffee'],
 'health-wellness':['naturacentric-organic-cacao-collagen-peptides','gold-sea-moss','magnum-solace-muscle-rub'],
 'shop-all':['mythical-snack-stick-dragon','mythical-meats-dungeons-dragons-eldritch-eats-warlock','casware-infuser-mug-16oz-farmhouse-blue'],
}
def thumb_for(cat):
    for s in CAT_THUMBS[cat]:
        p = BY_SLUG.get(s)
        if p and img_path(p, ''): return img_path(p, '')
    for p in sorted([q for q in M.values() if q['cat']==cat], key=lambda x:x['name']):
        if img_path(p, ''): return img_path(p, '')
    return None

def index_page():
    prefix = ''
    # hero
    hero = f'''<section class="hero">
  <img class="hero-img" src="{prefix}images/hero.png" alt="">
  <div class="veil"></div>
  <div class="hero-copy">
    <p class="hero-kicker">Two shops in South Jersey</p>
    <h1>Tea by the scoop, spice by the jar.</h1>
    <p class="lede">Loose-leaf tea, house spice blends, flavored sea salts, aged balsamics, olive oils and raw local honey. <strong style="color:var(--turmeric);font-style:normal">Free shipping on all orders over $75.</strong></p>
    <div class="hero-cta">
      <a class="btn btn-primary" href="{prefix}shop/all-items.html">Shop everything</a>
      <a class="btn btn-ghost" href="{prefix}locations/index.html">Plan a visit</a>
    </div>
  </div>
</section>
<div class="ticker" aria-hidden="true"><div class="ticker-track">'''
    tick_items = ['Small-batch tea','House spice blends','Gourmet sea salts','Aged balsamics','Single-estate olive oils','Raw local honey','Mushroom coffee']
    tick_html = ''.join(f'<span>{t}</span>' for t in tick_items)
    hero += tick_html + tick_html + '</div></div>'

    # categories
    cat_cards = ''
    for slug, name, tag in CATS:
        t = thumb_for(slug)
        cnt = sum(1 for p in M.values() if p['cat'] == slug)
        img = f'<img src="{t}" alt="" loading="lazy">' if t else ''
        cat_cards += f'''<a class="cat-card reveal" href="{prefix}shop/{slug}.html">
  {img}<span class="cat-label"><span class="name">{esc(name)}</span><br><span class="count">{cnt} items</span></span>
</a>
'''
    # featured
    feat = ''
    for s in FEATURED_SLUGS:
        p = BY_SLUG.get(s)
        if p: feat += prod_card_fix(p, prefix)
    return head('Rustic Earth Tea & Spice Co. — loose-leaf tea, spice blends, honey',
        'A family shop for loose-leaf tea, house spice blends, flavored sea salts, balsamics, olive oils and raw local honey. Two shops in South Jersey, free shipping over $75.', prefix) + \
      header(prefix, active='Home') + hero + f'''
<section class="section">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="kicker">Walk the shelves</p>
      <h2>Eight shelves, one counter</h2>
      <p>Everything here is sold the same way it is in the shop: scooped, jarred and labeled by hand in Dennisville and Berlin, New Jersey.</p>
    </div>
    <div class="cat-grid">{cat_cards}</div>
  </div>
</section>
<section class="section tint">
  <div class="wrap">
    <div class="section-head reveal">
      <p class="kicker">Counter picks</p>
      <h2>What the regulars keep coming back for</h2>
    </div>
    <div class="prod-grid">{feat}</div>
    <p style="margin-top:26px"><a class="btn btn-dark" href="{prefix}shop/all-items.html">See all items</a></p>
  </div>
</section>
<section class="section">
  <div class="wrap split">
    <img class="reveal" src="{prefix}images/products/abb-bee-s-wildflower-12oz.jpeg" alt="A jar of ABB-Bee's wildflower honey with a wooden dipper" loading="lazy" onerror="this.src='{prefix}images/hero.png'">
    <div class="reveal">
      <p class="kicker">From the hive</p>
      <h2>Raw honey from a neighbor's hives</h2>
      <p>Every jar of ABB-Bee's honey is gathered from New Jersey clover, wildflower and berry blossoms. It's raw, unfiltered, and the flavors change with the season, which is half the fun of asking what's new when you walk in.</p>
      <a class="btn btn-primary" style="margin-top:18px" href="{prefix}shop/honey.html">Shop honey</a>
    </div>
  </div>
</section>
<section class="section tint">
  <div class="wrap split">
    <div class="reveal">
      <p class="kicker">Visit us</p>
      <h2>Two shops, both worth the drive</h2>
      <p>Dennisville: the original counter on U.S. 9, Friday through Sunday. Berlin: a stall inside the Berlin Farmers Market, Thursday through Sunday. Come taste before you buy; that's what the spoons are for.</p>
      <a class="btn btn-primary" style="margin-top:18px" href="{prefix}locations/index.html">Hours &amp; directions</a>
    </div>
    <img class="reveal" src="{prefix}images/hero.png" alt="Rustic Earth's counter" loading="lazy">
  </div>
</section>
''' + footer(prefix)

# ---------- write everything ----------
def write(path, content):
    path = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f: f.write(content)

def main():
    write('index.html', index_page())
    for cat, name, _ in CATS:
        write(f'shop/{cat}.html', cat_page(cat, depth=1))
    write('shop/all-items.html', all_items_page(depth=1))
    for p in M.values():
        write(f"products/{p['slug']}/index.html", product_page(p, depth=2))
    write('locations/index.html', locations_index(depth=1))
    for key in LOCS:
        write(f'locations/{key}.html', location_page(key, depth=1))
    write('jobs/index.html', jobs_page(depth=1))
    n_html = sum(len(files) for _, _, files in os.walk(ROOT) if True) if False else None
    count = 0
    for r, d, files in os.walk('.'):
        count += sum(1 for f in files if f.endswith('.html'))
    print('html files:', count)

if __name__ == '__main__':
    main()
