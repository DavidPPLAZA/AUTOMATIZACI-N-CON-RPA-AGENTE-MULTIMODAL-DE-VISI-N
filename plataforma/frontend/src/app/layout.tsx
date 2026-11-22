import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Suspense } from "react";
import "./globals.css";
import Cabecera from "@/components/Cabecera";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Automatizando la automatización",
  description:
    "Agente orquestador con herramientas de clics y herramientas de visión para diseñar automatizaciones deterministas y auditables.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="es"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col font-sans">
        <Suspense fallback={<div className="h-14 border-b border-borde" />}>
          <Cabecera />
        </Suspense>
        <main className="flex-1 w-full max-w-6xl mx-auto px-5 py-8">{children}</main>
        <footer className="w-full max-w-6xl mx-auto px-5 py-6 text-xs text-tenue">
          Agente + RPA + Visión · banco de pruebas: GestCorp 98
        </footer>
      </body>
    </html>
  );
}
