import sys
print("Python version:", sys.version)

try:
    import torch
    print("\nPyTorch version:", torch.__version__)
    print("CUDA available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("CUDA version:", torch.version.cuda)
        print("Current device:", torch.cuda.current_device())
        print("Device name:", torch.cuda.get_device_name(0))
    else:
        print("CUDA is not available")
except Exception as e:
    print("Error:", str(e))
