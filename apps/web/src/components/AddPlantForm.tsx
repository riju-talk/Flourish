import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Loader2, Plus, Sparkles } from 'lucide-react';
import { createAutonomousPlant } from '@/integrations/api';
import { useAuth } from '@/hooks/useAuth';

interface AddPlantFormProps {
  onPlantAdded?: () => void;
}

export default function AddPlantForm({ onPlantAdded }: AddPlantFormProps) {
  const { user } = useAuth();
  const [plantName, setPlantName] = useState('');
  const [userLocation, setUserLocation] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!plantName.trim()) return;

    setIsLoading(true);
    setMessage('');

    try {
      const result = await createAutonomousPlant(plantName.trim(), userLocation.trim() || undefined);

      setMessage(result.message || `Successfully added ${plantName}!`);
      setPlantName('');
      setUserLocation('');

      // Call callback if provided
      if (onPlantAdded) {
        onPlantAdded();
      }

      // Clear success message after 3 seconds
      setTimeout(() => setMessage(''), 3000);

    } catch (error: any) {
      setMessage(error.response?.data?.detail || 'Failed to add plant. Please try again.');
      console.error('Error adding plant:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="text-center">
        <div className="mx-auto w-12 h-12 bg-gradient-to-r from-flourish-green to-flourish-dark rounded-full flex items-center justify-center mb-2">
          <Sparkles className="h-6 w-6 text-white" />
        </div>
        <CardTitle className="text-xl">Add New Plant</CardTitle>
        <CardDescription>
          Just enter the plant name and I'll figure out everything else!
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="plantName">Plant Name *</Label>
            <Input
              id="plantName"
              type="text"
              placeholder="e.g., Snake Plant, Peace Lily, Spider Plant"
              value={plantName}
              onChange={(e) => setPlantName(e.target.value)}
              required
              disabled={isLoading}
              className="w-full"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="location">Your Location (Optional)</Label>
            <Input
              id="location"
              type="text"
              placeholder="e.g., Living Room, Bedroom, Office"
              value={userLocation}
              onChange={(e) => setUserLocation(e.target.value)}
              disabled={isLoading}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground">
              Help me recommend the best placement for your plant
            </p>
          </div>

          {message && (
            <div className={`p-3 rounded-md text-sm ${
              message.includes('Successfully')
                ? 'bg-green-50 text-green-800 border border-green-200'
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}>
              {message}
            </div>
          )}

          <Button
            type="submit"
            className="w-full"
            disabled={!plantName.trim() || isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Analyzing Plant...
              </>
            ) : (
              <>
                <Plus className="h-4 w-4 mr-2" />
                Add Plant & Create Schedule
              </>
            )}
          </Button>
        </form>

        <div className="mt-4 p-3 bg-blue-50 rounded-md">
          <p className="text-sm text-blue-800">
            <strong>What I'll do automatically:</strong>
          </p>
          <ul className="text-xs text-blue-700 mt-1 space-y-1">
            <li>• Identify the plant species and characteristics</li>
            <li>• Determine optimal lighting and watering needs</li>
            <li>• Figure out the best placement locations</li>
            <li>• Create a complete 90-day care schedule</li>
            <li>• Set up fertilizer and pest management</li>
            <li>• Generate daily health check reminders</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
