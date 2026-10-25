#!/usr/bin/env python3
"""Generate the Rustic Earth Tea & Spice Co. redesign site. Concept: Stephen Fehon."""
import json, os, re, html as H, urllib.parse as U

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
_MP = ROOT + '/build/data/merged.json'
M = json.load(open(_MP if os.path.exists(_MP) else '/tmp/merged.json'))

import re as _re
_LABS = ['Antioxidant level', 'Antioxidants', 'Antioxidant', 'Caffeine',
         'Suggested Use', 'Ingredients', 'Allergen Alert', 'Natural/Raw',
         'Nutritional Facts', 'Steeping', 'Brewing']
def _clean_desc(s):
    if not s: return s
    s = s.replace('****', ' ')
    s = _re.sub(r'\s+', ' ', s).strip()
    # space after a sentence mark glued to a capital
    s = _re.sub(r'([.!?])(?=[A-Z])', r'\1 ', s)
    # separator before glued attribute labels
    for lab in _LABS:
        s = _re.sub(r'(?<=[\w\)\.\!\?"\'])\s*(' + _re.escape(lab) + r')\b', r' · \1', s)
    # paren-to-capital glue, colon glue
    s = _re.sub(r'\)([A-Z])', ') · \\1', s)
    s = _re.sub(r'(?<=[a-z0-9]):(?=[A-Z])', ': ', s)
    if 'Balsamics:' in s:  # gift-box flavor lists run together
        s = _re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', s)
    s = _re.sub(r'\s+', ' ', s).strip()
    # trim cuts that end mid-thought
    if _re.search(r'[.!?]["\')]?\s*$', s): return s
    if _re.search(r'[A-Za-z][^:]{0,30}: [\w /&+,.\'-]+$', s): return s
    def _bal(t):
        while t.count('(') > t.count(')'):
            k = t.rfind('(')
            t = t[:k].rstrip(' \u00b7,;:')
        return t
    j = s.rfind(' ')
    ms = list(_re.finditer(r'[.!?]["\')]?(?=\s|$)', s))
    if ms:
        m = ms[-1]
        tail = s[m.end():]
        if m.start() > len(s) * 0.35 and tail.count(',') < 3:
            return _bal(s[:m.end()].rstrip())
    i = s.rfind(',')
    if i > len(s) * 0.75: return _bal(s[:i].rstrip(' ,;:'))
    if j > len(s) * 0.75: return _bal(s[:j].rstrip(' ,;:'))
    if ms:
        m = ms[-1]
        if m.start() > len(s) * 0.3: return _bal(s[:m.end()].rstrip())
    return _bal(s[:j].rstrip(' ,;:')) if j > 0 else s
for _k in M:
    if not M[_k].get('preclean'):
        M[_k]['desc'] = _clean_desc(M[_k].get('desc'))

