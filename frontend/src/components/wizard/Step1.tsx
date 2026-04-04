'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, Calendar, Users, Wallet } from 'lucide-react';
import { useTripStore } from '@/store/useTripStore';
import { Chip } from '@/components/ui/Chip';
import { Button } from '@/components/ui/Button';

const destinations = [
  { label: 'Cairo & Giza', emoji: '🏛️' },
  { label: 'Alexandria', emoji: '🌊' },
  { label: 'Luxor', emoji: '🏺' },
  { label: 'Aswan', emoji: '🌴' },
  { label: 'Sharm El Sheikh', emoji: '🐠' },
  { label: 'Hurghada', emoji: '🏖️' },
  { label: 'Dahab', emoji: '🤿' },
];

const budgetOptions = [
  '500-1000 EGP',
  '1000-2000 EGP',
  '2000-5000 EGP',
  '5000-10000 EGP',
  '10000+ EGP',
];

interface Step1Props {
  onNext: () => void;
}

export function Step1({ onNext }: Step1Props) {
  const { input, setInput } = useTripStore();

  const toggleDestination = (dest: string) => {
    const current = input.destinations || [];
    const updated = current.includes(dest)
      ? current.filter((d) => d !== dest)
      : [...current, dest];
    if (updated.length > 0) {
      setInput({ destinations: updated });
    }
  };

  const handleDateChange = (field: 'startDate' | 'endDate', value: string) => {
    setInput({ [field]: value });
  };

  const handleGroupSizeChange = (delta: number) => {
    const newSize = Math.max(1, Math.min(20, (input.groupSize || 2) + delta));
    setInput({ groupSize: newSize });
  };

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-2 flex items-center gap-3">
          <MapPin className="w-6 h-6 text-amber" />
          Where are you going?
        </h2>
        <p className="text-offwhite-muted mb-4">Select your destinations</p>
        <div className="flex flex-wrap gap-3">
          {destinations.map((dest) => (
            <Chip
              key={dest.label}
              label={`${dest.emoji} ${dest.label}`}
              selected={(input.destinations || []).includes(dest.label)}
              onClick={() => toggleDestination(dest.label)}
            />
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold mb-2 flex items-center gap-3">
          <Calendar className="w-6 h-6 text-amber" />
          When are you traveling?
        </h2>
        <p className="text-offwhite-muted mb-4">Select your date range</p>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-offwhite-muted mb-2">Start Date</label>
            <input
              type="date"
              value={input.startDate || ''}
              onChange={(e) => handleDateChange('startDate', e.target.value)}
              className="w-full bg-charcoal-lighter border border-border rounded-xl px-4 py-3 text-offwhite focus:border-amber focus:outline-none transition-colors"
            />
          </div>
          <div>
            <label className="block text-sm text-offwhite-muted mb-2">End Date</label>
            <input
              type="date"
              value={input.endDate || ''}
              onChange={(e) => handleDateChange('endDate', e.target.value)}
              className="w-full bg-charcoal-lighter border border-border rounded-xl px-4 py-3 text-offwhite focus:border-amber focus:outline-none transition-colors"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-2xl font-bold mb-2 flex items-center gap-3">
            <Users className="w-6 h-6 text-amber" />
            Group Size
          </h2>
          <div className="flex items-center gap-4 mt-4">
            <button
              onClick={() => handleGroupSizeChange(-1)}
              className="w-12 h-12 rounded-xl bg-charcoal-lighter border border-border text-offwhite text-xl hover:border-amber transition-colors"
            >
              -
            </button>
            <span className="text-3xl font-bold text-amber min-w-[3rem] text-center">
              {input.groupSize || 2}
            </span>
            <button
              onClick={() => handleGroupSizeChange(1)}
              className="w-12 h-12 rounded-xl bg-charcoal-lighter border border-border text-offwhite text-xl hover:border-amber transition-colors"
            >
              +
            </button>
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-bold mb-2 flex items-center gap-3">
            <Wallet className="w-6 h-6 text-amber" />
            Budget
          </h2>
          <div className="flex flex-wrap gap-2 mt-4">
            {budgetOptions.map((budget) => (
              <Chip
                key={budget}
                label={budget}
                selected={input.budget === budget}
                onClick={() => setInput({ budget })}
              />
            ))}
          </div>
        </div>
      </div>

      <div className="flex justify-end pt-4">
        <Button onClick={onNext} size="lg">
          Next: Your Vibe
        </Button>
      </div>
    </div>
  );
}
