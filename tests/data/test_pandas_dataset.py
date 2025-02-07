# MultiMolecule
# Copyright (C) 2024-Present  MultiMolecule

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from functools import partial

import danling as dl
import pytest
import torch

from multimolecule import PandasDataset, Task, TaskLevel, TaskType


@pytest.mark.lfs
class TestRNADataset:

    pretrained = "multimolecule/rna"
    root = os.path.join("tests", "data", "datasets", "rna")

    @pytest.mark.parametrize("preprocess", [True, False])
    def test_5utr(self, preprocess: bool):
        file = os.path.join(self.root, "5utr.csv")
        dataset = PandasDataset(
            file, split="train", pretrained=self.pretrained, preprocess=preprocess, auto_rename_cols=True
        )
        task = Task(type=TaskType.Regression, level=TaskLevel.Sequence)
        elem = dataset[0]
        assert isinstance(elem["input_ids"], dl.PNTensor)
        assert isinstance(elem["labels"], torch.FloatTensor)
        batch = dataset[list(range(3))]
        assert isinstance(batch["input_ids"], dl.NestedTensor)
        assert isinstance(batch["labels"], torch.FloatTensor)
        assert dataset.tasks["labels"] == task

    @pytest.mark.parametrize("preprocess", [True, False])
    def test_ncrna(self, preprocess: bool):
        file = os.path.join(self.root, "ncrna.csv")
        dataset = PandasDataset(
            file, split="train", pretrained=self.pretrained, preprocess=preprocess, auto_rename_cols=True
        )
        task = Task(type=TaskType.MultiClass, level=TaskLevel.Sequence, num_labels=13)
        elem = dataset[0]
        assert isinstance(elem["input_ids"], dl.PNTensor)
        assert isinstance(elem["labels"], torch.LongTensor)
        batch = dataset[list(range(3))]
        assert isinstance(batch["input_ids"], dl.NestedTensor)
        assert isinstance(batch["labels"], torch.LongTensor)
        assert dataset.tasks["labels"] == task

    @pytest.mark.parametrize("preprocess", [True, False])
    def test_rnaswitches(self, preprocess: bool):
        file = os.path.join(self.root, "rnaswitches.csv")
        label_cols = ["ON", "OFF", "ON_OFF"]
        dataset = PandasDataset(
            file, split="train", pretrained=self.pretrained, preprocess=preprocess, label_cols=label_cols
        )
        task = Task(type=TaskType.Regression, level=TaskLevel.Sequence)
        elem = dataset[0]
        assert isinstance(elem["sequence"], dl.PNTensor)
        assert isinstance(elem["ON"], torch.FloatTensor)
        assert isinstance(elem["OFF"], torch.FloatTensor)
        batch = dataset[list(range(3))]
        assert isinstance(batch["sequence"], dl.NestedTensor)
        assert isinstance(batch["ON_OFF"], torch.FloatTensor)
        for t in dataset.tasks.values():
            assert t == task

    @pytest.mark.parametrize("preprocess", [True, False])
    def test_modifications(self, preprocess: bool):
        file = os.path.join(self.root, "modifications.json")
        dataset = PandasDataset(file, split="train", pretrained=self.pretrained, preprocess=preprocess)
        task = Task(type=TaskType.MultiLabel, level=TaskLevel.Sequence, num_labels=12)
        elem = dataset[0]
        assert isinstance(elem["sequence"], dl.PNTensor)
        assert isinstance(elem["label"], torch.LongTensor)
        batch = dataset[list(range(3))]
        assert isinstance(batch["sequence"], dl.NestedTensor)
        assert isinstance(batch["label"], torch.LongTensor)
        assert dataset.tasks["label"] == task

    @pytest.mark.parametrize("preprocess", [True, False])
    def test_degradation(self, preprocess: bool):
        file = os.path.join(self.root, "degradation.json")
        feature_cols = ["sequence"]  # , "structure", "predicted_loop_type"]
        label_cols = ["reactivity", "deg_Mg_pH10", "deg_Mg_50C", "deg_pH10", "deg_50C"]
        dataset = PandasDataset(
            file,
            split="train",
            pretrained=self.pretrained,
            preprocess=preprocess,
            feature_cols=feature_cols,
            label_cols=label_cols,
        )
        task = Task(type=TaskType.Regression, level=TaskLevel.Sequence, num_labels=68)
        elem = dataset[0]
        assert isinstance(elem["sequence"], dl.PNTensor)
        assert isinstance(elem["deg_pH10"], torch.FloatTensor)
        assert isinstance(elem["deg_50C"], torch.FloatTensor)
        batch = dataset[list(range(3))]
        assert isinstance(batch["sequence"], dl.NestedTensor)
        assert isinstance(batch["reactivity"], torch.FloatTensor)
        for t in dataset.tasks.values():
            assert t == task

    @pytest.mark.parametrize("preprocess", [True, False])
    def test_spliceai(self, preprocess: bool):
        file = os.path.join(self.root, "spliceai.json")
        feature_cols = ["sequence"]
        label_cols = ["splice_ai"]
        dataset = PandasDataset(
            file,
            split="train",
            pretrained=self.pretrained,
            preprocess=preprocess,
            feature_cols=feature_cols,
            label_cols=label_cols,
        )
        task = Task(type=TaskType.Binary, level=TaskLevel.Nucleotide, num_labels=1)
        elem = dataset[0]
        assert isinstance(elem["sequence"], dl.PNTensor)
        assert isinstance(elem["splice_ai"], torch.LongTensor)
        batch = dataset[list(range(3))]
        assert isinstance(batch["sequence"], dl.NestedTensor)
        assert isinstance(batch["splice_ai"], torch.LongTensor)
        for t in dataset.tasks.values():
            assert t == task


