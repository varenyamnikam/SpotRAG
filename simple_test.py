try:
    import torch
    print("Success! PyTorch version:", torch.__version__)
except Exception as e:
    print(f"Error importing torch: {e}")
