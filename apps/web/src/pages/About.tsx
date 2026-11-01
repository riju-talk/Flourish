import { Github, Linkedin, Mail, MapPin, Sprout } from "lucide-react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Seo } from "@/components/Seo";
import { Badge } from "@/components/ui/badge";

/* Profile content mirrors https://rijusmit.vercel.app/ */

const PROFILE = {
  name: "Rijusmit Biswas",
  title: "Software and Machine Learning Engineer",
  tagline: "I turn research into software people can rely on.",
  location: "New Delhi, India",
  bio: "I build software end to end and maintain it after launch: the frontend, API, database and servers, plus machine learning when a problem calls for it.",
  email: "rijusmit.biswas@gmail.com",
  github: "https://github.com/riju-talk",
  linkedin: "https://www.linkedin.com/in/rijusmit-biswas",
  portfolio: "https://rijusmit.vercel.app/",
};

const STATS = [
  { value: "12+", label: "Live deployments" },
  { value: "2", label: "First-author papers" },
  { value: "150+", label: "LeetCode problems" },
  { value: "1403", label: "Codeforces rating" },
  { value: "13", label: "Models evaluated" },
];

const EXPERIENCE = [
  {
    role: "Head of Product Development",
    org: "Student Council, IIIT Delhi",
    when: "2025 – present",
    points: [
      "Built a student services portal used by 500+ students (React, Node.js, Express, PostgreSQL).",
      "Own the database, indexing and API; set up CI with automated tests; review code for a team of eight.",
      "Replaced manual data entry with validated forms, cutting admin work by about 60% and reducing bad records.",
    ],
  },
  {
    role: "Software Engineering Intern",
    org: "Shipzee",
    when: "Mar 2026 – Aug 2026",
    points: [
      "Shipped full-stack features on a live courier aggregation product.",
      "Led a stack migration planned to avoid outages.",
      "Debugged cross-service production failures and wrote integration tests that caught contract mismatches.",
    ],
  },
  {
    role: "AI Engineer & Undergraduate Researcher",
    org: "MIDAS Lab, IIIT Delhi",
    when: "May 2025 – Jan 2026",
    points: [
      "Built an evaluation tool for scoring model output alignment; its checks cut made-up answers by about 20%.",
      "Ran reproducible pipelines over three datasets with retry and rate-limit handling.",
      "Trained models with LoRA and QLoRA at 4-bit precision.",
      "First author on a paper under review at AAAI 2027; the harness and benchmarks are open source.",
    ],
  },
  {
    role: "Machine Learning Research Intern",
    org: "Computational Social Science Lab, IIIT Delhi",
    when: "Jan 2025 – May 2025",
    points: [
      "Built a satellite imagery pipeline on Google Earth Engine for district-scale crop data.",
      "Compared CNN backbones for phenology, crop classification and yield estimation.",
      "Measured data drift across 10+ districts using difference-in-differences and fixed-effects models.",
    ],
  },
  {
    role: "Data Science Intern",
    org: "Complex Systems Lab, IIIT Delhi",
    when: "Aug 2024 – Dec 2024",
    points: [
      "Led a team of five on a 25-class classifier for messy real-world data (84.5% and 74.5% on two splits).",
      "Built real-time web visualisations using open food, recipe, carbon and nutrition datasets.",
      "Ran code reviews and mentored junior members.",
    ],
  },
  {
    role: "Open Source Contributor",
    org: "Meshery (Layer5)",
    when: "2025",
    points: ["Contributed bug reports, feature requests, documentation fixes and pull requests; took part in code reviews."],
  },
];

