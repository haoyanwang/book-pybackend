from app import myDb
from collections import defaultdict
from surprise import Reader
from surprise import SVD
from surprise import Dataset
from surprise import NormalPredictor
from surprise.model_selection import cross_validate
import pandas as pd

db = myDb['users']

class Recommand():
    def __init__(self):
        pass

    def get_top_n(predictions, n):
        top_n = defaultdict(list)
        for uid, iid, true_r, est, _ in predictions:
            top_n[uid].append((iid, est))
        for uid, user_ratings in top_n.items():
            user_ratings.sort(key=lambda x: x[1], reverse=True)
            top_n[uid] = user_ratings[:n]

        return top_n

    def gen_matrix(self):
        itemList = []
        userList = []
        ratingList = []
        result = db.find({})
        for i in result:
            if 'rate_map' in i:
                keysList = i['rate_map'].keys()
                for k in keysList:
                    itemList.append(k)
                    userList.append(i['username'])
                    ratingList.append(i['rate_map'][k])
        ratings_dict = {'itemID': itemList,
                        'userID': userList,
                        'rating': ratingList}
        df = pd.DataFrame(ratings_dict)

        reader = Reader(rating_scale=(1, 10))

        data = Dataset.load_from_df(df[['userID', 'itemID', 'rating']], reader)
        data.split(n_folds=5)
        cross_validate(NormalPredictor(), data, cv=5 ,measures=['RMSE', 'MAE'],verbose=True)
        trainset = data.build_full_trainset()
        algo = SVD()
        algo.fit(trainset)
        print(trainset)
        testset = trainset.build_anti_testset()
        predictions = algo.test(testset)
        print(predictions)
        for i in predictions:
            print(i)
        return predictions
