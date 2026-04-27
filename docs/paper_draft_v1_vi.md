# Tái hiện QUIS: Một Khung Đánh Giá Tự Động cho Hệ thống Phân tích Dữ liệu Khám phá Dựa trên Câu hỏi

**[Bản nháp v1 — 27-04-2026]**

---

> **Tác giả:** [Tên tác giả]  
> **Đơn vị:** [Trường / Tổ chức]  
> **Liên hệ:** [email]

---

## Tóm tắt

Chúng tôi trình bày một nghiên cứu tái hiện hệ thống QUIS (Manatkar và cộng sự, 2024) — một hệ thống Phân tích Dữ liệu Khám phá (EDA) tự động hai giai đoạn, gồm mô-đun Sinh câu hỏi (QUGEN) và mô-đun Sinh insight (ISGEN). Bài báo gốc đánh giá QUIS bằng đánh giá con người theo ba tiêu chí (độ liên quan, độ dễ hiểu, tính thông tin) và điểm insight tổng hợp — cả hai đều khó tái hiện ở quy mô lớn. Đóng góp chính của chúng tôi là một **khung đánh giá tự động, không cần tập tham chiếu** gồm 12 chỉ số trải rộng bốn chiều: (1) độ chính xác và tính hợp lệ thống kê, (2) tính đa dạng và tính mới của insight, (3) chất lượng cấu trúc ý định phân tích, và (4) độ sâu khám phá không gian con. Chúng tôi giới thiệu **Tỷ lệ Tính hợp lệ Cấu trúc (SVR)** — một chỉ số mới đo lường mức độ mà kiểu cột breakdown phù hợp về mặt ngữ nghĩa với pattern insight được gán — một ràng buộc không thể kiểm tra nếu thiếu khả năng suy luận schema. Chúng tôi tái hiện QUIS trên tập dữ liệu Adidas US Sales và đánh giá ba biến thể pipeline: hệ thống QUIS đầy đủ, phiên bản ablation ONLYSTATS (tái hiện baseline gốc), và một baseline LLM-based agentic mới. Kết quả xác nhận các luận điểm cốt lõi của bài báo gốc, đồng thời chỉ ra rằng đóng góp quyết định của QUGEN nằm ở **sinh câu hỏi có điều kiện**, giúp khám phá không gian con sâu hơn (+10,9 điểm phần trăm Subspace Rate so với ONLYSTATS). Đồng thời, khung đánh giá của chúng tôi phát hiện một điểm thất bại nghiêm trọng trong các phương pháp LLM phi cấu trúc: khoảng cách 57 điểm phần trăm về SVR giữa QUIS và baseline LLM (100% so với 43%), do hành vi sai lặp đi lặp lại là dùng cột số làm chiều breakdown.

---

## 1. Giới thiệu

Phân tích Dữ liệu Khám phá Tự động (Auto EDA) là bài toán tự động phát hiện các insight có ý nghĩa thống kê và có tính hành động từ dữ liệu dạng bảng mà không cần can thiệp thủ công. Các hệ thống gần đây tận dụng Mô hình Ngôn ngữ Lớn (LLM) để dẫn dắt quá trình phân tích (Laradji và cộng sự, 2023; Ma và cộng sự, 2023; Lipman và cộng sự, 2024), nhưng đánh giá nghiêm ngặt vẫn là thách thức dai dẳng. Đánh giá của con người tốn kém, khó tái hiện và dễ bị ảnh hưởng bởi người đánh giá, trong khi các chỉ số thuần thống kê (ví dụ điểm insight tổng hợp) không nắm bắt được chất lượng ngữ nghĩa của ý định phân tích.

QUIS (Manatkar và cộng sự, 2024) đề xuất một pipeline hai giai đoạn hoàn toàn tự động, không cần huấn luyện: mô-đun sinh câu hỏi QUGEN tạo ra Insight Card qua nhiều vòng lặp từ schema và thống kê tập dữ liệu, tiếp theo là mô-đun ISGEN phát hiện các pattern có ý nghĩa thống kê và tìm kiếm các điều kiện lọc không gian con. Đánh giá gốc so sánh QUIS với ablation ONLYSTATS bằng (i) đánh giá con người về độ liên quan, độ dễ hiểu và tính thông tin, và (ii) điểm insight chuẩn hóa. Mặc dù các kết quả này chứng minh hiệu quả của QUIS, chúng vẫn để ngỏ một số câu hỏi: *QUIS hoạt động thế nào so với một agent LLM không dùng sinh câu hỏi có cấu trúc của QUGEN? Vai trò cụ thể của việc điều kiện hóa theo schema trong QUGEN là gì? Và liệu đóng góp riêng của QUGEN có thể tách biệt khỏi năng lực của ISGEN không?*

Chúng tôi giải quyết các câu hỏi này thông qua một nghiên cứu tái hiện trên tập dữ liệu Adidas US Sales. Các đóng góp của chúng tôi gồm:

1. **Một khung đánh giá tự động** với 12 chỉ số bao phủ faithfulness, tính có ý nghĩa thống kê, tính mới, tính đa dạng, tính hợp lệ cấu trúc, và độ sâu khám phá không gian con — thay thế đánh giá con người bằng các phép đo tự động không cần tham chiếu, có thể tái hiện qua các lần chạy.

2. **Tỷ lệ Tính hợp lệ Cấu trúc (SVR)** — một chỉ số mới định lượng mức độ mà một hệ thống sinh ra các cặp breakdown–pattern thỏa mãn ràng buộc kiểu ngữ nghĩa (ví dụ: pattern TREND yêu cầu breakdown thời gian). SVR phơi bày một dạng thất bại cấu trúc mà các chỉ số hiện có không phát hiện được.

3. **So sánh ba chiều** mở rộng đánh giá QUIS gốc với một baseline LLM-based agentic (agent chuyên gia 5 bước không có QUGEN), cô lập đóng góp của sinh câu hỏi có cấu trúc khỏi đóng góp của engine ISGEN.

4. **Phân tích thực nghiệm** về khi nào QUGEN có giá trị: Subspace Rate là chỉ số duy nhất QUIS vượt cả hai baseline, cung cấp bằng chứng rõ ràng nhất cho đóng góp riêng của QUGEN vào khám phá insight có điều kiện và giàu không gian con.

---

## 2. Nghiên cứu liên quan

### 2.1 Khám phá dữ liệu tự động

