import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Sparkles, Loader2 } from 'lucide-react';
import { createAutonomousPlant } from '@/integrations/api';

interface AddPlantDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

const AddPlantDialog: React.FC<AddPlantDialogProps> = ({ open, onOpenChange, onSuccess }) => {
  const [plantName, setPlantName] = useState('');
  const [location, setLocation] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!plantName.trim() || isSubmitting) return;

    setIsSubmitting(true);
    setError(null);
    try {
      await createAutonomousPlant(plantName.trim(), location.trim() || undefined);
      setPlantName('');
      setLocation('');
      onOpenChange(false);
      onSuccess();
    } catch (err) {
      setError("Couldn't add that plant right now. Try again in a moment.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(next) => !isSubmitting && onOpenChange(next)}>
      <DialogContent className="sm:max-w-[440px]">
        <DialogHeader>
          <DialogTitle className="font-serif text-xl flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" /> Add a Plant
          </DialogTitle>
          <DialogDescription>
            PlantMind will research its care needs, find a matching photo, and build its
            watering &amp; fertilizing schedule automatically.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="plant-name">Plant name</Label>
            <Input
              id="plant-name"
              value={plantName}
              onChange={(e) => setPlantName(e.target.value)}
              placeholder="e.g., Monstera Deliciosa, Snake Plant, Basil"
              autoFocus
              disabled={isSubmitting}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="location">Where will it live? (optional)</Label>
            <Input
              id="location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="e.g., Living Room, Balcony"
              disabled={isSubmitting}
            />
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}

          <div className="flex justify-end space-x-2 pt-2">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={!plantName.trim() || isSubmitting}
              className="bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Researching...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" /> Add to My Garden
                </>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export { AddPlantDialog };
export default AddPlantDialog;
