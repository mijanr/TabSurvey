import sklearn.datasets
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder

import numpy as np
import pandas as pd


def discretize_colum(data_clm, num_values=10):
    """ Discretize a column by quantiles """
    r = np.argsort(data_clm)
    bin_sz = (len(r) / num_values) + 1  # make sure all quantiles are in range 0-(num_quarts-1)
    q = r // bin_sz
    return q


def load_data(args):
    print("Loading dataset " + args.dataset + "...")

    if args.dataset == "CaliforniaHousing":  # Regression dataset
        X, y = sklearn.datasets.fetch_california_housing(return_X_y=True)

    elif args.dataset == "Covertype":  # Multi-class classification dataset
        X, y = sklearn.datasets.fetch_covtype(return_X_y=True)
        # X, y = X[:10000, :], y[:10000]  # only take 10000 samples from dataset

    elif args.dataset == "KddCup99":  # Multi-class classification dataset with categorical data
        X, y = sklearn.datasets.fetch_kddcup99(return_X_y=True)
        X, y = X[:10000, :], y[:10000]  # only take 10000 samples from dataset

        # filter out all target classes, that occur less than 1%
        target_counts = np.unique(y, return_counts=True)
        smaller1 = int(X.shape[0] * 0.01)
        small_idx = np.where(target_counts[1] < smaller1)
        small_tar = target_counts[0][small_idx]
        for tar in small_tar:
            idx = np.where(y == tar)
            y[idx] = b"others"

        # new_target_counts = np.unique(y, return_counts=True)
        # print(new_target_counts)

        '''
        # filter out all target classes, that occur less than 100
        target_counts = np.unique(y, return_counts=True)
        small_idx = np.where(target_counts[1] < 100)
        small_tar = target_counts[0][small_idx]
        for tar in small_tar:
            idx = np.where(y == tar)
            y[idx] = b"others"

        # new_target_counts = np.unique(y, return_counts=True)
        # print(new_target_counts)
        '''
    elif args.dataset == "Adult" or args.dataset == "AdultCat":  # Binary classification dataset with categorical data, if you pass AdultCat, the numerical columns will be discretized.
        url_data = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"

        features = ['age', 'workclass', 'fnlwgt', 'education', 'education_num', 'marital-status', 'occupation',
                    'relationship', 'race', 'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 'native-country']
        label = "income"
        columns = features + [label]
        df = pd.read_csv(url_data, names=columns)

        # Fill NaN with something better?
        df.fillna(0, inplace=True)
        if args.dataset == "AdultCat":
            columns_to_discr = [('age', 10), ('fnlwgt', 25), ('capital-gain', 10), ('capital-loss', 10),
                                ('hours-per-week', 10)]
            for clm, nvals in columns_to_discr:
                df[clm] = discretize_colum(df[clm], num_values=nvals)
                df[clm] = df[clm].astype(int).astype(str)
            df['education_num'] = df['education_num'].astype(int).astype(str)
            args.cat_idx = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
        X = df[features].to_numpy()
        y = df[label].to_numpy()

    elif args.dataset == "HIGGS":  # Binary classification dataset with one categorical feature
        path = "/opt/notebooks/data/HIGGS.csv.gz"
        df = pd.read_csv(path, header=None)
        df.columns = ['x' + str(i) for i in range(df.shape[1])]
        num_col = list(df.drop(['x0', 'x21'], 1).columns)
        cat_col = ['x21']
        label_col = 'x0'

        def fe(x):
            if x > 2:
                return 1
            elif x > 1:
                return 0
            else:
                return 2

        df.x21 = df.x21.apply(fe)

        # Fill NaN with something better?
        df.fillna(0, inplace=True)

        X = df[num_col + cat_col].to_numpy()
        y = df[label_col].to_numpy()

    elif args.dataset == "Heloc":  # Binary classification dataset without categorical data
        path = "heloc_cleaned.csv"  # Missing values already filtered
        df = pd.read_csv(path)
        label_col = 'RiskPerformance'

        X = df.drop(label_col, axis=1).to_numpy()
        y = df[label_col].to_numpy()
    elif args.dataset == 'k80':
        path = "./data/simple.k80.s221.50k.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'k160':
        path = "./data/simple.k160.s221.50k.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'k160_s221_100k_f75':
        path = "./data/simple.k160.s221.100k.f75.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'k160_s221_100k_f76':
        path = "./data/simple.k160.s221.100k.f76.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'k160_s221_100k_f74':
        path = "./data/simple.k160.s221.100k.f74.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'k160_s221_100k_f75_selected':
        path = "./data/simple.k160.s221.100k.f75_selected.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'k160_s221_500k_f75':
        path = "./data/simple.k160.s221.500k.f75.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'k160_s221_500k_f75_selected':
        path = "./data/simple.k160.s221.500k.f75_selected.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'prefix_k67_s112_1500k_f73':
        path = "./data/prefix.k67.s112.1500k.f73.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'prefix_k67_s112_1500k_f73_selected':
        path = "./data/prefix.k67.s112.1500k.f73_selected.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'k_67_s112_100k_f83':
        path = "./data/simple.k67.s112.100k.f83.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'k_67_s112_100k_f83_selected':
        path = "./data/simple.k67.s112.100k.f83_selected.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'prefix_k67_s112_1500k_f66':
        path = "./data/prefix.k67.s112.1500k.f66.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'prefix_k67_s112_1500k_f66_selected':
        path = "./data/prefix.k67.s112.1500k.f66_selected.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'prefix_k67_s112_1500k_f66_selected_10':
        path = "./data/prefix.k67.s112.1500k.f66_selected_10.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'range_k67_s112_1500k_f83_f2_38':
        path = "./data/range.k67.s112.1500k.f83.f2_38.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'range_k67_s112_1500k_f47_f2_52':
        path = "./data/range.k67.s112.1500k.f47.f2_52.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'prefix_k67_s112_1500k_f_list':
        path = "./data/prefix.k67.s112.1500k.f[0, 20, 40, 60, 80, 100, 120, 140].csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'fwht_k160_s112_50k':
        path = "./data/fwht.k160.s112.50k.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'fwht2_k128_s112_50k':
        path = "./data/fwht2.k128.s112.50k.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        df = df.iloc[:, 0:129]
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'simple_k160_s221_100k_f75_selected_phik':
        path = "./data/simple.k160.s221.100k.f75.selected_phik.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == 'simple_k160_s221_100k_f75_selected_phik_10':
        path = "./data/simple.k160.s221.100k.f75.selected_phik_10.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == '05_two_bits_k160_s221_1000k_f80_160':
        path = "./data/05_two_bits.k160.s221.1000k.f80.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-2].to_numpy()
        y = df.iloc[:, -2].to_numpy()
    elif args.dataset == '05_two_bits_k160_s221_1000k_f80_161':
        path = "./data/05_two_bits.k160.s221.1000k.f80.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-2].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == '05_two_bits_k160_s221_1000k_f80_160_10k_samples':
        path = "./data/05_two_bits.k160.s221.1000k.f80.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        #choose 10k samples
        df = df.sample(n=10000, random_state=42)
        X = df.iloc[:, :-2].to_numpy()
        y = df.iloc[:, -2].to_numpy()
    elif args.dataset == '05_two_bits_k160_s221_1000k_f80_161_10k_samples':
        path = "./data/05_two_bits.k160.s221.1000k.f80.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        #choose 10k samples
        df = df.sample(n=10000, random_state=42)
        X = df.iloc[:, :-2].to_numpy()
        y = df.iloc[:, -1].to_numpy() 
    elif args.dataset == "05_two_bits_k160_s221_1000k_f80_160_1k_samples":
        path = "./data/05_two_bits.k160.s221.1000k.f80.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        #choose 1k samples
        df = df.sample(n=1000, random_state=42)  
        X = df.iloc[:, :-2].to_numpy()
        y = df.iloc[:, -2].to_numpy()
    elif args.dataset == "05_two_bits_k160_s221_1000k_f80_161_1k_samples":
        path = "./data/05_two_bits.k160.s221.1000k.f80.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        #choose 1k samples
        df = df.sample(n=1000, random_state=42)
        X = df.iloc[:, :-2].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == "simple_k160_s221_100k_f75_1k_samples":
        path = "./data/simple.k160.s221.100k.f75.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        #choose 1k samples
        df = df.sample(n=1000, random_state=42)
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()
    elif args.dataset == "simple_k160_s221_100k_f75_exp":
        path = "./data/simple.k160.s221.100k.f75.csv.gz"
        df = pd.read_csv(path, compression='gzip', header=None, sep=' ')
        X = df.iloc[:, :-1].to_numpy()
        y = df.iloc[:, -1].to_numpy()

    else:
        raise AttributeError("Dataset \"" + args.dataset + "\" not available")

    print("Dataset loaded!")
    print(X.shape)

    # Preprocess target
    if args.target_encode:
        le = LabelEncoder()
        y = le.fit_transform(y)

        # Setting this if classification task
        if args.objective == "classification":
            args.num_classes = len(le.classes_)
            print("Having", args.num_classes, "classes as target.")

    num_idx = []
    args.cat_dims = []

    # Preprocess data
    for i in range(args.num_features):
        if args.cat_idx and i in args.cat_idx:
            le = LabelEncoder()
            X[:, i] = le.fit_transform(X[:, i])

            # Setting this?
            args.cat_dims.append(len(le.classes_))

        else:
            num_idx.append(i)

    if args.scale:
        print("Scaling the data...")
        scaler = StandardScaler()
        X[:, num_idx] = scaler.fit_transform(X[:, num_idx])

    if args.one_hot_encode:
        ohe = OneHotEncoder(sparse=False, handle_unknown='ignore')
        new_x1 = ohe.fit_transform(X[:, args.cat_idx])
        new_x2 = X[:, num_idx]
        X = np.concatenate([new_x1, new_x2], axis=1)
        print("New Shape:", X.shape)

    return X, y
