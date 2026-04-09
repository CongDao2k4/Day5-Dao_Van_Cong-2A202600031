-- Dữ liệu mẫu DB CTSV đặt phòng — MSSV trùng mockdata_academic.sql để agent ghép 2 DB
-- Chạy sau setup_ctsv_rooms.sql

BEGIN;

TRUNCATE room_bookings, study_rooms RESTART IDENTITY CASCADE;

INSERT INTO study_rooms (room_code, building, floor, capacity, room_kind, institution, is_active, note_vi)
VALUES
    ('VIN-A-201', 'Tòa A — VinUni', 2, 6, 'group_study', 'vinuni', TRUE, 'Bàn nhóm, bảng trắng'),
    ('VIN-LIB-03', 'Thư viện trung tâm', 3, 12, 'self_study', 'vinuni', TRUE, 'Yên lặng'),
    ('VIN-B-105', 'Tòa B — VinUni', 1, 20, 'meeting', 'vinuni', TRUE, 'Họp CLB / nhóm môn'),
    ('VS-STEM-LAB', 'VinSchool — khu STEM', 1, 8, 'group_study', 'vinschool', TRUE, 'Demo track VinSchool');

-- Slot cố định (2026-04-10 = demo "tuần này") — một số phòng đã kín khung giờ
INSERT INTO room_bookings (room_id, student_mssv, purpose, starts_at, ends_at, status)
SELECT r.id, v.mssv, v.purpose, v.t0::timestamptz, v.t1::timestamptz, v.st
FROM study_rooms r
JOIN (VALUES
    ('VIN-A-201', '2A202600441', 'Ôn nhóm môn Kinh tế vi mô', '2026-04-10 08:00:00+07', '2026-04-10 10:00:00+07', 'confirmed'),
    ('VIN-A-201', '2A202600442', 'Capstone brainstorm', '2026-04-10 14:00:00+07', '2026-04-10 16:30:00+07', 'confirmed'),
    ('VIN-LIB-03', '2A202600443', 'Tự học', '2026-04-10 09:00:00+07', '2026-04-10 12:00:00+07', 'confirmed'),
    ('VIN-B-105', '2A202600447', 'Họp ban truyền thông CLB', '2026-04-11 13:00:00+07', '2026-04-11 15:00:00+07', 'pending'),
    ('VS-STEM-LAB', 'VS-DEMO-001', 'Dự án STEM nhóm 3', '2026-04-12 15:00:00+07', '2026-04-12 17:00:00+07', 'confirmed')
) AS v(room_code, mssv, purpose, t0, t1, st)
  ON r.room_code = v.room_code;

COMMIT;
