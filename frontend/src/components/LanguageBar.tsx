import React from 'react';
import { LANGUAGES, LANG_NAMES } from '../types';

interface LanguageBarProps {
  patientLang: string;
  doctorLang: string;
  onPatientLangChange: (lang: string) => void;
  onDoctorLangChange: (lang: string) => void;
  onSwap: () => void;
}

export const LanguageBar: React.FC<LanguageBarProps> = ({
  patientLang,
  doctorLang,
  onPatientLangChange,
  onDoctorLangChange,
  onSwap
}) => {
  return (
    <div id="lang-bar">
      <label>PATIENT speaks</label>
      <select 
        value={patientLang} 
        onChange={(e) => onPatientLangChange(e.target.value)}
      >
        {LANGUAGES.map(lang => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
      </select>

      <button id="swap-btn" onClick={onSwap} title="Swap languages">
        ⇄
      </button>

      <label>DOCTOR speaks</label>
      <select 
        value={doctorLang} 
        onChange={(e) => onDoctorLangChange(e.target.value)}
      >
        {LANGUAGES.map(lang => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
};