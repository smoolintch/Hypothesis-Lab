# samples

这里用于放样例策略说明、样例数据说明和固定回归样例文档。

固定行情样本本体不再直接放在 `docs/samples`，而是统一放在 `data/market`。
这样做的目的是把“说明文档”和“可被程序读取的数据文件”分开，避免后续回测引擎与 API 集成时继续混放。

当前已提供：
1. `ma-cross-btcusdt-4h.json`
2. `rsi-threshold-ethusdt-1d.json`

当前固定行情样本入口：
1. `data/market/README.md`
2. `data/market/fixture/BTCUSDT/4H/sample-v1`
3. `data/market/fixture/BTCUSDT/1D/sample-v1`
4. `data/market/fixture/ETHUSDT/4H/sample-v1`
5. `data/market/fixture/ETHUSDT/1D/sample-v1`

约定说明：
1. 样例策略文件保留在 `docs/samples`，用于人工阅读和后续回归样例管理。
2. 固定行情样本使用 `CSV + manifest.json`，统一放在 `data/market`。
3. 后续回测引擎或 API 需要消费固定样本时，应以 `data/market` 下的 manifest 为准，而不是从 `docs/samples` 推断数据路径。

建议后续继续补充：
1. 突破策略样例
2. 回归测试期望输出样本
3. 更多版本化固定行情切片
