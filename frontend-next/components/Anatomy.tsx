"use client";

/**
 * Original vector anatomy artwork.
 *
 * These are hand-authored SVGs rather than stock photography: they stay crisp at
 * any size, carry no licensing burden, and can be tinted per case.
 */

export function RespiratoryFigure({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 260 300" className={className} preserveAspectRatio="xMidYMid meet" role="img" aria-label="Respiratory anatomy illustration">
      <defs>
        <linearGradient id="lungLeft" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#F3D9E4" />
          <stop offset="52%" stopColor="#E4D4F2" />
          <stop offset="100%" stopColor="#CFE4F4" />
        </linearGradient>
        <linearGradient id="lungRight" x1="1" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#F3D9E4" />
          <stop offset="52%" stopColor="#DFE9F6" />
          <stop offset="100%" stopColor="#D6EFE6" />
        </linearGradient>
        <linearGradient id="airway" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#E8EDF5" />
          <stop offset="100%" stopColor="#C9D5E6" />
        </linearGradient>
        <filter id="lungShadow" x="-30%" y="-20%" width="160%" height="150%">
          <feDropShadow dx="0" dy="8" stdDeviation="9" floodColor="#0F172A" floodOpacity="0.10" />
        </filter>
      </defs>

      {/* trachea */}
      <rect x="120" y="18" width="20" height="54" rx="10" fill="url(#airway)" />
      {[0, 1, 2, 3, 4].map((i) => (
        <line
          key={i}
          x1="121.5"
          y1={28 + i * 10}
          x2="138.5"
          y2={28 + i * 10}
          stroke="#A9B8CC"
          strokeWidth="1.6"
          strokeLinecap="round"
          opacity="0.65"
        />
      ))}

      {/* main bronchi */}
      <path d="M130 70 C 112 78, 100 88, 92 100" stroke="#B7C6D9" strokeWidth="9" fill="none" strokeLinecap="round" />
      <path d="M130 70 C 148 78, 160 88, 168 100" stroke="#B7C6D9" strokeWidth="9" fill="none" strokeLinecap="round" />

      {/* lungs */}
      <g filter="url(#lungShadow)">
        <path
          d="M113 80 C 88 86, 62 106, 50 142 C 40 176, 42 220, 55 252
             C 64 274, 84 288, 99 282 C 112 277, 118 256, 118 232
             L 118 100 C 118 88, 118 82, 113 80 Z"
          fill="url(#lungLeft)"
        />
        <path
          d="M147 80 C 172 86, 198 106, 210 142 C 220 176, 218 220, 205 252
             C 196 274, 176 288, 161 282 C 148 277, 142 256, 142 232
             L 142 100 C 142 88, 142 82, 147 80 Z"
          fill="url(#lungRight)"
        />
      </g>

      {/* fissures */}
      <path d="M56 186 C 76 176, 100 174, 118 178" stroke="#FFFFFF" strokeWidth="2.4" fill="none" opacity="0.75" />
      <path d="M62 226 C 82 218, 102 216, 118 220" stroke="#FFFFFF" strokeWidth="2.2" fill="none" opacity="0.6" />
      <path d="M204 186 C 184 176, 160 174, 142 178" stroke="#FFFFFF" strokeWidth="2.4" fill="none" opacity="0.75" />
      <path d="M198 226 C 178 218, 158 216, 142 220" stroke="#FFFFFF" strokeWidth="2.2" fill="none" opacity="0.6" />

      {/* bronchial tree */}
      <g stroke="#9FB0C6" strokeWidth="2.6" fill="none" strokeLinecap="round" opacity="0.8">
        <path d="M92 100 C 88 120, 82 136, 76 152" />
        <path d="M90 118 C 78 126, 70 134, 64 142" />
        <path d="M84 140 C 74 148, 68 158, 62 166" />
        <path d="M80 168 C 72 178, 68 190, 64 202" />
        <path d="M168 100 C 172 120, 178 136, 184 152" />
        <path d="M170 118 C 182 126, 190 134, 196 142" />
        <path d="M176 140 C 186 148, 192 158, 198 166" />
        <path d="M180 168 C 188 178, 192 190, 196 202" />
      </g>
      <g fill="#9FB0C6" opacity="0.85">
        <circle cx="64" cy="142" r="3" />
        <circle cx="62" cy="166" r="2.6" />
        <circle cx="64" cy="202" r="2.4" />
        <circle cx="196" cy="142" r="3" />
        <circle cx="198" cy="166" r="2.6" />
        <circle cx="196" cy="202" r="2.4" />
      </g>

      {/* diaphragm */}
      <path
        d="M52 268 C 78 292, 106 296, 130 288 C 154 296, 182 292, 208 268"
        stroke="#B9C6D8"
        strokeWidth="7"
        fill="none"
        strokeLinecap="round"
        opacity="0.7"
      />
    </svg>
  );
}

