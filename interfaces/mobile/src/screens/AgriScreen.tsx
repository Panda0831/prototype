import React, { useState, useEffect } from 'react';
import {
  ScrollView,
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  FlatList,
  Image,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import * as ImagePicker from 'expo-image-picker';
import { palette } from '../theme/palette';
import * as Api from '../services/api';
const { agriService, authService, algoService } = Api;
import { Leaf, Navigation, PlusCircle, RefreshCw, ShoppingCart, DollarSign, User, Search, ShieldCheck, Brain, CheckCircle, Award, Camera, ImageIcon } from '../components/Icons';
import { FadeInView, SkeletonLoader } from '../components/Animations';
import { BobModal } from '../components/BobModal';

export default function AgriScreen({ route }: any) {
  console.log("[DEBUG Agri] route.params:", JSON.stringify(route.params));
  const [manualPublicKey, setManualPublicKey] = useState('');
  const user = route.params?.user;
  const activeKey = user?.public_key || manualPublicKey;
  console.log("[DEBUG Agri] activeKey:", activeKey);
  const [activeTab, setActiveTab] = useState<'scanner' | 'tracking' | 'transport' | 'harvest'>('scanner');
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);

  // Vanilla AI Scanner State
  const [scanDistrict, setScanDistrict] = useState('Sambava');
  const [scanLength, setScanLength] = useState('18.5');
  const [scanMoisture, setScanMoisture] = useState('32.0');
  const [scanVanillin, setScanVanillin] = useState('2.3');
  const [scanMaturity, setScanMaturity] = useState('96.0');
  const [scanWeight, setScanWeight] = useState('5.0');
  const [scanMold, setScanMold] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [aiAnalysis, setAiAnalysis] = useState<any>(null);

  // Photo bord-champ (Expo Image Picker)
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [photoBase64, setPhotoBase64] = useState<string | null>(null);
  const [photoLoading, setPhotoLoading] = useState(false);
  
  // Transport State
  const [destination, setDestination] = useState('');
  const [isDestinationSelection, setIsDestinationSelection] = useState(false);
  const [optimizedPath, setOptimizedPath] = useState<string[] | null>(null);
  const [districts, setDistricts] = useState<any[]>([]);
  
  // Form fields
  const [productType, setProductType] = useState('Vanille');
  const [district, setDistrict] = useState('');
  const [districtModalVisible, setDistrictModalVisible] = useState(false);
  const [weight, setWeight] = useState('');
  const [quality, setQuality] = useState('Premium');
  
  // Tracking fields
  const [lots, setLots] = useState<any[]>([]);

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

  const runInspect = async (values: {
    district: string;
    bean_length_cm: number;
    moisture_pct: number;
    vanillin_pct: number;
    maturity_pct: number;
    mold_detected: boolean;
    image_base64?: string | null;
  }) => {
    try {
      const payload = {
        ...values,
        image_base64: values.image_base64 !== undefined ? values.image_base64 : photoBase64,
      };
      const res = await agriService.inspectVanilla(payload);
      if (res.inspection) {
        const insp = res.inspection;
        if (insp.maturity_pct !== undefined) {
          setScanMaturity(String(insp.maturity_pct));
        }
        setAiAnalysis({
          maturity: insp.maturity_pct,
          grade: insp.quality_grade.replace(/_/g, ' '),
          fairPrice: `${insp.estimated_fair_price_mga_per_kg.toLocaleString('fr-FR')} MGA/kg`,
          fobUsd: `$${insp.estimated_fob_export_usd_per_kg} /kg`,
          status: insp.status === 'APPROVED_FOR_BLOCKCHAIN' ? insp.iso_compliance : 'REJETÉ (Non Conforme ISO)',
          isApproved: insp.status === 'APPROVED_FOR_BLOCKCHAIN',
          hash: insp.inspection_hash.substring(0, 16) + '...',
          imageSha256: insp.vision?.image_sha256,
          visionGrade: insp.vision?.predicted_grade ? insp.vision.predicted_grade.replace(/_/g, ' ') : undefined,
          greenRatio: insp.vision?.green_ratio !== undefined ? (insp.vision.green_ratio * 100).toFixed(1) : undefined,
          ebonyRatio: insp.vision?.dark_ebony_ratio !== undefined ? (insp.vision.dark_ebony_ratio * 100).toFixed(1) : undefined,
          sheenIndex: insp.vision?.sheen_index !== undefined ? (insp.vision.sheen_index * 100).toFixed(1) : undefined,
          visionMaturity: insp.vision?.reliable ? insp.vision.estimated_maturity_pct : undefined,
          visionMold: insp.vision?.reliable ? insp.vision.mold_risk_pct : undefined,
          visionReliable: insp.vision?.reliable,
          visionFlags: insp.vision?.flags || [],
          alertMessage: insp.status === 'REJECTED' ? (insp.explanations?.[0] || 'Lot non conforme') : null,
        });
      }
    } catch (e) {
      console.log('Inspect error:', e);
    }
  };

  const handleTakePhoto = async () => {
    try {
      setPhotoLoading(true);
      let result;
      if (Platform.OS === 'web') {
        result = await ImagePicker.launchImageLibraryAsync({
          allowsEditing: true,
          aspect: [4, 3],
          quality: 0.6,
          base64: true,
        });
      } else {
        const perm = await ImagePicker.requestCameraPermissionsAsync();
        if (!perm.granted) {
          Alert.alert('Permission requise', 'Accès caméra nécessaire pour analyser les gousses bord-champ.');
          setPhotoLoading(false);
          return;
        }
        result = await ImagePicker.launchCameraAsync({
          allowsEditing: true,
          aspect: [4, 3],
          quality: 0.6,
          base64: true,
        });
      }

      if (result && !result.canceled && result.assets && result.assets.length > 0) {
        const asset = result.assets[0];
        setPhotoUri(asset.uri);
        const b64 = asset.base64 ? `data:image/jpeg;base64,${asset.base64}` : null;
        setPhotoBase64(b64);
        await runInspect({
          district: scanDistrict,
          bean_length_cm: parseFloat(scanLength) || 18.0,
          moisture_pct: parseFloat(scanMoisture) || 32.0,
          vanillin_pct: parseFloat(scanVanillin) || 2.2,
          maturity_pct: parseFloat(scanMaturity) || 96.0,
          mold_detected: scanMold,
          image_base64: b64,
        });
      }
    } catch (err) {
      console.error('Erreur caméra:', err);
      Alert.alert('Erreur', 'Impossible de capturer la photo.');
    } finally {
      setPhotoLoading(false);
    }
  };

  const handlePickGallery = async () => {
    try {
      setPhotoLoading(true);
      if (Platform.OS !== 'web') {
        const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (!perm.granted) {
          Alert.alert('Permission requise', 'Accès galerie requis pour sélectionner une photo de vanille.');
          setPhotoLoading(false);
          return;
        }
      }
      const result = await ImagePicker.launchImageLibraryAsync({
        allowsEditing: true,
        aspect: [4, 3],
        quality: 0.6,
        base64: true,
      });
      if (result && !result.canceled && result.assets && result.assets.length > 0) {
        const asset = result.assets[0];
        setPhotoUri(asset.uri);
        const b64 = asset.base64 ? `data:image/jpeg;base64,${asset.base64}` : null;
        setPhotoBase64(b64);
        await runInspect({
          district: scanDistrict,
          bean_length_cm: parseFloat(scanLength) || 18.0,
          moisture_pct: parseFloat(scanMoisture) || 32.0,
          vanillin_pct: parseFloat(scanVanillin) || 2.2,
          maturity_pct: parseFloat(scanMaturity) || 96.0,
          mold_detected: scanMold,
          image_base64: b64,
        });
      }
    } catch (err) {
      console.error('Erreur sélection photo:', err);
      Alert.alert('Erreur', 'Impossible de charger la photo.');
    } finally {
      setPhotoLoading(false);
    }
  };

  const clearPhoto = () => {
    setPhotoUri(null);
    setPhotoBase64(null);
    handleLiveInspect(null);
  };

  const applyPreset = (preset: 'gourmet' | 'standard' | 'immature') => {
    const values = preset === 'gourmet'
      ? { district: 'Sambava', bean_length_cm: 18.5, moisture_pct: 32.0, vanillin_pct: 2.3, maturity_pct: 96.0, mold_detected: false }
      : preset === 'standard'
        ? { district: 'Antalaha', bean_length_cm: 15.2, moisture_pct: 28.0, vanillin_pct: 1.7, maturity_pct: 88.0, mold_detected: false }
        : { district: 'Andapa', bean_length_cm: 9.8, moisture_pct: 52.0, vanillin_pct: 0.7, maturity_pct: 48.0, mold_detected: false };

    setScanDistrict(values.district);
    setScanLength(String(values.bean_length_cm));
    setScanMoisture(String(values.moisture_pct));
    setScanVanillin(String(values.vanillin_pct));
    setScanMaturity(String(values.maturity_pct));
    setScanMold(values.mold_detected);
    setAiAnalysis(null);
    runInspect(values);
  };

  const handleLiveInspect = (customB64?: string | null) => runInspect({
    district: scanDistrict,
    bean_length_cm: parseFloat(scanLength) || 18.0,
    moisture_pct: parseFloat(scanMoisture) || 32.0,
    vanillin_pct: parseFloat(scanVanillin) || 2.2,
    maturity_pct: parseFloat(scanMaturity) || 96.0,
    mold_detected: scanMold,
    image_base64: customB64 !== undefined ? customB64 : photoBase64,
  });

  const handleSealVanilla = async () => {
    setScanning(true);
    try {
      const res = await agriService.sealVanillaPassport({
        owner_id: activeKey || 'ANONYMOUS_PRODUCER',
        district: scanDistrict,
        weight: parseFloat(scanWeight) || 5.0,
        bean_length_cm: parseFloat(scanLength) || 18.0,
        moisture_pct: parseFloat(scanMoisture) || 32.0,
        vanillin_pct: parseFloat(scanVanillin) || 2.2,
        mold_detected: scanMold,
        maturity_pct: parseFloat(scanMaturity) || 96.0,
        image_base64: photoBase64,
      });
      fetchData();
      Alert.alert(
        '🏆 Passeport Scellé en Blockchain !',
        `Lot ID : ${res.lot?.id}\nQualité : ${res.inspection?.quality_grade}\nPrix Garanti : ${res.inspection?.estimated_fair_price_mga_per_kg} MGA/kg\nBloc #${res.block_index} confirmé !`
      );
    } catch (error) {
      Alert.alert('Erreur', 'Échec du scellage sur la blockchain');
    } finally {
      setScanning(false);
    }
  };

  const fetchData = async () => {
    console.log("[DEBUG Agri] fetchData start. activeKey:", activeKey);
    if (!activeKey) {
      console.log("[DEBUG Agri] fetchData skipped: activeKey is empty");
      setInitialLoading(false);
      return;
    }
    try {
      const res = await agriService.getAllLots();
      console.log("[DEBUG Agri] Received lots count:", res.length);
      
      // Nettoyage des clés pour comparaison
      const normalize = (k: string) => k.replace(/[^a-zA-Z0-9]/g, '').toLowerCase();
      const myNormalizedKey = normalize(activeKey || '');
      console.log("[DEBUG Agri] myNormalizedKey:", myNormalizedKey);

      // On ne garde que les lots appartenant à l'utilisateur
      const myLots = res.filter((lot: any) => {
        const lotOwnerRaw = String(lot.owner_id || '');
        const lotOwnerNorm = normalize(lotOwnerRaw);
        const isMatch = lotOwnerNorm === myNormalizedKey;
        
        console.log('[DEBUG Agri] Lot ' + lot.id + ' Match: ' + isMatch);
        return isMatch;
      });
      
      setLots(myLots.reverse());
      
      const [districtsData, usersData] = await Promise.all([
        algoService.getDistricts(),
        authService.getUsers()
      ]);
      setDistricts(districtsData);
      setUsers(usersData);
    } catch (error) {
      console.error(error);
    } finally {
      setInitialLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const data = await authService.getUsers();
      setUsers(data);
    } catch (error) {
      console.error("Erreur lors de la récupération des utilisateurs", error);
    }
  };

  useEffect(() => {
    fetchData();
    fetchUsers();
  }, []);

  const handleHarvest = async () => {
    if (!district || !weight) return;
    setLoading(true);
    try {
      await agriService.recordHarvest({
        owner_id: activeKey || 'ANONYMOUS',
        product_type: productType,
        district,
        weight: parseFloat(weight),
        quality
      });
      Alert.alert('Succès', 'Récolte enregistrée sur la blockchain');
      setDistrict('');
      setWeight('');
      fetchData();
    } catch (error) {
      Alert.alert('Erreur', 'Échec de l’enregistrement');
    } finally {
      setLoading(false);
    }
  };

  const handleSell = async () => {
    if (!buyerId || !price || !selectedLot) return;
    setLoading(true);
    try {
      await agriService.sellLot({
        lot_id: selectedLot.id,
        buyer_id: buyerId,
        price: parseFloat(price),
        seller_id: route.params?.user?.public_key 
      });
      setSaleModalVisible(false);
      setBuyerId('');
      setBuyerName('');
      setPrice('');
      fetchData();
      Alert.alert('Félicitations', 'Vente enregistrée en blockchain !');
    } catch (error) {
      Alert.alert('Erreur', 'La vente a échoué. Vérifiez que vous êtes le propriétaire du lot.');
    } finally {
      setLoading(false);
    }
  };

  const selectBuyer = (user: any) => {
    setBuyerId(user.public_key);
    setBuyerName(user.username);
    setShowUserList(false);
    setUserSearch('');
  };

  const filteredUsers = users.filter(u => 
    u.username.toLowerCase().includes(userSearch.toLowerCase()) ||
    u.public_key.toLowerCase().includes(userSearch.toLowerCase())
  );

  const handleOptimizeTransport = async () => {
    if (!selectedLot || !destination) {
      Alert.alert('Erreur', 'Sélectionnez un lot et une destination');
      return;
    }

    setLoading(true);
    try {
      const res = await agriService.optimizeTransport({
        lot_id: selectedLot.id,
        destination: destination
      });
      
      if (res.path) {
        setOptimizedPath(res.path);
      }
      
      Alert.alert('Succès', 'Trajet optimisé via A* et enregistré !');
      fetchData();
    } catch (err) {
      Alert.alert('Erreur', 'Erreur lors de l\'optimisation du transport.');
    } finally {
      setLoading(false);
    }
  };

  const openSaleModal = (lot: any) => {
    setSelectedLot(lot);
    setSaleModalVisible(true);
  };

  const renderLotItem = ({ item }: { item: any }) => (
    <FadeInView style={styles.card}>
      <View style={styles.cardHeader}>
        <Text style={styles.lotId}>{item.id}</Text>
        <View style={[styles.statusBadge, item.status === 'CERTIFIE_CONFORME' && { backgroundColor: 'rgba(34, 197, 94, 0.15)' }]}>
          <Text style={[styles.statusText, item.status === 'CERTIFIE_CONFORME' && { color: '#16a34a' }]}>
            {item.status === 'CERTIFIE_CONFORME' ? '✓ ISO 5565-1' : item.status}
          </Text>
        </View>
      </View>
      <Text style={styles.productTitle}>{item.product_type} - {item.weight}kg</Text>
      <Text style={styles.lotInfo}>Origine: {item.district_origin}</Text>
      <Text style={styles.lotInfo}>Qualité: {item.quality}</Text>
      {item.passport_hash && (
        <View style={styles.passportBadge}>
          <ShieldCheck color="#16a34a" size={14} />
          <Text style={styles.passportText}>Passeport: {item.passport_hash.substring(0, 18)}...</Text>
        </View>
      )}
      
      <View style={styles.lotActions}>
        <TouchableOpacity style={styles.actionBtn} onPress={() => { setSelectedLot(item); setActiveTab('transport'); }}>
           <Navigation color={palette.accent} size={16} />
           <Text style={styles.actionBtnText}>Trajet A*</Text>
        </TouchableOpacity>
        
        {item.status !== 'VENDU' && (
          <TouchableOpacity style={[styles.actionBtn, styles.sellBtn]} onPress={() => openSaleModal(item)}>
            <ShoppingCart color="white" size={16} />
            <Text style={[styles.actionBtnText, { color: 'white' }]}>Vendre</Text>
          </TouchableOpacity>
        )}
      </View>
    </FadeInView>
  );

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Leaf color="#10b981" size={28} />
        <View style={{ marginLeft: 10 }}>
          <Text style={styles.title}>Hazo Lova Agri-AI</Text>
          <Text style={{ fontSize: 11, color: palette.gray, fontWeight: '600' }}>IA Vision & Blockchain • Filière Vanille</Text>
        </View>
      </View>

      {!activeKey && (
        <View style={{ padding: 15, backgroundColor: palette.surface, marginHorizontal: 15, marginTop: 10, borderRadius: 12 }}>
          <Text style={styles.label}>Clé Publique Planteur (Mode Démo)</Text>
          <TextInput 
            style={styles.input} 
            value={manualPublicKey} 
            onChangeText={setManualPublicKey} 
            placeholder="0x..." 
            placeholderTextColor={palette.gray} 
          />
        </View>
      )}

      <View style={styles.tabBar}>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'scanner' && styles.activeTab]} 
          onPress={() => setActiveTab('scanner')}
        >
          <Text style={[styles.tabText, activeTab === 'scanner' && styles.activeTabText]}>AI Scanner</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'tracking' && styles.activeTab]} 
          onPress={() => setActiveTab('tracking')}
        >
          <Text style={[styles.tabText, activeTab === 'tracking' && styles.activeTabText]}>Passeports</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'transport' && styles.activeTab]} 
          onPress={() => setActiveTab('transport')}
        >
          <Text style={[styles.tabText, activeTab === 'transport' && styles.activeTabText]}>Logistique</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={[styles.tab, activeTab === 'harvest' && styles.activeTab]} 
          onPress={() => setActiveTab('harvest')}
        >
          <Text style={[styles.tabText, activeTab === 'harvest' && styles.activeTabText]}>Classique</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.content}>
        {activeTab === 'scanner' && (
          <ScrollView style={{ flex: 1 }} showsVerticalScrollIndicator={false}>
            {/* CAMERA AR HUD CONTAINER */}
            <View style={styles.cameraFrame}>
              <View style={styles.cameraHeader}>
                <View style={styles.recBadge}>
                  <View style={styles.recDot} />
                  <Text style={styles.recText}>AR LIVE • ISO 5565-1</Text>
                </View>
                <Text style={styles.cameraDistrict}>{scanDistrict} (SAVA)</Text>
              </View>

              {/* TARGET RETICLE BRACKETS */}
              <View style={styles.reticleContainer}>
                {photoUri ? (
                  <Image source={{ uri: photoUri }} style={styles.capturedPhotoBg} resizeMode="cover" />
                ) : null}

                <View style={[styles.corner, styles.cornerTL]} />
                <View style={[styles.corner, styles.cornerTR]} />
                <View style={[styles.corner, styles.cornerBL]} />
                <View style={[styles.corner, styles.cornerBR]} />

                {/* AUGMENTED REALITY DETECTION BOX (Fidèle à la Figure 2) */}
                <View style={[styles.arBox, aiAnalysis && !aiAnalysis.isApproved && styles.arBoxRejected]}>
                  <View style={styles.arBoxHeader}>
                    <View style={[styles.arLiveDot, aiAnalysis && !aiAnalysis.isApproved && { backgroundColor: '#ef4444' }]} />
                    <Text style={styles.arTitle}>
                      {photoUri ? 'Photo bord-champ scellée :' : 'Augmented reality detection:'}
                    </Text>
                  </View>
                  {aiAnalysis ? (
                    <>
                      <Text style={styles.arItem}>• Maturity: <Text style={styles.arBold}>{aiAnalysis.maturity}%</Text></Text>
                      <Text style={styles.arItem}>• Grade: <Text style={styles.arBold}>{aiAnalysis.grade}</Text></Text>
                      <Text style={styles.arItem}>• Fair Price: <Text style={styles.arBold}>{aiAnalysis.fairPrice}</Text></Text>
                      <Text style={styles.arItem}>• Status: <Text style={styles.arBold}>{aiAnalysis.status}</Text></Text>
                      {aiAnalysis.visionGrade && (
                        <Text style={styles.arItem}>
                          • Vision IA: <Text style={styles.arBold}>{aiAnalysis.visionGrade}</Text> (vert: {aiAnalysis.greenRatio}%, ébène: {aiAnalysis.ebonyRatio}%, lustre: {aiAnalysis.sheenIndex}%)
                        </Text>
                      )}
                      {aiAnalysis.visionMaturity !== undefined && (
                        <Text style={styles.arItem}>
                          • Mesure Optique: <Text style={styles.arBold}>{aiAnalysis.visionMaturity}% mat. · {aiAnalysis.visionMold}% risque moisissure</Text>
                        </Text>
                      )}
                      {aiAnalysis.imageSha256 && (
                        <Text style={styles.arItem}>
                          • SHA-256 Photo: <Text style={styles.arBold}>{aiAnalysis.imageSha256.substring(0, 10)}...</Text>
                        </Text>
                      )}
                      {!aiAnalysis.isApproved && (
                        <Text style={[styles.arItem, { color: '#f87171', fontWeight: 'bold', marginTop: 4 }]}>
                          ⚠️ {aiAnalysis.alertMessage || 'Cueillette prématurée / Non conforme'}
                        </Text>
                      )}
                    </>
                  ) : (
                    <Text style={styles.arItem}>• Viser les gousses ou capturer une photo…</Text>
                  )}
                </View>
              </View>

              <View style={styles.cameraFooter}>
                <Text style={styles.hashText}>Hash: {aiAnalysis?.hash || '—'}</Text>
                <Text style={styles.fobText}>Export: {aiAnalysis?.fobUsd || '—'}</Text>
              </View>
            </View>

            {/* CAMERA SHUTTER & CONTROLS */}
            <View style={styles.cameraControlsContainer}>
              <TouchableOpacity 
                style={styles.galleryBtn} 
                onPress={handlePickGallery}
                disabled={photoLoading}
              >
                <ImageIcon color="#94a3b8" size={18} />
                <Text style={styles.galleryBtnText}>Galerie</Text>
              </TouchableOpacity>

              <TouchableOpacity 
                style={[styles.shutterBtn, photoLoading && { opacity: 0.6 }]} 
                onPress={handleTakePhoto}
                disabled={photoLoading}
              >
                {photoLoading ? (
                  <ActivityIndicator color="#090d16" />
                ) : (
                  <View style={styles.shutterInner}>
                    <Camera color="#090d16" size={24} />
                  </View>
                )}
              </TouchableOpacity>

              {photoUri ? (
                <TouchableOpacity style={styles.resetPhotoBtn} onPress={clearPhoto}>
                  <RefreshCw color="#ef4444" size={15} />
                  <Text style={styles.resetPhotoText}>Effacer</Text>
                </TouchableOpacity>
              ) : (
                <View style={{ width: 70 }} />
              )}
            </View>

            {/* PRESETS DEMO */}
            <View style={styles.presetSection}>
              <Text style={styles.presetTitle}>Presets Échantillons Réels :</Text>
              <View style={styles.presetRow}>
                <TouchableOpacity style={styles.presetBtn} onPress={() => applyPreset('gourmet')}>
                  <Text style={styles.presetBtnText}>⭐ Gourmet A (96%)</Text>
                </TouchableOpacity>
                <TouchableOpacity style={styles.presetBtn} onPress={() => applyPreset('standard')}>
                  <Text style={styles.presetBtnText}>🌿 Standard TK (88%)</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.presetBtn, { borderColor: '#ef4444' }]} onPress={() => applyPreset('immature')}>
                  <Text style={[styles.presetBtnText, { color: '#ef4444' }]}>⚠️ Immature (Rejet)</Text>
                </TouchableOpacity>
              </View>
            </View>

            {/* PARAMETERS FORM & SEALLING */}
            <FadeInView style={styles.form}>
              <Text style={styles.sectionTitle}>Certification & Scellage Blockchain</Text>
              
              <View style={styles.rowTwo}>
                <View style={{ flex: 1, marginRight: 8 }}>
                  <Text style={styles.label}>District d'Origine</Text>
                  <TextInput 
                    style={styles.input} 
                    value={scanDistrict} 
                    onChangeText={(t) => { setScanDistrict(t); handleLiveInspect(); }} 
                  />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.label}>Poids du Lot (kg)</Text>
                  <TextInput 
                    style={styles.input} 
                    value={scanWeight} 
                    onChangeText={setScanWeight} 
                    keyboardType="numeric" 
                  />
                </View>
              </View>

              <View style={styles.rowTwo}>
                <View style={{ flex: 1, marginRight: 8 }}>
                  <Text style={styles.label}>Longueur Gousse (cm)</Text>
                  <TextInput 
                    style={styles.input} 
                    value={scanLength} 
                    onChangeText={(t) => { setScanLength(t); handleLiveInspect(); }} 
                    keyboardType="numeric" 
                  />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={styles.label}>Maturité (%)</Text>
                  <TextInput 
                    style={styles.input} 
                    value={scanMaturity} 
                    onChangeText={(t) => { setScanMaturity(t); handleLiveInspect(); }} 
                    keyboardType="numeric" 
                  />
                </View>
              </View>

              <TouchableOpacity 
                style={[styles.sealButton, scanning && { opacity: 0.7 }]} 
                onPress={handleSealVanilla} 
                disabled={scanning}
              >
                {scanning ? (
                  <ActivityIndicator color="white" />
                ) : (
                  <>
                    <ShieldCheck color="white" size={20} />
                    <Text style={styles.sealButtonText}>SCELLER PASSEPORT EN BLOCKCHAIN</Text>
                  </>
                )}
              </TouchableOpacity>
            </FadeInView>
          </ScrollView>
        )}

        {activeTab === 'harvest' && (
          <ScrollView style={{ flex: 1 }} showsVerticalScrollIndicator={false}>
            <FadeInView style={styles.form}>
              <Text style={styles.sectionTitle}>Enregistrer une Récolte</Text>
              
              <Text style={styles.label}>Nom du Produit</Text>
              <TextInput 
                style={styles.input} 
                value={productType} 
                onChangeText={setProductType} 
                placeholder="Ex: Poivre Noir, Riz Makalioka..." 
                placeholderTextColor={palette.gray} 
              />

              <Text style={styles.label}>District</Text>
              <TouchableOpacity style={styles.input} onPress={() => setDistrictModalVisible(true)}>
                <Text style={district ? {color: palette.ink} : {color: palette.gray}}>
                  {district || "Sélectionner un district"}
                </Text>
              </TouchableOpacity>
              
              <Text style={styles.label}>Poids (kg)</Text>
              <TextInput style={styles.input} value={weight} onChangeText={setWeight} keyboardType="numeric" placeholder="Ex: 50.5" placeholderTextColor={palette.gray} />

              <TouchableOpacity style={styles.button} onPress={handleHarvest} disabled={loading}>
                {loading ? <ActivityIndicator color="white" /> : <><PlusCircle color="white" size={20} /><Text style={styles.buttonText}>Inscrire en Blockchain</Text></>}
              </TouchableOpacity>
            </FadeInView>
          </ScrollView>
        )}

        {activeTab === 'tracking' && (
          <View style={{ flex: 1 }}>
            {initialLoading ? (
              <View style={{ gap: 10 }}>
                <SkeletonLoader style={{ height: 120 }} />
                <SkeletonLoader style={{ height: 120 }} />
              </View>
            ) : (
              <FlatList
                data={lots}
                renderItem={renderLotItem}
                keyExtractor={(item) => item.id}
                ListEmptyComponent={<Text style={styles.empty}>Aucun lot enregistré</Text>}
                onRefresh={fetchData}
                refreshing={loading}
              />
            )}
          </View>
        )}

        {activeTab === 'transport' && (
          <ScrollView style={{ flex: 1 }} showsVerticalScrollIndicator={false}>
            <FadeInView style={styles.form}>
               <Text style={styles.sectionTitle}>Optimisation Logistique (A*)</Text>
               <Text style={styles.label}>Sélectionner un Lot</Text>
               <View style={styles.input}>
                  <ScrollView style={{ maxHeight: 150 }}>
                    {lots.map((item) => (
                      <TouchableOpacity key={item.id} onPress={() => setSelectedLot(item)} style={{ padding: 10, borderBottomWidth: 1, borderColor: '#eee' }}>
                         <Text style={{ color: palette.ink }}>{item.id} - {item.product_type} ({item.district_origin})</Text>
                      </TouchableOpacity>
                    ))}
                  </ScrollView>
               </View>
               <Text style={styles.label}>Destination</Text>
               <TouchableOpacity 
                 style={styles.input} 
                 onPress={() => { setIsDestinationSelection(true); setDistrictModalVisible(true); }}
               >
                  <Text style={destination ? {color: palette.ink} : {color: palette.gray}}>
                    {destination || "Sélectionner une destination"}
                  </Text>
               </TouchableOpacity>
               
               <TouchableOpacity style={styles.button} onPress={handleOptimizeTransport} disabled={loading}>
                {loading ? <ActivityIndicator color="white" /> : <Text style={styles.buttonText}>Optimiser Chemin</Text>}
               </TouchableOpacity>

               {optimizedPath && (
                  <View style={{ marginTop: 20, padding: 15, backgroundColor: '#f0f9ff', borderRadius: 12 }}>
                    <Text style={{ fontSize: 14, fontWeight: 'bold', color: palette.accent }}>Chemin calculé :</Text>
                    <Text style={{ color: palette.ink, marginTop: 5 }}>{optimizedPath.join(' -> ')}</Text>
                  </View>
               )}
            </FadeInView>
          </ScrollView>
        )}
      </View>

      <BobModal 
        visible={districtModalVisible} 
        onClose={() => { setDistrictModalVisible(false); setIsDestinationSelection(false); }}
        title="Sélectionner un District"
      >
        <FlatList
          data={districts}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <TouchableOpacity 
              style={styles.userSelectItem}
              onPress={() => { 
                if (isDestinationSelection) {
                  setDestination(item.nom);
                } else {
                  setDistrict(item.nom);
                }
                setDistrictModalVisible(false); 
                setIsDestinationSelection(false);
              }}
            >
              <Text style={styles.userSelectName}>{item.nom}</Text>
            </TouchableOpacity>
          )}
        />
      </BobModal>

      <BobModal 
        visible={saleModalVisible} 
        onClose={() => setSaleModalVisible(false)}
        title="Finaliser la Vente"
      >
        <View style={styles.saleForm}>
          <Text style={styles.lotSummary}>{selectedLot?.product_type} - {selectedLot?.weight}kg</Text>
          
          <View style={styles.inputGroup}>
            <Search color={palette.gray} size={18} style={styles.inputIcon} />
            <TextInput 
              style={styles.modalInput} 
              placeholder="Rechercher l'Acheteur..." 
              value={buyerName || userSearch}
              onChangeText={(txt) => {
                if (buyerName) { setBuyerName(''); setBuyerId(''); }
                setUserSearch(txt);
                setShowUserList(true);
              }}
              onFocus={() => setShowUserList(true)}
              placeholderTextColor={palette.gray}
            />
          </View>

          {showUserList && userSearch.length > 0 && (
            <View style={styles.userDropdown}>
              {filteredUsers.slice(0, 5).map((u) => (
                <TouchableOpacity 
                  key={u.public_key} 
                  style={styles.userSelectItem}
                  onPress={() => selectBuyer(u)}
                >
                  <View style={styles.userAvatarSmall}>
                    <Text style={styles.avatarTextSmall}>{u.username[0].toUpperCase()}</Text>
                  </View>
                  <View>
                    <Text style={styles.userSelectName}>{u.username}</Text>
                    <Text style={styles.userSelectKey}>{u.public_key.substring(0, 15)}...</Text>
                  </View>
                </TouchableOpacity>
              ))}
              {filteredUsers.length === 0 && <Text style={styles.noUser}>Aucun utilisateur trouvé</Text>}
            </View>
          )}

          <View style={styles.inputGroup}>
            <DollarSign color={palette.gray} size={18} style={styles.inputIcon} />
            <TextInput 
              style={styles.modalInput} 
              placeholder="Prix de vente (MGA)" 
              value={price}
              onChangeText={setPrice}
              keyboardType="numeric"
              placeholderTextColor={palette.gray}
            />
          </View>

          <TouchableOpacity 
            style={[styles.button, { marginTop: 20 }]} 
            onPress={handleSell}
            disabled={loading || !buyerId}
          >
            {loading ? <ActivityIndicator color="white" /> : <Text style={styles.buttonText}>Confirmer la Vente</Text>}
          </TouchableOpacity>
        </View>
      </BobModal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: palette.background },
  header: { flexDirection: 'row', alignItems: 'center', padding: 20, backgroundColor: palette.surface },
  title: { fontSize: 24, fontWeight: 'bold', marginLeft: 10, color: palette.ink },
  tabBar: { flexDirection: 'row', backgroundColor: palette.surface, borderBottomWidth: 1, borderBottomColor: palette.lightGray },
  tab: { flex: 1, padding: 15, alignItems: 'center' },
  activeTab: { borderBottomWidth: 3, borderBottomColor: palette.accent },
  tabText: { color: palette.gray, fontWeight: '600' },
  activeTabText: { color: palette.accent },
  content: { flex: 1, padding: 20 },
  form: { backgroundColor: palette.surface, borderRadius: 20, padding: 20, elevation: 2 },
  sectionTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 15, color: palette.ink },
  label: { fontSize: 14, fontWeight: '600', marginBottom: 8, color: palette.gray },
  input: { 
    borderWidth: 1.5, 
    borderColor: palette.lightGray, 
    borderRadius: 12, 
    padding: 12, 
    marginBottom: 15, 
    backgroundColor: palette.background,
    color: palette.ink
  },
  chipRow: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 5 },
  chip: { paddingHorizontal: 15, paddingVertical: 8, borderRadius: 20, backgroundColor: palette.lightGray, marginRight: 10, marginBottom: 10 },
  chipActive: { backgroundColor: palette.accentTransparent, borderWidth: 1, borderColor: palette.accent },
  chipText: { fontSize: 12, color: palette.gray, fontWeight: 'bold' },
  chipTextActive: { color: palette.accent },
  button: { 
    backgroundColor: palette.accent, 
    borderRadius: 14, 
    padding: 15, 
    flexDirection: 'row', 
    justifyContent: 'center', 
    alignItems: 'center',
    marginTop: 10
  },
  buttonText: { color: 'white', fontWeight: 'bold', marginLeft: 10 },
  card: { 
    backgroundColor: palette.surface, 
    borderRadius: 18, 
    padding: 18, 
    marginBottom: 15, 
    elevation: 2,
    shadowColor: palette.ink,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 5
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 },
  lotId: { fontSize: 12, color: palette.gray, fontWeight: 'bold' },
  statusBadge: { backgroundColor: palette.accentTransparent, paddingHorizontal: 10, paddingVertical: 4, borderRadius: 10 },
  statusText: { fontSize: 10, color: palette.accent, fontWeight: '900' },
  productTitle: { fontSize: 18, fontWeight: '900', color: palette.ink },
  lotInfo: { fontSize: 13, color: palette.gray, marginTop: 4 },
  lotActions: { 
    flexDirection: 'row', 
    marginTop: 15, 
    paddingTop: 15, 
    borderTopWidth: 1, 
    borderTopColor: palette.lightGray,
    gap: 10
  },
  actionBtn: { 
    flex: 1, 
    flexDirection: 'row', 
    alignItems: 'center', 
    justifyContent: 'center',
    paddingVertical: 10,
    borderRadius: 10,
    backgroundColor: palette.accentTransparent,
  },
  actionBtnText: { fontSize: 13, fontWeight: 'bold', marginLeft: 8, color: palette.accent },
  sellBtn: { backgroundColor: palette.accent },
  empty: { textAlign: 'center', marginTop: 40, color: palette.gray },
  
  // Modal Styles
  saleForm: { width: '100%' },
  lotSummary: { fontSize: 16, fontWeight: 'bold', color: palette.ink, marginBottom: 20, textAlign: 'center' },
  inputGroup: { 
    flexDirection: 'row', 
    alignItems: 'center', 
    backgroundColor: palette.background,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: palette.lightGray,
    marginBottom: 15,
    paddingHorizontal: 12,
  },
  inputIcon: { marginRight: 10 },
  modalInput: { flex: 1, paddingVertical: 12, color: palette.ink, fontSize: 15 },
  
  // User selection styles
  userDropdown: {
    backgroundColor: palette.background,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: palette.lightGray,
    marginBottom: 15,
    maxHeight: 200,
    overflow: 'hidden'
  },
  userSelectItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: palette.lightGray
  },
  userAvatarSmall: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: palette.accent,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12
  },
  avatarTextSmall: { color: 'white', fontWeight: 'bold', fontSize: 12 },
  userSelectName: { fontSize: 14, fontWeight: 'bold', color: palette.ink },
  userSelectKey: { fontSize: 10, color: palette.gray },
  noUser: { padding: 15, textAlign: 'center', color: palette.gray, fontSize: 12 },

  // Vanilla AR Scanner Styles
  cameraFrame: {
    backgroundColor: '#090d16',
    borderRadius: 20,
    padding: 16,
    marginBottom: 15,
    borderWidth: 1.5,
    borderColor: '#1e293b',
    minHeight: 280,
    justifyContent: 'space-between',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  cameraHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  recBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(239, 68, 68, 0.2)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  recDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#ef4444',
    marginRight: 6,
  },
  recText: {
    color: '#fca5a5',
    fontSize: 10,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  cameraDistrict: {
    color: '#94a3b8',
    fontSize: 11,
    fontWeight: '700',
  },
  reticleContainer: {
    height: 180,
    position: 'relative',
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 10,
  },
  corner: {
    position: 'absolute',
    width: 22,
    height: 22,
    borderColor: '#10b981',
  },
  cornerTL: { top: 0, left: 10, borderTopWidth: 3, borderLeftWidth: 3 },
  cornerTR: { top: 0, right: 10, borderTopWidth: 3, borderRightWidth: 3 },
  cornerBL: { bottom: 0, left: 10, borderBottomWidth: 3, borderLeftWidth: 3 },
  cornerBR: { bottom: 0, right: 10, borderBottomWidth: 3, borderRightWidth: 3 },
  arBox: {
    backgroundColor: 'rgba(15, 23, 42, 0.88)',
    borderWidth: 1.5,
    borderColor: '#10b981',
    borderRadius: 14,
    padding: 14,
    width: '88%',
    shadowColor: '#10b981',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 6,
  },
  arBoxRejected: {
    borderColor: '#ef4444',
    shadowColor: '#ef4444',
  },
  arBoxHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 6,
  },
  arLiveDot: {
    width: 7,
    height: 7,
    borderRadius: 4,
    backgroundColor: '#10b981',
    marginRight: 6,
  },
  arTitle: {
    color: '#34d399',
    fontSize: 11,
    fontWeight: '800',
    letterSpacing: 0.5,
  },
  arItem: {
    color: '#e2e8f0',
    fontSize: 12,
    lineHeight: 18,
    fontWeight: '500',
  },
  arBold: {
    fontWeight: '800',
    color: '#ffffff',
  },
  cameraFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderTopWidth: 1,
    borderTopColor: '#1e293b',
    paddingTop: 8,
  },
  hashText: {
    color: '#64748b',
    fontSize: 9,
    fontFamily: 'monospace',
  },
  fobText: {
    color: '#38bdf8',
    fontSize: 10,
    fontWeight: '700',
  },
  presetSection: {
    marginBottom: 15,
  },
  presetTitle: {
    fontSize: 12,
    fontWeight: '700',
    color: palette.gray,
    marginBottom: 8,
  },
  presetRow: {
    flexDirection: 'row',
    gap: 8,
  },
  presetBtn: {
    flex: 1,
    backgroundColor: palette.surface,
    borderWidth: 1,
    borderColor: palette.lightGray,
    borderRadius: 10,
    paddingVertical: 8,
    paddingHorizontal: 4,
    alignItems: 'center',
  },
  presetBtnText: {
    fontSize: 11,
    fontWeight: '700',
    color: palette.ink,
  },
  rowTwo: {
    flexDirection: 'row',
  },
  sealButton: {
    backgroundColor: '#10b981',
    borderRadius: 14,
    paddingVertical: 14,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 8,
  },
  sealButtonText: {
    color: '#ffffff',
    fontWeight: '900',
    fontSize: 13,
    marginLeft: 8,
    letterSpacing: 0.5,
  },
  passportBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 6,
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  passportText: {
    color: '#15803d',
    fontSize: 11,
    fontWeight: '700',
    marginLeft: 5,
    fontFamily: 'monospace',
  },
  capturedPhotoBg: {
    ...StyleSheet.absoluteFillObject,
    borderRadius: 14,
    opacity: 0.5,
  },
  cameraControlsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    marginBottom: 16,
  },
  shutterBtn: {
    width: 66,
    height: 66,
    borderRadius: 33,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 3.5,
    borderColor: '#10b981',
    shadowColor: '#10b981',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.35,
    shadowRadius: 6,
    elevation: 5,
  },
  shutterInner: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#10b981',
    justifyContent: 'center',
    alignItems: 'center',
  },
  galleryBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1e293b',
    paddingVertical: 9,
    paddingHorizontal: 12,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#334155',
  },
  galleryBtnText: {
    color: '#cbd5e1',
    fontSize: 12,
    fontWeight: '700',
    marginLeft: 5,
  },
  resetPhotoBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(239, 68, 68, 0.12)',
    paddingVertical: 9,
    paddingHorizontal: 11,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(239, 68, 68, 0.25)',
  },
  resetPhotoText: {
    color: '#ef4444',
    fontSize: 12,
    fontWeight: '700',
    marginLeft: 4,
  },
});
