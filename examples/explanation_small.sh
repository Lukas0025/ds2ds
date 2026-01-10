#!/bin/bash
# Example script to run a 2-stage explanation generation process. In fisrt stage, model asked to select the correct answer,
# in the second stage, model is asked to provide a detailed explanation of the solution.
# using ds2ds.py with qwen3:14b model.
# Make sure to set the HF_TOKEN environment variable before running.
# Usage: ./explanation.sh
#

python3 ../ds2ds.py \
    --models qwen3:14b qwen3:14b \
    --prompts "Vyber srávnou možnost řešení následujícího úkolu, napiš pouze vybrané písmeno odpovědi nic jiného, počítej že současný rok je {year}. Otázka:\n\n{question}\n\nOdpovědi: A - {A}, B - {B}, C - {C}, D - {D}, E - {E}" \
    "Napiš řešení pro následující úkol, výsledek zvírazni a postup dobře vysvětli, počítej že současný rok je {year}, česky:\n\n{question}" \
    --ollama_host "http://10.0.0.81:11434" --hf_token $HF_TOKEN \
    --hf_source "hynky/klokan-qa" --hf_output "lukasplevac/klokan-explanation" \
    --out_transfer_fields ">>NOT_EQ_DROP<<{correct_answer}" "explanation" --stages 2 --limit 1 --verbose