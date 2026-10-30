/**
 * LandingPage3D.tsx — Hazo Lova Blockchain Edition (Clean Video Edition)
 */

import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

const BRAND = {
  teal: "#0d9488",
  accent: "#0f766e",
  bg: "#ffffff",
  card: "rgba(255, 255, 255, 0.5)",
  text: "#0f172a",
  muted: "#475569",
};

const glassStyle = {
  background: BRAND.card,
  backdropFilter: "blur(16px)",
  border: "1px solid rgba(255,255,255,0.5)",
  borderRadius: "32px",
  boxShadow: "0 10px 40px 0 rgba(0, 0, 0, 0.05)",
};

export default function LandingPage3D() {
  const navigate = useNavigate();
  const isLoggedIn = Boolean(localStorage.getItem('user'));

  return (
    <div
      style={{
        background:
          "radial-gradient(1200px 600px at 80% 10%, rgba(13, 148, 136, 0.14), transparent 60%), radial-gradient(900px 500px at 10% 90%, rgba(15, 118, 110, 0.10), transparent 60%), #ffffff",
        minHeight: "100vh",
        color: BRAND.text,
        fontFamily: "'Inter', sans-serif",
        overflow: "hidden",
        position: "relative",
      }}
    >
      {/* Overlay Gradient (Ultra Light to maintain legibility) */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(to bottom, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.4) 100%)",
          zIndex: 1,
        }}
      />

      <div style={{ position: "relative", height: "100vh", zIndex: 2 }}>
        <nav
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            padding: "2.5rem 5rem",
            display: "flex",
            justifyContent: "space-between",
            zIndex: 10,
            alignItems: "center",
          }}
        >
          <div
            style={{
              fontSize: 28,
              fontWeight: 900,
              letterSpacing: "-0.02em",
              color: BRAND.text,
            }}
          >
            HAZO<span style={{ color: BRAND.teal }}>LOVA</span>
          </div>
          <div style={{ display: "flex", gap: "3rem", alignItems: "center" }}>
            <span
              onClick={() => navigate(isLoggedIn ? "/agri" : "/auth")}
              style={{
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "0.95rem",
                color: BRAND.text,
              }}
            >
              VANILLE
            </span>
            <span
              onClick={() => navigate("/auth")}
              style={{
                cursor: "pointer",
                fontWeight: 600,
                fontSize: "0.95rem",
                color: BRAND.text,
              }}
            >
              CONNEXION
            </span>
            <button
              onClick={() => navigate(isLoggedIn ? "/dashboard" : "/auth")}
              style={{
                padding: "0.9rem 2rem",
                background: BRAND.text,
                color: "#fff",
                borderRadius: "50px",
                border: "none",
                fontWeight: 700,
                cursor: "pointer",
                fontSize: "0.9rem",
                boxShadow: "0 4px 20px rgba(0, 0, 0, 0.1)",
              }}
            >
              {isLoggedIn ? 'OUVRIR LA DÉMO' : 'SE CONNECTER'}
            </button>
          </div>
        </nav>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            height: "100%",
            paddingLeft: "10%",
            maxWidth: "1200px",
          }}
        >
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1 }}
            style={{
              maxWidth: 650,
              zIndex: 10,
              ...glassStyle,
              padding: "4rem",
            }}
          >
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
              style={{
                color: BRAND.teal,
                fontWeight: 800,
                fontSize: "1rem",
                textTransform: "uppercase",
                letterSpacing: "0.4em",
                display: "block",
                marginBottom: "1rem",
              }}
            >
              MADAGASCAR 2035
            </motion.span>
            <h1
              style={{
                fontSize: "5.5rem",
                lineHeight: 0.9,
                margin: "0 0 2rem 0",
                fontWeight: 900,
                letterSpacing: "-0.03em",
                color: BRAND.text,
              }}
            >
              L'Héritage
              <br />
              <span style={{ color: "rgba(15, 23, 42, 0.4)" }}>Numérique.</span>
            </h1>
            <p
              style={{
                fontSize: "1.4rem",
                color: BRAND.muted,
                marginBottom: "3rem",
                lineHeight: 1.6,
                fontWeight: 500,
              }}
            >
              Analyse IA ISO 5565 et passeport blockchain infalsifiable pour
              les récoltes de vanille de la Grande Île.
            </p>
            <div style={{ display: "flex", gap: "1.5rem" }}>
              <button
                onClick={() => navigate(isLoggedIn ? "/agri" : "/auth")}
                style={{
                  padding: "1.2rem 3rem",
                  background: BRAND.teal,
                  color: "#fff",
                  borderRadius: "16px",
                  border: "none",
                  fontSize: "1.1rem",
                  fontWeight: 700,
                  cursor: "pointer",
                  transition: "all 0.3s ease",
                  boxShadow: "0 4px 15px rgba(13, 148, 136, 0.3)",
                }}
              >
                Lancer la démo vanille
              </button>
              <button
                onClick={() => navigate(isLoggedIn ? "/dashboard" : "/auth")}
                style={{
                  padding: "1.2rem 3rem",
                  background: "transparent",
                  color: BRAND.text,
                  borderRadius: "16px",
                  border: "2px solid rgba(15, 23, 42, 0.1)",
                  fontSize: "1.1rem",
                  fontWeight: 600,
                  cursor: "pointer",
                  backdropFilter: "blur(10px)",
                }}
              >
                {isLoggedIn ? 'Tableau de bord' : 'Créer un compte'}
              </button>
            </div>
          </motion.div>
        </div>

        {/* Bottom Bar */}
        <div
          style={{
            position: "absolute",
            bottom: "4rem",
            left: "10%",
            right: "10%",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            color: "rgba(15, 23, 42, 0.4)",
            fontSize: "0.9rem",
            fontWeight: 600,
          }}
        >
          <div style={{ display: "flex", gap: "4rem" }}>
            <div>
              <div
                style={{
                  color: BRAND.teal,
                  fontWeight: 800,
                  fontSize: "1.2rem",
                }}
              >
                119
              </div>
              <div style={{ fontSize: "0.7rem", letterSpacing: "0.1em" }}>
                DISTRICTS
              </div>
            </div>
            <div>
              <div
                style={{
                  color: BRAND.teal,
                  fontWeight: 800,
                  fontSize: "1.2rem",
                }}
              >
                1 000
              </div>
              <div style={{ fontSize: "0.7rem", letterSpacing: "0.1em" }}>
                LOTS ANALYSÉS
              </div>
            </div>
            <div>
              <div
                style={{
                  color: BRAND.teal,
                  fontWeight: 800,
                  fontSize: "1.2rem",
                }}
              >
                44,8 $
              </div>
              <div style={{ fontSize: "0.7rem", letterSpacing: "0.1em" }}>
                FOB ONU 2025
              </div>
            </div>
          </div>
          <div style={{ letterSpacing: "0.05em" }}>
            © 2026 HAZO LOVA FOUNDATION
          </div>
        </div>
      </div>
    </div>
  );
}
