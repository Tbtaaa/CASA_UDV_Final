/**
 * chart_enhancements.js
 * =====================
 * Interactive enhancements for the "Travel to School" section.
 *
 * Sources:
 *   - Schools: DfE Get Information About Schools 2024
 *   - NTS:     DfT National Travel Survey table NTS9908, August 2025
 */

// ═══════════════════════════════════════════════════════════════════
//  DATA — borough-level school statistics (from CSV)
// ═══════════════════════════════════════════════════════════════════
const BOROUGH_DATA = [
  { borough:"Barnet",        schoolCount:22, utilisationPct:87.5, p8Schools:10, ofsted:{outstanding:4,good:17,ri:0,inadequate:0,notInspected:1}, medianFsm:26.1, medianP8:0.61, totalPupils:23497 },
  { borough:"Hillingdon",    schoolCount:20, utilisationPct:91.4, p8Schools:6,  ofsted:{outstanding:4,good:10,ri:1,inadequate:0,notInspected:5}, medianFsm:20.2, medianP8:0.35, totalPupils:22416 },
  { borough:"Enfield",       schoolCount:19, utilisationPct:88.4, p8Schools:2,  ofsted:{outstanding:1,good:14,ri:0,inadequate:0,notInspected:4}, medianFsm:29.3, medianP8:0.28, totalPupils:20600 },
  { borough:"Hounslow",      schoolCount:19, utilisationPct:91.8, p8Schools:6,  ofsted:{outstanding:5,good:9,ri:0,inadequate:0,notInspected:5},  medianFsm:28.1, medianP8:0.46, totalPupils:18310 },
  { borough:"Newham",        schoolCount:19, utilisationPct:89.7, p8Schools:2,  ofsted:{outstanding:4,good:10,ri:0,inadequate:0,notInspected:5}, medianFsm:38.8, medianP8:0.27, totalPupils:21757 },
  { borough:"Southwark",     schoolCount:19, utilisationPct:92.8, p8Schools:5,  ofsted:{outstanding:6,good:10,ri:1,inadequate:0,notInspected:2}, medianFsm:37.3, medianP8:0.51, totalPupils:16456 },
  { borough:"Croydon",       schoolCount:18, utilisationPct:81.8, p8Schools:0,  ofsted:{outstanding:1,good:12,ri:3,inadequate:0,notInspected:2}, medianFsm:25.5, medianP8:-0.01, totalPupils:19449 },
  { borough:"Ealing",        schoolCount:16, utilisationPct:93.5, p8Schools:7,  ofsted:{outstanding:8,good:5,ri:0,inadequate:0,notInspected:3},  medianFsm:24.1, medianP8:0.75, totalPupils:15880 },
  { borough:"Redbridge",     schoolCount:16, utilisationPct:95.2, p8Schools:7,  ofsted:{outstanding:5,good:9,ri:1,inadequate:0,notInspected:1},  medianFsm:22.1, medianP8:0.65, totalPupils:18880 },
  { borough:"Brent",         schoolCount:16, utilisationPct:92.8, p8Schools:6,  ofsted:{outstanding:5,good:8,ri:0,inadequate:0,notInspected:3},  medianFsm:31.3, medianP8:0.62, totalPupils:15082 },
  { borough:"Waltham Forest",schoolCount:16, utilisationPct:93.9, p8Schools:0,  ofsted:{outstanding:1,good:13,ri:0,inadequate:0,notInspected:2}, medianFsm:32.3, medianP8:0.24, totalPupils:16014 },
  { borough:"Tower Hamlets", schoolCount:16, utilisationPct:92.0, p8Schools:2,  ofsted:{outstanding:3,good:11,ri:0,inadequate:0,notInspected:2}, medianFsm:44.1, medianP8:0.42, totalPupils:15327 },
  { borough:"Bromley",       schoolCount:16, utilisationPct:96.5, p8Schools:1,  ofsted:{outstanding:3,good:11,ri:0,inadequate:0,notInspected:2}, medianFsm:14.2, medianP8:0.15, totalPupils:16957 },
  { borough:"Lambeth",       schoolCount:15, utilisationPct:87.9, p8Schools:3,  ofsted:{outstanding:3,good:8,ri:2,inadequate:0,notInspected:2},  medianFsm:37.0, medianP8:0.34, totalPupils:11861 },
  { borough:"Hackney",       schoolCount:15, utilisationPct:91.8, p8Schools:5,  ofsted:{outstanding:3,good:12,ri:0,inadequate:0,notInspected:0}, medianFsm:40.2, medianP8:0.60, totalPupils:13200 },
  { borough:"Havering",      schoolCount:14, utilisationPct:91.3, p8Schools:2,  ofsted:{outstanding:2,good:10,ri:2,inadequate:0,notInspected:0}, medianFsm:18.9, medianP8:0.13, totalPupils:16399 },
  { borough:"Lewisham",      schoolCount:14, utilisationPct:84.9, p8Schools:3,  ofsted:{outstanding:4,good:7,ri:1,inadequate:0,notInspected:2},  medianFsm:31.1, medianP8:0.24, totalPupils:13028 },
  { borough:"Greenwich",     schoolCount:13, utilisationPct:91.7, p8Schools:5,  ofsted:{outstanding:4,good:7,ri:0,inadequate:1,notInspected:1},  medianFsm:31.2, medianP8:0.53, totalPupils:14064 },
  { borough:"Haringey",      schoolCount:12, utilisationPct:86.3, p8Schools:1,  ofsted:{outstanding:2,good:5,ri:2,inadequate:1,notInspected:2},  medianFsm:33.2, medianP8:0.16, totalPupils:10765 },
  { borough:"Harrow",        schoolCount:12, utilisationPct:95.6, p8Schools:5,  ofsted:{outstanding:4,good:5,ri:1,inadequate:0,notInspected:2},  medianFsm:17.8, medianP8:0.56, totalPupils:13403 },
  { borough:"Wandsworth",    schoolCount:11, utilisationPct:84.9, p8Schools:5,  ofsted:{outstanding:4,good:5,ri:0,inadequate:0,notInspected:2},  medianFsm:24.2, medianP8:0.72, totalPupils:9905 },
  { borough:"Islington",     schoolCount:10, utilisationPct:79.1, p8Schools:2,  ofsted:{outstanding:2,good:6,ri:1,inadequate:0,notInspected:1},  medianFsm:39.2, medianP8:0.45, totalPupils:7504 },
  { borough:"Camden",        schoolCount:10, utilisationPct:86.0, p8Schools:4,  ofsted:{outstanding:3,good:5,ri:0,inadequate:0,notInspected:2},  medianFsm:34.4, medianP8:0.62, totalPupils:8688 },
  { borough:"Merton",        schoolCount:9,  utilisationPct:93.6, p8Schools:3,  ofsted:{outstanding:1,good:5,ri:1,inadequate:0,notInspected:2},  medianFsm:19.8, medianP8:0.38, totalPupils:9283 },
  { borough:"Barking and Dagenham", schoolCount:9, utilisationPct:97.1, p8Schools:0, ofsted:{outstanding:0,good:8,ri:0,inadequate:0,notInspected:1}, medianFsm:42.9, medianP8:0.11, totalPupils:11428 },
  { borough:"Westminster",   schoolCount:8,  utilisationPct:78.5, p8Schools:4,  ofsted:{outstanding:4,good:3,ri:0,inadequate:0,notInspected:1},  medianFsm:39.6, medianP8:0.68, totalPupils:5912 },
  { borough:"Sutton",        schoolCount:8,  utilisationPct:95.1, p8Schools:2,  ofsted:{outstanding:3,good:4,ri:0,inadequate:0,notInspected:1},  medianFsm:13.3, medianP8:0.26, totalPupils:7736 },
  { borough:"Hammersmith and Fulham", schoolCount:8, utilisationPct:80.5, p8Schools:2, ofsted:{outstanding:2,good:4,ri:1,inadequate:0,notInspected:1}, medianFsm:30.2, medianP8:0.53, totalPupils:5832 },
  { borough:"Bexley",        schoolCount:8,  utilisationPct:98.1, p8Schools:0,  ofsted:{outstanding:1,good:5,ri:1,inadequate:0,notInspected:1},  medianFsm:17.1, medianP8:-0.01, totalPupils:9756 },
  { borough:"Richmond upon Thames", schoolCount:7, utilisationPct:94.3, p8Schools:1, ofsted:{outstanding:1,good:5,ri:0,inadequate:0,notInspected:1}, medianFsm:10.0, medianP8:0.34, totalPupils:7155 },
  { borough:"Kensington and Chelsea", schoolCount:6, utilisationPct:73.3, p8Schools:3, ofsted:{outstanding:3,good:2,ri:0,inadequate:0,notInspected:1}, medianFsm:31.2, medianP8:0.69, totalPupils:3592 },
  { borough:"Kingston upon Thames", schoolCount:5, utilisationPct:98.2, p8Schools:2, ofsted:{outstanding:1,good:3,ri:0,inadequate:0,notInspected:1}, medianFsm:13.6, medianP8:0.35, totalPupils:5827 },
];

