"""
Translation Service for Krishi Sakhi
Handles Malayalam Speech-to-Text and Text-to-Speech translation
Enhanced with specialized Malayalam models and audio denoising
"""
import torch
import logging
import tempfile
import os
import numpy as np
import scipy.signal
from transformers import (
    AutoProcessor, 
    SeamlessM4Tv2Model, 
    VitsTokenizer, 
    VitsModel, 
    set_seed,
    Wav2Vec2ForCTC,
    Wav2Vec2Processor,
    WhisperForConditionalGeneration,
    WhisperProcessor
)

# Handle optional audio dependencies gracefully
try:
    import torchaudio
    import soundfile as sf
    from pydub import AudioSegment
    AUDIO_SUPPORT = True
    logger = logging.getLogger(__name__)
    logger.info("Audio support enabled with torchaudio and soundfile")
except ImportError as e:
    AUDIO_SUPPORT = False
    logger = logging.getLogger(__name__)
    logger.warning(f"Audio support disabled due to missing dependencies: {e}")
except RuntimeError as e:
    if "FFmpeg" in str(e):
        AUDIO_SUPPORT = False
        logger = logging.getLogger(__name__)
        logger.warning(f"Audio support disabled due to FFmpeg issue: {e}")
    else:
        raise

logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.audio_support = AUDIO_SUPPORT
        logger.info(f"Translation service using device: {self.device}")
        logger.info(f"Audio support: {'enabled' if self.audio_support else 'disabled'}")
        
        # Initialize models
        self._load_translation_model()
        self._load_tts_model()
        self._load_malayalam_speech_model()
        self._load_malayalam_text_translation_model()
    
    def _load_translation_model(self):
        """Load SeamlessM4T model for speech-to-text translation"""
        try:
            model_id = "facebook/seamless-m4t-v2-large"
            logger.info("Loading translation model...")
            # Use use_fast=False to avoid the tiktoken conversion issues
            self.processor_trans = AutoProcessor.from_pretrained(model_id, use_fast=False)
            self.model_trans = SeamlessM4Tv2Model.from_pretrained(model_id).to(self.device)
            logger.info("Translation model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load translation model: {e}")
            raise
    
    def _load_tts_model(self):
        """Load Malayalam TTS model"""
        try:
            tts_model_id = "facebook/mms-tts-mal"
            logger.info("Loading TTS model...")
            self.tokenizer_tts = VitsTokenizer.from_pretrained(tts_model_id)
            self.model_tts = VitsModel.from_pretrained(tts_model_id).to(self.device)
            logger.info("TTS model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            raise
    
    def _load_malayalam_speech_model(self):
        """Load specialized Malayalam speech-to-text model"""
        try:
            malayalam_stt_model_id = "gvs/wav2vec2-large-xlsr-malayalam"
            logger.info("Loading Malayalam speech-to-text model...")
            self.malayalam_processor = Wav2Vec2Processor.from_pretrained(malayalam_stt_model_id)
            self.malayalam_model = Wav2Vec2ForCTC.from_pretrained(malayalam_stt_model_id).to(self.device)
            logger.info("Malayalam speech-to-text model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Malayalam speech model: {e}")
            # Fall back to existing model
            logger.warning("Using fallback SeamlessM4T model for Malayalam speech recognition")
            self.malayalam_processor = None
            self.malayalam_model = None
    
    def _load_malayalam_text_translation_model(self):
        """Load specialized Malayalam-to-English text translation model"""
        try:
            malayalam_trans_model_id = "Be-win/whisper-small-malayalam-to-english-bleu"
            logger.info("Loading Malayalam-to-English translation model...")
            self.malayalam_trans_processor = WhisperProcessor.from_pretrained(malayalam_trans_model_id)
            self.malayalam_trans_model = WhisperForConditionalGeneration.from_pretrained(malayalam_trans_model_id).to(self.device)
            logger.info("Malayalam-to-English translation model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Malayalam translation model: {e}")
            # Fall back to existing model
            logger.warning("Using fallback SeamlessM4T model for Malayalam text translation")
            self.malayalam_trans_processor = None
            self.malayalam_trans_model = None
    
    def _denoise_audio(self, audio_tensor, sample_rate):
        """
        Apply noise reduction to improve speech recognition accuracy
        
        Args:
            audio_tensor: Audio waveform tensor
            sample_rate: Sample rate of the audio
            
        Returns:
            Denoised audio tensor
        """
        try:
            # Convert to numpy for processing
            audio_np = audio_tensor.cpu().numpy() if isinstance(audio_tensor, torch.Tensor) else audio_tensor
            
            # Apply band-pass filter to remove noise outside speech frequency range (85-8000 Hz)
            nyquist = sample_rate / 2
            low_freq = 85 / nyquist
            high_freq = min(8000 / nyquist, 0.95)  # Ensure it's below Nyquist frequency
            
            sos = scipy.signal.butter(4, [low_freq, high_freq], btype='band', output='sos')
            filtered_audio = scipy.signal.sosfiltfilt(sos, audio_np)
            
            # Apply spectral gating for noise reduction
            # Calculate noise floor using the first 0.5 seconds (assumed to be quieter)
            noise_sample_length = min(int(0.5 * sample_rate), len(filtered_audio) // 4)
            if noise_sample_length > 0:
                noise_floor = np.std(filtered_audio[:noise_sample_length])
                
                # Apply gentle noise gate - reduce very quiet sounds
                threshold = noise_floor * 2.0
                gate_ratio = 0.3  # Reduce noise by 70%
                
                mask = np.abs(filtered_audio) < threshold
                filtered_audio[mask] *= gate_ratio
            
            # Normalize audio to prevent clipping
            max_val = np.max(np.abs(filtered_audio))
            if max_val > 0:
                filtered_audio = filtered_audio / max_val * 0.95
            
            # Convert back to tensor if needed
            if isinstance(audio_tensor, torch.Tensor):
                return torch.tensor(filtered_audio, dtype=audio_tensor.dtype, device=audio_tensor.device)
            else:
                return filtered_audio
                
        except Exception as e:
            logger.warning(f"Audio denoising failed, using original audio: {e}")
            return audio_tensor
    
    def malayalam_speech_to_malayalam_text(self, audio_file_path):
        """
        Convert Malayalam speech directly to Malayalam text using specialized model
        
        Args:
            audio_file_path (str): Path to audio file
            
        Returns:
            str: Malayalam text
        """
        if not self.audio_support or not self.malayalam_model:
            logger.warning("Malayalam speech-to-text not available, falling back to general model")
            return None
        
        try:
            logger.info(f"Converting Malayalam speech to Malayalam text: {audio_file_path}")
            target_sr = 16000
            
            # Load and preprocess audio
            try:
                # Try to load with pydub first
                audio = AudioSegment.from_file(audio_file_path)
                audio = audio.set_channels(1).set_frame_rate(target_sr)
                audio_tensor = torch.tensor(audio.get_array_of_samples()).float() / (2**15)
                logger.info(f"Audio loaded using pydub: {len(audio_tensor)} samples")
                
            except Exception as e:
                logger.warning(f"Failed to load with pydub: {e}. Trying torchaudio...")
                # Fallback to torchaudio
                audio_tensor, sr = torchaudio.load(audio_file_path)
                if audio_tensor.shape[0] > 1:
                    audio_tensor = torch.mean(audio_tensor, dim=0, keepdim=True)
                if sr != target_sr:
                    audio_tensor = torchaudio.functional.resample(
                        audio_tensor, orig_freq=sr, new_freq=target_sr
                    )
                audio_tensor = audio_tensor.squeeze(0)
                logger.info(f"Audio loaded using torchaudio: {len(audio_tensor)} samples")
            
            # Apply denoising
            audio_tensor = self._denoise_audio(audio_tensor, target_sr)
            
            # Process through Malayalam model
            inputs = self.malayalam_processor(
                audio_tensor.cpu().numpy(), 
                sampling_rate=target_sr, 
                return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                logits = self.malayalam_model(**inputs).logits
                predicted_ids = torch.argmax(logits, dim=-1)
            
            # Decode to Malayalam text
            malayalam_text = self.malayalam_processor.decode(predicted_ids[0])
            
            logger.info(f"Malayalam speech-to-text result: {malayalam_text}")
            return malayalam_text
            
        except Exception as e:
            logger.error(f"Malayalam speech to text conversion failed: {e}")
            return None
    
    def malayalam_text_to_english_text(self, malayalam_text):
        """
        Convert Malayalam text to English text using specialized model
        
        Args:
            malayalam_text (str): Malayalam text to translate
            
        Returns:
            str: English text translation
        """
        if not malayalam_text or not self.malayalam_trans_model:
            logger.warning("Malayalam text translation not available, falling back to general model")
            return None
        
        try:
            logger.info(f"Translating Malayalam text to English: {malayalam_text[:50]}...")
            
            # For Whisper model, we need to simulate audio processing
            # Since Whisper expects audio input, we'll use the general translation model instead
            # This is a limitation of the suggested model architecture
            logger.warning("Whisper model requires audio input, using general translation model for text")
            return None
            
        except Exception as e:
            logger.error(f"Malayalam text to English translation failed: {e}")
            return None
    
    def speech_to_text(self, audio_file_path):
        """
        Enhanced Malayalam speech to English text conversion
        Uses specialized models and denoising for better accuracy
        
        Args:
            audio_file_path (str): Path to audio file (mp3, wav, webm, or other formats)
            
        Returns:
            str: English text translation
        """
        if not self.audio_support:
            logger.warning("Speech-to-text requested but audio support is disabled")
            return "Audio processing unavailable due to missing FFmpeg or audio libraries."
        
        try:
            logger.info(f"Converting speech to text with enhanced pipeline: {audio_file_path}")
            
            # Step 1: Try Malayalam speech → Malayalam text using specialized model
            malayalam_text = self.malayalam_speech_to_malayalam_text(audio_file_path)
            
            if malayalam_text:
                # Step 2: Try Malayalam text → English text using specialized model
                english_text = self.malayalam_text_to_english_text(malayalam_text)
                
                if english_text:
                    logger.info(f"Enhanced pipeline result: {english_text}")
                    return english_text
                else:
                    # Step 2 fallback: Use general translation model for text
                    logger.info("Using general model for Malayalam text → English text")
                    try:
                        inputs = self.processor_trans(
                            text=malayalam_text, src_lang="mal", return_tensors="pt"
                        ).to(self.device)
                        
                        with torch.no_grad():
                            output_tokens = self.model_trans.generate(
                                **inputs, tgt_lang="eng", generate_speech=False
                            )
                        
                        english_text = self.processor_trans.decode(
                            output_tokens[0].tolist()[0], skip_special_tokens=True
                        )
                        
                        logger.info(f"Text translation result: {english_text}")
                        return english_text
                        
                    except Exception as e:
                        logger.error(f"Text translation fallback failed: {e}")
            
            # Fallback: Use original pipeline with denoising
            logger.info("Using original pipeline with denoising as fallback")
            target_sr = 16000
            
            # Load audio using pydub first to handle various formats, then convert to tensor
            try:
                # Try to load with pydub (supports many formats including webm)
                audio = AudioSegment.from_file(audio_file_path)
                audio = audio.set_channels(1).set_frame_rate(target_sr)
                audio_tensor = torch.tensor(audio.get_array_of_samples()).float() / (2**15)
                logger.info(f"Audio loaded using pydub: {len(audio_tensor)} samples")
                
            except Exception as e:
                logger.warning(f"Failed to load with pydub: {e}. Trying torchaudio...")
                # Fallback to torchaudio for standard formats
                audio_tensor, sr = torchaudio.load(audio_file_path)
                if audio_tensor.shape[0] > 1:
                    audio_tensor = torch.mean(audio_tensor, dim=0, keepdim=True)
                if sr != target_sr:
                    audio_tensor = torchaudio.functional.resample(
                        audio_tensor, orig_freq=sr, new_freq=target_sr
                    )
                audio_tensor = audio_tensor.squeeze(0)
                logger.info(f"Audio loaded using torchaudio: {len(audio_tensor)} samples")
            
            # Apply denoising
            audio_tensor = self._denoise_audio(audio_tensor, target_sr)
            
            # Process through model
            audio_inputs = self.processor_trans(
                audios=audio_tensor, return_tensors="pt"
            ).to(self.device)
            
            # Generate translation (speech → text)
            src_lang = "mal"  # Malayalam
            tgt_lang = "eng"  # English
            
            with torch.no_grad():
                output_tokens = self.model_trans.generate(
                    **audio_inputs,
                    tgt_lang=tgt_lang,
                    generate_speech=False
                )
            
            # Decode tokens
            english_text = self.processor_trans.decode(
                output_tokens[0].tolist()[0], skip_special_tokens=True
            )
            
            logger.info(f"Enhanced speech-to-text result: {english_text}")
            return english_text
            
        except Exception as e:
            logger.error(f"Speech to text conversion failed: {e}")
            raise
    
    def text_to_speech(self, english_text):
        """
        Convert English text to Malayalam speech
        
        Args:
            english_text (str): English text to convert
            
        Returns:
            str: Path to generated Malayalam audio file
        """
        if not self.audio_support:
            logger.warning("Text-to-speech requested but audio support is disabled")
            return None
        
        try:
            logger.info(f"Converting text to speech: {english_text[:50]}...")
            
            # Step 1: Translate English → Malayalam text
            inputs = self.processor_trans(
                text=english_text, src_lang="eng", return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                output_tokens = self.model_trans.generate(
                    **inputs, tgt_lang="mal", generate_speech=False
                )
            
            malayalam_text = self.processor_trans.decode(
                output_tokens[0].tolist()[0], skip_special_tokens=True
            )
            logger.info(f"Translated to Malayalam: {malayalam_text}")
            
            # Step 2: Malayalam Text → Speech using MMS-TTS
            set_seed(1234)  # For reproducibility
            
            # Encode text
            tts_inputs = self.tokenizer_tts(
                text=malayalam_text, return_tensors="pt"
            ).to(self.device)
            
            with torch.no_grad():
                tts_outputs = self.model_tts(**tts_inputs)
                waveform = tts_outputs.waveform[0]  # First batch
            
            # Save to temporary file
            sampling_rate = self.model_tts.config.sampling_rate
            wave_np = waveform.cpu().numpy()
            
            if wave_np.ndim > 1:
                wave_np = wave_np.squeeze()
            
            # Create temporary file
            temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
            temp_wav_path = temp_wav.name
            temp_wav.close()  # Close file handle before writing
            sf.write(temp_wav_path, wave_np, samplerate=sampling_rate)
            
            # Convert to MP3
            temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_mp3_path = temp_mp3.name
            temp_mp3.close()  # Close file handle before writing
            audio_seg = AudioSegment.from_wav(temp_wav_path)
            audio_seg.export(temp_mp3_path, format="mp3")
            
            # Clean up WAV file
            try:
                os.unlink(temp_wav_path)
            except:
                logging.warning(f"Could not delete temp WAV file: {temp_wav_path}")
            
            logger.info(f"Generated Malayalam speech: {temp_mp3_path}")
            return temp_mp3_path
            
        except Exception as e:
            logger.error(f"Text to speech conversion failed: {e}")
            raise
    
    def cleanup_temp_file(self, file_path):
        """Clean up temporary files"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {e}")

# Global translation service instance
translation_service = None

def get_translation_service():
    """Get or create translation service instance"""
    global translation_service
    if translation_service is None:
        logger.info("Initializing translation service...")
        translation_service = TranslationService()
        logger.info("Translation service initialized successfully")
    return translation_service