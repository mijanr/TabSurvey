#!/bin/bash

# N_TRIALS=2
# EPOCHS=3

SKLEARN_ENV="sklearn"
GBDT_ENV="gbdt"
TORCH_ENV="torch"
KERAS_ENV="keras"

# "LinearModel" "KNN" "DecisionTree" "RandomForest"
# "XGBoost" "CatBoost" "LightGBM"
# "MLP" "TabNet" "VIME"
# MODELS=( "LinearModel" "KNN" "DecisionTree" "RandomForest" "XGBoost" "CatBoost" "LightGBM" "MLP" "TabNet" "VIME")

declare -A MODELS
MODELS=( #
        # ["LinearModel"]=$SKLEARN_ENV
        #  ["KNN"]=$SKLEARN_ENV
        #  ["SVM"]=$SKLEARN_ENV
        #["DecisionTree"]=$SKLEARN_ENV
        #["RandomForest"]=$SKLEARN_ENV
        #["XGBoost"]=$GBDT_ENV
        #["CatBoost"]=$GBDT_ENV
        #["LightGBM"]=$GBDT_ENV
        #  ["MLP"]=$TORCH_ENV
        #["TabNet"]=$TORCH_ENV
        #  ["VIME"]=$TORCH_ENV
        #["TabTransformer"]=$TORCH_ENV
        #  ["ModelTree"]=$GBDT_ENV
         #["NODE"]=$TORCH_ENV
        #["DeepGBM"]=$TORCH_ENV
        #  ["RLN"]=$KERAS_ENV
        #["DNFNet"]=$KERAS_ENV
        #  ["STG"]=$TORCH_ENV
         # ["NAM"]=$TORCH_ENV
         #["DeepFM"]=$TORCH_ENV
        #  ["SAINT"]=$TORCH_ENV
         ["DANet"]=$TORCH_ENV
          )

CONFIGS=( #"config/k80.yml"
          #"config/k160_s221_100k_f75.yml"
          # "config/k160_s221_100k_f76.yml"
          # "config/k160_s221_100k_f74.yml"
          #"config/k160_s221_100k_f75_selected.yml"
          #"config/k160_s221_500k_f75.yml"
          #"config/k160_s221_500k_f75_selected.yml"
          #"config/prefix_k67_s112_1500k_f73.yml"
          #"config/prefix_k67_s112_1500k_f73_selected.yml"
          #"config/prefix_k67_s112_1500k_f66.yml"
          #"config/prefix_k67_s112_1500k_f66_selected.yml"
          #"config/prefix_k67_s112_1500k_f66_selected_10.yml"
          #"config/range_k67_s112_1500k_f83_f2_38.yml"
          # "config/prefix_k67_s112_1500k_f_list.yml"
          # "config/range_k67_s112_1500k_f47_f2_52.yml"
          #"config/fwht2_k128_s112_50k.yml"
          #"config/simple_k160_s221_100k_f75_selected_phik.yml"
          #"config/simple_k160_s221_100k_f75_selected_phik_10.yml"
          # "config/05_two_bits_k160_s221_1000k_f80_160.yml"
          # "config/05_two_bits_k160_s221_1000k_f80_161.yml"
          #"config/05_two_bits_k160_s221_1000k_f80_160_10k_samples.yml"
          #"config/05_two_bits_k160_s221_1000k_f80_161_10k_samples.yml"
          # "config/05_two_bits_k160_s221_1000k_f80_161_1k_samples.yml"
          # "config/05_two_bits_k160_s221_1000k_f80_160_1k_samples.yml"    
          #"config/simple_k160_s221_100k_f75_1k_samples.yml"  
          # "config/simple_k160_s221_100k_f75_500_samples.yml"
          # "config/simple_k160_s221_100k_f75_2k_samples.yml"
          #"config/simple_k160_s221_100k_f75_3k_samples.yml"
          # "config/simple_k160_s221_100k_f75_250_samples.yml"
          # "config/simple_k160_s221_100k_f75_700_samples.yml"
          # "config/simple_k160_s221_100k_f75_selected_phik_10_1k_samples.yml"
          # "config/simple_k160_s221_100k_f75_selected_phik_10_250_samples.yml"
          # "config/simple_k160_s221_100k_f75_selected_phik_10_500_samples.yml"
          # "config/simple_k160_s221_100k_f75_selected_phik_10_750_samples.yml"
          #"config/simple_k160_s221_100k_f75_50_50_split.yml"
          "config/simple_k160_s221_100k_f75_exp.yml"
          )

# conda init bash
eval "$(conda shell.bash hook)"

for config in "${CONFIGS[@]}"; do

  for model in "${!MODELS[@]}"; do
    printf "\n\n----------------------------------------------------------------------------\n"
    printf 'Training %s with %s in env %s\n\n' "$model" "$config" "${MODELS[$model]}"

    conda activate "${MODELS[$model]}"

    python train.py --config "$config" --model_name "$model" 

    conda deactivate

  done

done
