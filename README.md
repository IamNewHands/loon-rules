# Loon 分流规则镜像

[`luestr/ShuntRules`](https://github.com/luestr/ShuntRules) 索引的全部 Loon 分流规则镜像。

## 来源

上游索引仓库本身**不托管规则**，只有一个 README 列出 668 条 Loon（`.lsr`）与 668 条 Clash（`.yaml`）的导入链接，实际文件全部托管在 `rule.kelee.one`。本仓库把这些 Loon 规则抓取下来做只读镜像，用于主配置在源站不稳时仍能加载。

另收录 6 个不在索引内、但常用配置会引用的 `kelee.one/Tool/Loon/Lsr/` 文件：`AI`、`TikTok`、`LAN_SPLITTER`、`REGION_SPLITTER`、`SpeedtestChina`、`SpeedtestInternational`。

## 内容

| 项 | 数量 |
|---|---|
| 索引内规则 | 668 |
| 索引外特殊规则 | 6 |
| 落盘文件 | 673（`TikTok.lsr` 两个来源同名，保留 `Tool/Loon/Lsr` 版） |
| 总体积 | 47.4 MB |

文件未做任何改写，保持源站原文（含各文件自带的 `# UpdateTime` / `# RuleCount` 注释）。

## 使用

```
https://raw.githubusercontent.com/IamNewHands/loon-rules/main/loon/<名称>.lsr
```

例：

```
https://raw.githubusercontent.com/IamNewHands/loon-rules/main/loon/Google.lsr
https://raw.githubusercontent.com/IamNewHands/loon-rules/main/loon/Proxy.lsr
```

## 更新

镜像不自动同步。需要刷新时在上游索引页确认规则未改名后重新抓取整批。

## 声明

- 所有规则内容版权归原作者与 [`blackmatrix7/ios_rule_script`](https://github.com/blackmatrix7/ios_rule_script) 项目（上游数据源）所有。
- 本仓库仅作个人配置的可用性备份，不主张任何权利，不提供任何担保。
- 若原作者或上游维护者要求下架，将立即删除相应文件。
