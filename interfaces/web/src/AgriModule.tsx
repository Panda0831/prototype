import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  LayoutDashboard, 
  User, 
  Trees, 
  Wallet, 
  Search, 
  LogOut, 
  Bell, 
  Navigation,
  Box,
  TrendingUp,
  Globe,
  ArrowRight,
  Leaf,
  DollarSign,
  Brain
} from 'lucide-react';
import { agriService, algoService, authService, notificationService } from './services/api';
import { BobModal } from './components/BobModal';
import VanillaLab from './VanillaLab';
import './dashboard.css';
import './vanilla.css';

export default function AgriModule() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  
  const [activeTab, setActiveTab] = useState<'datascience' | 'harvest' | 'tracking' | 'transport' | 'notifications'>('datascience');
  const [loading, setLoading] = useState(false);
  const [lots, setLots] = useState<any[]>([]);
  const [districts, setDistricts] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [modelInfo, setModelInfo] = useState<any>(null);

  // Sale Modal State
  const [saleModalVisible, setSaleModalVisible] = useState(false);
  const [selectedLot, setSelectedLot] = useState<any>(null);
  const [buyerId, setBuyerId] = useState('');
  const [buyerName, setBuyerName] = useState('');
  const [price, setPrice] = useState('');
  
  // User Selection
  const [users, setUsers] = useState<any[]>([]);
  const [userSearch, setUserSearch] = useState('');
  const [showUserList, setShowUserList] = useState(false);

  // Harvest Form State
  const [harvestData, setHarvestData] = useState({
    productType: 'Vanille',
    district: '',
    weight: '',
    quality: 'Premium'
  });

  // Transport Form State
  const [selectedLotId, setSelectedLotId] = useState('');
  const [destination, setDestination] = useState('');
  const [optimizedPath, setOptimizedPath] = useState<string[] | null>(null);




  const fetchData = async () => {
    setLoading(true);
    try {
      const [lotsData, districtsData, usersData, notifs, modelData] = await Promise.all([
        agriService.getAllLots(),
        algoService.getDistricts(),
        authService.getUsers(),
        notificationService.getNotifications(user.public_key),
        agriService.getVanillaModelInfo().catch(() => null)
      ]);

      const normalize = (k: string) => k.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
      const myKey = normalize(user.public_key);

      // Filtrage : uniquement mes produits
      const myLots = lotsData.filter((l: any) => normalize(l.owner_id) === myKey);
      
      setLots(myLots.reverse());
      setDistricts(districtsData);
      setUsers(usersData);
      setNotifications(notifs);
      setModelInfo(modelData?.model || null);
    } catch (err) {
      console.error("Erreur chargement agriculture :", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleHarvest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!harvestData.district || !harvestData.weight) {
      alert("Veuillez remplir tous les champs.");
      return;
    }

    try {
      setLoading(true);
      await agriService.recordHarvest({
        owner_id: user.public_key,
        product_type: harvestData.productType,
        district: harvestData.district,
        weight: parseFloat(harvestData.weight),
        quality: harvestData.quality
      });
      alert("Récolte inscrite avec succès sur la blockchain !");
      setHarvestData({ ...harvestData, district: '', weight: '' });
      fetchData();
      setActiveTab('tracking');
    } catch (err) {
      alert("Erreur lors de l'enregistrement de la récolte.");
    } finally {
      setLoading(false);
    }
  };

  const handleSell = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!buyerId || !price || !selectedLot) return;
    setLoading(true);
    try {
      await agriService.sellLot({
        lot_id: selectedLot.id,
        buyer_id: buyerId,
        price: parseFloat(price),
        seller_id: user.public_key
      });
      setSaleModalVisible(false);
      setBuyerId('');
      setBuyerName('');
      setPrice('');
      fetchData();
      alert("Vente enregistrée en Blockchain !");
    } catch (error) {
      alert("La vente a échoué. Seul le propriétaire peut vendre ce lot.");
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptSale = async (saleOfferId: string) => {
    try {
      setLoading(true);
      await agriService.acceptSale(saleOfferId);
      alert("Vente acceptée avec succès !");
      fetchData();
    } catch (err) {
      alert("Erreur lors de l'acceptation de la vente.");
    } finally {
      setLoading(false);
    }
  };

  const selectBuyer = (selectedUser: any) => {

    setBuyerId(selectedUser.public_key);
    setBuyerName(selectedUser.username);
    setShowUserList(false);
    setUserSearch('');
  };

  const filteredUsers = users.filter(u => 
    u.username.toLowerCase().includes(userSearch.toLowerCase()) ||
    u.public_key.toLowerCase().includes(userSearch.toLowerCase())
  );

  const openSaleModal = (lot: any) => {
    setSelectedLot(lot);
    setSaleModalVisible(true);
  };

  const handleOptimizeTransport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLotId || !destination) {
      alert("Sélectionnez un lot et une destination.");
      return;
    }

    try {
      setLoading(true);
      const res = await agriService.optimizeTransport({
        lot_id: selectedLotId,
        destination: destination
      });
      
      if (res.path) {
        setOptimizedPath(res.path);
      }
      
      alert("Trajet optimisé via A* et enregistré !");
      fetchData();
    } catch (err) {
      alert("Erreur lors de l'optimisation du transport.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/auth');
  };

  const agriStats = [
    { label: 'Lots Actifs', value: lots.length.toString(), icon: <Box size={18} /> },
    { label: 'Volume Total', value: lots.reduce((acc, l) => acc + (l.weight || 0), 0).toFixed(1) + ' kg', icon: <TrendingUp size={18} /> },
    { label: 'Réseau Logistique', value: '119 Districts', icon: <Globe size={18} /> },
    { label: 'Status IA', value: 'A* Actif', icon: <Navigation size={18} /> }
  ];

  return (
    <div className="dashboard-wrapper">
      {/* SIDEBAR */}
      <aside className="sidebar">
        <Link to="/" className="sidebar-logo">HAZO LOVA</Link>
        <nav className="nav-group">
          <Link to="/dashboard" className="nav-item">
            <LayoutDashboard className="nav-icon" /> Dashboard
          </Link>
          <Link to="/profile" className="nav-item">
            <User className="nav-icon" /> Profil
          </Link>
          <Link to="/agri" className="nav-item active">
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
            <h1>Filière Vanille</h1>
          </div>
          <div className="user-status">
            <button className="nav-icon-btn" style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--navy)', opacity: 0.5 }}><Bell size={20} /></button>
            <Link to="/profile" style={{ textDecoration: 'none', color: 'inherit', display: 'flex', alignItems: 'center', gap: '20px' }}>
              <div className="profile-mini">
                <span className="username">{user.username}</span>
                <span className="public-key-hash">{user.public_key?.substring(0, 10)}...</span>
              </div>
              <div className="avatar-circle">{user.username?.charAt(0) || 'U'}</div>
            </Link>
          </div>
        </header>

        <div className="dashboard-content">
          <div className="tab-navigation">
            <button
              className={`tab-btn ${activeTab === 'datascience' ? 'active' : ''}`}
              onClick={() => setActiveTab('datascience')}
            >
              Agri-AI / Data Science
            </button>
            <button
              className={`tab-btn ${activeTab === 'harvest' ? 'active' : ''}`}
              onClick={() => setActiveTab('harvest')}
            >
              Enregistrer une récolte
            </button>
            <button
              className={`tab-btn ${activeTab === 'tracking' ? 'active' : ''}`}
              onClick={() => setActiveTab('tracking')}
            >
              Suivi & traçabilité
            </button>
            <button
              className={`tab-btn ${activeTab === 'transport' ? 'active' : ''}`}
              onClick={() => setActiveTab('transport')}
            >
              Logistique (A*)
            </button>
            <button
              className={`tab-btn ${activeTab === 'notifications' ? 'active' : ''}`}
              onClick={() => setActiveTab('notifications')}
            >
              Offres d'achat {notifications.length > 0 ? `(${notifications.length})` : ''}
            </button>
          </div>

          <div className="land-container-full">
            <div className="land-stats-summary" style={{ marginBottom: '40px' }}>
              {agriStats.map((stat, i) => (
                <div key={i} className="l-stat-card">
                  <div className="l-stat-icon" style={{ color: 'var(--emeraude)' }}>{stat.icon}</div>
                  <div className="l-stat-info">
                    <span className="l-stat-label">{stat.label}</span>
                    <span className="l-stat-value">{stat.value}</span>
                  </div>
                </div>
              ))}
            </div>

            {modelInfo?.trained && (() => {
              const m = modelInfo.metrics?.targets?.fair_farmgate_price_mga || {};
              const stats = [
                { label: 'MAE', value: `${Math.round(m.mae || 0).toLocaleString('fr-FR')} MGA/kg` },
                { label: 'R² (test)', value: (m.r2 ?? 0).toFixed(3) },
                { label: 'MAPE', value: `${m.mape_pct ?? 0}%` },
                { label: 'Entraîné le', value: (modelInfo.trained_at || '').slice(0, 10) }
              ];
              return (
                <div className="l-stat-card model-banner" style={{ marginBottom: '40px', justifyContent: 'space-between', flexWrap: 'wrap', gap: '24px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div className="l-stat-icon" style={{ background: 'rgba(255,255,255,0.12)', color: 'var(--or)' }}><Brain size={20} /></div>
                    <div className="l-stat-info">
                      <span className="l-stat-label" style={{ color: '#cbd5e1' }}>Modèle IA entraîné localement</span>
                      <span className="l-stat-value">Ridge multi-cibles · {modelInfo.n_samples} lots</span>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '32px', flexWrap: 'wrap' }}>
                    {stats.map((s, i) => (
                      <div key={i} className="l-stat-info">
                        <span className="l-stat-label" style={{ color: '#cbd5e1' }}>{s.label}</span>
                        <span className="l-stat-value">{s.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()}

            {activeTab === 'datascience' ? (
              <VanillaLab user={user} districts={districts} onSealed={fetchData} />
            ) : (
            <div className="land-main-layout">
              <div className="parcels-section">
                {activeTab === 'harvest' && (
                  <div className="registration-form-area">
                    <h2 className="section-title">Nouvelle Récolte</h2>
                    <form className="mutation-form" onSubmit={handleHarvest}>
                      <div className="form-field">
                        <label className="form-label">Nom du Produit</label>
                        <input 
                          type="text" 
                          className="form-input" 
                          placeholder="Ex: Poivre Noir, Riz Makalioka..." 
                          value={harvestData.productType}
                          onChange={(e) => setHarvestData({...harvestData, productType: e.target.value})}
                        />
                      </div>
                      <div className="form-field">
                        <label className="form-label">District d'Origine</label>
                        <select 
                          className="form-input"
                          value={harvestData.district}
                          onChange={(e) => setHarvestData({...harvestData, district: e.target.value})}
                        >
                          <option value="">Sélectionnez un district</option>
                          {districts.map(d => <option key={d.id} value={d.nom}>{d.nom}</option>)}
                        </select>
                      </div>
                      <div className="form-field">
                        <label className="form-label">Poids Net (kg)</label>
                        <input 
                          type="number" 
                          className="form-input" 
                          step="0.1"
                          placeholder="0.0"
                          value={harvestData.weight}
                          onChange={(e) => setHarvestData({...harvestData, weight: e.target.value})}
                        />
                      </div>
                      <div className="form-field">
                        <label className="form-label">Qualité Certifiée</label>
                        <select 
                          className="form-input"
                          value={harvestData.quality}
                          onChange={(e) => setHarvestData({...harvestData, quality: e.target.value})}
                        >
                          <option value="Premium">Premium (Grade A)</option>
                          <option value="Standard">Standard (Grade B)</option>
                          <option value="Export">Export Qualité</option>
                        </select>
                      </div>
                      <button type="submit" className="btn-submit-mutation" disabled={loading}>
                        {loading ? 'Traitement...' : 'CERTIFIER LA RÉCOLTE'}
                      </button>
                    </form>
                  </div>
                )}

                {activeTab === 'tracking' && (
                  <>
                    <h2 className="section-title">Flux de Production</h2>
                    <div className="parcels-grid">
                      {lots.length === 0 ? (
                        <p style={{ opacity: 0.5, gridColumn: '1/-1', textAlign: 'center', padding: '40px' }}>Aucun lot détecté.</p>
                      ) : lots.map((lot, idx) => (
                        <div key={idx} className="parcel-card" style={{ borderLeft: '4px solid var(--emeraude)' }}>
                          <div className="parcel-header">
                            <span className="parcel-id">{lot.id}</span>
                            <span className="parcel-status" style={{ background: 'rgba(45, 122, 88, 0.1)', color: 'var(--emeraude)' }}>{lot.status}</span>
                          </div>
                          <div style={{ fontSize: '18px', fontWeight: 900, margin: '10px 0' }}>{lot.product_type}</div>
                          <div className="parcel-info-row">
                            <span className="parcel-label">Poids</span>
                            <span className="parcel-value">{lot.weight} kg</span>
                          </div>
                          <div className="parcel-info-row">
                            <span className="parcel-label">Origine</span>
                            <span className="parcel-value">{lot.district_origin}</span>
                          </div>
                          <div className="parcel-actions" style={{ marginTop: '15px' }}>
                            <button className="parcel-btn btn-details" onClick={() => { setSelectedLotId(lot.id); setActiveTab('transport'); }}>
                              <Navigation size={14} /> Logistique
                            </button>
                            {lot.status !== 'VENDU' && (
                              <button className="parcel-btn btn-transfer" onClick={() => openSaleModal(lot)}>
                                <Wallet size={14} /> Vendre
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </>
                )}

                {activeTab === 'transport' && (
                  <div className="registration-form-area">
                    <h2 className="section-title">Optimisation de Trajet (A*)</h2>
                    <form className="mutation-form" onSubmit={handleOptimizeTransport}>
                      <div className="form-field">
                        <label className="form-label">Sélectionner un Lot</label>
                        <select 
                          className="form-input"
                          value={selectedLotId}
                          onChange={(e) => setSelectedLotId(e.target.value)}
                        >
                          <option value="">Choisir un lot...</option>
                          {lots.map(l => <option key={l.id} value={l.id}>{l.id} - {l.product_type} ({l.district_origin})</option>)}
                        </select>
                      </div>
                      <div className="form-field">
                        <label className="form-label">Destination (Port / Centre de Collecte)</label>
                        <select 
                          className="form-input"
                          value={destination}
                          onChange={(e) => setDestination(e.target.value)}
                        >
                          <option value="">Choisir une destination...</option>
                          {districts.map(d => <option key={d.id} value={d.nom}>{d.nom}</option>)}
                        </select>
                      </div>
                      <button type="submit" className="btn-submit-mutation" disabled={loading}>
                        CALCULER LE CHEMIN OPTIMAL
                      </button>
                    </form>

                    {optimizedPath && (
                      <div style={{ marginTop: '30px', padding: '20px', background: 'var(--off-white)', borderRadius: '16px' }}>
                        <h4 style={{ marginBottom: '15px', fontSize: '14px', fontWeight: 800 }}>RÉSULTAT DE L'ALGORITHME A*</h4>
                        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
                          {optimizedPath.map((step, i) => (
                            <React.Fragment key={i}>
                              <div style={{ padding: '8px 12px', background: 'white', borderRadius: '8px', fontSize: '12px', fontWeight: 700, border: '1px solid #e2e8f0' }}>
                                {step}
                              </div>
                              {i < optimizedPath.length - 1 && <ArrowRight size={14} opacity={0.3} />}
                            </React.Fragment>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                {activeTab === 'notifications' && (
                  <div style={{ background: 'var(--blanc)', padding: '40px', borderRadius: '24px', border: 'var(--border-main)' }}>
                    <h2 className="section-title">Mes Offres d'Achat</h2>
                    {notifications.length === 0 ? <p>Aucune offre en attente.</p> : (
                        <div className="parcels-grid">
                            {notifications.map((n, i) => (
                                <div key={i} className="parcel-card">
                                    <div className="parcel-header"><span className="parcel-id">{n.sale_offer_id}</span></div>
                                    <p>{n.message}</p>
                                    <button className="parcel-btn btn-transfer" onClick={() => handleAcceptSale(n.sale_offer_id)}>Accepter l'offre</button>
                                </div>
                            ))}
                        </div>
                    )}
                  </div>
                )}
              </div>

              <div className="land-sidebar-actions">
                <h2 className="section-title">Journal de Bord</h2>
                <div className="land-history-card" style={{ marginTop: 0 }}>
                  <div className="land-activity-list">
                    {lots.slice(0, 5).map((l, i) => (
                      <div key={i} className="land-activity-item">
                        <div className="act-icon-box"><Leaf size={14} style={{ color: 'var(--emeraude)' }} /></div>
                        <div className="act-content">
                          <span className="act-title">Récolte {l.product_type}</span>
                          <span className="act-meta">{l.district_origin} • {l.weight}kg</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div style={{ marginTop: '30px', padding: '20px', background: 'var(--navy)', color: 'white', borderRadius: '20px' }}>
                  <h4 style={{ fontSize: '14px', marginBottom: '10px' }}>Note Technique</h4>
                  <p style={{ fontSize: '11px', opacity: 0.7, lineHeight: 1.5 }}>
                    Le routage utilise l'algorithme A* sur un graphe de 119 districts. 
                    Chaque étape du transport est scellée dans un Merkle Tree pour garantir l'origine Madagascar.
                  </p>
                </div>
              </div>
            </div>
            )}
          </div>
        </div>
      </main>

      <BobModal 
        visible={saleModalVisible} 
        onClose={() => setSaleModalVisible(false)}
        title="Finaliser la Vente"
      >
        <form onSubmit={handleSell}>
          <div className="bob-summary">{selectedLot?.product_type} - {selectedLot?.weight}kg</div>
          
          <div className="bob-form-group">
            <label className="bob-label">Rechercher l'Acheteur</label>
            <div className="bob-input-wrapper">
              <Search size={18} color="var(--gray)" />
              <input 
                className="bob-input" 
                placeholder="Nom ou Clé publique..." 
                value={buyerName || userSearch}
                onChange={(e) => {
                  if (buyerName) { setBuyerName(''); setBuyerId(''); }
                  setUserSearch(e.target.value);
                  setShowUserList(true);
                }}
                onFocus={() => setShowUserList(true)}
                required
              />
            </div>
            
            {showUserList && userSearch.length > 0 && (
              <div className="bob-user-dropdown" style={{ 
                background: 'var(--white)', 
                border: '1px solid var(--border)', 
                borderRadius: '12px', 
                marginTop: '10px', 
                maxHeight: '200px', 
                overflowY: 'auto',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
              }}>
                {filteredUsers.slice(0, 5).map(u => (
                  <div 
                    key={u.public_key} 
                    onClick={() => selectBuyer(u)}
                    style={{ 
                      padding: '12px 16px', 
                      cursor: 'pointer', 
                      borderBottom: '1px solid var(--lightGray)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'var(--lightGray)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <div style={{ width: '32px', height: '32px', borderRadius: '16px', background: 'var(--accent)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '12px' }}>
                      {u.username[0].toUpperCase()}
                    </div>
                    <div>
                      <div style={{ fontSize: '14px', fontWeight: 700 }}>{u.username}</div>
                      <div style={{ fontSize: '10px', color: 'var(--gray)' }}>{u.public_key.substring(0, 20)}...</div>
                    </div>
                  </div>
                ))}
                {filteredUsers.length === 0 && <div style={{ padding: '16px', textAlign: 'center', color: 'var(--gray)', fontSize: '12px' }}>Aucun utilisateur trouvé</div>}
              </div>
            )}
          </div>

          <div className="bob-form-group">
            <label className="bob-label">Prix de vente (MGA)</label>
            <div className="bob-input-wrapper">
              <DollarSign size={18} color="var(--gray)" />
              <input 
                className="bob-input" 
                type="number"
                placeholder="Ex: 500000" 
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                required
              />
            </div>
          </div>

          <button type="submit" className="bob-submit-btn" disabled={loading || !buyerId}>
            {loading ? 'Traitement...' : 'Confirmer la Vente'}
          </button>
        </form>
      </BobModal>
    </div>
  );
}
