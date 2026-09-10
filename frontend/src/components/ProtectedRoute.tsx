import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

export const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
    const { token } = useContext(AuthContext);

    if (!token) {
        // Si no hay token, lo mandamos al login
        return <Navigate to="/" replace />;
    }

    return children;
};
