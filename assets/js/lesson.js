/* ============================================================
   Unity 星辰学院 · 课程页交互（lesson.js）
   代码一键复制、完成打卡(本地记录)、进度统计、目录高亮
   ============================================================ */
(function () {
  "use strict";

  // ---------- 代码块复制按钮 ----------
  document.querySelectorAll("pre").forEach(function (pre) {
    var btn = document.createElement("button");
    btn.className = "copy-btn";
    btn.textContent = "复制";
    pre.appendChild(btn);
    btn.addEventListener("click", function () {
      var code = pre.querySelector("code") ? pre.querySelector("code").innerText : pre.innerText;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(code).then(function () {
          btn.textContent = "已复制 ✓";
          setTimeout(function () { btn.textContent = "复制"; }, 1600);
        });
      } else {
        var ta = document.createElement("textarea");
        ta.value = code; document.body.appendChild(ta);
        ta.select(); document.execCommand("copy"); document.body.removeChild(ta);
        btn.textContent = "已复制 ✓";
        setTimeout(function () { btn.textContent = "复制"; }, 1600);
      }
    });
  });

  // ---------- 完成打卡（localStorage 进度） ----------
  var lessonKey = document.body.getAttribute("data-lesson-key");
  var doneBtn = document.getElementById("done-btn");
  if (lessonKey && doneBtn) {
    var isDone = localStorage.getItem("unity_done_" + lessonKey) === "1";
    function refresh() {
      doneBtn.classList.toggle("done", isDone);
      doneBtn.innerHTML = isDone ? "✓ 已完成本课" : "标记为已完成";
      var total = parseInt(localStorage.getItem("unity_total") || "300", 10);
      var done = parseInt(localStorage.getItem("unity_doneCount") || "0", 10);
      if (doneBtn.classList.contains("done") && !doneBtn.getAttribute("data-counted")) {
        // 首次标记时全局计数 +1
        localStorage.setItem("unity_doneCount", String(done + 1));
        doneBtn.setAttribute("data-counted", "1");
      }
    }
    doneBtn.addEventListener("click", function () {
      isDone = !isDone;
      localStorage.setItem("unity_done_" + lessonKey, isDone ? "1" : "0");
      // 重新统计全局已完成数量
      var count = 0;
      for (var i = 0; i < 300; i++) {
        var k = "lesson-" + String(i + 1).padStart(3, "0");
        if (localStorage.getItem("unity_done_" + k) === "1") count++;
      }
      localStorage.setItem("unity_doneCount", String(count));
      refresh();
      // 触发全局进度更新事件（主站可监听）
      window.dispatchEvent(new CustomEvent("unity-progress-change", { detail: { count: count } }));
    });
    refresh();
  }

  // ---------- 目录滚动高亮 ----------
  var tocLinks = document.querySelectorAll(".toc a");
  var headings = [];
  tocLinks.forEach(function (a) {
    var id = a.getAttribute("href");
    if (id && id.charAt(0) === "#") {
      var h = document.querySelector(id);
      if (h) headings.push({ id: id.slice(1), el: h, link: a });
    }
  });
  if (headings.length) {
    var toci = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        tocLinks.forEach(function (a) { a.classList.remove("active"); });
        var link = headings.find(function (h) { return h.id === en.target.id; });
        if (link) link.link.classList.add("active");
      });
    }, { rootMargin: "-18% 0px -70% 0px" });
    headings.forEach(function (h) { toci.observe(h.el); });
  }

  // ---------- 目录移动端折叠 ----------
  var tocToggle = document.querySelector(".toc-toggle");
  var tocBox = document.querySelector(".toc");
  if (tocToggle && tocBox) {
    tocToggle.addEventListener("click", function () {
      tocBox.classList.toggle("open");
      tocToggle.textContent = tocBox.classList.contains("open") ? "收起目录 ▲" : "展开目录 ▼";
    });
  }
})();
