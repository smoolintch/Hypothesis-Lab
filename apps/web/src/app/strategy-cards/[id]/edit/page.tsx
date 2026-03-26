import { StrategyCardEditor } from "@/features/strategy-card/components/strategy-card-editor";

type EditStrategyCardPageProps = {
  params: Promise<{
    id: string;
  }>;
};

export default async function EditStrategyCardPage({
  params,
}: EditStrategyCardPageProps) {
  const { id } = await params;

  return <StrategyCardEditor mode="edit" strategyCardId={id} />;
}
