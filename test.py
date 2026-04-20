import torch
import time

def test_gpu():
    print(f"PyTorch 版本: {torch.__version__}")
    
    # 1. 基本檢查
    if not torch.cuda.is_available():
        print("❌ 沒抓到 GPU，目前使用的是 CPU 模式。")
        return
    
    device = torch.device("cuda")
    print(f"✅ 抓到 GPU: {torch.cuda.get_device_name(0)}")
    
    # 2. 建立一個 10000x10000 的巨大矩陣 (約佔用 400MB 顯存)
    print("正在將矩陣推向 GPU 並進行運算測試...")
    try:
        x = torch.randn(10000, 10000, device=device)
        y = torch.randn(10000, 10000, device=device)
        
        # 紀錄運算時間
        start_time = time.time()
        # 進行矩陣乘法 (Matrix Multiplication)
        z = torch.matmul(x, y)
        # 強制同步，確保運算完成
        torch.cuda.synchronize()
        end_time = time.time()
        
        print(f"🔥 運算成功！耗時: {end_time - start_time:.4f} 秒")
        print(f"目前顯存佔用: {torch.cuda.memory_allocated(0) / 1024**2:.2f} MB")
        
    except Exception as e:
        print(f"❌ 運算過程中發生錯誤: {e}")

if __name__ == "__main__":
    test_gpu()