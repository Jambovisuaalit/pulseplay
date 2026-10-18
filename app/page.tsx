import TenderDashboard from "@/components/TenderDashboard";
import { getTenders } from "@/lib/tenders";

export default async function Home() {
  return <TenderDashboard notices={await getTenders()} />;
}
