# SigmaOS Packages
![Language](https://img.shields.io/badge/language-python-blue)
![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen)
[![Discord](https://img.shields.io/discord/1362801147202638145?label=discord)](https://discord.gg/KxUfgTszjN)

## Overview

This repository contains official and community-contributed packages for SigmaOS.

## What Are Packages?

Packages are like apps in SigmaOS. They extend its functionality by adding new features, tools, or integrations. Each package is self-contained and can include code, assets, and metadata.

## Package Structure

Each package is a directory containing at least:

- `main.py` — The code that runs when the package is executed.
- `description.txt` — A plain-text file with metadata like author, version, and dependencies.  
> See [sigma/description.txt](sigma/description.txt) for an example.

Packages can also include other files such as images, configuration files, or additional Python modules.

## Installation

You can install packages using the `ligma` package manager:

```sh
ligma install <packagename>
```

Alternatively, you can manually place the package directory into the `packages` folder inside your SigmaOS installation. Packages will be automatically detected and made available.


## Usage

Once installed, you can run a package by entering its name inside SigmaOS:

```sh
<packagename>
```

## Development

To get started with developing your own SigmaOS package, reach out to the SigmaOS team on [The404Company Discord](https://discord.gg/KxUfgTszjN). We're happy to help.

## Contributing

We welcome contributions! If you’ve built a package you want to share:

1. Fork this repository.
2. Add your package following the required structure.
3. Submit a pull request.

Make sure to include a `description.txt` file with relevant metadata. Check out existing packages for reference.

## License

This project is licensed under the terms described in [LICENSE.md](LICENSE.md). Please review it before contributing or using code from this repository.

