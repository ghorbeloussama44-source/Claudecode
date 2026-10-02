"""Classify speaker (F/H) per transcript line using pitch, and merge into turns.

faster-whisper's diarize=True does not work in this environment (returns
NO_SPEAKER for every segment). This pitch-based (F0) workaround is the
reliable substitute for a two-speaker recording like this one.

Usage: edit AUDIO and LINES below (LINES = the (start,end) seconds from a
faster-whisper transcript of the span you care about), then run. Re-check
the female/male F0 threshold (THRESHOLD_HZ) against new output if you run
this against a different audio file — voices differ.
"""
import librosa
import numpy as np

AUDIO = "/home/user/Claudecode/openmontage/projects/medilearn/assets/originals/client_audio_17min.m4a"
THRESHOLD_HZ = 165  # female >= this, male below — measured for this recording

# (start, end) seconds per transcript line — fill in from faster-whisper output
LINES: list[tuple[float, float]] = [
    # (0.0, 5.5), (6.3, 13.8), ...
]


def classify(y, sr, start, end):
    s, e = int(start * sr), int(end * sr)
    seg = y[s:e]
    if len(seg) < sr * 0.15:
        return None, 0.0
    f0, _, _ = librosa.pyin(seg, fmin=70, fmax=300, sr=sr)
    f0v = f0[~np.isnan(f0)]
    if len(f0v) == 0:
        return None, 0.0
    mean_f0 = float(np.mean(f0v))
    return ("F" if mean_f0 >= THRESHOLD_HZ else "H"), mean_f0


def merge_turns(results):
    turns = []
    cur_label, cur_start, cur_end = results[0][2], results[0][0], results[0][1]
    for (s, e, label, _f0) in results[1:]:
        if label == cur_label:
            cur_end = e
        else:
            turns.append((cur_start, cur_end, cur_label))
            cur_label, cur_start, cur_end = label, s, e
    turns.append((cur_start, cur_end, cur_label))
    return turns


if __name__ == "__main__":
    y, sr = librosa.load(AUDIO, sr=16000, mono=True)

    results = []
    for (s, e) in LINES:
        label, f0 = classify(y, sr, s, e)
        results.append((s, e, label, f0))
        print(f"{s:7.1f}-{e:7.1f}  {label}  f0={f0:.1f}")

    # fill gaps (no voiced pitch detected) with the previous line's speaker
    for i, (s, e, label, f0) in enumerate(results):
        if label is None:
            results[i] = (s, e, results[i - 1][2] if i > 0 else "F", f0)

    turns = merge_turns(results)
    print(f"\n--- {len(turns)} merged turns ---")
    for (s, e, label) in turns:
        print(f"{{ from: {s:.1f}, to: {e:.1f}, speaker: \"{label}\" }},")
