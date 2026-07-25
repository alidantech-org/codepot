export function HeroDecoration() {
  return (
    <svg
      aria-hidden="true"
      className="pointer-events-none absolute -right-28 top-1/2 hidden h-[620px] w-[620px] -translate-y-1/2 lg:block xl:-right-12"
      viewBox="0 0 620 620"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <radialGradient id="heroGlow" cx="0" cy="0" r="1" gradientTransform="translate(350 344) rotate(90) scale(214)">
          <stop stopColor="var(--primary-light)" stopOpacity="0.32" />
          <stop offset="1" stopColor="var(--primary-light)" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="heroClay" x1="220" y1="210" x2="432" y2="498" gradientUnits="userSpaceOnUse">
          <stop stopColor="#E2A663" />
          <stop offset="0.42" stopColor="#B86835" />
          <stop offset="1" stopColor="#63341E" />
        </linearGradient>
        <linearGradient id="heroRim" x1="235" y1="205" x2="420" y2="284" gradientUnits="userSpaceOnUse">
          <stop stopColor="#F3CD98" />
          <stop offset="1" stopColor="#8A4725" />
        </linearGradient>
        <linearGradient id="heroSmoke" x1="270" y1="50" x2="388" y2="252" gradientUnits="userSpaceOnUse">
          <stop stopColor="#F2DFC5" stopOpacity="0" />
          <stop offset="0.42" stopColor="#E0B77F" stopOpacity="0.85" />
          <stop offset="1" stopColor="#9C6139" stopOpacity="0.08" />
        </linearGradient>
        <filter id="heroShadow" x="160" y="180" width="340" height="360" filterUnits="userSpaceOnUse">
          <feDropShadow dx="0" dy="28" stdDeviation="24" floodColor="#1E0E07" floodOpacity="0.34" />
        </filter>
        <filter id="softGlow" x="-40%" y="-40%" width="180%" height="180%">
          <feGaussianBlur stdDeviation="7" />
        </filter>
      </defs>

      <circle cx="354" cy="342" r="214" fill="url(#heroGlow)" />

      <g className="hero-orbit" opacity="0.58">
        <ellipse cx="352" cy="342" rx="245" ry="128" transform="rotate(-18 352 342)" stroke="var(--primary-light)" strokeWidth="1.2" strokeDasharray="7 10" />
        <ellipse cx="352" cy="342" rx="205" ry="95" transform="rotate(24 352 342)" stroke="var(--accent-light)" strokeWidth="0.9" strokeDasharray="3 12" />
        <circle cx="570" cy="278" r="4" fill="var(--accent-light)" />
        <circle cx="155" cy="412" r="3" fill="var(--primary-light)" />
        <circle cx="455" cy="116" r="2.5" fill="var(--secondary-light)" />
      </g>

      <g className="hero-smoke-one">
        <path d="M302 238C234 198 267 146 335 123C399 102 416 55 390 20" stroke="url(#heroSmoke)" strokeWidth="24" strokeLinecap="round" filter="url(#softGlow)" opacity="0.34" />
        <path d="M302 238C234 198 267 146 335 123C399 102 416 55 390 20" stroke="url(#heroSmoke)" strokeWidth="9" strokeLinecap="round" opacity="0.86" />
      </g>
      <g className="hero-smoke-two">
        <path d="M342 247C298 209 328 175 370 157C410 139 432 112 423 82" stroke="url(#heroSmoke)" strokeWidth="6" strokeLinecap="round" opacity="0.58" />
      </g>

      <g className="hero-code-card">
        <rect x="93" y="250" width="90" height="68" rx="18" fill="var(--card)" fillOpacity="0.86" stroke="var(--border)" />
        <path d="M129 271L113 284L129 297M148 267L137 302M155 271L171 284L155 297" stroke="var(--primary)" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
      </g>

      <g className="hero-code-card-delayed">
        <rect x="466" y="385" width="96" height="68" rx="18" fill="var(--card)" fillOpacity="0.86" stroke="var(--border)" />
        <path d="M491 405L504 416L491 427" stroke="var(--accent)" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M511 430H539" stroke="var(--muted-foreground)" strokeWidth="4" strokeLinecap="round" />
      </g>

      <g className="hero-pot" transform="rotate(-12 350 360)" filter="url(#heroShadow)">
        <path d="M228 278C208 335 210 432 260 488C298 531 397 534 447 486C493 442 493 337 458 278H228Z" fill="url(#heroClay)" stroke="#542A18" strokeWidth="8" />
        <ellipse cx="343" cy="278" rx="118" ry="46" fill="url(#heroRim)" stroke="#542A18" strokeWidth="8" />
        <ellipse cx="343" cy="278" rx="78" ry="24" fill="#2A160F" />
        <ellipse cx="343" cy="271" rx="58" ry="12" fill="#120A07" opacity="0.95" />

        <path d="M239 333C302 358 394 359 463 330" stroke="#F1C183" strokeWidth="11" strokeLinecap="round" opacity="0.78" />
        <path d="M247 440C309 466 393 467 453 439" stroke="#4B2517" strokeWidth="8" strokeLinecap="round" opacity="0.55" />
        <path d="M252 312L272 331L292 311L312 331L332 311L352 331L372 311L392 331L412 311L432 331" stroke="#66331D" strokeWidth="8" strokeLinecap="round" strokeLinejoin="round" opacity="0.8" />
        <path d="M272 458L291 440L310 458L329 440L348 458L367 440L386 458L405 440L424 458" stroke="#D99A55" strokeWidth="7" strokeLinecap="round" strokeLinejoin="round" opacity="0.62" />

        <path d="M318 365L274 400L318 435" stroke="#27140D" strokeWidth="22" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M371 355L338 443" stroke="#27140D" strokeWidth="18" strokeLinecap="round" />
        <path d="M391 365L435 400L391 435" stroke="#27140D" strokeWidth="22" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M318 370L282 400L318 430" stroke="#F3D0A2" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" opacity="0.64" />
        <path d="M370 363L341 437" stroke="#F3D0A2" strokeWidth="4" strokeLinecap="round" opacity="0.64" />
        <path d="M391 370L427 400L391 430" stroke="#F3D0A2" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" opacity="0.64" />
      </g>
    </svg>
  );
}
