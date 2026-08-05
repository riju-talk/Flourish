import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { AlertTriangle, Link as LinkIcon, Plus, X } from "lucide-react";

interface RecommendationCardProps {
  recommendation: {
    id: string;
    plant_name: string;
    scientific_name?: string;
    image_url?: string;
    reasoning?: string;
    difficulty?: string;
    warnings?: string[];
    sources?: string[];
  };
  onAccept: (id: string) => void;
  onDismiss: (id: string) => void;
  isBusy?: boolean;
}

export const RecommendationCard = ({ recommendation, onAccept, onDismiss, isBusy }: RecommendationCardProps) => {
  const { id, plant_name, scientific_name, image_url, reasoning, difficulty, warnings, sources } = recommendation;

  return (
    <div className="glass-card hover-lift relative overflow-hidden">
      <button
        onClick={() => onDismiss(id)}
        disabled={isBusy}
        className="absolute top-3 right-3 z-10 bg-white/80 p-1.5 rounded-full shadow-sm hover:bg-destructive/10 hover:text-destructive transition-colors"
      >
        <X size={14} />
      </button>

      <div className="relative aspect-square overflow-hidden rounded-t-3xl">
        <img
          src={image_url || "https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=400&fit=crop"}
          alt={plant_name}
          className="w-full h-full object-cover"
        />
      </div>

      <div className="p-5 space-y-3">
        <div>
          <h3 className="text-lg font-bold text-foreground leading-tight">{plant_name}</h3>
          {scientific_name && (
            <p className="text-xs text-muted-foreground italic">{scientific_name}</p>
          )}
        </div>

        {difficulty && (
          <Badge variant="secondary" className="capitalize">{difficulty}</Badge>
        )}

        {reasoning && (
          <p className="text-sm text-muted-foreground leading-relaxed">{reasoning}</p>
        )}

        {warnings && warnings.length > 0 && (
          <div className="flex items-start gap-2 text-xs text-amber-600 dark:text-amber-400">
            <AlertTriangle size={14} className="mt-0.5 shrink-0" />
            <span>{warnings.join(" · ")}</span>
          </div>
        )}

        {sources && sources.length > 0 && (
          <a
            href={sources[0]}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1 text-xs text-muted-foreground hover:text-primary transition-colors"
          >
            <LinkIcon size={12} /> Sourced
          </a>
        )}

        <Button
          onClick={() => onAccept(id)}
          disabled={isBusy}
          className="w-full vibrant-gradient text-white font-semibold rounded-full shadow-md hover:shadow-glow"
        >
          <Plus size={16} className="mr-1" /> Add to My Garden
        </Button>
      </div>
    </div>
  );
};

export default RecommendationCard;
