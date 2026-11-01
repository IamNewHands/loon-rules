# 分流规则镜像库

个人自用的分流规则只读镜像，供 Loon / Clash 在源站不稳时仍能加载。三个独立数据集，互不覆盖。

| 目录 | 内容 | 数量 | 体积 | 上游 |
|---|---|---|---|---|
| `loon/` | Loon 规则（kelee 版） | 673 | 47.4 MB | [`luestr/ShuntRules`](https://github.com/luestr/ShuntRules) → `rule.kelee.one` |
| `bm7/` | Loon 规则（blackmatrix7 版，全量） | 815 | 31.0 MB | [`blackmatrix7/ios_rule_script`](https://github.com/blackmatrix7/ios_rule_script) `rule/Loon` |
| `clash/` | Clash 规则（kelee 版） | 668 | 51.1 MB | 同上 ShuntRules 索引 → `rule.kelee.one` |

合计 **2156 个文件 / 129.5 MB**。文件未做改写，保持源站原文（含各文件自带的 `# UpdateTime` / `# RuleCount` / `# NAME` 注释），仅 `loon/Proxy.lsr` 与 `loon/TikTok.lsr` 两处有本地补丁，见下文。

## 三者的关系

`luestr/ShuntRules` 本身**不托管任何规则**，仓库里只有 1 个 README（125KB），列出 668 条 Loon（`.lsr`）+ 668 条 Clash（`.yaml`）的导入链接，实际文件全部托管在 `rule.kelee.one`。

`ShuntRules` 的数据源是 `blackmatrix7/ios_rule_script`，它把上游拆分的 `X.list` + `X_Domain.list` + `X_Resolve.list` 合并成单文件 `X.lsr`。

- `loon/` = 合并版，每条规则集一个文件，开箱即用
- `bm7/` = 上游原始拆分版，668 个分组目录，规则集最全（815 个 `.list`），适合拿来做差异比对或按需取用

## 使用

**Loon（`loon/` 目录）**

```
https://raw.githubusercontent.com/IamNewHands/loon-rules/main/loon/<名称>.lsr
```

**Loon（`bm7/` 目录，按上游分组取）**

```
https://raw.githubusercontent.com/IamNewHands/loon-rules/main/bm7/<分组>/<分组>.list
https://raw.githubusercontent.com/IamNewHands/loon-rules/main/bm7/<分组>/<分组>_Domain.list
https://raw.githubusercontent.com/IamNewHands/loon-rules/main/bm7/<分组>/<分组>_Resolve.list
```

**Clash**

```
https://raw.githubusercontent.com/IamNewHands/loon-rules/main/clash/<名称>.yaml
```

## loon/ 的本地补丁

镜像非纯搬运，以下两处按上游 `blackmatrix7` 的更新做了手工修正：

| 文件 | 改动 | 原因 |
|---|---|---|
| `loon/Proxy.lsr` | **+9 条** | 上游 2026-10-26 新增港美股券商域名，kelee 尚未同步：`futu.cn`、`futubull.cn`、`longportapp.cn`、`openapi.longbridge.cn`、`openapi-quote.longbridge.cn`、`openapi-trade.longbridge.cn`、`schwab.com.cn`、`tigerbbs.cn`、`zhijianfengyi.cn`。7502 → 7511 条 |
| `loon/TikTok.lsr` | **−3 条** | kelee 的 `Tool/Loon/Lsr/TikTok.lsr`（2026-05-25 版）混入非 TikTok 域名：`cocacola.co.jp`、`api.snapkit.com`、`courses.snapsolve.com`。83 → 80 条 |

IP 类规则（`IP-CIDR` / `IP-ASN` / `GEOIP`）经 22 组逐一比对，与上游**完全一致，无任何新增**，未做改动。

`bm7/` 与 `clash/` 为纯镜像，未打补丁。

## 更新

不自动同步。需要刷新时重新抓取整批：

- `loon/`：`fetch_shunt.py`（私有仓库内）
- `bm7/` + `clash/`：`fetch_bulk.py`（私有仓库内）

上游集合会增删改名，重跑后需比对文件数变化。

## 未收录

`blackmatrix7` 的 `rule/Surge`（861 个 / 110.7 MB）与 `rule/QuantumultX`（689 个 / 62.0 MB）未镜像——格式与 Loon 不通用，且会使仓库膨胀到 300 MB 以上。需要时单独抓取。

## 声明

- 所有规则内容版权归原作者与 [`blackmatrix7/ios_rule_script`](https://github.com/blackmatrix7/ios_rule_script) 项目所有。
- 本仓库仅作个人配置的可用性备份，不主张任何权利，不提供任何担保。
- 若原作者或上游维护者要求下架，将立即删除相应文件。
