import { useEffect, useRef, useState, type ReactNode } from 'react';
import {
  Search, Loader2, Plus, Droplet, Sun, Leaf, Globe, Home, AlertTriangle, Lightbulb,
  ExternalLink, ShieldCheck, ShieldAlert, X, Sprout, SearchX, Clock, Thermometer,
  Ruler, TrendingUp, Flower2, Scissors, Bug, BookOpen, CheckCircle2, Sparkles, ArrowRight,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { lookupPlant, createAutonomousPlant } from '@/integrations/api';
import { useToast } from '@/hooks/use-toast';

const POPULAR_SEARCHES = ['Monstera', 'Pothos', 'Snake Plant', 'Peace Lily', 'Fiddle Leaf Fig', 'Succulent'];
const RECENT_SEARCHES_KEY = 'flourish-explore-recent-searches';
const MAX_RECENT = 6;

const CARE_LEVEL_STYLES: Record<string, string> = {
  easy: 'bg-emerald-600/10 text-emerald-700 dark:text-emerald-400 border-emerald-600/30',
  moderate: 'bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/30',
  difficult: 'bg-red-600/10 text-red-700 dark:text-red-400 border-red-600/30',
};

const TAXON_ORDER = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus'] as const;

const hostname = (url: string) => {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
};

const present = (v: unknown): v is string => typeof v === 'string' && v.trim() !== '' && v.toLowerCase() !== 'null';

/* ---------- small building blocks ---------- */

function Stat({ icon, label, value }: { icon: ReactNode; label: string; value?: string | null }) {
  if (!present(value)) return null;
  return (
    <div className="rounded-xl border border-border bg-card/60 p-4">
      <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {icon}
        {label}
      </div>
      <p className="mt-1.5 text-sm font-semibold text-foreground leading-snug">{value}</p>
    </div>
  );
}

function Section({ icon, title, badge, children }: { icon: ReactNode; title: string; badge?: ReactNode; children: ReactNode }) {
  return (
    <section className="rounded-xl border border-border bg-card/60 p-5">
      <h3 className="mb-3 flex items-center gap-2 text-sm font-semibold text-foreground">
        <span className="text-primary">{icon}</span>
        {title}
        {badge}
      </h3>
      {children}
    </section>
  );
}

function Facts({ rows }: { rows: [string, string | null | undefined][] }) {
  const visible = rows.filter(([, v]) => present(v));
  if (visible.length === 0) return null;
  return (
    <dl className="divide-y divide-border">
      {visible.map(([label, value]) => (
        <div key={label} className="grid grid-cols-1 gap-1 py-2.5 first:pt-0 last:pb-0 sm:grid-cols-[10rem_1fr] sm:gap-4">
          <dt className="text-sm text-muted-foreground">{label}</dt>
          <dd className="text-sm text-foreground">{value}</dd>
        </div>
      ))}
    </dl>
  );
}

const AiNote = () => (
  <Badge variant="outline" className="ml-1 text-[10px] font-normal">AI-estimated</Badge>
);

const Empty = ({ children }: { children: ReactNode }) => (
  <p className="rounded-xl border border-dashed border-border py-10 text-center text-sm text-muted-foreground">{children}</p>
);

/* ---------- page ---------- */

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
      window.scrollTo({ top: 0, behavior: 'smooth' });
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

  const info = plantInfo || {};
  const profile = info.profile || {};
  const growing = profile.growing || {};
  const upkeep = profile.upkeep || {};
  const wiki = info.wikipedia || null;
  const aiFilled: string[] = info.ai_filled_fields || [];
  const heroImage = info.image_url || wiki?.thumbnail;
  const overview = profile.overview || wiki?.extract;
  const taxonomy = TAXON_ORDER.filter((r) => info.classification?.[r]).map((r) => [r, info.classification[r]] as const);
  const waterStat = (info.care_schedule || []).find((c: any) => c.task === 'water')?.label || info.watering?.frequency;
  const petsStat =
    info.toxicity?.pets === 'toxic' ? 'Toxic to pets' : info.toxicity?.pets === 'safe' ? 'Pet safe' : null;
  const hasProfile = Object.keys(profile).length > 0;
  const pests: { name: string; signs: string; treatment: string }[] = profile.pests_diseases || [];

  return (
    <div className="container mx-auto px-4 max-w-5xl">
      {/* Search header - centered hero when idle, compact once a search has run */}
      <div className={isIdle ? 'py-20 text-center' : 'py-8'}>
        {isIdle && (
          <>
            <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-5">
              <Sprout className="h-7 w-7 text-primary" />
            </div>
            <h1 className="font-serif text-4xl md:text-5xl font-semibold text-foreground mb-3">
              Plant Explorer
            </h1>
            <p className="text-muted-foreground max-w-xl mx-auto mb-8">
              A complete, source-backed profile for any plant: care, growing conditions,
              toxicity, taxonomy, pests and more, compiled from live web search, botanical
              databases and PlantMind.
            </p>
          </>
        )}

        <div className="glass-card p-2 flex items-center gap-2 mx-auto max-w-2xl">
          <Search className="h-5 w-5 text-muted-foreground ml-2 shrink-0" />
          <Input
            ref={inputRef}
            placeholder="Search a plant by common or scientific name…"
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
        <div className="space-y-6 pb-14" aria-busy="true" aria-label="Researching plant">
          <p className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            Searching the web, botanical databases and care guides…
          </p>
          <div className="rounded-2xl border border-border p-6 flex flex-col md:flex-row gap-6">
            <Skeleton className="w-full md:w-60 h-60 rounded-xl shrink-0" />
            <div className="flex-1 space-y-3">
              <Skeleton className="h-9 w-1/2" />
              <Skeleton className="h-4 w-1/3" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
              <Skeleton className="h-10 w-40 mt-4" />
            </div>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-20 rounded-xl" />)}
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
            Try a different name, or check the spelling. Common and scientific names both work.
          </p>
        </div>
      )}

      {/* Results */}
      {hasResult && (
        <article className="pb-16 space-y-6">
          {/* Identity header */}
          <header className="rounded-2xl border border-border bg-card p-5 md:p-7 shadow-sm">
            <div className="flex flex-col md:flex-row gap-6">
              {heroImage ? (
                <img
                  src={heroImage}
                  alt={info.common_name}
                  className="w-full md:w-60 h-60 object-cover rounded-xl shrink-0 bg-secondary"
                />
              ) : (
                <div className="w-full md:w-60 h-60 rounded-xl shrink-0 bg-secondary flex items-center justify-center">
                  <Sprout className="h-12 w-12 text-muted-foreground/50" />
                </div>
              )}

              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h2 className="font-serif text-3xl font-semibold text-foreground">{info.common_name}</h2>
                    {info.scientific_name && (
                      <p className="text-muted-foreground italic mt-0.5">{info.scientific_name}</p>
                    )}
                  </div>
                  <Button onClick={handleAddToInventory} disabled={adding} className="shrink-0">
                    {adding ? (
                      <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Adding…</>
                    ) : (
                      <><Plus className="h-4 w-4 mr-2" />Add to My Plants</>
                    )}
                  </Button>
                </div>

                <div className="flex flex-wrap gap-2 mt-4">
                  <Badge variant="outline" className={`capitalize ${CARE_LEVEL_STYLES[info.care_level] || ''}`}>
                    {info.care_level || 'Unknown'} care
                  </Badge>
                  {petsStat && (
                    <Badge variant={info.toxicity.pets === 'toxic' ? 'destructive' : 'outline'} className="gap-1">
                      {info.toxicity.pets === 'toxic' ? <ShieldAlert className="h-3 w-3" /> : <ShieldCheck className="h-3 w-3 text-emerald-600" />}
                      {petsStat}
                    </Badge>
                  )}
                  {info.species_verified && (
                    <Badge variant="outline" className="gap-1">
                      <CheckCircle2 className="h-3 w-3 text-emerald-600" /> Species verified
                    </Badge>
                  )}
                  {info.family && <Badge variant="secondary">{info.family}</Badge>}
                </div>

                {overview && (
                  <p className="mt-4 text-sm leading-relaxed text-muted-foreground line-clamp-6">{overview}</p>
                )}
                {wiki?.url && (
                  <a
                    href={wiki.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 inline-flex items-center gap-1 text-xs text-primary hover:underline"
                  >
                    <BookOpen className="h-3 w-3" /> Read more on Wikipedia
                  </a>
                )}
                {info.also_known_as && (
                  <p className="mt-2 text-xs text-muted-foreground">Formerly classified as <em>{info.also_known_as}</em></p>
                )}
              </div>
            </div>

            {/* At-a-glance */}
            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
              <Stat icon={<Droplet className="h-3.5 w-3.5 text-blue-500" />} label="Water" value={waterStat} />
              <Stat icon={<Sun className="h-3.5 w-3.5 text-amber-500" />} label="Light" value={info.sunlight?.requirement} />
              <Stat icon={<Thermometer className="h-3.5 w-3.5 text-rose-500" />} label="Temperature" value={growing.temperature} />
              <Stat icon={<Ruler className="h-3.5 w-3.5 text-violet-500" />} label="Mature size" value={growing.mature_size} />
            </div>
          </header>

          {/* Detail tabs */}
          <Tabs defaultValue="care" className="w-full">
            <TabsList className="w-full h-auto justify-start overflow-x-auto">
              <TabsTrigger value="care">Care guide</TabsTrigger>
              <TabsTrigger value="growing">Growing</TabsTrigger>
              <TabsTrigger value="problems">Pests &amp; problems</TabsTrigger>
              <TabsTrigger value="about">About</TabsTrigger>
              <TabsTrigger value="sources">Sources</TabsTrigger>
            </TabsList>

            {/* CARE */}
            <TabsContent value="care" className="mt-4 space-y-4">
              {info.quick_start?.length > 0 && (
                <Section icon={<Sprout className="h-4 w-4" />} title="Your first week">
                  <ol className="space-y-2">
                    {info.quick_start.map((step: string, idx: number) => (
                      <li key={idx} className="flex gap-3 text-sm">
                        <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary/10 text-[11px] font-semibold text-primary">{idx + 1}</span>
                        <span>{step}</span>
                      </li>
                    ))}
                  </ol>
                </Section>
              )}

              <div className="grid gap-4 md:grid-cols-2">
                {info.watering && (
                  <Section icon={<Droplet className="h-4 w-4" />} title="Watering" badge={aiFilled.includes('watering') ? <AiNote /> : null}>
                    <Facts rows={[['Frequency', info.watering.frequency], ['Amount', info.watering.amount], ['Tips', info.watering.tips]]} />
                  </Section>
                )}
                {info.sunlight && (
                  <Section icon={<Sun className="h-4 w-4" />} title="Sunlight" badge={aiFilled.includes('sunlight') ? <AiNote /> : null}>
                    <Facts rows={[['Requirement', info.sunlight.requirement], ['Placement', info.sunlight.details]]} />
                  </Section>
                )}
                {info.fertilizing && (
                  <Section icon={<Leaf className="h-4 w-4" />} title="Fertilizing" badge={aiFilled.includes('fertilizing') ? <AiNote /> : null}>
                    <Facts rows={[['Frequency', info.fertilizing.frequency], ['Type', info.fertilizing.type]]} />
                  </Section>
                )}
                {info.toxicity && (
                  <Section
                    icon={info.toxicity.pets === 'toxic' ? <ShieldAlert className="h-4 w-4 text-red-600" /> : <ShieldCheck className="h-4 w-4" />}
                    title="Pet safety"
                  >
                    <p className="text-sm">{info.toxicity.details}</p>
                    {info.toxicity.source_url && (
                      <a href={info.toxicity.source_url} target="_blank" rel="noopener noreferrer" className="mt-2 inline-flex items-center gap-1 text-xs text-primary hover:underline">
                        <ExternalLink className="h-3 w-3" /> ASPCA source
                      </a>
                    )}
                  </Section>
                )}
              </div>

              {(upkeep.seasonal_care?.spring_summer || upkeep.seasonal_care?.autumn_winter) && (
                <Section icon={<Sparkles className="h-4 w-4" />} title="Seasonal care">
                  <Facts rows={[['Spring & summer', upkeep.seasonal_care.spring_summer], ['Autumn & winter', upkeep.seasonal_care.autumn_winter]]} />
                </Section>
              )}
            </TabsContent>

            {/* GROWING */}
            <TabsContent value="growing" className="mt-4 space-y-4">
              <Section icon={<Thermometer className="h-4 w-4" />} title="Growing conditions">
                {hasProfile && Object.values(growing).some(present) ? (
                  <Facts
                    rows={[
                      ['Temperature', growing.temperature],
                      ['Humidity', growing.humidity],
                      ['Soil', growing.soil],
                      ['Mature size', growing.mature_size],
                      ['Growth rate', growing.growth_rate],
                      ['Hardiness zones', growing.hardiness_zones],
                      ['Blooms', growing.bloom],
                    ]}
                  />
                ) : (
                  <p className="text-sm text-muted-foreground">No growing-condition data found for this plant.</p>
                )}
              </Section>

              <div className="grid gap-4 md:grid-cols-2">
                <Section icon={<Globe className="h-4 w-4" />} title="Native habitat">
                  <p className="text-sm text-muted-foreground">
                    {info.environment?.native_habitat || 'Not documented in available sources.'}
                  </p>
                </Section>
                <Section icon={<Home className="h-4 w-4" />} title="Best setting">
                  <p className="text-sm text-muted-foreground">
                    {info.environment?.grows_indoors === true && 'Thrives as an indoor plant.'}
                    {info.environment?.grows_indoors === false && 'Best suited to outdoor growing.'}
                    {info.environment?.grows_indoors == null && 'See the sunlight requirement for the best spot in your home or garden.'}
                  </p>
                </Section>
              </div>

              {(present(upkeep.pruning) || present(upkeep.repotting)) && (
                <Section icon={<Scissors className="h-4 w-4" />} title="Pruning & repotting">
                  <Facts rows={[['Pruning', upkeep.pruning], ['Repotting', upkeep.repotting]]} />
                </Section>
              )}

              {info.propagation?.length > 0 && (
                <Section icon={<TrendingUp className="h-4 w-4" />} title="Propagation">
                  <div className="flex flex-wrap gap-2">
                    {info.propagation.map((m: string, idx: number) => (
                      <Badge key={idx} variant="outline" className="font-normal">{m}</Badge>
                    ))}
                  </div>
                </Section>
              )}
            </TabsContent>

            {/* PROBLEMS */}
            <TabsContent value="problems" className="mt-4 space-y-4">
              {pests.length > 0 && (
                <Section icon={<Bug className="h-4 w-4" />} title="Common pests & diseases">
                  <div className="space-y-3">
                    {pests.map((p, idx) => (
                      <div key={idx} className="rounded-lg border border-border p-3 text-sm">
                        <p className="font-medium">{p.name}</p>
                        <p className="mt-1 text-muted-foreground"><span className="text-foreground">Signs:</span> {p.signs}</p>
                        <p className="text-muted-foreground"><span className="text-foreground">Treatment:</span> {p.treatment}</p>
                      </div>
                    ))}
                  </div>
                </Section>
              )}

              {info.warning_signs?.length > 0 && (
                <Section icon={<AlertTriangle className="h-4 w-4 text-amber-500" />} title="If you see…">
                  <div className="space-y-3">
                    {info.warning_signs.map((w: { symptom: string; cause: string; fix: string }, idx: number) => (
                      <div key={idx} className="rounded-lg border border-border p-3 text-sm">
                        <p className="font-medium">{w.symptom}</p>
                        <p className="mt-1 text-muted-foreground">Likely cause: {w.cause}</p>
                        <p><span className="font-medium">Fix:</span> {w.fix}</p>
                      </div>
                    ))}
                  </div>
                </Section>
              )}

              {info.common_issues?.length > 0 && (
                <Section icon={<AlertTriangle className="h-4 w-4" />} title="Other common issues">
                  <ul className="space-y-2">
                    {info.common_issues.map((issue: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2 text-sm">
                        <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-500" />
                        {issue}
                      </li>
                    ))}
                  </ul>
                </Section>
              )}

              {!pests.length && !info.warning_signs?.length && !info.common_issues?.length && (
                <Empty>No common problems reported for this plant.</Empty>
              )}
            </TabsContent>

            {/* ABOUT */}
            <TabsContent value="about" className="mt-4 space-y-4">
              {taxonomy.length > 0 && (
                <Section icon={<Flower2 className="h-4 w-4" />} title="Taxonomy">
                  <ol className="flex flex-wrap items-center gap-x-2 gap-y-2 text-sm">
                    {taxonomy.map(([rank, name], i) => (
                      <li key={rank} className="flex items-center gap-2">
                        <span>
                          <span className="block text-[10px] uppercase tracking-wide text-muted-foreground">{rank}</span>
                          <span className="font-medium">{name}</span>
                        </span>
                        {i < taxonomy.length - 1 && <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />}
                      </li>
                    ))}
                  </ol>
                </Section>
              )}

              {wiki?.extract && (
                <Section icon={<BookOpen className="h-4 w-4" />} title={wiki.title ? `${wiki.title} — Wikipedia` : 'Wikipedia'}>
                  {wiki.description && <p className="mb-2 text-xs italic text-muted-foreground">{wiki.description}</p>}
                  <p className="text-sm leading-relaxed text-muted-foreground">{wiki.extract}</p>
                </Section>
              )}

              {profile.uses?.length > 0 && (
                <Section icon={<Lightbulb className="h-4 w-4" />} title="Uses">
                  <div className="flex flex-wrap gap-2">
                    {profile.uses.map((u: string, idx: number) => <Badge key={idx} variant="secondary" className="font-normal">{u}</Badge>)}
                  </div>
                </Section>
              )}

              {info.interesting_facts?.length > 0 && (
                <Section icon={<Lightbulb className="h-4 w-4" />} title="Good to know">
                  <ul className="space-y-2">
                    {info.interesting_facts.map((fact: string, idx: number) => (
                      <li key={idx} className="flex items-start gap-2 text-sm">
                        <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                        {fact}
                      </li>
                    ))}
                  </ul>
                </Section>
              )}

              {profile.similar_plants?.length > 0 && (
                <Section icon={<Leaf className="h-4 w-4" />} title="Similar plants">
                  <div className="flex flex-wrap gap-2">
                    {profile.similar_plants.map((name: string) => (
                      <button
                        key={name}
                        onClick={() => handleSearchClick(name)}
                        className="rounded-full border border-border bg-card px-3 py-1.5 text-xs transition-colors hover:bg-secondary"
                      >
                        {name}
                      </button>
                    ))}
                  </div>
                </Section>
              )}
            </TabsContent>

            {/* SOURCES */}
            <TabsContent value="sources" className="mt-4 space-y-4">
              <Section icon={<ExternalLink className="h-4 w-4" />} title="Where this information comes from">
                <ul className="space-y-2">
                  {info.species_verified?.url && (
                    <li><a href={info.species_verified.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-primary hover:underline"><CheckCircle2 className="h-3.5 w-3.5 shrink-0" />GBIF — species identity &amp; taxonomy</a></li>
                  )}
                  {info.toxicity?.source_url && (
                    <li><a href={info.toxicity.source_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-primary hover:underline"><CheckCircle2 className="h-3.5 w-3.5 shrink-0" />ASPCA — pet toxicity</a></li>
                  )}
                  {wiki?.url && (
                    <li><a href={wiki.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-sm text-primary hover:underline"><BookOpen className="h-3.5 w-3.5 shrink-0" />Wikipedia — overview</a></li>
                  )}
                  {(info.sources || []).filter((u: string) => u !== wiki?.url).map((url: string, idx: number) => (
                    <li key={idx}>
                      <a href={url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 truncate text-sm text-primary hover:underline">
                        <ExternalLink className="h-3.5 w-3.5 shrink-0" />
                        {hostname(url)}
                      </a>
                    </li>
                  ))}
                </ul>
              </Section>
              <p className="text-xs text-muted-foreground">
                Care details are compiled from the sources above and summarised by PlantMind. Fields marked
                "AI-estimated" were not found in a source. Always check the pet-safety source before
                bringing a plant home if you have animals.
              </p>
            </TabsContent>
          </Tabs>
        </article>
      )}
    </div>
  );
}