// ═══════════════════════════════════════════════════════════════════
//  DATA — NTS mode share time series (London, 2002–2024)
// ═══════════════════════════════════════════════════════════════════
const TIME_SERIES = [
  { year:"2016 to 2017", ys:"2017", walkCycle:51.8, car:19.2, transit:27.3, bus:23.6, rail:3.7, sample:818 },
  { year:"2017 to 2018", ys:"2018", walkCycle:52.2, car:20.8, transit:24.0, bus:21.0, rail:3.0, sample:665 },
  { year:"2018 to 2019", ys:"2019", walkCycle:53.9, car:20.3, transit:23.6, bus:20.8, rail:2.8, sample:619 },
  { year:"2020",         ys:"2020", walkCycle:71.3, car:19.2, transit:9.5,  bus:9.5,  rail:0.0, sample:98  },
  { year:"2021",         ys:"2021", walkCycle:61.4, car:14.2, transit:24.4, bus:23.8, rail:0.6, sample:193 },
  { year:"2022",         ys:"2022", walkCycle:51.2, car:24.5, transit:23.6, bus:22.3, rail:1.2, sample:165 },
  { year:"2023 to 2024", ys:"2024", walkCycle:56.8, car:19.2, transit:21.5, bus:18.8, rail:2.7, sample:797 },
];

