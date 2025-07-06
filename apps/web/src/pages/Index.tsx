// pages/index.tsx

import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/hooks/use-toast';
import { useQuery } from '@tanstack/react-query';

import {
  getPlants,
  getCareTasks,
  createPlant,
} from '@/integrations/api';           // ← your API helpers

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';

import {
  Calendar,
  MessageSquare,
  Plus,
  Sun,
  Clock,
  LogOut,
  User,
} from 'lucide-react';

import PlantCard from '@/components/PlantCard';
import CareCalendar from '@/components/CareCalendar';
import AIAssistant from '@/components/AIAssistant';
import AddPlantDialog from '@/components/AddPlantDialog';

const Index = () => {
  const { user, signOut } = useAuth();
  const { toast } = useToast();
  const [showAddPlant, setShowAddPlant] = useState(false);

  // — Fetch all plants for this user
  const {
    data: plants = [],
    refetch: refetchPlants,
    isLoading: plantsLoading,
  } = useQuery({
    queryKey: ['plants', user?.id],
    queryFn: () => getPlants(),
    enabled: !!user,
  });

  // — Fetch today’s pending tasks
  const {
    data: todaysTasks = [],
    isLoading: tasksLoading,
  } = useQuery({
    queryKey: ['todaysTasks', user?.id],
    queryFn: () =>
      getCareTasks({ status: 'pending' }).then((tasks) =>
        tasks.filter(
          (t) => t.scheduled_date === new Date().toISOString().split('T')[0]
        )
      ),
    enabled: !!user,
  });

  const handleSignOut = async () => {
    await signOut();
    toast({ title: 'Signed out', description: "You've been signed out." });
  };

  const handleAddPlant = async (plantData: any) => {
    try {
      await createPlant({ ...plantData, user_id: user!.id });
      toast({ title: 'Plant added!', description: 'Your plant was created.' });
      refetchPlants();
      setShowAddPlant(false);
    } catch (err: any) {
      toast({
        title: 'Error adding plant',
        description: err.message || 'Something went wrong',
        variant: 'destructive',
      });
    }
  };

  // Stats
  const healthyPlants = plants.filter((p) => p.health_status === 'Healthy').length;
  const plantsNeedingAttention = plants.filter((p) => p.health_status === 'Needs Attention').length;

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-green-100 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">🌱</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-800">HaritPal</h1>
              <p className="text-sm text-gray-600">Your Smart Plant Care Assistant</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <User className="w-4 h-4" />
              <span>{user?.email}</span>
            </div>
            <Button onClick={() => setShowAddPlant(true)} className="bg-green-600 hover:bg-green-700">
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
        {/* Welcome */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            Welcome to Your Garden Dashboard
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Track your plants, get personalized care reminders, and let our AI assistant help you grow a thriving garden
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-white/60 backdrop-blur-sm border-green-200">
            <CardContent className="p-6 text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">{plants.length}</div>
              <div className="text-sm text-gray-600">Total Plants</div>
            </CardContent>
          </Card>
          <Card className="bg-white/60 backdrop-blur-sm border-blue-200">
            <CardContent className="p-6 text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">{todaysTasks.length}</div>
              <div className="text-sm text-gray-600">Tasks Today</div>
            </CardContent>
          </Card>
          <Card className="bg-white/60 backdrop-blur-sm border-yellow-200">
            <CardContent className="p-6 text-center">
              <div className="text-3xl font-bold text-yellow-600 mb-2">{plantsNeedingAttention}</div>
              <div className="text-sm text-gray-600">Needs Attention</div>
            </CardContent>
          </Card>
          <Card className="bg-white/60 backdrop-blur-sm border-green-200">
            <CardContent className="p-6 text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">{healthyPlants}</div>
              <div className="text-sm text-gray-600">Healthy Plants</div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="dashboard" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-8 bg-white/60 backdrop-blur-sm">
            <TabsTrigger value="dashboard" className="flex items-center space-x-2">
              <Sun className="w-4 h-4" /><span>Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="calendar" className="flex items-center space-x-2">
              <Calendar className="w-4 h-4" /><span>Care Calendar</span>
            </TabsTrigger>
            <TabsTrigger value="assistant" className="flex items-center space-x-2">
              <MessageSquare className="w-4 h-4" /><span>AI Assistant</span>
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Panel */}
          <TabsContent value="dashboard" className="space-y-8">
            <Card className="bg-white/60 backdrop-blur-sm border-green-200">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="w-5 h-5 text-green-600" /><span>Today's Tasks</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {tasksLoading ? (
                  <p>Loading tasks…</p>
                ) : todaysTasks.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No tasks scheduled for today!</p>
                ) : (
                  <div className="space-y-3">
                    {todaysTasks.map((task) => (
                      <div key={task.id} className="flex items-center justify-between p-3 bg-white/50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${
                            task.task_type === 'watering' ? 'bg-blue-500' :
                            task.task_type === 'fertilizing' ? 'bg-green-500' :
                            'bg-yellow-500'
                          }`} />
                          <span className="font-medium">{task.title}</span>
                        </div>
                        <Badge variant="outline">{task.task_type}</Badge>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Plants Grid / Fallback */}
            <div>
              <h3 className="text-2xl font-bold text-gray-800 mb-6">Your Plants</h3>
              {plantsLoading ? (
                <p>Loading plants…</p>
              ) : plants.length === 0 ? (
                <Card className="bg-white/60 backdrop-blur-sm border-green-200">
                  <CardContent className="p-12 text-center">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Plus className="w-8 h-8 text-green-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-gray-800 mb-2">No plants yet</h3>
                    <p className="text-gray-600 mb-4">
                      Start your plant care journey by adding your first plant!
                    </p>
                    <Button onClick={() => setShowAddPlant(true)} className="bg-green-600 hover:bg-green-700">
                      Add Your First Plant
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {plants.map((plant) => (
                    <PlantCard key={plant.id} plant={plant} />
                  ))}
                </div>
              )}
            </div>
          </TabsContent>

          {/* Calendar Panel */}
          <TabsContent value="calendar">
            <CareCalendar tasks={todaysTasks} />
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
