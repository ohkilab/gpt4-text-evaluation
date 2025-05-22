# GPT-4 Text Evaluation System

This system is a tool that uses GPT-4 to evaluate text files and score them based on specified criteria. This system is based on the following program used in IEEE Security and Privacy 2025.

https://github.com/wi-pi/ai-selected-best-poster

## Features

- Automatic text file evaluation
- Scoring based on customizable criteria (0 to 5 points)
- Generation of detailed explanations for each evaluation item
- Output of evaluation results in JSON format
- Calculation of average scores through multiple evaluation runs

## Requirements

- Python 3.8 or higher
- uv
- OpenAI API key

## Setup

1. Clone the repository:
```bash
git clone [repository URL]
cd [repository name]
```

2. Set up environment variables:
Create a `.env` file and add the following content:
```
OPENAI_API_KEY=your_api_key_here
```

3. Install dependencies:
```bash
uv venv
source .venv/bin/activate  # For Linux / Mac
# or
.venv\Scripts\activate  # For Windows

uv pip install -r requirements.txt
```

4. Place text files for evaluation:
- Place the text files you want to evaluate in the `texts` directory
- By default, a file named `your_text_file.txt` will be evaluated

## Usage

1. Evaluate a single file:
```bash
python3 gpt4_group_criteria.py --text_file "./texts/your_text_file.txt" --result_base_dir "./output_json_files"
```

2. Batch evaluate multiple files:
```bash
python3 gpt4_group_criteria_batch.py --text_dir "./texts" --result_base_dir "./output_json_files"
```

3. Check evaluation results:
- Evaluation results are saved in the `output_json_files` directory
- Individual JSON files are generated for each evaluation criterion
- File names follow the format `[criterion_name]_score_with_explanation_run[run_number].json`
- For batch evaluation, a summary of all file evaluations is output to `evaluation_summary.csv`

## Customizing Evaluation Criteria

Evaluation criteria are defined in the `criteria.json` file. You can customize the evaluation criteria by editing this file.

## Output Format

Each evaluation result is output in the following JSON format:
```json
{
    "score": 4,
    "explanation": "Explanation of the evaluation"
}
```

## Notes

- Usage of the OpenAI API incurs charges
- Text files for evaluation support UTF-8 or Shift-JIS encoding
- Evaluation is performed 3 times for each criterion, and an average score is calculated

## Troubleshooting

1. API Key Error:
- Verify that the correct API key is set in the `.env` file

2. File Reading Error:
- Ensure that input files are correctly placed in the `texts` directory with plain text format
- Verify that the file encoding is appropriate

3. Output Directory Permission Error:
- Check if you have write permissions for the `output_json_files` directory

4. Dependency Error:
- Try running `uv pip install -r requirements.txt` again
- Verify that the virtual environment is properly activated
