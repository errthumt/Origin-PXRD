---
title: Home
nav_order: 1
---


# Origin-PXRD <!-- omit from toc -->
A plugin for importing experimental patterns and calculating theoretical patterns for PXRD in OriginLab's OriginPro software.

The python code for calculating theoretical patterns from CIF files has been moved to a PyPI package, `cif2xrd`, to be used by any python runtime. Visit the [PyPI page](https://pypi.org/project/cif2xrd/) or the `cif2xrd` [GitHub](https://github.com/errthumt/cif2xrd) for more information.

This plugin is a companion for `cif2xrd.originlab`. `cif2xrd.originlab` wraps the simulation code into commands for importing patterns directly into OriginPro, with additional features such as:
* Dynamically scaling by phase fraction.
* Adding dynamic X columns in Q-space instead of 2θ.
* Square or Square-root intensities.
* Import experimental data in matching format (currently only supported for Rigaku *.RAS file format)

Origin-PXRD goes even further by wrapping `cif2xrd.originlab` into a convenient dropdown menu, and adds another menu for [managing annealing profiles](./instructions.md#new-annealing-profiles-dropdown) for solid-state synthesis. 

This plugin is primarily used by Kovnir and Zaikina research groups at Iowa State University, Department of Chemistry

_**Are you NOT from Kovnir or Zaikina group and want to use this plugin?**_ Fill out a feature request below to let me know what you're using it for.

# Where to go from here?
* [Updating or Installing the Plugin](./install_guide/)
* Having trouble installing or using the plugin? [Visit the FAQ](./faq.md) or fill out a bug report below.
* Looking for examples on how this plugin can be useful to you? [See some examples.](./examples.md)
* Looking for more details on how to use a feature? Visit the [Options Summary](./instructions.md)
* Curious about how the plugin simulates CIF patterns? Visit the [CIF Calculation Method](./phase_frac.md)

## Bug reports or Feature Requests
* <ins>**No GitHub Account?**</ins> [use this form](https://forms.office.com/r/9bfw1zLiDh)
* <ins>**If you have a GitHub account:**</ins>
  * [Create a bug report](https://github.com/errthumt/Origin-PXRD/issues/new?template=bug_report.md)
  * [Request a feature](https://github.com/errthumt/Origin-PXRD/issues/new?template=feature_request.md)
  * [Other feedback](https://github.com/errthumt/Origin-PXRD/issues/new)

---