Các hệ thống ADE dựa trên thống kê (Sellam và cộng sự, 2015; Ding và cộng sự, 2019; Wang và cộng sự, 2020) liệt kê tất cả các view và đánh điểm theo độ thú vị. Các phương pháp này đảm bảo độ phủ nhưng thiếu định hướng ngữ nghĩa, khám phá toàn bộ không gian tổ hợp (breakdown, measure) mà không có ưu tiên. Các hệ thống tương tác (Milo và Somech, 2016, 2018; Agarwal và cộng sự, 2023) giảm gánh nặng này qua phản hồi người dùng nhưng đòi hỏi sự tham gia liên tục. Các hệ thống định hướng mục tiêu (Tang và cộng sự, 2017; Laradji và cộng sự, 2023; Lipman và cộng sự, 2024) điều hướng khám phá theo mục tiêu xác định trước, có thể bỏ sót các phát hiện quan trọng ngoài dự kiến. Các hệ thống học tăng cường (Milo và Somech, 2018a; Bar El và cộng sự, 2019, 2020; Garg và cộng sự, 2023) đạt tự động hóa cao hơn nhưng yêu cầu huấn luyện riêng cho từng tập dữ liệu. QUIS giải quyết các hạn chế này thông qua khám phá dựa trên câu hỏi, hoàn toàn tự động và không cần huấn luyện (Manatkar và cộng sự, 2024).

### 2.2 Phân tích dữ liệu dựa trên LLM

Các hệ thống dùng LLM đã đạt hiệu suất tốt trong sinh mã phân tích dữ liệu (Chen và cộng sự, 2021; Zhang và cộng sự, 2023) và trả lời câu hỏi tự nhiên trên bảng (He và cộng sự, 2024). InsightPilot (Ma và cộng sự, 2023) dùng LLM để điều hướng khám phá insight trên đồ thị các phép toán phân tích. Talk2Data (Guo và cộng sự, 2024) phân rã câu hỏi ngôn ngữ tự nhiên thành các truy vấn phân tích con. Các hệ thống này tập trung vào khám phá do người dùng dẫn dắt, trong khi QUIS tự động sinh câu hỏi phân tích. Điểm khác biệt then chốt là mô-đun QUGEN của QUIS sinh *Insight Card có cấu trúc* (câu hỏi, lý do, breakdown, measure), điều kiện hóa phân tích tiếp theo trên các trường có kiểu schema rõ ràng thay vì văn bản tự do.

### 2.3 Đánh giá hệ thống EDA

Đánh giá trong nghiên cứu ADE bao gồm đánh giá con người (Ma và cộng sự, 2023; Manatkar và cộng sự, 2024), điểm độ thú vị (Ding và cộng sự, 2019; Tang và cộng sự, 2017), và các chỉ số tự động cho phân tích dựa trên mã (He và cộng sự, 2024). Đánh giá con người là tiêu chuẩn vàng nhưng tốn kém và khó tái hiện. Đánh giá tự động chất lượng insight — đặc biệt là các ràng buộc cấu trúc và ngữ nghĩa trên ý định phân tích — vẫn chưa được nghiên cứu đầy đủ. Công trình của chúng tôi đề xuất một khung toàn diện không cần tham chiếu, giải quyết trực tiếp khoảng trống này.

---

## 3. Tổng quan hệ thống QUIS

Chúng tôi tóm tắt QUIS (Manatkar và cộng sự, 2024) để thiết lập thuật ngữ dùng xuyên suốt bài báo.

### 3.1 Định nghĩa Insight

Một insight được định nghĩa hình thức là bộ tứ $\text{Insight}(B, M, S, P)$ trong đó:
- $B$ là chiều **breakdown** (cột nhóm),
- $M$ là **measure** biểu diễn dưới dạng $\text{agg}(C)$ với hàm tổng hợp và cột số $C$,
- $S$ là **không gian con** — tập điều kiện lọc $\{(X_i, y_i)\}$ giới hạn tập dữ liệu,
- $P$ là **pattern** thuộc tập $\{\text{TREND}, \text{OUTSTANDING\_VALUE}, \text{ATTRIBUTION}, \text{DISTRIBUTION\_DIFFERENCE}\}$.

Với $(B, M, S)$ cho trước, view $\text{view}(D_S, B, M)$ được tính bằng cách lọc $D$ theo $S$ rồi nhóm theo $B$ với tổng hợp $M$.

### 3.2 QUGEN: Sinh câu hỏi

QUGEN nhận schema bảng và thống kê ngôn ngữ tự nhiên làm đầu vào, sau đó sinh Insight Card qua $n$ vòng lặp. Mỗi Insight Card gồm bốn trường: Câu hỏi (Question), Lý do (Reason), $B$ (Breakdown), $M$ (Measure). LLM được lấy mẫu ở nhiệt độ $t = 1{,}1$ với $s = 3$ mẫu mỗi vòng. Insight Card trải qua ba bộ lọc: (i) lọc liên quan schema dùng embedding câu `all-MiniLM-L6-v2`, (ii) lọc trùng lặp theo độ tương đồng cặp câu hỏi, (iii) lọc câu hỏi đơn giản loại bỏ các câu ít phức tạp. Các card từ vòng trước phục vụ làm ví dụ in-context cho vòng sau, cho phép cải thiện chất lượng qua vòng lặp mà không cần ví dụ thủ công.

### 3.3 ISGEN: Sinh Insight

ISGEN xử lý từng Insight Card qua hai giai đoạn. **Trích xuất insight cơ bản** tính $\text{view}(D, B, M)$ trên toàn bộ tập dữ liệu và đánh giá nó theo các pattern phù hợp dựa trên kiểu breakdown. **Tìm kiếm không gian con** (Thuật toán 1, Manatkar và cộng sự, 2024) thực hiện beam search để tìm điều kiện lọc $S$ tăng cường insight, được hướng dẫn bởi LLM đề xuất cột lọc có ý nghĩa ngữ nghĩa.

Hàm tính điểm pattern tuân theo bài báo gốc:
- **TREND:** $1 - p_{\text{MK}}$ (p-value Mann-Kendall); ngưỡng $T = 0{,}95$ (tức $p < 0{,}05$)
- **OUTSTANDING\_VALUE:** $v_{\max 1} / v_{\max 2}$; ngưỡng $T = 1{,}4$
- **ATTRIBUTION:** $v_{\max} / \sum v$; ngưỡng $T = 0{,}5$
- **DISTRIBUTION\_DIFFERENCE:** độ phân kỳ Jensen-Shannon; ngưỡng $T = 0{,}2$

