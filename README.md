 # FluidSound Dataset

Bubble-based water sound synthesis code based on the papers:
    
> [Improved Water Sound Synthesis using Coupled Bubbles](https://graphics.stanford.edu/papers/coupledbubbles/). Kangrui Xue, Ryan M. Aronson, Jui-Hsien Wang, Timothy R. Langlois, Doug L. James. *ACM Transactions on Graphics (SIGGRAPH North America 2023)*.  

> [Toward Animating Water with Complex Acoustic Bubbles](https://www.cs.cornell.edu/projects/Sound/bubbles/). Timothy R. Langlois, Changxi Zheng, Doug L. James. *ACM Transactions on Graphics (SIGGRAPH North America 2016)*. 

Overview
--------

This repository provides dataset-generation utilities built on top of the FluidSound bubble-based water-sound synthesizer. It packages code and scripts to produce a systematically-varying audio texture dataset (wav + CSV annotations + a
parameters.json) intended for audio modelling and texture research. The original work is described in:

- Xue, K., Aronson, R. M., Wang, J.-H., Langlois, T. R., & James, D. L.,
  "Improved Water Sound Synthesis using Coupled Bubbles", ACM Trans. Graph., 2023.

See the paper and reference materials at https://graphics.stanford.edu/papers/coupledbubbles/.
The official BibTeX entry is provided in `CITATION.bib`.

Scripts overview
--------------------------------------

`scripts/generate_dataset.py`: Main dataset generator. It scales bubble radii
(parameter `bubble_size`), runs the `runFluidSound` executable for each scale,
converts the simulation `output.txt` into a normalized `.wav`, and writes the
resulting `.wav` + `.csv` pairs plus `parameters.json` directly into `raw/`.
This script and the accompanying files were developed using the FluidSound
implementation (https://github.com/kangruix/FluidSound). The generator varies
the bubble radius scale factor to produce systematically different water
sounds: smaller bubbles → higher-pitched (thin trickle), larger bubbles →
lower-pitched (heavy pour / fill). The parameter is called `bubble_size` and
is a continuous scale factor; physically, scaling the radius by `s` scales
the Minnaert frequency by `1/s`, so this directly controls the pitch
character of the synthesized audio. The generator produces a dataset of 330 clips, (each 5 seconds long), to get around 27 minutes of audio, with `bubble_size` values logarithmically spaced between 0.5 and 2.0 (the default range). See `scripts/generate_dataset.py` for the exact parameterization and usage.

  Defaults include `--num_clips 330`, `--samplerate 48000`, and the default
  `--output_dir` is `raw/`. Example:

```bash
python scripts/generate_dataset.py --num_clips 330 --scale_min 0.5 --scale_max 2.0 \
    --samplerate 48000 --scheme 0 --bubble_file Scenes/GlassPour/trackedBubInfo.txt \
    --executable build/runFluidSound --output_dir raw
```

- `scripts/write_wav.py`: Simple utility that reads a simulation `output.txt`
  (one sample per line) or a `.bin` float32 file and writes a normalized
  `.wav` file. Usage: `python scripts/write_wav.py <path to sim. output> <samplerate>`.

Dataset structure
--------------------------------------

- All generated files are placed in the repository `raw/` directory.
- `parameters.json`: JSON describing the sweep of the `bubble_size` parameter
  (the generator writes this into `raw/`). See `scripts/generate_dataset.py`
  for the exact fields written.
- Per-clip files (for each generated scale):
  - `bubble_size_XXXX.wav` — normalized audio (samplerate per `--samplerate`).
  - `bubble_size_XXXX.csv` — annotation with a header `bubble_size` and one
    row per frame (75 fps). The CSV contains the constant parameter value used
    for that clip (the generator creates these at 75 frames/sec).

Build & Quick Usage
-------------------

Dependencies:

- C++: C++11, Eigen3 (used by the FluidSound C++ code)
- Python: see `requirements.txt` (`numpy`, `matplotlib`, `soundfile`, `scipy`)

Build the C++ executable (creates `build/runFluidSound`):

```bash
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j4
```

Convert simulation output to WAV (example):

```bash
python scripts/write_wav.py output.txt 48000
```

Generate the dataset (example):

```bash
python scripts/generate_dataset.py --num_clips 330 \
    --scale_min 0.5 --scale_max 2.0 \
    --samplerate 48000 --scheme 0 \
    --bubble_file Scenes/GlassPour/trackedBubInfo.txt \
    --executable build/runFluidSound --output_dir raw
```
Citation & Licensing
---------------------

If you use these tools or the dataset in publications, please cite the original
FluidSound paper. The BibTeX entry is available in `CITATION.bib`.

This repository preserves the original MIT license. See `LICENSE.txt` for the
full license text and the short SPDX headers included at the top of source
files to document attribution.

Acknowledgements
----------------

This project packages dataset-generation utilities and documentation around the
FluidSound synthesis code and the example GlassPour scene. Many thanks to the
original authors (Kangrui Xue et al.)—please see the paper and original repo
for full credit. The GlassPour scene source data is provided from the WaveBlend / Stanford dataset: https://graphics.stanford.edu/papers/waveblender/dataset/index.html.

For contribution and developer guidance see `CONTRIBUTING.md`.
  - Defaults assume the repo root layout (see `scripts/generate_dataset.py`).
  - Each clip runs the `runFluidSound` executable and writes a `.wav` and `.csv` pair to `raw/`.
  - A temporary working directory is used and each simulation has a 5-minute timeout by default.

See `CONTRIBUTING.md` for a short developer guide and notes about building the project.

### Citation

If you use this code or dataset, please cite the FluidSound paper as follows:

```bibtex
@article{10.1145/3592424,
  author = {Xue, Kangrui and Aronson, Ryan M. and Wang, Jui-Hsien and Langlois, Timothy R. and James, Doug L.},
  title = {Improved Water Sound Synthesis using Coupled Bubbles},
  year = {2023},
  issue_date = {August 2023},
  publisher = {Association for Computing Machinery},
  address = {New York, NY, USA},
  volume = {42},
  number = {4},
  issn = {0730-0301},
  url = {https://doi.org/10.1145/3592424},
  doi = {10.1145/3592424},
  abstract = {We introduce a practical framework for synthesizing bubble-based water sounds that captures the rich inter-bubble coupling effects responsible for low-frequency acoustic emissions from bubble clouds. We propose coupled-bubble oscillator models with regularized singularities, and techniques to reduce the computational cost of time stepping with dense, time-varying mass matrices. Airborne acoustic emissions are estimated using finite-difference time-domain (FDTD) methods. We propose a simple, analytical surface-acceleration model, and a sample-and-hold GPU wavesolver that is simple and faster than prior CPU wavesolvers.Sound synthesis results are demonstrated using bubbly flows from incompressible, two-phase simulations, as well as procedurally generated examples using single-phase FLIP fluid animations. Our results demonstrate sound simulations with hundreds of thousands of bubbles, and perceptually significant frequency transformations with fuller low-frequency content.},
  journal = {ACM Trans. Graph.},
  month = {jul},
  articleno = {127},
  numpages = {13},
  keywords = {fluid animation, sound synthesis, acoustic bubbles}
}
```

An equivalent BibTeX entry is provided in `CITATION.bib` at the repository root.

### Acknowledgements & Credits

- This repository re-uses the FluidSound code and example scenes developed by Kangrui Xue et al. The original project is available at https://github.com/kangruix/FluidSound and should be cited when using the underlying algorithms (see citation above).
- GlassPour scene source data is provided from the WaveBlend / Stanford dataset: https://graphics.stanford.edu/papers/waveblender/dataset/index.html.

Because parts of the FluidSound implementation are included directly in this repository (rather than imported as an external library), the original licensing and copyright information has been preserved in source files. See the top of each source file for the reproduced license header.

If you reuse or redistribute this work, please cite the original FluidSound paper and repository.
