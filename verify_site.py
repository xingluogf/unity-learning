# -*- coding: utf-8 -*-
import glob, os, json, re

root = os.path.dirname(os.path.abspath(__file__))
os.chdir(root)

# 1. 页面数量与大小
pages = glob.glob('lessons/lesson-*/index.html')
print('页面总数:', len(pages))
sizes = [(os.path.getsize(p), p) for p in pages]
sizes.sort()
print('最小:', sizes[0][0], sizes[0][1])
print('最大:', sizes[-1][0], sizes[-1][1])

# 2. lessons-data.js 校验
d = open('assets/js/lessons-data.js', encoding='utf-8').read()
m = re.search(r'window\.UNITY_LESSONS=(.*?);\n', d)
lessons = json.loads(m.group(1))
print('UNITY_LESSONS 条数:', len(lessons))
print('首条:', lessons[0])
print('末条:', lessons[-1])
nums = [l['num'] for l in lessons]
print('num 覆盖 1-300:', nums == list(range(1, 301)))
m2 = re.search(r'window\.UNITY_CHAPTERS=(.*?);\n', d)
chs = json.loads(m2.group(1))
print('UNITY_CHAPTERS 条数:', len(chs))
print('章节:', [(c['start'], c['end'], c['name']) for c in chs])

# 3. 页面内链接完整性
missing = []
for i in range(1, 301):
    p = os.path.join('lessons', 'lesson-%03d' % i, 'index.html')
    if not os.path.exists(p):
        missing.append(i)
print('缺失页面:', missing if missing else '无')

# 4. 抽查部分页面关键结构
def check(p, must):
    t = open(p, encoding='utf-8').read()
    ok = all(k in t for k in must)
    print('   ', p, '->', 'OK' if ok else 'MISS', '' if ok else [k for k in must if k not in t])
    return ok

print('抽查 lesson-001:')
check('lessons/lesson-001/index.html', ['LESSON 1', 'lesson-002/index.html', '数据', 'steps', '标记为已完成'])
print('抽查 lesson-185:')
check('lessons/lesson-185/index.html', ['LESSON 185', 'lesson-184/index.html', 'lesson-186/index.html', '音频', '常见错误与排查'])
print('抽查 lesson-300:')
check('lessons/lesson-300/index.html', ['LESSON 300', '恭喜完成全部课程', 'lesson-299/index.html'])
print('全部检查完成')