BY_SLUG = {p['slug']: p for p in M.values()}
SKUS = json.load(open(ROOT + '/build/data/skus.json'))

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
# per-category line art for products without photos (concept by Stephen Fehon)
_CAT_MOTIFS = {
 'tea': '<path d="M118 236h164a8 8 0 0 1-8 42H126a8 8 0 0 1-8-42Z" fill="none" stroke="#D99A33" stroke-width="7"/><path d="M282 250c26-4 44 6 40 22s-28 22-44 14" fill="none" stroke="#D99A33" stroke-width="7"/><path d="M170 200c-10-26 10-34 2-58m36 58c-10-26 10-34 2-58" fill="none" stroke="#A6472E" stroke-width="6" stroke-linecap="round"/><path d="M140 292c-6 22 4 34 20 40" fill="none" stroke="#D99A33" stroke-width="5" stroke-linecap="round"/>',
 'honey': '<path d="M200 128l34 20v40l-34 20-34-20v-40Z" fill="none" stroke="#D99A33" stroke-width="7"/><path d="M166 188l34 20 34-20m-68-40-34 20v40l34 20" fill="none" stroke="#D99A33" stroke-width="5"/><path d="M200 246v64m0-64 26-10m-26 10-26-10" fill="none" stroke="#A6472E" stroke-width="7" stroke-linecap="round"/><circle cx="200" cy="322" r="14" fill="none" stroke="#A6472E" stroke-width="6"/>',
 'vinegar': '<path d="M182 132h36v34l22 20v96a10 10 0 0 1-10 10h-60a10 10 0 0 1-10-10v-96l22-20Z" fill="none" stroke="#A6472E" stroke-width="7"/><path d="M170 250h60" stroke="#A6472E" stroke-width="6"/><path d="M186 196h28" stroke="#D99A33" stroke-width="6" stroke-linecap="round"/>',
 'olive-oil': '<path d="M196 300c0-56 8-96 8-96h-8c0-32 10-44 4-64" fill="none" stroke="#5c6b3c" stroke-width="7" stroke-linecap="round"/><path d="M204 204c22-10 44-6 56 10-20 12-44 10-56-10Zm0-30c-22-12-46-8-58 8 20 12 46 10 58-8Z" fill="none" stroke="#5c6b3c" stroke-width="6"/><circle cx="232" cy="238" r="9" fill="#A6472E"/><circle cx="172" cy="208" r="9" fill="#2A2018"/>',
 'gourmet-salt': '<path d="M168 214l30-46 34 12 8 40-30 32-38-12Z" fill="none" stroke="#7f8fa0" stroke-width="7"/><path d="M240 268l22-30 28 10 6 28-24 22-30-10Z" fill="none" stroke="#7f8fa0" stroke-width="6"/><path d="M148 276l16-22 24 8 4 20-18 18-24-8Z" fill="none" stroke="#7f8fa0" stroke-width="5"/>',
 'spice': '<path d="M156 232h88l-10 62a10 10 0 0 1-10 8h-48a10 10 0 0 1-10-8Z" fill="none" stroke="#A6472E" stroke-width="7"/><path d="M236 156l28 48-16 10-26-44" fill="none" stroke="#A6472E" stroke-width="7" stroke-linecap="round"/><circle cx="168" cy="204" r="5" fill="#D99A33"/><circle cx="188" cy="196" r="5" fill="#D99A33"/><circle cx="208" cy="202" r="5" fill="#D99A33"/>',
 'coffee': '<path d="M150 216h104v34a34 34 0 0 1-34 34h-36a34 34 0 0 1-34-34Z" fill="none" stroke="#6b4a2e" stroke-width="7"/><path d="M254 228c20-2 32 10 28 24s-24 18-32 10" fill="none" stroke="#6b4a2e" stroke-width="6"/><path d="M184 190c-8-16 8-24 2-40m30 40c-8-16 8-24 2-40" fill="none" stroke="#6b4a2e" stroke-width="6" stroke-linecap="round"/><ellipse cx="296" cy="300" rx="14" ry="9" transform="rotate(-24 296 300)" fill="none" stroke="#D99A33" stroke-width="5"/>',
 'shop-all': '<path d="M168 172l62-38 100 62-56 92-106-52Z" fill="none" stroke="#D99A33" stroke-width="7"/><circle cx="206" cy="180" r="9" fill="#A6472E"/><path d="M296 152c20-12 38-8 48 6" fill="none" stroke="#A6472E" stroke-width="5" stroke-linecap="round"/>',
 'health-wellness': '<path d="M200 296c-56-18-64-74-36-112 10 44 22 60 36 78 14-18 26-34 36-78 28 38 20 94-36 112Z" fill="none" stroke="#5c7a52" stroke-width="7"/><path d="M200 282v40" stroke="#5c7a52" stroke-width="7" stroke-linecap="round"/>',
}
def art_html(p, prefix=''):
    svg = _CAT_MOTIFS.get(p.get('cat',''), _CAT_MOTIFS['tea'])
    return ('<span class="cat-art" role="img" aria-label="Product illustration">'
      '<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">'
      '<rect width="400" height="400" fill="#F3EADA"/>'
      '<circle cx="66" cy="84" r="120" fill="rgba(217,154,51,.10)"/>'
      '<circle cx="356" cy="330" r="150" fill="rgba(166,71,46,.07)"/>'
      + svg + '</svg></span>')

