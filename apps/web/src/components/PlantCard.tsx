import { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Droplets, Thermometer, Sun, Leaf, Heart } from "lucide-react";
import { Progress } from "@/components/ui/progress";

interface PlantCardProps {
  plant: {
    id: string;
    name: string;
    species: string;
    image_url?: string;
    health_score: number;
    watering_frequency_days: number;
    sunlight_requirement: string;
    plant_type: string;
  };
  className?: string;
}

export const PlantCard = ({ plant, className }: PlantCardProps) => {
  return (
    <div className={`glass-card group relative ${className}`}>
      {/* Floating Action Badge */}
      <div className="absolute top-3 right-3 z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <button className="bg-white/80 p-2 rounded-full shadow-lg hover:bg-white text-destructive">
          <Heart size={16} />
        </button>
      </div>

      <div className="relative h-56 overflow-hidden rounded-t-3xl">
        <img
          src={plant.image_url || "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=300&fit=crop"}
          alt={plant.name}
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
        />
        <div className="absolute top-3 left-3">
          <Badge className="bg-white/90 backdrop-blur-md text-primary font-bold shadow-sm border-none py-1.5 px-3 rounded-full">
            {plant.plant_type || "Indoor"}
          </Badge>
        </div>
        <div className="absolute bottom-0 left-0 right-0 h-24 bg-gradient-to-t from-black/60 to-transparent" />
      </div>

      <CardContent className="p-6 space-y-5">
        <div>
          <h3 className="text-xl font-bold text-foreground leading-tight">{plant.name}</h3>
          <p className="text-sm text-muted-foreground font-medium">{plant.species}</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="bg-blue-50/50 dark:bg-blue-900/20 p-2 rounded-xl flex items-center gap-2.5">
            <div className="bg-blue-100 dark:bg-blue-800 p-1.5 rounded-full text-blue-600 dark:text-blue-300">
              <Droplets size={14} />
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Water</span>
              <span className="text-xs font-semibold">{plant.watering_frequency_days}d</span>
            </div>
          </div>
          <div className="bg-amber-50/50 dark:bg-amber-900/20 p-2 rounded-xl flex items-center gap-2.5">
            <div className="bg-amber-100 dark:bg-amber-800 p-1.5 rounded-full text-amber-600 dark:text-amber-300">
              <Sun size={14} />
            </div>
            <div className="flex flex-col">
              <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Light</span>
              <span className="text-xs font-semibold">{plant.sunlight_requirement}</span>
            </div>
          </div>
        </div>

        <div className="space-y-2 pt-2 border-t border-border/50">
          <div className="flex justify-between items-end">
            <span className="text-xs font-bold text-muted-foreground uppercase tracking-wider">Health</span>
            <span className={`text-sm font-bold ${plant.health_score > 80 ? 'text-green-500' : 'text-yellow-500'}`}>
              {plant.health_score}%
            </span>
          </div>
          <Progress value={plant.health_score} className="h-2" />
        </div>
      </CardContent>
    </div>
  );
};