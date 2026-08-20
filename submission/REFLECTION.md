# Reflection — Day 20 Lab (Personal Report)

> **Đây là báo cáo cá nhân.** Số liệu của bạn **không** so sánh được với bạn cùng lớp
> — chỉ so **before vs after trên chính máy bạn**. Rubric chấm độ rõ ràng của setup,
> đo lường và **lập luận**, không chấm tốc độ tuyệt đối.
>
> `make verify` sẽ fail nếu còn placeholder chưa điền. Đó là cố ý.

**Họ Tên:** The Hung
**Cohort:** A20-K1
**Ngày submit:** 2026-08-20

---

## 1. Hardware & runtime  *(rubric 1, 2 — 10 điểm)*

> Từ `make probe`. Paste output hoặc điền tay.

- **OS:** macOS 14
- **CPU:** Apple M4 Pro
- **Cores:** 14 physical / 14 logical
- **CPU extensions:** NEON / ARM
- **RAM:** 24 GB
- **Accelerator:** Apple Metal
- **llama.cpp asset đã tải:** llama-b10488-bin-macos-arm64.tar.gz
- **Model đã dùng:** Gemma 4 E2B (`LAB_MODEL=gemma4-e2b`)
- **Quantization:** UD-Q4_K_XL + UD-Q2_K_XL

**Chạy ở đâu:** laptop của tôi
_(Nếu dùng cloud fallback: nói rõ vì sao — RAM < 8 GB, setup fail, v.v. Không mất điểm.)_

**Setup story** (≤ 80 chữ): điều gì cần thay đổi để lab chạy trên máy bạn? Có bước
nào fail rồi phải workaround không?

Mọi thứ chạy mượt mà ngay lần đầu tiên bằng lệnh `make setup` nhờ vào script cấu hình chuẩn. Apple M4 Pro đáp ứng quá đủ cấu hình nên không gặp bất cứ trục trặc nào về phần cứng hay cài đặt thư viện.

---

## 2. Đo lường  *(rubric 3, 4, 5 — 20 điểm)*

> Paste bảng từ `benchmarks/01-quickstart-results.md` (`make bench` tự sinh).

| Quantization | Size (GB) | Load (ms) | TTFT P50/P95 (ms) | TPOT P50/P95 (ms) | E2E P50/P95/P99 (ms) | Decode (tok/s) |
|---|--:|--:|--:|--:|--:|--:|
| UD-Q4_K_XL | 2.97 | - | 194 / 203 | 12.0 / 12.4 | - / - / - | 83.1 |
| UD-Q2_K_XL | 2.24 | - | 202 / 210 | 10.9 / 11.2 | - / - / - | 91.5 |

**Quan sát** (≤ 60 chữ): 2-bit nhanh hơn bao nhiêu, và **có đáng không**? Bạn đã thử
hỏi cùng một câu trên cả hai (`make serve` vs `.venv/bin/python labs/02-serve/serve.py --compare`)
chưa? Chất lượng khác nhau thế nào?

Bản 2-bit nhanh hơn 1.10x (~10%) so với bản 4-bit (91.5 vs 83.1 tok/s) và tiết kiệm 0.73 GB dung lượng đĩa. Sự đánh đổi này RẤT ĐÁNG GIÁ vì tốc độ sinh token tăng mà dung lượng giảm, chất lượng câu trả lời thực tế (khi test qua prompt) không bị suy giảm đáng kể đối với tác vụ cơ bản.

---

## 3. Serving under load  *(rubric 8, 9, 10 — 20 điểm)*

> Từ `benchmarks/02-server-results.md` (`make load-report`).

| Users | RPS | P50 (ms) | P95 (ms) | P99 (ms) | Eff. concurrency | Failures |
|--:|--:|--:|--:|--:|--:|--:|
| 10 | 2.34 | 3100 | 4700 | 5200 | 7.5 | 0.0% |
| 50 | 2.46 | 18000 | 21000 | 22000 | 40.3 | 0.0% |

- **Offered load tăng 5×, throughput thực tăng:** 1.05×
- **P95 tăng:** 4.47×
- **Effective concurrency ở 50 users:** 40.3 so với `--parallel` = 4 slots

**Peak `llamacpp:n_busy_slots_per_decode`** (từ `make metrics` khi `make load-50` đang
chạy): 3.70 / 4 slots

**Saturation reading** (≤ 80 chữ): server của bạn bão hoà ở đâu, và **bằng chứng nào**
thuyết phục bạn? Nếu P95 tăng nhanh hơn RPS thì phần latency thêm đó là queue time hay
compute time — bạn biết bằng cách nào? Nếu bạn phải nâng goodput@SLO, bạn sẽ đổi knob
nào **trước**, và vì sao knob đó?

Server bão hoà dưới mức 50 users. Bằng chứng là P95 tăng vọt 4.47x nhưng Throughput chỉ nhích nhẹ 1.05x. Phần latency tăng thêm hoàn toàn là Queue Time vì Effective Concurrency (40.3) lớn gấp 10 lần số slot giới hạn (4 slots). Để nâng Goodput, tôi sẽ tăng số `--parallel` trước vì máy dư RAM để chứa thêm KV Cache, giúp giải phóng hàng đợi.

---

## 4. Integration  *(rubric 12, 13 — 15 điểm)*

> Từ `make pipeline`. Nói thật cái nào real, cái nào stub — stub **không** mất điểm.

