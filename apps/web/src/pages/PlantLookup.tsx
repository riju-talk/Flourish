import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import PlantLookup from "@/components/PlantLookup";

export default function PlantLookupPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <main className="flex-1">
        <PlantLookup />
      </main>
      <Footer />
    </div>
  );
}
