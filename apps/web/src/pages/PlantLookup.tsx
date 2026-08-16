import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Seo } from "@/components/Seo";
import PlantLookup from "@/components/PlantLookup";

export default function PlantLookupPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Seo title="Explore" description="Look up any plant's care needs, native habitat, and common issues." />
      <Navbar />
      <main className="flex-1">
        <PlantLookup />
      </main>
      <Footer />
    </div>
  );
}
