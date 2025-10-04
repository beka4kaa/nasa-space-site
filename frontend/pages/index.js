import * as React from 'react';
import Head from 'next/head';
import Header from '../components/Header';
import CsvUpload from '../components/CsvUpload';
import KoiUpload from '../components/KoiUpload';
import Galaxy from '../components/Galaxy';
import { ThemeProvider, useTheme } from '../hooks/useTheme';
import { Rocket, BarChart3, Telescope, Microscope } from 'lucide-react';

function HomeContent() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Header />
      
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 sm:py-32">
        {/* Background Elements */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-primary/5 via-background to-background"></div>
        <div className="absolute inset-0 pointer-events-none">
          <Galaxy 
            transparent={true}
            density={0.8}
            hueShift={180}
            glowIntensity={0.4}
            starSpeed={0.3}
            speed={0.5}
            mouseInteraction={false}
            mouseRepulsion={false}
            twinkleIntensity={0.4}
            rotationSpeed={0.02}
            saturation={0.3}
          />
        </div>
          
          <div className="relative container mx-auto px-4">
            <div className="flex flex-col items-center text-center space-y-8 max-w-4xl mx-auto">
              <div className="space-y-4">
                <div className="inline-flex items-center rounded-full border px-4 py-1.5 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80">
                  <Rocket className="w-4 h-4 mr-2" />
                  NASA Hackathon 2025
                </div>
                
                <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl/none bg-gradient-to-r from-foreground via-foreground/90 to-foreground/60 bg-clip-text text-transparent">
                  Discover the
                  <span className="block bg-gradient-to-r from-primary via-primary/90 to-primary/60 bg-clip-text text-transparent">
                    Cosmic Unknown
                  </span>
                </h1>
                
                <p className="mx-auto max-w-3xl text-lg sm:text-xl text-muted-foreground leading-relaxed">
                  Advanced astronomical data analysis platform powered by NASA's Kepler mission data. 
                  Upload, analyze, and visualize exoplanet discoveries with cutting-edge tools designed 
                  for the next generation of space exploration.
                </p>
              </div>
              
              {/* Features Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl mt-12">
                <div className="group relative overflow-hidden rounded-xl border bg-card/50 backdrop-blur-sm p-6 hover:bg-card/80 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <BarChart3 className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="font-semibold">Data Analysis</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Advanced algorithms to process and analyze astronomical datasets
                  </p>
                </div>
                
                <div className="group relative overflow-hidden rounded-xl border bg-card/50 backdrop-blur-sm p-6 hover:bg-card/80 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Telescope className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="font-semibold">Visualization</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Interactive charts and graphs to explore cosmic phenomena
                  </p>
                </div>
                
                <div className="group relative overflow-hidden rounded-xl border bg-card/50 backdrop-blur-sm p-6 hover:bg-card/80 transition-all duration-300">
                  <div className="flex items-center space-x-3 mb-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                      <Microscope className="w-5 h-5 text-primary" />
                    </div>
                    <h3 className="font-semibold">Discovery</h3>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Identify patterns and anomalies in exoplanet research data
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
        
        {/* KOI Light Curves Section */}
        <section className="py-16 bg-muted/30">
          <div className="container mx-auto px-4 max-w-6xl">
            <KoiUpload />
          </div>
        </section>
        
        {/* General Data Upload Section */}
        <section className="py-16">
          <div className="container mx-auto px-4 max-w-6xl">
            <CsvUpload />
          </div>
        </section>
        
      {/* Footer */}
      <footer className="border-t bg-muted/30">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-sm text-muted-foreground">
            <p>Built for NASA Hackathon 2025 • Powered by Kepler Mission Data</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function Home() {
  return (
    <ThemeProvider>
      <Head>
        <title>NASA Explorer - Discover the Cosmos</title>
        <meta name="description" content="Advanced astronomical data analysis platform for NASA Hackathon" />
        <meta name="viewport" content="initial-scale=1, width=device-width" />
      </Head>
      <HomeContent />
    </ThemeProvider>
  );
}
