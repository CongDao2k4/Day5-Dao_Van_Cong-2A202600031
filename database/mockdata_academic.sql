-- StudentOps AI — dữ liệu mẫu DB Academic (PostgreSQL)
-- Chạy sau setup_academic.sql. Idempotent: xóa dữ liệu cũ rồi nạp lại.

BEGIN;

TRUNCATE email_send_log, tuition_invoices, student_term_academics, students, academic_terms
    RESTART IDENTITY CASCADE;

-- Học kỳ (một kỳ được đánh dấu hiện tại cho UC1: học phí / GPA / đăng ký kỳ này)
INSERT INTO academic_terms (code, label_vi, academic_year, semester_index, starts_on, ends_on, is_current)
VALUES
    ('2024-1', 'Học kỳ 1 (2024–2025)', 2024, 1, DATE '2024-09-02', DATE '2025-01-12', FALSE),
    ('2024-2', 'Học kỳ 2 (2024–2025)', 2024, 2, DATE '2025-01-20', DATE '2025-05-28', FALSE),
    ('2025-1', 'Học kỳ 1 (2025–2026)', 2025, 1, DATE '2025-09-01', DATE '2026-01-15', FALSE),
    ('2025-2', 'Học kỳ 2 (2025–2026)', 2025, 2, DATE '2026-01-19', DATE '2026-05-30', TRUE);

-- Sinh viên: email sv1..sv10 @ thanhnn.dev — tên đa dạng, không dùng mẫu A/B/C
INSERT INTO students (mssv, full_name, email, cohort, major, student_status, phone)
VALUES
    ('2A202600441', 'Lê Khánh Vy',       'sv1.test@thanhnn.dev',  'K67', 'Business Administration',        'active',    '0903712846'),
    ('2A202600442', 'Phạm Quốc Huy',     'sv2.test@thanhnn.dev',  'K67', 'Computer Science & Engineering', 'active',    '0938129054'),
    ('2A202600443', 'Võ Thu Hà',         'sv3.test@thanhnn.dev',  'K66', 'Electrical Engineering',         'active',    '0976451203'),
    ('2A202600444', 'Hoàng Anh Khôi',    'sv4.test@thanhnn.dev',  'K67', 'Mechanical Engineering',         'active',    '0915084739'),
    ('2A202600445', 'Bùi Thảo My',       'sv5.test@thanhnn.dev',  'K67', 'Biomedical Engineering',         'active',    '0892346712'),
    ('2A202600446', 'Đặng Gia Phúc',     'sv6.test@thanhnn.dev',  'K67', 'Economics & Data Science',       'active',    '0961208845'),
    ('2A202600447', 'Trương Bảo Ngân',   'sv7.test@thanhnn.dev',  'K67', 'Communications & Media',         'active',    '0945673091'),
    ('2A202600448', 'Cao Minh Đức',      'sv8.test@thanhnn.dev',  'K66', 'Computer Science & Engineering', 'suspended', '0927816540'),
    ('2A202600449', 'Huỳnh Lan Chi',     'sv9.test@thanhnn.dev',  'K66', 'Psychology',                     'leave',     '0889342156'),
    ('2A202600450', 'Tăng Việt Hùng',    'sv10.test@thanhnn.dev', 'K67', 'Integrated Hospitality',         'active',    '0902156983');

