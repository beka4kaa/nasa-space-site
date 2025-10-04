import React from 'react';
import { Rocket, Sparkles } from 'lucide-react';

const Header = () => {
  const scrollToUpload = () => {
    const uploadSection = document.getElementById('upload');
    if (uploadSection) {
      uploadSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/10 bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 max-w-7xl items-center justify-between px-4">
        {/* Logo */}
        <div className="flex items-center space-x-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary">
            <Rocket className="h-4 w-4 text-primary-foreground" />
          </div>
          <span className="hidden font-semibold text-foreground sm:inline-block">
            NASA Explorer
          </span>
        </div>

        {/* Get Started Button - Desktop & Mobile */}
        <button
          onClick={scrollToUpload}
          className="group relative inline-flex items-center justify-center gap-2 overflow-hidden rounded-lg border border-primary/20 bg-primary/10 px-5 py-2 text-sm font-medium text-foreground backdrop-blur-sm transition-all duration-300 hover:border-primary/40 hover:bg-primary/20 active:scale-98"
        >
          {/* Subtle gradient overlay on hover */}
          <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 via-purple-500/5 to-blue-500/0 opacity-0 transition-opacity duration-500 group-hover:opacity-100"></div>
          
          {/* Button content */}
          <span className="relative flex items-center gap-2">
            <Rocket className="h-4 w-4 text-primary transition-transform duration-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
            <span className="font-semibold">Get Started</span>
          </span>
        </button>
      </div>
    </header>
  );
};

export default Header;
