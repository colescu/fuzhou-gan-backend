-- ============================================================================
-- Schema Definitions for Fuzhou Gan Database
-- ============================================================================
-- This SQL file defines the structure of the SQLite3 database used in 
-- Colescu's Fuzhou Gan website.
--
-- Author: Colescu
-- Last Updated: 17 May 2025
-- ============================================================================

-- TABLES

CREATE TABLE 聲母 (
    聲母號 INTEGER PRIMARY KEY,
    聲母 TEXT,
    清濁 TEXT,
    音 TEXT,
    組 TEXT,
    拼音 TEXT,
    音標 TEXT
);

CREATE TABLE 韻母 (
    韻母號 INTEGER PRIMARY KEY,
    韻系 TEXT,
    等 TEXT,
    呼 TEXT,
    拼音 TEXT
);

CREATE TABLE 韻目 (
    韻目號 INTEGER PRIMARY KEY,
    韻目 TEXT,
    攝 TEXT,
    韻系 TEXT,
    聲調 TEXT,
    次序 INTEGER,
    信息 TEXT
);

CREATE TABLE 小韻 (
    小韻號 INTEGER PRIMARY KEY,
    聲母號 INTEGER,
    韻母號 INTEGER,
    韻目號 INTEGER,
    重紐 TEXT,
    上字 TEXT,
    下字 TEXT,
    推導撫州話 TEXT,
    推導普通話 TEXT,
    推導廣州話 TEXT,
    FOREIGN KEY (聲母號) REFERENCES 聲母(聲母號),
    FOREIGN KEY (韻母號) REFERENCES 韻母(韻母號),
    FOREIGN KEY (韻目號) REFERENCES 韻目(韻目號)
);

CREATE TABLE 字頭 (
    字頭號 INTEGER PRIMARY KEY,
    字頭 TEXT,
    小韻號 INTEGER,
    釋義 TEXT,
    FOREIGN KEY (小韻號) REFERENCES 小韻(小韻號)
);

CREATE TABLE 撫州話 (
    字頭 TEXT,
    字頭號 INTEGER,
    聲母 TEXT,
    介音 TEXT,
    韻腹 TEXT,
    韻尾 TEXT,
    聲調 TEXT,
    文白新 TEXT,
    訓作 TEXT,
    釋義 TEXT,
    FOREIGN KEY (字頭號) REFERENCES 字頭(字頭號)
);

-- VIEWS

CREATE VIEW 韻全 AS
SELECT
    韻母號, 韻目號,
    攝, 韻系, 等, 呼, 聲調,
    韻目 || 等 || 呼 AS 音韻地位,
    CASE
        WHEN 攝 IN ('止', '遇', '果', '假') THEN ''
        WHEN 攝 IN ('蟹') THEN 'i'
        WHEN 攝 IN ('效', '流') THEN 'u'
        WHEN 攝 IN ('深', '咸') THEN (
            CASE
                WHEN 聲調 = '入' THEN 'p'
                ELSE 'm'
            END
        )
        WHEN 攝 IN ('臻', '山') THEN (
            CASE
                WHEN 聲調 = '入' THEN 't'
                ELSE 'n'
            END
        )
        WHEN 攝 IN ('通', '江', '宕', '梗', '曾') THEN (
            CASE
                WHEN 聲調 = '入' THEN 'k'
                ELSE 'ŋ'
            END
        )
    END AS 韻尾,
    CASE 聲調
        WHEN '平' THEN 拼音
        WHEN '上' THEN 拼音 || 'x'
        WHEN '去' THEN 拼音 || 'h'
        WHEN '入' THEN (
            CASE
                WHEN 攝 IN ('深', '咸')
                    THEN SUBSTR(拼音, 1, LENGTH(拼音) - 1) || 'p'
                WHEN 攝 IN ('臻', '山')
                    THEN SUBSTR(拼音, 1, LENGTH(拼音) - 1) || 't'
                WHEN 攝 IN ('通', '江', '宕', '梗', '曾')
                    THEN SUBSTR(拼音, 1, LENGTH(拼音) - 2) || 'k'
                ELSE 拼音
            END
        )
    END AS 拼音
FROM 韻母 NATURAL JOIN 韻目
ORDER BY 韻母號, 韻目號;

CREATE VIEW 小韻全 AS
SELECT
    小韻號, 小韻.聲母號, 小韻.韻母號, 小韻.韻目號,
    聲母.拼音 || 韻全.拼音 AS 拼音,
    聲母 || 攝 || 韻系 || 等 || 呼 || ifnull(重紐, '') || 聲調 AS 音韻地位,
    聲母, 清濁, 音, 組,
    攝, 韻系, 等, 呼, 重紐, 聲調,
    上字, 下字, 推導撫州話,
	推導普通話, 推導廣州話
FROM 小韻
LEFT JOIN 聲母 ON 小韻.聲母號 = 聲母.聲母號
LEFT JOIN 韻全
    ON 小韻.韻母號 = 韻全.韻母號
    AND 小韻.韻目號 = 韻全.韻目號
ORDER BY 小韻號

CREATE VIEW 字頭全 AS
SELECT 字頭號, 字頭, 小韻全.*, 釋義
FROM 字頭
LEFT JOIN 小韻全 ON 字頭.小韻號 = 小韻全.小韻號
ORDER BY 字頭號;

CREATE VIEW 撫州話與廣韻 AS
SELECT
    古.字頭號, 撫.字頭, 古.小韻號,
    古.拼音 AS 中古拼音,
	推導撫州話,
    撫.聲母 || 撫.介音 || 撫.韻腹 || 撫.韻尾 || 撫.聲調 AS 撫州話,
    古.聲母 AS 中古聲母, 撫.聲母, 清濁, 音, 組,
    攝, 韻系, 撫.韻腹, 撫.韻尾,
    等, 呼, 撫.介音,
    古.聲調 AS 中古聲調, 撫.聲調,
    文白新
FROM 字頭全 古
INNER JOIN 撫州話 撫 ON 撫.字頭號 = 古.字頭號
WHERE 訓作 IS NULL;

CREATE VIEW 撫州話同音字表 AS
SELECT
    撫.聲母 || 撫.介音 || 撫.韻腹 || 撫.韻尾 AS 撫州話,
    GROUP_CONCAT(字頭, ' ') AS 字
FROM 撫州話 撫
GROUP BY 撫州話;

CREATE VIEW 導出 AS
SELECT
    CASE
		WHEN 撫.字頭 IS NULL THEN 古.字頭
		ELSE 撫.字頭
	END AS 字頭,
    撫.聲母 || 撫.介音 || 撫.韻腹 || 撫.韻尾 || 撫.聲調 AS 撫州話,
    推導撫州話,
    文白新, 訓作, 撫.釋義,
    古.拼音 AS 中古拼音, 音韻地位,
    古.聲母, 清濁, 音, 組,
    攝, 韻系, 等, 呼, 古.聲調,
    上字 || 下字 || '切' AS 反切,
	古.釋義 廣韻釋義,
	推導普通話, 推導廣州話
FROM 撫州話 撫
FULL OUTER JOIN 字頭全 古 ON 撫.字頭號 = 古.字頭號
ORDER BY 古.字頭號