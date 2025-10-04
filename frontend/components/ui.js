import * as React from 'react';

// Icon components
const X = ({ className, ...props }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
);

const AlertTriangle = ({ className, ...props }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" {...props}>
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
    <line x1="12" y1="9" x2="12" y2="13"></line>
    <line x1="12" y1="17" x2="12.01" y2="17"></line>
  </svg>
);

const Card = ({ children, className = "" }) => (
  <div className={`glass-card rounded-xl p-6 ${className}`}>
    {children}
  </div>
);

const Button = ({ children, variant = "primary", size = "md", disabled = false, className = "", ...props }) => {
  const baseClasses = "inline-flex items-center justify-center font-medium transition-all duration-200 rounded-lg";
  
  const variants = {
    primary: "bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl disabled:bg-slate-600",
    secondary: "bg-slate-700 hover:bg-slate-600 text-slate-100 border border-slate-600",
    outline: "border-2 border-dashed border-blue-500 hover:border-blue-400 text-blue-400 hover:bg-blue-500/10"
  };
  
  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2.5 text-sm",
    lg: "px-6 py-3 text-base"
  };
  
  return (
    <button
      className={`${baseClasses} ${variants[variant]} ${sizes[size]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

const Alert = ({ children, variant = "error" }) => {
  const variants = {
    error: "bg-red-900/50 border-red-500/50 text-red-200",
    success: "bg-green-900/50 border-green-500/50 text-green-200",
    warning: "bg-yellow-900/50 border-yellow-500/50 text-yellow-200"
  };
  
  return (
    <div className={`flex items-center space-x-2 p-4 rounded-lg border ${variants[variant]}`}>
      <AlertCircle className="w-5 h-5 flex-shrink-0" />
      <div className="text-sm">{children}</div>
    </div>
  );
};

const Badge = ({ children, variant = "default" }) => {
  const variants = {
    default: "bg-slate-700 text-slate-200",
    primary: "bg-blue-600 text-white",
    success: "bg-green-600 text-white"
  };
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]}`}>
      {children}
    </span>
  );
};

export { Card, Button, Alert, Badge };