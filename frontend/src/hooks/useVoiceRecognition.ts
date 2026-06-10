import { useState, useEffect, useCallback } from 'react';

// Declare standard Window types to include SpeechRecognition
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export function useVoiceRecognition() {
  const [isListening, setIsListening] = useState(false);
  const [activeField, setActiveField] = useState<string | null>(null);
  const [recognition, setRecognition] = useState<any>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        const reco = new SpeechRecognition();
        reco.continuous = false;
        reco.interimResults = false;
        reco.lang = 'en-US';
        setRecognition(reco);
      } else {
        console.warn("Speech Recognition API not supported in this browser.");
      }
    }
  }, []);

  const startListening = useCallback((fieldId: string, onResult: (text: string) => void) => {
    if (!recognition) {
      alert("Voice input is not supported in your browser (try Chrome/Edge/Safari).");
      return;
    }

    // Stop if already listening to something else
    if (isListening) {
      recognition.stop();
      if (activeField === fieldId) {
        setIsListening(false);
        setActiveField(null);
        return; // acts as a toggle
      }
    }

    setActiveField(fieldId);
    setIsListening(true);

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onResult(transcript);
      setIsListening(false);
      setActiveField(null);
    };

    recognition.onerror = (event: any) => {
      if (event.error !== 'aborted') {
        console.error("Speech recognition error:", event.error);
      }
      setIsListening(false);
      setActiveField(null);
    };

    recognition.onend = () => {
      setIsListening(false);
      setActiveField(null);
    };

    try {
      recognition.start();
    } catch (e: any) {
      if (e.name !== 'InvalidStateError') {
        console.error("Failed to start speech recognition:", e);
      }
    }
  }, [recognition, isListening, activeField]);

  return {
    isListening,
    activeField,
    startListening,
    hasSupport: !!recognition
  };
}
