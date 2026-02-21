 # FluidSound Dataset

Bubble-based water sound synthesis code based on the papers:
    
> [Improved Water Sound Synthesis using Coupled Bubbles](https://graphics.stanford.edu/papers/coupledbubbles/). Kangrui Xue, Ryan M. Aronson, Jui-Hsien Wang, Timothy R. Langlois, Doug L. James. *ACM Transactions on Graphics (SIGGRAPH North America 2023)*.  

> [Toward Animating Water with Complex Acoustic Bubbles](https://www.cs.cornell.edu/projects/Sound/bubbles/). Timothy R. Langlois, Changxi Zheng, Doug L. James. *ACM Transactions on Graphics (SIGGRAPH North America 2016)*. 

This repository provides dataset-generation utilities built on top of the FluidSound
bubble-based water-sound synthesizer. It packages code and scripts to produce a
systematically-varying audio texture dataset (wav + CSV annotations + a
parameters.json) intended for audio modelling and texture research.

Overview
--------

This project builds on the FluidSound implementation and reproduces the
appropriate attribution and licensing. The original work is described in:

- Xue, K., Aronson, R. M., Wang, J.-H., Langlois, T. R., & James, D. L.,
  "Improved Water Sound Synthesis using Coupled Bubbles", ACM Trans. Graph., 2023.

See the paper and reference materials at https://graphics.stanford.edu/papers/coupledbubbles/.
The official BibTeX entry is provided in `CITATION.bib`.

Dataset Aim
--------------------------------------

The goal is to create an audio texture dataset of bubble-based water sounds that
varies systematically in a single continuous parameter, `bubble_size` (a radius
scale). Key properties:

- Produce ≈25–30 minutes of audio split across many short clips (the default
  generator run produces several hundred clips). Each clip has an accompanying
  CSV annotation and the dataset root contains a single `parameters.json` that
  documents the parameter sweep.
- For each clip the generator writes: `bubble_size_XXXX.wav` and
  `bubble_size_XXXX.csv` (annotation with bubble/parameter-level info).
- The single varying parameter, `bubble_size`, is a multiplicative scale on
  bubble radii; scaling by s shifts the Minnaert frequency by 1/s, producing
  perceptually distinct pitch/timbre across the dataset.

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

Files produced by the generator are placed under `raw/`. This repository
includes the generated dataset files in `raw/`.

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

### Dataset Aim

This repository includes tools to create a small "texture" dataset of water
syntheses generated from the GlassPour scene. The goal is to produce roughly
25–30 minutes of audio distributed over a continuous parameter called
`bubble_size` (a multiplicative radius scale factor). Each dataset item is a
pair: a `.wav` audio clip produced by `runFluidSound` and a `.csv` annotation
file with a constant `bubble_size` value per clip. The generator writes
`parameters.json` describing the parameter range and produces `.wav`/`.csv`
pairs into `raw/` (the large generated files are omitted from the
repository; see `.gitignore`).

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
