/**
 * API service for communicating with AKE_BE backend
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ChatRequest {
    question: string
}

export interface ChatResponse {
    response: string
    intent?: string
}

export interface StatsResponse {
    universities: number
    programs: number
    visas: number
}

/**
 * Send a chat message to the chatbot
 */
export async function sendChatMessage(question: string): Promise<ChatResponse> {
    const response = await fetch(`${API_URL}/api/chatbot/query`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || 'Failed to send message')
    }

    return response.json()
}

/**
 * Get system statistics
 */
export async function getStats(): Promise<StatsResponse> {
    const response = await fetch(`${API_URL}/api/chatbot/stats`)

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || 'Failed to get stats')
    }

    return response.json()
}

/**
 * Check chatbot health
 */
export async function checkHealth(): Promise<{ status: string; neo4j: string }> {
    const response = await fetch(`${API_URL}/api/chatbot/health`)

    if (!response.ok) {
        throw new Error('Health check failed')
    }

    return response.json()
}
