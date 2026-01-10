# ds2ds - Dataset to Dataset Converter

A tool for converting and processing datasets using LLM models from Ollama. Enables multi-stage processing of datasets with custom prompts and models.

## Features

- 🔄 **Multi-stage processing** - Multiple stages with different models and prompts
- 🎯 **Custom prompts** - Define a prompt for each stage
- ✅ **Text verification** - Automatically remove erroneous items (`>>VERIFY<<`)
- 🌍 **Translation** - Translate content to any language (`>>TRANSLATE<<`)
- 🧠 **Clean outputs** - Automatically remove thinking blocks from models
- 📊 **Progress bar** - Visualize processing progress
- 📈 **Limiting** - Process only N items or from a specific index

## Setup

### 1. Initialize pipenv

```bash
pipenv install
```

### 2. Activate the virtual environment

```bash
pipenv shell
```

## Usage

### Basic example

```bash
python ds2ds.py \
  --ollama_host http://localhost:11434 \
  --hf_token YOUR_HF_TOKEN \
  --hf_source dataset_name \
  --hf_output output_dataset_name \
  --models llama2 \
  --prompts "Analyze the following text: {input}" \
  --out_transfer_fields output_field
```

### Multi-stage processing example

```bash
python ds2ds.py \
  --ollama_host http://localhost:11434 \
  --hf_token YOUR_HF_TOKEN \
  --hf_source my_dataset \
  --hf_output processed_dataset \
  --stages 2 \
  --models mistral llama2 \
  --prompts "Extract key points: {input}" "Summarize: {input}" \
  --out_transfer_fields extracted summary \
  --verbose
```

### Content verification (remove erroneous items) (col instruction)

```bash
python ds2ds.py \
  --ollama_host http://localhost:11434 \
  --hf_token YOUR_HF_TOKEN \
  --hf_source raw_dataset \
  --hf_output verified_dataset \
  --models llama2 \
  --prompts ">>VERIFY<<{instruction}" \
  --out_transfer_fields ">>VERIFY<<" \
  --verbose
```

### Translation to another language (col question)

```bash
python ds2ds.py \
  --ollama_host http://localhost:11434 \
  --hf_token YOUR_HF_TOKEN \
  --hf_source english_dataset \
  --hf_output czech_dataset \
  --models llama2 \
  --prompts ">>TRANSLATE<<" \
  --out_transfer_fields question \
  --to_lang "Czech"
```

or

```bash
python ds2ds.py \
  --ollama_host http://localhost:11434 \
  --hf_token YOUR_HF_TOKEN \
  --hf_source english_dataset \
  --hf_output czech_dataset \
  --models llama2 \
  --prompts ">>TRANSLATE<<{question}" \
  --out_transfer_fields question \
  --to_lang "Czech"
```

### Process only a subset of the dataset

```bash
python ds2ds.py \
  --ollama_host http://localhost:11434 \
  --hf_token YOUR_HF_TOKEN \
  --hf_source my_dataset \
  --hf_output subset_output \
  --models llama2 \
  --prompts "Process: {input}" \
  --out_transfer_fields result \
  --start_index 0 \
  --limit 100
```

## Arguments

- `--ollama_host` - Ollama server URL (required)
- `--hf_token` - Hugging Face token (required)
- `--hf_source` - Source dataset from HF Hub (required)
- `--hf_output` - Output dataset name on HF Hub (required)
- `--stages` - Number of processing stages (default: 1)
- `--models` - Models for each stage (count must match `--stages`)
- `--prompts` - Prompts for each stage (count must match `--stages`)
- `--out_transfer_fields` - Output fields for each stage (count must match `--stages`)
- `--to_lang` - Target language for translation (default: English)
- `--start_index` - Start from index (default: 0)
- `--limit` - Maximum number of items (default: all)
- `--verbose` - Detailed output (default: False)
- `--droped_csv` - Path to save droped items as CSV (default: None)

## Special prompts

- `>>VERIFY<<text` - Verifies text and removes items with errors
- `>>TRANSLATE<<` - Translates text of column defined by Output fields to the language specified in `--to_lang` 
- `>>TRANSLATE<<text` - Translates text to the language specified in `--to_lang` 


## Special Output fields

- `>>VERIFY<<` - Verifies text and removes items with errors
- `>>NOT_EQ_DROP<<value` - remove row if output of LLM is not same as value
