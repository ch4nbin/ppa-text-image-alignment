**Do not open `ppa_pages.jsonl.gz` in your editor.** It can be hundreds of MB or more.  
The integrity script streams it line-by-line (never loads the whole file).  
Don't double-click, decompress, or open it in the IDE.

---

Put your PPA files here, then run:

  python scripts/check_text_integrity.py \
    --metadata data/ppa_metadata.csv \
    --corpus data/ppa_pages.jsonl.gz \
    --work-id YOUR_WORK_ID

Expected files:
  - ppa_metadata.csv (or refined_ppa_metadata.csv)
  - ppa_pages.jsonl or ppa_pages.jsonl.gz

---

Do NOT open ppa_pages.jsonl.gz in your editor (VSCode, Cursor, etc.).  
It is hundreds of MB or more and will crash the IDE. The script streams it  
line-by-line and never loads the full file. Use the command above only.
