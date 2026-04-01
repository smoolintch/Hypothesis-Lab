import Link from "next/link";

import { RecentBacktestList } from "@/features/strategy-card/components/recent-backtest-list";
import { StrategyCardList } from "@/features/strategy-card/components/strategy-card-list";

import styles from "./page.module.css";

export default function Home() {
  return (
    <main className={styles.page} data-testid="home-page">
      <div className={styles.inner}>
        <p className={styles.eyebrow}>Hypothesis Lab · MVP</p>
        <h1 className={styles.title}>从策略假设到可验证闭环</h1>
        <p className={styles.lead}>
          先把交易想法写成可复现的策略假设卡，再进入回测、查看结果、形成结论，最终沉淀为可执行的交易手册。当前阶段优先打通「假设 →
          回测 → 结果 → 结论 → 沉淀」这条主路径。
        </p>

        <StrategyCardList />
        <RecentBacktestList />

        <div className={styles.actions}>
          <Link
            className={styles.cta}
            data-testid="home-create-strategy-link"
            href="/strategy-cards/new"
          >
            新建策略假设
          </Link>
        </div>
      </div>
    </main>
  );
}
