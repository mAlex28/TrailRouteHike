import Image from "next/image";

export default function Header() {
  return (
    <div className="tt-topbar">
      <div className="tt-brand">
        <Image
          src="/logo.png"
          alt="TrackAndTrail logo"
          width={354}
          height={220}
          priority
          style={{ height: 34, width: "auto" }}
        />
        <div className="tt-brand-word">
          Track<em>&amp;</em>Trail
        </div>
      </div>
      <div className="tt-topbar-sub">Train-accessible hikes across the UK</div>
    </div>
  );
}