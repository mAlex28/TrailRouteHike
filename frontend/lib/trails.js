// Dummy trail dataset + matching logic (from the TrackAndTrail design
// prototype) so the frontend demonstrates the full search/plan/surprise
// flow standalone.

const trails = [
  {
    id: 'sdw',
    name: 'South Downs Way',
    location: 'Hampshire → East Sussex',
    difficulty: 'Moderate',
    distanceKm: 162.81,
    distanceMi: 101.2,
    station: 'Winchester',
    stationCoords: [51.067, -1.319],
    trailCoords: [51.0606, -1.329],
    keywords: ['southampton', 'winchester', 'hampshire', 'south downs', 'eastbourne', 'brighton', 'sussex'],
    description:
      "A 100-mile chalk ridgeway from Winchester to Eastbourne — long-distance views, thatched villages, and cosy tea rooms the whole way.",
  },
  {
    id: 'seven',
    name: 'Seven Sisters',
    location: 'East Sussex',
    difficulty: 'Easy',
    distanceKm: 13,
    distanceMi: 8.1,
    station: 'Eastbourne',
    stationCoords: [50.7686, 0.2837],
    trailCoords: [50.744, 0.152],
    keywords: ['eastbourne', 'seven sisters', 'sussex', 'brighton', 'seaford'],
    description:
      'Dramatic white chalk cliffs rising and falling above the Channel to the Cuckmere estuary. Wide skies, sea air, easy underfoot.',
  },
  {
    id: 'box',
    name: 'Box Hill',
    location: 'Surrey',
    difficulty: 'Easy',
    distanceKm: 11,
    distanceMi: 6.8,
    station: 'Box Hill & Westhumble',
    stationCoords: [51.256, -0.327],
    trailCoords: [51.249, -0.31],
    keywords: ['box hill', 'dorking', 'surrey', 'london', 'guildford', 'westhumble'],
    description:
      "A zig-zag climb to one of Surrey's finest viewpoints, past the Stepping Stones over the Mole and the wooded North Downs.",
  },
  {
    id: 'mam',
    name: 'Mam Tor & the Great Ridge',
    location: 'Peak District, Derbyshire',
    difficulty: 'Moderate',
    distanceKm: 12.5,
    distanceMi: 7.8,
    station: 'Edale',
    stationCoords: [53.366, -1.816],
    trailCoords: [53.349, -1.81],
    keywords: ['peak district', 'edale', 'mam tor', 'derbyshire', 'sheffield', 'manchester', 'castleton', 'hills'],
    description:
      "The 'Shivering Mountain' and the airy ridge to Lose Hill — a breezy, panoramic walk over the heart of the Peak District.",
  },
  {
    id: 'malvern',
    name: 'Malvern Hills',
    location: 'Worcestershire',
    difficulty: 'Moderate',
    distanceKm: 14,
    distanceMi: 8.7,
    station: 'Great Malvern',
    stationCoords: [52.109, -2.317],
    trailCoords: [52.079, -2.347],
    keywords: ['malvern', 'worcester', 'worcestershire', 'great malvern'],
    description:
      'A spine of ancient hills rising straight from the plain — springs, Iron Age forts, and views over nine counties on a clear day.',
  },
  {
    id: 'catbells',
    name: 'Catbells',
    location: 'Lake District, Cumbria',
    difficulty: 'Hard',
    distanceKm: 5.5,
    distanceMi: 3.4,
    station: 'Windermere',
    stationCoords: [54.381, -2.905],
    trailCoords: [54.566, -3.17],
    keywords: ['lake district', 'keswick', 'windermere', 'catbells', 'cumbria', 'derwent'],
    description:
      'A friendly little fell above Derwentwater — a proper summit with lake views, easily done in an afternoon.',
  },
  {
    id: 'penyfan',
    name: 'Pen y Fan',
    location: 'Brecon Beacons, Wales',
    difficulty: 'Hard',
    distanceKm: 16,
    distanceMi: 9.9,
    station: 'Merthyr Tydfil',
    stationCoords: [51.749, -3.378],
    trailCoords: [51.884, -3.436],
    keywords: ['brecon', 'pen y fan', 'wales', 'merthyr', 'beacons', 'bannau', 'cardiff'],
    description:
      'The highest peak in southern Britain — a steady pull to a flat-topped summit over the sweeping Brecon Beacons.',
  },
  {
    id: 'ilkley',
    name: 'Ilkley Moor',
    location: 'West Yorkshire',
    difficulty: 'Easy',
    distanceKm: 9,
    distanceMi: 5.6,
    station: 'Ilkley',
    stationCoords: [53.925, -1.822],
    trailCoords: [53.912, -1.827],
    keywords: ['ilkley', 'yorkshire', 'leeds', 'bradford', 'moor'],
    description:
      'Heather moorland above the spa town, past the Cow and Calf rocks and ancient cup-and-ring carvings.',
  },
  {
    id: 'arnside',
    name: 'Arnside Knott',
    location: 'Cumbria',
    difficulty: 'Easy',
    distanceKm: 6,
    distanceMi: 3.7,
    station: 'Arnside',
    stationCoords: [54.201, -2.835],
    trailCoords: [54.198, -2.848],
    keywords: ['arnside', 'cumbria', 'silverdale', 'lancaster', 'morecambe'],
    description:
      'A short limestone knoll above the Kent estuary — woodland, rare butterflies, and views to the Lakeland fells.',
  },
  {
    id: 'frensham',
    name: 'Frensham Ponds',
    location: 'Surrey',
    difficulty: 'Easy',
    distanceKm: 7,
    distanceMi: 4.3,
    station: 'Farnham',
    stationCoords: [51.215, -0.799],
    trailCoords: [51.156, -0.82],
    keywords: ['frensham', 'farnham', 'surrey', 'aldershot', 'guildford'],
    description:
      'Gentle heath and two big ponds near Farnham — sandy paths, dragonflies, and an easy loop straight from the station.',
  },
];

export function planTrail({ query, difficulty, shortOnly, surprise }) {
  const pool = trails.filter(
    (t) => (difficulty === 'all' || t.difficulty === difficulty) && (!shortOnly || t.distanceMi < 5)
  );
  if (!pool.length) return null;

  const q = (query || '').toLowerCase();
  const matched = pool.filter((t) => t.keywords.some((k) => q.includes(k)));
  const set = matched.length ? matched : pool;

  return surprise ? set[Math.floor(Math.random() * set.length)] : set[0];
}
