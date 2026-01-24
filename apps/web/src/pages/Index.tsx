import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Navbar } from "@/components/Navbar";
import { PlantCard } from "@/components/PlantCard";
import { DailyChecklist } from "@/components/DailyChecklist";
import { LeaderboardPreview } from "@/components/LeaderboardPreview";
import { Button } from "@/components/ui/button";
import { Plus, Leaf, Calendar as CalendarIcon, Trophy } from "lucide-react";
import { getPlants, getTodaySchedule } from "@/integrations/api";
import { Skeleton } from "@/components/ui/skeleton";

const Index = () => {
  const { data: plants, isLoading: plantsLoading } = useQuery({
    queryKey: ["plants"],
    queryFn: getPlants,
  });

  const { data: schedule, isLoading: scheduleLoading } = useQuery({
    queryKey: ["today-schedule"],
    queryFn: getTodaySchedule,
  });

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <main className="container mx-auto px-4 py-8 space-y-8">
        {/* Header Section */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 animate-in fade-in duration-700">
          <div>
            <h1 className="text-4xl font-bold text-primary flex items-center gap-2">
              Welcome back, Botanist <Leaf className="text-primary leaf-pulse" />
            </h1>
            <p className="text-muted-foreground mt-2">Your garden is thriving today. You have {schedule?.tasks?.length || 0} tasks to complete.</p>
          </div>
          <div className="flex gap-3">
            <Button className="vibrant-gradient hover-lift text-white rounded-full px-6">
              <Plus className="mr-2 h-4 w-4" /> Add New Plant
            </Button>
            <Button variant="outline" className="rounded-full glass-card hover-lift">
              <CalendarIcon className="mr-2 h-4 w-4" /> View Calendar
            </Button>
          </div>
        </header>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

          {/* Main Content Area - Left (8/12) */}
          <div className="lg:col-span-8 space-y-8">

            {/* Daily Progress & Checklist */}
            <section className="glass-card p-6 rounded-3xl space-y-4 animate-in slide-in-from-left duration-500">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-semibold flex items-center gap-2">
                  Daily Checklist <Trophy className="h-5 w-5 text-yellow-500" />
                </h2>
                <div className="text-sm font-medium text-primary">65% Progress</div>
              </div>
              <div className="w-full h-3 bg-secondary rounded-full overflow-hidden">
                <div className="h-full vibrant-gradient transition-all duration-1000" style={{ width: '65%' }}></div>
              </div>
              <DailyChecklist tasks={schedule?.tasks || []} isLoading={scheduleLoading} />
            </section>

            {/* Plant Inventory */}
            <section className="space-y-4 animate-in fade-in duration-1000">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-semibold">Your Plant Family</h2>
                <Button variant="ghost" className="text-primary">View All</Button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {plantsLoading ? (
                  Array(3).fill(0).map((_, i) => <Skeleton key={i} className="h-64 rounded-3xl" />)
                ) : (plants && plants.length > 0) ? (
                  plants.map((plant: any) => (
                    <PlantCard key={plant.id} plant={plant} className="hover-lift" />
                  ))
                ) : (
                  <div className="col-span-full py-12 text-center glass-card rounded-3xl italic text-muted-foreground">
                    No plants yet. Start your journey by adding one!
                  </div>
                )}
              </div>
            </section>
          </div>

          {/* Sidebar Area - Right (4/12) */}
          <aside className="lg:col-span-4 space-y-8 animate-in slide-in-from-right duration-500">
            <LeaderboardPreview />

            {/* Quick Stats or Tips */}
            <div className="glass-card p-6 rounded-3xl bg-primary/5 border-primary/20">
              <h3 className="text-lg font-bold text-primary mb-3">Botanist Tip of the Day</h3>
              <p className="text-sm italic">
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