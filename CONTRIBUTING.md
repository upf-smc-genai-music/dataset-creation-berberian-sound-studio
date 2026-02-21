Contributing
============

This repository contains dataset-generation utilities built on top of the FluidSound
codebase. If you'd like to contribute, please follow these minimal steps.

Build the C++ project
---------------------

1. Install dependencies (Eigen 3).
2. From the repository root:

```bash
mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j4
```

This produces `build/runFluidSound` used by `scripts/generate_dataset.py`.

Python dependencies
-------------------

Install Python requirements for the helper scripts:

```bash
pip install -r requirements.txt
```

Running the dataset generator
-----------------------------

The generator calls the `runFluidSound` executable repeatedly with modified
bubble tracking files. Example:

```bash
python scripts/generate_dataset.py --num_clips 330 --scale_min 0.5 --scale_max 2.0 \
    --samplerate 48000 --scheme 0 --bubble_file Scenes/GlassPour/trackedBubInfo.txt \
    --executable build/runFluidSound --output_dir raw
```

Contributions & Issues
----------------------

- Open issues for bugs, feature requests, or dataset questions.
- For code contributions, please fork the repository and submit a pull request.

Licensing and attribution
-------------------------

This project includes code derived from the original FluidSound project by
Kangrui Xue et al. The original code is MIT-licensed; this repository preserves
that license. See `LICENSE.txt` for the full MIT license.

When reusing or redistributing, please cite the original FluidSound paper and
repository (links in `README.md`).
