# 分流规则镜像库

个人自用的 Loon 分流规则只读镜像，供配置在源站不稳时仍能加载。两个独立数据集，互不覆盖。

| 目录 | 内容 | 数量 | 体积 | 上游 |
|---|---|---|---|---|
| `loon/` | Loon 规则（kelee 版，合并格式） | 673 | 47.4 MB | [`luestr/ShuntRules`](https://github.com/luestr/ShuntRules) → `rule.kelee.one` |
| `bm7/` | Loon 规则（blackmatrix7 版，全量拆分格式） | 815 | 31.0 MB | [`blackmatrix7/ios_rule_script`](https://github.com/blackmatrix7/ios_rule_script) `rule/Loon` |

合计 **1489 个文件 / 78.4 MB**。文件未做改写，保持源站原文（含各文件自带的 `# UpdateTime` / `# RuleCount` / `# NAME` 注释），仅 `loon/Proxy.lsr` 与 `loon/TikTok.lsr` 两处有本地补丁，见下文。

## 两者的关系

`luestr/ShuntRules` 本身**不托管任何规则**，仓库里只有 1 个 README（125KB），列出一批导入链接，实际文件全部托管在 `rule.kelee.one`。

`ShuntRules` 的数据源是 `blackmatrix7/ios_rule_script`，它把上游拆分的 `X.list` + `X_Domain.list` + `X_Resolve.list` 合并成单文件 `X.lsr`。

```
blackmatrix7/ios_rule_script  rule/Loon   ← bm7/（原始拆分版，815 个）
        ↓ 合并 X.list + X_Domain.list + X_Resolve.list
luestr/ShuntRules  README 索引            ← 不托管文件，只是链接表
        ↓ 实际指向
rule.kelee.one/Loon/*.lsr                 ← loon/（合并版，673 个）
```

- `loon/` = 合并版，每条规则集一个文件，开箱即用
- `bm7/` = 上游原始拆分版，668 个分组目录，规则集最全（815 个 `.list`），适合做差异比对或按需取用

## 使用

**`loon/` 目录**

```
https://raw.githubusercontent.com/IamNewHands/loon-rules/main/loon/<名称>.lsr
```

**`bm7/` 目录**

```
https://raw.githubusercontent.com/IamNewHands/loon-rules/main/bm7/<分组>/<分组>.list
https://raw.githubusercontent.com/IamNewHands/loon-rules/main/bm7/<分组>/<分组>_Domain.list
https://raw.githubusercontent.com/IamNewHands/loon-rules/main/bm7/<分组>/<分组>_Resolve.list
```

## loon/ 的本地补丁

镜像非纯搬运，以下两处按上游 `blackmatrix7` 的更新做了手工修正：

| 文件 | 改动 | 原因 |
|---|---|---|
| `loon/Proxy.lsr` | **+9 条** | 上游 2026-10-26 新增港美股券商域名，kelee 尚未同步：`futu.cn`、`futubull.cn`、`longportapp.cn`、`openapi.longbridge.cn`、`openapi-quote.longbridge.cn`、`openapi-trade.longbridge.cn`、`schwab.com.cn`、`tigerbbs.cn`、`zhijianfengyi.cn`。7502 → 7511 条 |
| `loon/TikTok.lsr` | **−3 条** | kelee 的 `Tool/Loon/Lsr/TikTok.lsr`（2026-05-25 版）混入非 TikTok 域名：`cocacola.co.jp`、`api.snapkit.com`、`courses.snapsolve.com`。83 → 80 条 |

IP 类规则（`IP-CIDR` / `IP-ASN` / `GEOIP`）经 22 组逐一比对，与上游**完全一致，无任何新增**，未做改动。

`bm7/` 为纯镜像，未打补丁。

## 更新

不自动同步。需要刷新时重新抓取整批：

- `loon/`：`fetch_shunt.py`（私有仓库工作目录）
- `bm7/`：`fetch_bulk.py`
- 与上游的差异比对：`compare_upstream.py`

上游集合会增删改名，重跑后需比对文件数变化。

## 需要注意

`bm7/` 各分组的更新节奏差异很大：`bm7/Google/Google.list` 头部是 `# UPDATED: 2026-05-12`，而对应的 `loon/Google.lsr` 是 `2026-10-29`。`bm7/` 适合做结构参考与差异比对，实际配置仍以 `loon/` 为准。

## 未收录

- Clash 规则（668 个 `.yaml`，51.1 MB）—— Loon 不读取 Clash 格式，2026-11-01 已从本库移除
- `blackmatrix7` 的 `rule/Surge`（110.7 MB）、`rule/QuantumultX`（62.0 MB）—— 格式与 Loon 不通用

## 声明

- 所有规则内容版权归原作者与 [`blackmatrix7/ios_rule_script`](https://github.com/blackmatrix7/ios_rule_script) 项目所有。
- 本仓库仅作个人配置的可用性备份，不主张任何权利，不提供任何担保。
- 若原作者或上游维护者要求下架，将立即删除相应文件。