// ═══════════════════════════════════════════════════════════════════
//  DATA — travel times by borough (PLACEHOLDER — fill from parquet)
//  Run convert_travel_parquet.py to generate this.
//  Format:  { "londonWide": { "transitAny": 15.2, ... },
//             "byBorough":  { "Barnet": { "transitAny": 14.1, ... }, ... } }
// ═══════════════════════════════════════════════════════════════════
const BOROUGH_TRAVEL = {
  "byBorough": {
    "Barking and Dagenham": {
      "transitAny": 5.5,
      "walkAny": 5.5,
      "cycleAny": 3.5,
      "carAny": 2.5
    },
    "Barnet": {
      "transitAny": 7.5,
      "walkAny": 7.5,
      "cycleAny": 4.0,
      "carAny": 2.0
    },
    "Bexley": {
      "transitAny": 6.0,
      "walkAny": 6.0,
      "cycleAny": 4.0,
      "carAny": 2.0
    },
    "Brent": {
      "transitAny": 11.5,
      "walkAny": 11.5,
      "cycleAny": 6.0,
      "carAny": 3.0
    },
    "Bromley": {
      "transitAny": 10.0,
      "walkAny": 10.0,
      "cycleAny": 7.0,
      "carAny": 3.0
    },
    "Camden": {
      "transitAny": 7.0,
      "walkAny": 7.0,
      "cycleAny": 4.0,
      "carAny": 3.0
    },
    "Croydon": {
      "transitAny": 8.0,
      "walkAny": 8.0,
      "cycleAny": 5.0,
      "carAny": 3.0
    },
    "Ealing": {
      "transitAny": 7.0,
      "walkAny": 7.0,
      "cycleAny": 4.0,
      "carAny": 2.0
    },
    "Enfield": {
      "transitAny": 8.0,
      "walkAny": 8.0,
      "cycleAny": 4.0,
      "carAny": 3.0
    },
    "Greenwich": {
      "transitAny": 12.0,
      "walkAny": 12.0,
      "cycleAny": 5.0,
      "carAny": 3.0
    },
    "Hackney": {
      "transitAny": 6.0,
      "walkAny": 6.0,
      "cycleAny": 4.0,
      "carAny": 2.0
    },
    "Hammersmith and Fulham": {
      "transitAny": 6.0,
      "walkAny": 6.0,
      "cycleAny": 3.0,
      "carAny": 2.0
    },
    "Haringey": {
      "transitAny": 9.0,
      "walkAny": 9.0,
      "cycleAny": 5.0,
      "carAny": 2.0
    },
    "Harrow": {
      "transitAny": 8.0,
      "walkAny": 8.0,
      "cycleAny": 4.0,
      "carAny": 2.0
    },
    "Havering": {
      "transitAny": 7.5,
      "walkAny": 7.5,
      "cycleAny": 3.0,
      "carAny": 2.0
    },
    "Hillingdon": {
      "transitAny": 10.0,
      "walkAny": 10.0,
      "cycleAny": 4.0,
      "carAny": 3.0
    },
    "Hounslow": {
      "transitAny": 11.0,
      "walkAny": 11.0,
      "cycleAny": 4.0,
      "carAny": 3.0
    },
    "Islington": {
      "transitAny": 6.0,
      "walkAny": 6.0,
      "cycleAny": 3.0,
      "carAny": 2.5
    },
    "Kensington and Chelsea": {
      "transitAny": 7.0,
      "walkAny": 7.0,
      "cycleAny": 3.0,
      "carAny": 1.0
    },
    "Kingston upon Thames": {
      "transitAny": 11.0,
      "walkAny": 11.0,
      "cycleAny": 5.0,
      "carAny": 3.0
    },
    "Lambeth": {
      "transitAny": 7.0,
      "walkAny": 7.0,
      "cycleAny": 4.0,
      "carAny": 2.0
    },
    "Lewisham": {
      "transitAny": 7.0,
      "walkAny": 7.0,
      "cycleAny": 2.5,
      "carAny": 2.0
    },
    "Merton": {
      "transitAny": 8.0,
      "walkAny": 8.0,
      "cycleAny": 4.0,
      "carAny": 4.0
    },
    "Newham": {
      "transitAny": 6.5,
      "walkAny": 6.5,
      "cycleAny": 4.0,
      "carAny": 2.0
    },
    "Redbridge": {
      "transitAny": 8.0,
      "walkAny": 8.0,
      "cycleAny": 3.0,
      "carAny": 2.5
    },
    "Richmond upon Thames": {
      "transitAny": 9.0,
      "walkAny": 9.0,
      "cycleAny": 5.0,
      "carAny": 3.0
    },
    "Southwark": {
      "transitAny": 7.0,
      "walkAny": 7.0,
      "cycleAny": 3.0,
      "carAny": 2.0
    },
    "Sutton": {
      "transitAny": 8.0,
      "walkAny": 8.0,
      "cycleAny": 4.0,
      "carAny": 2.0
    },
    "Tower Hamlets": {
      "transitAny": 6.5,
      "walkAny": 6.5,
      "cycleAny": 3.0,
      "carAny": 2.5
    },
    "Waltham Forest": {
      "transitAny": 8.0,
      "walkAny": 8.0,
      "cycleAny": 3.0,
      "carAny": 3.0
    },
    "Wandsworth": {
      "transitAny": 6.5,
      "walkAny": 6.5,
      "cycleAny": 3.0,
      "carAny": 2.5
    },
    "Westminster": {
      "transitAny": 5.0,
      "walkAny": 5.0,
      "cycleAny": 2.0,
      "carAny": 2.0
    }
  }
};  // ← paste JSON output here

