import tensorflow as tf


INPUT_COLS = ['pickup_longitude', 'pickup_latitude', 
                  'dropoff_longitude', 'dropoff_latitude', 
                  'passenger_count']

# TODO 2
# input layer
inputs = {
   colname : tf.keras.layers.Input(name=colname, shape=(), dtype='float32')
        for colname in INPUT_COLS
}

print(f'inputs: {inputs}')