-- GPA / tín chỉ theo kỳ (một số kỳ lịch sử + kỳ hiện tại 2025-2)
INSERT INTO student_term_academics (student_id, term_id, term_gpa, credits_registered, credits_earned)
SELECT s.id, t.id, v.term_gpa, v.cr_reg, v.cr_earn
FROM (VALUES
    ('2A202600441', '2024-1', 2.85, 16, 16),
    ('2A202600441', '2024-2', 2.40, 18, 18),
    ('2A202600441', '2025-1', 2.10, 17, 17),
    ('2A202600441', '2025-2', 1.65, 15, 15),
    ('2A202600442', '2024-1', 3.10, 17, 17),
    ('2A202600442', '2024-2', 3.25, 18, 18),
    ('2A202600442', '2025-1', 3.05, 16, 16),
    ('2A202600442', '2025-2', 3.20, 18, 18),
    ('2A202600443', '2024-1', 2.95, 18, 18),
    ('2A202600443', '2024-2', 2.70, 17, 17),
    ('2A202600443', '2025-1', 2.85, 18, 18),
    ('2A202600443', '2025-2', 2.80, 17, 17),
    ('2A202600444', '2024-1', 2.30, 16, 16),
    ('2A202600444', '2024-2', 2.15, 17, 17),
    ('2A202600444', '2025-1', 2.05, 18, 18),
    ('2A202600444', '2025-2', 2.10, 16, 16),
    ('2A202600445', '2024-1', 2.50, 17, 17),
    ('2A202600445', '2024-2', 2.20, 18, 18),
    ('2A202600445', '2025-1', 1.95, 16, 16),
    ('2A202600445', '2025-2', 1.85, 17, 17),
    ('2A202600446', '2024-1', 3.40, 18, 18),
    ('2A202600446', '2024-2', 3.35, 17, 17),
    ('2A202600446', '2025-1', 3.50, 18, 18),
    ('2A202600446', '2025-2', 0.00, 0,  0),
    ('2A202600447', '2024-1', 3.60, 16, 16),
    ('2A202600447', '2024-2', 3.55, 17, 17),
    ('2A202600447', '2025-1', 3.48, 18, 18),
    ('2A202600447', '2025-2', 3.50, 18, 18),
    ('2A202600448', '2024-1', 2.75, 17, 17),
    ('2A202600448', '2024-2', 2.60, 16, 16),
    ('2A202600448', '2025-1', 2.45, 17, 17),
    ('2A202600448', '2025-2', 0.00, 0,  0),
    ('2A202600449', '2024-1', 3.05, 18, 18),
    ('2A202600449', '2024-2', 2.95, 17, 17),
    ('2A202600449', '2025-1', 2.90, 16, 16),
    ('2A202600449', '2025-2', 0.00, 0,  0),
    ('2A202600450', '2024-1', 3.70, 17, 17),
    ('2A202600450', '2024-2', 3.80, 18, 18),
    ('2A202600450', '2025-1', 3.75, 17, 17),
    ('2A202600450', '2025-2', 3.85, 18, 18)
) AS v(mssv, term_code, term_gpa, cr_reg, cr_earn)
JOIN students s ON s.mssv = v.mssv
JOIN academic_terms t ON t.code = v.term_code;

-- Học phí (kỳ hiện tại + một kỳ trước để demo truy vấn theo kỳ)
INSERT INTO tuition_invoices (student_id, term_id, amount_due_vnd, amount_paid_vnd, due_date, is_fully_paid)
SELECT s.id, t.id, v.due, v.paid, v.due_dt, v.paid >= v.due
FROM (VALUES
    ('2A202600441', '2025-1', 47200000, 47200000, DATE '2025-10-15'),
    ('2A202600441', '2025-2', 48800000, 0,        DATE '2026-03-10'),
    ('2A202600442', '2025-1', 47200000, 47200000, DATE '2025-10-15'),
    ('2A202600442', '2025-2', 48800000, 48800000, DATE '2026-03-10'),
    ('2A202600443', '2025-1', 46800000, 46800000, DATE '2025-10-15'),
    ('2A202600443', '2025-2', 48400000, 48400000, DATE '2026-03-10'),
    ('2A202600444', '2025-1', 47200000, 47200000, DATE '2025-10-15'),
    ('2A202600444', '2025-2', 48800000, 12000000, DATE '2026-03-10'),
    ('2A202600445', '2025-1', 47200000, 47200000, DATE '2025-10-15'),
    ('2A202600445', '2025-2', 48800000, 48800000, DATE '2026-03-10'),
    ('2A202600446', '2025-1', 47500000, 47500000, DATE '2025-10-15'),
    ('2A202600446', '2025-2', 49100000, 0,        DATE '2026-03-10'),
    ('2A202600447', '2025-1', 47200000, 47200000, DATE '2025-10-15'),
    ('2A202600447', '2025-2', 48800000, 0,        DATE '2026-03-10'),
    ('2A202600448', '2025-1', 46800000, 46800000, DATE '2025-10-15'),
    ('2A202600448', '2025-2', 48400000, 48400000, DATE '2026-03-10'),
    ('2A202600449', '2025-1', 46500000, 20000000, DATE '2025-10-15'),
    ('2A202600449', '2025-2', 48100000, 0,        DATE '2026-03-10'),
    ('2A202600450', '2025-1', 47200000, 47200000, DATE '2025-10-15'),
    ('2A202600450', '2025-2', 48800000, 48800000, DATE '2026-03-10')
) AS v(mssv, term_code, due, paid, due_dt)
JOIN students s ON s.mssv = v.mssv
JOIN academic_terms t ON t.code = v.term_code;

