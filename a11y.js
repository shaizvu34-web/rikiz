/* ============================================================
   תפריט נגישות — ללא תלות בשירות חיצוני
   ההעדפות נשמרות ב-localStorage ונטענות בכל עמוד באתר.
   ============================================================ */
(function () {
  "use strict";

  var KEY = "rikiz-a11y";
  var root = document.documentElement;

  // מתגים פשוטים: מפתח → מחלקה על תגית html
  var TOGGLES = [
    { key: "contrast", cls: "a11y-contrast", label: "ניגודיות גבוהה" },
    { key: "mono",     cls: "a11y-mono",     label: "גווני אפור" },
    { key: "links",    cls: "a11y-links",    label: "הדגשת קישורים" },
    { key: "readable", cls: "a11y-readable", label: "גופן קריא" },
    { key: "nomotion", cls: "a11y-nomotion", label: "עצירת אנימציות" },
    { key: "cursor",   cls: "a11y-cursor",   label: "סמן גדול" }
  ];

  var state = load();

  function load() {
    try {
      return JSON.parse(localStorage.getItem(KEY)) || { zoom: 0 };
    } catch (e) {
      return { zoom: 0 };
    }
  }

  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
  }

  function apply() {
    TOGGLES.forEach(function (t) { root.classList.toggle(t.cls, !!state[t.key]); });
    for (var i = 1; i <= 3; i++) root.classList.remove("a11y-zoom-" + i);
    if (state.zoom) root.classList.add("a11y-zoom-" + state.zoom);
  }

  apply();   // לפני בניית הממשק, כדי שלא תהיה הבהוב של המצב הקודם

  function el(tag, attrs, html) {
    var n = document.createElement(tag);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (html != null) n.innerHTML = html;
    return n;
  }

  function build() {
    // קישור דילוג לתוכן
    var target = document.querySelector("main") || document.querySelector("body > .wrap");
    if (target) {
      if (!target.id) target.id = "main-content";
      var skip = el("a", { href: "#" + target.id, "class": "skip-link" }, "דילוג לתוכן המרכזי");
      document.body.insertBefore(skip, document.body.firstChild);
    }

    var btn = el("button", {
      "class": "a11y-btn", type: "button",
      "aria-expanded": "false", "aria-controls": "a11y-panel",
      "aria-label": "פתיחת תפריט נגישות"
    }, '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="3.8" r="2"/>' +
       '<path d="M20.5 7.2c-2.6.9-5.4 1.4-8.5 1.4S6.1 8.1 3.5 7.2a1.1 1.1 0 0 0-.7 2.1c1.9.7 4 1.2 6.1 1.4l-.7 4.1-2 5.6a1.1 1.1 0 0 0 2.1.7l1.8-5.1h1.8l1.8 5.1a1.1 1.1 0 0 0 2.1-.7l-2-5.6-.7-4.1c2.1-.2 4.2-.7 6.1-1.4a1.1 1.1 0 0 0-.7-2.1z"/></svg>');

    var panel = el("div", {
      "class": "a11y-panel", id: "a11y-panel",
      role: "dialog", "aria-modal": "false", "aria-label": "התאמות נגישות"
    });

    panel.appendChild(el("h2", {}, "התאמות נגישות"));
    panel.appendChild(el("p", { "class": "a11y-sub" },
      "ההעדפות נשמרות בדפדפן שלך ויישמרו גם בביקור הבא."));

    var list = el("ul", {});

    // הגדלת תצוגה
    var zoomItem = el("li", {});
    var zoomBtn = el("button", { "class": "a11y-opt", type: "button", "aria-pressed": String(!!state.zoom) });
    function paintZoom() {
      zoomBtn.innerHTML = "הגדלת תצוגה" +
        '<span class="mark">' + (state.zoom ? [115, 130, 150][state.zoom - 1] + "%" : "רגיל") + "</span>";
      zoomBtn.setAttribute("aria-pressed", String(!!state.zoom));
    }
    paintZoom();
    zoomBtn.addEventListener("click", function () {
      state.zoom = (state.zoom + 1) % 4;
      apply(); save(); paintZoom();
    });
    zoomItem.appendChild(zoomBtn);
    list.appendChild(zoomItem);

    // שאר המתגים
    TOGGLES.forEach(function (t) {
      var li = el("li", {});
      var b = el("button", { "class": "a11y-opt", type: "button", "aria-pressed": String(!!state[t.key]) },
        t.label + '<span class="mark">' + (state[t.key] ? "פעיל" : "כבוי") + "</span>");
      b.addEventListener("click", function () {
        state[t.key] = !state[t.key];
        apply(); save();
        b.setAttribute("aria-pressed", String(!!state[t.key]));
        b.innerHTML = t.label + '<span class="mark">' + (state[t.key] ? "פעיל" : "כבוי") + "</span>";
      });
      li.appendChild(b);
      list.appendChild(li);
    });

    panel.appendChild(list);

    var reset = el("button", { "class": "a11y-reset", type: "button" }, "איפוס כל ההתאמות");
    reset.addEventListener("click", function () {
      state = { zoom: 0 };
      apply(); save();
      panel.querySelectorAll(".a11y-opt").forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
      TOGGLES.forEach(function (t, i) {
        var b = list.children[i + 1].firstChild;
        b.innerHTML = t.label + '<span class="mark">כבוי</span>';
      });
      paintZoom();
    });
    panel.appendChild(reset);

    panel.appendChild(el("p", { "class": "a11y-note" },
      'נתקלת בבעיית נגישות? <a href="https://shaizvu34-web.github.io/rikiz/accessibility.html">להצהרת הנגישות ולדרכי פנייה</a>'));

    function setOpen(open) {
      panel.setAttribute("data-open", String(open));
      btn.setAttribute("aria-expanded", String(open));
      btn.setAttribute("aria-label", (open ? "סגירת" : "פתיחת") + " תפריט נגישות");
      if (open) panel.querySelector(".a11y-opt").focus();
    }

    btn.addEventListener("click", function () {
      setOpen(panel.getAttribute("data-open") !== "true");
    });

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && panel.getAttribute("data-open") === "true") {
        setOpen(false); btn.focus();
      }
    });

    document.addEventListener("click", function (e) {
      if (panel.getAttribute("data-open") !== "true") return;
      if (!panel.contains(e.target) && !btn.contains(e.target)) setOpen(false);
    });

    document.body.appendChild(btn);
    document.body.appendChild(panel);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", build);
  } else {
    build();
  }
})();
