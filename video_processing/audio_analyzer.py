import librosa
import numpy as np
from typing import List, Dict, Any, Tuple
import soundfile as sf

class AudioAnalyzer:
    def __init__(self, sample_rate: int = 22050):
        """
        Initialize the audio analyzer.
        
        Args:
            sample_rate (int): Sample rate for audio processing
        """
        self.sample_rate = sample_rate
        
    def extract_audio(self, video_path: str) -> Tuple[np.ndarray, int]:
        """
        Extract audio from a video file.
        
        Args:
            video_path (str): Path to the video file
            
        Returns:
            Tuple[np.ndarray, int]: Audio data and sample rate
        """
        y, sr = librosa.load(video_path, sr=self.sample_rate)
        return y, sr
    
    def detect_applause(self, 
                       audio_data: np.ndarray,
                       threshold: float = 0.5,
                       min_duration: float = 0.5) -> List[Dict[str, Any]]:
        """
        Detect applause in audio data.
        
        Args:
            audio_data (np.ndarray): Audio data
            threshold (float): Detection threshold
            min_duration (float): Minimum duration for applause detection
            
        Returns:
            List[Dict[str, Any]]: List of applause segments
        """
        # Compute onset strength
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=self.sample_rate)
        
        # Detect onsets
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=self.sample_rate,
            wait=0.1,
            pre_avg=0.1,
            post_avg=0.1,
            pre_max=0.1,
            post_max=0.1
        )
        
        # Convert frames to time
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sample_rate)
        
        # Group nearby onsets into applause segments
        applause_segments = []
        current_segment = None
        
        for time in onset_times:
            if current_segment is None:
                current_segment = {'start': time, 'end': time}
            elif time - current_segment['end'] < 0.5:  # Merge if less than 0.5s apart
                current_segment['end'] = time
            else:
                duration = current_segment['end'] - current_segment['start']
                if duration >= min_duration:
                    applause_segments.append(current_segment)
                current_segment = {'start': time, 'end': time}
        
        # Add final segment if exists
        if current_segment is not None:
            duration = current_segment['end'] - current_segment['start']
            if duration >= min_duration:
                applause_segments.append(current_segment)
        
        return applause_segments
    
    def analyze_crowd_reaction(self,
                             audio_data: np.ndarray,
                             window_size: float = 1.0) -> List[Dict[str, Any]]:
        """
        Analyze crowd reactions in audio data.
        
        Args:
            audio_data (np.ndarray): Audio data
            window_size (float): Size of analysis window in seconds
            
        Returns:
            List[Dict[str, Any]]: List of crowd reaction segments
        """
        # Compute spectrogram
        D = librosa.stft(audio_data)
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        
        # Compute energy in different frequency bands
        freqs = librosa.fft_frequencies(sr=self.sample_rate)
        low_band = np.mean(S_db[(freqs >= 20) & (freqs <= 200)], axis=0)
        mid_band = np.mean(S_db[(freqs >= 200) & (freqs <= 2000)], axis=0)
        high_band = np.mean(S_db[(freqs >= 2000) & (freqs <= 20000)], axis=0)
        
        # Convert to time
        times = librosa.times_like(low_band)
        
        # Detect significant energy changes
        reactions = []
        window_frames = int(window_size * self.sample_rate / 2048)  # 2048 is default hop length
        
        for i in range(0, len(times) - window_frames, window_frames):
            window_low = low_band[i:i+window_frames]
            window_mid = mid_band[i:i+window_frames]
            window_high = high_band[i:i+window_frames]
            
            # Calculate energy metrics
            energy_low = np.mean(window_low)
            energy_mid = np.mean(window_mid)
            energy_high = np.mean(window_high)
            
            # Detect significant reactions
            if energy_mid > -30 or energy_high > -40:  # Thresholds for crowd noise
                reactions.append({
                    'start_time': times[i],
                    'end_time': times[i + window_frames],
                    'energy_low': float(energy_low),
                    'energy_mid': float(energy_mid),
                    'energy_high': float(energy_high)
                })
        
        return reactions
    
    def save_audio_segment(self,
                          audio_data: np.ndarray,
                          start_time: float,
                          end_time: float,
                          output_path: str) -> str:
        """
        Save a segment of audio to a file.
        
        Args:
            audio_data (np.ndarray): Audio data
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            output_path (str): Path to save the audio segment
            
        Returns:
            str: Path to the saved audio segment
        """
        start_sample = int(start_time * self.sample_rate)
        end_sample = int(end_time * self.sample_rate)
        
        segment = audio_data[start_sample:end_sample]
        sf.write(output_path, segment, self.sample_rate)
        
        return output_path 