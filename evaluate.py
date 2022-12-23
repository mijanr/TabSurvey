from utils.io_utils import get_predictions_from_file, save_results_to_file
from utils.parser import get_given_parameters_parser
from utils.scorer import get_scorer

import numpy as np
import pandas as pd

def main(args):
    print("Evaluate model " + args.model_name)

    predictions = get_predictions_from_file(args)
    scorer = get_scorer(args)
    #from here
    stacked_predictions = np.vstack(predictions)
    #conver to dataframe
    df = pd.DataFrame(stacked_predictions)
    #rename columns
    df.columns = ['truth', 'pred_0', 'pred_1']
    #save to csv
    name = args.model_name + "_prediction_" + args.dataset + ".csv"
    df.to_csv(name, index=False)
    for pred in predictions:
        # [:,0] is the truth and [:,1:] are the prediction probabilities

        truth = pred[:, 0]
        out = pred[:, 1:]
        pred_label = np.argmax(out, axis=1)

        scorer.eval(truth, pred_label, out)

    result = scorer.get_results()
    print(result)

    save_results_to_file(args, result)


if __name__ == "__main__":

    # Also load the best parameters
    parser = get_given_parameters_parser()
    arguments = parser.parse_args()
    print(arguments)

    main(arguments)
