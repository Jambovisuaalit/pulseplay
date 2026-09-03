import TenderDashboard from "@/components/TenderDashboard";
import rawData from "@/data/hilma_analysoitu.json";
import type { Tender } from "@/types/tender";

export default function Home() {
  const notices = (Array.isArray(rawData)
    ? rawData
    : (rawData as { notices?: Tender[] }).notices ?? []) as Tender[];

  return <TenderDashboard notices={notices} />;
}
