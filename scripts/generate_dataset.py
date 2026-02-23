#!/usr/bin/env python3
"""
generate_dataset.py
Dataset generation script for FluidSound texture dataset.

This script and the accompanying files were developed using the FluidSound
implementation (see https://github.com/kangruix/FluidSound). The repository
retains the original project's licensing; see LICENSE.txt for details.

Varies the bubble radius scale factor to produce systematically different
water sounds. Smaller bubbles → higher-pitched (thin trickle), larger
bubbles → lower-pitched (heavy pour / fill).

The parameter is called "bubble_size" and is a continuous scale factor.
Physically, scaling the radius by s scales the Minnaert frequency by 1/s,
so this directly controls the pitch character of the water sound.

Usage:
    python generate_dataset.py [--num_clips N] [--scale_min S] [--scale_max S]
                                [--samplerate SR] [--scheme SCHEME]

    Output structure:
    raw/
        parameters.json
        bubble_size_0001.wav
        bubble_size_0001.csv
        bubble_size_0002.wav
        bubble_size_0002.csv
        ...
"""

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile

import numpy as np

# Try to import soundfile; fall back to scipy if unavailable
try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False
    from scipy.io import wavfile


# ---------------------------------------------------------------------------
# Bubble file manipulation
# ---------------------------------------------------------------------------

def modify_bubble_file(input_path, output_path, radius_scale):
    """
    Read a trackedBubInfo.txt file and write a modified version with scaled
    bubble radii and correspondingly scaled frequencies.

    Minnaert relation: f ∝ 1/r, so scaling radius by s requires scaling
    frequency by 1/s to maintain physical consistency.

    Parameters
    ----------
    input_path : str
        Path to the original trackedBubInfo.txt
    output_path : str
        Path to write the modified bubble file
    radius_scale : float
        Multiplicative factor for bubble radii (>1 = larger bubbles = lower freq)
    """
    freq_scale = 1.0 / radius_scale  # Minnaert: f ∝ 1/r

    with open(input_path, 'r') as fin, open(output_path, 'w') as fout:
        for line in fin:
            stripped = line.strip()

            # Bubble header: "Bub <id> <radius>"
            if stripped.startswith("Bub "):
                parts = stripped.split()
                # parts = ['Bub', '<id>', '<radius>']
                old_radius = float(parts[2])
                new_radius = old_radius * radius_scale
                fout.write(f"Bub {parts[1]} {new_radius:.15f}\n")

            # Start/End lines: pass through unchanged
            elif stripped.startswith("Start:") or stripped.startswith("End:"):
                fout.write(line)

            # Solve data lines: "  <time> <freqHz> <x> <y> <z> [<pressure>]"
            # These are indented with 2 spaces and start with a number
            elif line.startswith("  ") and stripped and stripped[0].isdigit():
                parts = stripped.split()
                time_val = parts[0]
                old_freq = float(parts[1])
                new_freq = old_freq * freq_scale
                x, y, z = parts[2], parts[3], parts[4]
                # Preserve optional pressure field if present
                if len(parts) >= 6:
                    pressure = parts[5]
                    fout.write(f"  {time_val} {new_freq:.3f} {x} {y} {z} {pressure}\n")
                else:
                    fout.write(f"  {time_val} {new_freq:.3f} {x} {y} {z}\n")

            else:
                # Pass through any other lines unchanged
                fout.write(line)


# ---------------------------------------------------------------------------
# Audio I/O helpers
# ---------------------------------------------------------------------------

def txt_to_wav(txt_path, wav_path, samplerate):
    """
    Read simulation output (one sample per line) and write normalized .wav.
    """
    data = np.loadtxt(txt_path)
    max_val = np.max(np.abs(data))
    if max_val > 0:
        data /= max_val  # normalize to [-1, 1]
    else:
        print(f"  Warning: silent output for {txt_path}")

    if HAS_SOUNDFILE:
        sf.write(wav_path, data, samplerate)
    else:
        wavfile.write(wav_path, samplerate, (data * 32767).astype(np.int16))

    duration = len(data) / samplerate
    return duration


def create_csv(csv_path, duration, bubble_size_value):
    """
    Create a CSV annotation file for one audio clip.
    75 frames per second, constant parameter value throughout.
    """
    num_frames = max(1, int(math.ceil(duration * 75)))
    with open(csv_path, 'w') as f:
        f.write("bubble_size\n")
        for _ in range(num_frames):
            f.write(f"{bubble_size_value:.6f}\n")


def create_parameters_json(json_path, scale_min, scale_max):
    """
    Write the parameters.json specification file.
    """
    params = {
        "parameter_1": {
            "name": "bubble_size",
            "type": "continuous",
            "unit": "scale",
            "min": scale_min,
            "max": scale_max
        }
    }
    with open(json_path, 'w') as f:
        json.dump(params, f, indent=4)
    print(f"Wrote {json_path}")


