import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/hooks/useAuth';
import { Sparkles, Heart, Leaf } from 'lucide-react';

const Auth = () => {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();
  const { signInWithGoogle } = useAuth();

  const handleGoogleSignIn = async () => {
    setLoading(true);
    try {
      await signInWithGoogle();
      toast({
        title: "Welcome to Flourish! 🌱",
        description: "Your journey to better plant care starts now!",
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
    <div className="min-h-screen bg-gradient-to-br from-flourish-cream via-white to-flourish-sage/20 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-32 h-32 bg-flourish-green/10 rounded-full blur-xl animate-pulse-soft"></div>
        <div className="absolute bottom-20 right-10 w-40 h-40 bg-flourish-sage/15 rounded-full blur-xl animate-bounce-gentle"></div>
        <div className="absolute top-1/2 left-1/4 w-24 h-24 bg-flourish-dark/5 rounded-full blur-xl animate-pulse-soft"></div>
      </div>
      
      <Card className="w-full max-w-md bg-white/95 backdrop-blur-sm border-flourish-sage/30 shadow-2xl relative z-10">
        <CardHeader className="text-center space-y-6">
          {/* Logo */}
          <div className="mx-auto w-24 h-24 bg-gradient-to-br from-flourish-green to-flourish-dark rounded-3xl flex items-center justify-center mb-4 relative shadow-lg">
            <Leaf className="w-10 h-10 text-white animate-bounce-gentle" />
            <Sparkles className="w-4 h-4 text-flourish-cream absolute top-2 right-2 animate-pulse-soft" />
            <Heart className="w-4 h-4 text-flourish-cream/80 absolute bottom-2 left-2 animate-pulse-soft" />
          </div>
          
          {/* Title */}
          <div className="space-y-2">
            <CardTitle className="text-4xl font-bold text-flourish-forest">
              Flourish
            </CardTitle>
            <p className="text-flourish-dark font-medium text-lg">Your Plant Care Companion</p>
            <p className="text-flourish-green/80 text-sm font-medium">
              Nurture 🌱 Grow 🌿 Flourish 🌸
            </p>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Welcome message */}
          <div className="text-center space-y-2">
            <h3 className="text-flourish-forest font-semibold text-lg">Welcome to your garden! 🌺</h3>
            <p className="text-flourish-dark/70 text-sm leading-relaxed">
              Join thousands of plant parents who are nurturing healthier, happier plants with AI-powered care guidance.
            </p>
          </div>
          
          {/* Google Sign In */}
          <Button 
            onClick={handleGoogleSignIn}
            disabled={loading}
            className="w-full h-12 bg-gradient-to-r from-flourish-green to-flourish-dark hover:from-flourish-dark hover:to-flourish-forest text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
          >
            {loading ? (
              <div className="flex items-center space-x-2">
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                <span>Connecting...</span>
              </div>
            ) : (
              <div className="flex items-center space-x-3">
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span>Continue with Google</span>
              </div>
            )}
          </Button>
          
          {/* Features highlight */}
          <div className="grid grid-cols-3 gap-4 pt-4 border-t border-flourish-sage/20">
            <div className="text-center">
              <div className="w-8 h-8 bg-flourish-sage/20 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-sm">🤖</span>
              </div>
              <p className="text-xs text-flourish-dark/70 font-medium">AI Care Tips</p>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-flourish-green/20 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-sm">📱</span>
              </div>
              <p className="text-xs text-flourish-dark/70 font-medium">Smart Reminders</p>
            </div>
            <div className="text-center">
              <div className="w-8 h-8 bg-flourish-dark/20 rounded-full flex items-center justify-center mx-auto mb-2">
                <span className="text-sm">📊</span>
              </div>
              <p className="text-xs text-flourish-dark/70 font-medium">Growth Tracking</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Auth;