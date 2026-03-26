"use client";

import { useFormContext, useWatch } from "react-hook-form";

import {
  RULE_TEMPLATES_BY_POSITION,
  createDefaultRuleInstance,
  getRuleTemplateDefinition,
} from "../rule-templates";
import type { StrategyCardFormInput } from "../schema";
import type { RulePosition, RuleTemplateKey } from "../types";
import styles from "./strategy-card-editor.module.css";

type RuleSectionProps = {
  position: RulePosition;
  title: string;
  description: string;
  required?: boolean;
};

function getErrorMessage(error: unknown): string | undefined {
  if (
    error &&
    typeof error === "object" &&
    "message" in error &&
    typeof error.message === "string"
  ) {
    return error.message;
  }

  return undefined;
}

export function RuleSection({
  position,
  title,
  description,
  required = false,
}: RuleSectionProps) {
  const {
    control,
    register,
    setValue,
    formState: { errors },
  } = useFormContext<StrategyCardFormInput>();

  const ruleName = `rule_set.${position}` as const;
  const selectedRule = useWatch({
    control,
    name: ruleName,
  });
  const ruleError = errors.rule_set?.[position] as
    | {
        template_key?: unknown;
        params?: Record<string, unknown>;
      }
    | undefined;

  const options = RULE_TEMPLATES_BY_POSITION[position].map((templateKey) => ({
    value: templateKey,
    label: getRuleTemplateDefinition(templateKey).label,
  }));

  function handleTemplateChange(nextTemplateKey: string) {
    if (!nextTemplateKey) {
      setValue(ruleName, null as never, {
        shouldDirty: true,
        shouldTouch: true,
        shouldValidate: true,
      });
      return;
    }

    setValue(
      ruleName,
      createDefaultRuleInstance(nextTemplateKey as RuleTemplateKey) as never,
      {
        shouldDirty: true,
        shouldTouch: true,
        shouldValidate: true,
      },
    );
  }

  const definition = selectedRule
    ? getRuleTemplateDefinition(selectedRule.template_key)
    : null;

  return (
    <section className={styles.section} data-testid={`rule-section-${position}`}>
      <div className={styles.sectionHeader}>
        <div className={styles.sectionTitleRow}>
          <h2 className={styles.sectionTitle}>{title}</h2>
          {!required ? <span className={styles.optionalBadge}>可选</span> : null}
        </div>
        <p className={styles.sectionDescription}>{description}</p>
      </div>

      <div className={styles.grid}>
        <div className={styles.field}>
          <label className={styles.label} htmlFor={`${position}-template`}>
            规则模板
          </label>
          <select
            id={`${position}-template`}
            data-testid={`${position}-template-select`}
            className={styles.control}
            value={selectedRule?.template_key ?? ""}
            onChange={(event) => handleTemplateChange(event.target.value)}
          >
            {!required ? <option value="">不启用</option> : null}
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {selectedRule ? (
            <input
              type="hidden"
              value={selectedRule.template_key}
              readOnly
              {...register(`rule_set.${position}.template_key` as never)}
            />
          ) : null}
          {getErrorMessage(ruleError?.template_key) ? (
            <p className={styles.errorText}>
              {getErrorMessage(ruleError?.template_key)}
            </p>
          ) : null}
        </div>

        {definition ? (
          <div className={`${styles.field} ${styles.fieldWide}`}>
            <span className={styles.hint}>{definition.description}</span>
          </div>
        ) : (
          <div className={`${styles.field} ${styles.fieldWide}`}>
            <span className={styles.hint}>当前未启用该风险规则。</span>
          </div>
        )}

        {definition
          ? definition.fields.map((field) => {
              const fieldPath = `rule_set.${position}.params.${field.name}`;
              const fieldError = ruleError?.params?.[field.name];

              return (
                <div className={styles.field} key={`${position}-${field.name}`}>
                  <label
                    className={styles.label}
                    htmlFor={`${position}-${field.name}`}
                  >
                    {field.label}
                  </label>
                  {field.input === "select" ? (
                    <select
                      id={`${position}-${field.name}`}
                      data-testid={`${position}-${field.name}-input`}
                      className={styles.control}
                      {...register(fieldPath as never)}
                    >
                      {field.options?.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      id={`${position}-${field.name}`}
                      data-testid={`${position}-${field.name}-input`}
                      className={styles.control}
                      type="number"
                      min={field.min}
                      max={field.max}
                      step={field.step}
                      inputMode={field.integer ? "numeric" : "decimal"}
                      {...register(fieldPath as never, {
                        valueAsNumber: true,
                      })}
                    />
                  )}
                  {field.description ? (
                    <span className={styles.hint}>{field.description}</span>
                  ) : null}
                  {getErrorMessage(fieldError) ? (
                    <p className={styles.errorText}>{getErrorMessage(fieldError)}</p>
                  ) : null}
                </div>
              );
            })
          : null}
      </div>
    </section>
  );
}