// ═══════════════════════════════════════════════════════════════════
//  COLOUR PALETTE (matches existing page theme)
// ═══════════════════════════════════════════════════════════════════
const C = {
  bg:      "#0f1225",
  card:    "#171b30",
  text:    "#f0e8d8",
  sub:     "#8a8578",
  grid:    "rgba(255,255,255,0.06)",
  accent:  "#d4944a",
  green:   "#5DCAA5",
  blue:    "#378ADD",
  purple:  "#7F77DD",
  amber:   "#BA7517",
  coral:   "#D85A30",
  red:     "#E24B4A",
  lgray:   "#D3D1C7",
  ofsted:  { outstanding:"#1D9E75", good:"#378ADD", ri:"#BA7517", inadequate:"#E24B4A", notInspected:"#555" },
};


// ═══════════════════════════════════════════════════════════════════
//  CHART 2 — Borough bar chart with rich tooltip
// ═══════════════════════════════════════════════════════════════════
function initChart2(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  // Sort boroughs by school count (descending for display, but
  // horizontal bars are drawn bottom-up so we reverse)
  const sorted = [...BOROUGH_DATA].sort((a, b) => b.schoolCount - a.schoolCount);
  const top = sorted.slice(0, 10);  // show top 10

  // Create canvas + tooltip div
  container.style.position = "relative";
  container.innerHTML = `
    <div style="position:relative; width:100%; height:${top.length * 38 + 80}px;">
      <canvas id="${containerId}-canvas"></canvas>
    </div>
    <div id="${containerId}-tooltip" style="
      display:none; position:absolute; z-index:20;
      background:${C.card}; border:1px solid rgba(255,255,255,0.12);
      border-radius:10px; padding:16px; width:280px;
      box-shadow:0 8px 32px rgba(0,0,0,0.5); pointer-events:none;
      font-family:inherit; color:${C.text};
    "></div>
  `;

  const ctx = document.getElementById(`${containerId}-canvas`);
  const tooltipEl = document.getElementById(`${containerId}-tooltip`);

  // Build Ofsted-segmented bars using stacked horizontal bar
  const grades = ["outstanding", "good", "ri", "inadequate", "notInspected"];
  const gradeLabels = ["Outstanding", "Good", "Requires improvement", "Inadequate", "Not yet inspected"];
  const gradeColors = [C.ofsted.outstanding, C.ofsted.good, C.ofsted.ri, C.ofsted.red, C.ofsted.notInspected];

  const datasets = grades.map((g, i) => ({
    label: gradeLabels[i],
    data: top.map(b => b.ofsted[g]),
    backgroundColor: gradeColors[i],
    borderWidth: 0,
    borderSkipped: false,
    barPercentage: 0.7,
  }));

  const chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: top.map(b => b.borough),
      datasets,
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          stacked: true,
          grid: { color: C.grid },
          ticks: { color: C.sub, font: { family: "'IBM Plex Mono', monospace", size: 11 } },
          title: { display: true, text: "Number of non-selective schools", color: C.sub, font: { size: 11 } },
        },
        y: {
          stacked: true,
          grid: { display: false },
          ticks: { color: C.text, font: { family: "'IBM Plex Mono', monospace", size: 11 } },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: { enabled: false },
      },
      onHover: (event, elements) => {
        if (!elements.length) { tooltipEl.style.display = "none"; return; }
        const idx = elements[0].index;
        const b = top[idx];
        showTooltip(b, event, tooltipEl, container);
      },
    },
  });

  // Click-away hides tooltip
  document.addEventListener("click", (e) => {
    if (!container.contains(e.target)) tooltipEl.style.display = "none";
  });
}

