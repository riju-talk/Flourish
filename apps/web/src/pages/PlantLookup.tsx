import { Navbar } from "@/components/Navbar";
import PlantLookup from "@/components/PlantLookup";

export default function PlantLookupPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <PlantLookup />
    </div>
  );
}
