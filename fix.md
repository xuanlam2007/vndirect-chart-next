| Ưu tiên | Hạng mục                  | Loại | Vấn đề hiện tại / Mục tiêu                                             | Cần làm                                                              |
| ------- | ------------------------- | ---- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| P0      | Volume MA 20 SMA 9        | Sửa  | `smoothingLength` hiện chưa được áp dụng đúng                          | Implement `primary MA` và `smoothed MA` đúng logic Volume Study         |
| P0      | Volume legend value       | Sửa  | Giá trị MA trên header có thể khác line đang vẽ                        | Dùng cùng dataset đã filter session cho cả line và legend               |
| P0      | Realtime volume semantics | Sửa  | Chưa chắc `tick.volume` là incremental hay cumulative                  | Kiểm tra feed và sửa aggregation volume cho đúng                        |
| P0      | Session engine            | Sửa  | Đang hard-code giờ bằng `hour <= 14:45`                                | Tạo session logic HOSE chuẩn, có nghỉ trưa, ATC, close                  |
| P0      | Future timeline           | Sửa  | Đang tạo timestamp tương lai bằng cộng đều phút                        | Chỉ tạo các mốc thời gian hợp lệ theo trading session                   |
| P0      | Wheel zoom                | Sửa  | Đang zoom bằng `setVisibleLogicalRange()` và heuristic                 | Chuyển sang logic dựa trên `barSpacing` + `rightOffset` gần TradingView |
| P0      | Volume pane               | Sửa  | Volume đang overlay chung pane bằng `scaleMargins`                     | Tách Volume thành pane riêng khoảng 20% chiều cao                       |
| P0      | Price autoscale           | Sửa  | Horizontal pan/zoom có lúc làm thay đổi vertical scale không mong muốn | Giữ autoscale ổn định và chỉ scale theo behavior TradingView            |
| P0      | Realtime candle OHLC      | Sửa  | Open/high/low/close realtime có thể lệch VNDirect                      | Reconcile current bar bằng history API định kỳ hoặc khi mở bar mới      |
| P0      | Candle color realtime     | Sửa  | Màu nến cuối có thể khác VNDirect do open bar sai                      | Dùng authoritative open của current minute                              |
| P1      | Go to realtime            | Thêm | Chưa có nút về latest bar                                              | Thêm nút xuất hiện khi user scroll xa khỏi realtime                     |
| P1      | Market status             | Thêm | Chưa biết OPEN/CLOSED/ATC/HOLIDAY                                      | Hiển thị trạng thái thị trường theo session                             |
| P1      | Candle countdown          | Thêm | Chưa có thời gian còn lại của nến hiện tại                             | Hiển thị countdown tới bar close                                        |
| P1      | Session break display     | Thêm | Chưa biểu diễn nghỉ trưa/session break                                 | Render gap/session break giống TradingView                              |
| P1      | Object Tree               | Thêm | Chưa quản lý series/indicator/drawing tập trung                        | Tạo panel hide/lock/delete/reorder                                      |
| P1      | Redo                      | Thêm | Mới có Undo                                                            | Implement Undo/Redo stack đầy đủ                                        |
| P1      | Drawing favorites         | Thêm | Chưa pin drawing tool                                                  | Cho favorite và quick access                                            |
| P1      | Drawing templates         | Thêm | Chưa save style của drawing                                            | Save/load style template cho drawing                                    |
| P1      | Indicator settings dialog | Thêm | Control indicator còn đơn giản                                         | Tạo dialog Inputs / Style / Visibility                                  |
| P1      | Compare symbol            | Thêm | Chỉ xem 1 symbol                                                       | Overlay VN30, VNINDEX hoặc symbol khác                                  |
| P2      | Indicator system          | Thêm | Mới chủ yếu có Volume MA                                               | Thêm SMA, EMA, RSI, MACD, Bollinger Bands, ATR, OBV                     |
| P2      | Indicator templates       | Thêm | Chưa có                                                                | Save/load bộ indicator                                                  |
| P2      | Symbol search             | Thêm | Symbol đang hard-code                                                  | Search symbol bằng API                                                  |
| P2      | Custom interval           | Thêm | Chỉ chọn interval cố định                                              | Cho nhập custom timeframe                                               |
| P2      | Favorite intervals        | Thêm | Chưa có                                                                | Cho star timeframe hay dùng                                             |
| P2      | Timezone selector         | Thêm | Đang cố định UTC+7                                                     | Cho chọn timezone                                                       |
| P2      | Save chart layout         | Thêm | Mới lưu drawing local                                                  | Save symbol, timeframe, indicators, drawings, scale                     |
| P2      | Auto-save layout          | Thêm | Chưa có                                                                | Tự động lưu layout theo symbol                                          |
| P2      | Bar Replay                | Thêm | Chưa có                                                                | Replay historical bars từng bước                                        |
| P2      | Alerts                    | Thêm | Chưa có                                                                | Price/indicator/drawing alerts                                          |
| P2      | Marks / events            | Thêm | Chưa có                                                                | Hiển thị marker trên timeline                                           |
| P3      | Chart style switcher      | Thêm | Chỉ candlestick                                                        | Thêm Bars, Line, Area, Heikin Ashi                                      |
| P3      | Snapshot                  | Thêm | Chưa có                                                                | Export chart thành image                                                |
| P3      | Fullscreen                | Thêm | Chưa có                                                                | Fullscreen chart                                                        |
| P3      | Multi-chart layout        | Thêm | Chỉ 1 chart                                                            | Hỗ trợ 2/4 chart synchronized                                           |
| P3      | Watchlist                 | Thêm | Chưa có                                                                | Danh sách symbol yêu thích                                              |