---

## 4. Khung Đánh Giá

Đánh giá QUIS gốc dựa vào đánh giá con người và điểm tổng hợp, cả hai đều khó tái hiện một cách có hệ thống. Chúng tôi đề xuất một khung đánh giá tự động đa chiều gồm 12 chỉ số chia thành bốn nhóm.

### 4.1 Nguyên tắc thiết kế

Khung của chúng tôi được xây dựng theo bốn nguyên tắc:

**Nguyên tắc 1 — Không cần tham chiếu.** Các chỉ số không được yêu cầu chú thích chuẩn vàng. Chúng được tính trực tiếp từ đầu ra hệ thống và tập dữ liệu đầu vào.

**Nguyên tắc 2 — Đặc trưng theo chiều.** Mỗi chỉ số đo một chiều chất lượng riêng biệt. Các chỉ số không được tổng hợp thành một điểm duy nhất để bảo toàn khả năng diễn giải.

**Nguyên tắc 3 — So sánh được giữa các hệ thống.** Các chỉ số áp dụng đồng nhất cho tất cả biến thể pipeline, kể cả ablation và baseline.

**Nguyên tắc 4 — Có thể bác bỏ.** Mỗi chỉ số xuất phát từ một giả thuyết có thể kiểm chứng về điều tạo nên chất lượng trong Auto EDA (ví dụ: "insight tốt phải có ý nghĩa thống kê").

### 4.2 Nhóm I — Độ chính xác và Tính hợp lệ thống kê

**Faithfulness (Độ trung thực)** đo lường tỷ lệ giá trị view được báo cáo có thể tính lại từ tập dữ liệu nguồn:

$$\text{Faithfulness} = \frac{\text{verified\_count}}{\text{total\_count}}$$

Một view được coi là verified nếu các giá trị tính lại khớp chính xác với giá trị được báo cáo. Faithfulness đóng vai trò **điều kiện tiên quyết (sanity floor)**: bất kỳ khoảng cách nào giữa các hệ thống trên các chỉ số khác đều phản ánh chất lượng ý định phân tích, không phải lỗi tính toán.

**Tính có ý nghĩa thống kê (Statistical Significance)** đo tỷ lệ insight có ý nghĩa thống kê ở mức $\alpha = 0{,}05$:

$$\text{Significance} = \frac{1}{N}\sum_{i=1}^{N} \mathbf{1}(p_i < 0{,}05)$$

trong đó $p_i$ là thống kê kiểm định phù hợp với pattern (xem Mục 3.3). Để tránh thiên lệch từ phân phối pattern không đều giữa các hệ thống, chúng tôi báo cáo **significance trung bình theo pattern** — trung bình của các tỷ lệ significance theo từng pattern — thay vì tỷ lệ thô.

**Độ phủ pattern (Pattern Coverage)** đo tỷ lệ bốn pattern insight có ít nhất một insight hợp lệ về cấu trúc:

$$\text{PatternCoverage} = \frac{|\text{covered}|}{4}$$

trong đó "covered" yêu cầu ít nhất một insight với kiểu breakdown đúng cho pattern đó. Chỉ số này bổ sung cho Significance bằng cách đánh giá độ rộng phủ phân tích.

### 4.3 Nhóm II — Tính đa dạng và Tính mới

**Novelty (Tính mới của insight)** đo tỷ lệ insight của một hệ thống không tương đồng với insight của baseline LLM-agentic, phản ánh mức độ khám phá mới:

$$\text{Novelty} = \frac{|\{i : \max_{j} \text{cosine}(\mathbf{e}_i, \mathbf{e}_j) < \tau\}|}{N}, \quad \tau = 0{,}85$$

trong đó $\mathbf{e}_i = \text{Embed}(\text{breakdown}_i \mid \text{measure}_i \mid \text{pattern}_i \mid \text{subspace}_i)$ dùng `all-MiniLM-L6-v2`.

**Semantic Diversity (Tính đa dạng ngữ nghĩa)** đo mức độ khác biệt nội hệ thống của cấu trúc insight:

$$\text{Diversity}_{\text{sem}} = 1 - \frac{1}{\binom{N}{2}} \sum_{i < j} \text{cosine}(\mathbf{e}_i, \mathbf{e}_j)$$

### 4.4 Nhóm III — Chất lượng cấu trúc ý định

Nhóm này trực tiếp đánh giá chất lượng Insight Card do QUGEN (hoặc cơ chế đặc tả ý định tương đương) tạo ra.

**Tỷ lệ Tính hợp lệ Cấu trúc (Structural Validity Rate — SVR)** là chỉ số mới chính của chúng tôi. Nó đo tỷ lệ insight có kiểu breakdown phù hợp về mặt ngữ nghĩa với pattern được gán:

$$\text{SVR} = \frac{\text{valid\_total}}{\text{total}}$$

Quy tắc hợp lệ được suy ra từ định nghĩa insight trong Mục 3.1:
- **TREND** yêu cầu $B$ là cột thời gian (datetime)
- **ATTRIBUTION** và **DISTRIBUTION\_DIFFERENCE** yêu cầu $B$ là cột phân loại hoặc ID
- **OUTSTANDING\_VALUE** không ràng buộc kiểu breakdown

SVR vận hành hóa một ràng buộc ngữ nghĩa ẩn trong định nghĩa insight của QUIS nhưng không được các baseline LLM phi cấu trúc tuân thủ. Chúng tôi báo cáo SVR tổng thể và theo từng pattern.

**BM Actionability (Tính hành động)** đo tỷ lệ cặp (breakdown, measure) trong đó breakdown $B$ là phân loại hoặc thời gian — điều kiện cần cho so sánh nhóm có ý nghĩa:

$$\text{Actionability} = \frac{|\{(B, M) : \text{type}(B) \in \{\text{Phân loại, Thời gian, ID}\}\}|}{|\text{pairs}|}$$

**Reason–Insight Coherence (Độ nhất quán Lý do–Insight)** đo sự liên kết giữa trường lý do (đặc trưng của hệ thống có QUGEN) và insight cuối cùng:

