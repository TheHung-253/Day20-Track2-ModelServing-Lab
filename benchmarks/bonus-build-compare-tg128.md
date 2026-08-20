# Bonus B1 - Prebuilt vs source build

Host `Darwin-arm64` · CPU `Apple M4 Pro`
Vector extensions detected: NEON
llama.cpp `b10488` both sides · `threads=14` ·
**both pinned to `ngl=0`** so this isolates the compiler ·
metric `tg128`, 3 repetitions

| Binary | Built for | tg128 (tok/s) | Relative |
|:--|--:|--:|--:|
| prebuilt release | runtime CPU dispatch | 31.7 | 1.00x |
| your source build | this CPU (`-DGGML_NATIVE=ON`) | 37.9 | 1.20x |

On this machine, the source build is **1.20x faster**.

before: 31.7 tok/s (prebuilt release)
after:  37.9 tok/s (source build, -DGGML_NATIVE=ON)
speedup: 1.20x

Same source revision, same model, same backend, same `-ngl` -- the only difference
is what the compiler was allowed to assume about the CPU.


### Separately: what GPU offload is worth on the same binary

`tg128` on the source build at `-ngl 99` instead of `-ngl 0`:

| Source build | tg128 (tok/s) | vs its own CPU run |
|:--|--:|--:|
| `-ngl 0` (CPU) | 37.9 | 1.00x |
| `-ngl 99` (offloaded to MTL0: Apple M4 Pro (18186 MiB, 18185 MiB free)) | 82.5 | 2.18x |

This number is **not** part of the B1 comparison above -- it is a different knob.
Reporting it separately is the point: a compiler flag and an accelerator are not
interchangeable explanations for a speedup.


## Your explanation
Bản biên dịch từ mã nguồn (source build) chạy nhanh hơn 1.20x so với bản prebuilt release. Sự gia tăng hiệu năng này có thể giải thích như sau:
- **Tập lệnh đặc thù của CPU:** Bản `prebuilt release` được biên dịch để tương thích với tất cả các CPU kiến trúc ARM64, trong khi bản `source build` được biên dịch với flag `-DGGML_NATIVE=ON`. Flag này báo cho trình biên dịch (compiler) tối ưu hoá trực tiếp cho chip Apple M4 Pro hiện tại, từ đó tận dụng triệt để các tập lệnh mở rộng phần cứng như **NEON**. M4 Pro hỗ trợ tốt tính toán song song vector, giúp quá trình decode xử lý số liệu ma trận nhanh hơn đáng kể.
- **Tính chất công việc (Memory vs Compute):** Mặc dù tác vụ decode thường bị giới hạn bởi băng thông bộ nhớ (memory bandwidth), nhưng việc tối ưu hóa mức instruction-level thông qua trình biên dịch đã giúp giảm thiểu các nút thắt ở phần CPU tính toán logic. Băng thông cực rộng trên M4 Pro cộng với việc bộ tính toán NEON được khai thác tối đa (nhờ -DGGML_NATIVE=ON) khiến tốc độ nhảy vọt từ 31.7 lên 37.9 tok/s ở `-ngl 0`.
- Riêng việc sử dụng GPU Offload (`-ngl 99`) không liên quan tới compiler của bản build CPU, mà nó khai thác trực tiếp sức mạnh phần cứng GPU (Metal) với 18GB bộ nhớ chia sẻ chung, nên tốc độ đạt ngưỡng trần của phần cứng (82.5 tok/s).
