-- StudentOps AI — DB Phòng CTSV: đặt phòng tự học / họp nhóm (tách khỏi DB academic)
-- Track VinUni / VinSchool: institution = vinuni | vinschool
-- Khóa nối với DB academic: room_bookings.student_mssv = students.mssv (không FK xuyên DB)
-- PostgreSQL 14+
-- Tạo DB: CREATE DATABASE studentops_ctsv;  \c studentops_ctsv
-- Chạy: psql -f setup_ctsv_rooms.sql  (sau đó mockdata_ctsv_rooms.sql)

BEGIN;

CREATE TABLE IF NOT EXISTS study_rooms (
    id              SERIAL PRIMARY KEY,
    room_code       VARCHAR(32) NOT NULL UNIQUE,
    building        VARCHAR(96) NOT NULL,
    floor           SMALLINT,
    capacity        SMALLINT NOT NULL CHECK (capacity > 0 AND capacity <= 200),
    room_kind       VARCHAR(24) NOT NULL
        CHECK (room_kind IN ('self_study', 'group_study', 'meeting')),
    institution     VARCHAR(24) NOT NULL DEFAULT 'vinuni'
        CHECK (institution IN ('vinuni', 'vinschool')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    note_vi         VARCHAR(256)
);

COMMENT ON TABLE study_rooms IS 'Phòng mở cho SV/HS đặt: tự học, nhóm, họp; institution phân VinUni vs VinSchool (demo).';

CREATE INDEX IF NOT EXISTS idx_study_rooms_institution ON study_rooms (institution);
CREATE INDEX IF NOT EXISTS idx_study_rooms_active ON study_rooms (is_active) WHERE is_active = TRUE;

CREATE TABLE IF NOT EXISTS room_bookings (
    id              BIGSERIAL PRIMARY KEY,
    room_id         INTEGER NOT NULL REFERENCES study_rooms (id) ON DELETE CASCADE,
    student_mssv    VARCHAR(16) NOT NULL,
    purpose         VARCHAR(512),
    starts_at       TIMESTAMPTZ NOT NULL,
    ends_at         TIMESTAMPTZ NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'confirmed'
        CHECK (status IN ('pending', 'confirmed', 'cancelled')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CHECK (ends_at > starts_at)
);

COMMENT ON TABLE room_bookings IS 'Lịch đặt phòng; student_mssv khớp students.mssv ở DB academic (tra cứu tên/email bên đó).';

CREATE INDEX IF NOT EXISTS idx_bookings_mssv ON room_bookings (student_mssv);
CREATE INDEX IF NOT EXISTS idx_bookings_room_time ON room_bookings (room_id, starts_at, ends_at);
CREATE INDEX IF NOT EXISTS idx_bookings_status ON room_bookings (status);

-- Gợi ý truy vấn phòng trống: phòng active không có booking confirmed/pending chồng lấn khoảng thời gian.
CREATE OR REPLACE VIEW v_room_upcoming_bookings AS
SELECT
    b.id AS booking_id,
    r.room_code,
    r.building,
    r.institution,
    r.capacity,
    r.room_kind,
    b.student_mssv,
    b.purpose,
    b.starts_at,
    b.ends_at,
    b.status
FROM room_bookings b
JOIN study_rooms r ON r.id = b.room_id
WHERE b.status IN ('pending', 'confirmed')
  AND b.ends_at > NOW()
ORDER BY b.starts_at;

COMMENT ON VIEW v_room_upcoming_bookings IS 'Các slot đặt phòng sắp tới (demo NL-to-SQL).';

COMMIT;
