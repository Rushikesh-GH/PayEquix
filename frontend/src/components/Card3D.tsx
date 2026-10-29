import React, { useRef, useState } from 'react';

interface Card3DProps {
  children: React.ReactNode;
  className?: string;
  glowColor?: 'indigo' | 'emerald' | 'amber' | 'rose' | 'purple' | 'cyan' | 'slate';
  tiltStrength?: number;
  depth?: number;
  onClick?: () => void;
}

export const Card3D: React.FC<Card3DProps> = ({
  children,
  className = '',
  glowColor = 'indigo',
  tiltStrength = 10,
  depth = 20,
  onClick,
}) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);
  const [glarePos, setGlarePos] = useState({ x: 50, y: 50, opacity: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const glowStyles = {
    indigo: 'hover:shadow-[0_20px_45px_-12px_rgba(99,102,241,0.25)] hover:border-indigo-300/80',
    emerald: 'hover:shadow-[0_20px_45px_-12px_rgba(16,185,129,0.25)] hover:border-emerald-300/80',
    amber: 'hover:shadow-[0_20px_45px_-12px_rgba(245,158,11,0.25)] hover:border-amber-300/80',
    rose: 'hover:shadow-[0_20px_45px_-12px_rgba(244,63,94,0.25)] hover:border-rose-300/80',
    purple: 'hover:shadow-[0_20px_45px_-12px_rgba(168,85,247,0.25)] hover:border-purple-300/80',
    cyan: 'hover:shadow-[0_20px_45px_-12px_rgba(6,182,212,0.25)] hover:border-cyan-300/80',
    slate: 'hover:shadow-[0_20px_45px_-12px_rgba(100,116,139,0.25)] hover:border-slate-300',
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotX = ((y - centerY) / centerY) * -tiltStrength;
    const rotY = ((x - centerX) / centerX) * tiltStrength;

    setRotateX(rotX);
    setRotateY(rotY);

    setGlarePos({
      x: (x / rect.width) * 100,
      y: (y / rect.height) * 100,
      opacity: 0.22,
    });
  };

  const handleMouseEnter = () => {
    setIsHovered(true);
  };

  const handleMouseLeave = () => {
    setIsHovered(false);
    setRotateX(0);
    setRotateY(0);
    setGlarePos((prev) => ({ ...prev, opacity: 0 }));
  };

  return (
    <div
      style={{ perspective: '1100px' }}
      className={`relative transition-all duration-300 ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
    >
      <div
        ref={cardRef}
        onMouseMove={handleMouseMove}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        style={{
          transform: `rotateX(${rotateX}deg) rotateY(${rotateY}deg) ${
            isHovered ? `scale3d(1.015, 1.015, 1.015) translateZ(${depth}px)` : 'scale3d(1, 1, 1)'
          }`,
          transformStyle: 'preserve-3d',
          transition: isHovered
            ? 'transform 0.08s ease-out, box-shadow 0.25s ease-out'
            : 'transform 0.45s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.4s ease',
        }}
        className={`relative rounded-2xl bg-white/90 backdrop-blur-md border border-slate-200/90 shadow-sm transition-colors overflow-hidden flex flex-col ${
          glowStyles[glowColor]
        } ${className}`}
      >
        {/* Dynamic Specular Glare Reflection */}
        <div
          className="pointer-events-none absolute inset-0 z-20 rounded-2xl transition-opacity duration-300"
          style={{
            background: `radial-gradient(circle 280px at ${glarePos.x}% ${glarePos.y}%, rgba(255,255,255,0.7), transparent 70%)`,
            opacity: glarePos.opacity,
          }}
        />

        {/* Card Content Container */}
        <div style={{ transform: isHovered ? `translateZ(${depth / 2}px)` : 'none' }} className="relative z-10 flex-1 flex flex-col justify-between">
          {children}
        </div>
      </div>
    </div>
  );
};