# ---------------------------------------------------------------------------
# Main generation loop
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate FluidSound texture dataset with varying bubble size"
    )
    parser.add_argument("--num_clips", type=int, default=330,
                        help="Number of clips to generate (default: 330, ~30 min)")
    parser.add_argument("--scale_min", type=float, default=0.5,
                        help="Minimum radius scale factor (default: 0.5)")
    parser.add_argument("--scale_max", type=float, default=2.0,
                        help="Maximum radius scale factor (default: 2.0)")
    parser.add_argument("--samplerate", type=int, default=48000,
                        help="Audio sample rate (default: 48000)")
    parser.add_argument("--scheme", type=int, default=0,
                        help="Coupling scheme: 0=uncoupled, 1=coupled (default: 0)")
    parser.add_argument("--bubble_file", type=str,
                        default=None,
                        help="Path to original trackedBubInfo.txt")
    parser.add_argument("--executable", type=str, default=None,
                        help="Path to runFluidSound executable")
    parser.add_argument("--output_dir", type=str, default=None,
                        help="Output dataset directory (default: ./raw)")
    args = parser.parse_args()

    # Resolve paths relative to this script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_dir = os.path.dirname(script_dir)

    if args.bubble_file is None:
        args.bubble_file = os.path.join(repo_dir, "Scenes", "GlassPour", "trackedBubInfo.txt")
    if args.executable is None:
        args.executable = os.path.join(repo_dir, "build", "runFluidSound")
    if args.output_dir is None:
        # Place outputs directly under the repository `raw/` directory
        args.output_dir = os.path.join(repo_dir, "raw")

    # Validate inputs
    if not os.path.isfile(args.bubble_file):
        print(f"ERROR: Bubble file not found: {args.bubble_file}")
        sys.exit(1)
    if not os.path.isfile(args.executable):
        print(f"ERROR: Executable not found: {args.executable}")
        print("Build the project first: cd build && cmake .. && make -j4")
        sys.exit(1)

    # Create output directory structure (args.output_dir already points to raw)
    raw_dir = args.output_dir
    os.makedirs(raw_dir, exist_ok=True)

    # Write parameters.json
    create_parameters_json(
        os.path.join(raw_dir, "parameters.json"),
        args.scale_min, args.scale_max
    )

    # Generate scale values (linearly spaced)
    scale_values = np.linspace(args.scale_min, args.scale_max, args.num_clips)

    total_duration = 0.0
    successful = 0
    failed = 0

    # Create a temporary working directory for intermediate files
    with tempfile.TemporaryDirectory(prefix="fluidsound_") as tmpdir:
        for i, scale in enumerate(scale_values):
            clip_name = f"bubble_size_{i+1:04d}"
            wav_path = os.path.join(raw_dir, f"{clip_name}.wav")
            csv_path = os.path.join(raw_dir, f"{clip_name}.csv")

            print(f"\n[{i+1}/{args.num_clips}] scale={scale:.4f} -> {clip_name}")

            # Skip if already generated
            if os.path.isfile(wav_path) and os.path.isfile(csv_path):
                # Read existing wav to accumulate duration
                try:
                    if HAS_SOUNDFILE:
                        info = sf.info(wav_path)
                        dur = info.duration
                    else:
                        sr_existing, data_existing = wavfile.read(wav_path)
                        dur = len(data_existing) / sr_existing
                    total_duration += dur
                    successful += 1
                    print(f"  Already exists ({dur:.2f}s), skipping")
                    continue
                except Exception:
                    pass  # re-generate if existing file is corrupted

            # Step 1: Create modified bubble file
            mod_bub_path = os.path.join(tmpdir, "modified_bub.txt")
            modify_bubble_file(args.bubble_file, mod_bub_path, scale)

            # Step 2: Run FluidSound simulation
            output_txt = os.path.join(tmpdir, "output.txt")
            # Remove previous output if it exists
            if os.path.exists(output_txt):
                os.remove(output_txt)

            try:
                result = subprocess.run(
                    [args.executable, mod_bub_path, str(args.samplerate), str(args.scheme)],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 min timeout per clip
                )
                # The executable may crash at cleanup (trace trap) but still produce valid output
                if not os.path.isfile(output_txt):
                    print(f"  ERROR: No output.txt produced")
                    if result.stderr:
                        print(f"  stderr: {result.stderr[:200]}")
                    failed += 1
                    continue

                # Check output has content
                file_size = os.path.getsize(output_txt)
                if file_size == 0:
                    print(f"  ERROR: Empty output.txt")
                    failed += 1
                    continue

            except subprocess.TimeoutExpired:
                print(f"  ERROR: Simulation timed out")
                failed += 1
                continue
            except Exception as e:
                print(f"  ERROR: {e}")
                failed += 1
                continue

            # Step 3: Convert to WAV
            try:
                duration = txt_to_wav(output_txt, wav_path, args.samplerate)
                total_duration += duration
                print(f"  Generated {duration:.2f}s audio")
            except Exception as e:
                print(f"  ERROR converting to WAV: {e}")
                failed += 1
                continue

            # Step 4: Create CSV annotation
            create_csv(csv_path, duration, scale)
            successful += 1

            # Progress report
            if (i + 1) % 10 == 0:
                print(f"\n  === Progress: {successful} done, {failed} failed, "
                      f"total audio: {total_duration:.1f}s ({total_duration/60:.1f} min) ===\n")

    # Final report
    print("\n" + "=" * 60)
    print(f"Dataset generation complete!")
    print(f"  Clips generated: {successful}/{args.num_clips}")
    print(f"  Failed: {failed}")
    print(f"  Total audio: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"  Output directory: {raw_dir}")
    print(f"  Files: parameters.json + {successful} .wav/.csv pairs")
    print("=" * 60)

    if total_duration < 1500:
        print(f"\nWARNING: Total audio ({total_duration/60:.1f} min) is less than the "
              f"target 25 min. Consider increasing --num_clips.")


if __name__ == "__main__":
    main()
