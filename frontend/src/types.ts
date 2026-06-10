export interface PredictionResponse {
  success: boolean;
  prediction?: string;
  confidence?: number;
  full_sentence?: string;
  error?: string;
}