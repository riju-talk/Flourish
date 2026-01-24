import { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Droplets, Thermometer, Sun, Leaf } from "lucide-react";
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
    <Card className={`glass-card rounded-3xl overflow-hidden group border-none ${className}`}>
      <div className="relative h-48 overflow-hidden">
        <img
          src={plant.image_url || "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=300&fit=crop"}
          alt={plant.name}
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
        />
        <div className="absolute top-3 left-3">
          <Badge className="bg-primary/80 backdrop-blur-md text-white border-none py-1 px-3">
            {plant.plant_type || "Indoor"}
          </Badge>
        </div>
      </div>
      <CardContent className="p-5 space-y-4">
        <div>
          <h3 className="text-xl font-bold text-foreground">{plant.name}</h3>
          <p className="text-xs text-muted-foreground italic">{plant.species}</p>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
            <Droplets size={14} className="text-blue-500" />
            {plant.watering_frequency_days}d cycle
          </div>
          <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
            <Sun size={14} className="text-yellow-500" />
            {plant.sunlight_requirement}
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
            <span>Health Score</span>
            <span>{plant.health_score}%</span>
          </div>
          <Progress value={plant.health_score} className="h-1.5 bg-secondary" />
        </div>
      </CardContent>
    </Card>
  );
};