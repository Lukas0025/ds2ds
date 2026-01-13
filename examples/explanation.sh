#!/bin/bash
# Example script to run a 2-stage explanation generation process. In fisrt stage, model asked to select the correct answer,
# in the second stage, model is asked to provide a detailed explanation of the solution.
# using ds2ds.py with gpt-oss model.
# Make sure to set the HF_TOKEN environment variable before running.
# Usage: ./explanation.sh
#

python3 ../ds2ds.py \
    --models gpt-oss:120b gpt-oss:120b \
    --prompts "Vyber srávnou možnost řešení následujícího úkolu, napiš pouze vybrané písmeno odpovědi nic jiného, počítej že současný rok je {year}. Otázka:\n\n{question}\n\nOdpovědi: A - {A}, B - {B}, C - {C}, D - {D}, E - {E}" \
    "Napiš řešení následujícího úkolu. Výsledek zvýrazni a postup srozumitelně vysvětli, ale piš stručně – drž se alpaca stylu, ale nikde nepiš že je to alpaca styl. Předpokládej, že aktuální rok je {year}. Odpovídej česky.\nÚloha:\n\n{question}" \
    --ollama_host "http://10.0.0.81:11434" --hf_token $HF_TOKEN \
    --hf_source "hynky/klokan-qa" --hf_output "lukasplevac/klokan-explanation" \
    --out_transfer_fields ">>NOT_EQ_DROP<<{correct_answer}" "explanation" --stages 2 --droped_csv "dropped_items.csv"