$$\text{Coh}_{R\text{-}I} = \frac{1}{N} \sum_{i=1}^{N} \text{cosine}(\text{Embed}(\text{reason}_i), \text{Embed}(\text{insight\_string}_i))$$

trong đó $\text{insight\_string} = \text{breakdown} \mid \text{measure} \mid \text{pattern} \mid \text{condition}$.

**Question–Insight Alignment (Độ liên kết Câu hỏi–Insight)** được dùng làm chỉ số kiểm soát:

$$\text{Align}_{Q\text{-}I} = \frac{1}{N} \sum_{i=1}^{N} \text{cosine}(\text{Embed}(q_i), \text{Embed}(\text{insight\_string}_i))$$

Nếu ISGEN thực thi Insight Card trung thực như nhau ở cả QUIS và Baseline, khoảng cách về $\text{Align}_{Q\text{-}I}$ giữa hai hệ thống sẽ không đáng kể, xác nhận rằng các khác biệt quan sát được trên các chỉ số khác xuất phát từ QUGEN chứ không phải ISGEN.

### 4.5 Nhóm IV — Khám phá không gian con

**Subspace Rate (Tỷ lệ không gian con)** đo tỷ lệ insight có ít nhất một điều kiện lọc không gian con:

$$\text{SubspaceRate} = \frac{\text{insights\_with\_subspace}}{\text{total\_insights}}$$

Đây là phép đo trực tiếp nhất về khả năng khám phá không gian dữ liệu có điều kiện — một năng lực trọng tâm trong thiết kế QUIS.

**Score Uplift (Cải thiện điểm)** đo liệu tìm kiếm không gian con có cải thiện điểm insight không:

$$\Delta_{\text{uplift}} = \bar{s}_{\text{subspace}} - \bar{s}_{\text{no-subspace}}$$

$\Delta$ càng lớn (ít âm hơn) cho thấy tìm kiếm không gian con tìm được các điều kiện thực sự làm sắc nét pattern insight thay vì làm suy yếu nó.

---

## 5. Thiết lập thực nghiệm

### 5.1 Tập dữ liệu

Chúng tôi tái hiện QUIS trên **tập dữ liệu Adidas US Sales** (Chaudhari, 2022) — một trong ba tập dữ liệu dùng trong bài báo gốc. Tập dữ liệu gồm 9.648 dòng và 9 cột: `Retailer` (CHAR), `Region` (CHAR), `SalesMethod` (CHAR), `Product` (CHAR), `PricePerUnit` (INT), `UnitsSold` (INT), `TotalSales` (INT), `OperatingProfit` (INT), `OperatingMargin` (DOUBLE). Một cột thời gian (`InvoiceDate`) được tạo trong bước tiền xử lý.

Chúng tôi chọn tập dữ liệu này vì (i) nó có sẵn công khai, (ii) nó chứa đầy đủ các pattern insight có thể áp dụng (kể cả TREND thông qua cột thời gian), và (iii) schema 9 cột đại diện cho các kịch bản phân tích kinh doanh thực tế.

### 5.2 Các hệ thống so sánh

Chúng tôi đánh giá ba biến thể pipeline:

**QUIS** — pipeline QUIS đầy đủ với QUGEN + ISGEN. Tham số QUGEN tuân theo bài báo gốc: nhiệt độ $t = 1{,}1$, mẫu mỗi vòng $s = 3$, số vòng lặp $n = 10$, ví dụ in-context = 6. Tham số ISGEN: beam\_width = 20, exp\_factor = 20, max\_depth = 1. LLM: GPT-4o-mini (qua API tương thích OpenAI), thay thế Llama-3-70B-instruct dùng trong bài gốc (xem Mục 7.1 để thảo luận).

**ONLYSTATS** — tái hiện ablation gốc. QUGEN được thay bằng mô-đun thống kê: lấy mẫu ngẫu nhiên một breakdown $B$ từ các cột hợp lệ, xếp hạng tất cả measure $M$ theo độ mạnh liên kết Kruskal-Wallis, và chọn 20 cặp $(B, M)$ hàng đầu làm đầu vào cho ISGEN. Tham số ISGEN giống QUIS.

**Baseline** — baseline LLM-based agentic mới do chúng tôi giới thiệu. Nó tuân theo pipeline năm bước: (1) phân tích cột, (2) đánh giá chất lượng dữ liệu, (3) thống kê mô tả, (4) khám phá pattern, và (5) tổng hợp insight với đánh giá điểm ISGEN và tìm kiếm không gian con. Baseline dùng cùng LLM với QUIS nhưng không có sinh Insight Card có cấu trúc của QUGEN. Đầu ra được chuyển đổi sang định dạng tương thích QUIS (breakdown, measure, pattern, subspace) để đánh giá thống nhất.

### 5.3 Chi tiết đánh giá

Embedding được tính bằng `all-MiniLM-L6-v2` (Reimers và Gurevych, 2019), tải dưới dạng singleton để đảm bảo biểu diễn nhất quán qua tất cả phép tính chỉ số. Tất cả tính lại điểm insight dùng cùng hàm tính điểm với ISGEN để đảm bảo kiểm tra faithfulness được xác định tốt. Significance trung bình theo pattern dùng trung bình không trọng số trên bốn pattern để tránh thiên lệch do mất cân bằng số lượng pattern.

---

## 6. Kết quả

Bảng 1 báo cáo các chỉ số được chọn cho ba hệ thống. Kết quả đầy đủ trên tất cả 12 chỉ số được trình bày ở Phụ lục.

**Bảng 1: Các chỉ số được chọn — QUIS so với Baseline so với ONLYSTATS (Tập dữ liệu Adidas)**

| Nhóm | Chỉ số | QUIS | Baseline | ONLYSTATS |
|------|--------|------|----------|-----------|
| Độ chính xác | Faithfulness | **100,0%** | **100,0%** | **100,0%** |
| Hợp lệ | Significance thống kê | 74,7% | 60,3% | **92,0%†** |
| Phủ | Độ phủ pattern | **4/4** | 3/4 | **4/4** |
| Cấu trúc | SVR (tổng thể) | **100,0%** | 43,0% | **100,0%** |
| Cấu trúc | SVR — ATTRIBUTION | **100%** | 0% | **100%** |
| Cấu trúc | SVR — TREND | **100%** | 38% | **100%** |
| Cấu trúc | BM Actionability | **1,000** | 0,677 | **1,000** |
| Không gian con | Subspace Rate | **46,4%** ★ | 37,2% | 35,5% |
| Kiểm soát | Q–I Alignment | 0,563 | **0,576** | — |
| Lý luận | Reason–Insight Coherence | **0,571** | 0,510 | — |

