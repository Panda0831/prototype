import React from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { Check } from './Icons';
import { palette } from '../theme/palette';

interface TimelineRowProps {
  title: string;
  subtitle: string;
  time: string;
  isLast?: boolean;
}

export default function TimelineRow({ title, subtitle, time, isLast }: TimelineRowProps) {
  return (
    <View style={[styles.timelineRow, isLast && { borderBottomWidth: 0 }]}>
      <View style={styles.timelineLeft}>
        <View style={styles.timelineCheck}>
          <Check color={palette.accent} size={14} />
        </View>
        <View>
          <Text style={styles.timelineTitle}>{title}</Text>
          <Text style={styles.timelineSubtitle}>{subtitle}</Text>
        </View>
      </View>
      <Text style={styles.timelineTime}>{time}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  timelineRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(24, 36, 54, 0.05)',
  },
  timelineLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  timelineCheck: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: palette.accentTransparent,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 12,
  },
  timelineTitle: {
    fontSize: 14,
    color: palette.ink,
    fontWeight: '700',
  },
  timelineSubtitle: {
    fontSize: 12,
    color: palette.gray,
    marginTop: 2,
  },
  timelineTime: {
    fontSize: 11,
    color: palette.gray,
    fontWeight: '600',
  },
});
