import TenderDashboard from "@/components/TenderDashboard";
import { getTenders } from "@/lib/tenders";

export default function Home() {
  return <TenderDashboard notices={getTenders()} />;
}