const PROJECTS = [
  { name: "Executive Career Agent", desc: "Local-first desktop app with seven cooperating agents for job search, including an anti-fabrication validator.", tech: ["React", "TypeScript", "Electron", "Node.js", "MCP", "LangChain", "Docker"] },
  { name: "TURBO", desc: "Reimplementation of a 2025 arXiv paper fusing Vision Transformer and BART features, scored with BLEU, ROUGE and METEOR.", tech: ["PyTorch", "ViT", "BART", "Hugging Face"] },
  { name: "SICKLE++", desc: "Tests how pretrained satellite crop models transfer across regions, comparing three architectures against a mean baseline.", tech: ["PyTorch", "ConvLSTM", "U-TAE", "UNet3D", "Google Earth Engine"] },
  { name: "ResonantBERT", desc: "Two-stage system that ranks news articles by newsworthiness using a ModernBERT encoder with LoRA.", tech: ["PyTorch", "ModernBERT", "LoRA", "Hugging Face", "scikit-learn"] },
  { name: "SpanBERT-CRF", desc: "From-scratch SpanBERT encoder with a linear-chain CRF for SQuAD v2.0 QA and CoNLL-2003 NER.", tech: ["PyTorch", "SpanBERT", "LoRA", "Hugging Face"] },
  { name: "MineMEETS", desc: "Pipelines turning images, text and audio into embeddings behind one interface.", tech: ["CLIP", "Whisper", "Pinecone", "Docker", "Pytest"] },
  { name: "Cross-Portfolio Default Risk Prediction", desc: "Credit default study on 30K credit card and 5K loan records; ROC-AUC of 0.7769 (cards) and 0.7467 (loans).", tech: ["Python", "XGBoost", "LightGBM", "SHAP", "scikit-learn", "Optuna"] },
  { name: "ShipCast", desc: "Forecasts daily shipment volume for 27 Brazilian states; LightGBM beats a seasonal-naive baseline and an LSTM at most horizons.", tech: ["LightGBM", "PyTorch", "Pandas"] },
  { name: "DreamDOT", desc: "GraphQL microservices backend for a creator platform with subscriptions and pay-per-view.", tech: ["GraphQL", "Node.js", "MongoDB", "Docker"] },
  { name: "Hostiggo", desc: "Production SaaS taken from idea to product on AWS, with CI and monitoring.", tech: ["Node.js", "React", "PostgreSQL", "AWS", "Docker"] },
];

const SKILLS: [string, string[]][] = [
  ["Languages", ["Python", "TypeScript", "JavaScript", "C++", "SQL", "C"]],
  ["Backend & APIs", ["Node.js", "Express", "FastAPI", "REST", "GraphQL (federation)", "WebSockets", "Retries & rate limiting"]],
  ["Frontend", ["React", "Next.js", "Tailwind CSS", "Dashboards", "Live WebSocket interfaces"]],
  ["Infrastructure & delivery", ["AWS", "Docker", "GitHub Actions", "Linux", "Vercel", "Pytest", "Structured logging", "Static analysis"]],
  ["Data & distributed systems", ["PostgreSQL", "MongoDB", "Prisma", "Pinecone", "Schema design", "Indexing", "PySpark", "Airflow", "ETL"]],
  ["ML & research", ["PyTorch", "Hugging Face", "LoRA / QLoRA", "LangChain", "RAG", "CLIP & Whisper", "Google Earth Engine"]],
];

const PUBLICATIONS = [
  { venue: "AAAI 2027, AI Alignment Track", status: "Under review", desc: "Cross-evaluation protocol for alignment interference, and constrained RL post-training for LLM safety and factuality." },
  { venue: "ACL ARR 2026 October", status: "Under review", desc: "Editorial-value news ranking using a factor-grounded transformer." },
];

const OPEN_TO = ["SDE", "SDE Intern", "MLE", "MLE Intern", "Data Scientist", "DS Intern", "Data Engineer", "Data Engineering Intern"];

