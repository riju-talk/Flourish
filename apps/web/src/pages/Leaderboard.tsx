import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import Leaderboard from "@/components/Leaderboard";

export default function LeaderboardPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <main className="flex-1">
        <Leaderboard />
      </main>
      <Footer />
    </div>
  );
}
