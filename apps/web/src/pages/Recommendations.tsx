import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { RecommendationCard } from "@/components/RecommendationCard";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useToast } from "@/hooks/use-toast";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getRecommendations,
  generateRecommendations,
  acceptRecommendation,
  dismissRecommendation,
} from "@/integrations/api";
import { Sparkles } from "lucide-react";

export default function RecommendationsPage() {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: recommendations, isLoading } = useQuery({
    queryKey: ["recommendations"],
    queryFn: getRecommendations,
  });

  const generateMutation = useMutation({
    mutationFn: () => generateRecommendations(3),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      toast({ title: "Fresh picks ready! 🌿" });
    },
    onError: () => {
      toast({ title: "Couldn't generate recommendations", variant: "destructive" });
    },
  });

  const acceptMutation = useMutation({
    mutationFn: (id: string) => acceptRecommendation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
      queryClient.invalidateQueries({ queryKey: ["plants"] });
      toast({ title: "Added to your garden! 🌱" });
    },
  });

  const dismissMutation = useMutation({
    mutationFn: (id: string) => dismissRecommendation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["recommendations"] });
    },
  });

  const isBusy = acceptMutation.isPending || dismissMutation.isPending;

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-10 space-y-8">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="font-serif text-4xl md:text-5xl font-semibold tracking-tight">Picked for your garden</h1>
            <p className="text-muted-foreground mt-1">
              Personalized plant suggestions based on what you already grow.
            </p>
          </div>
          <Button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="vibrant-gradient text-primary-foreground font-semibold rounded-full shadow-md hover:shadow-lg transition-shadow duration-500"
          >
            <Sparkles size={16} className="mr-2" />
            {generateMutation.isPending ? "Thinking..." : "Get New Suggestions"}
          </Button>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-96 rounded-3xl" />
            ))}
          </div>
        ) : recommendations && recommendations.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {recommendations.map((rec: any) => (
              <RecommendationCard
                key={rec.id}
                recommendation={rec}
                onAccept={(id) => acceptMutation.mutate(id)}
                onDismiss={(id) => dismissMutation.mutate(id)}
                isBusy={isBusy}
              />
            ))}
          </div>
        ) : (
          <div className="glass-card text-center py-16 px-6">
            <div className="w-16 h-16 vibrant-gradient rounded-3xl flex items-center justify-center mx-auto mb-4">
              <Sparkles className="text-primary-foreground" size={28} />
            </div>
            <h3 className="font-serif text-xl font-semibold mb-2">We're still learning about your garden</h3>
            <p className="text-muted-foreground mb-6 max-w-md mx-auto">
              Add a few plants, then ask PlantMind for suggestions tailored to your space.
            </p>
            <Button
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
              className="vibrant-gradient text-primary-foreground font-semibold rounded-full shadow-md hover:shadow-lg transition-shadow duration-500"
            >
              <Sparkles size={16} className="mr-2" /> Get My First Suggestions
            </Button>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
