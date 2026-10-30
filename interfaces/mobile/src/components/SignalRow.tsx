import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { palette } from '../theme/palette';

interface SignalRowProps {
  label: string;
  status: string;
  icon: React.ReactNode;
}

export default function SignalRow({ label, status, icon }: SignalRowProps) {
  return (
    <View style={styles.signalRow}>
      <View style={styles.signalLeft}>
        <View style={styles.iconContainer}>{icon}</View>
        <Text style={styles.signalLabel}>{label}</Text>
      </View>
      <View style={styles.statusBadge}>
        <Text style={styles.statusText}>{status}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  signalRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 14,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(24, 36, 54, 0.05)',
  },
  signalLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  iconContainer: {
    marginRight: 10,
  },
  signalLabel: {
    fontSize: 14,
    color: palette.ink,
    fontWeight: '600',
  },
  statusBadge: {
    backgroundColor: palette.accentTransparent,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '800',
    color: palette.accent,
  },
});
