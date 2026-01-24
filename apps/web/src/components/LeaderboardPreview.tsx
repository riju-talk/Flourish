import { Trophy } from "lucide-react";
import { glass-card } from "@/index.css"; // Note: This is an illustrative import, classes are global

export const LeaderboardPreview = () => {
    const leaders = [
        { name: "Sunny Leaf", score: 1250, rank: 1 },
        { name: "Cactus Jack", score: 1100, rank: 2 },
        { name: "Aloe Vera", score: 950, rank: 3 },
    ];

    return (
        <section className="glass-card p-6 rounded-3xl space-y-4">
            <h3 className="text-xl font-bold flex items-center gap-2">
                <Trophy className="h-5 w-5 text-yellow-500" /> Global Leaderboard
            </h3>
            <div className="space-y-3">
                {leaders.map((leader) => (
                    <div key={leader.name} className="flex items-center justify-between p-3 rounded-2xl bg-white/40 border border-white/20">
                        <div className="flex items-center gap-3">
                            <span className="font-bold text-lg text-primary w-6">#{leader.rank}</span>
                            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center font-bold">
                                {leader.name[0]}
                            </div>
                            <span className="font-medium">{leader.name}</span>
                        </div>
                        <span className="text-primary font-bold">{leader.score}</span>
                    </div>
                ))}
            </div>
            <button className="w-full text-center text-sm font-medium text-primary hover:underline">
                View Full Standings
            </button>
        </section>
    );
};
