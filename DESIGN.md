# Rustic Earth Tea & Spice Co. — redesign concept

Real content from rusticearthco.com (products, prices, hours, addresses, phone).
One-page concept; shop links point at the live store.

## Subject
A family-run South Jersey tea & spice pantry (Dennis Township store + Berlin
Farmers Market stall). Audience: cooks, tea drinkers, gift buyers. Job: make
the pantry feel real and worth the trip, then route to the shop or the store.

## Palette (grounded in the spices themselves, not a default scheme)
- Bark        #2A2018  deep cocoa base (dominant, not cream)
- Bark deep   #221A12  hero overlay / footer
- Malt cream  #F3EADA  text + label cards (their existing cream, kept)
- Turmeric    #D99A33  accent, links and stamps
- Paprika     #A6472E  second accent, used twice on the page only
- Nutmeg tan  #C7B299  hairlines, shelf boards

## Type
Fraunces (display; soft, food-adjacent, used at real display sizes with
optical sizing) + Karla (body and UI). No all-caps eyebrows, no single-word
accent color inside headlines, no numbered markers.

## The one bold idea
The page reads like the shop's own pantry: dark cocoa field, cream label
cards with punched-tag detail, thin tan shelf boards that categories actually
sit on, and a dark band given to the shop's genuinely odd real product line
(Mythical Meats fantasy snack sticks) as a slow stamp-ticker.

## Motion plan (v188 / v184 / v187)
- Story arc: act 1 hero (what the shop is), act 2 shelves + picks + odd shelf
  (explore the pantry), act 3 visit + contact (resolve: come in or order).
- Mechanism, chosen on purpose: scroll-TRIGGERED staged reveals per section
  (each runs its own clock; this is discovery browsing, not a data story that
  needs the scrollbar as playhead). One orchestrated page-load sequence in the
  hero. CSS marquee on the odd shelf. No scroll hijacking, no wheel events.
- Implementation: IntersectionObserver toggling a class; transitions animate
  transform and opacity only. Hover transitions answer the user's action.
- Reduced motion: every reveal is visible immediately; the marquee renders as
  a static wrapped row; hero sequence skipped. Content carries the page.
