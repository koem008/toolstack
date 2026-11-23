/* ============================================================
   Měření a ověření webu (načítá nastavení z config.js).
   Spouští se automaticky na každé stránce.
   ============================================================ */
(function () {
  "use strict";
  var cfg = window.CONFIG || {};

  // Google Search Console — ověřovací meta tag
  if (cfg.GSC_VERIFICATION) {
    var m = document.createElement("meta");
    m.name = "google-site-verification";
    m.content = cfg.GSC_VERIFICATION;
    document.head.appendChild(m);
  }

  // Google Analytics 4 — měří se jen když je vyplněné ID
  if (cfg.GA_MEASUREMENT_ID) {
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(cfg.GA_MEASUREMENT_ID);
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;
    gtag("js", new Date());
    gtag("config", cfg.GA_MEASUREMENT_ID);
  }
})();
