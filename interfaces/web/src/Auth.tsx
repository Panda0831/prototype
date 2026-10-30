import {
  ArrowLeft,
  ChevronRight,
  Database,
  FileCheck,
  Globe,
  Loader2,
  Lock,
  Map as MapIcon,
  ShieldCheck,
  Trees,
  Zap,
} from "lucide-react";
import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./auth.css";
import { authService, blockchainService } from "./services/api";

const BlockchainGraph = () => {
  const [blockHeight, setBlockHeight] = useState(0);

  useEffect(() => {
    blockchainService
      .getStatus()
      .then((status: any) => setBlockHeight(status?.longueur ?? 0))
      .catch(() => setBlockHeight(0));
  }, []);

  const shortHash = (label: string) =>
    label
      .split("")
      .map((char) => char.charCodeAt(0).toString(16))
      .join("")
      .slice(0, 4)
      .toUpperCase();

  const nodes = [
    {
      id: 1,
      label: "GENÈSE",
      icon: <ShieldCheck size={14} />,
      x: 50,
      y: 35,
      delay: "0s",
      type: "core",
    },
    {
      id: 2,
      label: "RÉCOLTE",
      icon: <MapIcon size={14} />,
      x: 25,
      y: 45,
      delay: "-2s",
      type: "asset",
    },
    {
      id: 3,
      label: "SCAN IA",
      icon: <Trees size={14} />,
      x: 75,
      y: 45,
      delay: "-4s",
      type: "asset",
    },
    {
      id: 4,
      label: "PASSEPORT",
      icon: <FileCheck size={14} />,
      x: 50,
      y: 55,
      delay: "-1s",
      type: "cert",
    },
    {
      id: 5,
      label: "IDENTITÉ",
      icon: <Lock size={14} />,
      x: 20,
      y: 70,
      delay: "-3s",
      type: "user",
    },
    {
      id: 6,
      label: "EXPORT",
      icon: <Database size={14} />,
      x: 80,
      y: 70,
      delay: "-5s",
      type: "cert",
    },
    {
      id: 7,
      label: "VALIDATION",
      icon: <Zap size={14} />,
      x: 50,
      y: 80,
      delay: "-6s",
      type: "core",
    },
  ];

  const connections = [
    { from: 1, to: 2 },
    { from: 1, to: 3 },
    { from: 2, to: 4 },
    { from: 3, to: 4 },
    { from: 4, to: 7 },
    { from: 5, to: 7 },
    { from: 6, to: 7 },
    { from: 5, to: 4 },
    { from: 6, to: 4 },
  ];

  return (
    <div className="blockchain-graph-container">
      <div className="live-counter">
        <span className="counter-label">BLOC ACTUEL</span>
        <span className="counter-value">#{blockHeight.toLocaleString()}</span>
      </div>

      <svg className="graph-lines">
        {connections.map((conn, i) => {
          const from = nodes.find((n) => n.id === conn.from);
          const to = nodes.find((n) => n.id === conn.to);
          if (!from || !to) return null;
          return (
            <g key={i}>
              <line
                x1={`${from.x}%`}
                y1={`${from.y}%`}
                x2={`${to.x}%`}
                y2={`${to.y}%`}
                className="base-line"
              />
              <circle r="2" className="traveling-dot">
                <animateMotion
                  dur={`${3 + (i % 4)}s`}
                  repeatCount="indefinite"
                  path={`M ${from.x * 4},${from.y * 4} L ${to.x * 4},${to.y * 4}`}
                />
              </circle>
            </g>
          );
        })}
      </svg>
      {nodes.map((node) => (
        <div
          key={node.id}
          className={`graph-node-wrapper node-type-${node.type}`}
          style={{
            left: `${node.x}%`,
            top: `${node.y}%`,
            animationDelay: node.delay,
          }}
        >
          <div className="graph-node">
            <div className="node-icon">{node.icon}</div>
            <div className="node-info">
              <span className="node-label">{node.label}</span>
              <span className="node-hash">0x{shortHash(node.label)}</span>
            </div>
          </div>
        </div>
      ))}
      <div className="hashes-bg">
        {Array.from({ length: 15 }).map((_, i) => (
          <div
            key={i}
            className="hash-line"
            style={{
              top: `${i * 6}%`,
              animationDelay: `${i * 0.8}s`,
              opacity: 0.05 - i * 0.002,
            }}
          >
            BLOCK_{Math.max(0, blockHeight - i)} :: SIG:{" "}
            {shortHash(`BLOCK_${i}`)}...
          </div>
        ))}
      </div>
    </div>
  );
};

