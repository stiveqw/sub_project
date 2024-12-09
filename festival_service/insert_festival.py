from sqlalchemy import create_engine, text
from config import Config
from datetime import datetime

# 데이터베이스 연결 설정
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)

# 삽입할 데이터
insert_data = """
INSERT INTO festivals (festival_key, title, total_seats, capacity, date) VALUES
(:festival_key, :title, :total_seats, :capacity, :date)
"""

festivals = [
    ('0f1g2h3i-4j5k-6l7m-8n9o-1p2q3r4s5t6u', '강릉 단오제', 200, 150, '2025-06-06'),
    ('0p2q3r4s-5t6u-7v8w-9x0y-1z2a3b4c5d6e', '포항 호미곶 해맞이 축제', 500, 400, '2025-01-01'),
    ('1f2e3d4c-5a6b-7c8d-9e1f-2g3h4i5j6k7l', '봄꽃 축제', 100, 25, '2025-03-20'),
    ('1g2h3i4j-5k6l-7m8n-9o1p-2q3r4s5t6u7v', '청계천 빛 축제', 250, 220, '2025-12-01'),
    ('1q3r4s5t-6u7v-8w9x-0y1z-2a3b4c5d6e7f', '수원 화성 문화제', 300, 250, '2025-09-20'),
    ('2e3d4c5a-6b7c-8d9e-1f2g-3h4i5j6k7l8m', '여름 해변 파티', 150, 80, '2025-07-15'),
    ('2h3i4j5k-6l7m-8n9o-1p2q-3r4s5t6u7v8w', '전주 비빔밥 축제', 100, 80, '2025-04-15'),
    ('2r4s5t6u-7v8w-9x0y-1z2a-3b4c5d6e7f8g', '안동 국제 탈춤 페스티벌', 200, 180, '2025-10-05'),
    ('3d4c5a6b-7c8d-9e1f-2g3h-4i5j6k7l8m9n', '가을 단풍 축제', 200, 150, '2025-10-10'),
    ('3i4j5k6l-7m8n-9o1p-2q3r-4s5t6u7v8w9x', '춘천 막국수 축제', 200, 100, '2025-07-20'),
    ('3s5t6u7v-8w9x-0y1z-2a3b-4c5d6e7f8g9h', '광주 비엔날레', 250, 200, '2025-04-01'),
    ('4c5a6b7c-8d9e-1f2g-3h4i-5j6k7l8m9n0o', '겨울 눈꽃 축제', 300, 200, '2025-12-25'),
    ('4j5k6l7m-8n9o-1p2q-3r4s-5t6u7v8w9x0y', '인천 송도 마라톤', 300, 280, '2025-09-01'),
    ('4t6u7v8w-9x0y-1z2a-3b4c-5d6e7f8g9h0i', '속초 오징어 축제', 150, 100, '2025-07-10'),
    ('5a6b7c8d-9e1f-2g3h-4i5j-6k7l8m9n0o1p', '한강 불꽃놀이', 500, 400, '2025-08-15'),
    ('5k6l7m8n-9o1p-2q3r-4s5t-6u7v8w9x0y1z', '대전 로봇 축제', 150, 50, '2025-11-20'),
    ('6b7c8d9e-1f2g-3h4i-5j6k-7l8m9n0o1p2q', '전주 한옥마을 축제', 120, 60, '2025-05-05'),
    ('6l7m8n9o-1p2q-3r4s-5t6u-7v8w9x0y1z2a', '부산 바다축제', 200, 150, '2025-08-01'),
    ('7c8d9e1f-2g3h-4i5j-6k7l-8m9n0o1p2q3r', '부산 국제 영화제', 250, 200, '2025-10-01'),
    ('7m8n9o1p-2q3r-4s5t-6u7v-8w9x0y1z2a3b', '여수 야경 축제', 180, 160, '2025-10-15'),
    ('8d9e1f2g-3h4i-5j6k-7l8m-9n0o1p2q3r4s', '서울 패션 위크', 300, 280, '2025-03-27'),
    ('8n9o1p2q-3r4s-5t6u-7v8w-9x0y1z2a3b4c', '제천 국제 음악 영화제', 250, 200, '2025-08-15'),
    ('9e1f2g3h-4i5j-6k7l-8m9n-0o1p2q3r4s5t', '제주 감귤 축제', 150, 100, '2025-11-01'),
    ('9o1p2q3r-4s5t-6u7v-8w9x-0y1z2a3b4c5d', '김해 가야 문화 축제', 120, 100, '2025-05-01')
]

try:
    with engine.connect() as connection:
        for festival in festivals:
            result = connection.execute(
                text(insert_data),
                {
                    'festival_key': festival[0],
                    'title': festival[1],
                    'total_seats': festival[2],
                    'capacity': festival[3],
                    'date': datetime.strptime(festival[4], '%Y-%m-%d'),         
                }
            )
        connection.commit()
    print("축제 데이터가 성공적으로 삽입되었습니다.")
except Exception as e:
    print(f"데이터 삽입 중 오류가 발생했습니다: {e}")

