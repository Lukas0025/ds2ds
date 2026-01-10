#!/bin/bash
# Example script to run a 4-stage translation process. In fisrt 3 stage, model asked to translate text into target language (For one column is one stage),
# in last stage, model is asked to verify the translation.
# using ds2ds.py with gpt-oss model.
# Make sure to set the HF_TOKEN environment variable before running.
# Usage: ./explanation.sh
#

python3 ../ds2ds.py --to_lang Czech \
    --models gemma3:12b gemma3:12b gemma3:12b qwen3:14b \
    --prompts ">>TRANSLATE<<" ">>TRANSLATE<<" ">>TRANSLATE<<" ">>VERIFY<<instruction:\n{instruction}\n\ninput:\n{input}\n\noutput:\n{output}" \
    --ollama_host "http://10.0.0.81:11434" --hf_token $HF_TOKEN \
    --hf_source "yahma/alpaca-cleaned" --hf_output "lukasplevac/alpaca-cs" \
    --out_transfer_fields "instruction" "input" "output" ">>VERIFY<<" --stages 4 --limit 10