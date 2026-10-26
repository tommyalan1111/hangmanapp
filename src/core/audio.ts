type OscillatorShape = OscillatorType;

class SoundEngine {
  private context: AudioContext | null = null;
  private enabled = true;

  setEnabled(enabled: boolean): void {
    this.enabled = enabled;
  }

  unlock(): void {
    if (!this.enabled) return;
    this.getContext()?.resume().catch(() => undefined);
  }

  private getContext(): AudioContext | null {
    if (!this.enabled) return null;
    if (this.context) return this.context;
    const AudioContextClass =
      window.AudioContext ??
      (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!AudioContextClass) return null;
    try {
      this.context = new AudioContextClass();
      return this.context;
    } catch {
      return null;
    }
  }

  private tone(
    frequency: number,
    startOffset: number,
    duration: number,
    shape: OscillatorShape = "sine",
    volume = 0.045,
    endFrequency?: number,
  ): void {
    const context = this.getContext();
    if (!context) return;
    const start = context.currentTime + startOffset;
    const oscillator = context.createOscillator();
    const gain = context.createGain();
    oscillator.type = shape;
    oscillator.frequency.setValueAtTime(frequency, start);
    if (endFrequency) {
      oscillator.frequency.exponentialRampToValueAtTime(Math.max(30, endFrequency), start + duration);
    }
    gain.gain.setValueAtTime(0.0001, start);
    gain.gain.exponentialRampToValueAtTime(volume, start + 0.012);
    gain.gain.exponentialRampToValueAtTime(0.0001, start + duration);
    oscillator.connect(gain);
    gain.connect(context.destination);
    oscillator.start(start);
    oscillator.stop(start + duration + 0.02);
  }

  tap(): void {
    this.tone(320, 0, 0.05, "triangle", 0.025, 220);
  }

  correct(): void {
    this.tone(523.25, 0, 0.14, "sine", 0.045);
    this.tone(783.99, 0.09, 0.2, "sine", 0.04);
  }

  wrong(): void {
    this.tone(150, 0, 0.2, "sawtooth", 0.035, 82);
    this.tone(92, 0.03, 0.18, "triangle", 0.025, 62);
  }

  hint(): void {
    this.tone(880, 0, 0.1, "sine", 0.03);
    this.tone(1174.66, 0.08, 0.14, "sine", 0.025);
  }

  win(): void {
    [523.25, 659.25, 783.99, 1046.5].forEach((note, index) => {
      this.tone(note, index * 0.1, 0.3, "sine", 0.045);
    });
    this.tone(1318.51, 0.42, 0.45, "sine", 0.03);
  }

  lose(): void {
    [392, 349.23, 293.66, 196].forEach((note, index) => {
      this.tone(note, index * 0.14, 0.4, "triangle", 0.035);
    });
  }
}

export const sounds = new SoundEngine();
