import React, { useState, useEffect } from 'react';
import { View, Text, Button, Image, StyleSheet, ScrollView, Alert } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import axios from 'axios';

export default function HomeScreen() {
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [faceShape, setFaceShape] = useState('');
  const [overlayImages, setOverlayImages] = useState<string[]>([]);

  useEffect(() => {
    (async () => {
      const { status: cameraStatus } = await ImagePicker.requestCameraPermissionsAsync();
      const { status: galleryStatus } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      console.log('Camera:', cameraStatus, '| Gallery:', galleryStatus);
      if (cameraStatus !== 'granted' || galleryStatus !== 'granted') {
        Alert.alert('Permission Required', 'Camera and gallery access is needed.');
      }
    })();
  }, []);

  const handlePick = async (from: 'camera' | 'gallery') => {
    try {
      const result = from === 'camera'
        ? await ImagePicker.launchCameraAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images, quality: 1 })
        : await ImagePicker.launchImageLibraryAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images, quality: 1 });

      if (!result.canceled && result.assets && result.assets.length > 0) {
        const uri = result.assets[0].uri;
        setImageUri(uri);
        setFaceShape('');
        setOverlayImages([]);
      } else {
        console.log('Image picking cancelled');
      }
    } catch (err) {
      console.error('Error opening picker:', err);
      Alert.alert('Error', 'Could not open image picker.');
    }
  };

  const uploadImage = async () => {
    if (!imageUri) return;

    const formData = new FormData();
    formData.append('file', {
      uri: imageUri,
      type: 'image/jpeg',
      name: 'photo.jpg',
    } as any);

    try {
      const res = await axios.post('http://10.253.180.120:8000/predict', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setFaceShape(res.data.face_shape);
      setOverlayImages(res.data.images);
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'Something went wrong while uploading.');
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Glassio</Text>

      <View style={styles.buttonGroup}>
        <Button title="Take Photo" onPress={() => handlePick('camera')} />
        <Button title="Pick from Gallery" onPress={() => handlePick('gallery')} />
      </View>

      {imageUri && <Image source={{ uri: imageUri }} style={styles.image} />}
      {imageUri && <Button title="Upload & Predict" onPress={uploadImage} />}
      {faceShape !== '' && <Text style={styles.result}>Face Shape: {faceShape}</Text>}

      <View style={styles.overlayContainer}>
        {overlayImages.map((img, index) => (
          <Image
            key={index}
            source={{ uri: `data:image/png;base64,${img}` }}
            style={styles.overlay}
          />
        ))}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingTop: 50,
    alignItems: 'center',
    paddingBottom: 100,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  buttonGroup: {
    flexDirection: 'row',
    gap: 10,
    marginBottom: 20,
  },
  image: {
    width: 250,
    height: 250,
    borderRadius: 10,
    marginBottom: 10,
  },
  result: {
    fontSize: 18,
    marginTop: 20,
  },
  overlayContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    marginTop: 20,
    gap: 10,
  },
  overlay: {
    width: 100,
    height: 100,
    margin: 5,
    borderRadius: 8,
  },
});
