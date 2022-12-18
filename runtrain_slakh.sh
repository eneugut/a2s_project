if [[ $# -lt 3 ]] ; then
    echo 'missing arguments: ./runtrain.sh config manifest_id model_id [args]'
    exit -1
fi
config=$1
manid=$2
modid=$3
shift 3
# Or python -m multiproc for multi-GPU training 
python train.py --cuda --config-path configs/slakh.cfg --train-manifest train_slakh.csv --val-manifest val_slakh.csv --labels-path labels_slakh.json --num-workers 4 --model-path models/slakh.pth


# baby slakh
python train.py --cuda --config-path configs/slakh.cfg --train-manifest train_baby_slakh.csv --val-manifest validation_baby_slakh.csv --labels-path labels_slakh.json --num-workers 4 --model-path models/slakh.pth

#regular slakh
python train.py --config-path configs/slakh.cfg --train-manifest train_slakh.csv --val-manifest val_slakh.csv --labels-path labels_slakh.json --num-workers 4 --model-path models/slakh.pth


pip3 install torch torchaudio --extra-index-url https://download.pytorch.org/whl/cu117

