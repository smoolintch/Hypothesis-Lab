import Link from "next/link";

import styles from "./page.module.css";

export default function Home() {
  return (
    <main className={styles.page} data-testid="home-page">
      <div className={styles.inner}>
        <p className={styles.eyebrow}>Hypothesis Lab · MVP</p>
        <h1 className={styles.title}>从策略假设到可验证闭环</h1>
        <p className={styles.lead}>
          先把交易想法写成可复现的策略假设卡，再进入回测、查看结果、形成结论，最终沉淀为可执行的交易手册。当前阶段优先打通「假设 →
          回测 → 结果占位」这条主路径。
        </p>

        <section className={styles.panel} aria-labelledby="home-loop-heading">
          <h2 className={styles.panelTitle} id="home-loop-heading">
            MVP 核心闭环
          </h2>
          <ol className={styles.loop}>
            <li>策略假设（策略卡）</li>
            <li>回测</li>
            <li>结果</li>
            <li>结论</li>
          </ol>
          <p className={styles.note}>
            当前首页为最小起始页，不依赖策略列表接口；创建策略后可通过保存成功后的跳转或自行保存的链接进入编辑与回测。
          </p>
        </section>

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
