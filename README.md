本倉庫用於存儲 [Colescu 撫州話網站](https://colescu.github.io/fuzhou-gan/)的數據庫與後端處理脚本。

This repository stores the locally served backend of [Colescu's Fuzhou Gan website](https://colescu.github.io/fuzhou-gan/).

# 關於數據

我使用了以下數據作爲基準：

- [qieyun-sqlite](https://github.com/nk2028/qieyun-sqlite) 的中古漢語數據庫
- [韻典網](https://ytenx.org)
- [漢字音典](https://github.com/osfans/MCPDict/tree/master)使用的數據庫：[臨川.tsv](https://github.com/osfans/MCPDict/blob/master/tools/tables/output/%E8%87%A8%E5%B7%9D.tsv) 與 [臨川上頓渡.tsv](https://github.com/osfans/MCPDict/blob/master/tools/tables/output/%E8%87%A8%E5%B7%9D%E4%B8%8A%E9%A0%93%E6%B8%A1.tsv)
- OpenCC 的簡繁轉換數據庫
- 中古漢語推導普通話與粵語來自 [Wiktionary](https://en.wiktionary.org/wiki/Module:ltc-pron/predict)

# Usage

## The `Updater` class:

- Connect to the database:

  ```python
  session = Updater(db_path="撫州話.sqlite3")
  ```

  Commit changes and close the connection:

  ```python
  del session
  ```

- Use `session.cursor` to access the cursor.
- After updating `推導撫州話.py`, run `update.bat`.
- TODO

# TODOs

- Fix rhymes that are differentiated only in 廣韻 (真臻諄, 庚清)
- Support variant characters (e.g. 窗窻)
- Implement phonological constraints in `FGSyllable`.
- Implement predictors for 白讀 and 新文讀 in Fuzhou Gan.
