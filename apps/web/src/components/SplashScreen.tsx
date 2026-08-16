export const SplashScreen = () => (
  <div className="min-h-screen bg-background flex items-center justify-center">
    <div className="text-center">
      <div className="w-20 h-20 bg-white rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-2xl">
        <img src="/logo_transparent.png" alt="Flourish" className="w-12 h-12 object-contain" />
      </div>
      <p className="text-primary font-bold text-xl tracking-tight">Flourishing...</p>
    </div>
  </div>
);

export default SplashScreen;
