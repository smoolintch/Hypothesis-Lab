import { StrategyCardEditor } from "@/features/strategy-card/components/strategy-card-editor";

type EditStrategyCardPageProps = {
  params: Promise<{
    id: string;
  }>;
  searchParams: Promise<{
    duplicatedFrom?: string;
    sourceId?: string;
    sourceName?: string;
  }>;
};

export default async function EditStrategyCardPage({
  params,
  searchParams,
}: EditStrategyCardPageProps) {
  const { id } = await params;
  const resolvedSearchParams = await searchParams;

  return (
    <StrategyCardEditor
      mode="edit"
      strategyCardId={id}
      duplicatedFromSourceId={
        resolvedSearchParams.duplicatedFrom === "true"
          ? resolvedSearchParams.sourceId
          : undefined
      }
      duplicatedFromSourceName={
        resolvedSearchParams.duplicatedFrom === "true"
          ? resolvedSearchParams.sourceName
          : undefined
      }
    />
  );
}
