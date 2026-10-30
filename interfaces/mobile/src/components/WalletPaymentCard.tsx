import React from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';
import { palette } from '../theme/palette';
import { Wallet, CheckCircle, Clock3 } from './Icons';

interface WalletPaymentCardProps {
  amount: number;
  description: string;
  senderId: string;
  onAccept: () => void;
  loading?: boolean;
}

export const WalletPaymentCard = ({ 
  amount, 
  description, 
  senderId, 
  onAccept, 
  loading 
}: WalletPaymentCardProps) => {
  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.iconContainer}>
          <Wallet color={palette.accent} size={20} />
        </View>
        <View style={styles.statusBadge}>
          <Clock3 color={palette.warning} size={12} />
          <Text style={styles.statusText}>En attente</Text>
        </View>
      </View>

      <Text style={styles.amount}>{amount.toLocaleString()} MGA</Text>
      <Text style={styles.description}>{description}</Text>
      
      <View style={styles.divider} />
      
      <View style={styles.footer}>
        <View style={{ flex: 1 }}>
          <Text style={styles.label}>Destinataire (Clé)</Text>
          <Text style={styles.key} numberOfLines={1}>{senderId}</Text>
        </View>
        
        <TouchableOpacity 
          style={styles.payButton} 
          onPress={onAccept}
          disabled={loading}
        >
          <CheckCircle color="white" size={18} />
          <Text style={styles.payButtonText}>Payer</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: palette.surface,
    borderRadius: 24,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: palette.lightGray,
    shadowColor: palette.ink,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.05,
    shadowRadius: 10,
    elevation: 2,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  iconContainer: {
    padding: 8,
    backgroundColor: palette.accentTransparent,
    borderRadius: 12,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(245, 158, 11, 0.1)',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 20,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '800',
    color: palette.warning,
    marginLeft: 5,
    textTransform: 'uppercase',
  },
  amount: {
    fontSize: 28,
    fontWeight: '900',
    color: palette.ink,
    marginBottom: 5,
  },
  description: {
    fontSize: 14,
    color: palette.gray,
    fontWeight: '500',
    marginBottom: 20,
  },
  divider: {
    height: 1,
    backgroundColor: palette.lightGray,
    marginBottom: 15,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  label: {
    fontSize: 10,
    color: palette.gray,
    fontWeight: '700',
    textTransform: 'uppercase',
    marginBottom: 2,
  },
  key: {
    fontSize: 12,
    color: palette.ink,
    fontFamily: 'monospace',
    opacity: 0.6,
  },
  payButton: {
    backgroundColor: palette.accent,
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 18,
    paddingVertical: 10,
    borderRadius: 14,
    marginLeft: 15,
  },
  payButtonText: {
    color: 'white',
    fontWeight: '800',
    fontSize: 14,
    marginLeft: 8,
  },
});
