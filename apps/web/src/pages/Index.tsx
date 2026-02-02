import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Navbar } from "@/components/Navbar";
import { PlantCard } from "@/components/PlantCard";
import { DailyChecklist } from "@/components/DailyChecklist";
import { LeaderboardPreview } from "@/components/LeaderboardPreview";
import { AddPlantDialog } from "@/components/AddPlantDialog";
import { Button } from "@/components/ui/button";
import { Plus, Leaf, Calendar as CalendarIcon, Trophy, Sparkles } from "lucide-react";
import { getPlants, getTodayTasks, createPlant } from "@/integrations/api";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/useAuth";

const Index = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isAddPlantOpen, setIsAddPlantOpen] = useState(false);
  
  const { data: plants, isLoading: plantsLoading } = useQuery({
    queryKey: ["plants"],
    queryFn: getPlants,
  });

  const { data: schedule, isLoading: scheduleLoading } = useQuery({
    queryKey: ["today-schedule"],
    queryFn: getTodayTasks,
  });

  const addPlantMutation = useMutation({
    mutationFn: createPlant,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["plants"] });
      setIsAddPlantOpen(false);
      console.log("Plant added successfully!");
    },
    onError: (error) => {
      console.error("Failed to add plant:", error);
    },
  });

  const handleAddPlant = (plantData: any) => {
    addPlantMutation.mutate(plantData);
  };

  return (
    <div className="min-h-screen bg-transparent pb-12">
      <Navbar />
      <AddPlantDialog 
        open={isAddPlantOpen} 
        onOpenChange={setIsAddPlantOpen}
        onAddPlant={handleAddPlant}
      />

      <main className="container mx-auto px-4 py-8 space-y-10">
        {/* Hero / Header Section */}
        <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 animate-in fade-in slide-in-from-bottom-5 duration-700">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-primary/10 text-primary px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
                Today's Overview
              </span>
            </div>
            <h1 className="text-4xl md:text-5xl font-extrabold text-foreground tracking-tight">
              Hello, <span className="text-gradient">Botanist</span> <span className="inline-block animate-bounce">👋</span>
            </h1>
            <p className="text-muted-foreground mt-3 text-lg max-w-xl">
              Your garden is thriving! You have <strong className="text-primary">{schedule?.tasks?.length || 0} tasks</strong> pending for today.
            </p>
          </div>

          <div className="flex gap-3">
            <Button 
              className="vibrant-gradient hover-lift text-white rounded-full px-6 h-12 shadow-lg shadow-primary/20"
              onClick={() => setIsAddPlantOpen(true)}
            >
              <Plus className="mr-2 h-5 w-5" /> Add New Plant
            </Button>
            <Button 
              variant="outline" 
              className="rounded-full glass-card hover-lift h-12 border-white/20"
              onClick={() => navigate('/calendar')}
            >
              <CalendarIcon className="mr-2 h-5 w-5 text-muted-foreground" /> View Calendar
            </Button>
          </div>
        </header>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

          {/* Main Content Area - Left (8/12) */}
          <div className="lg:col-span-8 space-y-8">

            {/* Daily Progress & Checklist */}
            <section className="glass-card p-8 rounded-[2rem] space-y-6 animate-in slide-in-from-left duration-700 delay-100 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-32 bg-primary/5 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none"></div>

              <div className="flex items-center justify-between relative z-10">
                <div>
                  <h2 className="text-2xl font-bold flex items-center gap-2">
                    Daily Rituals <Sparkles className="h-5 w-5 text-yellow-400 fill-yellow-400" />
                  </h2>
                  <p className="text-muted-foreground text-sm">Keep your streak alive!</p>
                </div>
                <div className="text-2xl font-black text-gradient">65%</div>
              </div>

              <div className="w-full h-4 bg-secondary/50 rounded-full overflow-hidden p-1">
                <div className="h-full vibrant-gradient rounded-full transition-all duration-1000 shadow-sm" style={{ width: '65%' }}></div>
              </div>

              <div className="pt-2">
                <DailyChecklist tasks={schedule?.tasks || []} isLoading={scheduleLoading} />
              </div>
            </section>

            {/* Plant Inventory */}
            <section className="space-y-6 animate-in fade-in duration-1000 delay-200">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-foreground">My Jungle</h2>
                <Button variant="ghost" className="text-primary font-semibold hover:bg-primary/5 rounded-full">See all plants</Button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {plantsLoading ? (
                  Array(3).fill(0).map((_, i) => <Skeleton key={i} className="h-64 rounded-xl bg-white/20" />)
                ) : plants && plants.length > 0 ? (
                  plants.map((plant: any) => (
                    <PlantCard key={plant.id} plant={plant} className="hover-lift" />
                  ))
                ) : (
                  <div className="col-span-full py-16 text-center glass-card rounded-[2rem] flex flex-col items-center justify-center gap-4">
                    <div className="bg-secondary/50 p-6 rounded-full">
                      <Leaf className="w-12 h-12 text-muted-foreground" />
                    </div>
                    <div className="space-y-2">
                      <h3 className="text-xl font-bold text-foreground">No Plants Yet</h3>
                      <p className="text-muted-foreground font-medium">Your garden is empty. Time to plant something!</p>
                    </div>
                    <Button 
                      className="vibrant-gradient text-white rounded-full px-6"
                      onClick={() => setIsAddPlantOpen(true)}
                    >
                      <Plus className="mr-2 h-4 w-4" /> Add Your First Plant
                    </Button>
                  </div>
                )}
              </div>
            </section>
          </div>

          {/* Sidebar Area - Right (4/12) */}
          <aside className="lg:col-span-4 space-y-8 animate-in slide-in-from-right duration-700 delay-300">
            <LeaderboardPreview />

            {/* Quick Stats or Tips */}
            <div className="glass-card p-6 rounded-[2rem] bg-gradient-to-br from-primary/10 to-transparent border border-primary/10 relative overflow-hidden">
              <div className="absolute -bottom-4 -right-4 text-9xl opacity-5 select-none">🌿</div>
              <h3 className="text-lg font-bold text-primary mb-3 flex items-center gap-2">
                <span className="bg-primary text-white p-1 rounded-md text-xs">TIP</span>
                Botanist Wisdom
              </h3>
              <p className="text-sm leading-relaxed text-muted-foreground italic">
                "Wait, is it drooping or just napping? Most Monsteras prefer to dry out slightly before the next watering check."
              </p>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
};

export default Index;