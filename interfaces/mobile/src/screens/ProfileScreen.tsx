import React from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ScrollView } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { palette } from '../theme/palette';
import { User, LogOut, Shield, Mail, Key } from 'lucide-react-native';

const ROLE_LABELS: Record<string, string> = {
  PLANTEUR: 'Planteur',
  COLLECTEUR: 'Collecteur',
  EXPORTATEUR: 'Exportateur',
  CITOYEN: 'Citoyen',
};

export default function ProfileScreen({ route, navigation }: any) {
  const user = route.params?.user || {};
  const role = ROLE_LABELS[user.role] || user.role || 'Citoyen';

  const handleLogout = () => {
    navigation.replace('Login');
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.header}>
          <View style={styles.avatar}>
            <User color="white" size={40} />
          </View>
          <Text style={styles.username}>{user.username || 'Utilisateur'}</Text>
          <Text style={styles.role}>{role}</Text>
        </View>

        <View style={styles.card}>
          <View style={styles.infoRow}>
            <Mail color={palette.gray} size={20} />
            <View style={styles.infoText}>
              <Text style={styles.label}>Email</Text>
              <Text style={styles.value}>{user.email || 'Non renseigné'}</Text>
            </View>
          </View>
          <View style={styles.infoRow}>
            <Shield color={palette.gray} size={20} />
            <View style={styles.infoText}>
              <Text style={styles.label}>District</Text>
              <Text style={styles.value}>{user.district || 'Non renseigné'}</Text>
            </View>
          </View>
          <View style={styles.infoRow}>
            <Key color={palette.gray} size={20} />
            <View style={styles.infoText}>
              <Text style={styles.label}>Clé Publique</Text>
              <Text style={styles.value} numberOfLines={1} ellipsizeMode="middle">{user.public_key || '...'}</Text>
            </View>
          </View>
          <View style={styles.infoRow}>
            <Shield color={palette.gray} size={20} />
            <View style={styles.infoText}>
              <Text style={styles.label}>ID Numérique</Text>
              <Text style={styles.value}>
                HZL-USER-{user.public_key ? user.public_key.substring(2, 10).toUpperCase() : 'INCONNU'}
              </Text>
            </View>
          </View>
        </View>

        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <LogOut color="white" size={20} />
          <Text style={styles.logoutText}>Se déconnecter</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: palette.background },
  content: { padding: 20 },
  header: { alignItems: 'center', marginBottom: 30, marginTop: 20 },
  avatar: { width: 100, height: 100, borderRadius: 50, backgroundColor: palette.accent, justifyContent: 'center', alignItems: 'center', marginBottom: 15 },
  username: { fontSize: 24, fontWeight: 'bold', color: palette.ink },
  role: { fontSize: 14, color: palette.accent, fontWeight: '700', textTransform: 'uppercase', marginTop: 5 },
  card: { backgroundColor: palette.surface, borderRadius: 20, padding: 20, elevation: 2 },
  infoRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 20 },
  infoText: { marginLeft: 15, flex: 1 },
  label: { fontSize: 12, color: palette.gray },
  value: { fontSize: 16, color: palette.ink, fontWeight: '600', marginTop: 2 },
  logoutButton: { flexDirection: 'row', backgroundColor: palette.error, padding: 20, borderRadius: 20, justifyContent: 'center', alignItems: 'center', marginTop: 30 },
  logoutText: { color: 'white', fontWeight: 'bold', fontSize: 16, marginLeft: 10 }
});
