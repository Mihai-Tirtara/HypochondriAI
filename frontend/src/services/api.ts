import axios from 'axios';

// Define API base URL - change this to match your Spring Boot backend
const API_BASE_URL = 'http://localhost:8000';

// Define types
export interface SymptomRequest {
  symptoms: string;
  userContext?: string;
}

export interface SymptomResponse {
  response: string;

}

// API function to analyze symptoms
export const analyzeSymptoms = async (request: SymptomRequest): Promise<SymptomResponse> => {
  try {
    const response = await axios.post(`${API_BASE_URL}/analyse`, request, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    return response.data;
  } catch (error) {
    console.error('Error analyzing symptoms:', error);
    throw error;
  }
};
