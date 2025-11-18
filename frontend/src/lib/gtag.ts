// frontend/src/lib/gtag.ts

export const GA_MEASUREMENT_ID = 'G-PFNYJ5DXPF';

// Declare gtag function to avoid TypeScript errors
declare global {
  interface Window {
    gtag: (...args: any[]) => void;
  }
}

export const pageview = (url: string) => {
  if (typeof window.gtag === 'function') {
    window.gtag('config', GA_MEASUREMENT_ID, {
      page_path: url,
    });
  }
};
