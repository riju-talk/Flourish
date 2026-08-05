export const Footer = () => {
  const year = new Date().getFullYear();

  return (
    <footer className="bg-flourish-forest text-flourish-cream mt-16">
      <div className="container mx-auto px-4 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-4">
          <div className="flex items-center gap-2">
            <img src="/logo_transparent.png" alt="Flourish" className="w-[18px] h-[18px] object-contain" />
            <span className="font-serif text-lg font-semibold">Flourish</span>
          </div>
          <span className="text-sm text-flourish-cream/50">
            © {year} Flourish Botanical. All rights reserved.
          </span>
        </div>

        <div className="flex items-center gap-6 text-sm text-flourish-cream/70">
          <a href="#" className="hover:text-flourish-cream transition-colors duration-500 ease-out">
            Privacy Policy
          </a>
          <a href="#" className="hover:text-flourish-cream transition-colors duration-500 ease-out">
            Terms of Service
          </a>
          <a href="#" className="hover:text-flourish-cream transition-colors duration-500 ease-out">
            Sustainability Report
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
