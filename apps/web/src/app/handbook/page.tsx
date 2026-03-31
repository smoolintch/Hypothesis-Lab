import Link from "next/link";

import styles from "../page.module.css";

export default function HandbookPage() {
  return (
    <main className={styles.page} data-testid="handbook-page">
      <div className={styles.inner}>
        <p className={styles.eyebrow}>Handbook · MVP</p>
        <h1 className={styles.title}>交易手册</h1>
        <p className={styles.lead}>
          将优质策略结论沉淀为可执行的交易规则。在回测结果页保存结论、选择「加入交易手册」后，条目将沉淀至此。
        </p>

        <section className={styles.panel} data-testid="handbook-placeholder">
          <h2 className={styles.panelTitle}>手册条目</h2>
          <p className={styles.note}>
            「加入交易手册」功能已开通。当前阶段侧重策略假设 →
            回测 → 结论 → 沉淀的完整闭环，手册条目列表将在后续版本中提供。
          </p>
        </section>

        <div className={styles.actions}>
          <Link
            className={styles.cta}
            data-testid="handbook-create-strategy-link"
            href="/strategy-cards/new"
          >
            新建策略假设
          </Link>
        </div>
      </div>
    </main>
  );
}
