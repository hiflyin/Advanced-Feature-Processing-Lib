

from feature_stuff.pandas_based import *
from model_features_insights_extractions import *
import xgboost as xgb

def generate_mock_data():

    df = pd.DataFrame([["a", "a", 1, 18]], columns=["cat1", "cat2", "num1", "num2"])
    df.loc[1] = ["a", "a", 1, 3]
    df.loc[2] = ["a", "b", 2, 4]
    df.loc[3] = ["a", "b", 2, 4]
    df.loc[4] = ["b", "c", 1, 3]
    df.loc[5] = ["b", "d", 2, 4]
    df.loc[6] = ["b", "d", 2, 4]
    df.loc[17] = ["b", "e", 3, 3]
    df.loc[15] = ["b", "e", 3, 4]
    df.loc[16] = ["b", "e", 3, 4]
    df.loc[7] = ["c", "f", 1, 3]
    df.loc[8] = ["c", "f", 2, 4]
    df.loc[9] = ["c", "f", 2, 4]
    df.loc[10] = ["c", "g", 3, 4]
    df.loc[11] = ["d", "h", 1, 3]
    df.loc[12] = ["d", "h", 1, 4]
    df.loc[13] = ["d", "h", 1, 4]
    df.loc[14] = ["d", "i", 2, 4]

    return df

def createDF(arrs):

    d = {}
    for i in range(len(arrs)):
        d["x" + str(i)] = arrs[i]
    df = pd.DataFrame(data=d, index=range(len(arrs[0])))

    return df

def test_addInteractions():

    data = createDF([[0,1,0,1], range(4), [1,0,1,0]])
    target = data.x0 * data.x1 + data.x2*data.x1
    model = xgb.train({'max_depth': 4, "seed": 123}, xgb.DMatrix(data, label=target), num_boost_round=2)
    data = addInteractions(data, model)

    # either at least one of these interactions must have been discovered
    assert data.inter_0.values.tolist() == [x for x in data.x0 * data.x1] or data.inter_0.values.tolist() == [x for x in
                                                                                                              data.x2 * data.x1]

    interactions = get_xgboost_interactions(model)
    data = createDF([[0, 1, 0, 1], range(4), [1, 0, 1, 0]])
    data = addInteractions(data, model, interactions=interactions)

    # either at least one of these interactions must have been discovered
    assert data.inter_0.values.tolist() == [x for x in data.x0 * data.x1] or data.inter_0.values.tolist() == [x for x in data.x2 * data.x1]

def test_add_group_values():

    data = createDF([[0, 1, 0, 1], range(4), [1, 0, 1, 0]])
    data = add_group_values(data, ["x0"], "x1", "x1_sum", sum, agg_type='float32')
    assert data.x1_sum.values.tolist() == [2,4,2,4]

def test_targetEncoding():

    train_data = createDF([[0, 1, 0, 1], range(4)])
    test_data = createDF([[1, 0, 0, 1], range(4)])
    target = range(4)

    test_data = targetEncoding(test_data, train_data, "x0", target, smoothing_func=exponentialPriorSmoothing, aggr_func="mean", smoothing_prior_weight=1)

    assert test_data.x0_bayes_mean.values.tolist()==[1.7310585786300048, 1.0, 1.0, 1.7310585786300048]

def test_add_dummies_selected_cat():

    df = generate_mock_data()
    df = df.loc[df['cat2'].isin(['a', 'b'])]
    result = add_dummies(["cat2"], df)

    assert result.shape[0] == df.shape[0]
    assert result["cat2_a"].values.tolist() == [1, 1, 0, 0]
    assert result["cat2_b"].values.tolist() == [0, 0, 1, 1]

def test_add_dummies_selected_cat():

    df = generate_mock_data()
    df = df.loc[df.cat2.isin(["a", "b", "c"]),]
    result = add_dummies_selected_cat("cat2", df, ["a", "b"])

    assert result.shape[0] == df.shape[0]
    assert result.shape[1] == df.shape[1] +1 # added 2 dummies and dropped one col
    assert result["cat2_a"].values.tolist() == [1,1,0,0,0]
    assert result["cat2_b"].values.tolist() == [0, 0, 1, 1, 0]