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

from __future__ import annotations

import os
from copy import deepcopy
from dataclasses import dataclass

import torch

from multimolecule.models import RnaBertConfig as Config
from multimolecule.models import RnaBertForPreTraining as Model
from multimolecule.models.conversion_utils import ConvertConfig as ConvertConfig_
from multimolecule.models.conversion_utils import save_checkpoint
from multimolecule.tokenisers.rna.utils import convert_word_embeddings, get_alphabet

torch.manual_seed(1016)


def _convert_checkpoint(config, original_state_dict, vocab_list, original_vocab_list):
    state_dict = {}
    for key, value in original_state_dict.items():
        key = key[7:]
        key = key.replace("LayerNorm", "layer_norm")
        key = key.replace("gamma", "weight")
        key = key.replace("beta", "bias")
        key = key.replace("selfattn", "self")
        key = key.replace("seq_relationship", "seq_relationship.decoder")
        if key.startswith("bert"):
            state_dict["rna" + key] = value
            continue
        if key.startswith("cls"):
            key = "pretrain." + key[4:]
            state_dict[key] = value
            continue
        state_dict[key] = value

    word_embed_weight, decoder_weight, decoder_bias = convert_word_embeddings(
        state_dict["rnabert.embeddings.word_embeddings.weight"],
        state_dict["pretrain.predictions.decoder.weight"],
        state_dict["pretrain.predictions.bias"],
        old_vocab=original_vocab_list,
        new_vocab=vocab_list,
        std=config.initializer_range,
    )
    state_dict["rnabert.embeddings.word_embeddings.weight"] = word_embed_weight
    state_dict["pretrain.predictions.decoder.weight"] = decoder_weight
    state_dict["pretrain.predictions.decoder.bias"] = state_dict["pretrain.predictions.bias"] = decoder_bias
    state_dict["pretrain.predictions_ss.decoder.bias"] = state_dict["pretrain.predictions_ss.bias"]
    return state_dict


def convert_checkpoint(convert_config):
    vocab_list = get_alphabet().vocabulary
    original_vocab_list = ["<pad>", "<mask>", "A", "U", "G", "C"]
    config = Config()
    config.architectures = ["RnaBertModel"]
    config.vocab_size = len(vocab_list)

    model = Model(config)

    ckpt = torch.load(convert_config.checkpoint_path, map_location=torch.device("cpu"))
    state_dict = _convert_checkpoint(config, ckpt, vocab_list, original_vocab_list)

    model.load_state_dict(state_dict)

    model.lm_head = deepcopy(model.pretrain.predictions)

    save_checkpoint(convert_config, model)


@dataclass
class ConvertConfig(ConvertConfig_):
    root: str = os.path.dirname(__file__)
    output_path: str = Config.model_type


if __name__ == "__main__":
    config = ConvertConfig()
    config.parse()  # type: ignore[attr-defined]
    convert_checkpoint(config)