function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    role: "PLANTEUR",
    district: "Antananarivo",
  });

  const navigate = useNavigate();

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isLogin) {
        const data = await authService.signIn({
          email: formData.email,
          password: formData.password,
        });
        localStorage.setItem("user", JSON.stringify(data));
        navigate("/dashboard");
      } else {
        await authService.signUp({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          role: formData.role,
          district: formData.district,
        });
        alert("Compte créé avec succès !");
        setIsLogin(true);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Erreur de connexion au réseau");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page-wrapper">
      <div className="noise-overlay"></div>

      {/* PANEL GAUCHE - Blockchain Vivante */}
      <div className="auth-side-branding">
        <div className="branding-header">
          <div className="branding-logo">HAZO LOVA</div>
          <div className="network-stats">
            <div className="stat-item">
              <span className="stat-dot"></span>
              Réseau Actif
            </div>
            <div className="stat-item">
              <Globe size={12} /> MG-BFT v2.4
            </div>
          </div>
        </div>

        <div className="branding-main-title">
          <div className="pre-title">MADAGASCAR 2035</div>
          <h2 className="branding-title">LE JUSTE PRIX, PROUVÉ.</h2>
        </div>

        <BlockchainGraph />

        <div className="branding-footer-area">
          <p className="branding-quote">
            "Un diagnostic IA scellé sur la blockchain, du champ de Sambava
            jusqu'au port de Toamasina."
          </p>
          <div className="branding-footer">
            © 2026 Hazo Lova Agri-AI — Filière Vanille, IndabaX Madagascar
          </div>
        </div>
      </div>

      {/* PANEL DROIT - Formulaire Premium */}
      <div className="auth-side-form">
        <Link to="/" className="auth-back-btn">
          <ArrowLeft size={16} /> Retour
        </Link>

        <div className="auth-form-container animate-fade">
          <div className="auth-card-modern">
            <div className="auth-tabs">
              <button
                className={`tab-btn ${isLogin ? "active" : ""}`}
                onClick={() => setIsLogin(true)}
              >
                Connexion
              </button>
              <button
                className={`tab-btn ${!isLogin ? "active" : ""}`}
                onClick={() => setIsLogin(false)}
              >
                Inscription
              </button>
              <div
                className={`tab-indicator ${isLogin ? "left" : "right"}`}
              ></div>
            </div>

            <h1 className="auth-title-modern">
              {isLogin ? "Authentification" : "Rejoindre le réseau"}
            </h1>

            {error && <div className="error-message-modern">{error}</div>}

            <form onSubmit={handleSubmit} className="premium-form">
              {!isLogin && (
                <>
                  <div className="form-group-modern">
                    <label className="label-modern">Identité</label>
                    <input
                      type="text"
                      name="username"
                      className="input-modern"
                      placeholder="Nom complet"
                      value={formData.username}
                      onChange={handleInputChange}
                      required={!isLogin}
                    />
                  </div>
                  <div className="form-group-modern">
                    <label className="label-modern">Rôle</label>
                    <select
                      name="role"
                      className="input-modern"
                      value={formData.role}
                      onChange={handleInputChange}
                    >
                      <option value="CITOYEN">Citoyen</option>
                      <option value="PLANTEUR">Planteur</option>
                      <option value="COLLECTEUR">Collecteur</option>
                      <option value="EXPORTATEUR">Exportateur</option>
                    </select>
                  </div>
                </>
              )}

              <div className="form-group-modern">
                <label className="label-modern">Email Réseau</label>
                <input
                  type="email"
                  name="email"
                  className="input-modern"
                  placeholder="nom@hazolova.mg"
                  value={formData.email}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="form-group-modern">
                <label className="label-modern">Clé d'accès</label>
                <input
                  type="password"
                  name="password"
                  className="input-modern"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <button className="btn-modern" disabled={loading}>
                {loading ? (
                  <Loader2 className="animate-spin" size={18} />
                ) : (
                  <>
                    {isLogin ? "Se connecter" : "Valider mon accès"}
                    <ChevronRight size={18} />
                  </>
                )}
              </button>
            </form>

            <div className="auth-divider">Méthodes Alternatives</div>

            <div className="social-grid">
              <button className="btn-modern btn-secondary-modern id-mada">
                <ShieldCheck size={18} color="#2D7A58" /> Mobile
              </button>
              <button className="btn-modern btn-secondary-modern express">
                <Zap size={18} color="#D4A373" /> Google
              </button>
            </div>

            <div className="security-badge">
              <Lock size={12} />
              Chiffrement de bout en bout — Protocole HZ-AES
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AuthPage;
