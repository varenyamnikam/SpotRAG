import tensorflow as tf

# Check if TensorFlow is built with GPU support
print("Is TensorFlow built with GPU support? ", tf.test.is_built_with_cuda())

# List available GPUs
print("Available GPUs: ", tf.config.experimental.list_physical_devices('GPU'))

# Check TensorFlow version
print("TensorFlow version: ", tf.__version__)
