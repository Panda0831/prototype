import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  LayoutDashboard, 
  User,
  Trees, 
  LogOut, 
  Bell, 
  ChevronRight,
  TrendingUp,
  ShieldCheck,
  Brain
} from 'lucide-react';
import { blockchainService, agriService } from './services/api';

export default function Dashboard() {
  const navigate = useNavigate();
  const userStr = localStorage.getItem('user');
  if (!userStr) {
    // Ne devrait pas arriver avec ProtectedRoute mais par sécurité
    return null;
  }
  const user = JSON.parse(userStr);
  const [brainInfo, setBrainInfo] = useState<any>(null);
  const [realStats, setRealStats] = useState({
    blocks: 0,
    lots: 0,
    volume: 0,
    modelMae: null as number | null,
    modelR2: null as number | null
  });

  useEffect(() => {
    blockchainService.getBrainInfo().then(setBrainInfo).catch(console.error);
    
    const fetchRealData = async () => {
        try {
            const [blocks, lots, modelRes] = await Promise.all([
                blockchainService.getBlocks(),
                agriService.getAllLots(),
                agriService.getVanillaModelInfo().catch(() => null)
            ]);
            const priceMetrics = modelRes?.model?.metrics?.targets?.fair_farmgate_price_mga;
            setRealStats({ 
                blocks: blocks.length, 
                lots: lots.length,
                volume: lots.reduce((acc: number, l: any) => acc + (l.weight || 0), 0),
                modelMae: priceMetrics?.mae ?? null,
                modelR2: priceMetrics?.r2 ?? null
            });
        } catch (e) { console.error(e); }
    };
    fetchRealData();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/auth');
  };

  const stats = [
    { label: 'Blocs Validés', value: realStats.blocks.toString(), trend: 'Live', icon: <ShieldCheck size={20} /> },
    { label: 'Lots Traçés', value: realStats.lots.toString(), trend: 'Live', icon: <Trees size={20} /> },
    { label: 'Volume Vanille', value: `${realStats.volume.toFixed(1)} kg`, trend: 'Bord-champ', icon: <TrendingUp size={20} /> },
    {
      label: 'Modèle IA Local',
      value: realStats.modelR2 !== null ? `R² ${realStats.modelR2.toFixed(3)}` : 'Non entraîné',
      trend: realStats.modelMae !== null ? `MAE ${Math.round(realStats.modelMae).toLocaleString('fr-FR')} MGA/kg` : 'Lancer train_vanilla_ai.py',
      icon: <Brain size={20} />
    }
  ];

  const modules = [
    { 
      title: 'Vanille', 
      description: 'Analyse IA ISO 5565, passeport blockchain et routage A* des récoltes de vanille.', 
      icon: <Trees size={24} />, 
      path: '/agri',
      tag: 'HZ-AGRI'
    }
  ];

  return (
    <div className="dashboard-wrapper">
      
      {/* SIDEBAR */}
      <aside className="sidebar">
        <Link to="/" className="sidebar-logo">HAZO LOVA</Link>
        
        <nav className="nav-group">
          <Link to="/dashboard" className="nav-item active">
            <LayoutDashboard className="nav-icon" /> Dashboard
          </Link>
          <Link to="/profile" className="nav-item">
            <User className="nav-icon" /> Profil
          </Link>
          <Link to="/agri" className="nav-item">
            <Trees className="nav-icon" /> Vanille
          </Link>
        </nav>

        <div className="sidebar-footer">
          <button onClick={handleLogout} className="logout-btn">
            <LogOut size={18} /> Déconnexion
          </button>
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-content">
        <header className="top-bar">
          <div className="page-title-area">
            <div className="pre-title" style={{ fontSize: '10px', color: 'var(--or)', letterSpacing: '2px', fontWeight: 900, marginBottom: '4px' }}>HAZO LOVA AGRI-AI</div>
            <h1>Tableau de bord</h1>
          </div>
          
          <div className="user-status">
            <button className="nav-icon-btn" style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--navy)', opacity: 0.5 }}><Bell size={20} /></button>
            <Link to="/profile" style={{ textDecoration: 'none', color: 'inherit', display: 'flex', alignItems: 'center', gap: '20px' }}>
              <div className="profile-mini">
                <span className="username">{user.username}</span>
                <span className="public-key-hash">{user.public_key?.substring(0, 10)}...</span>
              </div>
              <div className="avatar-circle">
                {user.username?.charAt(0) || 'U'}
              </div>
            </Link>
          </div>
        </header>

        <div className="dashboard-content">
          {/* STATS */}
          <div className="stats-grid">
            {stats.map((stat, i) => (
              <div key={i} className="stat-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div className="stat-label">{stat.label}</div>
                  <div style={{ color: 'var(--emeraude)', opacity: 0.6 }}>{stat.icon}</div>
                </div>
                <div className="stat-value">{stat.value}</div>
                <div className="stat-trend">{stat.trend}</div>
              </div>
            ))}
          </div>

          <div className="dashboard-main-grid">
            {/* MODULES */}
            <div className="modules-area">
              <h2 className="section-title">Parcours de démonstration</h2>
              <div className="modules-grid">
                {modules.map((m, i) => (
                  <div key={i} className="module-card" onClick={() => navigate(m.path)}>
                    <div className="module-icon-box">{m.icon}</div>
                    <div className="module-tag" style={{ fontSize: '9px', fontWeight: 900, color: 'var(--or)', letterSpacing: '1px', marginBottom: '8px' }}>{m.tag}</div>
                    <h3>{m.title}</h3>
                    <p>{m.description}</p>
                    <div className="module-action">
                      Lancer le module <ChevronRight size={14} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* AI CONSENSUS MONITOR */}
            <div className="activity-area">
              <h2 className="section-title">Consensus blockchain</h2>
              <div id="ai-monitor" className="activity-list">
                 {brainInfo ? Object.entries(brainInfo).map(([state, info]: any) => (
                    <div key={state} className="activity-item" style={{display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center'}}>
                        <div>
                            <div className="act-type">{state}</div>
                            <div className="act-desc">{info.best_leader}</div>
                        </div>
                        <div className="act-time" style={{fontWeight: 800}}>{info.score.toFixed(1)}</div>
                    </div>
                 )) : <p style={{fontSize: '13px'}}>Chargement de l'intelligence réseau...</p>}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
