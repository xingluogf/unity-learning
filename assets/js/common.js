/* ============================================================
   Unity 星辰学院 · 通用交互（common.js）
   导航栏、汉堡菜单、滚动显现、返回顶部、阅读进度条、鼠标光晕
   ============================================================ */
(function () {
  "use strict";

  // ---------- 导航栏滚动状态 ----------
  var navbar = document.querySelector(".navbar");
  window.addEventListener("scroll", function () {
    if (navbar) navbar.classList.toggle("scrolled", window.scrollY > 20);
  }, { passive: true });

  // ---------- 汉堡菜单 ----------
  var burger = document.querySelector(".nav-burger");
  var linksBox = document.querySelector(".nav-links");
  if (burger && linksBox) {
    burger.addEventListener("click", function () { linksBox.classList.toggle("open"); });
    linksBox.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { linksBox.classList.remove("open"); });
    });
  }

  // ---------- 滚动显现 ----------
  var revealEls = document.querySelectorAll(".reveal");
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
    });
  }, { threshold: 0.12 });
  revealEls.forEach(function (el) { io.observe(el); });

  // ---------- 返回顶部 ----------
  var toTop = document.querySelector(".to-top");
  if (toTop) {
    window.addEventListener("scroll", function () {
      toTop.classList.toggle("show", window.scrollY > 600);
    }, { passive: true });
    toTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  // ---------- 顶部阅读进度条 ----------
  var topBar = document.querySelector(".top-bar");
  if (topBar) {
    window.addEventListener("scroll", function () {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      var p = h > 0 ? (window.scrollY / h) * 100 : 0;
      topBar.style.width = p + "%";
    }, { passive: true });
  }

  // ---------- 鼠标光晕跟随 ----------
  var glow = document.createElement("div");
  glow.className = "cursor-glow";
  document.body.appendChild(glow);
  var tx = -180, ty = -180, cx = -180, cy = -180;
  window.addEventListener("mousemove", function (e) {
    tx = e.clientX - 180; ty = e.clientY - 180;
  }, { passive: true });
  (function follow() {
    cx += (tx - cx) * 0.12; cy += (ty - cy) * 0.12;
    glow.style.transform = "translate(" + cx + "px," + cy + "px)";
    requestAnimationFrame(follow);
  })();

  // ---------- 数字滚动动画 ----------
  var counters = document.querySelectorAll("[data-count]");
  var cio = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) {
      if (!en.isIntersecting) return;
      var el = en.target, target = parseFloat(el.getAttribute("data-count"));
      var suffix = el.getAttribute("data-suffix") || "";
      var dur = 1400, start = performance.now();
      (function tick(now) {
        var p = Math.min((now - start) / dur, 1);
        var ease = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.floor(target * ease) + suffix;
        if (p < 1) requestAnimationFrame(tick);
      })(start);
      cio.unobserve(el);
    });
  }, { threshold: 0.4 });
  counters.forEach(function (el) { cio.observe(el); });
})();
