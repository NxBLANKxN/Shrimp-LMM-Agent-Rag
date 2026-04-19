import torch
print(f"GPU 是否可用: {torch.cuda.is_available()}")
print(f"目前使用的裝置: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")