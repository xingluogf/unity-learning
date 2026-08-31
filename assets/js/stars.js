/* ============================================================
   Unity 星辰学院 · 星空特效引擎（stars.js）
   功能：动态星海、闪烁星星、流星、鼠标光晕、星座连线
   所有页面共用，自动运行
   ============================================================ */
(function () {
  "use strict";
  var canvas = document.getElementById("stars-canvas");
  if (!canvas) {
    // 兜底：若页面没有画布则自动创建一个
    canvas = document.createElement("canvas");
    canvas.id = "stars-canvas";
    document.body.insertBefore(canvas, document.body.firstChild);
  }
  var ctx = canvas.getContext("2d");
  var W, H, stars = [], meteors = [], links = [], DPR = Math.min(window.devicePixelRatio || 1, 2);
  var mouse = { x: -9999, y: -9999 };

  function resize() {
    W = window.innerWidth; H = window.innerHeight;
    canvas.width = W * DPR; canvas.height = H * DPR;
    canvas.style.width = W + "px"; canvas.style.height = H + "px";
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    initStars();
  }

  function rand(a, b) { return a + Math.random() * (b - a); }

  function initStars() {
    var count = Math.floor(W * H / 5200);
    count = Math.max(90, Math.min(count, 320));
    stars = [];
    for (var i = 0; i < count; i++) {
      stars.push({
        x: Math.random() * W,
        y: Math.random() * H,
        z: rand(0.25, 1),            // 深度（视差）
        r: rand(0.4, 1.9),
        base: rand(0, Math.PI * 2),  // 闪烁相位
        speed: rand(0.008, 0.03),
        hue: Math.random() < 0.18 ? rand(0, 360) : 0  // 少量彩色星
      });
    }
  }

  function spawnMeteor() {
    var fromRight = Math.random() < 0.5;
    meteors.push({
      x: fromRight ? W + 60 : rand(0, W),
      y: rand(0, H * 0.4),
      vx: fromRight ? -rand(6, 10) : rand(6, 10),
      vy: rand(2.5, 5),
      life: 1,
      len: rand(120, 260)
    });
  }

  function frame() {
    ctx.clearRect(0, 0, W, H);

    // ---- 背景深空渐变（让画布本身也带星云感）----
    var g = ctx.createRadialGradient(W * 0.5, H * 0.35, 0, W * 0.5, H * 0.35, W * 0.75);
    g.addColorStop(0, "rgba(30,41,90,.28)");
    g.addColorStop(1, "rgba(2,3,12,.0)");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);

    // ---- 星星 ----
    var t = Date.now() / 1000;
    for (var i = 0; i < stars.length; i++) {
      var s = stars[i];
      var tw = 0.5 + 0.5 * Math.sin(t * s.speed * 10 + s.base); // 闪烁
      var alpha = (0.25 + 0.75 * tw) * s.z;
      if (s.hue) {
        ctx.fillStyle = "hsla(" + s.hue + ",85%,80%," + alpha + ")";
      } else {
        ctx.fillStyle = "rgba(220,235,255," + alpha + ")";
      }
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.r * s.z, 0, Math.PI * 2);
      ctx.fill();
      // 亮星加十字星光
      if (s.z > 0.9 && tw > 0.85) {
        ctx.strokeStyle = "rgba(190,225,255," + (alpha * 0.5) + ")";
        ctx.lineWidth = 1;
        var L = 6;
        ctx.beginPath();
        ctx.moveTo(s.x - L, s.y); ctx.lineTo(s.x + L, s.y);
        ctx.moveTo(s.x, s.y - L); ctx.lineTo(s.x, s.y + L);
        ctx.stroke();
      }
    }

    // ---- 星座连线（鼠标附近较亮的星星连线，科技感）----
    links = [];
    for (var a = 0; a < stars.length; a++) {
      var sa = stars[a];
      if (sa.z < 0.8) continue;
      for (var b = a + 1; b < stars.length; b++) {
        var sb = stars[b];
        var dx = sa.x - sb.x, dy = sa.y - sb.y;
        var d2 = dx * dx + dy * dy;
        if (d2 < 150 * 150 && Math.random() < 0.06) {
          links.push({ ax: sa.x, ay: sa.y, bx: sb.x, by: sb.y, d: Math.sqrt(d2) });
        }
      }
    }
    ctx.lineWidth = 0.6;
    for (var k = 0; k < links.length; k++) {
      var ln = links[k];
      ctx.strokeStyle = "rgba(96,165,250," + (0.16 * (1 - ln.d / 150)) + ")";
      ctx.beginPath();
      ctx.moveTo(ln.ax, ln.ay); ctx.lineTo(ln.bx, ln.by);
      ctx.stroke();
    }

    // ---- 流星 ----
    if (Math.random() < 0.004 && meteors.length < 3) spawnMeteor();
    for (var m = meteors.length - 1; m >= 0; m--) {
      var mt = meteors[m];
      mt.x += mt.vx; mt.y += mt.vy; mt.life -= 0.012;
      if (mt.life <= 0) { meteors.splice(m, 1); continue; }
      var grad = ctx.createLinearGradient(mt.x, mt.y, mt.x - mt.vx * 0.28 * mt.len / 10, mt.y - mt.vy * 0.28 * mt.len / 10);
      grad.addColorStop(0, "rgba(255,255,255," + (0.95 * mt.life) + ")");
      grad.addColorStop(0.3, "rgba(120,200,255," + (0.5 * mt.life) + ")");
      grad.addColorStop(1, "rgba(120,200,255,0)");
      ctx.strokeStyle = grad;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(mt.x, mt.y);
      ctx.lineTo(mt.x - mt.vx * 3.2, mt.y - mt.vy * 3.2);
      ctx.stroke();
    }

    // ---- 鼠标光晕 ----
    if (mouse.x > -1000) {
      var mg = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, 140);
      mg.addColorStop(0, "rgba(34,211,238,.10)");
      mg.addColorStop(1, "rgba(34,211,238,0)");
      ctx.fillStyle = mg;
      ctx.fillRect(mouse.x - 140, mouse.y - 140, 280, 280);
    }
    requestAnimationFrame(frame);
  }

  // ---- 鼠标跟随（相对于页面）----
  window.addEventListener("mousemove", function (e) {
    mouse.x = e.clientX; mouse.y = e.clientY;
  });
  window.addEventListener("mouseleave", function () { mouse.x = -9999; mouse.y = -9999; });

  window.addEventListener("resize", resize);
  resize();
  frame();
})();
