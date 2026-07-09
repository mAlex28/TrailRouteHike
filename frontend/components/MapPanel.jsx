"use client";

import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { ACCENT_COLOR, DARK_COLOR } from "../lib/theme";

const UK_CENTER = [52.5, -2.2];
const UK_ZOOM = 6;
const TILE_URL = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png";
const TILE_ATTRIBUTION = "&copy; OpenStreetMap &copy; CARTO";

function makeIcons() {
  const trailIcon = L.divIcon({
    className: "",
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    html: `<div style="width:18px;height:18px;border-radius:50%;background:${ACCENT_COLOR};border:3px solid #fff;box-shadow:0 1px 5px rgba(0,0,0,.45)"></div>`,
  });
  const stationIcon = L.divIcon({
    className: "",
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    html: `<div style="width:13px;height:13px;background:${DARK_COLOR};border:3px solid #fff;box-shadow:0 1px 5px rgba(0,0,0,.45);transform:rotate(45deg)"></div>`,
  });
  return { trailIcon, stationIcon };
}

export default function MapPanel({ trail }) {
  const mapElRef = useRef(null);
  const mapRef = useRef(null);
  const groupRef = useRef(null);

  useEffect(() => {
    const map = L.map(mapElRef.current, { scrollWheelZoom: false, attributionControl: true }).setView(
      UK_CENTER,
      UK_ZOOM
    );
    L.tileLayer(TILE_URL, { attribution: TILE_ATTRIBUTION, subdomains: "abcd", maxZoom: 19 }).addTo(map);
    const group = L.layerGroup().addTo(map);
    mapRef.current = map;
    groupRef.current = group;

    const resizeTimer = setTimeout(() => map.invalidateSize(), 350);

    return () => {
      clearTimeout(resizeTimer);
      map.remove();
      mapRef.current = null;
      groupRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const group = groupRef.current;
    if (!map || !group) return;

    group.clearLayers();
    if (!trail) return;

    const { trailIcon, stationIcon } = makeIcons();
    L.polyline([trail.stationCoords, trail.trailCoords], {
      color: ACCENT_COLOR,
      weight: 3,
      opacity: 0.85,
      dashArray: "3 8",
    }).addTo(group);
    L.marker(trail.stationCoords, { icon: stationIcon })
      .addTo(group)
      .bindTooltip(trail.station, { direction: "top", offset: [0, -8], className: "tt-tip" });
    L.marker(trail.trailCoords, { icon: trailIcon })
      .addTo(group)
      .bindTooltip(trail.name, { direction: "top", offset: [0, -12], className: "tt-tip" });

    map.fitBounds([trail.stationCoords, trail.trailCoords], { padding: [70, 70], maxZoom: 11 });
  }, [trail]);

  return (
    <div className="tt-map-wrap">
      <div ref={mapElRef} className="tt-map" />
      {!trail && (
        <div className="tt-map-empty">No trail matches those filters — try widening your search.</div>
      )}
      <div className="tt-map-legend">
        <div className="tt-map-legend-row">
          <span className="tt-map-legend-dot" />
          Trailhead
        </div>
        <div className="tt-map-legend-row">
          <span className="tt-map-legend-diamond" />
          Nearest station
        </div>
      </div>
    </div>
  );
}
