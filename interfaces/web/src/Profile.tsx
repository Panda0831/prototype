import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  User,
  Mail,
  Key,
  Shield,
  Bell,
  LogOut,
  LayoutDashboard,
  Trees,
  Fingerprint,
  MapPin,
  Leaf,
} from 'lucide-react';
import { agriService } from './services/api';
import './dashboard.css';
import './profile.css';

const ROLE_LABELS: Record<string, string> = {
  PLANTEUR: 'Planteur',
  COLLECTEUR: 'Collecteur',
  EXPORTATEUR: 'Exportateur',
  CITOYEN: 'Citoyen',
};

export default function Profile() {
  const navigate = useNavigate();
  const userStr = localStorage.getItem('user');
  if (!userStr) {
    return null;
  }
  const user = JSON.parse(userStr);
  const [lots, setLots] = useState<any[]>([]);

  useEffect(() => {
    agriService
      .getAllLots()
      .then((data: any[]) => {
        const normalize = (k: string) => String(k || '').replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
        const mine = data.filter((lot) => normalize(lot.owner_id) === normalize(user.public_key));
        setLots(mine.slice(-3).reverse());
      })
      .catch(() => setLots([]));
  }, [user.public_key]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/auth');
  };

  const role = ROLE_LABELS[user.role] || user.role || 'Citoyen';

  return (
    <div className="dashboard-wrapper">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <Link to="/" className="sidebar-logo">HAZO LOVA</Link>

        <nav className="nav-group">
          <Link to="/dashboard" className="nav-item">
            <LayoutDashboard className="nav-icon" /> Dashboard
          </Link>
          <Link to="/profile" className="nav-item active">
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
            <div className="pre-title" style={{ fontSize: '10px', color: 'var(--or)', letterSpacing: '2px', fontWeight: 900, marginBottom: '4px' }}>MON COMPTE</div>
            <h1>Identité numérique</h1>
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
          <div className="profile-grid">
            {/* CARTE D'IDENTITÉ */}
            <div className="profile-main-card">
              <div className="profile-header-info">
                <div className="profile-avatar-large">
                  {user.username?.charAt(0) || 'U'}
                </div>
                <div className="profile-titles">
                  <h2>{user.username}</h2>
                  <p className="user-role">{role} — Réseau Hazo Lova</p>
                </div>
              </div>

              <div className="info-rows">
                <div className="info-row">
                  <div className="info-label"><Mail size={14} /> Adresse Email</div>
                  <div className="info-value">{user.email || 'Non renseigné'}</div>
                </div>
                <div className="info-row">
                  <div className="info-label"><MapPin size={14} /> District</div>
                  <div className="info-value">{user.district || 'Non renseigné'}</div>
                </div>
                <div className="info-row">
                  <div className="info-label"><Key size={14} /> Clé Publique (Signature)</div>
                  <div className="info-value-box">
                    <code>{user.public_key}</code>
                  </div>
                </div>
                <div className="info-row">
                  <div className="info-label"><Fingerprint size={14} /> ID Numérique</div>
                  <div className="info-value">HZL-USER-{user.public_key?.substring(2, 10).toUpperCase() || 'INCONNU'}</div>
                </div>
              </div>
            </div>

            {/* STATUT & PASSEPORTS */}
            <div className="profile-side-panels">
              <div className="security-status-card">
                <h3 className="section-title">Statut du compte</h3>
                <div className="security-tags">
                  <div className="sec-tag protected"><Shield size={12} /> Compte actif</div>
                  <div className="sec-tag protected"><Shield size={12} /> Clé ECDSA</div>
                  <div className="sec-tag protected"><Shield size={12} /> Rôle : {role}</div>
                </div>
              </div>

              <div className="recent-activity-card">
                <h3 className="section-title">Derniers passeports</h3>
                <div className="mini-activity-list">
                  {lots.length === 0 ? (
                    <p style={{ fontSize: '12px', opacity: 0.6 }}>
                      Aucun passeport scellé pour ce compte.
                    </p>
                  ) : (
                    lots.map((lot) => (
                      <div key={lot.id} className="mini-act-item">
                        <div className="mini-act-desc">
                          <Leaf size={12} /> {lot.id} · {lot.quality}
                        </div>
                        <div className="mini-act-time">{lot.district_origin} · {lot.weight} kg</div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
