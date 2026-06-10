import axios from 'axios';
import { PredictionResponse } from '../types';

import type { PredictionResponse } from '../types';   // <-- type-only import
import { PredictionResponse } from './types'; 
const API_BASE = 'http://localhost:8000/api';

export const predictVideo = async (
  videoBlob: Blob,
  currentSentence: string
): Promise<PredictionResponse> => {
  const formData = new FormData();
  formData.append('video', videoBlob, 'recording.mp4');
  formData.append('current_sentence', currentSentence);

  const response = await axios.post<PredictionResponse>(
    `${API_BASE}/predict`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000, // 30 seconds
    }
  );
  return response.data;
};