def img_path(p, prefix=''):
    f = IMG_EXT.get(p['slug'])
    if f: return prefix+'images/products/'+f
    cat = p.get('cat','') if p.get('cat','') in _CAT_MOTIFS else 'shop-all'
    return prefix+'images/cat/'+cat+'.svg'

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
<meta property="og:type" content="website">
<meta property="og:site_name" content="Rustic Earth Tea &amp; Spice Co.">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="https://stewiefeh.github.io/rustic-earth-co-redesign/images/hero.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2A2018">
<link rel="icon" type="image/png" href="{prefix}images/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,560;9..144,640&family=Karla:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}css/style.css?v=11">
{extra}</head>
<body data-root="{prefix}">
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
<div class="promo"><strong>Free shipping</strong> on all orders over $75. Two shops in South Jersey</div>
<header class="site-head" id="siteHead">
  <div class="head-inner">
    <div class="head-top">
    <a class="brand" href="{prefix}index.html" aria-label="Rustic Earth Tea &amp; Spice Co. home">
      <img src="{prefix}images/logo-mark.png" alt="Rustic Earth Tea &amp; Spice Co. stamp logo" width="56" height="56">
      <span class="wordmark">Rustic Earth<small>Tea &amp; Spice Co.</small></span>
    </a>
      <a class="cart-btn" href="{prefix}cart.html" aria-label="View cart">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M6 7h12l-1.2 12.2a1.8 1.8 0 0 1-1.8 1.8H9a1.8 1.8 0 0 1-1.8-1.8Z"/><path d="M9 7V5.6A3 3 0 0 1 12 3a3 3 0 0 1 3 2.6V7"/></svg>
        <span class="cart-count" data-cart-count hidden>0</span>
      </a>
    </div>
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
      <p style="font-size:.93rem">New arrivals, tastings and restocks:</p>
      <form class="loop-form" data-loop>
        <input type="email" name="email" required placeholder="you@email.com" aria-label="Your email address">
        <button class="btn btn-primary" type="submit">Sign up</button>
      </form>
      <p class="loop-note" data-loop-note hidden>Thanks! Your email app opens with everything filled in &mdash; hit send and the shop adds you to the list.</p>
      <p style="margin-top:8px;font-size:.93rem"><a href="mailto:{EMAIL}" style="display:inline;padding:0">Prefer a plain email? Write to us.</a></p>
    </div>
  </div>
  <div class="wrap fineprint">
    <span>&copy; 2026 Rustic Earth Tea &amp; Spice Co. All rights reserved.</span>
    <span>Site concept by Stephen Fehon.</span>
  </div>
