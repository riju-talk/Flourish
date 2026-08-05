import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/hooks/useAuth';
import { Leaf, Loader2 } from 'lucide-react';

const Onboarding = () => {
  const { completeOnboarding } = useAuth();
  const { toast } = useToast();
  const [fullName, setFullName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fullName.trim() || !phoneNumber.trim()) return;

    setLoading(true);
    try {
      await completeOnboarding(fullName.trim(), phoneNumber.trim());
      toast({
        title: "You're all set! 🌱",
        description: "Welcome to your garden.",
      });
    } catch (error: any) {
      toast({
        title: "Couldn't save your details",
        description: error.response?.data?.detail || 'Please try again.',
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-mesh flex items-center justify-center p-4">
      <Card className="glass-card w-full max-w-md shadow-xl">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 vibrant-gradient rounded-3xl flex items-center justify-center shadow-lg animate-float">
            <Leaf className="w-8 h-8 text-white" />
          </div>
          <div className="space-y-1">
            <CardTitle className="text-3xl font-extrabold tracking-tight">Let's get you growing</CardTitle>
            <CardDescription>Tell us a bit about yourself.</CardDescription>
          </div>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="fullName">Full name</Label>
              <Input
                id="fullName"
                type="text"
                placeholder="Alex Rivera"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phoneNumber">Phone number</Label>
              <Input
                id="phoneNumber"
                type="tel"
                placeholder="+1 555 123 4567"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
                required
                disabled={loading}
              />
            </div>

            <Button
              type="submit"
              disabled={loading || !fullName.trim() || !phoneNumber.trim()}
              className="w-full h-12 vibrant-gradient text-white font-semibold rounded-full shadow-md hover:shadow-glow transition-all"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="h-5 w-5 animate-spin" /> Starting your garden...
                </span>
              ) : (
                "Start My Garden"
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

export default Onboarding;