† Significance của ONLYSTATS là cận trên kỳ vọng (xem Mục 6.2).  
★ QUIS là hệ thống duy nhất vượt cả hai baseline trên chỉ số này.

### 6.1 Độ chính xác: Faithfulness làm điều kiện tiên quyết

Cả ba hệ thống đều đạt faithfulness 100% trên lần lượt 97, 86 và 93 insight. Điều này xác nhận rằng tất cả pipeline đều được tính toán trên dữ liệu thực, và các khác biệt quan sát được trên các chỉ số khác phản ánh sự khác biệt thực sự về chất lượng ý định phân tích chứ không phải hallucination hay lỗi tính toán.

### 6.2 Tính hợp lệ thống kê và Độ phủ pattern

QUIS đạt significance thống kê 74,7%, vượt Baseline 14,4 điểm phần trăm. ONLYSTATS đạt 92,0%, nhưng điều này phản ánh **cận trên thống kê của liệt kê đầy đủ**: bằng cách kiểm định hệ thống tất cả cặp (B, M) được xếp hạng theo độ mạnh Kruskal-Wallis, ONLYSTATS ưu tiên chọn các cặp có liên kết cao nhất — một thiên lệch lựa chọn làm tăng significance mà không phản ánh chất lượng phân tích.

Độ phủ pattern cho thấy khoảng cách cấu trúc trong Baseline: nó chỉ phủ 3/4 pattern vì tất cả 11 insight ATTRIBUTION đều dùng cột số làm breakdown (ví dụ `TotalSales` làm breakdown), vi phạm ràng buộc ngữ nghĩa của pattern ATTRIBUTION. QUIS và ONLYSTATS đều đạt 4/4 phủ, chứng minh rằng sinh câu hỏi nhận thức schema — dù bởi QUGEN hay liệt kê có hệ thống — đảm bảo độ rộng phân tích.

### 6.3 Tỷ lệ Tính hợp lệ Cấu trúc: Khoảng cách quan trọng

SVR là chỉ số có khoảng cách lớn nhất trong đánh giá của chúng tôi: QUIS 100,0% so với Baseline 43,0% (+57 điểm phần trăm). Khoảng cách này phản ánh sự thất bại hệ thống trong sinh câu hỏi LLM phi cấu trúc của Baseline:

- **ATTRIBUTION (0% với Baseline):** Toàn bộ 11 insight ATTRIBUTION của Baseline dùng `TotalSales` hoặc `UnitsSold` làm chiều breakdown — đây là measure số chứ không phải descriptor phân loại. Điều này vi phạm ràng buộc ngữ nghĩa của pattern ATTRIBUTION rằng breakdown phải cho phép so sánh nhóm. LLM Baseline liên tục không phân biệt được "cần đo gì" và "cần so sánh theo gì".

- **TREND (38% với Baseline):** 24 trong số 39 insight TREND của Baseline dùng `Retailer` hoặc `Region` (cột phân loại) làm trục thời gian. LLM sinh câu hỏi trend đúng về ngôn ngữ tự nhiên nhưng ánh xạ chúng sang breakdown không phải thời gian trong đầu ra có cấu trúc.

Cả QUIS và ONLYSTATS đều đạt SVR = 100%. Với QUIS, điều này nhờ lý luận chuỗi suy nghĩ của QUGEN (Lý do → Câu hỏi → Breakdown, Measure) bảo toàn tính nhất quán kiểu schema. Với ONLYSTATS, điều này nhờ cơ chế kiểm tra ràng buộc kiểu breakdown nội bộ của ISGEN. Sự phân biệt này quan trọng: SVR xác định các hệ thống *nhận thức schema* (cả QUIS và ONLYSTATS) khỏi các hệ thống *không nhất quán cấu trúc* (Baseline), nhưng không phân biệt hai cơ chế đạt được nhận thức schema.

BM Actionability củng cố phát hiện này: Baseline đạt 67,7% (so với 100% của cả QUIS và ONLYSTATS), xác nhận rằng LLM Baseline liên tục sinh cặp breakdown–measure không hành động được — trong đó cột breakdown là số.

### 6.4 Subspace Rate: Đóng góp riêng của QUGEN

Subspace Rate là **chỉ số duy nhất trong khung của chúng tôi mà QUIS vượt cả hai baseline**:

| Hệ thống | Subspace Rate |
|----------|--------------|
| QUIS | **46,4%** (45/97) |
| Baseline | 37,2% (32/86) |
| ONLYSTATS | 35,5% (33/93) |

Ưu thế của QUIS so với ONLYSTATS (+10,9 điểm phần trăm) đặc biệt có ý nghĩa vì ONLYSTATS dùng cùng engine ISGEN, cùng LLM và cùng thuật toán tìm kiếm không gian con. Sự khác biệt duy nhất là nguồn gốc của Insight Card. Điều này cô lập QUGEN là nguyên nhân của tỷ lệ không gian con cao hơn.

Cơ chế là việc QUGEN sinh **câu hỏi có điều kiện**: các câu hỏi chỉ định ngữ cảnh nhóm trong nội dung câu hỏi (ví dụ: *"Trong nhóm sản phẩm Giày thể thao, xu hướng doanh số theo vùng khác nhau thế nào giữa các quý?"*). Những câu hỏi này mang tín hiệu ngữ cảnh vào tìm kiếm không gian con của ISGEN, cung cấp điểm khởi đầu có ý nghĩa ngữ nghĩa hướng dẫn beam search đến các điều kiện không gian con phong phú hơn. ONLYSTATS sinh câu hỏi dựa trên template không mang ngữ cảnh điều kiện này, nên tìm kiếm không gian con của ISGEN bắt đầu từ prior không có thông tin.

Score Uplift cung cấp bằng chứng bổ sung: QUIS đạt $\Delta = -0{,}091$ (điểm insight không gian con trung bình 0,832), so với ONLYSTATS $\Delta = -0{,}128$ (trung bình 0,785). Mức giảm nhỏ hơn trong QUIS cho thấy các không gian con được tìm bởi tìm kiếm dẫn dắt bởi câu hỏi có điều kiện nhất quán hơn với pattern insight gốc, không chỉ nhiều hơn về số lượng.

