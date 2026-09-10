import React, { useEffect, useState, useContext } from 'react';
import { api } from '../services/api';
import { AuthContext } from '../context/AuthContext';
import { BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import { LogOut, Activity, Users, AlertTriangle, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Metrics {
    total_dias_ausencia: number;
    casos_riesgo_alto: number;
    ausentismo_por_categoria: { categoria: string, dias: number }[];
}

export const Dashboard = () => {
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [medicalHistory, setMedicalHistory] = useState<any[]>([]);
    const [searchId, setSearchId] = useState('EMP-006'); // Empleado por defecto para demo
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();

    useEffect(() => {
        // Cargar métricas (Pilar C)
        api.get('/dashboard/metrics').then(res => {
            setMetrics(res.data.metricas);
        }).catch(err => console.error(err));
    }, []);

    const fetchHistory = () => {
        // Cargar historia médica (Pilar A)
        api.get(`/employees/${searchId}/history`).then(res => {
            setMedicalHistory(res.data);
        }).catch(err => alert("Error o acceso denegado"));
    };

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    if (!metrics) return <div className="p-10 text-center">Cargando métricas...</div>;

    const isLider = user?.rol === 'LIDER_HRBP';

    return (
        <div className="min-h-screen bg-gray-100">
            {/* Navbar */}
            <nav className="bg-white shadow-sm p-4 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <Activity className="text-blue-600" />
                    <h1 className="text-xl font-bold text-gray-800">SuperApp SST</h1>
                </div>
                <div className="flex items-center gap-4">
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-bold">
                        Perfil: {user?.rol}
                    </span>
                    <button onClick={handleLogout} className="text-gray-500 hover:text-red-500 flex items-center gap-1">
                        <LogOut size={18} /> Salir
                    </button>
                </div>
            </nav>

            <div className="p-6 max-w-7xl mx-auto space-y-6">
                
                {/* PILAR C: MÉTRICAS (Visible para todos) */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 flex items-center gap-4">
                        <div className="bg-blue-100 p-3 rounded-full"><Users className="text-blue-600" /></div>
                        <div>
                            <p className="text-gray-500 text-sm">Días Acumulados de Ausentismo</p>
                            <h2 className="text-3xl font-bold">{metrics.total_dias_ausencia}</h2>
                        </div>
                    </div>
                    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 flex items-center gap-4">
                        <div className="bg-red-100 p-3 rounded-full"><AlertTriangle className="text-red-600" /></div>
                        <div>
                            <p className="text-gray-500 text-sm">Alertas Tempranas (Riesgo Alto)</p>
                            <h2 className="text-3xl font-bold">{metrics.casos_riesgo_alto}</h2>
                        </div>
                    </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
                    <h2 className="text-lg font-bold mb-4">Ausentismo por Categoría de Salud</h2>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={metrics.ausentismo_por_categoria}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="categoria" />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="dias" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* PILAR A: RBAC (Historia Clínica) */}
                <div className={`p-6 rounded-lg shadow-sm border ${isLider ? 'bg-white border-gray-200' : 'bg-red-50 border-red-200'}`}>
                    <div className="flex justify-between items-center mb-4">
                        <h2 className={`text-lg font-bold flex items-center gap-2 ${isLider ? 'text-gray-800' : 'text-red-700'}`}>
                            <FileText />
                            Buscador de Historia Clínica {isLider ? '(Vista Agregada)' : '(Vista Confidencial Médica)'}
                        </h2>
                    </div>
                    
                    <div className="flex gap-2 mb-4">
                        <input 
                            type="text" 
                            className="border p-2 rounded w-64"
                            value={searchId}
                            onChange={(e) => setSearchId(e.target.value)}
                            placeholder="Ej. EMP-006"
                        />
                        <button onClick={fetchHistory} className="bg-blue-600 text-white px-4 py-2 rounded">
                            Buscar
                        </button>
                    </div>

                    {medicalHistory.length > 0 && (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="bg-gray-100 text-gray-600 text-sm">
                                        <th className="p-3 border-b">Código</th>
                                        <th className="p-3 border-b">Fecha Inicio</th>
                                        <th className="p-3 border-b">Días</th>
                                        <th className="p-3 border-b">Categoría</th>
                                        <th className="p-3 border-b">Diagnóstico Médico</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {medicalHistory.map((h, i) => (
                                        <tr key={i} className="border-b hover:bg-gray-50 text-sm">
                                            <td className="p-3 font-mono text-xs">{h.cod_registro}</td>
                                            <td className="p-3">{h.fecha_inicio_incapacidad}</td>
                                            <td className="p-3 font-bold">{h.dias_ausencia}</td>
                                            <td className="p-3">{h.categoria_salud}</td>
                                            <td className="p-3">
                                                {h.diagnostico_medico_confidencial === '*** ENMASCARADO ***' ? (
                                                    <span className="bg-gray-200 text-gray-500 px-2 py-1 rounded text-xs font-bold">
                                                        *** CENSURADO ***
                                                    </span>
                                                ) : (
                                                    <span className="text-red-600 font-semibold">
                                                        {h.diagnostico_medico_confidencial}
                                                    </span>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

            </div>
        </div>
    );
};
