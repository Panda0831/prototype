import React, { useState } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { palette } from '../theme/palette';
import { authService } from '../services/api';
import { StatusBar } from 'expo-status-bar';
import { FadeInView } from '../components/Animations';

export default function LoginScreen({ navigation }: { navigation: any }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [role, setRole] = useState('CITOYEN');
  const [loading, setLoading] = useState(false);

  const roles = [
    { id: 'PLANTEUR', label: 'Planteur' },
    { id: 'COLLECTEUR', label: 'Collecteur' },
    { id: 'EXPORTATEUR', label: 'Exportateur' },
  ];

  const handleAuth = async () => {
    if (!email || !password || (!isLogin && !username)) {
      alert('Veuillez remplir tous les champs');
      return;
    }

    setLoading(true);
    try {
      let data;
      if (isLogin) {
        data = await authService.signIn({ email, password });
      } else {
        data = await authService.signUp({ username, email, password, role });
      }
      console.log("[DEBUG Login] User data received:", JSON.stringify(data));
      navigation.replace('Main', { user: data });
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erreur d\'authentification');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.inner}
      >
        <ScrollView showsVerticalScrollIndicator={false} contentContainerStyle={styles.scrollContent}>
          <FadeInView duration={800}>
            <View style={styles.header}>
              <View style={styles.logoBadge}>
                <Text style={styles.logoText}>HL</Text>
              </View>
              <Text style={styles.logoTitle}>HAZO LOVA</Text>
              <Text style={styles.title}>
                {isLogin ? 'Bon retour' : 'Rejoindre le réseau'}
              </Text>
              <Text style={styles.subtitle}>
                Le juste prix de la vanille, scellé sur la blockchain.
              </Text>
            </View>

            <View style={styles.form}>
              {!isLogin && (
                <View style={styles.inputGroup}>
                  <Text style={styles.inputLabel}>Nom d'utilisateur</Text>
                  <TextInput
                    style={styles.input}
                    placeholder="Ex: Jean Rakoto"
                    value={username}
                    onChangeText={setUsername}
                    autoCapitalize="words"
                    placeholderTextColor={palette.gray}
                  />
                </View>
              )}

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Adresse Email</Text>
                <TextInput
                  style={styles.input}
                  placeholder="nom@exemple.mg"
                  value={email}
                  onChangeText={setEmail}
                  keyboardType="email-address"
                  autoCapitalize="none"
                  placeholderTextColor={palette.gray}
                />
              </View>

              <View style={styles.inputGroup}>
                <Text style={styles.inputLabel}>Mot de passe</Text>
                <TextInput
                  style={styles.input}
                  placeholder="••••••••"
                  value={password}
                  onChangeText={setPassword}
                  secureTextEntry
                  placeholderTextColor={palette.gray}
                />
              </View>

              {!isLogin && (
                <View style={styles.roleSection}>
                  <Text style={styles.inputLabel}>Rôle dans l'écosystème</Text>
                  <View style={styles.roleList}>
                    {roles.map((r) => (
                      <TouchableOpacity
                        key={r.id}
                        activeOpacity={0.7}
                        style={[styles.roleChip, role === r.id && styles.roleChipActive]}
                        onPress={() => setRole(r.id)}
                      >
                        <Text style={[styles.roleChipText, role === r.id && styles.roleChipTextActive]}>
                          {r.label}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>
              )}

              <TouchableOpacity 
                style={styles.button} 
                onPress={handleAuth}
                disabled={loading}
                activeOpacity={0.8}
              >
                {loading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.buttonText}>
                    {isLogin ? 'Se connecter' : 'Créer mon identité'}
                  </Text>
                )}
              </TouchableOpacity>

              <TouchableOpacity 
                style={styles.switchButton} 
                onPress={() => setIsLogin(!isLogin)}
              >
                <Text style={styles.switchText}>
                  {isLogin 
                    ? "Nouveau ici ? S'inscrire au réseau" 
                    : "Déjà inscrit ? Se connecter"}
                </Text>
              </TouchableOpacity>
            </View>
          </FadeInView>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: palette.background },
  inner: { flex: 1 },
  scrollContent: { padding: 30, paddingBottom: 50 },
  header: { marginTop: 40, marginBottom: 40, alignItems: 'center' },
  logoBadge: {
    width: 70,
    height: 70,
    borderRadius: 22,
    backgroundColor: palette.accent,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 15,
    shadowColor: palette.accent,
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.3,
    shadowRadius: 15,
    elevation: 8,
  },
  logoText: { color: '#fff', fontSize: 28, fontWeight: '900' },
  logoTitle: { 
    fontSize: 16, 
    fontWeight: '800', 
    color: palette.accent, 
    letterSpacing: 5, 
    marginBottom: 10,
    textTransform: 'uppercase'
  },
  title: { fontSize: 32, fontWeight: '800', color: palette.ink, marginBottom: 8, textAlign: 'center' },
  subtitle: { fontSize: 15, color: palette.gray, textAlign: 'center', lineHeight: 22, maxWidth: 280 },
  form: { width: '100%' },
  inputGroup: { marginBottom: 20 },
  inputLabel: { fontSize: 14, fontWeight: '700', color: palette.ink, marginBottom: 8, marginLeft: 4 },
  input: { 
    backgroundColor: palette.surface, 
    padding: 18, 
    borderRadius: 18, 
    fontSize: 16,
    borderWidth: 1.5,
    borderColor: palette.lightGray,
    color: palette.ink,
  },
  roleSection: { marginBottom: 30 },
  roleList: { flexDirection: 'row', flexWrap: 'wrap', marginTop: 5 },
  roleChip: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 14,
    backgroundColor: palette.lightGray,
    borderWidth: 1.5,
    borderColor: 'transparent',
    marginRight: 10,
    marginBottom: 10,
  },
  roleChipActive: {
    backgroundColor: palette.accentTransparent,
    borderColor: palette.accent,
  },
  roleChipText: { fontSize: 13, color: palette.gray, fontWeight: '700' },
  roleChipTextActive: { color: palette.accent },
  button: { 
    backgroundColor: palette.accent, 
    padding: 20, 
    borderRadius: 20, 
    alignItems: 'center',
    marginTop: 10,
    shadowColor: palette.accent,
    shadowOffset: { width: 0, height: 8 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 6
  },
  buttonText: { color: '#fff', fontWeight: '800', fontSize: 17 },
  switchButton: { marginTop: 25, alignItems: 'center', padding: 10 },
  switchText: { color: palette.accent, fontSize: 14, fontWeight: '700' }
});
