# 01 - Tune: thread-count sweep

Model `gemma-4-E2B-it-UD-Q4_K_XL.gguf` · host `Darwin-arm64` · llama.cpp `b10488`
CPU: **14 physical · 14 logical** cores · `ngl=99` · metric `tg128`

| threads (-t) | tg128 (tok/s) | vs best |
|:--|--:|--:|
| 1 | 93.4 | 98% |
| 7 | 95.0 | 100% |
| 14 | 86.9 | 91% |
| 28 | 77.5 | 82% |

**Best**: `-t 7` at 95.0 tok/s
**Slowest tested**: `-t 28` at 77.5 tok/s (1.22x spread)
**Against the physical-core default** (`-t 14`, 86.9 tok/s): 1.09x

Use this in your run:

```bash
LAB_N_THREADS=7 make bench
```

## Your explanation
Dựa trên kết quả benchmark, điểm bão hoà (knee) nằm ở **7 threads** (đạt 95.0 tok/s), trong khi đó mặc định theo số core vật lý (14 threads) lại làm giảm hiệu năng xuống còn 86.9 tok/s. Ngay cả 1 thread cũng đạt đến 93.4 tok/s (98% so với peak). Hiện tượng này xảy ra do 3 nguyên nhân chính:
1. **Nút thắt băng thông bộ nhớ (Memory Bandwidth Bottleneck):** Quá trình decode (TPOT) bị giới hạn bởi tốc độ đọc/ghi RAM chứ không phải khả năng tính toán (FLOPs). Chip Apple M4 Pro có băng thông bộ nhớ cực lớn, nhưng chỉ cần 1 đến 7 threads là đã đủ để vắt kiệt (saturate) băng thông này. Do đó, nhồi thêm thread không làm tăng thêm data truyền qua RAM.
2. **Chi phí đồng bộ hoá (Synchronization Overhead & Cache Contention):** Khi băng thông đã chạm trần, việc chia nhỏ công việc ra 14 hoặc 28 threads sẽ sinh ra chi phí điều phối (scheduling overhead) và tranh chấp bộ nhớ đệm (cache contention). Việc các luồng phải đợi nhau khiến tốc độ tụt thê thảm (28 threads tụt xuống chỉ còn 77.5 tok/s).
3. **P-cores và E-cores:** Apple M4 Pro (14 cores) là kiến trúc bất đối xứng gồm các nhân hiệu năng cao (P-cores) và nhân tiết kiệm điện (E-cores). Khi dùng 7 threads, công việc có khả năng được phân bổ toàn bộ lên các P-cores. Nếu ép chạy 14 threads, workload sẽ bị đẩy sang cả E-cores. Vì các thread phải đồng bộ với nhau, các P-cores nhanh hơn buộc phải "chờ" các E-cores chậm hơn hoàn thành, gây ra hiện tượng giảm tốc.

