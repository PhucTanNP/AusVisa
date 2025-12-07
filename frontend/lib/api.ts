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
 * Stream chat message with real-time response
 */
export async function streamChatMessage(
    question: string,
    onChunk: (chunk: string) => void,
    onComplete: () => void,
    onError: (error: Error) => void
): Promise<void> {
    try {
        const response = await fetch(`${API_URL}/api/chatbot/query-stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ question }),
        })

        if (!response.ok) {
            throw new Error('Failed to start streaming')
        }

        const reader = response.body?.getReader()
        const decoder = new TextDecoder()

        if (!reader) {
            throw new Error('No response body')
        }

        while (true) {
            const { done, value } = await reader.read()

            if (done) {
                onComplete()
                break
            }

            const chunk = decoder.decode(value, { stream: true })
            const lines = chunk.split('\n')

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6) // Remove 'data: ' prefix

                    if (data === '[DONE]') {
                        onComplete()
                        return
                    }

                    if (data) {
                        try {
                            const parsed = JSON.parse(data)
                            if (parsed.text) {
                                onChunk(parsed.text)
                            }
                        } catch (e) {
                            // Fallback for plain text
                            onChunk(data)
                        }
                    }
                }
            }
        }
    } catch (error) {
        onError(error instanceof Error ? error : new Error('Unknown streaming error'))
    }
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

// ============= Admin API Functions =============

export interface UserWithStats {
    id: number
    email: string
    username: string
    full_name: string | null
    role: string
    is_active: boolean
    created_at: string
    updated_at: string | null
    last_login: string | null
    session_count: number
}

export interface UserStats {
    total_users: number
    active_users: number
    pending_users: number
    suspended_users: number
}

export interface Neo4jGraphData {
    nodes: Array<{
        id: string
        label: string
        type: string
        x: number
        y: number
    }>
    edges: Array<{
        from: string
        to: string
    }>
}

export interface Neo4jStats {
    node_counts: Array<{ label: string; count: number }>
    rel_counts: Array<{ type: string; count: number }>
}

/**
 * Get Neo4j graph statistics (admin only)
 */
export async function getNeo4jStats(): Promise<Neo4jStats> {
    const token = getAuthToken()
    if (!token) throw new Error('Not authenticated')

    const response = await fetch(`${API_URL}/api/admin/neo4j/stats`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || 'Failed to get graph stats')
    }

    return response.json()
}

/**
 * Get authentication token from localStorage
 */
function getAuthToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem('token')
}

/**
 * Get all users (admin only)
 */
export async function getAdminUsers(): Promise<UserWithStats[]> {
    const token = getAuthToken()
    if (!token) throw new Error('Not authenticated')

    const response = await fetch(`${API_URL}/api/admin/users`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || 'Failed to get users')
    }

    return response.json()
}

/**
 * Get user statistics (admin only)
 */
export async function getAdminStats(): Promise<UserStats> {
    const token = getAuthToken()
    if (!token) throw new Error('Not authenticated')

    const response = await fetch(`${API_URL}/api/admin/stats`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || 'Failed to get stats')
    }

    return response.json()
}

/**
 * Update user status (admin only)
 */
export async function updateUserStatus(userId: number, isActive: boolean): Promise<void> {
    const token = getAuthToken()
    if (!token) throw new Error('Not authenticated')

    const response = await fetch(`${API_URL}/api/admin/users/${userId}/status`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_active: isActive }),
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || 'Failed to update user status')
    }
}

/**
 * Update user role (admin only)
 */
export async function updateUserRole(userId: number, role: string): Promise<void> {
    const token = getAuthToken()
    if (!token) throw new Error('Not authenticated')

    const response = await fetch(`${API_URL}/api/admin/users/${userId}/role`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ role }),
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || 'Failed to update user role')
    }
}

/**
 * Delete user (admin only)
 */
export async function deleteUser(userId: number): Promise<void> {
    const token = getAuthToken()
    if (!token) throw new Error('Not authenticated')

    const response = await fetch(`${API_URL}/api/users/${userId}`, {
        method: 'DELETE',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || 'Failed to delete user')
    }
}

/**
 * Get Neo4j graph data (admin only)
 */
export async function getNeo4jGraph(): Promise<Neo4jGraphData> {
    const token = getAuthToken()
    if (!token) throw new Error('Not authenticated')

    const response = await fetch(`${API_URL}/api/admin/neo4j/graph`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || 'Failed to get graph data')
    }

    return response.json()
}

// ============= Authentication API Functions =============

export interface LoginRequest {
    email: string
    password: string
}

export interface RegisterRequest {
    email: string
    username: string
    password: string
    full_name?: string
}

export interface LoginResponse {
    access_token: string
    token_type: string
    user: UserWithStats
}

/**
 * Login user
 */
export async function login(email: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${API_URL}/api/users/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || 'Login failed')
    }

    return response.json()
}

/**
 * Register new user
 */
export async function register(data: RegisterRequest): Promise<UserWithStats> {
    const response = await fetch(`${API_URL}/api/users/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || 'Registration failed')
    }

    return response.json()
}

/**
 * Get current user info
 */
export async function getCurrentUser(): Promise<UserWithStats> {
    const token = getAuthToken()
    if (!token) throw new Error('Not authenticated')

    const response = await fetch(`${API_URL}/api/users/me`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        },
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(error.detail || 'Failed to get user info')
    }

    return response.json()
}
