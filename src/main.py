from preprocessing import load, parse_tokens
import sys
import argparse

from utils.config import Config
from utils.one_hot_encoding import OneHotEncoder

# Rules used during tokenisation.
tokenisation_rules = {
    "TOKENISE_QUOTES": True,
    "TOKENISE_NUMBERS": True,
    "TOKENISE_MONTH": True,
    "TOKENISE_PERCENTAGES": True,
    "REMOVE_QUESTION_MARKS": True,
    "TOKENISE_STOPWORDS": False,
    "TOKENISE_URLS": True,
    "TOKENISE_MONEY": True,
    "TOKENISE_YEAR": True,
    "TOKENISE_COMMA_SEPERATED_NUMBERS": True
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', action='store_true', help='Run the code to train a model')
    parser.add_argument('--test', action='store_true', help='Run the code to test a model')
    parser.add_argument('--config', nargs=1)
    args = parser.parse_args(sys.argv[1:])
    config = Config.from_config_file(args.config[0])

    # TODO: Handle the case when the argument is --test instead of --train
    # Load the dataset
    questions, classifications = load(config.path_train)

    # Map questions to tokenised questions
    tokenised_questions = list(map(lambda x: parse_tokens(x, tokenisation_rules), questions))

    one_hot_encoder = OneHotEncoder()
    one_hot_encoding = one_hot_encoder.encode(tokenised_questions, update_corpus=True)

    # Display the pre and post tokenised questions
    for i, question in enumerate(questions):
        print(f"{question}\n{tokenised_questions[i]}\n{classifications[i]}\n{one_hot_encoding[i].shape}\n")
