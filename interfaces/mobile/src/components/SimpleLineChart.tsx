import React from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';
import Svg, { Path, Polyline } from 'react-native-svg';
import { palette } from '../theme/palette';

interface SimpleLineChartProps {
  data: number[];
  height?: number;
  width?: number;
}

export const SimpleLineChart = ({ data, height = 150, width }: SimpleLineChartProps) => {
  const chartWidth = width || Dimensions.get('window').width - 80;
  if (!data || data.length < 2) return null;

  const max = Math.max(...data) || 1;
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = data.map((val, i) => {
    const x = (i / (data.length - 1)) * chartWidth;
    const y = height - ((val - min) / range) * (height - 20) - 10;
    return `${x},${y}`;
  }).join(' ');

  return (
    <View style={[styles.container, { height, width: chartWidth }]}>
      <Svg height={height} width={chartWidth}>
        <Polyline
          points={points}
          fill="none"
          stroke={palette.accent}
          strokeWidth="4"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </Svg>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    marginVertical: 10,
    alignSelf: 'center',
  },
});