function showTooltip(b, event, el, container) {
  const o = b.ofsted;
  const total = o.outstanding + o.good + o.ri + o.inadequate + o.notInspected;

  // Ofsted micro bar segments (percentage widths)
  const pct = (n) => Math.round((n / total) * 100);
  const ofstedBar = `
    <div style="display:flex;gap:2px;height:6px;border-radius:3px;overflow:hidden;margin:4px 0 6px;">
      ${o.outstanding ? `<span style="width:${pct(o.outstanding)}%;background:${C.ofsted.outstanding}"></span>` : ""}
      ${o.good ? `<span style="width:${pct(o.good)}%;background:${C.ofsted.good}"></span>` : ""}
      ${o.ri ? `<span style="width:${pct(o.ri)}%;background:${C.ofsted.ri}"></span>` : ""}
      ${o.inadequate ? `<span style="width:${pct(o.inadequate)}%;background:${C.ofsted.inadequate}"></span>` : ""}
      ${o.notInspected ? `<span style="width:${pct(o.notInspected)}%;background:${C.ofsted.notInspected}"></span>` : ""}
    </div>
    <div style="display:flex;gap:8px;flex-wrap:wrap;font-size:10px;color:${C.sub};">
      ${o.outstanding ? `<span>● ${o.outstanding} outstanding</span>` : ""}
      <span style="color:${C.ofsted.good}">● ${o.good} good</span>
      ${o.ri ? `<span style="color:${C.ofsted.ri}">● ${o.ri} RI</span>` : ""}
      ${o.inadequate ? `<span style="color:${C.red}">● ${o.inadequate} inadequate</span>` : ""}
      ${o.notInspected ? `<span>● ${o.notInspected} not inspected</span>` : ""}
    </div>
  `;

  // Utilisation bar
  const utilColor = b.utilisationPct > 100 ? C.red : b.utilisationPct > 95 ? C.amber : C.blue;
  const utilBar = `
    <div style="display:flex;align-items:center;gap:6px;">
      <div style="flex:1;height:5px;background:${C.grid};border-radius:3px;overflow:hidden;">
        <div style="width:${Math.min(b.utilisationPct, 110)}%;height:100%;background:${utilColor};border-radius:3px;"></div>
      </div>
      <span style="font-family:'IBM Plex Mono',monospace;font-size:12px;font-weight:500;">${b.utilisationPct}%</span>
    </div>
  `;

  // Travel time rows (if data available)
  let travelHtml = "";
  if (BOROUGH_TRAVEL && BOROUGH_TRAVEL.byBorough[b.borough]) {
    const t = BOROUGH_TRAVEL.byBorough[b.borough];
    const modes = [
      { label: "Transit", val: t.transitAny, color: C.blue },
      { label: "Walk",    val: t.walkAny,    color: C.green },
      { label: "Cycle",   val: t.cycleAny,   color: C.purple },
      { label: "Car",     val: t.carAny,     color: C.amber },
    ];
    const maxVal = Math.max(...modes.map(m => m.val || 0), 1);

    travelHtml = `
      <div style="border-top:1px solid rgba(255,255,255,0.08);margin:8px 0;padding-top:8px;">
        <div style="font-size:10px;color:${C.accent};letter-spacing:0.06em;margin-bottom:6px;">
          MEDIAN TRAVEL TIME TO NEAREST SCHOOL
        </div>
        ${modes.map(m => `
          <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
            <span style="font-size:10px;color:${C.sub};width:44px;">${m.label}</span>
            <div style="flex:1;height:4px;background:${C.grid};border-radius:2px;">
              <div style="width:${((m.val || 0) / maxVal * 100)}%;height:100%;background:${m.color};border-radius:2px;"></div>
            </div>
            <span style="font-size:10px;font-family:'IBM Plex Mono',monospace;color:${C.text};width:36px;text-align:right;">
              ${m.val != null ? Math.round(m.val) + " min" : "—"}
            </span>
          </div>
        `).join("")}
      </div>
      ${t.transitP8 != null ? `
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:4px;">
          <span style="font-size:10px;color:${C.sub};">Quality penalty (P8)</span>
          <span style="font-size:10px;padding:2px 6px;border-radius:4px;
            background:rgba(232,75,74,0.15);color:${C.red};font-family:'IBM Plex Mono',monospace;">
            +${Math.round(t.transitP8 - t.transitAny)} min by transit
          </span>
        </div>
      ` : ""}
    `;
  }

  el.innerHTML = `
    <div style="font-size:15px;font-weight:500;margin-bottom:10px;">${b.borough}</div>
    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
      <span style="font-size:11px;color:${C.sub};">Schools (non-selective)</span>
      <span style="font-family:'IBM Plex Mono',monospace;font-size:13px;font-weight:500;">${b.schoolCount}</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
      <span style="font-size:11px;color:${C.sub};">Top-25% P8 schools</span>
      <span style="font-family:'IBM Plex Mono',monospace;font-size:13px;font-weight:500;color:${C.ofsted.outstanding};">${b.p8Schools}</span>
    </div>
    <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
      <span style="font-size:11px;color:${C.sub};">Pupils</span>
      <span style="font-family:'IBM Plex Mono',monospace;font-size:13px;">${(b.totalPupils || 0).toLocaleString()}</span>
    </div>
    <div style="border-top:1px solid rgba(255,255,255,0.08);margin:8px 0;padding-top:8px;">
      <div style="font-size:10px;color:${C.accent};letter-spacing:0.06em;margin-bottom:4px;">OFSTED BREAKDOWN</div>
      ${ofstedBar}
    </div>
    <div style="border-top:1px solid rgba(255,255,255,0.08);margin:8px 0;padding-top:8px;">
      <div style="font-size:10px;color:${C.accent};letter-spacing:0.06em;margin-bottom:6px;">UTILISATION</div>
      ${utilBar}
    </div>
    ${travelHtml}
  `;

  // Position tooltip
  const rect = container.getBoundingClientRect();
  let left = event.native.clientX - rect.left + 20;
  let top  = event.native.clientY - rect.top - 60;
  if (left + 300 > rect.width) left = left - 320;
  if (top < 0) top = 10;
  el.style.left = left + "px";
  el.style.top  = top + "px";
  el.style.display = "block";
}


