# -*- coding: utf-8 -*-
"""
Unity 星辰学院 · 站点构建脚本
功能：
  1. 汇总 18 个章节的内容数据
  2. 为 300 节课生成 lessons/lesson-XXX/index.html
  3. 生成主站所需的 assets/js/lessons-data.js
  4. 输出构建统计与校验信息
用法：python build_site.py
"""
import os, re, json, html as html_mod

ROOT = os.path.dirname(os.path.abspath(__file__))
LESSONS_DIR = os.path.join(ROOT, "lessons")
DATA_DIR = os.path.join(ROOT, "build")

# ---------- 章节定义（顺序即学习路线） ----------
CHAPTERS = [
    {"name": "认识 Unity 与准备", "desc": "了解游戏引擎、注册账号、下载安装 Unity Hub 与引擎、认识主界面，迈出第一步。", "start": 1,   "end": 10},
    {"name": "Unity 界面初探",   "desc": "吃透五大窗口与工具栏、快捷键、布局切换，熟练操作编辑器是后续一切的基础。", "start": 11,  "end": 20},
    {"name": "场景与基础对象",   "desc": "创建对象、理解坐标与父子关系、灯光摄像机、材质天空盒、预制体，搭建你的第一个 3D 场景。", "start": 21,  "end": 35},
    {"name": "资源导入与管理",   "desc": "导入模型贴图音频字体、Asset Store 资源商店、Package Manager 包管理器、资源打包与设置。", "start": 36,  "end": 45},
    {"name": "C# 编程基础",      "desc": "从变量到类与继承，30 节系统讲解 C# 与 Unity API，写出你的第一个游戏脚本。", "start": 46,  "end": 75},
    {"name": "游戏对象与组件交互", "desc": "实例化、销毁、查找对象、标签层级、组件生命周期，让对象真正活起来。", "start": 76,  "end": 90},
    {"name": "物理系统",         "desc": "刚体、碰撞体、触发检测、力与扭矩、关节、射线检测，打造真实可信的物理世界。", "start": 91,  "end": 110},
    {"name": "输入系统",         "desc": "键盘鼠标触摸输入、新版 Input System、角色移动与视角控制，让玩家掌控游戏。", "start": 111, "end": 125},
    {"name": "动画系统",         "desc": "动画窗口、状态机、混合树、动画事件、骨骼动画，让角色栩栩如生。", "start": 126, "end": 145},
    {"name": "UI 界面系统",      "desc": "Canvas 画布、按钮、血条、菜单、对话框、背包、拖拽，做出专业游戏界面。", "start": 146, "end": 170},
    {"name": "音频系统",         "desc": "背景音乐、音效、3D 立体声、混音器 AudioMixer，为游戏配上声音。", "start": 171, "end": 185},
    {"name": "特效与粒子",       "desc": "粒子系统制作火焰爆炸雨雪、拖尾、光晕、后处理特效，让画面炫起来。", "start": 186, "end": 200},
    {"name": "2D 游戏开发",      "desc": "精灵、2D 物理、Tilemap 瓦片地图、2D 动画、像素风格，完成 2D 横版小游戏。", "start": 201, "end": 225},
    {"name": "3D 游戏进阶",      "desc": "第一/三人称控制、存档读档、场景切换、游戏管理器、敌人 AI，向完整游戏进发。", "start": 226, "end": 250},
    {"name": "寻路与导航",       "desc": "NavMesh 导航网格烘焙、寻路代理、动态障碍、Off-Mesh Link，实现聪明的敌人。", "start": 251, "end": 265},
    {"name": "性能优化",         "desc": "Profiler 性能分析、Draw Call 合批、LOD、对象池、GC 优化，让游戏跑得又稳又快。", "start": 266, "end": 280},
    {"name": "发布与进阶修炼",   "desc": "发布到 PC / WebGL / 手机，Player Settings 设置、设计模式、版本管理、职业路线。", "start": 281, "end": 295},
    {"name": "项目实战",         "desc": "跑酷、射击、塔防、平台跳跃四个完整小游戏实战，毕业设计压轴收尾。", "start": 296, "end": 300},
]

DIFF = {"入门": "badge-green", "初级": "badge-cyan", "中级": "badge-purple", "进阶": "badge-gold"}

def esc(s):
    return html_mod.escape(str(s), quote=False)

def render_code(code):
    if not code:
        return ""
    return '<pre><code class="lang-csharp">' + esc(code.strip("\n")) + "</code></pre>"

