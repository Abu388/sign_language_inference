export interface Message {
  id: string;
  text: string;
  type: 'original' | 'translated';
  meta: string;
  timestamp: Date;
}

export interface TranslationResult {
  transcript: string;
  translated?: boolean;
  translated_text?: string;
  audio_b64?: string;
  error?: string;
}

export interface PredictionResponse {
  success: boolean;
  prediction?: string;
  confidence?: number;
  full_sentence?: string;
  error?: string;
}

export const API_BASE = 'http://localhost:8000/api';

export const LANGUAGES = [
  { code: 'am', name: 'Amharic (አማርኛ)' },
  { code: 'en', name: 'English' },
  { code: 'om', name: 'Afan Oromo' },
];

export const LANG_NAMES: Record<string, string> = {
  am: 'Amharic',
  en: 'English',
  om: 'Afan Oromo',
};