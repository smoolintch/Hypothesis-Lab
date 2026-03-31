"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { ApiClientError } from "@/lib/api/client";

import { useCreateConclusionMutation } from "../api";
import type { ConclusionNextAction, ConclusionResponse } from "../types";
import { CONCLUSION_NEXT_ACTION_LABELS } from "../types";
import styles from "../backtest-run.module.css";

// ─── form schema ──────────────────────────────────────────────────────────────

const NEXT_ACTION_VALUES = [
  "rerun",
  "refine_rules",
  "observe_only",
  "add_to_handbook",
  "discard",
] as const;

const conclusionSchema = z.object({
  is_worth_researching: z.boolean(),
  can_accept_drawdown: z.boolean(),
  next_action: z.enum(NEXT_ACTION_VALUES),
  market_condition_notes: z.string().max(2000, "最多 2000 字").optional(),
  notes: z.string().max(4000, "最多 4000 字").optional(),
});

type ConclusionFormValues = z.infer<typeof conclusionSchema>;

// ─── saved view ───────────────────────────────────────────────────────────────

function SavedConclusionView({ conclusion }: { conclusion: ConclusionResponse }) {
  return (
    <div
      className={styles.conclusionSaved}
      data-testid="conclusion-saved"
    >
      <div className={`${styles.message} ${styles.messageSuccess}`}>
        <p>结论已保存。</p>
      </div>

      <div className={styles.conclusionSummary}>
        <div className={styles.conclusionRow}>
          <span className={styles.label}>是否值得继续研究</span>
          <span className={styles.value}>
            {conclusion.is_worth_researching ? "✓ 是" : "✗ 否"}
          </span>
        </div>
        <div className={styles.conclusionRow}>
          <span className={styles.label}>是否接受当前回撤</span>
          <span className={styles.value}>
            {conclusion.can_accept_drawdown ? "✓ 是" : "✗ 否"}
          </span>
        </div>
        <div className={styles.conclusionRow}>
          <span className={styles.label}>下一步行动</span>
          <span className={styles.value}>
            {CONCLUSION_NEXT_ACTION_LABELS[conclusion.next_action] ?? conclusion.next_action}
          </span>
        </div>
        {conclusion.market_condition_notes && (
          <div className={styles.conclusionRow}>
            <span className={styles.label}>适用行情说明</span>
            <span className={styles.value}>{conclusion.market_condition_notes}</span>
          </div>
        )}
        {conclusion.notes && (
          <div className={styles.conclusionRow}>
            <span className={styles.label}>备注</span>
            <span className={styles.value}>{conclusion.notes}</span>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── main form ────────────────────────────────────────────────────────────────

interface ConclusionFormProps {
  resultId: string;
  strategyCardId: string;
}

export function ConclusionForm({ resultId, strategyCardId }: ConclusionFormProps) {
  const [savedConclusion, setSavedConclusion] = useState<ConclusionResponse | null>(null);
  const mutation = useCreateConclusionMutation(strategyCardId);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ConclusionFormValues>({
    resolver: zodResolver(conclusionSchema),
    defaultValues: {
      is_worth_researching: false,
      can_accept_drawdown: false,
      next_action: "observe_only",
      market_condition_notes: "",
      notes: "",
    },
  });

  if (savedConclusion) {
    return <SavedConclusionView conclusion={savedConclusion} />;
  }

  const serverErrorMessage = (() => {
    if (!mutation.error) return null;
    const err =
      mutation.error instanceof ApiClientError
        ? mutation.error
        : new ApiClientError({ status: 500, fallbackMessage: "保存结论失败。" });
    if (err.code === "CONCLUSION_ALREADY_EXISTS") {
      return "该回测结果已有结论，无法重复保存。";
    }
    return err.message;
  })();

  function onSubmit(values: ConclusionFormValues) {
    mutation.mutate(
      {
        backtest_result_id: resultId,
        is_worth_researching: values.is_worth_researching,
        can_accept_drawdown: values.can_accept_drawdown,
        next_action: values.next_action as ConclusionNextAction,
        market_condition_notes: values.market_condition_notes || undefined,
        notes: values.notes || undefined,
      },
      {
        onSuccess: (data) => {
          setSavedConclusion(data);
        },
      },
    );
  }

  const disabled = isSubmitting || mutation.isPending;

  return (
    <form
      className={styles.conclusionForm}
      onSubmit={handleSubmit(onSubmit)}
      data-testid="conclusion-form"
    >
      <h2 className={styles.sectionTitle}>写下你的结论</h2>

      {/* is_worth_researching */}
      <div className={styles.cfField}>
        <label className={styles.cfCheckboxLabel}>
          <input
            type="checkbox"
            className={styles.cfCheckbox}
            data-testid="conclusion-is-worth-researching"
            disabled={disabled}
            {...register("is_worth_researching")}
          />
          <span>这个策略值得继续研究</span>
        </label>
      </div>

      {/* can_accept_drawdown */}
      <div className={styles.cfField}>
        <label className={styles.cfCheckboxLabel}>
          <input
            type="checkbox"
            className={styles.cfCheckbox}
            data-testid="conclusion-can-accept-drawdown"
            disabled={disabled}
            {...register("can_accept_drawdown")}
          />
          <span>我可以接受当前回撤水平</span>
        </label>
      </div>

      {/* next_action */}
      <div className={styles.cfField}>
        <label className={styles.cfLabel} htmlFor="conclusion-next-action">
          下一步行动 <span className={styles.cfRequired}>*</span>
        </label>
        <select
          id="conclusion-next-action"
          className={styles.cfSelect}
          data-testid="conclusion-next-action"
          disabled={disabled}
          {...register("next_action")}
        >
          {NEXT_ACTION_VALUES.map((v) => (
            <option key={v} value={v}>
              {CONCLUSION_NEXT_ACTION_LABELS[v]}
            </option>
          ))}
        </select>
        {errors.next_action && (
          <p className={styles.cfError}>{errors.next_action.message}</p>
        )}
      </div>

      {/* market_condition_notes */}
      <div className={styles.cfField}>
        <label className={styles.cfLabel} htmlFor="conclusion-market-notes">
          适用行情说明
          <span className={styles.cfHint}>（选填，最多 2000 字）</span>
        </label>
        <textarea
          id="conclusion-market-notes"
          className={styles.cfTextarea}
          rows={3}
          placeholder="例如：仅适用于趋势行情，震荡市表现较差。"
          data-testid="conclusion-market-condition-notes"
          disabled={disabled}
          {...register("market_condition_notes")}
        />
        {errors.market_condition_notes && (
          <p className={styles.cfError}>{errors.market_condition_notes.message}</p>
        )}
      </div>

      {/* notes */}
      <div className={styles.cfField}>
        <label className={styles.cfLabel} htmlFor="conclusion-notes">
          备注
          <span className={styles.cfHint}>（选填，最多 4000 字）</span>
        </label>
        <textarea
          id="conclusion-notes"
          className={styles.cfTextarea}
          rows={4}
          placeholder="其他想法、后续优化方向、注意事项等。"
          data-testid="conclusion-notes"
          disabled={disabled}
          {...register("notes")}
        />
        {errors.notes && (
          <p className={styles.cfError}>{errors.notes.message}</p>
        )}
      </div>

      {/* server error */}
      {serverErrorMessage && (
        <div
          className={`${styles.message} ${styles.messageError}`}
          role="alert"
          data-testid="conclusion-save-error"
        >
          <p>{serverErrorMessage}</p>
        </div>
      )}

      {/* submit */}
      <div className={styles.cfActions}>
        <button
          type="submit"
          className={styles.cfSubmitButton}
          disabled={disabled}
          data-testid="conclusion-submit-button"
        >
          {mutation.isPending ? "保存中…" : "保存结论"}
        </button>
      </div>
    </form>
  );
}
