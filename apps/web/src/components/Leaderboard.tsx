import { useEffect, useState } from 'react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Trophy, Mail, Phone, Flame } from 'lucide-react';
import { getLeaderboard, getUserStats } from '@/integrations/api';
import { useAuth } from '@/hooks/useAuth';

interface LeaderboardEntry {
  rank: number;
  user_id: string;
  display_name: string;
  photo_url?: string;
  score: number;
  tasks_completed: number;
  level: number;
  streak: number;
  is_current_user: boolean;
  email?: string;
  phone_number?: string;
}

interface UserStats {
  profile: {
    display_name: string;
    email: string;
    photo_url?: string;
    level: number;
    total_score: number;
    streak_days: number;
    achievements: any[];
  };
  stats: {
    rank: number;
    completed_tasks: number;
    completion_rate: number;
  };
}

const PODIUM_STYLE: Record<number, { ring: string; badge: string }> = {
  1: { ring: 'ring-amber-300', badge: 'bg-amber-500' },
  2: { ring: 'ring-slate-300', badge: 'bg-slate-400' },
  3: { ring: 'ring-orange-300', badge: 'bg-orange-500' },
};

export default function Leaderboard() {
  const { user } = useAuth();
  const [period, setPeriod] = useState<'all_time' | 'monthly' | 'weekly'>('all_time');
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard();
    fetchUserStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [period]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const data = await getLeaderboard(period, 100);
      const mapped = (data.leaderboard || []).map((entry: any) => ({
        rank: entry.rank || 0,
        user_id: entry.id,
        display_name: entry.display_name || 'Unknown',
        photo_url: entry.photo_url,
        score: entry.total_score || 0,
        tasks_completed: entry.tasks_completed || 0,
        level: entry.level || 1,
        streak: entry.streak_days || 0,
        is_current_user: entry.id === user?.uid,
        email: entry.email,
        phone_number: entry.phone_number,
      }));
      setLeaderboard(mapped);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserStats = async () => {
    try {
      const stats = await getUserStats();
      setUserStats({
        profile: {
          display_name: user?.displayName || '',
          email: user?.email || '',
          photo_url: user?.photoURL,
          level: stats.level || 1,
          total_score: stats.total_score || 0,
          streak_days: stats.streak_days || 0,
          achievements: stats.achievements || [],
        },
        stats: {
          rank: stats.rank || 0,
          completed_tasks: stats.tasks_completed || 0,
          completion_rate: stats.completion_rate || 0,
        },
      });
    } catch (error) {
      console.error('Failed to fetch user stats:', error);
    }
  };

  const podium = leaderboard.slice(0, 3);
  const rest = leaderboard.slice(3);
  const levelProgress = userStats ? userStats.profile.total_score % 1000 / 10 : 0;

  return (
    <div className="container mx-auto px-4 py-8 space-y-10">
      <div>
        <p className="text-xs font-semibold tracking-widest text-muted-foreground uppercase mb-2">
          Community Rankings
        </p>
        <h1 className="font-serif text-4xl md:text-5xl font-semibold text-foreground">
          Top Plant Parents
        </h1>
        <p className="text-muted-foreground mt-3 max-w-2xl">
          Celebrate the dedication of our top cultivators — a deep well of botanical
          wisdom and exceptional care routines.
        </p>
      </div>

      {/* Podium */}
      {!loading && podium.length >= 3 && (
        <div className="grid grid-cols-3 gap-4 md:gap-6 items-end max-w-3xl mx-auto">
          {[podium[1], podium[0], podium[2]].map((entry, idx) => {
            const isFirst = entry.rank === 1;
            const style = PODIUM_STYLE[entry.rank] || PODIUM_STYLE[3];
            return (
              <div
                key={entry.user_id}
                className={`glass-card p-5 flex flex-col items-center text-center gap-2 ${isFirst ? 'py-8 order-2' : `pt-8 ${idx === 0 ? 'order-1' : 'order-3'}`}`}
              >
                <Badge className={`${style.badge} text-white border-none mb-1`}>
                  Rank {entry.rank}
                </Badge>
                <Avatar className={`ring-4 ${style.ring} ${isFirst ? 'w-20 h-20' : 'w-14 h-14'}`}>
                  <AvatarImage src={entry.photo_url} alt={entry.display_name} />
                  <AvatarFallback>{entry.display_name.charAt(0).toUpperCase()}</AvatarFallback>
                </Avatar>
                <p className={`font-serif font-semibold ${isFirst ? 'text-lg' : 'text-sm'}`}>{entry.display_name}</p>
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                  <Flame size={12} className="text-orange-500" /> {entry.streak} day streak
                </div>
                <p className="font-bold text-primary">{entry.score.toLocaleString()} XP</p>
              </div>
            );
          })}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Global Rankings */}
        <div className="lg:col-span-8 glass-card p-6 space-y-5">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <h2 className="font-serif text-xl font-semibold flex items-center gap-2">
              <Trophy className="h-5 w-5 text-primary" /> Global Rankings
            </h2>
            <Tabs value={period} onValueChange={(v) => setPeriod(v as any)}>
              <TabsList>
                <TabsTrigger value="weekly">This Week</TabsTrigger>
                <TabsTrigger value="monthly">This Month</TabsTrigger>
                <TabsTrigger value="all_time">All Time</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>

          <div className="space-y-2">
            {loading ? (
              <p className="text-center text-muted-foreground py-8">Loading leaderboard...</p>
            ) : leaderboard.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">Be the first to bloom!</p>
            ) : (
              (rest.length > 0 ? rest : leaderboard).map((entry) => (
                <div
                  key={entry.user_id}
                  className={`flex items-center justify-between p-3 rounded-xl transition-colors ${
                    entry.is_current_user ? 'bg-accent' : 'hover:bg-secondary/50'
                  }`}
                >
                  <div className="flex items-center gap-4">
                    <span className="w-6 text-center text-sm font-semibold text-muted-foreground">
                      {entry.rank}
                    </span>
                    <Avatar className="w-9 h-9">
                      <AvatarImage src={entry.photo_url} alt={entry.display_name} />
                      <AvatarFallback>{entry.display_name.charAt(0).toUpperCase()}</AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-medium text-sm">
                        {entry.display_name}
                        {entry.is_current_user && (
                          <Badge variant="secondary" className="ml-2">You</Badge>
                        )}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Level {entry.level} · {entry.streak} day streak
                      </p>
                      {(entry.email || entry.phone_number) && (
                        <div className="flex items-center gap-3 text-xs text-muted-foreground mt-0.5">
                          {entry.email && (
                            <span className="flex items-center gap-1">
                              <Mail className="h-3 w-3" /> {entry.email}
                            </span>
                          )}
                          {entry.phone_number && (
                            <span className="flex items-center gap-1">
                              <Phone className="h-3 w-3" /> {entry.phone_number}
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  <span className="font-semibold text-sm text-primary">{entry.score.toLocaleString()}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Your Ranking */}
        <div className="lg:col-span-4">
          <div className="glass-card p-6 space-y-5 sticky top-24">
            <h2 className="font-serif text-lg font-semibold">Your Ranking</h2>

            {userStats && (
              <>
                <div className="flex items-center gap-3">
                  <Avatar className="w-12 h-12">
                    <AvatarImage src={userStats.profile.photo_url} alt={userStats.profile.display_name} />
                    <AvatarFallback>{userStats.profile.display_name.charAt(0).toUpperCase() || 'B'}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium text-sm">{userStats.profile.display_name || 'You'}</p>
                    <Badge className="bg-primary text-primary-foreground border-none">
                      Rank #{userStats.stats.rank || '—'}
                    </Badge>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Level {userStats.profile.level}</span>
                    <span>{userStats.profile.total_score.toLocaleString()} XP</span>
                  </div>
                  <Progress value={levelProgress} className="h-2" />
                </div>

                <div className="flex items-center gap-2 text-sm text-muted-foreground bg-secondary/60 rounded-xl px-3 py-2">
                  <Flame size={16} className="text-orange-500" />
                  {userStats.profile.streak_days} day streak
                </div>

                <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl">
                  Log Care Activity
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