def render_section(sec):
    """渲染一个课程小节（标题 + 步骤/代码/提示）"""
    h = sec.get("h", "")
    parts = ['<div class="lesson-card reveal">', "<h2><span class='ic'>◆</span>%s</h2>" % esc(h)]
    # 引言
    if sec.get("lead"):
        parts.append("<p>%s</p>" % esc(sec["lead"]))
    # 详细步骤（核心：闭着眼也能做）
    steps = sec.get("steps", [])
    if steps:
        lis = "".join("<li>%s</li>" % esc(s) for s in steps)
        parts.append('<ol class="steps">%s</ol>' % lis)
    # 代码
    if sec.get("code"):
        parts.append(render_code(sec["code"]))
    # 代码后的补充说明
    if sec.get("after_code"):
        parts.append("<p>%s</p>" % esc(sec["after_code"]))
    # 提示
    for tip in sec.get("tips", []):
        icon = {"note": "💡", "warn": "⚠️", "danger": "⛔", "success": "✅"}.get(tip.get("t", "note"), "💡")
        cls = {"note": "tip-note", "warn": "tip-warn", "danger": "tip-danger", "success": "tip-success"}.get(tip.get("t", "note"), "tip-note")
        parts.append('<div class="tip %s"><span class="t-ic">%s</span><div>%s</div></div>' % (cls, icon, esc(tip.get("c", ""))))
    parts.append("</div>")
    return "\n".join(parts)

def render_errors(errors):
    if not errors:
        return ""
    items = []
    for e in errors:
        items.append(
            '<div class="tip tip-danger" style="margin:10px 0">'
            '<span class="t-ic">⛔</span><div>'
            "<b>错误：</b>%s<br><b>原因：</b>%s<br><b>解决：</b>%s"
            "</div></div>" % (esc(e.get("err", "")), esc(e.get("why", "")), esc(e.get("fix", "")))
        )
    return '\n<div class="lesson-card reveal"><h2><span class="ic">⚠</span>常见错误与排查</h2>' + "".join(items) + "</div>"

def render_exercise(ex):
    lis = "".join("<li>%s</li>" % esc(i) for i in ex)
    return ('\n<div class="lesson-card reveal"><h2><span class="ic">★</span>动手练习</h2>'
            '<div class="exercise"><h4>课后小任务（做出来才算真的学会）</h4><ul class="task-list">%s</ul></div></div>' % lis)

def render_summary(s):
    if not s:
        return ""
    return ('\n<div class="lesson-card reveal"><h2><span class="ic">✓</span>本节小结</h2>'
            "<p>%s</p></div>" % esc(s))

def render_objectives(objs):
    lis = "".join("<li>%s</li>" % esc(o) for o in objs)
    return '<div class="lesson-card reveal"><h2><span class="ic">🎯</span>本节学习目标</h2><ul class="task-list">%s</ul></div>' % lis

def render_intro(intro):
    return '<div class="lesson-card reveal"><h2><span class="ic">🚀</span>课程导读</h2><p>%s</p></div>' % esc(intro)

def render_toc(lesson, idx):
    """目录：学习目标 / 导读 / 各小节 / 常见错误 / 练习 / 小结"""
    items = ['<a href="#goal">本节目标</a>', '<a href="#intro">课程导读</a>']
    for i, sec in enumerate(lesson.get("sections", [])):
        items.append('<a href="#sec-%d">%s</a>' % (i, esc(sec.get("h", "小节"))))
    if lesson.get("errors"):
        items.append('<a href="#errors">常见错误</a>')
    if lesson.get("exercise"):
        items.append('<a href="#exercise">动手练习</a>')
    if lesson.get("summary"):
        items.append('<a href="#summary">本节小结</a>')
    return '\n'.join(items)

