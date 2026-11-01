#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""同步上游分流规则到本仓库。

数据源
  loon/  luestr/ShuntRules README 索引 -> rule.kelee.one（合并版 .lsr）
         + 6 个索引外的 kelee.one/Tool/Loon/Lsr/ 特殊文件
  bm7/   blackmatrix7/ios_rule_script rule/Loon 全量（拆分版 .list）

本地补丁在同步后重新应用，保证幂等。
"""
import os
import re
import sys
import time
import gzip
import json
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
UA = 'Mozilla/5.0 (compatible; loon-rules-sync/1.0)'
SHUNT_README = 'https://raw.githubusercontent.com/luestr/ShuntRules/main/README.md'
BM7_API = 'https://api.github.com/repos/blackmatrix7/ios_rule_script/git/trees/master?recursive=1'
BM7_RAW = 'https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/'

# 索引里没有、但常用配置会引用的特殊文件
EXTRA = [
    'https://kelee.one/Tool/Loon/Lsr/SpeedtestInternational.lsr',
    'https://kelee.one/Tool/Loon/Lsr/SpeedtestChina.lsr',
    'https://kelee.one/Tool/Loon/Lsr/AI.lsr',
    'https://kelee.one/Tool/Loon/Lsr/TikTok.lsr',
    'https://kelee.one/Tool/Loon/Lsr/LAN_SPLITTER.lsr',
    'https://kelee.one/Tool/Loon/Lsr/REGION_SPLITTER.lsr',
]

# ---- 本地补丁 ----
# 上游已加、kelee 尚未同步的港美股券商域名
PROXY_ADD = [
    'futu.cn', 'futubull.cn', 'longportapp.cn',
    'openapi.longbridge.cn', 'openapi-quote.longbridge.cn', 'openapi-trade.longbridge.cn',
    'schwab.com.cn', 'tigerbbs.cn', 'zhijianfengyi.cn',
]
# kelee Tool/Loon/Lsr/TikTok.lsr 混入的非 TikTok 域名
TIKTOK_DROP = {'cocacola.co.jp', 'api.snapkit.com', 'courses.snapsolve.com'}
PROXY_MARK = '# --- 本地补丁：上游 blackmatrix7 新增港美股券商域名（kelee 未同步）---'
TIKTOK_MARK = '# --- 本地补丁：移除误入的非 TikTok 域名 ---'

MIN_SUCCESS = 0.95  # 成功率低于此值则整体放弃，不覆盖现有文件


def fetch(url, tries=3, timeout=40):
    last = ''
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read(), ''
        except Exception as e:
            last = '%s: %s' % (type(e).__name__, str(e)[:60])
            if i < tries - 1:
                time.sleep(1 + i)
    return None, last


def valid(body):
    if not body or len(body) < 5:
        return False
    head = body[:300].lstrip().lower()
    return not (head.startswith(b'<!doctype') or head.startswith(b'<html'))


def fetch_many(jobs, label):
    """jobs: [(rel_path, url)] -> ({rel: bytes}, [failures])"""
    out, fail = {}, []

    def work(j):
        rel, url = j
        body, err = fetch(url)
        if body is None or not valid(body):
            return rel, None, err or 'invalid'
        return rel, body, ''

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=12) as ex:
        for i, (rel, body, err) in enumerate(ex.map(work, jobs), 1):
            if body is None:
                fail.append((rel, err))
            else:
                out[rel] = body
            if i % 100 == 0:
                print('  %s %d/%d ok=%d fail=%d %.0fs' % (label, i, len(jobs), len(out), len(fail), time.time() - t0))
    print('%s: 成功 %d / 失败 %d / %.0fs' % (label, len(out), len(fail), time.time() - t0))
    for rel, err in fail[:15]:
        print('   失败 %-45s %s' % (rel, err))
    return out, fail


def apply_patches(files):
    """在内存中应用本地补丁，返回改动说明列表。"""
    changed = []

    p = 'loon/Proxy.lsr'
    if p in files:
        s = files[p].decode('utf-8', 'replace')
        have = {l.strip().lower() for l in s.splitlines()}
        add = [d for d in PROXY_ADD if ('domain-suffix, %s' % d).lower() not in have]
        if add:
            if not s.endswith('\n'):
                s += '\n'
            s += '\n%s\n' % PROXY_MARK
            s += ''.join('DOMAIN-SUFFIX, %s\n' % d for d in add)
            files[p] = s.encode('utf-8')
            changed.append('Proxy +%d' % len(add))

    p = 'loon/TikTok.lsr'
    if p in files:
        lines = files[p].decode('utf-8', 'replace').split('\n')
        kept, removed = [], []
        for l in lines:
            t = l.strip()
            if t and not t.startswith('#') and ',' in t:
                key = t.split(',', 1)[1].strip().lower()
                if key in TIKTOK_DROP:
                    removed.append(key)
                    continue
            kept.append(l)
        if removed:
            files[p] = '\n'.join(kept).encode('utf-8')
            changed.append('TikTok -%d' % len(removed))
    return changed


def write_tree(subdir, files):
    """把 {rel: bytes} 写入 <ROOT>/<subdir>，删除该目录下不再存在的文件。"""
    base = os.path.join(ROOT, subdir)
    want = set()
    for rel, body in files.items():
        dst = os.path.join(base, rel)
        want.add(os.path.abspath(dst))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        old = None
        if os.path.exists(dst):
            with open(dst, 'rb') as f:
                old = f.read()
        if old != body:
            with open(dst, 'wb') as f:
                f.write(body)
    removed = 0
    for root, _, fs in os.walk(base):
        for fn in fs:
            p = os.path.abspath(os.path.join(root, fn))
            if p not in want:
                os.remove(p)
                removed += 1
    # 清理空目录
    for root, dirs, fs in os.walk(base, topdown=False):
        if root != base and not os.listdir(root):
            os.rmdir(root)
    return removed


def main():
    # ---- 1. loon/ from ShuntRules index ----
    print('读取 ShuntRules 索引...')
    body, err = fetch(SHUNT_README)
    if body is None:
        print('索引读取失败: %s' % err)
        return 1
    text = body.decode('utf-8', 'replace')
    urls = sorted({m.group(1) for m in re.finditer(r'rules=(https?://\S+\.lsr)', text)})
    print('索引内 Loon 规则: %d' % len(urls))
    jobs = [(u.rsplit('/', 1)[-1], u) for u in urls]
    # EXTRA 优先：索引里的 TikTok.lsr 是 35 条的纯 TikTok 版，而 Tool/Loon/Lsr 的
    # 80 条版覆盖面更全（含字节 CDN），主配置一直用后者，同名时必须让 EXTRA 覆盖索引
    for u in EXTRA:
        n = u.rsplit('/', 1)[-1]
        jobs = [j for j in jobs if j[0] != n]
        jobs.append((n, u))
    loon, loon_fail = fetch_many(jobs, 'loon')
    if len(loon) < len(jobs) * MIN_SUCCESS:
        print('loon 成功率过低（%d/%d），放弃本次同步' % (len(loon), len(jobs)))
        return 1

    # ---- 2. bm7/ from blackmatrix7 ----
    print('读取 blackmatrix7 文件树...')
    api = BM7_API
    headers = {'User-Agent': UA, 'Accept-Encoding': 'gzip'}
    if os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    tree = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(api, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as r:
                raw = r.read()
                if r.headers.get('Content-Encoding') == 'gzip':
                    raw = gzip.decompress(raw)
            tree = json.loads(raw)['tree']
            break
        except Exception as e:
            print('  文件树读取第 %d 次失败: %s: %s' % (attempt + 1, type(e).__name__, str(e)[:70]))
            time.sleep(3 + attempt * 3)
    if tree is None:
        print('文件树读取失败，放弃本次同步')
        return 1
    bm_jobs = []
    for t in tree:
        p = t.get('path', '')
        if t.get('type') == 'blob' and p.startswith('rule/Loon/') and p.endswith('.list'):
            bm_jobs.append((p[len('rule/Loon/'):], BM7_RAW + p))
    print('blackmatrix7 rule/Loon: %d 个 .list' % len(bm_jobs))
    bm7, bm_fail = fetch_many(bm_jobs, 'bm7')
    if len(bm7) < len(bm_jobs) * MIN_SUCCESS:
        print('bm7 成功率过低（%d/%d），放弃本次同步' % (len(bm7), len(bm_jobs)))
        return 1

    # ---- 3. 补丁 ----
    files = {'loon/' + k: v for k, v in loon.items()}
    files.update({'bm7/' + k: v for k, v in bm7.items()})
    changed = apply_patches(files)
    print('补丁应用: %s' % (', '.join(changed) if changed else '无变化'))

    # ---- 4. 落盘 ----
    loon_files = {k[5:]: v for k, v in files.items() if k.startswith('loon/')}
    bm7_files = {k[4:]: v for k, v in files.items() if k.startswith('bm7/')}
    del_loon = write_tree('loon', loon_files)
    del_bm7 = write_tree('bm7', bm7_files)
    print('写入 loon %d 个（删除 %d）, bm7 %d 个（删除 %d）'
          % (len(loon_files), del_loon, len(bm7_files), del_bm7))

    summary = {
        'synced_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'loon': {'total': len(loon_files), 'index': len(urls), 'extra': len(EXTRA), 'fail': len(loon_fail)},
        'bm7': {'total': len(bm7_files), 'fail': len(bm_fail)},
        'patches': changed,
    }
    with open(os.path.join(ROOT, 'sync-status.json'), 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False))

    # 输出给 workflow 用
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
            f.write('changed=%s\n' % ('true' if (len(loon_fail) == 0 and len(bm_fail) == 0) else 'false'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