const SectionTitle = ({ children }: { children: string }) => (
  <h2 className="font-serif text-2xl font-semibold text-foreground mb-5">{children}</h2>
);

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Seo title="About" description={`About Flourish and ${PROFILE.name}, the engineer who built it.`} />
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-14 max-w-4xl space-y-14">
        {/* About Flourish */}
        <section className="glass-card p-6 md:p-8 flex gap-4 items-start">
          <div className="bg-primary/10 p-3 rounded-xl shrink-0">
            <Sprout className="h-6 w-6 text-primary" />
          </div>
          <div>
            <p className="text-xs font-semibold tracking-widest text-muted-foreground uppercase mb-2">About Flourish</p>
            <p className="text-muted-foreground leading-relaxed">
              Flourish is a plant care companion: track your garden, get a daily care checklist and
              calendar, ask PlantMind (an AI assistant grounded in your own plants and live data), and
              explore source-backed profiles for any species. It is built with React, FastAPI, Firebase
              and Groq.
            </p>
          </div>
        </section>

        {/* Profile */}
        <header>
          <p className="text-xs font-semibold tracking-widest text-muted-foreground uppercase mb-3">The developer</p>
          <h1 className="font-serif text-4xl md:text-5xl font-semibold text-foreground">{PROFILE.name}</h1>
          <p className="mt-2 text-lg text-primary font-medium">{PROFILE.title}</p>
          <p className="mt-4 font-serif text-xl italic text-foreground/80">“{PROFILE.tagline}”</p>
          <p className="mt-4 text-muted-foreground leading-relaxed max-w-2xl">{PROFILE.bio}</p>

          <div className="mt-5 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-muted-foreground">
            <span className="flex items-center gap-1.5"><MapPin className="h-4 w-4" />{PROFILE.location}</span>
            <a href={`mailto:${PROFILE.email}`} className="flex items-center gap-1.5 hover:text-foreground transition-colors"><Mail className="h-4 w-4" />{PROFILE.email}</a>
            <a href={PROFILE.github} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 hover:text-foreground transition-colors"><Github className="h-4 w-4" />GitHub</a>
            <a href={PROFILE.linkedin} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 hover:text-foreground transition-colors"><Linkedin className="h-4 w-4" />LinkedIn</a>
            <a href={PROFILE.portfolio} target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors underline underline-offset-4">Portfolio</a>
          </div>
        </header>

        {/* Stats */}
        <section aria-label="Highlights" className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {STATS.map((s) => (
            <div key={s.label} className="rounded-xl border border-border bg-card/60 p-4 text-center">
              <p className="font-serif text-3xl font-semibold text-foreground">{s.value}</p>
              <p className="mt-1 text-xs text-muted-foreground">{s.label}</p>
            </div>
          ))}
        </section>

        {/* Experience */}
        <section>
          <SectionTitle>Experience</SectionTitle>
          <ol className="space-y-6 border-l border-border pl-6">
            {EXPERIENCE.map((e) => (
              <li key={`${e.org}-${e.role}`} className="relative">
                <span className="absolute -left-[1.85rem] top-1.5 h-2.5 w-2.5 rounded-full bg-primary ring-4 ring-background" />
                <div className="flex flex-wrap items-baseline justify-between gap-x-4">
                  <h3 className="font-semibold text-foreground">{e.role}</h3>
                  <span className="text-xs text-muted-foreground">{e.when}</span>
                </div>
                <p className="text-sm text-primary">{e.org}</p>
                <ul className="mt-2 space-y-1.5">
                  {e.points.map((p) => (
                    <li key={p} className="flex gap-2 text-sm text-muted-foreground leading-relaxed">
                      <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-muted-foreground/60" />
                      {p}
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ol>
        </section>

        {/* Projects */}
        <section>
          <SectionTitle>Projects</SectionTitle>
          <div className="grid gap-4 md:grid-cols-2">
            {PROJECTS.map((p) => (
              <article key={p.name} className="rounded-xl border border-border bg-card/60 p-5 flex flex-col">
                <h3 className="font-semibold text-foreground">{p.name}</h3>
                <p className="mt-1.5 text-sm text-muted-foreground leading-relaxed flex-1">{p.desc}</p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {p.tech.map((t) => <Badge key={t} variant="secondary" className="font-normal text-[11px]">{t}</Badge>)}
                </div>
              </article>
            ))}
          </div>
          <p className="mt-4 text-sm text-muted-foreground">
            More projects on the <a href={PROFILE.portfolio} target="_blank" rel="noopener noreferrer" className="text-primary underline underline-offset-4">portfolio</a>.
          </p>
        </section>

        {/* Skills */}
        <section>
          <SectionTitle>Skills</SectionTitle>
          <dl className="space-y-4">
            {SKILLS.map(([group, items]) => (
              <div key={group} className="grid gap-2 sm:grid-cols-[13rem_1fr] sm:gap-4">
                <dt className="text-sm font-medium text-foreground">{group}</dt>
                <dd className="flex flex-wrap gap-1.5">
                  {items.map((i) => <Badge key={i} variant="outline" className="font-normal">{i}</Badge>)}
                </dd>
              </div>
            ))}
          </dl>
        </section>

        {/* Publications */}
        <section>
          <SectionTitle>Publications</SectionTitle>
          <ul className="space-y-3">
            {PUBLICATIONS.map((p) => (
              <li key={p.venue} className="rounded-xl border border-border bg-card/60 p-5">
                <div className="flex flex-wrap items-center gap-2">
                  <h3 className="font-semibold text-foreground">{p.venue}</h3>
                  <Badge variant="outline" className="text-[11px] font-normal">{p.status}</Badge>
                </div>
                <p className="mt-1.5 text-sm text-muted-foreground">{p.desc}</p>
              </li>
            ))}
          </ul>
        </section>

        {/* Open to */}
        <section className="glass-card p-6 md:p-8">
          <SectionTitle>Open to</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {OPEN_TO.map((r) => <Badge key={r} className="font-normal">{r}</Badge>)}
          </div>
          <p className="mt-4 text-sm text-muted-foreground">
            Get in touch at <a href={`mailto:${PROFILE.email}`} className="text-primary underline underline-offset-4">{PROFILE.email}</a>.
          </p>
        </section>
      </main>
      <Footer />
    </div>
  );
}
