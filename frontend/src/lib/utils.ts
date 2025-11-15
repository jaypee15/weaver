import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatFileSize(bytes: number): string {
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString()
}