</footer>
<script src="{prefix}js/main.js?v=8" defer></script>
<script src="{prefix}js/square-links.js?v=1" defer></script>
<script src="{prefix}js/cart.js?v=4" defer></script>
</body>
</html>
'''

def price_html(price):
    if not price: return ''
    parts = [q.strip() for q in price.replace('$','').split('-')]
    if len(parts) == 2:
        return f'<span class="price">${esc(parts[0].strip())} &ndash; ${esc(parts[1].strip())}</span>'
    return f'<span class="price">{esc(price)}</span>'

def stock_badge(stock):
    s = (stock or '').strip()
    if not s: return ''
    cls = 'out' if 'Out' in s else 'low'
    return f'<span class="stock {cls}">{esc(s)}</span>'

def price_badge(price):
    if not price: return 'Ask in store'
    parts = [q.strip().replace('$', '') for q in price.split('-')]
    if len(parts) == 2 and parts[1]:
        return f'${esc(parts[0])} &ndash; ${esc(parts[1])}'
    return f'${esc(parts[0])}'

def prod_card(p, prefix, subval=None):
    ip = img_path(p, prefix)
    thumb = (f'<img src="{ip}" alt="{esc(p["name"])}" loading="lazy">' if ip
             else art_html(p))
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
    has_img = p['slug'] in IMG_EXT
    photo = (f'<img src="{ip}" alt="{esc(p["name"])}" loading="eager">' if has_img
             else art_html(p))
    nophoto = '' if has_img else ' nophoto'
    desc_paras = ''.join(f'<p>{esc(s.strip())}</p>' for s in re.split(r'\n+', p['desc'] or '') if s.strip())
    stock = (p['stock'] or '').strip()
    if not stock: scls, stxt = 'in', 'In stock'
    elif 'Out' in stock: scls, stxt = 'out', 'Out of stock'
    else: scls, stxt = 'low', 'Low stock'
    # purchase block: variants, quantity, add-to-cart
    vs = SKUS.get(p['id'], [])
    sold = (stock == 'Out of stock') or (vs and all(v['soldOut'] for v in vs))
    if not vs:
        buy = ''
    elif sold:
        buy = ('<div class="buy-box no-js-hide"><p class="sold-line">Sold out right now &mdash; '
               'call <a href="tel:+1' + PHONE.replace('-', '') + '">' + PHONE + '</a> or ask in store about the next batch.</p></div>')
    else:
        opts = ''
        if len(vs) > 1:
            opts = '<label class="opt-label" for="vsel">Choose an option</label>\n        <div class="sel-wrap"><select id="vsel" data-variant>'
            for v in vs:
                mark = ' (sold out)' if v['soldOut'] else ''
                dis = ' disabled' if v['soldOut'] else ''
                opts += '<option value="%s"%s>%s</option>' % (v['id'], dis, esc(v['name'] + mark))
            opts += '</select></div>'
        addbtn = ('<button class="btn btn-primary add-btn" type="submit" data-add>Add to cart '
                  '<span class="add-price" data-addprice>%s</span></button>' % esc(vs[0]['fmt']))
        buy = ('<div class="buy-box">\n      <form data-buyform>\n        ' + opts +
               '\n        <div class="qty-row">\n'
               '          <button type="button" class="qty-btn" data-q="-1" aria-label="Decrease quantity">&minus;</button>\n'
               '          <input class="qty-input" data-qty type="number" value="1" min="1" inputmode="numeric" aria-label="Quantity">\n'
               '          <button type="button" class="qty-btn" data-q="1" aria-label="Increase quantity">+</button>\n'
               '        </div>\n        ' + addbtn + '\n      </form>\n    </div>\n'
               '    <script>window.RE_ITEM=' + json.dumps({'id': p['id'], 'slug': p['slug'], 'name': p['name'], 'img': img_path(p, '')}) +
               ';window.RE_VARIANTS=' + json.dumps(vs) + ';</script>')
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
      <p class="pd-price" data-price>{esc(p['price']) if p['price'] else 'Ask in store'}</p>
      <span class="pd-stock {scls}">{stxt}</span>
      {buy}
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


# ---------- cart page ----------
def cart_page(depth=1):
    prefix = prefix_for(depth)
    shop = {'email': EMAIL, 'phone': PHONE, 'freeAt': 75}
    extra = ('<script>window.RE_SHOP=' + json.dumps(shop) + ';</script>')
    return head('Your Cart | Rustic Earth Tea & Spice Co.', 'Review your order: items, quantities and total. Place it by email or phone; free shipping on orders over $75.', prefix, extra) + \
      header(prefix, active='Cart') + f'''
<div class="wrap page-head">
  <p class="crumbs"><a href="{prefix}index.html">Home</a> &rsaquo; Cart</p>
  <h1>Your cart</h1>
