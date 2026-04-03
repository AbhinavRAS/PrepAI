import React, { useState, useRef, useEffect } from 'react';

export default function AudioPlayer({ audioUrl, text, autoPlay = false }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const audioRef = useRef(null);

  useEffect(() => {
    if (autoPlay && audioUrl && audioRef.current) {
      audioRef.current.play().catch(console.error);
    }
  }, [autoPlay, audioUrl]);

  // Add loading state and error handling
const [audioError, setAudioError] = useState(false);

const togglePlay = () => {
  if (audioRef.current) {
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play().catch(error => {
        console.error("Audio play error:", error);
        setAudioError(true);
      });
    }
    setIsPlaying(!isPlaying);
  }
};

  const repeatAudio = () => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
      audioRef.current.play().catch(console.error);
      setIsPlaying(true);
    }
  };

  // Update the return statement to show audio error
  if (!audioUrl) {
    return (
      <div className="flex items-center space-x-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
        <span className="text-yellow-600">📝 Question:</span>
        <p className="text-sm text-gray-700 font-medium">{text}</p>
        {audioError && (
          <p className="text-xs text-red-600 mt-1">⚠️ Audio unavailable</p>
        )}
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-3 p-3 bg-blue-50 rounded-lg">
      <button
        onClick={togglePlay}
        disabled={isLoading}
        className={`p-2 rounded-full transition-colors ${
          isPlaying 
            ? 'bg-red-500 hover:bg-red-600' 
            : 'bg-blue-500 hover:bg-blue-600'
        } text-white`}
      >
        {isLoading ? (
          <div className="animate-spin">⏳</div>
        ) : isPlaying ? (
          '⏸️'
        ) : (
          '▶️'
        )}
      </button>

      <button
        onClick={repeatAudio}
        disabled={isLoading}
        className="p-2 rounded-full bg-green-500 hover:bg-green-600 text-white transition-colors"
        title="Repeat Question"
      >
        🔁
      </button>
      
      <audio
        ref={audioRef}
        src={audioUrl}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onEnded={() => setIsPlaying(false)}
        preload="metadata"
      />
      
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-900">{text}</p>
      </div>
    </div>
  );
}