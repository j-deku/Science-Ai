import { useRef, useEffect } from "react";

export default function useSoundEffects() {
  const soundFiles = [
    "/sounds/single-key.mp3",
    "/sounds/key2.wav",
  ];

  const audios = useRef([]);

  useEffect(() => {
    // PRELOAD + DECODE AUDIO BEFORE ANY TYPING
    audios.current = soundFiles.map((src) => {
      const a = new Audio(src);
      a.preload = "auto";
      a.volume = 0.35;

      // Silent warm-play to remove delay
      a.muted = true;
      a.play().finally(() => {
        a.pause();
        a.muted = false;
      });

      return a;
    });
  }, []);

  function playTypeSound() {
    if (!audios.current.length) return;

    const sound =
      audios.current[Math.floor(Math.random() * audios.current.length)];

    sound.currentTime = 0;
    sound.play().catch(() => {});
  }

  return { playTypeSound };
}
