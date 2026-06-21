import type { Metadata } from "next";
import { Cinzel, Cormorant_Garamond, Inter, Orbitron, Space_Grotesk } from "next/font/google";
import "./globals.css";
import "../styles/rudra-prime.css";

const cinzel = Cinzel({
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  variable: "--font-cinzel",
  display: "swap",
});

const orbitron = Orbitron({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-orbitron",
  display: "swap",
});

const cormorant = Cormorant_Garamond({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  style: ["normal", "italic"],
  variable: "--font-cormorant",
  display: "swap",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-space",
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL ?? "https://rudra-kl5i.vercel.app"),
  title: "RUDRA — Prime",
  description:
    "Rudra Prime — cosmic command deck with voice-armed counsel, nine Navagraha planets, and the Trishul at the still point.",
  icons: { icon: "/trishula-icon.png", apple: "/trishula-icon.png" },
  openGraph: {
    title: "RUDRA — Prime",
    description: "Nine planets, one trident, voice-armed counsel. Local-first personal intelligence.",
    images: [{ url: "/rudra-prime-reference.png", width: 1920, height: 1080, alt: "Rudra Prime" }],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "RUDRA — Prime",
    description: "Nine planets, one trident, voice-armed counsel.",
    images: ["/rudra-prime-reference.png"],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`dark ${cinzel.variable} ${inter.variable} ${spaceGrotesk.variable} ${orbitron.variable} ${cormorant.variable}`}
    >
      <body className="font-display">{children}</body>
    </html>
  );
}
