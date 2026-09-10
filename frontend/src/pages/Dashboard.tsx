import { useEffect, useState, useContext } from 'react';
import { api } from '../services/api';
import { AuthContext } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Users, AlertTriangle, Activity, LogOut, FileText, PlusCircle, Bell } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface Metrics {
    total_dias_ausencia: number;
    casos_riesgo_alto: number;
    ausentismo_por_categoria: { categoria: string, dias: number }[];
}

export const Dashboard = () => {
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [medicalHistory, setMedicalHistory] = useState<any[]>([]);
    const [employeeSurveys, setEmployeeSurveys] = useState<any[]>([]);
    const [detailedAlerts, setDetailedAlerts] = useState<any[]>([]);
    const [searchId, setSearchId] = useState('EMP-014'); // Empleado por defecto para demo
    const [popupAlerts, setPopupAlerts] = useState<any[]>([]);
    const { user, logout } = useContext(AuthContext);
    const navigate = useNavigate();

    const isLider = ['LIDER_HRBP', 'LIDER_AREA', 'RELACIONES_LABORALES'].includes(user?.rol || '');

    const fetchMetrics = () => {
        api.get('/dashboard/metrics').then(res => setMetrics(res.data.metricas)).catch(console.error);
    };

    const fetchDetailedAlerts = () => {
        if (!isLider) {
            api.get('/dashboard/alerts_details').then(res => setDetailedAlerts(res.data)).catch(console.error);
        }
    };

    useEffect(() => {
        fetchMetrics();
        fetchDetailedAlerts();
    }, [isLider]);

    const fetchHistory = () => {
        api.get(`/employees/${searchId}/history`).then(res => {
            setMedicalHistory(res.data);
        }).catch(err => {
            if (err.response?.status === 403) {
                alert("Acceso denegado: El Líder HRBP no tiene permisos para ver historias clínicas.");
            } else {
                alert("Error al buscar el empleado.");
            }
        });

        if (!isLider) {
            api.get(`/employees/${searchId}/surveys`).then(res => {
                setEmployeeSurveys(res.data);
            }).catch(console.error);
        }
    };

    const handleSimulateIncapacity = () => {
        const dummyData = {
            fecha_inicio_incapacidad: new Date().toISOString().split('T')[0],
            dias_ausencia: 3,
            codigo_cie10: "M54.5",
            diagnostico_medico_confidencial: "Lumbago recurrente",
            categoria_salud: "Trauma / osteomuscular",
            entidad_expedidora: "EPS Sura"
        };
        api.post(`/employees/${searchId}/incapacities`, dummyData)
           .then(res => {
               fetchMetrics();
               fetchHistory();
               fetchDetailedAlerts();
               
               if (res.data.alertas_detonadas && res.data.alertas_detonadas.length > 0) {
                   setPopupAlerts(res.data.alertas_detonadas);
               } else {
                   alert("Incapacidad registrada correctamente. No se generaron alertas de riesgo.");
               }
           }).catch(err => alert("Error al registrar incapacidad. Verifique permisos."));
    };

    const handleLogout = () => {
        logout();
        navigate('/');
    };

    if (!metrics) return <div className="p-10 text-center font-bold text-gray-500">Cargando métricas en tiempo real...</div>;

    return (
        <div className="min-h-screen bg-gray-100 relative">
            
            {/* Modal de Alertas (Popup Flotante) */}
            {popupAlerts.length > 0 && (
                <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
                    <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full overflow-hidden border-2 border-red-500 animate-in fade-in zoom-in duration-300">
                        <div className="bg-red-600 p-4 flex items-center gap-3 text-white">
                            <AlertTriangle size={28} />
                            <h2 className="text-xl font-bold">¡ALERTA AUTOMÁTICA DETECTADA!</h2>
                        </div>
                        <div className="p-6 space-y-4">
                            {popupAlerts.map((alerta, i) => (
                                <div key={i} className="bg-red-50 border border-red-200 p-4 rounded-lg">
                                    <span className={`inline-block text-white text-xs px-2 py-1 rounded font-bold mb-2 ${alerta.nivel === 'CRÍTICO' ? 'bg-purple-600' : 'bg-red-600'}`}>
                                        NIVEL: {alerta.nivel}
                                    </span>
                                    <p className="text-red-900 font-medium">{alerta.motivo}</p>
                                </div>
                            ))}
                            <button 
                                onClick={() => setPopupAlerts([])} 
                                className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-3 rounded-lg transition-colors"
                            >
                                Entendido
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Navbar */}
            <nav className="bg-white shadow-sm p-4 flex justify-between items-center sticky top-0 z-40">
                <div className="flex items-center gap-2">
                    <Activity className="text-blue-600" />
                    <h1 className="text-xl font-bold text-gray-800">SuperApp SST</h1>
                </div>
                <div className="flex items-center gap-4">
                    <span className={`px-4 py-1 rounded-full text-sm font-bold ${isLider ? 'bg-indigo-100 text-indigo-800' : 'bg-emerald-100 text-emerald-800'}`}>
                        Perfil Activo: {user?.rol}
                    </span>
                    <button onClick={handleLogout} className="text-gray-500 hover:text-red-500 flex items-center gap-1 font-medium transition-colors">
                        <LogOut size={18} /> Salir
                    </button>
                </div>
            </nav>

            <div className="p-6 max-w-7xl mx-auto space-y-8">
                
                {/* PILAR C: MÉTRICAS GENERALES */}
                <section>
                    <h2 className="text-lg font-bold text-gray-700 mb-4">Panel de Control (Vista General)</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex items-center gap-5 hover:shadow-md transition-shadow">
                            <div className="bg-blue-100 p-4 rounded-full"><Users size={32} className="text-blue-600" /></div>
                            <div>
                                <p className="text-gray-500 text-sm font-medium uppercase tracking-wide">Días Acumulados de Ausentismo</p>
                                <h2 className="text-4xl font-black text-gray-800">{metrics.total_dias_ausencia}</h2>
                            </div>
                        </div>
                        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex items-center gap-5 hover:shadow-md transition-shadow">
                            <div className="bg-red-100 p-4 rounded-full"><AlertTriangle size={32} className="text-red-600" /></div>
                            <div>
                                <p className="text-gray-500 text-sm font-medium uppercase tracking-wide">Alertas de Riesgo Alto</p>
                                <h2 className="text-4xl font-black text-gray-800">{metrics.casos_riesgo_alto}</h2>
                            </div>
                        </div>
                    </div>
                </section>

                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
                    <h2 className="text-lg font-bold mb-6 text-gray-700">Distribución de Ausentismo por Categoría</h2>
                    <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={metrics.ausentismo_por_categoria}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                                <XAxis dataKey="categoria" tick={{fill: '#6b7280', fontSize: 12}} />
                                <YAxis tick={{fill: '#6b7280', fontSize: 12}} />
                                <Tooltip cursor={{fill: '#f3f4f6'}} contentStyle={{borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'}} />
                                <Bar dataKey="dias" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* PILAR B: BANDEJA DE ALERTAS DEL MÉDICO */}
                {!isLider && (
                    <section className="bg-white p-6 rounded-xl shadow-sm border border-red-200">
                        <h2 className="text-lg font-bold flex items-center gap-2 text-red-700 mb-4">
                            <Bell /> Bandeja de Alertas Clínicas (Exclusivo Médico)
                        </h2>
                        {detailedAlerts.length === 0 ? (
                            <p className="text-gray-500 text-sm">No hay alertas activas en el sistema.</p>
                        ) : (
                            <div className="overflow-x-auto">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="bg-red-50 text-red-800 text-xs uppercase tracking-wider">
                                            <th className="p-3 border-b border-red-100 rounded-tl-lg">Fecha</th>
                                            <th className="p-3 border-b border-red-100">Empleado</th>
                                            <th className="p-3 border-b border-red-100">Cargo</th>
                                            <th className="p-3 border-b border-red-100">Nivel</th>
                                            <th className="p-3 border-b border-red-100 rounded-tr-lg">Motivo y Correlación</th>
                                        </tr>
                                    </thead>
                                    <tbody className="text-sm">
                                        {detailedAlerts.map((a, i) => (
                                            <tr key={i} className="border-b border-gray-100 hover:bg-gray-50">
                                                <td className="p-3 text-gray-500">{a.fecha_alerta}</td>
                                                <td className="p-3 font-bold text-gray-800">
                                                    {a.nombre_empleado} <br/><span className="text-xs text-gray-400 font-mono">{a.empleado_id}</span>
                                                </td>
                                                <td className="p-3 text-gray-600">{a.cargo}</td>
                                                <td className="p-3">
                                                    <span className={`px-2 py-1 rounded text-xs font-bold text-white ${a.nivel_riesgo === 'CRÍTICO' ? 'bg-purple-600' : 'bg-red-500'}`}>
                                                        {a.nivel_riesgo}
                                                    </span>
                                                </td>
                                                <td className="p-3 text-gray-700 max-w-md">{a.motivo}</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </section>
                )}

                {/* PILAR A: RBAC (Historia Clínica) */}
                <section className={`p-6 rounded-xl shadow-sm border ${isLider ? 'bg-white border-gray-200' : 'bg-emerald-50 border-emerald-200'}`}>
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
                        <div>
                            <h2 className={`text-lg font-bold flex items-center gap-2 ${isLider ? 'text-gray-800' : 'text-emerald-800'}`}>
                                <FileText /> 
                                Gestión de Historias Clínicas {isLider ? '(Acceso Bloqueado)' : '(Acceso Médico Total)'}
                            </h2>
                            <p className="text-sm text-gray-500 mt-1">
                                {isLider 
                                    ? "Por protección de datos, RRHH no puede ver detalles clínicos ni crear incapacidades." 
                                    : "Busca un empleado para ver su historial en claro o simular una nueva incapacidad."}
                            </p>
                        </div>
                    </div>
                    
                    <div className="flex flex-wrap gap-3 mb-6">
                        <input 
                            type="text" 
                            className="border border-gray-300 p-2.5 rounded-lg w-64 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                            value={searchId}
                            onChange={(e) => setSearchId(e.target.value)}
                            placeholder="Ej. EMP-014"
                        />
                        <button 
                            onClick={fetchHistory} 
                            className="bg-gray-800 hover:bg-gray-900 text-white px-5 py-2.5 rounded-lg font-medium transition-colors"
                        >
                            Buscar Historial
                        </button>
                        
                        {!isLider && (
                            <button 
                                onClick={handleSimulateIncapacity} 
                                className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2.5 rounded-lg font-bold flex items-center gap-2 transition-colors ml-auto shadow-sm"
                            >
                                <PlusCircle size={18} /> Registrar Incapacidad (Demo Motor)
                            </button>
                        )}
                    </div>

                    {medicalHistory.length > 0 && (
                        <div className="overflow-x-auto rounded-lg border border-gray-200">
                            <table className="w-full text-left border-collapse bg-white">
                                <thead>
                                    <tr className="bg-gray-50 text-gray-600 text-xs uppercase tracking-wider">
                                        <th className="p-4 border-b">Código</th>
                                        <th className="p-4 border-b">Fecha Inicio</th>
                                        <th className="p-4 border-b">Días</th>
                                        <th className="p-4 border-b">Categoría</th>
                                        <th className="p-4 border-b">Diagnóstico Médico</th>
                                    </tr>
                                </thead>
                                <tbody className="text-sm">
                                    {medicalHistory.map((h, i) => (
                                        <tr key={i} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                                            <td className="p-4 font-mono text-xs text-gray-500">{h.cod_registro}</td>
                                            <td className="p-4 text-gray-700">{h.fecha_inicio_incapacidad}</td>
                                            <td className="p-4 font-black text-gray-800">{h.dias_ausencia}</td>
                                            <td className="p-4 text-gray-600">{h.categoria_salud}</td>
                                            <td className="p-4">
                                                <span className="text-emerald-700 font-bold bg-emerald-50 px-2 py-1 rounded border border-emerald-100">
                                                    {h.diagnostico_medico_confidencial}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}

                    {/* Historial de Encuestas (Pilar A - Médico) */}
                    {employeeSurveys.length > 0 && !isLider && (
                        <div className="mt-8">
                            <h3 className="text-md font-bold flex items-center gap-2 text-emerald-800 mb-4">
                                <FileText size={18} /> Historial de Autoreporte de Síntomas
                            </h3>
                            <div className="overflow-x-auto rounded-lg border border-gray-200">
                                <table className="w-full text-left border-collapse bg-white">
                                    <thead>
                                        <tr className="bg-gray-50 text-gray-600 text-xs uppercase tracking-wider">
                                            <th className="p-4 border-b">Código Encuesta</th>
                                            <th className="p-4 border-b">Fecha</th>
                                            <th className="p-4 border-b">Síntomas Reportados</th>
                                            <th className="p-4 border-b">Nivel Dolor</th>
                                            <th className="p-4 border-b">Requiere Valoración</th>
                                        </tr>
                                    </thead>
                                    <tbody className="text-sm">
                                        {employeeSurveys.map((s, i) => (
                                            <tr key={i} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
                                                <td className="p-4 font-mono text-xs text-gray-500">{s.id_respuesta}</td>
                                                <td className="p-4 text-gray-700">{s.fecha_encuesta}</td>
                                                <td className="p-4 text-gray-800">
                                                    <span className="font-semibold text-gray-900">{s.sintoma_principal}</span>
                                                    <br/>
                                                    <span className="text-xs text-gray-500">Peligro: {s.peligro_identificado}</span>
                                                </td>
                                                <td className="p-4">
                                                    <span className={`px-2 py-1 rounded font-bold text-white text-xs ${s.nivel_dolor_percibido >= 7 ? 'bg-red-500' : s.nivel_dolor_percibido >= 4 ? 'bg-yellow-500' : 'bg-emerald-500'}`}>
                                                        {s.nivel_dolor_percibido} / 10
                                                    </span>
                                                </td>
                                                <td className="p-4">
                                                    {s.requiere_valoracion_medica ? (
                                                        <span className="text-red-700 font-bold bg-red-50 px-2 py-1 rounded border border-red-100">Sí</span>
                                                    ) : (
                                                        <span className="text-gray-500">No</span>
                                                    )}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                </section>

            </div>
        </div>
    );
};
