
import React, { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface AddPlantDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAddPlant: (plant: any) => void;
}

const AddPlantDialog: React.FC<AddPlantDialogProps> = ({ open, onOpenChange, onAddPlant }) => {
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    location: '',
    sunlight: '',
    image: ''
  });

  const plantTypes = [
    "Indoor Plant",
    "Outdoor Plant",
    "Herb",
    "Succulent",
    "Flowering Plant",
    "Tree"
  ];

  const sunlightOptions = [
    "Full Sun",
    "Partial Sun",
    "Bright, indirect",
    "Low light",
    "Shade"
  ];

  const plantImages = [
    "https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=300&h=200&fit=crop",
    "https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07?w=300&h=200&fit=crop",
    "https://images.unsplash.com/photo-1535268647677-300dbf3d78d1?w=300&h=200&fit=crop",
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=300&h=200&fit=crop"
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name && formData.type && formData.location && formData.sunlight) {
      onAddPlant({
        name: formData.name,
        species: formData.type,
        location: formData.location,
        sunlight_requirement: formData.sunlight,
        image_url: formData.image || plantImages[Math.floor(Math.random() * plantImages.length)],
        plant_type: formData.type.toLowerCase().includes('indoor') ? 'indoor' : formData.type.toLowerCase().includes('outdoor') ? 'outdoor' : 'both',
        watering_frequency_days: 7,
        fertilizing_frequency_days: 30,
        pruning_frequency_days: 90,
        health_status: "healthy"
      });
      setFormData({ name: '', type: '', location: '', sunlight: '', image: '' });
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px] bg-white/95 backdrop-blur-sm">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold text-gray-800">Add New Plant</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Plant Name</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Monstera Deliciosa"
              className="border-green-200 focus:border-green-400"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="type">Plant Type</Label>
            <Select value={formData.type} onValueChange={(value) => setFormData({ ...formData, type: value })}>
              <SelectTrigger className="border-green-200 focus:border-green-400">
                <SelectValue placeholder="Select plant type" />
              </SelectTrigger>
              <SelectContent>
                {plantTypes.map((type) => (
                  <SelectItem key={type} value={type}>{type}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="location">Location</Label>
            <Input
              id="location"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              placeholder="e.g., Living Room, Balcony"
              className="border-green-200 focus:border-green-400"
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="sunlight">Sunlight Requirements</Label>
            <Select value={formData.sunlight} onValueChange={(value) => setFormData({ ...formData, sunlight: value })}>
              <SelectTrigger className="border-green-200 focus:border-green-400">
                <SelectValue placeholder="Select sunlight needs" />
              </SelectTrigger>
              <SelectContent>
                {sunlightOptions.map((option) => (
                  <SelectItem key={option} value={option}>{option}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancel
            </Button>
            <Button type="submit" className="bg-green-600 hover:bg-green-700">
              Add Plant
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export { AddPlantDialog };
export default AddPlantDialog;
