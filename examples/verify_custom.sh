#!/bin/bash
# Example script to run a 2-stage explanation generation process. In fisrt stage, model asked to select the correct answer,
# in the second stage, model is asked to provide a detailed explanation of the solution.
# using ds2ds.py with gpt-oss model.
# Make sure to set the HF_TOKEN environment variable before running.
# Usage: ./explanation.sh
#

python3 ../ds2ds.py \
    --models gemma3:12b \
    --prompts "Vyber srávnou možnost řešení pro následující postup, napiš pouze vybrané písmeno odpovědi nic jiného. Řešení:\n\n{explanation}\n\nOdpovědi: A - {A}, B - {B}, C - {C}, D - {D}, E - {E}, F - jiné" \
    --ollama_host "http://10.0.0.81:11434" --hf_token $HF_TOKEN \
    --hf_source "lukasplevac/klokan-explanation" --hf_output "lukasplevac/klokan-explanation-clean" \
    --out_transfer_fields ">>NOT_EQ_DROP<<{correct_answer}" --stages 1 --droped_csv "dropped_items.csv"