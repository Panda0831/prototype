import 'react-native-gesture-handler';
import { enableScreens } from 'react-native-screens';
enableScreens();
import React from 'react';
import AppNavigator from './src/navigation/AppNavigator';

console.log('LOG: App.tsx loading');

export default function App() {
  console.log('LOG: App rendering with Navigator');
  return <AppNavigator />;
}
