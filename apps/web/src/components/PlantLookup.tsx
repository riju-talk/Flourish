import { useEffect, useRef, useState } from 'react';
import {
  Search, Loader2, Plus, Droplet, Sun, Leaf, Globe, Home,
  AlertTriangle, Lightbulb, ExternalLink, ShieldCheck, ShieldAlert,
  X, Sprout, SearchX, Clock,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { lookupPlant, createAutonomousPlant } from '@/integrations/api';
import { useToast } from '@/hooks/use-toast';

const POPULAR_SEARCHES = ['Monstera', 'Pothos', 'Snake Plant', 'Peace Lily', 'Fiddle Leaf Fig', 'Succulent'];
const RECENT_SEARCHES_KEY = 'flourish-explore-recent-searches';
const MAX_RECENT = 6;

const CARE_LEVEL_STYLES: Record<string, string> = {
  easy: 'bg-emerald-500 hover:bg-emerald-500',
  moderate: 'bg-amber-500 hover:bg-amber-500',
  difficult: 'bg-red-500 hover:bg-red-500',
};

const hostname = (url: string) => {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
};

export default function PlantLookup() {
  const [plantName, setPlantName] = useState('');
  const [loading, setLoading] = useState(false);
  const [plantInfo, setPlantInfo] = useState<any>(null);
  const [notFound, setNotFound] = useState(false);
  const [adding, setAdding] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  useEffect(() => {
    try {
      const stored = localStorage.getItem(RECENT_SEARCHES_KEY);
      if (stored) setRecentSearches(JSON.parse(stored));
    } catch {
      // localStorage unavailable - recent searches just won't persist
    }
  }, []);

  const rememberSearch = (name: string) => {
    setRecentSearches((prev) => {
      const next = [name, ...prev.filter((s) => s.toLowerCase() !== name.toLowerCase())].slice(0, MAX_RECENT);
      try {
        localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(next));
      } catch {
        // ignore
      }
      return next;
    });
  };

  const runLookup = async (query: string) => {
    if (!query.trim() || loading) return;

    setLoading(true);
    setNotFound(false);
    try {
      const result = await lookupPlant(query);
      setPlantInfo(result.plant_info);
      rememberSearch(query.trim());
    } catch (error: any) {
      setPlantInfo(null);
      setNotFound(true);
      toast({
        title: 'Search failed',
        description: error.response?.data?.detail || "Couldn't find information for that plant",
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearchClick = (query: string) => {
    setPlantName(query);
    runLookup(query);
  };

  const handleClear = () => {
    setPlantName('');
    setPlantInfo(null);
    setNotFound(false);
    inputRef.current?.focus();
  };

  const handleAddToInventory = async () => {
    if (!plantInfo) return;

    setAdding(true);
    try {
      await createAutonomousPlant(plantInfo.common_name || plantName);
      toast({
        title: 'Plant Added',
        description: `${plantInfo.common_name} has been added to your inventory`,
      });
      handleClear();
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

  const hasResult = !loading && plantInfo;
  const isIdle = !loading && !plantInfo && !notFound;

  return (
    <div className="container mx-auto px-4 max-w-4xl">
      {/* Search header - centered hero when idle, compact once a search has run */}
      <div className={isIdle ? 'py-20 text-center' : 'py-10'}>
        {isIdle && (
          <>
            <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-5">
              <Sprout className="h-7 w-7 text-primary" />
            </div>
            <h1 className="font-serif text-4xl md:text-5xl font-semibold text-foreground mb-3">
              Explore any plant
            </h1>
            <p className="text-muted-foreground max-w-xl mx-auto mb-8">
              Search the web, a botanical database, and PlantMind's synthesis to get a
              complete, trustworthy care profile in seconds.
            </p>
          </>
        )}

        <div className={`glass-card p-2 flex items-center gap-2 mx-auto transition-all duration-300 ${isIdle ? 'max-w-2xl' : 'max-w-2xl'}`}>
          <Search className="h-5 w-5 text-muted-foreground ml-2 shrink-0" />
          <Input
            ref={inputRef}
            placeholder="Search for a plant, e.g. Monstera Deliciosa..."
            value={plantName}
            onChange={(e) => setPlantName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && runLookup(plantName)}
            disabled={loading}
            className="border-none bg-transparent focus-visible:ring-0 h-11"
          />
          {plantName && !loading && (
            <button
              onClick={handleClear}
              aria-label="Clear search"
              className="p-1.5 rounded-full text-muted-foreground hover:text-foreground hover:bg-secondary transition-colors shrink-0"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          <Button
            onClick={() => runLookup(plantName)}
            disabled={loading || !plantName.trim()}
            className="bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl shrink-0 h-11"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Search'}
          </Button>
        </div>

        {isIdle && (
          <div className="mt-6 space-y-3 max-w-2xl mx-auto">
            {recentSearches.length > 0 && (
              <div className="flex flex-wrap items-center justify-center gap-2">
                <span className="text-xs text-muted-foreground flex items-center gap-1 mr-1">
                  <Clock className="h-3.5 w-3.5" /> Recent:
                </span>
                {recentSearches.map((name) => (
                  <button
                    key={name}
                    onClick={() => handleSearchClick(name)}
                    className="text-xs px-3 py-1.5 rounded-full border border-border bg-card hover:bg-secondary transition-colors"
                  >
                    {name}
                  </button>
                ))}
              </div>
            )}
            <div className="flex flex-wrap items-center justify-center gap-2">
              <span className="text-xs text-muted-foreground mr-1">Popular:</span>
              {POPULAR_SEARCHES.map((name) => (
                <button
                  key={name}
                  onClick={() => handleSearchClick(name)}
                  className="text-xs px-3 py-1.5 rounded-full bg-secondary/60 hover:bg-secondary transition-colors"
                >
                  {name}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Loading skeleton */}
      {loading && (
        <div className="space-y-6 pb-14">
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col md:flex-row gap-6">
                <Skeleton className="w-full md:w-48 h-48 rounded-lg shrink-0" />
                <div className="flex-1 space-y-3">
                  <Skeleton className="h-8 w-1/2" />
                  <Skeleton className="h-4 w-1/3" />
                  <Skeleton className="h-6 w-40" />
                  <Skeleton className="h-9 w-36" />
                </div>
              </div>
            </CardContent>
          </Card>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => <Skeleton key={i} className="h-28 rounded-lg" />)}
          </div>
        </div>
      )}

      {/* Not found state */}
      {!loading && notFound && (
        <div className="text-center py-16 pb-20">
          <div className="w-14 h-14 rounded-2xl bg-secondary flex items-center justify-center mx-auto mb-4">
            <SearchX className="h-7 w-7 text-muted-foreground" />
          </div>
          <h3 className="font-serif text-xl font-semibold mb-2">No results for "{plantName}"</h3>
          <p className="text-muted-foreground max-w-md mx-auto">
            Try a different name, or check the spelling - common names and scientific
            names both work.
          </p>
        </div>
      )}

      {/* Results */}
      {hasResult && (
        <div className="pb-14">
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
                    <div className="flex flex-wrap gap-2 mt-3">
                      <Badge className={CARE_LEVEL_STYLES[plantInfo.care_level] || 'bg-gray-500 hover:bg-gray-500'}>
                        {plantInfo.care_level || 'Unknown'} Care
                      </Badge>
                      {plantInfo.toxicity?.pets && plantInfo.toxicity.pets !== 'unknown' && (
                        <Badge
                          variant={plantInfo.toxicity.pets === 'toxic' ? 'destructive' : 'default'}
                          className="flex items-center gap-1"
                        >
                          {plantInfo.toxicity.pets === 'toxic' ? (
                            <ShieldAlert className="h-3 w-3" />
                          ) : (
                            <ShieldCheck className="h-3 w-3" />
                          )}
                          {plantInfo.toxicity.pets === 'toxic' ? 'Toxic to Pets' : 'Pet Safe'}
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
                    {plantInfo.watering && (
                      <div className="p-4 bg-blue-50 dark:bg-blue-950 rounded-lg">
                        <h3 className="font-semibold mb-2 flex items-center gap-2">
                          <Droplet className="h-4 w-4 text-blue-500" /> Watering
                        </h3>
                        <p className="text-sm mb-1"><strong>Frequency:</strong> {plantInfo.watering.frequency}</p>
                        {plantInfo.watering.amount && (
                          <p className="text-sm mb-1"><strong>Amount:</strong> {plantInfo.watering.amount}</p>
                        )}
                        <p className="text-sm text-muted-foreground">{plantInfo.watering.tips}</p>
                      </div>
                    )}

                    {plantInfo.sunlight && (
                      <div className="p-4 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
                        <h3 className="font-semibold mb-2 flex items-center gap-2">
                          <Sun className="h-4 w-4 text-yellow-500" /> Sunlight
                        </h3>
                        <p className="text-sm mb-1"><strong>Requirement:</strong> {plantInfo.sunlight.requirement}</p>
                        <p className="text-sm text-muted-foreground">{plantInfo.sunlight.details}</p>
                      </div>
                    )}

                    {plantInfo.fertilizing && (
                      <div className="p-4 bg-green-50 dark:bg-green-950 rounded-lg">
                        <h3 className="font-semibold mb-2 flex items-center gap-2">
                          <Leaf className="h-4 w-4 text-green-600" /> Fertilizing
                        </h3>
                        <p className="text-sm mb-1"><strong>Frequency:</strong> {plantInfo.fertilizing.frequency}</p>
                        <p className="text-sm"><strong>Type:</strong> {plantInfo.fertilizing.type}</p>
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="environment" className="space-y-4">
                    <div className="p-4 bg-orange-50 dark:bg-orange-950 rounded-lg">
                      <h3 className="font-semibold mb-2 flex items-center gap-2">
                        <Globe className="h-4 w-4 text-orange-500" /> Native Habitat
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {plantInfo.environment?.native_habitat || 'Not documented in available sources.'}
                      </p>
                    </div>

                    <div className="p-4 bg-cyan-50 dark:bg-cyan-950 rounded-lg">
                      <h3 className="font-semibold mb-2 flex items-center gap-2">
                        <Home className="h-4 w-4 text-cyan-600" /> Preferred Setting
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        {plantInfo.environment?.grows_indoors === true && 'Thrives as an indoor plant.'}
                        {plantInfo.environment?.grows_indoors === false && 'Best suited for outdoor growing.'}
                        {plantInfo.environment?.grows_indoors == null && 'See sunlight requirement above for the best spot in your home or garden.'}
                      </p>
                    </div>
                  </TabsContent>

                  <TabsContent value="issues" className="space-y-2">
                    {plantInfo.common_issues && plantInfo.common_issues.length > 0 ? (
                      <ul className="space-y-2">
                        {plantInfo.common_issues.map((issue: string, idx: number) => (
                          <li key={idx} className="flex items-start gap-2 p-3 bg-accent rounded-lg">
                            <AlertTriangle className="h-4 w-4 mt-0.5 shrink-0 text-amber-500" />
                            <span className="text-sm">{issue}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-muted-foreground text-center py-8">No common issues reported</p>
                    )}

                    {plantInfo.propagation && plantInfo.propagation.length > 0 && (
                      <div className="mt-6">
                        <h3 className="font-semibold mb-2 flex items-center gap-2">
                          <Leaf className="h-4 w-4 text-green-600" /> Propagation Methods
                        </h3>
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
                          <li key={idx} className="flex items-start gap-2 p-3 bg-accent rounded-lg">
                            <Lightbulb className="h-4 w-4 mt-0.5 shrink-0 text-amber-400" />
                            <span className="text-sm">{fact}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-muted-foreground text-center py-8">No interesting facts available</p>
                    )}

                    {plantInfo.sources && plantInfo.sources.length > 0 && (
                      <div className="mt-6">
                        <h3 className="font-semibold mb-2 flex items-center gap-2">
                          <ExternalLink className="h-4 w-4" /> Sources
                        </h3>
                        <ul className="space-y-1.5">
                          {plantInfo.sources.map((url: string, idx: number) => (
                            <li key={idx}>
                              <a
                                href={url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="flex items-center gap-1.5 text-sm text-primary hover:underline truncate"
                              >
                                <ExternalLink className="h-3.5 w-3.5 shrink-0" />
                                {hostname(url)}
                              </a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </TabsContent>
                </Tabs>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
