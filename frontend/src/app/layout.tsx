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
  title: "RUDRA — Trishula Cosmos",
  description:
    "Personal Intelligence OS — a cosmic command deck where the trishula awakens and nine planets answer.",
  icons: { icon: "/trishula-icon.png", apple: "/trishula-icon.png" },
  openGraph: {
    title: "RUDRA — Trishula Cosmos",
    description: "Nine planets, one trident. Local-first personal intelligence for Laxman.",
    images: [{ url: "/trishula-icon.png", width: 512, height: 512, alt: "Rudra trishula" }],
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "RUDRA — Trishula Cosmos",
    description: "Nine planets, one trident. Local-first personal intelligence.",
    images: ["/trishula-icon.png"],
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
