#install by executing: "bash -l envs.sh" in the terminal
#this will create all the necessary environments
set -euo pipefail


# Set up Sklearn environment
conda create -n sklearn -y scikit-learn
eval "$(conda shell.bash hook)"
conda activate sklearn
conda install -n sklearn -y -c anaconda ipykernel
python -m ipykernel install --user --name=sklearn
conda install -n sklearn -y -c conda-forge configargparse
conda install -n sklearn -y pandas
python -m pip install optuna

#############################################################################################################

# Set up GBDT environment
conda create -n gbdt -y
eval "$(conda shell.bash hook)"
conda activate gbdt
conda install -n gbdt -y -c anaconda ipykernel
python -m ipykernel install --user --name=gbdt
python -m pip install xgboost==1.5.0 catboost==1.0.3 lightgbm==3.3.1 optuna
conda install -n gbdt -y -c conda-forge configargparse
conda install -n gbdt -y scikit-learn pandas
# For ModelTrees
python -m pip install https://github.com/schufa-innovationlab/model-trees/archive/master.zip

#############################################################################################################

# Set up Pytorch environment
conda create -n torch -y pytorch cudatoolkit=11.3 -c pytorch
eval "$(conda shell.bash hook)"
conda activate torch
conda install -n torch -y -c anaconda ipykernel
python -m ipykernel install --user --name=torch
conda install -n torch -y -c conda-forge configargparse
conda install -n torch -y scikit-learn pandas matplotlib shap
conda install -n torch -y -c pytorch captum
python -m pip install requests qhoptim lightgbm==3.3.1 einops pytorch-tabnet einops optuna nam h5py yacs lifelines

#############################################################################################################

# Set up Keras environment
conda create -n tensorflow -y tensorflow-gpu=1.15.0 keras
eval "$(conda shell.bash hook)"
conda activate tensorflow
conda install -n tensorflow -y -c anaconda ipykernel
conda install -n tensorflow -y -c conda-forge configargparse
conda install -n tensorflow -y scikit-learn pandas
python -m pip install stg==0.1.2 optuna tabulate yacs
python -m pip install https://github.com/AmrMKayid/nam/archive/main.zip



