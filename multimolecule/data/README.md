---
authors:
  - Zhiyuan Chen
date: 2024-05-04
---

# data

`data` provides a collection of data processing utilities for handling data.

While :hugs: [`datasets`](https://huggingface.co/docs/datasets) is a powerful library for managing datasets, it is a general-purpose tool that may not cover all the specific functionalities of scientific applications.

The `data` package is designed to complement [`datasets`](https://huggingface.co/docs/datasets) by offering additional data processing utilities that are commonly used in scientific tasks.

## Key Features

- Data Pre-Processing: [`Dataset`][multimolecule.Dataset] is a base class that provides a consistent interface for pre-processing data. It includes methods for identifying the data columns and tasks, tokenizing sequences, and batching.
- Data Loading: [`PandasDataset`][multimolecule.PandasDataset] is a subclass of [`Dataset`][multimolecule.Dataset] that loads data in a [`DataFrame`][pandas.DataFrame] compatible format. This provides a convenient way to work with many common data formats, including CSV, JSON, and Excel files.
