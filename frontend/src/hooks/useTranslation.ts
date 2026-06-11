import { useState, useCallback } from 'react';
import axios from 'axios';
import { API_BASE, TranslationResult } from '../types';

export const useTranslation = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const translateAudio = useCallback(async (
    audioBlob: Blob,
    sourceLang: string,
    targetLang: string
  ): Promise<TranslationResult> => {
    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('audio', audioBlob, 'speech.webm');
    formData.append('source_lang', sourceLang);
    formData.append('target_lang', targetLang);

    try {
      const response = await axios.post(`${API_BASE}/interpret`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      return response.data;
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Translation failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    translateAudio
  };
};