UPDATE tuition_invoices ti
SET is_fully_paid = (ti.amount_paid_vnd >= ti.amount_due_vnd),
    updated_at = NOW();

-- Nhật ký gửi email mẫu (merge field / HIL / logging_tool)
INSERT INTO email_send_log (batch_id, student_mssv, recipient_email, subject, body_preview, send_status, operator_user_id, provider_message_id, error_message, created_at, sent_at)
VALUES
    (
        'a1b2c3d4-e5f6-4789-a012-3456789abcde',
        '2A202600441',
        'sv1.test@thanhnn.dev',
        '[Thông báo] Nhắc hoàn tất học phí HK2 2025–2026',
        'Kính gửi {{name}}, mã SV {{mssv}} — khoản còn lại {{amount}} VND, hạn {{due}}...',
        'sent',
        'staff.ptcs.vuong',
        'sg-msg-7f3c9a2b1e0044',
        NULL,
        TIMESTAMPTZ '2026-03-28 09:15:00+07',
        TIMESTAMPTZ '2026-03-28 09:16:02+07'
    ),
    (
        'a1b2c3d4-e5f6-4789-a012-3456789abcde',
        '2A202600444',
        'sv4.test@thanhnn.dev',
        '[Thông báo] Nhắc hoàn tất học phí HK2 2025–2026',
        'Kính gửi {{name}}, mã SV {{mssv}} — khoản còn lại {{amount}} VND...',
        'sent',
        'staff.ptcs.vuong',
        'sg-msg-8d41e7c5031145',
        NULL,
        TIMESTAMPTZ '2026-03-28 09:15:00+07',
        TIMESTAMPTZ '2026-03-28 09:16:05+07'
    ),
    (
        'b2c3d4e5-f6a7-4890-b123-456789abcdef',
        '2A202600447',
        'sv7.test@thanhnn.dev',
        'Mời tham dự workshop kỹ năng mềm (tuần 12)',
        'Chào {{name}} ({{mssv}}), Phòng CTSV mời bạn tham gia buổi workshop...',
        'failed',
        'staff.ptcs.lan',
        NULL,
        'SMTP 554: mailbox unavailable (simulated)',
        TIMESTAMPTZ '2026-04-02 14:22:00+07',
        NULL
    ),
    (
        'c3d4e5f6-a7b8-4901-c234-567890abcdef',
        '2A202600442',
        'sv2.test@thanhnn.dev',
        'Xác nhận đã nhận đủ học phí HK2 2025–2026',
        'Kính gửi {{name}}, hệ thống ghi nhận khoản {{amount}} VND...',
        'sent',
        'staff.dt.hai',
        'sg-msg-9e52f8d6142256',
        NULL,
        TIMESTAMPTZ '2026-04-05 08:40:00+07',
        TIMESTAMPTZ '2026-04-05 08:40:11+07'
    ),
    (
        'c3d4e5f6-a7b8-4901-c234-567890abcdef',
        '2A202600450',
        'sv10.test@thanhnn.dev',
        'Xác nhận đã nhận đủ học phí HK2 2025–2026',
        'Kính gửi {{name}}, hệ thống ghi nhận khoản {{amount}} VND...',
        'pending',
        'staff.dt.hai',
        NULL,
        NULL,
        TIMESTAMPTZ '2026-04-08 16:00:00+07',
        NULL
    );

COMMIT;