// ═══════════════════════════════════════════════════════════════════
//  CHART 1a — Mode share time series (line chart, 2003–2024)
// ═══════════════════════════════════════════════════════════════════
function initChart1TimeSeries(containerId) {
  const container = document.getElementById(containerId);
  if (!container) return;

  container.innerHTML = `
    <div style="position:relative;width:100%;height:320px;">
      <canvas id="${containerId}-canvas"></canvas>
    </div>
  `;

  const ctx = document.getElementById(`${containerId}-canvas`);

  // Highlight COVID year
  const covidPlugin = {
    id: "covidBand",
    beforeDraw(chart) {
      const { ctx: c, chartArea: { top, bottom }, scales: { x } } = chart;
      const i2020 = TIME_SERIES.findIndex(d => d.ys === "2020");
      const i2021 = TIME_SERIES.findIndex(d => d.ys === "2021");
      if (i2020 < 0) return;
      const x0 = x.getPixelForValue(i2020) - 8;
      const x1 = x.getPixelForValue(i2021) + 8;
      c.save();
      c.fillStyle = "rgba(232,75,74,0.08)";
      c.fillRect(x0, top, x1 - x0, bottom - top);
      c.fillStyle = C.sub;
      c.font = "10px sans-serif";
      c.textAlign = "center";
      c.fillText("COVID", (x0 + x1) / 2, top + 14);
      c.restore();
    },
  };

  new Chart(ctx, {
    type: "line",
    data: {
      labels: TIME_SERIES.map(d => d.ys),
      datasets: [
        {
          label: "Walk / cycle",
          data: TIME_SERIES.map(d => d.walkCycle),
          borderColor: C.green,
          backgroundColor: C.green + "20",
          fill: false,
          tension: 0.3,
          pointRadius: 3,
          pointHoverRadius: 6,
          borderWidth: 2.5,
        },
        {
          label: "Car",
          data: TIME_SERIES.map(d => d.car),
          borderColor: C.coral,
          fill: false,
          tension: 0.3,
          pointRadius: 3,
          pointHoverRadius: 6,
          borderWidth: 2.5,
        },
        {
          label: "Transit (bus + rail)",
          data: TIME_SERIES.map(d => d.transit),
          borderColor: C.blue,
          fill: false,
          tension: 0.3,
          pointRadius: 3,
          pointHoverRadius: 6,
          borderWidth: 2.5,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      scales: {
        x: {
          grid: { color: C.grid },
          ticks: { color: C.sub, font: { size: 10 }, maxRotation: 45 },
        },
        y: {
          grid: { color: C.grid },
          ticks: {
            color: C.sub,
            callback: (v) => v + "%",
            font: { size: 10 },
          },
          min: 0, max: 75,
          title: { display: true, text: "Mode share (%)", color: C.sub, font: { size: 11 } },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: C.card,
          titleColor: C.text,
          bodyColor: C.text,
          borderColor: "rgba(255,255,255,0.12)",
          borderWidth: 1,
          padding: 12,
          callbacks: {
            title: (items) => {
              const d = TIME_SERIES[items[0].dataIndex];
              return `${d.year}`;
            },
            label: (item) => ` ${item.dataset.label}: ${item.raw}%`,
          },
        },
      },
    },
    plugins: [covidPlugin],
  });

  // Custom legend below chart
  const legend = document.createElement("div");
  legend.style.cssText = "display:flex;gap:16px;justify-content:center;margin-top:8px;font-size:12px;";
  legend.innerHTML = [
    { label: "Walk / cycle", color: C.green },
    { label: "Car", color: C.coral },
    { label: "Transit", color: C.blue },
  ].map(l => `
    <span style="display:flex;align-items:center;gap:4px;color:${C.sub};">
      <span style="width:12px;height:3px;background:${l.color};border-radius:1px;"></span>
      ${l.label}
    </span>
  `).join("");
  container.appendChild(legend);
}


// ═══════════════════════════════════════════════════════════════════
//  CHART 1b — Travel time lollipop (Option A companion)
//  Only renders if BOROUGH_TRAVEL is filled in.
// ═══════════════════════════════════════════════════════════════════
function initChart1Lollipop(containerId) {
  const container = document.getElementById(containerId);
  if (!container || !BOROUGH_TRAVEL) return;

  const lw = BOROUGH_TRAVEL.londonWide;
  const modes = [
    { label: "Car",     val: lw.carAny,     color: C.amber },
    { label: "Cycle",   val: lw.cycleAny,   color: C.purple },
    { label: "Transit", val: lw.transitAny, color: C.blue },
    { label: "Walk",    val: lw.walkAny,    color: C.green },
  ];

  container.innerHTML = `<div style="position:relative;width:100%;height:200px;">
    <canvas id="${containerId}-canvas"></canvas>
  </div>`;

  const ctx = document.getElementById(`${containerId}-canvas`);

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: modes.map(m => m.label),
      datasets: [{
        data: modes.map(m => m.val),
        backgroundColor: modes.map(m => m.color),
        borderWidth: 0,
        barPercentage: 0.5,
      }],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: C.grid },
          ticks: { color: C.sub, callback: (v) => v + " min", font: { size: 10 } },
          title: { display: true, text: "Median travel time to nearest school (min)", color: C.sub, font: { size: 10 } },
        },
        y: {
          grid: { display: false },
          ticks: { color: C.text, font: { family: "'IBM Plex Mono', monospace", size: 11 } },
        },
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: C.card,
          titleColor: C.text,
          bodyColor: C.text,
          borderColor: "rgba(255,255,255,0.12)",
          borderWidth: 1,
          callbacks: { label: (item) => ` ${Math.round(item.raw)} minutes` },
        },
      },
    },
  });
}


