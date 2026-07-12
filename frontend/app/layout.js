import { Spectral, Inter, IBM_Plex_Mono } from "next/font/google"
import "./globals.css"

const inter = Inter({
  variable: "--font-sans",
  subsets: ["latin"],
})

export const metadata = {
  title: "TrackAndTrail — train-accessible hikes across the UK",
  description:
    "Find UK hiking trails you can reach by train. Enter a location, pick a difficulty, and get a trail plus the nearest station.",
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>{children}</body>
    </html>
  )
}