export function CirculationFigure({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 260 300" className={className} preserveAspectRatio="xMidYMid meet" role="img" aria-label="Circulation anatomy illustration">
      <defs>
        <linearGradient id="heartGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#F6C7D2" />
          <stop offset="55%" stopColor="#E4B9D8" />
          <stop offset="100%" stopColor="#C9C4EF" />
        </linearGradient>
        <linearGradient id="vessel" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="#F0B6C4" />
          <stop offset="100%" stopColor="#B9A9E8" />
        </linearGradient>
        <filter id="heartShadow" x="-30%" y="-20%" width="160%" height="150%">
          <feDropShadow dx="0" dy="7" stdDeviation="8" floodColor="#0F172A" floodOpacity="0.10" />
        </filter>
      </defs>

      {/* aorta arch */}
      <path
        d="M132 44 C 132 22, 190 22, 190 60 C 190 92, 168 110, 152 126"
        stroke="url(#vessel)"
        strokeWidth="15"
        fill="none"
        strokeLinecap="round"
      />
      {/* vena cava */}
      <path d="M104 40 C 104 90, 108 130, 118 166" stroke="#CBD9E8" strokeWidth="13" fill="none" strokeLinecap="round" />
      {/* pulmonary trunk */}
      <path d="M150 120 C 176 118, 194 132, 202 156" stroke="url(#vessel)" strokeWidth="11" fill="none" strokeLinecap="round" />

      <g filter="url(#heartShadow)">
        <path
          d="M130 250 C 92 216, 78 178, 88 146 C 96 120, 124 116, 138 140
             C 152 116, 182 122, 190 148 C 199 180, 182 218, 130 250 Z"
          fill="url(#heartGrad)"
        />
      </g>

      {/* chamber separation */}
      <path d="M138 140 C 130 168, 132 208, 130 246" stroke="#FFFFFF" strokeWidth="2.6" fill="none" opacity="0.7" />
      <path d="M120 156 C 140 172, 158 172, 176 158" stroke="#FFFFFF" strokeWidth="2.2" fill="none" opacity="0.55" />

      {/* coronary hint */}
      <path d="M150 128 C 158 150, 158 176, 150 202" stroke="#C4899F" strokeWidth="2.4" fill="none" opacity="0.6" />

      {/* ECG trace */}
      <path
        d="M24 232 L58 232 L68 210 L78 254 L88 232 L236 232"
        stroke="#8B7CF6"
        strokeWidth="2.4"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity="0.75"
      />
    </svg>
  );
}

export function NeuroFigure({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 260 300" className={className} preserveAspectRatio="xMidYMid meet" role="img" aria-label="Neurological anatomy illustration">
      <defs>
        <linearGradient id="brainGrad" x1="0" y1="0" x2="0.6" y2="1">
          <stop offset="0%" stopColor="#E3D9F7" />
          <stop offset="55%" stopColor="#D6D9F2" />
          <stop offset="100%" stopColor="#D3E8F4" />
        </linearGradient>
        <filter id="brainShadow" x="-30%" y="-20%" width="160%" height="150%">
          <feDropShadow dx="0" dy="8" stdDeviation="9" floodColor="#0F172A" floodOpacity="0.10" />
        </filter>
      </defs>

      <g filter="url(#brainShadow)">
        <path
          d="M130 44 C 96 44, 70 66, 68 100 C 50 112, 50 142, 66 154
             C 66 186, 96 206, 130 200 C 164 206, 194 186, 194 154
             C 210 142, 210 112, 192 100 C 190 66, 164 44, 130 44 Z"
          fill="url(#brainGrad)"
        />
      </g>

      <g stroke="#FFFFFF" strokeWidth="2.2" fill="none" opacity="0.75" strokeLinecap="round">
        <path d="M130 52 C 118 74, 118 96, 130 116 C 142 96, 142 74, 130 52" />
        <path d="M130 116 C 112 118, 98 132, 96 152" />
        <path d="M130 116 C 148 118, 162 132, 164 152" />
        <path d="M130 116 C 130 140, 130 164, 130 190" />
        <path d="M96 152 C 82 162, 76 176, 78 190" />
        <path d="M164 152 C 178 162, 184 176, 182 190" />
      </g>

      {/* brainstem + cord */}
      <path d="M130 200 C 130 226, 128 246, 126 268" stroke="#C3D2E4" strokeWidth="15" fill="none" strokeLinecap="round" />
      <path d="M126 268 C 126 276, 122 284, 120 292" stroke="#C3D2E4" strokeWidth="9" fill="none" strokeLinecap="round" />

      {/* focus marker */}
      <circle cx="96" cy="152" r="5" fill="#E4737F" opacity="0.9" />
      <circle cx="96" cy="152" r="11" fill="none" stroke="#E4737F" strokeWidth="1.6" opacity="0.45" />
    </svg>
  );
}

