import React, { useState, useEffect } from 'react';
import { TouchableOpacity, View, Text, StyleSheet } from 'react-native';
import { Bell } from 'lucide-react-native'; // Ajout nécessaire à Icons.tsx
import { palette } from '../theme/palette';

export const NotificationBell = ({ publicKey }: { publicKey: string }) => {
  const [count, setCount] = useState(0);

  // Simulation d'un fetch (devrait être un service réel)
  useEffect(() => {
    // intervalle de polling ou socket
  }, []);

  return (
    <TouchableOpacity style={styles.container}>
      <Bell color={palette.ink} size={24} />
      {count > 0 && (
        <View style={styles.badge}>
          <Text style={styles.badgeText}>{count}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: { padding: 5 },
  badge: { 
    position: 'absolute', right: 0, top: 0, 
    backgroundColor: palette.error, borderRadius: 10, 
    width: 18, height: 18, justifyContent: 'center', alignItems: 'center' 
  },
  badgeText: { color: 'white', fontSize: 10, fontWeight: 'bold' }
});
