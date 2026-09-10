import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { AuthContext } from '../context/AuthContext';
import { Shield } from 'lucide-react';

export const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        try {
            // Ahora enviamos un JSON limpio porque simplificamos la API
            const response = await api.post('/auth/login', {
                email: email,
                password: password
            });
            
            // Decodificamos el JWT manualmente rápido (solo para el frontend visual)
            const token = response.data.access_token;
            const payload = JSON.parse(atob(token.split('.')[1]));
            
            login(token, payload.rol);
            navigate('/dashboard');
        } catch (err) {
            setError('Credenciales inválidas');
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="bg-white p-8 rounded-lg shadow-md w-96">
                <div className="flex flex-col items-center mb-6">
                    <Shield className="w-12 h-12 text-blue-600 mb-2" />
                    <h1 className="text-2xl font-bold text-gray-800">SuperApp SST</h1>
                    <p className="text-gray-500 text-sm">Acceso al Sistema</p>
                </div>
                
                {error && <div className="bg-red-100 text-red-600 p-2 rounded mb-4 text-sm text-center">{error}</div>}

                <form onSubmit={handleLogin}>
                    <div className="mb-4">
                        <label className="block text-gray-700 text-sm font-bold mb-2">Usuario</label>
                        <input 
                            type="text" 
                            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="lider@superapp.com"
                        />
                    </div>
                    <div className="mb-6">
                        <label className="block text-gray-700 text-sm font-bold mb-2">Contraseña</label>
                        <input 
                            type="password" 
                            className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="123456"
                        />
                    </div>
                    <button 
                        type="submit" 
                        className="w-full bg-blue-600 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 transition"
                    >
                        Ingresar
                    </button>
                </form>
                
                <div className="mt-6 text-xs text-gray-400 text-center">
                    <p>Usuarios de prueba:</p>
                    <p>lider@superapp.com (123456)</p>
                    <p>medico@superapp.com (123456)</p>
                </div>
            </div>
        </div>
    );
};
