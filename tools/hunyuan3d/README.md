# Tạo model Gun ZONE bằng Hunyuan3D-2

Bộ lệnh tạo model từ ảnh, xuất GLB và căn nhân vật theo chiều cao 1,7732026344 m của Gun ZONE. Nguồn Hunyuan được tải vào thư mục làm việc riêng khi chạy setup.

- Repo nguồn https://github.com/Tencent-Hunyuan/Hunyuan3D-2
- Revision f8db63096c8282cb27354314d896feba5ba6ff8a
- Trọng số tencent/Hunyuan3D-2 được tải khi chạy lần đầu.
- Model xuất ra cần gắn xương, ghép chuyển động và kiểm tra trong game trước khi thêm vào Trang phục.

## Chuẩn bị trên Windows

Cài Git, Python và môi trường biên dịch CUDA phù hợp với PyTorch. Phần texture sử dụng hai extension CUDA của upstream. README upstream công bố khoảng 6 GB VRAM cho hình khối và 16 GB cho hình khối cùng texture. Bộ lệnh này sử dụng NVIDIA CUDA.

Từ thư mục repo Gun ZONE chạy trong PowerShell.

```powershell
python tools/hunyuan3d/setup.py --workspace D:/AZONE-Hunyuan --texture
```

Lần đầu, setup tạo môi trường Python và in đường dẫn executable. Chọn gói PyTorch CUDA tương ứng máy tại https://pytorch.org/get-started/locally/ rồi cài torch và torchvision bằng Python trong môi trường vừa tạo.

```powershell
& D:/AZONE-Hunyuan/venv/Scripts/python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
python tools/hunyuan3d/setup.py --workspace D:/AZONE-Hunyuan --texture
```

Lệnh cu128 là ví dụ cho máy có driver tương thích CUDA 12.8. Chọn lại index theo cấu hình thực tế. Trên Linux, executable nằm ở venv/bin/python. Cài extension texture cần CUDA Toolkit cùng compiler tương thích.

## Tạo nhân vật từ ảnh

Ảnh toàn thân, tay chân tách rõ và hướng đứng thẳng giúp chuẩn bị rig. Mặc định công cụ xóa nền ảnh opaque, tạo hình khối, giảm lưới về mục tiêu 30.000 tam giác, tạo texture nếu có --texture, căn chân về mặt đất và xuất GLB theo trục Y hướng lên.

```powershell
& D:/AZONE-Hunyuan/venv/Scripts/python.exe tools/hunyuan3d/generate.py D:/Anh/nhan-vat.png --output D:/Models/nhan-vat.glb --texture --seed 42
```

Dùng --keep-background để giữ nền đầu vào. Có thể chỉnh --height, --steps và --faces. Chọn tên đầu ra mới cho mỗi lần chạy. Sau khi xuất, kiểm tra hướng mặt, topology, UV, rig và các động tác cầm súng, chạy, ngồi trước khi tích hợp.

## Trạng thái kiểm tra

Đã kiểm tra cú pháp Python, CLI và phép chuẩn hóa chiều cao. Môi trường thực hiện cập nhật chưa có PyTorch và GPU CUDA được xác nhận, nên chưa chạy suy luận tạo model hoặc kiểm chứng cài extension CUDA.

Mã và trọng số upstream đi kèm giấy phép tại repo nguồn. Giữ các tệp giấy phép khi tải và phân phối.
