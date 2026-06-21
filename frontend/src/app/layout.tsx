import type { Metadata } from "next";
import { Cinzel, Inter, Space_Grotesk } from "next/font/google";
import "./globals.css";

const cinzel = Cinzel({
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  variable: "--font-cinzel",
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
  title: "RUDRA PRIME — Trishula × Jarvis",
  description:
    "Personal Intelligence OS — Rudra Prime fuses Trishula cosmos with Jarvis voice engine. Nine Grahas, arc reactor core, local-first counsel.",
  icons: { icon: "/trishula-icon.png", apple: "/trishula-icon.png" },
  openGraph: {
    title: "RUDRA PRIME — Trishula × Jarvis",
    description: "Nine Grahas orbit the arc reactor. Local-first personal intelligence for Laxman.",
    images: [{ url: "/trishula-icon.png", width: 512, height: 512, alt: "Rudra Prime" }],
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "RUDRA PRIME — Trishula × Jarvis",
    description: "Trishula core · Jarvis engine · local-first counsel.",
    images: ["/trishula-icon.png"],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`dark ${cinzel.variable} ${inter.variable} ${spaceGrotesk.variable}`}>
      <body className="font-display">{children}</body>
    </html>
  );
}
