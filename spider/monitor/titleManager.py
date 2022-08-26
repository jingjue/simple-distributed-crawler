"""
将不同平台的关键词保存到不同的redis数据库中
"""
from base.db.dbSlot import Slot
from models.predict import build_dataset, build_iterator
from monitor.setting import REDIS_KEYWORD
from monitor import logger


class Title:
    def __init__(self, keywords: set = None):
        if keywords:
            self.keywords = keywords
        else:
            self.keywords = set()

    def append(self, keyword):
        self.keywords.add(keyword)

    def __add__(self, other):
        if isinstance(other, Title):
            return Title(self.keywords | other.keywords)
        else:
            return self

    def wipe_data(self):
        self.keywords.clear()


class TitleManager:
    def __init__(self):
        self.keywords = {}  # platform:Title

    def __getitem__(self, item):
        if self.keywords.get(item, False):
            return self.keywords[item]
        else:
            self.keywords[item] = Title()
            return self.keywords[item]

    def __setitem__(self, key, value):
        self.keywords[key] = value

    def wipe_data(self):
        """
        清空所有关键词
        :return:
        """
        for key in self.keywords:
            self.keywords[key].wipe_data()

    def classify(self, titles=None):
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

    def persist(self, dbslot: Slot):
        """
        根据不同平台的关键词保存到不同的redis数据库当中
        """
        for platform, title in self.keywords.items():
            redis_key = REDIS_KEYWORD.substitute(platform=platform)
            keywords = self.keywords[platform].keywords
            if keywords:
                dbslot.redis.sadd(redis_key, *self.keywords[platform].keywords)
                logger.info(f"{platform} keywords saved to {redis_key} {list(self.keywords[platform].keywords)}")


if __name__ == '__main__':
    t = TitleManager()
    t["baidu"] = Title({"a", "b", "c"})
    tt = Title({"a", "b", "c", "d"})
    t["baibu"] += tt
