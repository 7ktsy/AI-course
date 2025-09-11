-- 为placed_events表添加board_date字段的SQL脚本

-- 1. 检查字段是否已存在
SELECT COUNT(*) as column_exists 
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
AND TABLE_NAME = 'placed_events' 
AND COLUMN_NAME = 'board_date';

-- 2. 添加board_date字段（如果不存在）
ALTER TABLE placed_events 
ADD COLUMN board_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- 3. 更新现有数据的board_date字段
UPDATE placed_events pe
JOIN teaching_boards tb ON pe.board_id = tb.id
SET pe.board_date = tb.board_date
WHERE pe.board_date = CURRENT_TIMESTAMP;

-- 4. 添加索引
CREATE INDEX ix_placed_event_date ON placed_events(board_date);

-- 5. 验证结果
SELECT 
    'placed_events' as table_name,
    COUNT(*) as total_records,
    COUNT(CASE WHEN board_date IS NOT NULL THEN 1 END) as records_with_date
FROM placed_events; 