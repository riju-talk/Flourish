import { useState } from 'react';
import { Search, Loader2, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { lookupPlant, createAutonomousPlant } from '@/integrations/api';
import { useToast } from '@/hooks/use-toast';

export default function PlantLookup() {
  const [plantName, setPlantName] = useState('');
  const [loading, setLoading] = useState(false);
  const [plantInfo, setPlantInfo] = useState<any>(null);
  const [adding, setAdding] = useState(false);
  const { toast } = useToast();

  const handleLookup = async () => {
    if (!plantName.trim()) return;

    setLoading(true);
    try {
      const result = await lookupPlant(plantName);
      setPlantInfo(result.plant_info);
    } catch (error: any) {
      toast({
        title: 'Lookup Failed',
        description: error.response?.data?.detail || 'Failed to lookup plant information',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleAddToInventory = async () => {
    if (!plantInfo) return;

    setAdding(true);
    try {
      await createAutonomousPlant(plantInfo.common_name || plantName);
      toast({
        title: 'Plant Added!',
        description: `${plantInfo.common_name} has been added to your inventory`,
      });
      // Reset form
      setPlantName('');
      setPlantInfo(null);
    } catch (error: any) {
      toast({
        title: 'Failed to Add Plant',
        description: error.response?.data?.detail || 'Something went wrong',
        variant: 'destructive',
      });
    } finally {
      setAdding(false);
    }
  };

  const getCareLevelColor = (level: string) => {
    switch (level) {
      case 'easy':
        return 'bg-green-500';
      case 'moderate':
        return 'bg-yellow-500';
      case 'difficult':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="container mx-auto px-4 py-14 max-w-4xl">
      <div className="text-center mb-10">
        <p className="text-xs font-semibold tracking-widest text-muted-foreground uppercase mb-3">
          Discovery Engine
        </p>
        <h1 className="font-serif text-4xl md:text-5xl font-semibold text-foreground mb-4">
          Agentic Plant Lookup
        </h1>
        <p className="text-muted-foreground max-w-xl mx-auto">
          Harness our botanical AI to instantly identify flora, diagnose issues, or
          uncover specialized care protocols. Enter a plant name below.
        </p>
      </div>

      <div className="glass-card p-3 flex gap-2 mb-10 max-w-2xl mx-auto">
        <Input
          placeholder="e.g., Monstera Deliciosa, Snake Plant, Peace Lily..."
          value={plantName}
          onChange={(e) => setPlantName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleLookup()}
          disabled={loading}
          className="border-none bg-transparent focus-visible:ring-0"
        />
        <Button
          onClick={handleLookup}
          disabled={loading || !plantName.trim()}
          className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl shrink-0"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              Looking up...
            </>
          ) : (
            <>
              <Search className="h-4 w-4 mr-2" />
              Analyze
            </>
          )}
        </Button>
      </div>

      {plantInfo && (
        <Card>
          <CardContent className="pt-6">
            <div className="space-y-6">
              {/* Header with Image */}
              <div className="flex flex-col md:flex-row gap-6">
                {plantInfo.image_url && (
                  <img
                    src={plantInfo.image_url}
                    alt={plantInfo.common_name}
                    className="w-full md:w-48 h-48 object-cover rounded-lg"
                  />
                )}
                <div className="flex-1">
                  <h2 className="text-2xl font-bold">{plantInfo.common_name}</h2>
                  {plantInfo.scientific_name && (
                    <p className="text-muted-foreground italic">{plantInfo.scientific_name}</p>
                  )}
                  <div className="flex gap-2 mt-3">
                    <Badge className={getCareLevelColor(plantInfo.care_level)}>
                      {plantInfo.care_level || 'Unknown'} Care
                    </Badge>
                    {plantInfo.toxicity?.pets && (
                      <Badge variant={plantInfo.toxicity.pets === 'toxic' ? 'destructive' : 'default'}>
                        {plantInfo.toxicity.pets === 'toxic' ? '⚠️ Toxic to Pets' : '✅ Pet Safe'}
                      </Badge>
                    )}
                  </div>
                  <Button onClick={handleAddToInventory} disabled={adding} className="mt-4">
                    {adding ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Adding...
                      </>
                    ) : (
                      <>
                        <Plus className="h-4 w-4 mr-2" />
                        Add to My Plants
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {/* Detailed Information Tabs */}
              <Tabs defaultValue="care" className="w-full">
                <TabsList className="grid w-full grid-cols-4">
                  <TabsTrigger value="care">Care</TabsTrigger>
                  <TabsTrigger value="environment">Environment</TabsTrigger>
                  <TabsTrigger value="issues">Common Issues</TabsTrigger>
                  <TabsTrigger value="facts">Facts</TabsTrigger>
                </TabsList>

                <TabsContent value="care" className="space-y-4">
                  {/* Watering */}
                  {plantInfo.watering && (
                    <div className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
                      <h3 className="font-semibold mb-2 flex items-center">
                        💧 Watering
                      </h3>
                      <p className="text-sm mb-1"><strong>Frequency:</strong> {plantInfo.watering.frequency}</p>
                      <p className="text-sm mb-1"><strong>Amount:</strong> {plantInfo.watering.amount}</p>
                      <p className="text-sm text-muted-foreground">{plantInfo.watering.tips}</p>
                    </div>
                  )}

                  {/* Sunlight */}
                  {plantInfo.sunlight && (
                    <div className="p-4 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
                      <h3 className="font-semibold mb-2 flex items-center">
                        ☀️ Sunlight
                      </h3>
                      <p className="text-sm mb-1"><strong>Requirement:</strong> {plantInfo.sunlight.requirement}</p>
                      <p className="text-sm text-muted-foreground">{plantInfo.sunlight.details}</p>
                    </div>
                  )}

                  {/* Fertilizing */}
                  {plantInfo.fertilizing && (
                    <div className="p-4 bg-green-50 dark:bg-green-950 rounded-lg">
                      <h3 className="font-semibold mb-2 flex items-center">
                        🌿 Fertilizing
                      </h3>
                      <p className="text-sm mb-1"><strong>Frequency:</strong> {plantInfo.fertilizing.frequency}</p>
                      <p className="text-sm"><strong>Type:</strong> {plantInfo.fertilizing.type}</p>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="environment" className="space-y-4">
                  {/* Temperature */}
                  {plantInfo.temperature && (
                    <div className="p-4 bg-orange-50 dark:bg-orange-950 rounded-lg">
                      <h3 className="font-semibold mb-2">🌡️ Temperature</h3>
                      <p className="text-sm mb-1"><strong>Range:</strong> {plantInfo.temperature.min}°F - {plantInfo.temperature.max}°F</p>
                      <p className="text-sm text-muted-foreground">{plantInfo.temperature.ideal}</p>
                    </div>
                  )}

                  {/* Humidity */}
                  {plantInfo.humidity && (
                    <div className="p-4 bg-cyan-50 dark:bg-cyan-950 rounded-lg">
                      <h3 className="font-semibold mb-2">💨 Humidity</h3>
                      <p className="text-sm mb-1"><strong>Requirement:</strong> {plantInfo.humidity.requirement}</p>
                      <p className="text-sm"><strong>Level:</strong> {plantInfo.humidity.percentage}</p>
                    </div>
                  )}

                  {/* Soil */}
                  {plantInfo.soil && (
                    <div className="p-4 bg-amber-50 dark:bg-amber-950 rounded-lg">
                      <h3 className="font-semibold mb-2">🌱 Soil</h3>
                      <p className="text-sm mb-1"><strong>Type:</strong> {plantInfo.soil.type}</p>
                      <p className="text-sm"><strong>pH:</strong> {plantInfo.soil.ph}</p>
                    </div>
                  )}

                  {/* Growth */}
                  {plantInfo.growth && (
                    <div className="p-4 bg-lime-50 dark:bg-lime-950 rounded-lg">
                      <h3 className="font-semibold mb-2">📈 Growth</h3>
                      <p className="text-sm mb-1"><strong>Rate:</strong> {plantInfo.growth.rate}</p>
                      <p className="text-sm"><strong>Max Size:</strong> {plantInfo.growth.max_size}</p>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="issues" className="space-y-2">
                  {plantInfo.common_issues && plantInfo.common_issues.length > 0 ? (
                    <ul className="space-y-2">
                      {plantInfo.common_issues.map((issue: string, idx: number) => (
                        <li key={idx} className="flex items-start p-3 bg-accent rounded-lg">
                          <span className="mr-2">⚠️</span>
                          <span className="text-sm">{issue}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted-foreground text-center py-8">No common issues reported</p>
                  )}

                  {plantInfo.propagation && plantInfo.propagation.length > 0 && (
                    <div className="mt-6">
                      <h3 className="font-semibold mb-2">🌱 Propagation Methods</h3>
                      <div className="flex flex-wrap gap-2">
                        {plantInfo.propagation.map((method: string, idx: number) => (
                          <Badge key={idx} variant="outline">{method}</Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="facts" className="space-y-2">
                  {plantInfo.interesting_facts && plantInfo.interesting_facts.length > 0 ? (
                    <ul className="space-y-2">
                      {plantInfo.interesting_facts.map((fact: string, idx: number) => (
                        <li key={idx} className="flex items-start p-3 bg-accent rounded-lg">
                          <span className="mr-2">💡</span>
                          <span className="text-sm">{fact}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted-foreground text-center py-8">No interesting facts available</p>
                  )}
                </TabsContent>
              </Tabs>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
