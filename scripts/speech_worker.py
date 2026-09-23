"""One local CPU synthesis attempt, launched only by the user-run evaluator."""
import argparse
import io
import json
import os
from pathlib import Path
import random
import socket
import time
import wave
from importlib import metadata
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load(candidate):
    base = ROOT / 'models/speech'
    if candidate == 'piper':
        from piper import PiperVoice
        model = PiperVoice.load(ROOT / 'models/piper/en_US-lessac-medium.onnx', use_cuda=False)
        def speak(text, output):
            with wave.open(str(output), 'wb') as wav:
                model.synthesize_wav(text, wav)
        return speak
    import numpy as np
    import torch
    import soundfile as sf
    def writer(audio, rate, output):
        if hasattr(audio, 'detach'):
            audio = audio.detach().cpu().numpy()
        audio = np.asarray(audio).reshape(-1)
        if not audio.size or not np.isfinite(audio).all():
            raise ValueError('Empty or nonfinite generated audio')
        sf.write(str(output), audio, rate, subtype='PCM_16')
    if candidate == 'kokoro':
        from kokoro import KModel, KPipeline
        import spacy
        if not spacy.util.is_package('en_core_web_sm'):
            raise RuntimeError('Missing local en_core_web_sm; automatic download disabled')
        path = base / 'kokoro'
        model = KModel(repo_id='hexgrad/Kokoro-82M', config=str(path / 'config.json'), model=str(path / 'kokoro-v1_0.pth')).cpu().eval()
        pipeline = KPipeline(lang_code='a', repo_id='hexgrad/Kokoro-82M', model=model, device='cpu', trf=False)
        if pipeline.g2p.fallback is None:
            raise RuntimeError('English phonemiser fallback unavailable; refusing silent word skipping')
        voice = torch.load(path / 'voices/af_heart.pt', map_location='cpu', weights_only=True)
        def speak(text, output):
            chunks = [r.audio for r in pipeline(text, voice=voice, speed=1)]
            writer(torch.cat(chunks), 24000, output)
        return speak
    if candidate == 'mms':
        from transformers import AutoTokenizer, VitsModel
        path = base / 'mms-eng'
        tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
        model = VitsModel.from_pretrained(path, local_files_only=True).cpu().eval()
        def speak(text, output):
            audio = model(**tokenizer(text, return_tensors='pt')).waveform
            writer(audio, model.config.sampling_rate, output)
        return speak
    if candidate == 'speecht5':
        from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
        processor = SpeechT5Processor.from_pretrained(base / 'speecht5', local_files_only=True)
        model = SpeechT5ForTextToSpeech.from_pretrained(base / 'speecht5', local_files_only=True).cpu().eval()
        vocoder = SpeechT5HifiGan.from_pretrained(base / 'speecht5-hifigan', local_files_only=True).cpu().eval()
        with zipfile.ZipFile(base / 'speecht5-speakers/spkrec-xvect.zip') as archive:
            embedding = np.load(io.BytesIO(archive.read('spkrec-xvect/cmu_us_slt_arctic-wav-arctic_b0258.npy')), allow_pickle=False)
        speaker = torch.tensor(embedding, dtype=torch.float32).reshape(1, 512)
        def speak(text, output):
            inputs = processor(text=text, return_tensors='pt')
            writer(model.generate_speech(inputs['input_ids'], speaker, vocoder=vocoder), 16000, output)
        return speak
    if candidate == 'xtts':
        from TTS.tts.configs.xtts_config import XttsConfig
        from TTS.tts.models.xtts import Xtts
        path = base / 'xtts-v2'
        config = XttsConfig()
        config.load_json(str(path / 'config.json'))
        model = Xtts.init_from_config(config)
        model.load_checkpoint(config, checkpoint_dir=str(path), use_deepspeed=False)
        model.cpu().eval()
        speaker = model.speaker_manager.speakers['Ana Florence']
        def speak(text, output):
            result = model.inference(text, 'en', speaker['gpt_cond_latent'], speaker['speaker_embedding'],
                                     temperature=0.75, length_penalty=1.0, repetition_penalty=10.0,
                                     top_k=50, top_p=0.85, speed=1.0, enable_text_splitting=True)
            writer(result['wav'], config.audio.output_sample_rate, output)
        return speak
    raise ValueError('Unknown candidate')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', type=Path)
    args = parser.parse_args()
    request = json.loads(args.request.read_text(encoding='utf-8'))
    folder = args.request.parent
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1')
    def deny(*args, **kwargs):
        raise RuntimeError('Network disabled during speech evaluation')
    socket.socket.connect = deny
    socket.socket.connect_ex = deny
    result = {'success': False, 'load_seconds': None, 'synthesis_seconds': None,
              'seed_supported': request['candidate'] != 'piper', 'device': 'cpu'}
    started = time.perf_counter()
    try:
        random.seed(request['seed'])
        if request['candidate'] != 'piper':
            import numpy as np
            import torch
            np.random.seed(request['seed'])
            torch.manual_seed(request['seed'])
            torch.set_num_threads(4)
        synthesize = load(request['candidate'])
        result['load_seconds'] = time.perf_counter() - started
        started = time.perf_counter()
        if request['candidate'] == 'piper':
            synthesize(request['text'], folder / 'audio.wav')
        else:
            with torch.inference_mode():
                synthesize(request['text'], folder / 'audio.wav')
        result.update(success=True, synthesis_seconds=time.perf_counter() - started)
    except Exception as exc:
        result['error'] = f'{type(exc).__name__}: {exc}'
    result['packages'] = {d.metadata['Name']: d.version for d in metadata.distributions()}
    (folder / 'worker.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    return 0 if result['success'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
