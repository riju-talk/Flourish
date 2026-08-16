import { useState, useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Seo } from "@/components/Seo";
import { PlantCard } from "@/components/PlantCard";
import { DailyChecklist } from "@/components/DailyChecklist";
import { LeaderboardPreview } from "@/components/LeaderboardPreview";
import { AddPlantDialog } from "@/components/AddPlantDialog";
import { Button } from "@/components/ui/button";
import { Plus, Leaf, Calendar as CalendarIcon, Trophy, Sparkles } from "lucide-react";
import { getPlants, getTodayProgress, generateRecommendations } from "@/integrations/api";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/useAuth";

const getGreeting = () => {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
};

const Index = () => {
  const { user, profile } = useAuth();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isAddPlantOpen, setIsAddPlantOpen] = useState(false);
  
  const { data: plants, isLoading: plantsLoading } = useQuery({
    queryKey: ["plants"],
    queryFn: getPlants,
  });

  const { data: todayProgress, isLoading: scheduleLoading } = useQuery({
    queryKey: ["today-schedule"],
    queryFn: getTodayProgress,
  });
  const schedule = todayProgress?.tasks;
  const completionPercent = todayProgress?.completion_percent ?? 0;

  const handlePlantAdded = () => {
    queryClient.invalidateQueries({ queryKey: ["plants"] });
    queryClient.invalidateQueries({ queryKey: ["today-schedule"] });
    // Fire-and-forget: let PlantMind refresh suggestions in the background now that
    // the garden has grown, so "For You" stays current without the user asking.
    generateRecommendations(3)
      .then(() => queryClient.invalidateQueries({ queryKey: ["recommendations"] }))
      .catch(() => {});
  };

  return (
    <div className="min-h-screen bg-transparent flex flex-col">
      <Seo title="Dashboard" description="Your garden at a glance - today's care tasks, plant health, and quick actions." />
      <Navbar />
      <AddPlantDialog
        open={isAddPlantOpen}
        onOpenChange={setIsAddPlantOpen}
        onSuccess={handlePlantAdded}
      />

      <main className="flex-1 container mx-auto px-4 py-8 space-y-10">
        {/* Hero / Header Section */}
        <header className="flex flex-col md:flex-row md:items-end justify-between gap-6 animate-in fade-in slide-in-from-bottom-3 duration-1000 ease-out">
          <div>
            <p className="text-xs font-semibold tracking-widest text-muted-foreground uppercase mb-2">
              Today's Overview
            </p>
            <h1 className="font-serif text-4xl md:text-5xl font-semibold text-foreground tracking-tight">
              {getGreeting()}, {profile?.full_name?.split(' ')[0] || 'Botanist'}.
            </h1>
            <p className="text-muted-foreground mt-3 text-lg max-w-xl">
              Your garden is thriving. You have <strong className="text-primary">{schedule?.length || 0} tasks</strong> pending today.
            </p>
          </div>

          <div className="flex gap-3">
            <Button
              className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl px-6 h-12 shadow-sm"
              onClick={() => setIsAddPlantOpen(true)}
            >
              <Plus className="mr-2 h-5 w-5" /> Add New Plant
            </Button>
            <Button
              variant="outline"
              className="rounded-xl glass-card hover-lift h-12"
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
            <section className="glass-card p-8 space-y-6 animate-in fade-in slide-in-from-left-4 duration-1000 ease-out delay-100">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="font-serif text-2xl font-semibold flex items-center gap-2">
                    Daily Rituals <Sparkles className="h-5 w-5 text-amber-500" />
                  </h2>
                  <p className="text-muted-foreground text-sm">Consistency is the root of growth.</p>
                </div>
                <div className="text-2xl font-bold text-primary">{completionPercent}%</div>
              </div>

              <div className="w-full h-2.5 bg-secondary rounded-full overflow-hidden">
                <div className="h-full bg-primary rounded-full transition-all duration-1000" style={{ width: `${completionPercent}%` }}></div>
              </div>

              <div className="pt-2">
                <DailyChecklist tasks={schedule || []} isLoading={scheduleLoading} />
              </div>
            </section>

            {/* Plant Inventory */}
            <section className="space-y-6 animate-in fade-in duration-1000 ease-out delay-200">
              <div className="flex items-center justify-between">
                <h2 className="font-serif text-2xl font-semibold text-foreground">My Garden</h2>
                <Button variant="ghost" className="text-primary font-semibold hover:bg-primary/5 rounded-full">See all plants</Button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {plantsLoading ? (
                  Array(3).fill(0).map((_, i) => <Skeleton key={i} className="h-64 rounded-xl" />)
                ) : plants && plants.length > 0 ? (
                  plants.map((plant: any) => (
                    <PlantCard key={plant.id} plant={plant} className="hover-lift" />
                  ))
                ) : (
                  <div className="col-span-full py-16 text-center glass-card flex flex-col items-center justify-center gap-4">
                    <div className="bg-secondary p-6 rounded-full">
                      <Leaf className="w-12 h-12 text-muted-foreground" />
                    </div>
                    <div className="space-y-2">
                      <h3 className="font-serif text-xl font-semibold text-foreground">Your garden is waiting</h3>
                      <p className="text-muted-foreground">Add your first plant and start tracking its growth.</p>
                    </div>
                    <Button
                      className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl px-6"
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
          <aside className="lg:col-span-4 space-y-8 animate-in fade-in slide-in-from-right-4 duration-1000 ease-out delay-300">
            <LeaderboardPreview />

            {/* Botanist Wisdom */}
            <div className="bg-primary text-primary-foreground rounded-2xl p-6 relative overflow-hidden">
              <h3 className="font-serif text-lg font-semibold mb-3">Botanist Wisdom</h3>
              <p className="text-sm leading-relaxed text-primary-foreground/80 italic">
                "During the dormant winter months, reduce watering significantly.
                Overwatering when growth has slowed is the leading cause of root rot
                in aroid species."
              </p>
            </div>

            {/* New Plants Recommended */}
            <button
              onClick={() => navigate('/recommendations')}
              className="glass-card hover-lift p-6 w-full text-left group"
            >
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="h-4 w-4 text-primary" />
                <h3 className="font-serif text-lg font-semibold text-foreground">
                  New Plants Recommended For You
                </h3>
              </div>
              <p className="text-sm text-muted-foreground">
                Fresh picks based on your garden and care habits.
                <span className="text-primary font-medium group-hover:underline"> See your picks →</span>
              </p>
            </button>
          </aside>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Index;