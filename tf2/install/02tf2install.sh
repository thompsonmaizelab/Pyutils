#!/usr/bin/env bash

# activate our virtual environment
source env/bin/activate

# install tensorflow 2
pip install --upgrade tensorflow

# verify the installation of tensorflow 2
python -c 'import tensorflow as tf;print(tf.reduce_sum(tf.random.normal([100,100])))'

# deactivate our virtual environment
deactivate

