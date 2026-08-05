import { useState, useEffect } from "react";
import { Trophy, Medal, Crown } from "lucide-react";
import { getLeaderboard } from "@/integrations/api";

const FALLBACK_LEADERS = [
    { name: "Sunny Leaf", score: 1250, rank: 1 },
    { name: "Cactus Jack", score: 1100, rank: 2 },
    { name: "Aloe Vera", score: 950, rank: 3 },
];

export const LeaderboardPreview = () => {
    const [leaders, setLeaders] = useState(FALLBACK_LEADERS);

    useEffect(() => {
        getLeaderboard("all_time", 3).then((data) => {
            if (data?.leaderboard?.length >= 3) {
                setLeaders(data.leaderboard.slice(0, 3).map((e: any, i: number) => ({
                    name: e.display_name || "Unknown",
                    score: e.total_score || 0,
                    rank: i + 1,
                })));
            }
        }).catch(() => {});
    }, []);

    const getRankIcon = (rank: number) => {
        switch (rank) {
            case 1: return <Crown size={16} className="text-yellow-500 fill-yellow-500" />;
            case 2: return <Medal size={16} className="text-gray-400 fill-gray-400" />;
            case 3: return <Medal size={16} className="text-amber-700 fill-amber-700" />;
            default: return <span className="text-sm font-bold text-muted-foreground">#{rank}</span>;
        }
    };

    return (
        <section className="glass-card p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h3 className="font-serif text-lg font-semibold flex items-center gap-2">
                    <div className="bg-amber-100 p-1.5 rounded-lg">
                        <Trophy className="h-5 w-5 text-amber-600" />
                    </div>
                    Global Leaders
                </h3>
                <span className="text-xs font-medium text-muted-foreground bg-secondary px-2 py-1 rounded-full">All time</span>
            </div>

            <div className="space-y-4 relative z-10">
                {leaders.map((leader, index) => (
                    <div
                        key={leader.name}
                        className="flex items-center justify-between p-3 rounded-2xl bg-secondary/40 border border-border transition-all duration-500 ease-out hover:scale-[1.01] hover:bg-secondary/70"
                        style={{
                            animationDelay: `${index * 100}ms`
                        }}
                    >
                        <div className="flex items-center gap-4">
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold shadow-sm ${leader.rank === 1 ? 'bg-yellow-100 ring-2 ring-yellow-200' :
                                    leader.rank === 2 ? 'bg-gray-100 ring-2 ring-gray-200' :
                                        'bg-amber-100 ring-2 ring-amber-200'
                                }`}>
                                {getRankIcon(leader.rank)}
                            </div>

                            <div className="flex flex-col">
                                <span className="font-bold text-sm text-foreground">{leader.name}</span>
                                <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-wider">Rank {leader.rank}</span>
                            </div>
                        </div>
                        <span className="text-primary font-black text-sm bg-primary/5 px-2 py-1 rounded-md">{leader.score} XP</span>
                    </div>
                ))}
            </div>

            <button className="w-full py-3 mt-2 text-center text-sm font-bold text-primary hover:bg-primary/5 rounded-xl transition-colors relative z-10">
                View Full Standings
            </button>
        </section>
    );
};
