import React, { useRef, useState } from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCard3DProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  badge?: {
    text: string;
    type: 'success' | 'warning' | 'danger' | 'info';
  };
  accentColor?: 'indigo' | 'emerald' | 'amber' | 'rose' | 'cyan';
}

export const MetricCard3D: React.FC<MetricCard3DProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badge,
  accentColor = 'indigo',
}) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);
  const [glarePos, setGlarePos] = useState({ x: 50, y: 50 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotX = ((y - centerY) / centerY) * -12; // tilt angle
    const rotY = ((x - centerX) / centerX) * 12;

    setRotateX(rotX);
    setRotateY(rotY);
    setGlarePos({
      x: (x / rect.width) * 100,
      y: (y / rect.height) * 100,
    });
  };

  const handleMouseLeave = () => {
    setRotateX(0);
    setRotateY(0);
    setIsHovered(false);
  };

  const badgeStyles = {
    success: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30 shadow-emerald-500/20',
    warning: 'bg-amber-500/15 text-amber-300 border-amber-500/30 shadow-amber-500/20',
    danger: 'bg-rose-500/15 text-rose-300 border-rose-500/30 shadow-rose-500/20',
    info: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30 shadow-indigo-500/20',
  };

  const accentStyles = {
    indigo: 'from-indigo-600/20 via-slate-900/40 to-slate-950 border-indigo-500/30 text-indigo-400 group-hover:border-indigo-400/60 shadow-indigo-500/10',
    emerald: 'from-emerald-600/20 via-slate-900/40 to-slate-950 border-emerald-500/30 text-emerald-400 group-hover:border-emerald-400/60 shadow-emerald-500/10',
    amber: 'from-amber-600/20 via-slate-900/40 to-slate-950 border-amber-500/30 text-amber-400 group-hover:border-amber-400/60 shadow-amber-500/10',
    rose: 'from-rose-600/20 via-slate-900/40 to-slate-950 border-rose-500/30 text-rose-400 group-hover:border-rose-400/60 shadow-rose-500/10',
    cyan: 'from-cyan-600/20 via-slate-900/40 to-slate-950 border-cyan-500/30 text-cyan-400 group-hover:border-cyan-400/60 shadow-cyan-500/10',
  };

  return (
    <div
      style={{ perspective: 1000 }}
      className="group cursor-pointer"
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={handleMouseLeave}
    >
      <div
        ref={cardRef}
        style={{
          transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(${isHovered ? 1.02 : 1}, ${isHovered ? 1.02 : 1}, 1)`,
          transformStyle: 'preserve-3d',
          transition: isHovered ? 'transform 0.08s ease-out' : 'transform 0.5s ease-out',
        }}
        className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${accentStyles[accentColor]} border p-5 backdrop-blur-xl shadow-xl transition-all duration-300`}
      >
        {/* Dynamic Specular Glare Overlay */}
        {isHovered && (
          <div
            style={{
              background: `radial-gradient(circle at ${glarePos.x}% ${glarePos.y}%, rgba(255,255,255,0.18) 0%, rgba(255,255,255,0) 65%)`,
            }}
            className="pointer-events-none absolute inset-0 z-20 transition-opacity duration-200"
          />
        )}

        {/* 3D Depth Card Content */}
        <div style={{ transform: 'translateZ(30px)' }} className="relative z-10">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              {title}
            </span>
            <div className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700/60 shadow-inner text-white group-hover:scale-110 transition-transform">
              <Icon className="w-5 h-5 text-indigo-400 group-hover:text-white transition-colors" />
            </div>
          </div>

          <div className="mt-3 flex items-baseline justify-between">
            <div className="text-3xl font-extrabold tracking-tight text-white font-mono drop-shadow-sm">
              {value}
            </div>
            {badge && (
              <span className={`text-[11px] px-2.5 py-0.5 rounded-full font-medium border shadow-xs ${badgeStyles[badge.type]}`}>
                {badge.text}
              </span>
            )}
          </div>

          {subtitle && (
            <p className="mt-2 text-xs text-slate-400 flex items-center space-x-1">
              <span>{subtitle}</span>
            </p>
          )}
        </div>

        {/* Subtle Metallic Corner Edge Highlight */}
        <div className="absolute top-0 right-0 w-16 h-16 bg-white/5 rounded-bl-3xl pointer-events-none" />
      </div>
    </div>
  );
};
