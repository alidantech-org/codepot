export function HeroDecoration1() {
  return (
    <svg
      aria-hidden="true"
      className="pointer-events-none absolute inset-y-0 right-0 h-full w-auto opacity-10 md:opacity-60"
      viewBox="0 0 200 400"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient
          id="heroProgrammingGradient"
          x1="0%"
          y1="0%"
          x2="100%"
          y2="100%"
        >
          <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.8" />
          <stop offset="50%" stopColor="var(--secondary)" stopOpacity="0.7" />
          <stop offset="100%" stopColor="var(--accent)" stopOpacity="0.6" />
        </linearGradient>
      </defs>

      <rect
        x="140"
        y="40"
        width="50"
        height="35"
        rx="3"
        fill="var(--primary)"
        opacity="0.24"
        stroke="var(--primary)"
        strokeWidth="1"
      />
      <rect
        x="145"
        y="45"
        width="40"
        height="25"
        rx="2"
        fill="var(--background)"
        opacity="0.88"
      />
      <rect
        x="155"
        y="80"
        width="20"
        height="5"
        fill="var(--primary)"
        opacity="0.4"
      />
      <rect
        x="160"
        y="85"
        width="10"
        height="3"
        fill="var(--primary)"
        opacity="0.3"
      />

      <line
        x1="150"
        y1="50"
        x2="180"
        y2="50"
        stroke="var(--primary)"
        strokeWidth="1"
        opacity="0.6"
      />
      <line
        x1="150"
        y1="55"
        x2="175"
        y2="55"
        stroke="var(--secondary)"
        strokeWidth="1"
        opacity="0.6"
      />
      <line
        x1="150"
        y1="60"
        x2="178"
        y2="60"
        stroke="var(--accent)"
        strokeWidth="1"
        opacity="0.6"
      />
      <line
        x1="150"
        y1="65"
        x2="170"
        y2="65"
        stroke="var(--primary)"
        strokeWidth="1"
        opacity="0.6"
      />

      <rect
        x="160"
        y="110"
        width="25"
        height="25"
        rx="4"
        fill="#F7DF1E"
        opacity="0.8"
      />
      <text
        x="172"
        y="127"
        fontSize="10"
        fill="#000"
        textAnchor="middle"
        fontWeight="bold"
      >
        JS
      </text>
      <rect
        x="155"
        y="145"
        width="25"
        height="25"
        rx="4"
        fill="#3178C6"
        opacity="0.8"
      />
      <text
        x="167"
        y="162"
        fontSize="8"
        fill="#fff"
        textAnchor="middle"
        fontWeight="bold"
      >
        TS
      </text>
      <rect
        x="165"
        y="180"
        width="25"
        height="25"
        rx="4"
        fill="#3776AB"
        opacity="0.8"
      />
      <text
        x="177"
        y="197"
        fontSize="8"
        fill="#FFD43B"
        textAnchor="middle"
        fontWeight="bold"
      >
        Py
      </text>
      <circle cx="172" cy="225" r="12" fill="#61DAFB" opacity="0.8" />
      <circle cx="172" cy="225" r="6" fill="var(--background)" opacity="0.9" />
      <circle cx="172" cy="225" r="2" fill="#61DAFB" />
      <rect
        x="160"
        y="250"
        width="25"
        height="25"
        rx="4"
        fill="#339933"
        opacity="0.8"
      />
      <text
        x="172"
        y="267"
        fontSize="8"
        fill="#fff"
        textAnchor="middle"
        fontWeight="bold"
      >
        Node
      </text>

      <circle cx="170" cy="300" r="15" fill="var(--secondary)" opacity="0.36" />
      <path
        d="M160 295 Q170 290 180 295 Q175 305 170 310 Q165 305 160 295"
        fill="var(--primary)"
        opacity="0.6"
      />
      <circle cx="165" cy="298" r="2" fill="var(--accent)" opacity="0.8" />
      <circle cx="175" cy="298" r="2" fill="var(--accent)" opacity="0.8" />
      <circle cx="170" cy="305" r="2" fill="var(--accent)" opacity="0.8" />

      <text
        x="145"
        y="350"
        fontSize="16"
        fill="var(--primary)"
        opacity="0.7"
        fontWeight="bold"
      >
        &lt;/&gt;
      </text>
      <text
        x="155"
        y="370"
        fontSize="14"
        fill="var(--secondary)"
        opacity="0.6"
        fontWeight="bold"
      >
        {"{}"}
      </text>

      <path
        d="M200 0 Q150 100 180 200 T160 400"
        stroke="url(#heroProgrammingGradient)"
        strokeWidth="2"
        fill="none"
        opacity="0.8"
      />
      <path
        d="M180 50 Q120 150 160 250 T140 350"
        stroke="var(--primary)"
        strokeWidth="1"
        fill="none"
        opacity="0.6"
      />
      <circle cx="185" cy="75" r="3" fill="var(--primary)" opacity="0.7" />
      <circle cx="175" cy="125" r="2.5" fill="var(--secondary)" opacity="0.6" />
      <circle cx="190" cy="175" r="2" fill="var(--accent)" opacity="0.5" />
      <circle cx="180" cy="240" r="3" fill="var(--primary)" opacity="0.7" />
      <circle cx="170" cy="330" r="2.5" fill="var(--secondary)" opacity="0.6" />
      <text x="160" y="90" fontSize="8" fill="var(--accent)" opacity="0.6">
        &lt;
      </text>
      <text x="180" y="140" fontSize="8" fill="var(--primary)" opacity="0.6">
        /
      </text>
      <text x="165" y="215" fontSize="8" fill="var(--secondary)" opacity="0.6">
        &gt;
      </text>
      <text x="185" y="280" fontSize="8" fill="var(--accent)" opacity="0.6">
        ;
      </text>
    </svg>
  );
}
export function HeroDecoration2() {
  return (
    <svg
      aria-hidden="true"
      className="pointer-events-none absolute inset-y-0 right-4 h-full w-auto opacity-15 md:opacity-70"
      viewBox="0 0 200 400"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        {/* Changed ID to prevent clashing with Decoration 1 */}
        <linearGradient
          id="heroBackendGradient"
          x1="100%"
          y1="0%"
          x2="0%"
          y2="100%"
        >
          <stop offset="0%" stopColor="var(--accent)" stopOpacity="0.8" />
          <stop offset="50%" stopColor="var(--secondary)" stopOpacity="0.7" />
          <stop offset="100%" stopColor="var(--primary)" stopOpacity="0.6" />
        </linearGradient>
      </defs>

      {/* RUST - Orange theme */}
      <rect
        x="25"
        y="110"
        width="25"
        height="25"
        rx="4"
        fill="#CE412B"
        opacity="0.85"
      />
      <text
        x="37.5"
        y="126"
        fontSize="7"
        fill="#fff"
        textAnchor="middle"
        fontWeight="bold"
      >
        RUST
      </text>

      {/* RUBY - Deep Red theme */}
      <rect
        x="40"
        y="145"
        width="25"
        height="25"
        rx="4"
        fill="#CC342D"
        opacity="0.85"
      />
      <text
        x="52.5"
        y="161"
        fontSize="8"
        fill="#fff"
        textAnchor="middle"
        fontWeight="bold"
      >
        RB
      </text>

      {/* GO LANG - Cyan theme */}
      <rect
        x="20"
        y="180"
        width="25"
        height="25"
        rx="4"
        fill="#00ADD8"
        opacity="0.85"
      />
      <text
        x="32.5"
        y="196"
        fontSize="8"
        fill="#fff"
        textAnchor="middle"
        fontWeight="bold"
      >
        GO
      </text>

      {/* C++ - Blue theme */}
      <rect
        x="35"
        y="215"
        width="25"
        height="25"
        rx="4"
        fill="#00599C"
        opacity="0.85"
      />
      <text
        x="47.5"
        y="231"
        fontSize="8"
        fill="#fff"
        textAnchor="middle"
        fontWeight="bold"
      >
        C++
      </text>

      {/* PHP - Purple theme */}
      <rect
        x="25"
        y="250"
        width="25"
        height="25"
        rx="4"
        fill="#777BB4"
        opacity="0.85"
      />
      <text
        x="37.5"
        y="266"
        fontSize="8"
        fill="#fff"
        textAnchor="middle"
        fontWeight="bold"
      >
        PHP
      </text>

      {/* Database/Server visual asset icon */}
      <circle cx="35" cy="300" r="14" fill="var(--primary)" opacity="0.3" />
      <ellipse
        cx="35"
        cy="294"
        rx="10"
        ry="3"
        fill="none"
        stroke="var(--primary)"
        strokeWidth="1.5"
        opacity="0.8"
      />
      <path
        d="M25 294 V300 C25 303 45 303 45 300 V294"
        fill="none"
        stroke="var(--primary)"
        strokeWidth="1.5"
        opacity="0.8"
      />
      <path
        d="M25 300 V306 C25 309 45 309 45 306 V300"
        fill="none"
        stroke="var(--primary)"
        strokeWidth="1.5"
        opacity="0.8"
      />

      {/* Code syntax structural fragments */}
      <text
        x="25"
        y="350"
        fontSize="15"
        fill="var(--accent)"
        opacity="0.7"
        fontWeight="bold"
      >
        =&gt;
      </text>
      <text
        x="35"
        y="370"
        fontSize="13"
        fill="var(--primary)"
        opacity="0.6"
        fontWeight="bold"
      >
        []
      </text>

      {/* Mirrored flow lines running from left downwards to right */}
      <path
        d="M0 20 Q60 120 30 220 T50 400"
        stroke="url(#heroBackendGradient)"
        strokeWidth="2"
        fill="none"
        opacity="0.8"
      />
      <path
        d="M20 70 Q90 170 40 270 T70 380"
        stroke="var(--secondary)"
        strokeWidth="1"
        fill="none"
        opacity="0.5"
      />

      {/* Floating terminal particles */}
      <circle cx="15" cy="75" r="2.5" fill="var(--accent)" opacity="0.6" />
      <circle cx="55" cy="130" r="2" fill="var(--primary)" opacity="0.5" />
      <circle cx="10" cy="195" r="3" fill="var(--secondary)" opacity="0.7" />
      <circle cx="50" cy="245" r="2" fill="var(--accent)" opacity="0.6" />
      <circle cx="20" cy="330" r="2.5" fill="var(--primary)" opacity="0.5" />

      <text x="45" y="95" fontSize="9" fill="var(--primary)" opacity="0.6">
        ::
      </text>
      <text x="15" y="150" fontSize="9" fill="var(--accent)" opacity="0.6">
        &amp;
      </text>
      <text x="55" y="200" fontSize="9" fill="var(--secondary)" opacity="0.6">
        *
      </text>
      <text x="10" y="280" fontSize="9" fill="var(--primary)" opacity="0.6">
        #
      </text>
    </svg>
  );
}
