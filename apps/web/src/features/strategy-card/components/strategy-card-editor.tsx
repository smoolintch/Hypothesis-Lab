"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import {
  FormProvider,
  type Path,
  type UseFormSetError,
  useForm,
} from "react-hook-form";

import { useStartBacktestMutation } from "@/features/backtest/api";

import {
  ApiClientError,
  useCreateStrategyCardMutation,
  useStrategyCardQuery,
  useUpdateStrategyCardMutation,
} from "../api";
import {
  createDefaultStrategyCardFormValues,
  toStrategyCardFormValues,
  toStrategyCardPayload,
} from "../mappers";
import {
  strategyCardFormSchema,
  type StrategyCardFormInput,
  type StrategyCardFormValues,
} from "../schema";
import type {
  RulePosition,
  StrategyCardDetail,
  StrategyCardEditorMode,
} from "../types";
import { StrategyBacktestHistoryList } from "./strategy-backtest-history-list";
import { StrategyCardFormFields } from "./strategy-card-form-fields";
import styles from "./strategy-card-editor.module.css";

type StrategyCardEditorProps = {
  mode: StrategyCardEditorMode;
  strategyCardId?: string;
};

type ServerValidationError = {
  loc?: unknown;
  msg?: string;
};

function normalizeLocSegments(loc: unknown): string[] {
  if (!Array.isArray(loc)) {
    return [];
  }

  return loc
    .filter(
      (segment): segment is string | number =>
        typeof segment === "string" || typeof segment === "number",
    )
    .map((segment) => String(segment));
}

function getServerValidationErrors(
  details: Record<string, unknown>,
): ServerValidationError[] {
  const errors = details.validation_errors;
  return Array.isArray(errors) ? (errors as ServerValidationError[]) : [];
}

function mapRequestValidationPath(
  loc: unknown,
): Path<StrategyCardFormInput> | null {
  const segments = normalizeLocSegments(loc).filter((segment) => segment !== "body");

  if (!segments.length) {
    return null;
  }

  return segments.join(".") as Path<StrategyCardFormInput>;
}

function mapRuleValidationPath(
  position: RulePosition,
  loc: unknown,
): Path<StrategyCardFormInput> {
  const segments = normalizeLocSegments(loc).filter((segment) => segment !== "params");

  if (!segments.length) {
    return `rule_set.${position}.template_key` as Path<StrategyCardFormInput>;
  }

  return `rule_set.${position}.params.${segments.join(".")}` as Path<StrategyCardFormInput>;
}

function applyApiErrorToForm(
  error: ApiClientError,
  setError: UseFormSetError<StrategyCardFormInput>,
) {
  if (error.code === "STRATEGY_CARD_VALIDATION_FAILED") {
    for (const validationError of getServerValidationErrors(error.details)) {
      if (!validationError.msg) {
        continue;
      }

      const fieldPath = mapRequestValidationPath(validationError.loc);

      if (fieldPath) {
        setError(fieldPath, {
          type: "server",
          message: validationError.msg,
        });
      }
    }

    return;
  }

  if (error.code === "UNSUPPORTED_SYMBOL") {
    setError("symbol", {
      type: "server",
      message: error.message,
    });
    return;
  }

  if (error.code === "UNSUPPORTED_TIMEFRAME") {
    setError("timeframe", {
      type: "server",
      message: error.message,
    });
    return;
  }

  if (error.code === "RULE_TEMPLATE_INVALID") {
    const position = error.details.position;

    if (
      position === "entry" ||
      position === "exit" ||
      position === "stop_loss" ||
      position === "take_profit"
    ) {
      const validationErrors = getServerValidationErrors(error.details);

      if (validationErrors.length === 0) {
        setError(`rule_set.${position}.template_key`, {
          type: "server",
          message: error.message,
        });
        return;
      }

      for (const validationError of validationErrors) {
        if (!validationError.msg) {
          continue;
        }

        setError(mapRuleValidationPath(position, validationError.loc), {
          type: "server",
          message: validationError.msg,
        });
      }
    }
  }
}