### 6.5 Chỉ số kiểm soát: Tách biệt QUGEN khỏi ISGEN

Một giải thích thay thế có thể có cho ưu thế của QUIS trên SVR và Significance là ISGEN của QUIS thực thi câu hỏi trung thực hơn ISGEN của Baseline. Question–Insight Alignment kiểm soát điều này: QUIS đạt 0,563 so với 0,576 của Baseline (Tie, khoảng cách = 0,013). Điều này xác nhận rằng ISGEN thực thi Insight Card với độ trung thực tương đương ở cả hai hệ thống, loại trừ giải thích thay thế. Các khác biệt quan sát được về SVR, Significance và Subspace Rate có thể quy cho sinh câu hỏi có cấu trúc của QUGEN.

Reason–Insight Coherence củng cố thêm: QUIS đạt 0,571 so với 0,510 của Baseline (+0,061, QUIS thắng). Trường lý do tường minh của QUGEN ("*Lý do: Vùng Đông Bắc có thể có đỉnh doanh số theo mùa do mua hàng liên quan đến thời tiết...*") gắn kết với các giả thuyết phân tích cụ thể, trái ngược với mô tả template hậu nghiệm của Baseline. Chỉ số này không áp dụng cho ONLYSTATS vì nó dùng câu hỏi template tổng hợp không có lý luận có ý nghĩa.

---

## 7. Thảo luận

### 7.1 Sự khác biệt cài đặt so với bài báo gốc

Nghiên cứu tái hiện của chúng tôi khác với bài báo QUIS gốc ở các điểm sau:

**LLM:** Chúng tôi dùng GPT-4o-mini qua OpenAI API thay vì Llama-3-70B-instruct. Mặc dù so sánh hiệu suất trực tiếp không khả thi, GPT-4o-mini là mô hình tuân theo hướng dẫn mạnh và chúng tôi không kỳ vọng kết luận phụ thuộc vào lựa chọn LLM. Một ablation có hệ thống theo các lựa chọn LLM được để lại cho công việc tương lai.

**Tham số ISGEN:** Chúng tôi dùng beam\_width = 20 và exp\_factor = 20 thay vì beam\_width = 100 và exp\_factor = 100 trong bài gốc. Điều này cần thiết do ràng buộc tính toán. Beam width nhỏ hơn có thể giảm phủ không gian con; chúng tôi lưu ý điều này là hạn chế và quan sát rằng các kết quả Subspace Rate vẫn phân biệt rõ ba hệ thống.

**Bộ lọc câu hỏi đơn giản:** Bài gốc lọc câu hỏi bằng cách thực thi SQL và loại bỏ những câu chỉ trả về một dòng. Cài đặt của chúng tôi dùng heuristic (độ dài câu hỏi + mẫu từ khóa) do không có engine thực thi SQL. Điều này có thể ảnh hưởng đến thành phần Insight Card nhưng không ảnh hưởng đến các chỉ số sau QUGEN.

**Thống kê ngôn ngữ tự nhiên:** Bài gốc sinh thống kê qua pipeline LLM-to-SQL-to-NL. Cài đặt của chúng tôi dùng thống kê mô tả theo cột (min/max/mean cho số, đếm giá trị duy nhất cho phân loại) sinh trực tiếp từ DataFrame.

### 7.2 Hạn chế của khung đánh giá

**Một tập dữ liệu.** Tất cả kết quả từ một tập dữ liệu (Adidas US Sales). Bài gốc báo cáo kết quả trên ba tập dữ liệu và cho thấy ONLYSTATS đôi khi vượt QUIS. Khung tự động của chúng tôi tránh sự nhạy cảm theo tập dữ liệu này bằng cách đo chất lượng cấu trúc (SVR, Actionability) và độ sâu khám phá (Subspace Rate) thay vì chất lượng cảm nhận — nhưng xác nhận đa tập dữ liệu vẫn cần thiết cho các luận điểm tổng quát mạnh hơn.

**Hiệu chỉnh significance theo hỗn hợp pattern.** Significance trung bình theo pattern trọng số đều mỗi pattern bất kể số lượng. Trên tập dữ liệu có phân phối pattern mất cân bằng nặng, điều này có thể đại diện quá mức cho pattern hiếm. Công việc tương lai nên khám phá các phương án có trọng số.

**Chỉ số dựa trên embedding.** Các chỉ số dùng embedding `all-MiniLM-L6-v2` (Novelty, Diversity, SVR, Coherence) chịu hạn chế của mô hình embedding nền. Cụ thể, các chuỗi có cấu trúc ngắn (ví dụ "TotalSales | MEAN(UnitsSold) | TREND") có thể không nắm bắt quan hệ ngữ nghĩa đáng tin cậy bằng câu đầy đủ.

### 7.3 Khi nào QUGEN có giá trị?

Kết quả của chúng tôi đề xuất một câu trả lời có sắc thái. QUGEN **không cần thiết** cho:
- **Faithfulness**: tất cả phương pháp đều đạt 100% do cấu trúc hệ thống
- **SVR và Actionability**: ONLYSTATS đạt điều này nhờ kiểm tra kiểu nội bộ của ISGEN
- **Độ phủ pattern**: liệt kê schema đủ để phủ tất cả pattern

QUGEN **có tính quyết định** cho:
- **Subspace Rate**: sinh câu hỏi có điều kiện riêng biệt cho phép insight giàu không gian con (+10,9 điểm phần trăm so với ONLYSTATS)
- **Significance thống kê so với LLM phi cấu trúc**: sinh theo chuỗi suy nghĩ có cấu trúc tạo ra giả thuyết hợp lệ thống kê hơn (+14,4 điểm phần trăm so với Baseline)
- **Reason–Insight Coherence**: chỉ hệ thống có QUGEN cung cấp lý luận phân tích có cơ sở

Điều này gợi ý rằng giá trị của QUGEN tỷ lệ với tầm quan trọng của *khám phá có điều kiện* trong trường hợp sử dụng mục tiêu. Với tập dữ liệu mà biến thiên theo nhóm là mối quan tâm phân tích chính (ví dụ dữ liệu doanh số với phân khúc địa lý và sản phẩm), sinh câu hỏi có điều kiện của QUGEN mang lại lợi thế rõ ràng. Với tập dữ liệu mà liệt kê (B, M) đơn giản làm cạn kiệt cấu trúc thú vị, ONLYSTATS có thể cạnh tranh tốt.

