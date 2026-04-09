-- StudentOps AI — schema cho prototype VinUni/VinSchool
-- PostgreSQL 14+. Tài khoản ứng dụng NL-to-SQL: chỉ GRANT SELECT (read-only).
-- Chạy: psql -f setup.sql  (sau đó mockdata.sql)

BEGIN;

-- ---------------------------------------------------------------------------
-- Bảng tham chiếu: học kỳ (để join GPA, học phí, đăng ký theo kỳ)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS academic_terms (
    id              SMALLSERIAL PRIMARY KEY,
    code            VARCHAR(16) NOT NULL UNIQUE,
    label_vi        VARCHAR(64) NOT NULL,
    academic_year   SMALLINT NOT NULL,
    semester_index  SMALLINT NOT NULL CHECK (semester_index IN (1, 2, 3)),
    starts_on       DATE NOT NULL,
    ends_on         DATE NOT NULL,
    is_current      BOOLEAN NOT NULL DEFAULT FALSE
);

COMMENT ON TABLE academic_terms IS 'Danh mục học kỳ; is_current = true: học kỳ đang diễn ra (dùng cho UC1: học phí/đăng ký kỳ này).';

-- ---------------------------------------------------------------------------
-- Sinh viên
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    id              SERIAL PRIMARY KEY,
    mssv            VARCHAR(16) NOT NULL UNIQUE,
    full_name       VARCHAR(128) NOT NULL,
    email           VARCHAR(256) NOT NULL UNIQUE,
    cohort          VARCHAR(8) NOT NULL,
    major           VARCHAR(128) NOT NULL,
    student_status  VARCHAR(24) NOT NULL DEFAULT 'active'
        CHECK (student_status IN ('active', 'leave', 'graduated', 'suspended')),
    phone           VARCHAR(32),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE students IS 'Sinh viên; cohort (VD K67), major, trạng thái học tập.';
CREATE INDEX IF NOT EXISTS idx_students_cohort ON students (cohort);
CREATE INDEX IF NOT EXISTS idx_students_status ON students (student_status);

-- ---------------------------------------------------------------------------
-- Điểm & tín chỉ theo học kỳ (GPA kỳ, không thay cumulative — tính bằng view)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS student_term_academics (
    id                      SERIAL PRIMARY KEY,
    student_id              INTEGER NOT NULL REFERENCES students (id) ON DELETE CASCADE,
    term_id                 SMALLINT NOT NULL REFERENCES academic_terms (id) ON DELETE RESTRICT,
    term_gpa                NUMERIC(3, 2) NOT NULL CHECK (term_gpa >= 0 AND term_gpa <= 4),
    credits_registered      SMALLINT NOT NULL DEFAULT 0 CHECK (credits_registered >= 0 AND credits_registered <= 40),
    credits_earned          SMALLINT NOT NULL DEFAULT 0,
    UNIQUE (student_id, term_id)
);

COMMENT ON TABLE student_term_academics IS 'GPA và tín chỉ theo từng học kỳ; credits_registered = 0 nghĩa là chưa đăng ký môn kỳ đó.';

CREATE INDEX IF NOT EXISTS idx_sta_term ON student_term_academics (term_id);
CREATE INDEX IF NOT EXISTS idx_sta_gpa ON student_term_academics (term_gpa);

-- ---------------------------------------------------------------------------
-- Học phí theo học kỳ (số tiền nợ / đã đóng)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tuition_invoices (
    id                  SERIAL PRIMARY KEY,
    student_id          INTEGER NOT NULL REFERENCES students (id) ON DELETE CASCADE,
    term_id             SMALLINT NOT NULL REFERENCES academic_terms (id) ON DELETE RESTRICT,
    amount_due_vnd      BIGINT NOT NULL CHECK (amount_due_vnd >= 0),
    amount_paid_vnd     BIGINT NOT NULL DEFAULT 0 CHECK (amount_paid_vnd >= 0),
    currency            VARCHAR(3) NOT NULL DEFAULT 'VND',
    due_date            DATE NOT NULL,
    is_fully_paid       BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, term_id)
);

COMMENT ON TABLE tuition_invoices IS 'Công nợ học phí theo kỳ; amount_due_vnd - amount_paid_vnd = số còn phải đóng.';
CREATE INDEX IF NOT EXISTS idx_tuition_term ON tuition_invoices (term_id);
CREATE INDEX IF NOT EXISTS idx_tuition_unpaid ON tuition_invoices (is_fully_paid) WHERE is_fully_paid = FALSE;

-- ---------------------------------------------------------------------------
-- Nhật ký gửi email (UC2 + logging_tool) — chỉ ghi sau khi HIL confirm (demo có cả bản ghi mẫu)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS email_send_log (
    id                  BIGSERIAL PRIMARY KEY,
    batch_id            UUID NOT NULL,
    student_mssv        VARCHAR(16) NOT NULL,
    recipient_email     VARCHAR(256) NOT NULL,
    subject             VARCHAR(512) NOT NULL,
    body_preview        TEXT,
    send_status         VARCHAR(16) NOT NULL
        CHECK (send_status IN ('pending', 'sent', 'failed', 'cancelled')),
    operator_user_id    VARCHAR(64) NOT NULL,
    provider_message_id VARCHAR(256),
    error_message       TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    sent_at             TIMESTAMPTZ
);

COMMENT ON TABLE email_send_log IS 'Lịch sử gửi email: trạng thái, người thực hiện (operator_user_id), batch theo batch_id.';
CREATE INDEX IF NOT EXISTS idx_email_log_batch ON email_send_log (batch_id);
CREATE INDEX IF NOT EXISTS idx_email_log_mssv ON email_send_log (student_mssv);
CREATE INDEX IF NOT EXISTS idx_email_log_operator ON email_send_log (operator_user_id);
CREATE INDEX IF NOT EXISTS idx_email_log_created ON email_send_log (created_at DESC);

-- ---------------------------------------------------------------------------
-- View tiện cho truy vấn NL: GPA kỳ hiện tại + công nợ kỳ hiện tại
-- ---------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_student_current_term_snapshot AS
SELECT
    s.id AS student_id,
    s.mssv,
    s.full_name,
    s.email,
    s.cohort,
    s.major,
    s.student_status,
    t.code AS current_term_code,
    t.label_vi AS current_term_label,
    sta.term_gpa AS current_term_gpa,
    sta.credits_registered AS current_term_credits_registered,
    ti.amount_due_vnd,
    ti.amount_paid_vnd,
    (ti.amount_due_vnd - ti.amount_paid_vnd) AS outstanding_tuition_vnd,
    ti.is_fully_paid AS tuition_fully_paid,
    ti.due_date AS tuition_due_date
FROM students s
JOIN academic_terms t ON t.is_current = TRUE
LEFT JOIN student_term_academics sta
    ON sta.student_id = s.id AND sta.term_id = t.id
LEFT JOIN tuition_invoices ti
    ON ti.student_id = s.id AND ti.term_id = t.id;

COMMENT ON VIEW v_student_current_term_snapshot IS 'Ảnh chụp nhanh: sinh viên + học kỳ hiện tại (GPA kỳ, tín chỉ đăng ký, học phí).';

COMMIT;

-- Guardrail (tham khảo): tài khoản chỉ đọc cho sql_query_tool — bỏ comment và chạy sau khi có user DB.
-- CREATE ROLE studentops_ro LOGIN PASSWORD 'change_me';
-- GRANT CONNECT ON DATABASE your_db TO studentops_ro;
-- GRANT USAGE ON SCHEMA public TO studentops_ro;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO studentops_ro;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO studentops_ro;
