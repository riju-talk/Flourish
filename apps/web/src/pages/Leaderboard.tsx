import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Seo } from "@/components/Seo";
import Leaderboard from "@/components/Leaderboard";

export default function LeaderboardPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Seo title="Leaderboard" description="See how your gardening streak and score stack up against other Flourish growers." />
      <Navbar />
      <main className="flex-1">
        <Leaderboard />
      </main>
      <Footer />
    </div>
  );
}