</div>
<div class="wrap cart-wrap">
  <div id="cartRoot" class="cart-root">
    <noscript><p class="cart-empty">The cart needs JavaScript. You can still order by phone at <a href="tel:+1{PHONE.replace('-','')}">{PHONE}</a> or by email at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></noscript>
  </div>
  <aside class="cart-side no-js-hide" id="cartSide" hidden>
    <div class="ship-track" data-shiptrack hidden>
      <div class="ship-bar" data-shipbar></div>
      <p class="ship-msg" data-shipmsg></p>
    </div>
    <div class="cart-sumline"><span>Subtotal</span><strong data-subtotal>$0.00</strong></div>
    <p class="cart-fine">Shipping is free over $75. Below that, the shop quotes exact shipping when they confirm your order.</p>
    <div class="cart-contact">
      <h2>Your details</h2>
      <label>Name<input data-cname type="text" autocomplete="name" placeholder="Your name"></label>
      <label>Phone or email<input data-ccontact type="text" autocomplete="tel email" placeholder="So they can confirm"></label>
    </div>
    <button class="btn btn-primary place-btn" data-place>Place order by email</button>
    <a class="btn btn-ghost call-btn" style="color:var(--bark);border-color:rgba(42,32,24,.4)" href="tel:+1{PHONE.replace('-','')}">Call your order in: {PHONE}</a>
    <p class="cart-fine">Placing opens a prefilled email to the shop with your order. They confirm stock, payment and pickup or shipping by reply.</p>
  </aside>
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
        cards += f'''<article class="loc-card reveal reveal-l">
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
    <div data-hours='{esc(L["hours_json"])}'><h3 style="margin:20px 0 0">Hours</h3>
    <table class="hours-table">{rows}</table>
    <p style="font-size:.85rem;color:#7a6f60;margin-top:10px">{esc(L['hours_note'])}</p></div>
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
        cat_cards += f'''<a class="cat-card reveal reveal-s" href="{prefix}shop/{slug}.html">
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
    <img class="reveal reveal-r" src="{prefix}images/products/abb-bee-s-wildflower-12oz.jpeg" alt="A jar of ABB-Bee's wildflower honey with a wooden dipper" loading="lazy" onerror="this.src='{prefix}images/hero.png'">
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
    <img class="reveal reveal-l" src="{prefix}images/hero.png" alt="Rustic Earth's counter" loading="lazy">
  </div>
</section>
'''.replace(' loading="lazy"', '') + footer(prefix)

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
    write('cart.html', cart_page(depth=0))
    # sitemap, robots, custom 404 (concept by Stephen Fehon)
    base = 'https://stewiefeh.github.io/rustic-earth-co-redesign/'
    urls = [('', '1.0'), ('shop/shop-all.html', '0.9')]
    for s, n, _ in CATS: urls.append((f'shop/{s}.html', '0.9'))
    urls += [('locations/index.html','0.7'),('locations/dennis.html','0.6'),('locations/berlin.html','0.6'),('jobs/index.html','0.6')]
    for p in sorted(M.values(), key=lambda x: x['slug']):
        urls.append((f"products/{p['slug']}/", '0.8'))
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u, pr in urls:
        sm += f'  <url><loc>{base}{u}</loc><priority>{pr}</priority></url>\n'
    sm += '</urlset>\n'
    with open('sitemap.xml','w') as fh: fh.write(sm)
    with open('robots.txt','w') as fh: fh.write('User-agent: *\nAllow: /\nSitemap: ' + base + 'sitemap.xml\n')
    nf = head('Page not found | Rustic Earth Tea & Spice Co.', 'That page is not here. Browse the shelves or head back to the shop.', '') + header('', active='') + f'''
<div class="wrap" style="padding:72px 22px;text-align:center">
  <h1>That page is not on the shelf</h1>
  <p>The link you followed leads nowhere. The shop is one click away.</p>
  <p style="margin-top:18px"><a class="btn btn-primary" href="index.html">Back to the shop</a></p>
</div>
''' + footer('')
    write('404.html', nf)
    import os as _os
    _os.makedirs('images/cat', exist_ok=True)
    for _n, _b in _CAT_MOTIFS.items():
        with open(f'images/cat/{_n}.svg','w') as _fh:
            _fh.write('<svg viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg"><rect width="400" height="400" fill="#F3EADA"/><circle cx="66" cy="84" r="120" fill="rgba(217,154,51,.10)"/><circle cx="356" cy="330" r="150" fill="rgba(166,71,46,.07)"/>'+_b+'</svg>')
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
