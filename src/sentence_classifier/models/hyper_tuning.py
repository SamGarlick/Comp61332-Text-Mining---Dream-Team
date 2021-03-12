import numpy as np
import torch
from torch import nn

from sentence_classifier.analysis import roc
from sentence_classifier.models.model import Model
from sentence_classifier.preprocessing.reader import load
from sentence_classifier.preprocessing.tokenisation import parse_tokens
from test.test_end_to_end import OneHotLabels


REPEATS = 5
CLASSES = 50

TRAIN_FILE_PATH = "../data/train.txt"
TEST_FILE_PATH = "../data/test.txt"

X, Y = load(TRAIN_FILE_PATH)
test_X, test_Y = load(TEST_FILE_PATH)

one_hot_labels = OneHotLabels(Y)


def train_model(model, loss_fn, optimizer, repeat, epochs=10):
    for epoch in range(epochs):
        for count in range(len(X)):
            model.train()

            question = X[count]
            label = Y[count]

            yhat = model(parse_tokens(question))

            loss = loss_fn(yhat.reshape(1, CLASSES), torch.LongTensor([one_hot_labels.idx_for_label(label)]))
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            print("\rExperiment: {}, Epochs: {}, Step: {}/{}, Loss: {}".format(
                repeat + 1, epoch + 1, count + 1, len(X), loss.detach().numpy()
            ), end="")

    return roc.analyse(test_Y, [
        one_hot_labels.label_for_idx(torch.argmax(model(parse_tokens(test_question))))
        for test_question in test_X
    ])["f1"]


def BOWModel():
    return (Model.Builder()
            .with_glove_word_embeddings("../data/glove.small.txt")
            .with_bow_sentence_embedder()
            .with_classifier(300)
            .build())


def BiLSTM():
    return (Model.Builder()
            .with_glove_word_embeddings("../data/glove.small.txt")
            .with_bilstm_sentence_embedder(300, 300)
            .with_classifier(300)
            .build())


if __name__ == "__main__":

    for lr in [0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01]:
        results = []
        for repeat in range(REPEATS):
            model = BiLSTM()

            loss_fn = nn.NLLLoss(reduction="mean")
            optimizer = torch.optim.Adam(model.parameters(), lr=lr)

            results.append(train_model(model, loss_fn, optimizer, repeat))

        print("\rLr: {}: {}".format(
            lr, np.mean(results)
        ))