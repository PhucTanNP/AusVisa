# Data Files

Thư mục này chứa các file CSV để import vào Neo4j database.

## Required Files

Bạn cần copy các file CSV sau vào thư mục này:

1. `About_Final_Neo4j.csv` - Thông tin về các loại visa
2. `Eligibility_Final_Neo4j.csv` - Điều kiện đủ điều kiện cho visa
3. `Step_Final_Neo4j.csv` - Các bước xin visa
4. `Settlement_All.csv` - Thông tin về định cư tại Úc
5. `Uni_Info_Program_Final.csv` - Thông tin trường đại học và chương trình

## Import Data

Sau khi copy các file CSV vào thư mục này, chạy lệnh sau để import dữ liệu:

```bash
# Import tất cả dữ liệu
python scripts/run_all.py

# Hoặc import từng phần riêng lẻ
python scripts/import_visa.py
python scripts/import_settlement.py
python scripts/import_study.py
python scripts/import_cross_rel.py
```

## File Format

Các file CSV phải có encoding UTF-8 và format phù hợp với schema của Neo4j.

## Troubleshooting

Nếu gặp lỗi khi import:
1. Kiểm tra Neo4j connection trong `.env`
2. Đảm bảo các file CSV tồn tại và có đúng format
3. Xem logs trong thư mục `logs/` để debug
