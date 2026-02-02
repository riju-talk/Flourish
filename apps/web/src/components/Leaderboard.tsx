import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Trophy, Medal, Award, TrendingUp } from 'lucide-react';
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
    total_tasks: number;
    completed_tasks: number;
    pending_tasks: number;
    overdue_tasks: number;
    completion_rate: number;
  };
}

export default function Leaderboard() {
  const { user } = useAuth();
  const [period, setPeriod] = useState<'all_time' | 'monthly' | 'weekly'>('all_time');
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [userStats, setUserStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLeaderboard();
    fetchUserStats();
  }, [period]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const data = await getLeaderboard(period, 100);
      setLeaderboard(data.leaderboard);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserStats = async () => {
    try {
      const stats = await getUserStats();
      setUserStats(stats);
    } catch (error) {
      console.error('Failed to fetch user stats:', error);
    }
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="h-6 w-6 text-yellow-500" />;
    if (rank === 2) return <Medal className="h-6 w-6 text-gray-400" />;
    if (rank === 3) return <Medal className="h-6 w-6 text-amber-600" />;
    return <span className="text-lg font-bold text-muted-foreground">#{rank}</span>;
  };

  return (
    <div className="container mx-auto p-4 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">🏆 Leaderboard</h1>
      </div>

      {/* User Stats Card */}
      {userStats && (
        <Card>
          <CardHeader>
            <CardTitle>Your Stats</CardTitle>
            <CardDescription>Your plant care journey</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-primary">{userStats.stats.rank}</p>
                <p className="text-sm text-muted-foreground">Global Rank</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-primary">{userStats.profile.total_score}</p>
                <p className="text-sm text-muted-foreground">Total Points</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-primary">{userStats.profile.level}</p>
                <p className="text-sm text-muted-foreground">Level</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-primary">{userStats.profile.streak_days} 🔥</p>
                <p className="text-sm text-muted-foreground">Day Streak</p>
              </div>
            </div>
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <p className="text-lg font-semibold">{userStats.stats.completed_tasks}</p>
                <p className="text-xs text-muted-foreground">Completed</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-semibold">{userStats.stats.pending_tasks}</p>
                <p className="text-xs text-muted-foreground">Pending</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-semibold">{userStats.stats.overdue_tasks}</p>
                <p className="text-xs text-muted-foreground">Overdue</p>
              </div>
              <div className="text-center">
                <p className="text-lg font-semibold">{userStats.stats.completion_rate}%</p>
                <p className="text-xs text-muted-foreground">Success Rate</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Leaderboard */}
      <Card>
        <CardHeader>
          <CardTitle>Top Plant Parents</CardTitle>
          <CardDescription>See who's leading the plant care game</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={period} onValueChange={(v) => setPeriod(v as any)}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="all_time">All Time</TabsTrigger>
              <TabsTrigger value="monthly">This Month</TabsTrigger>
              <TabsTrigger value="weekly">This Week</TabsTrigger>
            </TabsList>

            <TabsContent value={period} className="space-y-2 mt-4">
              {loading ? (
                <p className="text-center text-muted-foreground">Loading leaderboard...</p>
              ) : leaderboard.length === 0 ? (
                <p className="text-center text-muted-foreground">No data available yet</p>
              ) : (
                leaderboard.map((entry) => (
                  <div
                    key={entry.user_id}
                    className={`flex items-center justify-between p-4 rounded-lg border ${
                      entry.is_current_user ? 'bg-primary/5 border-primary' : 'bg-background'
                    }`}
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-12 flex items-center justify-center">
                        {getRankIcon(entry.rank)}
                      </div>
                      <Avatar>
                        <AvatarImage src={entry.photo_url} alt={entry.display_name} />
                        <AvatarFallback>{entry.display_name.charAt(0).toUpperCase()}</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-semibold">
                          {entry.display_name}
                          {entry.is_current_user && (
                            <Badge variant="secondary" className="ml-2">
                              You
                            </Badge>
                          )}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          Level {entry.level} • {entry.tasks_completed} tasks
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold text-primary">{entry.score}</p>
                      <p className="text-xs text-muted-foreground">points</p>
                      {entry.streak > 0 && (
                        <p className="text-sm">🔥 {entry.streak} day streak</p>
                      )}
                    </div>
                  </div>
                ))
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
