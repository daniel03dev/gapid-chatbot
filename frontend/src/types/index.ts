"""
Tipos TypeScript para el frontend.
"""

export interface Message {
  id: number;
  role: "user" | "assistant";
  role_display: string;
  content: string;
  created_at: string;
}

export interface Conversation {
  id: number;
  created_at: string;
  updated_at: string;
  messages?: Message[];
  message_count?: number;
}

export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export interface ChatRequest {
  conversation_id?: number;
  message: string;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  confidence_score: number;
}
