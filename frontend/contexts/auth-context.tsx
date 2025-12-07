"use client"

import { useRouter } from 'next/navigation'
import React, { createContext, useContext, useEffect, useState } from 'react'

interface User {
    id: number
    email: string
    username: string
    full_name: string | null
    role: string
    is_active: boolean
    created_at: string
    updated_at: string
}

interface AuthContextType {
    user: User | null
    token: string | null
    login: (email: string, password: string) => Promise<void>
    logout: () => void
    isLoading: boolean
    error: string | null
    clearError: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [token, setToken] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const router = useRouter()

    // Load user from token on mount
    useEffect(() => {
        const loadUser = async () => {
            const storedToken = localStorage.getItem('token')
            if (!storedToken) {
                setIsLoading(false)
                return
            }

            try {
                // Verify token and get user info
                const response = await fetch('http://localhost:8000/api/users/me', {
                    headers: {
                        'Authorization': `Bearer ${storedToken}`,
                    },
                })

                if (response.ok) {
                    const userData = await response.json()
                    setUser(userData)
                    setToken(storedToken)
                } else {
                    // Token is invalid, clear it
                    localStorage.removeItem('token')
                }
            } catch (err) {
                console.error('Failed to load user:', err)
                localStorage.removeItem('token')
            } finally {
                setIsLoading(false)
            }
        }

        loadUser()
    }, [])

    const login = async (email: string, password: string) => {
        setIsLoading(true)
        setError(null)

        try {
            const response = await fetch('http://localhost:8000/api/users/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, password }),
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || 'Đăng nhập thất bại')
            }

            const data = await response.json()

            // Store token and user
            localStorage.setItem('token', data.access_token)
            setToken(data.access_token)
            setUser(data.user)

            // Redirect based on role
            if (data.user.role === 'admin') {
                router.push('/admin')
            } else {
                router.push('/')
            }
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Đăng nhập thất bại'
            setError(errorMessage)
            throw err
        } finally {
            setIsLoading(false)
        }
    }

    const logout = () => {
        localStorage.removeItem('token')
        setToken(null)
        setUser(null)
        router.push('/login')
    }

    const clearError = () => {
        setError(null)
    }

    return (
        <AuthContext.Provider value={{ user, token, login, logout, isLoading, error, clearError }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
