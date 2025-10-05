import React, { useState } from 'react';
import { Card, CardContent } from './ui/card';
import { Upload, CheckCircle2, FileText, Activity, AlertCircle, Download, BarChart3 } from 'lucide-react';

export default function KoiUpload() {
  // Component is disabled - no functionality needed

  return (
    <div className="w-full max-w-5xl mx-auto space-y-8" id="koi-upload">
      {/* Header Section */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-muted/20 mb-4">
          <Activity className="h-8 w-8 text-muted-foreground" />
        </div>
        <h2 className="text-3xl font-bold tracking-tight text-muted-foreground">KOI Light Curves Analysis</h2>
        <div className="inline-flex items-center gap-2 rounded-full bg-yellow-500/10 border border-yellow-500/20 px-4 py-2 mb-4">
          <AlertCircle className="h-4 w-4 text-yellow-500" />
          <span className="text-sm font-medium text-yellow-500">Coming Soon - Feature Under Development</span>
        </div>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Advanced KOI light curve analysis will be available soon. Our team is working on implementing this feature.
        </p>
      </div>

      {/* Disabled Features Preview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="border-muted/40 bg-muted/20 backdrop-blur-sm opacity-60">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <h4 className="font-semibold text-sm mb-1 text-muted-foreground">Future: File Formats</h4>
                <p className="text-xs text-muted-foreground">CSV, FITS, TXT, DAT</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-muted/40 bg-muted/20 backdrop-blur-sm opacity-60">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <Activity className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <h4 className="font-semibold text-sm mb-1 text-muted-foreground">Future: Light Curve Analysis</h4>
                <p className="text-xs text-muted-foreground">Time series flux measurements</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-muted/40 bg-muted/20 backdrop-blur-sm opacity-60">
          <CardContent className="p-4">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <h4 className="font-semibold text-sm mb-1 text-muted-foreground">Future: Auto Detection</h4>
                <p className="text-xs text-muted-foreground">Transit events & periodicity</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Disabled Upload Card */}
      <Card className="overflow-hidden border-0 shadow-lg bg-muted/20 backdrop-blur-sm opacity-60">
        <CardContent className="p-8">
          <div className="relative border-2 border-dashed border-muted rounded-2xl p-12 text-center">
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-5">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_1px_1px,_rgba(255,255,255,0.15)_1px,_transparent_0)] bg-[length:20px_20px]"></div>
            </div>
            
            <div className="relative">
              <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-muted text-muted-foreground">
                <AlertCircle className="h-8 w-8" />
              </div>
              
              <div className="space-y-3">
                <h3 className="text-xl font-semibold text-muted-foreground">
                  Feature Under Development
                </h3>
                <p className="text-muted-foreground max-w-md mx-auto">
                  KOI light curve analysis functionality is currently being implemented. This feature will support advanced time series analysis for exoplanet transit detection.
                </p>
              </div>
              
              <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
                <button 
                  disabled 
                  className="inline-flex items-center justify-center gap-2 rounded-lg border border-muted bg-muted/20 px-5 py-2.5 text-sm font-medium text-muted-foreground cursor-not-allowed"
                >
                  <Upload className="h-4 w-4" />
                  <span>Upload Disabled</span>
                </button>
              </div>
            </div>
          </div>

          {/* Development Info */}
          <div className="mt-6 p-4 rounded-lg border border-blue-500/20 bg-blue-500/5">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-blue-500 mt-0.5" />
              <div className="flex-1">
                <h4 className="font-semibold text-sm mb-2 text-blue-500">Development Status</h4>
                <p className="text-xs text-muted-foreground">
                  Our development team is actively working on implementing KOI light curve analysis capabilities. 
                  This will include transit detection algorithms, period analysis, and automated exoplanet candidate identification.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Alternative Action */}
      <div className="text-center">
        <p className="text-sm text-muted-foreground mb-4">
          In the meantime, use our KOI parameter analysis tool below for exoplanet classification
        </p>
        <button 
          onClick={() => document.getElementById('upload')?.scrollIntoView({ behavior: 'smooth' })}
          className="inline-flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors border border-primary/20 rounded-lg px-4 py-2 bg-primary/10 hover:bg-primary/20"
        >
          <BarChart3 className="h-4 w-4" />
          <span>Try KOI Parameter Analysis</span>
        </button>
      </div>
    </div>
  );
}
