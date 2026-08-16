import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Seo } from '@/components/Seo';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/hooks/useAuth';
import { Sparkles, CalendarCheck, MessagesSquare } from 'lucide-react';

const highlights = [
  { icon: Sparkles, label: 'AI-guided care' },
  { icon: CalendarCheck, label: 'Adaptive schedules' },
  { icon: MessagesSquare, label: 'Ask PlantMind anything' },
];

const Auth = () => {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const { signInWithGoogle } = useAuth();

  const handleGoogleSignIn = async () => {
    setLoading(true);
    try {
      await signInWithGoogle();
      toast({
        title: "Welcome to Flourish",
        description: "Your journey to better plant care starts now.",
      });
    } catch (error) {
      toast({
        title: "Sign in failed",
        description: "Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Seo title="Sign In" description="Sign in to Flourish to start tracking and caring for your garden." />
      <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 rounded-3xl overflow-hidden shadow-xl border border-border">
        {/* Brand panel */}
        <div className="hidden md:flex flex-col justify-between bg-primary text-primary-foreground p-10">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 bg-primary rounded-lg flex items-center justify-center shrink-0 p-1">
              <img src="/logo_transparent.png" alt="Flourish" className="w-full h-full object-contain" />
            </div>
            <span className="text-2xl font-serif font-semibold">Flourish</span>
          </div>

          <div className="space-y-6">
            <p className="font-serif text-3xl leading-snug">
              Transform your black thumb into a green one.
            </p>
            <p className="text-primary-foreground/70 text-sm leading-relaxed">
              An AI garden agent that monitors, predicts, and adapts — so your plants
              get exactly the care they need, before they ever ask for it.
            </p>
          </div>

          <div className="space-y-3">
            {highlights.map(({ icon: Icon, label }) => (
              <div key={label} className="flex items-center gap-3 text-sm">
                <div className="w-8 h-8 rounded-full bg-primary-foreground/10 flex items-center justify-center shrink-0">
                  <Icon size={15} />
                </div>
                <span className="text-primary-foreground/85">{label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Sign-in panel */}
        <div className="bg-card p-10 flex flex-col justify-center">
          <div className="md:hidden flex items-center gap-2.5 mb-8">
            <div className="w-9 h-9 bg-white rounded-lg flex items-center justify-center shrink-0 p-1 border border-border">
              <img src="/logo_transparent.png" alt="Flourish" className="w-full h-full object-contain" />
            </div>
            <span className="text-2xl font-serif font-semibold text-primary">Flourish</span>
          </div>

          <p className="text-xs font-semibold tracking-widest text-muted-foreground uppercase mb-2">
            Welcome back
          </p>
          <h1 className="font-serif text-3xl text-foreground mb-2">
            Sign in to your garden
          </h1>
          <p className="text-sm text-muted-foreground mb-8">
            Continue with Google to pick up right where you left off.
          </p>

          <Button
            onClick={handleGoogleSignIn}
            disabled={loading}
            className="w-full h-12 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold rounded-xl shadow-sm transition-all"
          >
            {loading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                <span>Connecting...</span>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <svg className="w-4 h-4" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span>Continue with Google</span>
              </div>
            )}
          </Button>

          <p className="text-xs text-muted-foreground text-center mt-6">
            By continuing you agree to Flourish's Terms of Service and Privacy Policy.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Auth;
