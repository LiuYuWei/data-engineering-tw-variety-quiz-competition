from datasets import load_dataset
import json

def check_hf_format(repo_id="Simon-Liu/tw-variety-quiz-competition"):
    dataset = load_dataset(repo_id)
    df = dataset['train'].to_pandas()
    print("Columns:", df.columns.tolist())
    if 'conversation' in df.columns:
        print("Conversation sample:", df['conversation'].iloc[0])
        print("Type of conversation:", type(df['conversation'].iloc[0]))

if __name__ == "__main__":
    check_hf_format()
