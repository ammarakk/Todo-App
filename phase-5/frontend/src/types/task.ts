export interface Task {
  id: string
  user_id: string
  title: string
  description?: string
  due_date?: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  tags: string[]
  status: 'active' | 'completed' | 'deleted'
  created_at: string
  updated_at: string
}

export interface ChatResponse {
  response: string
  intent_detected: string
  skill_agent_used: string
  confidence_score: number
  requires_clarification: boolean
  data?: {
    task_id?: string
    tasks?: Task[]
  }
}

export interface ChatRequest {
  user_input: string
  conversation_id?: string
}
