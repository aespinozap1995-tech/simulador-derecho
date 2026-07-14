import type { Metadata } from "next";
import { Geist, Lora } from "next/font/google";
import "./globals.css";

const geist = Geist({ variable: "--font-sans", subsets: ["latin"] });
const lora = Lora({ variable: "--font-serif", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Aula Jurídica | Simulador de exámenes",
  description: "Practica Derecho con simulacros, consejos y retroalimentación sencilla.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body className={`${geist.variable} ${lora.variable}`}>{children}</body>
    </html>
  );
}
