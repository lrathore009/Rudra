import type { Metadata } from "next";
import { Cinzel, Inter } from "next/font/google";
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

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000"),
  title: "RUDRA — Rudraksha Intelligence",
  description:
    "Personal Intelligence OS — a living Rudraksha interface for Laxman's private command center.",
  icons: { icon: "/rudraksha-icon.svg", apple: "/rudraksha-icon.svg" },
  openGraph: {
    title: "RUDRA — Rudraksha Intelligence",
    description: "Nine facets, one voice. Local-first personal intelligence for Laxman.",
    images: [{ url: "/rudraksha-icon.svg", width: 64, height: 64, alt: "Rudraksha bead" }],
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "RUDRA — Rudraksha Intelligence",
    description: "Nine facets, one voice. Local-first personal intelligence.",
    images: ["/rudraksha-icon.svg"],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`dark ${cinzel.variable} ${inter.variable}`}>
      <body className="font-display">{children}</body>
    </html>
  );
}