| Day | Piece | Real hay stub? |
|---|---|---|
| N16 Cloud/IaC | - | stub |
| N17 Data pipeline | - | stub |
| N18 Lakehouse | - | stub |
| N19 Vector + features | - | stub |
| N20 Serving | `llama-server` | real |

**Latency split** (mean của 3 query, từ output của `pipeline.py`):

- embed: 0.0 ms
- retrieve: 0.0 ms
- llm: 519.7 ms
- **stage chiếm nhiều nhất:** llm (100% của total)

**Reflection** (≤ 60 chữ): bottleneck ở đâu? Có khớp với kỳ vọng của bạn không? Nếu
phải giảm latency của pipeline này 2×, bạn sẽ tấn công vào đâu?

Bottleneck 100% nằm ở khâu LLM, hoàn toàn khớp với kỳ vọng vì các khâu khác đang bị stub (hardcode giả lập) nên tốn 0.0ms. Để giảm latency 2x, theo định luật Amdahl, tôi BẮT BUỘC phải tấn công khâu LLM (đổi model nhỏ hơn, lượng tử hoá mạnh hơn hoặc tăng băng thông bộ nhớ).

---

## 5. The single change that mattered most  *(rubric 11 — 10 điểm)*

> **Phần quan trọng nhất của report.** Không cần bonus track: `make tune` đã cho bạn
> một before/after thật (`benchmarks/01-tuning-tg128.md`). Đổi quantization,
> `LAB_N_CTX`, hay `--parallel` rồi đo lại cũng được.

**Change:** Giảm số lượng luồng (threads) từ 14 (mặc định) xuống 7

```
before:  86.9 tok/s
after:   95.0 tok/s
speedup: 1.09×
```

**Tại sao nó work** (1–2 đoạn — đây là phần grader đọc kỹ nhất):

_Giải thích như đang nói với bạn ngồi cạnh. Bám vào **cơ chế**, không phải "vibes":
memory bandwidth? vector width? cache residency? scheduling? queueing? Nếu kết quả
**khác** với kỳ vọng từ deck — nói rõ, và giải thích vì sao. Grader thưởng điểm cho
lập luận đúng về một kết quả bất ngờ, hơn là một con số đẹp không được giải thích._

Kết quả này chứng minh rằng "nhiều luồng hơn không phải lúc nào cũng nhanh hơn", đặc biệt là ở quá trình decode của LLM vốn bị giới hạn bởi Băng thông bộ nhớ (Memory Bandwidth Bottleneck) chứ không phải tốc độ tính toán (FLOPs). Chip Apple M4 Pro có băng thông bộ nhớ cực lớn, nhưng chỉ cần 7 luồng (tương đương với số P-cores vật lý) là đã đủ vắt kiệt băng thông RAM này.

Việc cố gắng nhồi thêm luồng (lên 14) khi băng thông đã chạm trần không mang lại lợi ích tính toán nào, mà ngược lại còn sinh ra chi phí đồng bộ hoá (Synchronization Overhead) giữa các luồng. Các luồng phải tranh chấp bộ nhớ đệm (Cache contention) và đợi nhau (Wait time) khiến tốc độ sụt giảm. Việc giới hạn về đúng số P-cores (7 threads) giúp tối ưu hoá việc điều phối (scheduling), loại bỏ chi phí đồng bộ thừa thãi và giúp quá trình decode chạy với tốc độ cao nhất (95.0 tok/s).

---

## 6. Bonus  *(optional — tối đa 20 điểm)*

> Bỏ trống nếu không làm. Xem `bonus/README.md`. Đừng làm hết — **một** finding sâu
> ăn điểm hơn năm bảng nông.

**Đã làm:** _<B1 build-compare / B2 sweep nào / B4 challenge nào / B5 lựa chọn nào>_

**Numbers:**

```
before:  <số>
after:   <số>
speedup: <X.Y>×
```

**Điều này nói lên gì mà deck chưa nói:**

_(để trống nếu bạn không làm phần này)_

---

## 7. Điều làm bạn ngạc nhiên nhất  *(optional)*

_(1–2 câu. Không bắt buộc, nhưng grader đọc hết.)_

_(để trống nếu bạn không làm phần này)_

---

## 8. Self-check trước khi push

- [ ] `hardware.json` committed
- [ ] `models/active.json` committed
- [ ] `benchmarks/01-quickstart-results.md` committed (`make bench`)
- [ ] `benchmarks/01-tuning-tg128.md` committed (`make tune`)
- [ ] `benchmarks/02-server-results.md` committed (`make load-report`)
- [ ] `benchmarks/02-server-batching-u50.md` hoặc `-metrics-u50.csv` committed (`make metrics`)
- [ ] `benchmarks/locust-10_stats.csv` + `locust-50_stats.csv` committed (`make load-10` / `load-50`)
- [ ] `benchmarks/03-integration-results.md` committed (`make pipeline`)
- [ ] Mọi section **"required — replace this line"** trong các file `benchmarks/*.md`
      đã được thay bằng nhận xét của bạn
- [ ] 5 screenshots trong `submission/screenshots/`
- [ ] `make verify` → **exit 0**
- [ ] Repo GitHub ở chế độ **public**
- [ ] Đã paste public URL vào VinUni LMS
- [ ] **Không** commit `models/*.gguf` hay `runtime/` (đã có trong `.gitignore`)

**Quan trọng:** repo phải **public** đến khi điểm được công bố. Private → grader không
xem được → 0 điểm.
