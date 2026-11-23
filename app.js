/* ============================================================
   TOOLSTACK — logika (načtení obsahu + 3D let vpřed + hledání)
   Obsah se načítá z content/data.json (edituje se přes /admin
   nebo ručně). Když soubor nejde načíst (otevření přes file://),
   použije se offline záloha z data.js.
   ============================================================ */
(function () {
  "use strict";

  var track = document.getElementById("track");
  var scene = document.getElementById("scene");
  var progress = document.getElementById("progress");
  var searchInput = document.getElementById("search");
  var counterEl = document.getElementById("counter");

  // ---------- Matrix déšť (písmena + čísla) — běží po celou dobu ----------
  var fx = document.getElementById("fx");
  var rctx = fx.getContext("2d");
  var fontSize = 11;
  var rainCols = 0;
  var drops = [];
  var chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

  function sizeRain() {
    fx.width = window.innerWidth;
    fx.height = window.innerHeight;
    rainCols = Math.floor(fx.width / fontSize);
    drops = [];
    for (var i = 0; i < rainCols; i++) drops[i] = Math.random() * -60;
  }
  sizeRain();
  window.addEventListener("resize", sizeRain);

  function drawRain() {
    rctx.fillStyle = "rgba(6,6,7,0.04)";
    rctx.fillRect(0, 0, fx.width, fx.height);
    rctx.font = fontSize + "px monospace";
    for (var i = 0; i < rainCols; i++) {
      var ch = chars.charAt(Math.floor(Math.random() * chars.length));
      rctx.fillStyle = "#a6ffc0";  // jasná hlava
      rctx.fillText(ch, i * fontSize, drops[i] * fontSize);
      if (drops[i] * fontSize > fx.height && Math.random() > 0.975) drops[i] = 0;
      drops[i]++;
    }
    fx.style.opacity = "1";
    requestAnimationFrame(drawRain);
  }
  drawRain();

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function domainOf(url) {
    try {
      var a = document.createElement("a");
      a.href = url;
      return a.hostname || "";
    } catch (e) { return ""; }
  }

  function slugify(name) {
    return String(name)
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "") || "nastroj";
  }

  function categoryHTML(item) {
    var tools = item.tools
      .map(function (t) {
        var dom = domainOf(t.url);
        var logoSrc = dom ? "https://www.google.com/s2/favicons?domain=" + dom + "&sz=128" : "";
        var initial = (t.name || "?").charAt(0).toUpperCase();
        return (
          '<a class="tool" href="' + esc("nastroje/" + slugify(t.name) + ".html") + '" data-name="' +
          esc(t.name) + '">' +
          '<div class="tool-logo"><span class="tool-logo-letter">' + esc(initial) + "</span>" +
          (logoSrc ? '<img src="' + esc(logoSrc) + '" alt="" onerror="this.style.display=\'none\'" />' : "") +
          "</div>" +
          '<div class="tool-info">' +
          '<div class="tool-name">' + esc(t.name) + "</div>" +
          '<div class="tool-desc">' + esc(t.desc) + "</div>" +
          "</div>" +
          '<span class="tool-no">Nº ' + (t.no ? ("00" + t.no).slice(-3) : "000") + "</span>" +
          '<span class="tool-go">Vyzkoušet' +
          '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>' +
          "</span></a>"
        );
      })
      .join("");
    return (
      '<div class="shelf-tools">' + tools + "</div>" +
      '<div class="shelf-bar">' +
      '<span class="shelf-code">' + esc(item.code) + "</span>" +
      '<div class="shelf-meta"><div class="shelf-name">' + esc(item.name) + "</div>" +
      '<div class="shelf-count">' + item.tools.length + " nástrojů</div></div>" +
      '<span class="shelf-caret">\u203a</span>' +
      "</div>"
    );
  }

  function introHTML(site) {
    var title = (site.introTitle || "").replace(/\n/g, "<br>").replace(/\*(.+?)\*/g, "<em>$1</em>");
    return (
      '<div class="shelf-panel">' +
      '<div class="panel-boot">' + esc(site.introEyebrow || "") + "</div>" +
      '<div class="panel-title">' + title + "</div>" +
      "</div>"
    );
  }

  function outroHTML(site) {
    var steps = (site.steps || [])
      .map(function (s, i) {
        return (
          '<div class="step"><span class="step-num">' + (i + 1) + "</span>" +
          '<span class="step-txt"><b>' + esc(s.title) + "</b> — " + esc(s.text) + "</span></div>"
        );
      })
      .join("");
    return (
      '<div class="shelf-panel">' +
      '<div class="panel-boot">' + esc(site.outroEyebrow || "") + "</div>" +
      '<div class="panel-title panel-title--small">' + esc(site.outroTitle || "") + "</div>" +
      '<div class="panel-steps">' + steps + "</div>" +
      '<div class="panel-note">' + esc(site.outroNote || "") + "</div>" +
      "</div>"
    );
  }

  // ---------- Sestavení a spuštění ----------
  function boot(content) {
    var site = content.site || {};
    var categories = content.categories || [];

    var noCounter = 0;
    categories.forEach(function (c) { c.tools.forEach(function (t) { t.no = ++noCounter; }); });

    document.title = (site.name || "Katalog") + " — " + (site.tagline || "");
    var brandName = document.getElementById("brand-name");
    var brandTag = document.getElementById("brand-tag");
    if (brandName) brandName.textContent = site.name || "Katalog";
    if (brandTag) brandTag.textContent = site.tagline || "";

    var shelfEls = [];
    var items = [{ type: "intro" }].concat(
      categories.map(function (c) { c.type = "category"; return c; }),
      [{ type: "outro" }]
    );

    items.forEach(function (item) {
      var el = document.createElement("section");
      el.className = "shelf";
      if (item.type === "intro") el.innerHTML = introHTML(site);
      else if (item.type === "outro") el.innerHTML = outroHTML(site);
      else el.innerHTML = categoryHTML(item);
      track.appendChild(el);
      shelfEls.push(el);
    });

    // Indikátor pozice
    var dots = [];
    shelfEls.forEach(function (_, i) {
      var d = document.createElement("span");
      d.className = "dot";
      progress.appendChild(d);
      dots.push(d);
    });

    // Let vpřed (kamera tunelem)
    var spacing = 1600;
    var camZ = 0;
    var targetZ = 0;
    var maxZ = (shelfEls.length - 1) * spacing;

    function clampTarget(v) {
      targetZ = Math.max(0, Math.min(maxZ, v));
    }

    window.addEventListener("wheel", function (e) {
      e.preventDefault();
      clampTarget(targetZ + e.deltaY * 16);
    }, { passive: false });

    window.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight" || e.key === "ArrowDown") { e.preventDefault(); clampTarget(targetZ + spacing); }
      else if (e.key === "ArrowLeft" || e.key === "ArrowUp") { e.preventDefault(); clampTarget(targetZ - spacing); }
      else if (e.key === "Home") { e.preventDefault(); clampTarget(0); }
      else if (e.key === "End") { e.preventDefault(); clampTarget(maxZ); }
    });

    var dragging = false;
    var startX = 0;
    var startTargetZ = 0;

    scene.addEventListener("pointerdown", function (e) {
      dragging = true;
      startX = e.clientX;
      startTargetZ = targetZ;
      scene.classList.add("dragging");
    });
    window.addEventListener("pointermove", function (e) {
      if (!dragging) return;
      clampTarget(startTargetZ + (startX - e.clientX) * 4);
    });
    window.addEventListener("pointerup", function () {
      dragging = false;
      scene.classList.remove("dragging");
    });

    // Vykreslovací smyčka
    var openIndex = -1;
    function render() {
      camZ += (targetZ - camZ) * 0.1;
      if (Math.abs(targetZ - camZ) < 0.5) camZ = targetZ;

      var idx = camZ / spacing;
      var nearest = Math.max(0, Math.min(shelfEls.length - 1, Math.round(idx)));

      shelfEls.forEach(function (el, i) {
        var z = camZ - i * spacing;
        var ad = Math.abs(z);
        var opacity;
        if (z <= 0) {
          opacity = Math.max(0.35, 1 - (-z / spacing) * 0.55);
        } else {
          opacity = Math.max(0, 1 - z / (spacing * 0.5));
        }
        el.style.transform = "translate(-50%, -50%) translateZ(" + (z * 0.5).toFixed(1) + "px)";
        el.style.opacity = String(opacity.toFixed(3));
        el.style.zIndex = String(Math.round(1000 - ad));
        el.classList.toggle("is-active", ad < spacing * 0.35);
      });

      if (nearest !== openIndex) {
        openIndex = nearest;
        dots.forEach(function (d, i) { d.classList.toggle("on", i === nearest); });
      }

      requestAnimationFrame(render);
    }

    // Deep-link: ?pos=N skočí na N-tý stojan (0 = intro)
    try {
      var qp = new URLSearchParams(window.location.search).get("pos");
      if (qp !== null && !isNaN(qp)) {
        var pi0 = Math.max(0, Math.min(shelfEls.length - 1, parseInt(qp, 10)));
        camZ = pi0 * spacing;
        targetZ = camZ;
      }
    } catch (e0) {}

    render();

    // Hledání
    function filterTools(q) {
      var n = 0;
      var ql = q.trim().toLowerCase();
      shelfEls.forEach(function (el) {
        var tools = el.querySelectorAll(".tool");
        var matches = 0;
        tools.forEach(function (t) {
          var name = (t.getAttribute("data-name") || "").toLowerCase();
          var hit = !ql || name.indexOf(ql) !== -1;
          t.classList.toggle("hidden", !hit);
          t.classList.toggle("match", !!(ql && hit));
          if (hit) matches++;
        });
        el.classList.toggle("muted", !!(ql && matches === 0));
        n += matches;
      });
      counterEl.textContent = ql ? n + " nalezeno" : "";
    }

    searchInput.addEventListener("input", function () {
      filterTools(searchInput.value);
    });
  }

  // ---------- Načtení obsahu ----------
  fetch("content/data.json", { cache: "no-store" })
    .then(function (r) {
      if (!r.ok) throw new Error("missing content");
      return r.json();
    })
    .then(boot)
    .catch(function () {
      // Offline záloha (otevření přes file://)
      boot({
        site: (typeof SITE !== "undefined") ? SITE : {},
        categories: (typeof CATEGORIES !== "undefined") ? CATEGORIES : []
      });
    });
})();
