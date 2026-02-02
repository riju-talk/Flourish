import { Navbar } from "@/components/Navbar";
import Leaderboard from "@/components/Leaderboard";

export default function LeaderboardPage() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <Leaderboard />
    </div>
  );
}
