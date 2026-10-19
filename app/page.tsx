import TenderDashboard from "@/components/TenderDashboard";
import { getTenders } from "@/lib/tenders";

export const dynamic = "force-dynamic";

export default function Home() {
  return <TenderDashboard notices={getTenders()} />;
}