def render_lesson(lesson, prev, nxt, ch_name, ch_idx):
    """渲染单节课程 HTML 页面"""
    num = lesson["num"]
    key = "lesson-%03d" % num
    sections_html = "\n".join(render_section(s) for s in lesson.get("sections", []))
    toc_html = render_toc(lesson, num)

    # 上下课导航
    nav = '<div class="lesson-nav">'
    if prev:
        nav += '<a class="nav-item" href="../lesson-%03d/index.html"><span class="dir">← 上一课</span><span class="t">%s</span></a>' % (prev["num"], esc(prev["title"]))
    else:
        nav += '<div class="nav-item" style="opacity:.35;pointer-events:none"><span class="dir">已是第一课</span><span class="t">返回主站继续</span></div>'
    if nxt:
        nav += '<a class="nav-item next" href="../lesson-%03d/index.html"><span class="dir">下一课 →</span><span class="t">%s</span></a>' % (nxt["num"], esc(nxt["title"]))
    else:
        nav += '<div class="nav-item next" style="opacity:.35;pointer-events:none"><span class="dir">恭喜完成全部课程</span><span class="t">回到主站</span></div>'
    nav += "</div>"

    # 元信息
    meta = ('<div class="lesson-meta">'
            '<span class="meta-item">⏱ %s</span>'
            '<span class="meta-item">📊 难度：<span class="badge %s">%s</span></span>'
            '<span class="meta-item">🗂 第 %d 章 · %s</span>'
            '<span class="meta-item">📍 第 %d / 300 课</span>'
            "</div>") % (
                esc(lesson.get("time", "约 10 分钟")),
                DIFF.get(lesson.get("difficulty", "入门"), "badge-green"),
                esc(lesson.get("difficulty", "入门")),
                ch_idx, esc(ch_name), num)

    # 页头进度
    progress = ('<div class="lesson-progress"><span class="p-label">课程进度</span>'
                '<div class="progress-track"><div class="progress-fill" style="width:%.1f%%"></div></div>'
                '<span class="p-label" style="font-family:var(--font-mono)">%d / 300</span></div>'
                % (num / 300 * 100, num))

    # 正文各卡片（带锚点）
    body = []
    body.append('<div id="goal" class="reveal">' + render_objectives(lesson.get("objectives", [])) + "</div>")
    body.append('<div id="intro" class="reveal">' + render_intro(lesson.get("intro", "")) + "</div>")
    for i, s in enumerate(lesson.get("sections", [])):
        body.append('<div id="sec-%d" class="reveal">%s</div>' % (i, render_section(s)))
    if lesson.get("errors"):
        body.append('<div id="errors" class="reveal">%s</div>' % render_errors(lesson["errors"]))
    if lesson.get("exercise"):
        body.append('<div id="exercise" class="reveal">%s</div>' % render_exercise(lesson["exercise"]))
    if lesson.get("summary"):
        body.append('<div id="summary" class="reveal">%s</div>' % render_summary(lesson["summary"]))
    body_html = "\n".join(body)

    page = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>第 {num} 课：{title} · Unity 星辰学院</title>
<meta name="description" content="{title} · Unity 星辰学院第 {num} 课，超详细步骤，闭着眼都能做。">
<link rel="icon" href="../../favicon.ico">
<link rel="stylesheet" href="../../assets/css/theme.css">
<link rel="stylesheet" href="../../assets/css/lesson.css">
<style>
.lesson-layout{{padding-top:120px}}
</style>
</head>
<body data-lesson-key="{key}">
<canvas id="stars-canvas"></canvas>
<div class="grid-overlay"></div>
<div class="top-bar"></div>

<nav class="navbar">
  <div class="brand"><div class="logo">U</div><span>Unity <span style="color:var(--cyan)">星辰学院</span></span></div>
  <div class="nav-links">
    <a href="../../index.html">首页</a>
    <a href="../../index.html#course">课程表</a>
    <a href="../../index.html#chapters">章节导览</a>
    <a href="../lesson-001/index.html">第 1 课</a>
    <a href="../../index.html#start" class="btn btn-cyan btn-sm" style="margin-left:8px">返回主站</a>
  </div>
  <div class="nav-burger"><span></span><span></span><span></span></div>
</nav>

<div class="lesson-layout">
  <div class="crumb">
    <a href="../../index.html">首页</a><span class="sep">/</span>
    <a href="../../index.html#chapters">第 {ch_idx} 章 · {ch_name}</a><span class="sep">/</span>
    <span>第 {num} 课</span>
  </div>

  <div class="lesson-hero reveal">
    <span class="lesson-no">LESSON {num} · {ch_name}</span>
    <h1>{title}</h1>
    <p class="sub">{summary}</p>
    {meta}
  </div>

  {progress}

  <div style="display:grid;grid-template-columns:240px 1fr;gap:26px;align-items:start">
    <aside>
      <button class="toc-toggle">展开目录 ▼</button>
      <div class="toc"><h3>本课目录</h3>{toc}</div>
    </aside>
    <div class="lesson-body">
      {body}
    </div>
  </div>

  <div class="done-zone">
    <button id="done-btn" class="">标记为已完成</button>
    <p style="margin-top:10px;font-size:13px;color:var(--text-3)">完成打卡后，主站会实时更新你的学习进度 🎯</p>
  </div>

  {nav}
</div>