@pytest.mark.lfs
class TestSyntheticDataset:

    pretrained = "multimolecule/rna"
    root = os.path.join("tests", "data", "datasets", "synthetic")

    def test_null(self):
        file = os.path.join(self.root, "null.csv")
        dataset_factory = partial(PandasDataset, file, split="train", pretrained=self.pretrained)
        dataset = dataset_factory(nan_process="ignore")
        assert len(dataset) == 67
        with pytest.raises(RuntimeError):
            dataset[0]
        with pytest.raises(ValueError):
            dataset = dataset_factory(nan_process="raise")
        dataset = dataset_factory(nan_process="fill", fill_value=0)
        assert dataset[0]["label"] == 0
        dataset = dataset_factory(nan_process="fill", fill_value=1)
        assert dataset[0]["label"] == 1
        dataset = dataset_factory(nan_process="drop")
        assert len(dataset) == 61

    def test_rna_task_recognition_json(self):
        file = os.path.join(self.root, "rna.json")
        dataset = PandasDataset(file, split="train", pretrained=self.pretrained)
        assert dataset.tasks["sequence_binary"] == Task(type=TaskType.Binary, level=TaskLevel.Sequence, num_labels=1)
        assert dataset.tasks["sequence_multiclass"] == Task(
            type=TaskType.MultiClass, level=TaskLevel.Sequence, num_labels=7
        )
        assert dataset.tasks["sequence_multilabel"] == Task(
            type=TaskType.MultiLabel, level=TaskLevel.Sequence, num_labels=7
        )
        assert dataset.tasks["sequence_multireg"] == Task(
            type=TaskType.Regression, level=TaskLevel.Sequence, num_labels=7
        )
        assert dataset.tasks["sequence_regression"] == Task(
            type=TaskType.Regression, level=TaskLevel.Sequence, num_labels=1
        )
        assert dataset.tasks["nucleotide_binary"] == Task(
            type=TaskType.Binary, level=TaskLevel.Nucleotide, num_labels=1
        )
        assert dataset.tasks["nucleotide_multiclass"] == Task(
            type=TaskType.MultiClass, level=TaskLevel.Nucleotide, num_labels=5
        )
        assert dataset.tasks["nucleotide_multilabel"] == Task(
            type=TaskType.MultiLabel, level=TaskLevel.Nucleotide, num_labels=5
        )
        assert dataset.tasks["nucleotide_multireg"] == Task(
            type=TaskType.Regression, level=TaskLevel.Nucleotide, num_labels=5
        )
        assert dataset.tasks["nucleotide_regression"] == Task(
            type=TaskType.Regression, level=TaskLevel.Nucleotide, num_labels=1
        )
        assert dataset.tasks["contact_binary"] == Task(type=TaskType.Binary, level=TaskLevel.Contact, num_labels=1)
        assert dataset.tasks["contact_multiclass"] == Task(
            type=TaskType.MultiClass, level=TaskLevel.Contact, num_labels=3
        )
        assert dataset.tasks["contact_multilabel"] == Task(
            type=TaskType.MultiLabel, level=TaskLevel.Contact, num_labels=3
        )
        assert dataset.tasks["contact_multireg"] == Task(
            type=TaskType.Regression, level=TaskLevel.Contact, num_labels=3
        )
        assert dataset.tasks["contact_regression"] == Task(
            type=TaskType.Regression, level=TaskLevel.Contact, num_labels=1
        )
