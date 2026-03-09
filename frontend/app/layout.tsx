import { SessionProvider } from "next-auth/react";
import { AuthProvider } from "@/context/AuthContext";
import "./globals.css";
import { Kanit, Saira_Condensed } from "next/font/google";
import type { Metadata } from "next";

const kanit = Kanit({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600"],
  variable: "--font-sans",
  display: "swap",
});

const sairaCondensed = Saira_Condensed({
  subsets: ["latin"],
  weight: ["400", "600", "700", "800", "900"],
  variable: "--font-display",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Codebasics Practice Room",
  description: "Python & Data Practice Room by Codebasics",
  icons: {
    icon: "/assets/favicon.png",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${kanit.variable} ${sairaCondensed.variable} font-sans antialiased`} suppressHydrationWarning>
        <SessionProvider>
          <AuthProvider>{children}</AuthProvider>
        </SessionProvider>
      </body>
    </html>
  );
}
