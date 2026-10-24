/* Rustic Earth redesign — header state. Reveals are CSS scroll-driven
   (see style.css); no-JS and reduced-motion users get the full page. */
(function () {
  var head = document.getElementById("siteHead");
  var onScroll = function () {
    head.classList.toggle("scrolled", window.scrollY > 40);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });
})();