function formatDateTime(value: string) {
  const date = new Date(value);

  if (Number.isNaN(date.valueOf())) {
    return "-";
  }

  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function buildApiErrorDetails(error: ApiClientError): string[] {
  if (error.code === "RULE_TEMPLATE_INVALID") {
    const messages = getServerValidationErrors(error.details)
      .map((item) => item.msg)
      .filter((item): item is string => typeof item === "string");

    if (messages.length > 0) {
      return messages;
    }
  }

  if (error.code === "STRATEGY_CARD_VALIDATION_FAILED") {
    const messages = getServerValidationErrors(error.details)
      .map((item) => item.msg)
      .filter((item): item is string => typeof item === "string");

    if (messages.length > 0) {
      return messages.slice(0, 4);
    }
  }

  const allowedValues = error.details.allowed_values;
  if (Array.isArray(allowedValues) && allowedValues.length > 0) {
    return [`允许值：${allowedValues.join(" / ")}`];
  }

  return [];
}

function getPageCopy(mode: StrategyCardEditorMode) {
  if (mode === "create") {
    return {
      eyebrow: "Strategy Card",
      title: "新建策略假设卡",
      subtitle:
        "完成本轮阶段 1 所需的最小输入链路。首次保存成功后会自动跳转到编辑页，并继续基于真实 API 回填编辑。",
      submitLabel: "保存并进入编辑页",
    };
  }

  return {
    eyebrow: "Strategy Card",
    title: "编辑策略假设卡",
    subtitle:
      "编辑页会从真实 API 加载当前策略卡，完成回填后支持继续更新保存，不依赖列表接口。",
    submitLabel: "保存变更",
  };
}

export function StrategyCardEditor({
  mode,
  strategyCardId,
}: StrategyCardEditorProps) {
  const router = useRouter();
  const copy = getPageCopy(mode);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<ApiClientError | null>(null);
  const [backtestError, setBacktestError] = useState<ApiClientError | null>(null);

  const defaultValues = useMemo(() => createDefaultStrategyCardFormValues(), []);
  const form = useForm<StrategyCardFormInput, unknown, StrategyCardFormValues>({
    resolver: zodResolver(strategyCardFormSchema),
    defaultValues,
    mode: "onBlur",
    shouldUnregister: true,
  });

  const strategyCardQuery = useStrategyCardQuery(
    mode === "edit" ? strategyCardId : undefined,
  );
  const createMutation = useCreateStrategyCardMutation();
  const updateMutation = useUpdateStrategyCardMutation(strategyCardId);
  const startBacktestMutation = useStartBacktestMutation(
    mode === "edit" ? strategyCardId : undefined,
  );
  const activeMutation = mode === "edit" ? updateMutation : createMutation;
  const detail = strategyCardQuery.data as StrategyCardDetail | undefined;

  useEffect(() => {
    if (mode === "edit" && detail) {
      form.reset(toStrategyCardFormValues(detail));
    }
  }, [detail, form, mode]);

  const hasClientValidationErrors =
    form.formState.submitCount > 0 && Object.keys(form.formState.errors).length > 0;

  async function handleSubmit(values: StrategyCardFormValues) {
    form.clearErrors();
    setSaveMessage(null);
    setSubmitError(null);
    setBacktestError(null);

    try {
      const payload = toStrategyCardPayload(values);
      const savedDetail =
        mode === "edit"
          ? await updateMutation.mutateAsync(payload)
          : await createMutation.mutateAsync(payload);

      if (mode === "create") {
        router.replace(`/strategy-cards/${savedDetail.id}/edit`);
        return;
      }

      form.reset(toStrategyCardFormValues(savedDetail));
      setSaveMessage("策略已保存");
    } catch (error) {
      const apiError =
        error instanceof ApiClientError
          ? error
          : new ApiClientError({
              status: 500,
              fallbackMessage: "保存失败，请稍后重试。",
            });

      applyApiErrorToForm(apiError, form.setError);
      setSubmitError(apiError);
    }
  }

  async function handleStartBacktest() {
    if (mode !== "edit" || !strategyCardId) {
      return;
    }

    setBacktestError(null);
    setSaveMessage(null);

    const valid = await form.trigger();
    if (!valid) {
      return;
    }

    if (form.formState.isDirty) {
      try {
        setSubmitError(null);
        const values = strategyCardFormSchema.parse(form.getValues());
        const saved = await updateMutation.mutateAsync(
          toStrategyCardPayload(values),
        );
        form.reset(toStrategyCardFormValues(saved));
        setSaveMessage("策略已保存");
      } catch (error) {
        const apiError =
          error instanceof ApiClientError
            ? error
            : new ApiClientError({
                status: 500,
                fallbackMessage: "保存失败，请稍后重试。",
              });

        applyApiErrorToForm(apiError, form.setError);
        setSubmitError(apiError);
        return;
      }
    }

    try {
      const run = await startBacktestMutation.mutateAsync();
      router.push(`/backtests/${run.run_id}`);
    } catch (error) {
      const apiError =
        error instanceof ApiClientError
          ? error
          : new ApiClientError({
              status: 500,
              fallbackMessage: "发起回测失败，请稍后重试。",
            });

      setBacktestError(apiError);
    }
  }

  if (mode === "edit" && strategyCardQuery.isPending) {
    return (
      <main className={styles.page} data-testid="strategy-card-editor-page">
        <div className={styles.container}>
          <header className={styles.header}>
            <p className={styles.eyebrow}>{copy.eyebrow}</p>
            <h1 className={styles.title}>{copy.title}</h1>
            <p className={styles.subtitle}>{copy.subtitle}</p>
          </header>
          <section
            className={`${styles.panel} ${styles.statePanel}`}
            data-testid="strategy-card-loading-state"
          >
            <h2 className={styles.sectionTitle}>编辑加载中</h2>
            <p className={styles.sectionDescription}>
              正在调用 `GET /api/strategy-cards/:id` 加载真实数据并准备回填表单。
            </p>
          </section>
        </div>
      </main>
    );
  }

  if (mode === "edit" && strategyCardQuery.error) {
    const queryError =
      strategyCardQuery.error instanceof ApiClientError
        ? strategyCardQuery.error
        : new ApiClientError({
            status: 500,
            fallbackMessage: "加载策略卡失败。",
          });

    const isNotFound =
      queryError.status === 404 || queryError.code === "STRATEGY_CARD_NOT_FOUND";

    return (
      <main className={styles.page} data-testid="strategy-card-editor-page">
        <div className={styles.container}>
          <header className={styles.header}>
            <p className={styles.eyebrow}>{copy.eyebrow}</p>
            <h1 className={styles.title}>{copy.title}</h1>
            <p className={styles.subtitle}>{copy.subtitle}</p>
          </header>
          <section
            className={`${styles.panel} ${styles.statePanel}`}
            data-testid={isNotFound ? "strategy-card-not-found-state" : "strategy-card-load-error-state"}
          >
            <h2 className={styles.sectionTitle}>
              {isNotFound ? "策略卡不存在" : "加载失败"}
            </h2>
            <p className={styles.sectionDescription}>{queryError.message}</p>
            <div className={styles.inlineActions}>
              {!isNotFound ? (
                <button
                  className={styles.buttonPrimary}
                  type="button"
                  onClick={() => strategyCardQuery.refetch()}
                >
                  重新加载
                </button>
              ) : null}
              <Link className={styles.buttonSecondary} href="/strategy-cards/new">
                新建策略卡
              </Link>
            </div>
          </section>
        </div>
      </main>
    );
  }

  return (
    <main className={styles.page} data-testid="strategy-card-editor-page">
      <div className={styles.container}>
        <header className={styles.header}>
          <p className={styles.eyebrow}>{copy.eyebrow}</p>
          <h1 className={styles.title}>{copy.title}</h1>
          <p className={styles.subtitle}>{copy.subtitle}</p>
        </header>

        <section className={styles.panel} data-testid="strategy-card-editor-panel">
          {detail ? (
            <>
              <div className={styles.metaGrid} data-testid="strategy-card-meta">
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>策略卡 ID</span>
                  <span className={styles.metaValue}>{detail.id}</span>
                </div>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>当前状态</span>
                  <span className={styles.metaValue}>{detail.status}</span>
                </div>
                <div className={styles.metaItem}>
                  <span className={styles.metaLabel}>最近更新时间</span>
                  <span className={styles.metaValue}>
                    {formatDateTime(detail.updated_at)}
                  </span>
                </div>
              </div>
              <StrategyBacktestHistoryList strategyCardId={detail.id} />
            </>
          ) : null}

          {hasClientValidationErrors ? (
            <div
              className={`${styles.message} ${styles.messageError}`}
              data-testid="strategy-card-client-validation-message"
            >
              <p className={styles.messageTitle}>字段校验失败</p>
              <p>请先修正表单中的错误，再重新保存。</p>
            </div>
          ) : null}

          {submitError ? (
            <div
              className={`${styles.message} ${styles.messageError}`}
              data-testid="strategy-card-submit-error"
            >
              <p className={styles.messageTitle}>保存失败</p>
              <p>{submitError.message}</p>
              {buildApiErrorDetails(submitError).length > 0 ? (
                <ul className={styles.messageList}>
                  {buildApiErrorDetails(submitError).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              ) : null}
            </div>
          ) : null}

          {backtestError ? (
            <div
              className={`${styles.message} ${styles.messageError}`}
              data-testid="strategy-card-backtest-error"
            >
              <p className={styles.messageTitle}>发起回测失败</p>
              <p>{backtestError.message}</p>
            </div>
          ) : null}

          {saveMessage ? (
            <div
              className={`${styles.message} ${styles.messageSuccess}`}
              data-testid="strategy-card-save-success"
            >
              <p className={styles.messageTitle}>保存成功</p>
              <p>{saveMessage}</p>
            </div>
          ) : null}

          <FormProvider {...form}>
            <form
              className={styles.form}
              data-testid="strategy-card-form"
              onSubmit={form.handleSubmit(handleSubmit)}
            >
              <StrategyCardFormFields mode={mode} />

              <div className={styles.actions}>
                {mode === "edit" && strategyCardId ? (
                  <Link
                    className={styles.buttonSecondary}
                    href={`/strategy-cards/${strategyCardId}/edit`}
                  >
                    刷新当前页
                  </Link>
                ) : (
                  <Link className={styles.buttonSecondary} href="/">
                    返回首页
                  </Link>
                )}
                {mode === "edit" && strategyCardId ? (
                  <button
                    className={styles.buttonSecondary}
                    data-testid="strategy-card-start-backtest-button"
                    disabled={
                      activeMutation.isPending ||
                      form.formState.isSubmitting ||
                      startBacktestMutation.isPending
                    }
                    type="button"
                    onClick={() => void handleStartBacktest()}
                  >
                    {startBacktestMutation.isPending ? "发起中..." : "发起回测"}
                  </button>
                ) : null}
                <button
                  className={styles.buttonPrimary}
                  data-testid="strategy-card-submit-button"
                  disabled={
                    activeMutation.isPending ||
                    form.formState.isSubmitting ||
                    startBacktestMutation.isPending
                  }
                  type="submit"
                >
                  {activeMutation.isPending || form.formState.isSubmitting
                    ? "保存中..."
                    : copy.submitLabel}
                </button>
              </div>
            </form>
          </FormProvider>
        </section>
      </div>
    </main>
  );
}
