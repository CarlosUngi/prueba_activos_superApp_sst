import React, { createContext, useState, useEffect } from 'react';
import { api } from '../services/api';

interface User {
    email: string;
    rol: string;
}

interface AuthContextProps {
    user: User | null;
    token: string | null;
    login: (token: string, rol: string) => void;
    logout: () => void;
}

export const AuthContext = createContext<AuthContextProps>({} as AuthContextProps);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [user, setUser] = useState<User | null>(null);
    const [token, setToken] = useState<string | null>(localStorage.getItem('token'));

    // Al iniciar, leemos el localStorage
    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        const storedRol = localStorage.getItem('rol');
        if (storedToken && storedRol) {
            setToken(storedToken);
            setUser({ email: 'usuario', rol: storedRol });
        }
    }, []);

    const login = (newToken: string, rol: string) => {
        localStorage.setItem('token', newToken);
        localStorage.setItem('rol', rol);
        setToken(newToken);
        setUser({ email: 'usuario', rol });
    };

    const logout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('rol');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