---

## 8. Kết luận

Chúng tôi đã trình bày một nghiên cứu tái hiện QUIS (Manatkar và cộng sự, 2024) trên tập dữ liệu Adidas US Sales, đóng góp một khung đánh giá tự động gồm 12 chỉ số thay thế đánh giá con người bằng các phép đo có thể mở rộng và tái hiện. Khung của chúng tôi giới thiệu Tỷ lệ Tính hợp lệ Cấu trúc (SVR) như một chỉ số mới phơi bày điểm thất bại nghiêm trọng trong EDA dựa trên LLM phi cấu trúc: dùng sai cột số làm chiều breakdown một cách hệ thống (SVR ATTRIBUTION 0% trong baseline LLM so với 100% trong QUIS).

So sánh ba chiều — QUIS so với Baseline LLM-agentic so với ablation ONLYSTATS — xác nhận các luận điểm gốc của QUIS trong khi cung cấp thêm sắc thái. Đóng góp *riêng biệt* và *quyết định* của QUGEN là **sinh câu hỏi có điều kiện**, cho phép khám phá không gian con sâu hơn mà liệt kê schema không thể tái tạo được. Khoảng cách Subspace Rate (+10,9 điểm phần trăm so với ONLYSTATS) cô lập đóng góp này một cách thực nghiệm, với kết quả score uplift xác nhận rằng các không gian con được tìm có chất lượng cao hơn, không chỉ nhiều hơn về số lượng.

Khung đánh giá của chúng tôi được phát hành kèm theo nghiên cứu tái hiện này và có thể áp dụng cho bất kỳ hệ thống nào tạo ra đầu ra tương thích QUIS (breakdown, measure, pattern, subspace). Chúng tôi hy vọng khung này thúc đẩy đánh giá nghiêm ngặt và có thể tái hiện trong cộng đồng nghiên cứu Auto EDA rộng lớn hơn.

---

## Lời cảm ơn

[Cần bổ sung.]

---

## Tài liệu tham khảo

Agarwal, S., Chan, G. Y., Garg, S., Yu, T., và Mitra, S. (2023). Fast Natural Language Based Data Exploration with Samples. Trong *SIGMOD Companion*, trang 155–158.

Bar El, O., Milo, T., và Somech, A. (2019). ATENA: An Autonomous System for Data Exploration Based on Deep Reinforcement Learning. Trong *CIKM*, trang 2873–2876.

Bar El, O., Milo, T., và Somech, A. (2020). Automatically Generating Data Exploration Sessions Using Deep Reinforcement Learning. Trong *SIGMOD*, trang 1527–1537.

Chaudhari, H. (2022). Adidas Sales Dataset (Adidas Sales in United States). Truy cập ngày 19-07-2024.

Ding, R., Han, S., Xu, Y., Zhang, H., và Zhang, D. (2019). QuickInsights: Quick and Automatic Discovery of Insights from Multi-Dimensional Data. Trong *SIGMOD*, trang 317–332.

Garg, S., Mitra, S., Yu, T., Gadhia, Y., và Kashettiwar, A. (2023). Reinforced Approximate Exploratory Data Analysis. Trong *AAAI*, tập 37, trang 7660–7669.

Guo, Y., Shi, D., Guo, M., Wu, Y., Cao, N., Lu, H., và Chen, Q. (2024). Talk2Data: A Natural Language Interface for Exploratory Visual Analysis via Question Decomposition. *ACM TIIS*, 14(2):1–24.

He, X. và cộng sự (2024). Text2Analysis: A Benchmark of Table Question Answering with Advanced Data Analysis and Unclear Queries. Trong *AAAI*, tập 38, trang 18206–18215.

Hussain, M. và Mahmud, I. (2019). pyMannKendall: a python package for non parametric Mann Kendall family of trend tests. *JOSS*, 4(39):1556.

Kruskal, W. H. và Wallis, W. A. (1952). Use of ranks in one-criterion variance analysis. *JASA*, 47(260):583–621.

Laradji, I. H. và cộng sự (2023). Capture the Flag: Uncovering Data Insights with Large Language Models. Trong *NeurIPS Workshop*.

Lin, J. (1991). Divergence measures based on the Shannon entropy. *IEEE Transactions on Information Theory*, 37:145–151.

Lipman, T., Milo, T., Somech, A., Wolfson, T., và Zafar, O. (2024). Linx: A language driven generative system for goal-oriented automated data exploration. *arXiv:2406.05107*.

Ma, P., Ding, R., Han, S., và Zhang, D. (2021). MetaInsight: Automatic Discovery of Structured Knowledge for Exploratory Data Analysis. Trong *SIGMOD*, trang 1262–1274.

Ma, P., Ding, R., Wang, S., Han, S., và Zhang, D. (2023). InsightPilot: An LLM-Empowered Automated Data Exploration System. Trong *EMNLP System Demonstrations*, trang 346–352.

Manatkar, A., Akella, A., Gupta, P., và Narayanam, K. (2024). QUIS: Question-guided Insights Generation for Automated Exploratory Data Analysis. *arXiv:2410.10270*.

Mann, H. B. (1945). Nonparametric Tests Against Trend. *Econometrica*, 13:245–259.

Milo, T. và Somech, A. (2016). REACT: Context-Sensitive Recommendations for Data Analysis. Trong *SIGMOD*, trang 2137–2140.

Milo, T. và Somech, A. (2018a). Deep Reinforcement-Learning Framework for Exploratory Data Analysis. Trong *aiDM Workshop*, trang 1–4.

Milo, T. và Somech, A. (2018b). Next-Step Suggestions for Modern Interactive Data Analysis Platforms. Trong *KDD*, trang 576–585.

Reimers, N. và Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. Trong *EMNLP*, trang 3982–3992.

Sellam, T., Müller, E., và Kersten, M. (2015). Semi-Automated Exploration of Data Warehouses. Trong *CIKM*, trang 1321–1330.

Tang, B., Han, S., Yiu, M. L., Ding, R., và Zhang, D. (2017). Extracting Top-K Insights from Multi-dimensional Data. Trong *SIGMOD*, trang 1509–1524.

Wei, J. và cộng sự (2022). Chain-of-thought prompting elicits reasoning in large language models. *NeurIPS*, 35:24824–24837.

---

## Phụ lục A — Kết quả đánh giá đầy đủ

