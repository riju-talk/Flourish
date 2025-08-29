import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Sun, MapPin, Clock, Droplets } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useQueryClient } from '@tanstack/react-query';

interface Plant {
  id: string;
  name: string;
  type: string;
  location: string;
  sunlight_requirement: string;
  last_watered_date: string | null;
  health_status: string;
  image_url: string | null;
  watering_frequency_days: number;
}

interface PlantCardProps {
  plant: Plant;
}

const PlantCard: React.FC<PlantCardProps> = ({ plant }) => {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'Healthy':
        return 'bg-flourish-green/20 text-flourish-forest border-flourish-green/30';
      case 'Needs Attention':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'Critical':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-flourish-sage/20 text-flourish-dark border-flourish-sage/30';
    }
  };

  const getNextWateringDate = () => {
    if (!plant.last_watered_date) return 'Today';
    
    const lastWatered = new Date(plant.last_watered_date);
    const nextWatering = new Date(lastWatered);
    nextWatering.setDate(lastWatered.getDate() + plant.watering_frequency_days);
    
    const today = new Date();
    const diffTime = nextWatering.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays <= 0) return 'Today';
    if (diffDays === 1) return 'Tomorrow';
    return `In ${diffDays} days`;
  };

  const handleWaterNow = async () => {
    try {
      // For now, just show a success message - can be connected to API later
      toast({
        title: "Plant watered! 💧",
        description: `${plant.name} has been watered successfully.`,
      });

      // Refresh the data
      queryClient.invalidateQueries({ queryKey: ['plants'] });
      queryClient.invalidateQueries({ queryKey: ['todaysTasks'] });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update watering record",
        variant: "destructive",
      });
    }
  };

  const getLastWateredText = () => {
    if (!plant.last_watered_date) return 'Never watered';
    
    const lastWatered = new Date(plant.last_watered_date);
    const today = new Date();
    const diffTime = today.getTime() - lastWatered.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return '1 day ago';
    return `${diffDays} days ago`;
  };

  return (
    <Card className="bg-white/95 border-2 border-flourish-sage/30 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105 overflow-hidden relative">
      {plant.image_url && (
        <div className="h-40 bg-gradient-to-br from-flourish-cream to-flourish-sage/20 overflow-hidden relative">
          <img 
            src={plant.image_url} 
            alt={plant.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
        </div>
      )}
      
      <div className="absolute top-3 right-3">
        <Badge 
          className={`${getHealthColor(plant.health_status)} text-xs px-3 py-1 rounded-full border font-semibold shadow-sm`}
        >
          {plant.health_status}
        </Badge>
      </div>
      
      <CardHeader className="pb-3 pt-4">
        <CardTitle className="text-xl font-bold text-flourish-forest">{plant.name}</CardTitle>
        <Badge variant="outline" className="w-fit bg-flourish-cream/50 text-flourish-dark border-flourish-sage/40 font-medium">
          {plant.type}
        </Badge>
      </CardHeader>
      
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 gap-3">
          <div className="flex items-center space-x-2 text-sm text-flourish-dark/80">
            <div className="w-8 h-8 bg-flourish-sage/20 rounded-full flex items-center justify-center">
              <MapPin className="w-4 h-4 text-flourish-green" />
            </div>
            <span className="font-medium">{plant.location}</span>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-flourish-dark/80">
            <div className="w-8 h-8 bg-flourish-green/20 rounded-full flex items-center justify-center">
              <Sun className="w-4 h-4 text-flourish-green" />
            </div>
            <span className="font-medium">{plant.sunlight_requirement}</span>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-flourish-dark/80">
            <div className="w-8 h-8 bg-flourish-dark/20 rounded-full flex items-center justify-center">
              <Clock className="w-4 h-4 text-flourish-dark" />
            </div>
            <span className="font-medium">Last watered: {getLastWateredText()}</span>
          </div>
        </div>
        
        <div className="pt-3 border-t border-flourish-sage/20">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm font-semibold text-flourish-forest">
              Next watering: 
            </p>
            <span className="text-sm font-bold text-flourish-green">
              {getNextWateringDate()}
            </span>
          </div>
          <Button 
            size="sm" 
            className="w-full bg-gradient-to-r from-flourish-green to-flourish-dark hover:from-flourish-dark hover:to-flourish-forest text-white font-semibold py-2 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300"
            onClick={handleWaterNow}
          >
            <Droplets className="w-4 h-4 mr-2" />
            Water Now 💧
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default PlantCard;