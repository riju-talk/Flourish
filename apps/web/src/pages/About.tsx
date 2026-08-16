import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Seo } from "@/components/Seo";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Seo title="About" description="About Flourish and the person behind it." />
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-14 max-w-3xl space-y-8">
        <header>
          <p className="text-xs font-semibold tracking-widest text-muted-foreground uppercase mb-3">
            About
          </p>
          <h1 className="font-serif text-4xl md:text-5xl font-semibold text-foreground mb-4">
            About Me
          </h1>
        </header>

        <section className="glass-card p-8 space-y-4">
          {/* Edit the paragraphs below with your own bio/content. */}
          <p className="text-muted-foreground leading-relaxed">
            Hi, I'm [Your Name]. I built Flourish.
          </p>
          <p className="text-muted-foreground leading-relaxed">
            [A sentence or two about who you are - your background, what you do, or why you're into this.]
          </p>
          <p className="text-muted-foreground leading-relaxed">
            [Why you built Flourish / what problem it solves for you.]
          </p>
          <p className="text-muted-foreground leading-relaxed">
            [Anything else you want visitors to know - links, contact info, etc.]
          </p>
        </section>
      </main>
      <Footer />
    </div>
  );
}
