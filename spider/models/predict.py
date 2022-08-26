# coding: UTF-8
import pickle as pkl
from importlib import import_module

import jieba
import numpy as np
import pandas as pd
import torch

UNK, PAD = '<UNK>', '<PAD>'  # 未知字，padding符号


def build_dataset():
    vocab = pkl.load(open("./data/vocab.pkl", "rb"))
    print(f"Vocab size: {len(vocab)}")

    def load_dataset(pad_size=16):
        new_data = pd.read_csv("../keywords/2021年/10月/2021年10月09日20点.csv")
        contents = []
        contents_emb = []
        for row in new_data.iterrows():
            content = row[1]["keyword"]
            contents.append(content)
            if not content:
                continue
            words_line = []
            words = [word for word in jieba.cut(content, cut_all=False)]
            seq_len = len(words)
            if pad_size:
                if len(words) < pad_size:
                    words.extend([PAD] * (pad_size - len(words)))
                else:
                    words = words[:pad_size]
                    seq_len = pad_size
            for word in words:
                words_line.append(vocab.get(word, vocab.get(UNK)))
            contents_emb.append((words_line, seq_len))
        return contents, contents_emb

    contents, contents_emb = load_dataset()
    return vocab, contents, contents_emb


class DatasetIterator(object):
    def __init__(self, batches, batch_size, device):
        self.batch_size = batch_size
        self.batches = batches
        self.n_batches = len(batches) // batch_size
        self.residue = False  # 记录batch数量是否为整数
        if len(batches) % self.n_batches != 0:
            self.residue = True
        self.index = 0
        self.device = device

    def _to_tensor(self, data):
        x = torch.LongTensor([_[0] for _ in data]).to(self.device)
        seq_len = torch.LongTensor([_[1] for _ in data]).to(self.device)
        return (x, seq_len)

    def __next__(self):
        if self.residue and self.index == self.n_batches:
            batches = self.batches[self.index * self.batch_size: len(self.batches)]
            self.index += 1
            batches = self._to_tensor(batches)
            return batches

        elif self.index >= self.n_batches:
            self.index = 0
            raise StopIteration
        else:
            batches = self.batches[self.index * self.batch_size: (self.index + 1) * self.batch_size]
            self.index += 1
            batches = self._to_tensor(batches)
            return batches

    def __iter__(self):
        return self

    def __len__(self):
        if self.residue:
            return self.n_batches + 1
        else:
            return self.n_batches


def build_iterator(dataset, config):
    return DatasetIterator(dataset, config.batch_size, config.device)


def execute(config, model, data_iter):
    # test
    model.load_state_dict(torch.load(config.save_path))
    model.eval()
    predict_all = np.array([], dtype=int)
    with torch.no_grad():
        for texts in data_iter:
            outputs = model(texts)
            predict = torch.max(outputs.data, 1)[1].cpu().numpy()
            predict_all = np.append(predict_all, predict)
    return predict_all


if __name__ == '__main__':
    x = import_module('models.TextCNN')
    config = x.Config()
    np.random.seed(1)
    torch.manual_seed(1)
    torch.cuda.manual_seed_all(1)
    torch.backends.cudnn.deterministic = True  # 保证每次结果一样

    vocab, contents, contents_emb = build_dataset()
    contents_iter = build_iterator(contents_emb, config)

    config.n_vocab = len(vocab)
    model = x.Model(config).to(config.device)
    predict_all = execute(config, model, contents_iter)
    dict = {0: "财经", 1: "房地产", 2: "股票", 3: "教育", 4: "科学", 5: "社会", 6: "政治", 7: "运动", 8: "游戏", 9: "娱乐"}

    for i in range(0, len(predict_all)):
        print(contents[i] + " " + dict[predict_all[i]])

