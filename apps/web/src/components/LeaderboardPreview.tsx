import { Trophy, Medal, Crown } from "lucide-react";

export const LeaderboardPreview = () => {
    const leaders = [
        { name: "Sunny Leaf", score: 1250, rank: 1 },
        { name: "Cactus Jack", score: 1100, rank: 2 },
        { name: "Aloe Vera", score: 950, rank: 3 },
    ];

    const getRankIcon = (rank: number) => {
        switch (rank) {
            case 1: return <Crown size={16} className="text-yellow-500 fill-yellow-500" />;
            case 2: return <Medal size={16} className="text-gray-400 fill-gray-400" />;
            case 3: return <Medal size={16} className="text-amber-700 fill-amber-700" />;
            default: return <span className="text-sm font-bold text-muted-foreground">#{rank}</span>;
        }
    };

    return (
        <section className="glass-card p-6 rounded-[2rem] space-y-6 relative overflow-hidden group hover:shadow-2xl transition-all duration-500">
            <div className="absolute top-0 right-0 p-16 bg-yellow-500/10 rounded-full blur-3xl -mr-8 -mt-8 pointer-events-none"></div>

            <div className="flex items-center justify-between relative z-10">
                <h3 className="text-lg font-bold flex items-center gap-2">
                    <div className="bg-yellow-100 p-1.5 rounded-lg">
                        <Trophy className="h-5 w-5 text-yellow-600" />
                    </div>
                    Global Leaders
                </h3>
                <span className="text-xs font-medium text-muted-foreground bg-white/50 px-2 py-1 rounded-full">Weekly</span>
            </div>

            <div className="space-y-4 relative z-10">
                {leaders.map((leader, index) => (
                    <div
                        key={leader.name}
                        className="flex items-center justify-between p-3 rounded-2xl bg-white/40 border border-white/30 transition-all duration-300 hover:scale-[1.02] hover:bg-white/60"
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
