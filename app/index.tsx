import React, { useState, useEffect } from 'react';
import { ReactNode } from 'react';
import { LinearGradient } from 'expo-linear-gradient';
import {
  View, Text, StyleSheet,
  ScrollView, Alert, ActivityIndicator, Pressable, Animated
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import axios from 'axios';
import { BlurView } from 'expo-blur';
import * as Animatable from 'react-native-animatable';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';

export default function HomeScreen() {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [faceShape, setFaceShape] = useState('');
  const [overlayImages, setOverlayImages] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [scale] = useState(new Animated.Value(1));
  const fadeAnim = useState(new Animated.Value(0))[0];
  const scaleAnim = useState(new Animated.Value(0.8))[0];

  useEffect(() => {
    Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true,
      }),
      Animated.spring(scaleAnim, {
        toValue: 1,
        friction: 4,
        useNativeDriver: true,
      }),
    ]).start();
  }, []);

  useEffect(() => {
    (async () => {
      const { status: cam } = await ImagePicker.requestCameraPermissionsAsync();
      const { status: gal } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (cam !== 'granted' || gal !== 'granted') {
        Alert.alert('Permissions needed', 'Allow camera and gallery access.');
      }
    })();
  }, []);

  const animatePress = () => {
    Animated.sequence([
      Animated.timing(scale, {
        toValue: 0.96,
        duration: 80,
        useNativeDriver: true,
      }),
      Animated.timing(scale, {
        toValue: 1,
        duration: 80,
        useNativeDriver: true,
      }),
    ]).start();
  };

  const handlePick = async (from: 'camera' | 'gallery') => {
    animatePress();
    try {
      const result = from === 'camera'
        ? await ImagePicker.launchCameraAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images, quality: 1 })
        : await ImagePicker.launchImageLibraryAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images, quality: 1 });

      if (!result.canceled && result.assets?.length) {
        setImageUri(result.assets[0].uri);
        setFaceShape('');
        setOverlayImages([]);
      }
    } catch (err) {
      console.error(err);
      Alert.alert('Error', 'Could not open image picker.');
    }
  };

  const uploadImage = async () => {
    animatePress();
    if (!imageUri) return;
    setLoading(true);

    const formData = new FormData();
    formData.append('file', {
      uri: imageUri,
      type: 'image/jpeg',
      name: 'upload.jpg',
    } as any);

    try {
      const res = await axios.post('http://10.253.180.120:8000/predict', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 8000,
      });

      setFaceShape(res.data.face_shape);
      setOverlayImages(res.data.images || []);
    } catch (err) {
      console.error(err);
      Alert.alert('Upload Failed', 'Could not connect to backend or request timed out.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <LinearGradient colors={['#0f0c29', '#302b63', '#24243e']} style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={styles.container}>
        <Animated.Image
          source={require('../assets/logo.png')}
          style={[styles.logo, { opacity: fadeAnim, transform: [{ scale: scaleAnim }] }]}
        />

        

        <View style={styles.buttonRow}>
          <GlassButton
            icon={<Ionicons name="camera-outline" size={28} color="white" />}
            label="Take Photo"
            onPress={() => handlePick('camera')}
          />
          <GlassButton
            icon={<MaterialIcons name="photo-library" size={28} color="white" />}
            label="Pick from Gallery"
            onPress={() => handlePick('gallery')}
          />
        </View>

        {imageUri && (
          <>
            <Animatable.Image
              animation="fadeInUp"
              duration={700}
              source={{ uri: imageUri }}
              style={styles.image}
            />
            <GlassButton
              icon={<Ionicons name="cloud-upload-outline" size={24} color="white" />}
              label="Upload & Predict"
              onPress={uploadImage}
              wide
            />
          </>
        )}

        {loading && <ActivityIndicator size="large" color="#007AFF" style={{ marginTop: 20 }} />}
        {faceShape && (
          <Animatable.Text
            animation="fadeIn"
            delay={200}
            style={styles.result}
          >
            Detected Shape: {faceShape}
          </Animatable.Text>
        )}

        <View style={styles.overlayContainer}>
          {overlayImages.map((img, index) => (
            <Animatable.Image
              key={index}
              animation="zoomIn"
              delay={index * 100}
              source={{ uri: `data:image/png;base64,${img}` }}
              style={styles.overlay}
            />
          ))}
        </View>
      </ScrollView>
    </LinearGradient>
  );
}

function GlassButton({
  icon,
  label,
  onPress,
  wide = false,
}: {
  icon: ReactNode;
  label: string;
  onPress: () => void;
  wide?: boolean;
}) {
  return (
    <Pressable onPress={onPress} style={({ pressed }) => [
      styles.glassWrapper,
      wide && styles.wide,
      pressed && { opacity: 0.85 },
    ]}>
      <BlurView intensity={50} tint="dark" style={styles.glass}>
        {icon}
        <Text style={styles.glassText}>{label}</Text>
      </BlurView>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  logo: {
    width: 140,
    height: 140,
    marginBottom: 10,
    resizeMode: 'contain',
  },
  container: {
    flexGrow: 1,
    justifyContent: 'flex-start',
    alignItems: 'center',
    paddingTop: 100,
    paddingBottom: 50,
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 30,
    fontWeight: '800',
    color: '#fff',
    marginBottom: 40,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 20,
    marginTop: 40,
    marginBottom: 20,
    flexWrap: 'wrap',
    justifyContent: 'center',
  },
  glassWrapper: {
    borderRadius: 18,
    overflow: 'hidden',
    marginVertical: 10,
  },
  wide: {
    width: 240,
    alignSelf: 'center',
  },
  glass: {
    width: 140,
    height: 120,
    borderRadius: 18,
    backgroundColor: 'rgba(255,255,255,0.05)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 15,
  },
  glassText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginTop: 8,
    textAlign: 'center',
  },
  image: {
    width: 260,
    height: 260,
    borderRadius: 16,
    marginTop: 15,
  },
  result: {
    fontSize: 18,
    fontWeight: '600',
    color: '#fff',
    marginTop: 20,
  },
  overlayContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    marginTop: 20,
    gap: 12,
  },
  overlay: {
    width: 100,
    height: 100,
    borderRadius: 10,
  },
});