**Bảng A1: So sánh ba chiều đầy đủ (Tập dữ liệu Adidas)**

| Nhóm | Chỉ số | QUIS | Baseline | ONLYSTATS |
|------|--------|------|----------|-----------|
| Cốt lõi | Tổng số insight | 97 | 86 | 93 |
| Cốt lõi | Faithfulness | 100,0% | 100,0% | 100,0% |
| Cốt lõi | Significance thống kê (Tổng thể) | 74,7% | 60,3% | 92,0% |
| Cốt lõi | — TREND | 50,0% (2) | 93,3% (15) | 100,0% (10) |
| Cốt lõi | — OUTSTANDING\_VALUE | 53,0% (66) | 81,2% (16) | 68,2% (66) |
| Cốt lõi | — ATTRIBUTION | 95,8% (24) | N/A | 100,0% (15) |
| Cốt lõi | — DISTRIBUTION\_DIFFERENCE | 100,0% (4) | 66,7% (9) | 100,0% (2) |
| Cốt lõi | Độ phủ pattern | 4/4 | 3/4 | 4/4 |
| Cốt lõi | Novelty insight (so với Baseline) | 61,9% | — | 33,3% |
| Cốt lõi | Đa dạng ngữ nghĩa | 0,468 | 0,451 | 0,405 |
| Cốt lõi | Entropy Đa dạng Subspace | 1,354 | 1,516 | 1,563 |
| Cốt lõi | Đa dạng Value | 1,000 | 0,375 | 0,788 |
| Không gian con | Subspace Rate | 46,4% (45/97) | 37,2% (32/86) | 35,5% (33/93) |
| Không gian con | Faithfulness Subspace | 100,0% | 100,0% | 100,0% |
| Không gian con | Significance Subspace | 55,6% | 66,7% | 60,0% |
| Không gian con | Score Uplift Δ | −0,091 | −0,112 | −0,128 |
| Không gian con | Điểm Subspace trung bình | 0,832 | 0,812 | 0,785 |
| Ý định | SVR (Tổng thể) | 100,0% (97/97) | 43,0% (37/86) | 100,0% (93/93) |
| Ý định | SVR — OUTSTANDING\_VALUE | 100% (66/66) | 100% (16/16) | 100% (66/66) |
| Ý định | SVR — TREND | 100% (3/3) | 38% (15/39) | 100% (10/10) |
| Ý định | SVR — ATTRIBUTION | 100% (24/24) | 0% (0/11) | 100% (15/15) |
| Ý định | SVR — DISTRIBUTION\_DIFFERENCE | 100% (4/4) | 30% (6/20) | 100% (2/2) |
| Ý định | BM Actionability | 1,000 | 0,677 | 1,000 |
| Ý định | BM NMI (trung bình) | 0,075 | 0,121 | 0,096 |
| Ý định | BM Interestingness | 0,085 | 0,131 | 0,105 |
| Ý định | Đa dạng câu hỏi | 0,521 | 0,596 | 0,405 |
| Ý định | Đặc hiệu câu hỏi | 9,53 ± 1,76 | 12,78 ± 5,24 | 7,57 ± 0,65 |
| Ý định | Q–I Alignment | 0,563 | 0,576 | 0,726 |
| Ý định | Reason–Insight Coherence | 0,571 | 0,510 | N/A |

---

## Phụ lục B — Phân tích lỗi SVR của Baseline LLM

Bảng sau minh họa các trường hợp không khớp breakdown–pattern điển hình trong Baseline LLM:

| Pattern | Kiểu B kỳ vọng | B thực tế (Baseline) | Hợp lệ? |
|---------|----------------|----------------------|---------|
| ATTRIBUTION | Phân loại | `TotalSales` (INT) | Không |
| ATTRIBUTION | Phân loại | `UnitsSold` (INT) | Không |
| TREND | Thời gian | `Retailer` (CHAR) | Không |
| TREND | Thời gian | `Region` (CHAR) | Không |
| TREND | Thời gian | `InvoiceDate` (Date) | Có |

LLM Baseline liên tục nhầm lẫn **breakdown** (cột nhóm) với **measure** (đại lượng cần tổng hợp). Trong các insight ATTRIBUTION, LLM sinh câu hỏi như *"Chỉ số doanh số nào đóng góp nhiều nhất vào hiệu suất tổng thể?"* — một câu hỏi phân tích hợp lệ — nhưng sau đó ánh xạ `TotalSales` sang chiều breakdown thay vì chiều measure. Sinh theo chuỗi suy nghĩ của QUGEN (Lý do → Câu hỏi → Breakdown → Measure) đảm bảo tính nhất quán định hướng: Breakdown luôn là chiều "nhóm theo", không phải đại lượng quan tâm.

---

## Phụ lục C — Ví dụ insight theo hệ thống

**QUIS — Ví dụ insight có không gian con:**

> *Câu hỏi:* Trong danh mục Giày thể thao Nữ, lợi nhuận hoạt động thay đổi thế nào theo vùng?  
> *Breakdown:* Region | *Measure:* MEAN(OperatingProfit) | *Pattern:* OUTSTANDING\_VALUE  
> *Subspace:* Product = "Women's Street Footwear"  
> *Điểm:* 0,91  
> *Diễn giải:* Vùng Đông Nam tạo ra lợi nhuận hoạt động trung bình cao hơn đáng kể so với các vùng khác cho danh mục Giày thể thao Nữ.

**ONLYSTATS — Ví dụ insight cơ bản:**

> *Câu hỏi:* Lợi nhuận hoạt động trung bình so sánh thế nào giữa các vùng?  
> *Breakdown:* Region | *Measure:* MEAN(OperatingProfit) | *Pattern:* OUTSTANDING\_VALUE  
> *Subspace:* (không có)  
> *Điểm:* 0,77  
> *Diễn giải:* Vùng Đông Nam có lợi nhuận hoạt động trung bình cao nhất, vượt trội so với các vùng khác.

**Baseline — Ví dụ insight SVR không hợp lệ:**

> *Câu hỏi:* Chỉ số doanh số nào có attribution cao nhất?  
> *Breakdown:* TotalSales (INT) | *Measure:* MEAN(OperatingProfit) | *Pattern:* ATTRIBUTION  
> *Subspace:* (không có)  
> *SVR:* Không hợp lệ (breakdown số cho pattern ATTRIBUTION)
