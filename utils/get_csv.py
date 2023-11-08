import csv
import get_data

# new_data_list = get_data.processing_data(page_index=1, page_size=10, total=50)
new_data_list = get_data.processing_data()
# print(new_data_list)

with open("dummy_restaurant.csv", 'w', encoding='utf-8') as file:
    header = list(get_data.DB_FIELD.values())
    writer = csv.DictWriter(file, fieldnames=header)
    writer.writeheader()

  # 데이터를 CSV 파일에 쓰기
    for el in new_data_list:
      for row in el:
          writer.writerow(row)