export function SystemicFigure({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 260 300" className={className} preserveAspectRatio="xMidYMid meet" role="img" aria-label="Systemic physiology illustration">
      <defs>
        <linearGradient id="cellGrad" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#FBDDD2" />
          <stop offset="55%" stopColor="#F6D6E8" />
          <stop offset="100%" stopColor="#D9D6F6" />
        </linearGradient>
        <filter id="cellShadow" x="-30%" y="-30%" width="160%" height="160%">
          <feDropShadow dx="0" dy="6" stdDeviation="8" floodColor="#0F172A" floodOpacity="0.09" />
        </filter>
      </defs>

      {/* large cell */}
      <g filter="url(#cellShadow)">
        <path
          d="M132 60 C 186 60, 214 100, 208 148 C 202 196, 164 224, 118 214
             C 72 204, 44 168, 50 122 C 56 78, 90 60, 132 60 Z"
          fill="url(#cellGrad)"
        />
      </g>

      {/* membrane */}
      <path
        d="M132 74 C 176 74, 198 106, 194 146 C 190 184, 158 206, 122 198
           C 86 190, 62 160, 66 124 C 70 88, 98 74, 132 74 Z"
        fill="none"
        stroke="#FFFFFF"
        strokeWidth="2.4"
        opacity="0.7"
      />

      {/* nucleus */}
      <circle cx="132" cy="140" r="34" fill="#C9BCEA" opacity="0.85" />
      <circle cx="132" cy="140" r="34" fill="none" stroke="#FFFFFF" strokeWidth="2" opacity="0.6" />
      <circle cx="122" cy="132" r="9" fill="#FFFFFF" opacity="0.45" />

      {/* pathogens */}
      <g fill="#E4737F" opacity="0.9">
        <circle cx="62" cy="252" r="9" />
        <circle cx="96" cy="270" r="6" />
        <circle cx="176" cy="256" r="8" />
        <circle cx="206" cy="274" r="5" />
      </g>
      <g stroke="#E4737F" strokeWidth="2" opacity="0.5" strokeLinecap="round">
        <path d="M54 246 L 44 238" />
        <path d="M70 247 L 80 239" />
        <path d="M168 250 L 158 242" />
      </g>
      <g fill="#8B7CF6" opacity="0.85">
        <circle cx="200" cy="238" r="7" />
        <circle cx="34" cy="266" r="5" />
      </g>

      {/* cytokine drift */}
      <g fill="#4FBFA8" opacity="0.65">
        <circle cx="46" cy="72" r="5" />
        <circle cx="212" cy="86" r="4" />
        <circle cx="24" cy="132" r="3.5" />
        <circle cx="234" cy="168" r="4.5" />
      </g>
    </svg>
  );
}

/** Picks the figure that matches the dominant system in the case text. */
export function figureForText(text: string): "respiratory" | "circulation" | "neuro" | "systemic" {
  const t = text.toLowerCase();
  const score = (words: string[]) => words.reduce((n, w) => (t.includes(w) ? n + 1 : n), 0);

  const resp = score(["cough", "sputum", "breath", "crackles", "pleuritic", "spO2".toLowerCase(), "wheeze", "hypoxia"]);
  const circ = score(["chest pain", "ecg", "st elevation", "troponin", "palpitation", "heart rate", "angina", "infarct"]);
  const neuro = score(["stroke", "facial droop", "slurred", "weakness", "nihss", "seizure", "confusion", "paralysis"]);
  const sys = score(["sepsis", "fever", "lactate", "wbc", "infection", "shock", "organ dysfunction"]);

  const best = Math.max(resp, circ, neuro, sys);
  if (best === 0) return "systemic";
  if (best === resp) return "respiratory";
  if (best === circ) return "circulation";
  if (best === neuro) return "neuro";
  return "systemic";
}

export function AnatomyFigure({ kind, className = "" }: { kind: string; className?: string }) {
  if (kind === "respiratory") return <RespiratoryFigure className={className} />;
  if (kind === "circulation") return <CirculationFigure className={className} />;
  if (kind === "neuro") return <NeuroFigure className={className} />;
  return <SystemicFigure className={className} />;
}