<footer class="footer">
  <div class="brand" style="justify-content:center"><div class="logo">U</div><span>Unity 星辰学院</span></div>
  <div class="f-links">
    <a href="../../index.html">首页</a>
    <a href="../../index.html#course">课程表</a>
    <a href="../lesson-001/index.html">第 1 课</a>
    <a href="../lesson-300/index.html">最后一课</a>
  </div>
  <p>© 2026 Unity 星辰学院 · 300 节零基础到精通全攻略</p>
</footer>

<button class="to-top" title="返回顶部">↑</button>

<script src="../../assets/js/stars.js"></script>
<script src="../../assets/js/common.js"></script>
<script src="../../assets/js/lesson.js"></script>
</body>
</html>""".format(
        num=num, key=key, title=esc(lesson["title"]),
        summary=esc(lesson.get("summary", "")),
        meta=meta, toc=toc_html, body=body_html,
        nav=nav, progress=progress,
        ch_name=esc(ch_name), ch_idx=ch_idx)
    return page

def collect_lessons():
    """从 build/ 下的数据文件汇总全部课程（按 num 排序）"""
    lessons = {}
    for fname in sorted(os.listdir(DATA_DIR)):
        if fname.startswith("lessons_part") and fname.endswith(".py"):
            ns = {}
            with open(os.path.join(DATA_DIR, fname), encoding="utf-8") as f:
                exec(compile(f.read(), fname, "exec"), ns)
            for l in ns.get("LESSONS_PART", []):
                lessons[l["num"]] = l
    missing = [n for n in range(1, 301) if n not in lessons]
    if missing:
        raise SystemExit("缺少课程: %s" % missing)
    return [lessons[n] for n in range(1, 301)]

def chapter_of(num):
    for i, c in enumerate(CHAPTERS):
        if c["start"] <= num <= c["end"]:
            return i, c
    return 0, CHAPTERS[0]

def build():
    lessons = collect_lessons()
    total = len(lessons)
    print("汇总课程总数:", total)

    # 生成课程页面
    for i, l in enumerate(lessons):
        num = l["num"]
        ch_idx, ch = chapter_of(num)
        prev = lessons[i - 1] if i > 0 else None
        nxt = lessons[i + 1] if i < total - 1 else None
        d = os.path.join(LESSONS_DIR, "lesson-%03d" % num)
        os.makedirs(d, exist_ok=True)
        page = render_lesson(l, prev, nxt, ch["name"], ch_idx + 1)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(page)

    # 生成主站课程数据 js
    js_lessons = []
    for l in lessons:
        ch_idx, ch = chapter_of(l["num"])
        js_lessons.append({
            "num": l["num"],
            "key": "lesson-%03d" % l["num"],
            "title": l["title"],
            "summary": l.get("summary", ""),
            "keywords": l.get("keywords", ""),
            "chapter": str(ch_idx),
            "chapterName": ch["name"],
            "url": "lessons/lesson-%03d/index.html" % l["num"],
        })
    js_chapters = []
    for i, c in enumerate(CHAPTERS):
        start = c["start"]
        count = c["end"] - c["start"] + 1
        keys = ["lesson-%03d" % n for n in range(start, start + count)]
        js_chapters.append({
            "name": c["name"], "desc": c["desc"],
            "start": start, "end": c["end"], "count": count, "list": keys,
        })
    js = "window.UNITY_LESSONS=" + json.dumps(js_lessons, ensure_ascii=False) + ";\n"
    js += "window.UNITY_CHAPTERS=" + json.dumps(js_chapters, ensure_ascii=False) + ";\n"
    with open(os.path.join(ROOT, "assets", "js", "lessons-data.js"), "w", encoding="utf-8") as f:
        f.write(js)

    # 统计
    ch_detail = {}
    for l in lessons:
        ch_idx, _ = chapter_of(l["num"])
        ch_detail.setdefault(ch_idx, []).append(l["num"])
    print("=" * 50)
    for i, c in enumerate(CHAPTERS):
        nums = ch_detail[i]
        print("第 %02d 章 %-12s 课 %d - %d（%d 节）" % (i + 1, c["name"], c["start"], c["end"], len(nums)))
    print("=" * 50)
    print("课程页面已生成:", total)
    print("数据文件: assets/js/lessons-data.js")

    # 校验：所有页面文件数 & 链接
    count_files = 0
    for i in range(1, 301):
        p = os.path.join(LESSONS_DIR, "lesson-%03d" % i, "index.html")
        if os.path.exists(p):
            count_files += 1
    print("校验：课程目录内 index.html 数量 =", count_files)
    return total

if __name__ == "__main__":
    build()
