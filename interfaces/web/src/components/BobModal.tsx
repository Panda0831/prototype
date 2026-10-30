import React from 'react';
import './BobModal.css';

interface BobModalProps {
  visible: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export const BobModal: React.FC<BobModalProps> = ({ visible, onClose, title, children }) => {
  if (!visible) return null;

  return (
    <div className="bob-modal-overlay" onClick={onClose}>
      <div className="bob-modal-container" onClick={(e) => e.stopPropagation()}>
        <div className="bob-modal-handle" />
        <div className="bob-modal-header">
          <h2 className="bob-modal-title">{title}</h2>
          <button className="bob-modal-close" onClick={onClose}>Annuler</button>
        </div>
        <div className="bob-modal-content">
          {children}
        </div>
      </div>
    </div>
  );
};
