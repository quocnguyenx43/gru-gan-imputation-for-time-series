<!-- Banner -->
<p align="center">
  <a href="https://www.uit.edu.vn/" title="Trường Đại học Công nghệ Thông tin" style="border: none;">
    <img src="https://i.imgur.com/WmMnSRt.png" alt="Trường Đại học Công nghệ Thông tin | University of Information Technology">
  </a>
</p>

<h1 align="center"><b>Phân tích và trực quan hóa dữ liệu - DS105.N11</b></h>

## COURSE INTRODUCTION

- **Name:** Phân tích và trực quan hóa dữ liệu - Data Visualization & Analysis
- **Course ID:** DS105
- **Class ID:** DS105.N11
- **Year:** First Semester (2022 - 2023)
- **Lecturer**: MSc. Phạm Thế Sơn

## Giải thích cấu trúc thư mục
- `data`: Thư mục chứa tập dữ liệu.
- `application`: Thư mục chứa triển khai Flask Server (Dashboard và vis kết quả thực nghiệm của các phương pháp điền khuyết).
- `gan`: Thư mục chứa triển khai mô hình **GAN**
    * `config.ymal`: Config các biến toàn cục và các tham số của mô hình (missing_ratio, batch_size, learning_rate,...).
    * `deterioration.py`: Tạo dữ liệu khuyết.
    * `load_data.py`: Đọc các siêu tham số, dữ liệu và tính toán ma trận Boundary. 
    * `processing.py`: Chuyển đổi dữ liệu thành dạng input đầu vào của model.
    * `tools.py`: Tạo label cho Discriminator và sinh dữ liệu fake/real.
    * `model.py`: Triển khai các Model: Generator, Discriminator và GAN.
    * `train.py`: Train model.
- `notebooks`: Thư mục chứa các file `*.ipynb` thực hiện các tác vụ như `EDA`, vẽ thử các charts và xây dựng thử mô hình **GAN**
    * `eda.ipynb`: EDA.
    * `plot.ipynb`: Thử nghiệm plot dashboard.
    * `GANnCompare.ipynb`: Xây dựng thử nghiệm mô hình **GAN**.
- `results`: Thư mục chứa các file `.csv` là kết quả của các phương pháp điền khuyết.
    * `gan.csv`, `knn.csv`, `random.csv`: Các bộ dữ liệu được điền khuyết bởi mô hình.
    * `boundary.csv`: Biên.
    * `metrics`: Kết quả chạy các mô hình hồi quy.
- `run.py`: File chạy trực tiếp và train mô hình **GAN**
- `main.py`: File start **Flask Server** chạy trên `localhost:5000`.
- `requirements.txt`: File chứa các yêu cầu thư viện Python cần thiết chạy project này.
- `README.md`

## 1. Chạy console: `python main.py` hoặc xem trong file `GANnCompare.ipynb`

## 2. Chạy Flask Server localhost: Dashboard trực quan hóa dữ liệu và mô hình GAN
    - Cài môi trường ảo: `pip install virtualenv`
    - Tạo môi trường ảo: `virtualenv venv`
    - Active môi trường ảo: `venv\Scripts\activate`
    - Cài đặt các thư viện và framework yêu cầu: `pip install -r requirements.txt`
    - Chạy `python run.py`

`pip3 freeze > requirements.txt`
