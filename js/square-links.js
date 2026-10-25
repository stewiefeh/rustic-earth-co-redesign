/* Square checkout links - Rustic Earth Tea & Spice Co. redesign.
   Concept by Stephen Fehon.

   Go live with Square checkout (about 2 minutes per product):
   1. Square Dashboard > Items > pick the product variant.
   2. "Create checkout link" (Payment Links). Square returns a URL
      like https://square.link/u/XXXXXXXX.
   3. Paste it below, keyed by the variant's SKU code. Save and push:
      that variant's product page then shows "Buy with Square" and the
      cart shows a Pay with Square link for that line. Variants without
      a link keep the order-by-email flow, so nothing breaks mid-demo.
*/
window.RE_SQUARE_LINKS = window.RE_SQUARE_LINKS || {};
/* Example shape (replace with the shop's real links):
RE_SQUARE_LINKS["3000"] = "https://square.link/u/XXXXXXXX";
*/
