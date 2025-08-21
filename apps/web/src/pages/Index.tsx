import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/hooks/use-toast';
import { useQuery } from '@tanstack/react-query';

import {
  getDashboardData,
  getTodayTasks,
  createPlant,
  completeTask,
} from '@/integrations/api';

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';

import {
  Brain,
  Calendar,
  MessageSquare,
  Plus,
  Sun,
  Clock,
  LogOut,
  User,
  Heart,
  Zap,
  Target,
  TrendingUp,
  Camera,
  CheckCircle,
} from 'lucide-react';

import PlantCard from '@/components/PlantCard';
import CareCalendar from '@/components/CareCalendar';
import AIAssistant from '@/components/AIAssistant';
import AddPlantDialog from '@/components/AddPlantDialog';

const Index = () => {
  const { user, signOut } = useAuth();
  const { toast } = useToast();
  const [showAddPlant, setShowAddPlant] = useState(false);

  // Fetch dashboard data
  const {
    data: dashboardData,
    refetch: refetchDashboard,
    isLoading: dashboardLoading,
  } = useQuery({
    queryKey: ['dashboard', user?.uid],
    queryFn: () => getDashboardData(user!.uid),
    enabled: !!user,
  });

  // Fetch today's tasks
  const {
    data: todaysTasks = [],
    refetch: refetchTasks,
    isLoading: tasksLoading,
  } = useQuery({
    queryKey: ['todaysTasks', user?.uid],
    queryFn: () => getTodayTasks(user!.uid),
    enabled: !!user,
  });

  const handleSignOut = async () => {
    await signOut();
    toast({ title: 'Signed out', description: "You've been signed out." });
  };

  const handleAddPlant = async (plantData: any) => {
    try {
      await createPlant({ ...plantData, user_id: user!.uid });
      toast({ 
        title: 'Plant added! 🌱', 
        description: 'Your AI care schedule has been generated.' 
      });
      refetchDashboard();
      setShowAddPlant(false);
    } catch (err: any) {
      toast({
        title: 'Error adding plant',
        description: err.message || 'Something went wrong',
        variant: 'destructive',
      });
    }
  };

  const handleCompleteTask = async (taskId: string) => {
    try {
      await completeTask(taskId);
      toast({ 
        title: 'Task completed! ✅', 
        description: 'Great job taking care of your plants!' 
      });
      refetchTasks();
      refetchDashboard();
    } catch (err: any) {
      toast({
        title: 'Error completing task',
        description: err.message || 'Something went wrong',
        variant: 'destructive',
      });
    }
  };

  // Get happiness emoji based on overall health
  const getHappinessEmoji = (level: string) => {
    switch (level) {
      case 'happy': return '😊';
      case 'concerned': return '😐';
      case 'worried': return '😟';
      default: return '🌱';
    }
  };

  const stats = dashboardData?.stats || {
    total_plants: 0,
    healthy_plants: 0,
    tasks_completed_today: 0,
    streak_days: 0
  };

  const overallHealth = dashboardData?.overall_health_score || 0;
  const happinessLevel = dashboardData?.happiness_level || 'happy';
  const aiInsights = dashboardData?.ai_insights || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      {/* Header */}
      <header className="bg-white/90 backdrop-blur-sm border-b border-emerald-100 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl flex items-center justify-center relative">
              <Brain className="w-6 h-6 text-white absolute top-1 left-1" />
              <span className="text-white font-bold text-lg absolute bottom-1 right-1">🌱</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-teal-600 bg-clip-text text-transparent">
                PlantMind
              </h1>
              <p className="text-sm text-gray-600">Your AI Plant Care Agent</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <User className="w-4 h-4" />
              <span>{user?.email}</span>
            </div>
            <Button onClick={() => setShowAddPlant(true)} className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600">
              <Plus className="w-4 h-4 mr-2" />
              Add Plant
            </Button>
            <Button variant="outline" onClick={handleSignOut} size="sm">
              <LogOut className="w-4 h-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="text-center mb-12">
          <div className="text-6xl mb-4">{getHappinessEmoji(happinessLevel)}</div>
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            Your Garden is {happinessLevel === 'happy' ? 'Thriving' : happinessLevel === 'concerned' ? 'Doing Well' : 'Needs Attention'}!
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            PlantMind AI is actively monitoring your plants and optimizing their care schedules
          </p>
        </div>

        {/* Health Score & Stats */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <Card className="md:col-span-2 bg-gradient-to-r from-emerald-500 to-teal-500 text-white border-0">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold">Overall Plant Health</h3>
                  <p className="text-emerald-100">AI-calculated wellness score</p>
                </div>
                <Heart className="w-8 h-8 text-emerald-200" />
              </div>
              <div className="text-4xl font-bold mb-2">{overallHealth.toFixed(0)}%</div>
              <Progress value={overallHealth} className="bg-emerald-400" />
            </CardContent>
          </Card>
          
          <Card className="bg-white/70 backdrop-blur-sm border-emerald-200">
            <CardContent className="p-6 text-center">
              <Zap className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
              <div className="text-2xl font-bold text-gray-800">{stats.total_plants}</div>
              <div className="text-sm text-gray-600">Total Plants</div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/70 backdrop-blur-sm border-emerald-200">
            <CardContent className="p-6 text-center">
              <Target className="w-8 h-8 text-green-500 mx-auto mb-2" />
              <div className="text-2xl font-bold text-gray-800">{todaysTasks.length}</div>
              <div className="text-sm text-gray-600">Tasks Today</div>
            </CardContent>
          </Card>
          
          <Card className="bg-white/70 backdrop-blur-sm border-emerald-200">
            <CardContent className="p-6 text-center">
              <TrendingUp className="w-8 h-8 text-blue-500 mx-auto mb-2" />
              <div className="text-2xl font-bold text-gray-800">{stats.streak_days}</div>
              <div className="text-sm text-gray-600">Day Streak</div>
            </CardContent>
          </Card>
        </div>

        {/* AI Insights */}
        {aiInsights.length > 0 && (
          <Card className="mb-8 bg-gradient-to-r from-purple-50 to-pink-50 border-purple-200">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="w-5 h-5 text-purple-600" />
                <span>AI Insights</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {aiInsights.map((insight, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 flex-shrink-0" />
                    <p className="text-gray-700">{insight}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Tabs */}
        <Tabs defaultValue="dashboard" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8 bg-white/70 backdrop-blur-sm">
            <TabsTrigger value="dashboard" className="flex items-center space-x-2">
              <Sun className="w-4 h-4" /><span>Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="calendar" className="flex items-center space-x-2">
              <Calendar className="w-4 h-4" /><span>AI Schedule</span>
            </TabsTrigger>
            <TabsTrigger value="assistant" className="flex items-center space-x-2">
              <MessageSquare className="w-4 h-4" /><span>AI Assistant</span>
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Panel */}
          <TabsContent value="dashboard" className="space-y-8">
            {/* Today's Tasks */}
            <Card className="bg-white/70 backdrop-blur-sm border-emerald-200">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="w-5 h-5 text-emerald-600" />
                  <span>Today's AI-Generated Tasks</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {tasksLoading ? (
                  <p>Loading tasks…</p>
                ) : todaysTasks.length === 0 ? (
                  <div className="text-center py-8">
                    <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                    <p className="text-gray-500">All tasks completed! Your plants are happy 🌱</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {todaysTasks.map((task: any) => (
                      <div key={task.id} className="flex items-center justify-between p-4 bg-white/50 rounded-lg border border-emerald-100">
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${
                            task.task_type === 'watering' ? 'bg-blue-500' :
                            task.task_type === 'fertilizing' ? 'bg-green-500' :
                            task.task_type === 'checking' ? 'bg-purple-500' :
                            'bg-yellow-500'
                          }`} />
                          <div>
                            <span className="font-medium">{task.title}</span>
                            <p className="text-sm text-gray-500">{task.plant_name} • {task.estimated_time}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={task.priority === 'high' ? 'destructive' : 'outline'}>
                            {task.priority}
                          </Badge>
                          <Button 
                            size="sm" 
                            onClick={() => handleCompleteTask(task.id)}
                            className="bg-emerald-500 hover:bg-emerald-600"
                          >
                            Complete
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Plants Grid */}
            <div>
              <h3 className="text-2xl font-bold text-gray-800 mb-6">Your Plants</h3>
              {dashboardLoading ? (
                <p>Loading plants…</p>
              ) : !dashboardData?.plants || dashboardData.plants.length === 0 ? (
                <Card className="bg-white/70 backdrop-blur-sm border-emerald-200">
                  <CardContent className="p-12 text-center">
                    <div className="w-20 h-20 bg-gradient-to-r from-emerald-100 to-teal-100 rounded-full flex items-center justify-center mx-auto mb-6">
                      <Brain className="w-10 h-10 text-emerald-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-800 mb-2">Ready to start your AI-powered garden?</h3>
                    <p className="text-gray-600 mb-6">
                      Add your first plant and let PlantMind create a personalized care schedule with proactive monitoring!
                    </p>
                    <Button onClick={() => setShowAddPlant(true)} className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600">
                      <Plus className="w-4 h-4 mr-2" />
                      Add Your First Plant
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {dashboardData.plants.map((plant: any) => (
                    <PlantCard key={plant.id} plant={plant} />
                  ))}
                </div>
              )}
            </div>
          </TabsContent>

          {/* Calendar Panel */}
          <TabsContent value="calendar">
            <CareCalendar />
          </TabsContent>

          {/* AI Assistant Panel */}
          <TabsContent value="assistant">
            <AIAssistant />
          </TabsContent>
        </Tabs>
      </div>

      <AddPlantDialog
        open={showAddPlant}
        onOpenChange={setShowAddPlant}
        onAddPlant={handleAddPlant}
      />
    </div>
  );
};

export default Index;