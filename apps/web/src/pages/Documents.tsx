import { Navbar } from "@/components/Navbar";
import DocumentAnalyzer from "@/components/DocumentAnalyzer";

export default function DocumentsPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <DocumentAnalyzer />
    </div>
  );
}