// ═══════════════════════════════════════════════════════════════════
//  INIT — run on DOM ready
// ═══════════════════════════════════════════════════════════════════
function initChartEnhancements() {
  initChart1bTravelTime("chart2-bar-container"); 
  initChart1TimeSeries("chart1-timeseries");
  initChart1Lollipop("chart1-lollipop");
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initChartEnhancements);
} else {
  initChartEnhancements();
}


// Add this anywhere in chart_enhancements.js
function initChart1bTravelTime(containerId) {
  const container = document.getElementById(containerId);
  if (!container || !BOROUGH_TRAVEL || !BOROUGH_TRAVEL.byBorough) return;

  // 1. Get ALL boroughs and sort by Transit Time descending (longest at the top)
  const sortedBoroughs = Object.keys(BOROUGH_TRAVEL.byBorough)
    .sort((a, b) => BOROUGH_TRAVEL.byBorough[b].transitAny - BOROUGH_TRAVEL.byBorough[a].transitAny);

  // 2. Prepare datasets (Order: Car, Cycle, Walk, Transit to match the image)
  const dataCar     = sortedBoroughs.map(b => BOROUGH_TRAVEL.byBorough[b].carAny);
  const dataCycle   = sortedBoroughs.map(b => BOROUGH_TRAVEL.byBorough[b].cycleAny);
  const dataWalk    = sortedBoroughs.map(b => BOROUGH_TRAVEL.byBorough[b].walkAny);
  const dataTransit = sortedBoroughs.map(b => BOROUGH_TRAVEL.byBorough[b].transitAny);

  // 3. Set height tall enough for all 32 boroughs to breathe
  container.style.position = "relative";
  container.innerHTML = `
    <div style="position:relative; width:100%; height:900px;">
      <canvas id="${containerId}-canvas"></canvas>
    </div>
  `;

  const ctx = document.getElementById(`${containerId}-canvas`);

  // 4. Custom plugin to draw the dashed median line
  const medianLinePlugin = {
    id: 'medianLine',
    beforeDraw(chart) {
      const { ctx, chartArea: { top, bottom }, scales: { x } } = chart;
      const xPos = x.getPixelForValue(8); // 8 minutes median
      
      ctx.save();
      ctx.beginPath();
      ctx.strokeStyle = 'rgba(245, 166, 35, 0.6)'; // Semi-transparent orange
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]); // Dashed line
      ctx.moveTo(xPos, top);
      ctx.lineTo(xPos, bottom);
      ctx.stroke();

      // Add text label next to the line
      ctx.fillStyle = '#F5A623'; // Orange text
      ctx.font = '11px sans-serif';
      ctx.fillText('London median', xPos + 8, top + 15);
      ctx.fillText('8 min (transit)', xPos + 8, top + 28);
      ctx.restore();
    }
  };

  new Chart(ctx, {
    type: "bar",
    data: {
      labels: sortedBoroughs,
      datasets: [
        { label: "Car",     data: dataCar,     backgroundColor: "#F5A623", barPercentage: 0.85, categoryPercentage: 0.8 },
        { label: "Cycle",   data: dataCycle,   backgroundColor: "#A78BFA", barPercentage: 0.85, categoryPercentage: 0.8 },
        { label: "Walk",    data: dataWalk,    backgroundColor: "#4EC9A0", barPercentage: 0.85, categoryPercentage: 0.8 },
        { label: "Transit", data: dataTransit, backgroundColor: "#5B8DEF", barPercentage: 0.85, categoryPercentage: 0.8 }
      ]
    },
    options: {
      indexAxis: "y", 
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: "rgba(255,255,255,0.06)", drawBorder: false },
          ticks: { color: "#8B8FA8", font: { size: 11 } },
          title: { display: true, text: "Median travel time to nearest non-selective school (minutes)", color: "#8B8FA8" },
          suggestedMax: 12 // Ensures the grid goes out to 12 like the image
        },
        y: {
          grid: { display: false },
          ticks: { color: "#E8E4D9", font: { family: "sans-serif", size: 11 } }
        }
      },
      plugins: {
        legend: {
          position: "bottom",
          align: "end", // Pushes the legend to the right side
          labels: { color: "#E8E4D9", usePointStyle: true, boxWidth: 8, padding: 20 }
        },
        tooltip: {
          backgroundColor: "#1E2240",
          titleColor: "#E8E4D9",
          bodyColor: "#E8E4D9",
          borderColor: "rgba(255,255,255,0.12)",
          borderWidth: 1,
          callbacks: {
            label: (item) => ` ${item.dataset.label}: ${item.raw} min`
          }
        }
      }
    },
    plugins: [medianLinePlugin] // Activate our custom dashed line
  });
}