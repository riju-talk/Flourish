import { Link } from "react-router-dom";
import { Github } from "lucide-react";

const GITHUB_URL = "https://github.com/riju-talk/Flourish";

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
            © {year} Flourish. All rights reserved.
          </span>
        </div>

        <nav aria-label="Footer" className="flex items-center gap-6 text-sm text-flourish-cream/70">
          <Link to="/about" className="hover:text-flourish-cream transition-colors duration-500 ease-out">
            About
          </Link>
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 hover:text-flourish-cream transition-colors duration-500 ease-out"
          >
            <Github className="h-4 w-4" />
            GitHub
          </a>
        </nav>
      </div>
    </footer>
  );
};

export default Footer;
