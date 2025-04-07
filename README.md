Trong lĩnh vực NLP, TF‑IDF, Word2Vec và các pretrained model (BERT, PhoBERT…) là ba phương pháp biểu diễn văn bản cơ bản, nhưng chúng sẽ có những đặc điểm và ứng dụng rất khác nhau. 
<br>

1. TF‑IDF

Term Frequency–Inverse Document Frequency, well, ý tưởng của phương pháp này rất đơn giản nhưng...hiệu quả: 
Mỗi tài liệu được chuyển thành một vector mà trong đó mỗi scalar (Kiểu, giả sử vector như một array thì scalar là một thành phần của array đó ấy....) phản ánh tần suất xuất hiện của một từ trong tài liệu, được điều chỉnh bởi mức độ phổ biến của từ đó trên toàn bộ tập văn bản, hay còn gọi là độ "độc đáo" của từ trên toàn bộ tập văn bản. Ý tưởng dựa trên một suy nghĩ đơn giản là thông thường, những tập văn bản liên quan đến một chủ đề cụ thể nào đó thì trong tập văn bản đó, sẽ có một số từ ngữ được sử dụng với tần suất nhiều hơn so với những từ khác. For instances, xét một tập văn bản liên quan về Machine Learning chẳng hạn, tập văn bản này sẽ có xu hướng sử dụng nhiều từ ngữ chuyên ngành như feature space, regression, clustering,... và dựa vào tần suất xuất hiện của những từ này, ta có thể dự đoán được chủ đề, hay Label của nó. Anyways, khi sử dụng TF-IDF, kết quả ta nhận được sẽ là một sparse vector có số chiều bằng kích thước từ điển, phần lớn các phần tử trong vector này sẽ bằng 0 do các tập văn bản sẽ chỉ sử dụng một subset của toàn bộ từ điển. Vector này sẽ giúp ta có được weight của toàn bộ từ có trong văn bản đó, weight càng lớn, những từ có ý nghĩa càng cao và thường những từ này sẽ là những từ liên quan đến chuyên ngành.  

  Ví dụ một tf-idf vector: 
 + Docs = [
    "Tôi yêu học máy",

    "Học máy rất thú vị",

    "Tôi thích lập trình Python"
]

Vocabulary = ['học' 'máy' 'python' 'rất' 'thích' 'trình' 'tôi' 'thú' 'vị' 'yêu' 'lập']

TF-IDF matrix:
 + Doc1 = [0.58, 0.58, 0,    0,    0,    0,    0.58, 0,    0,    0.58, 0]
 + Doc2 = [0.41, 0.41, 0,    0.58, 0,    0,    0,    0.58, 0.58, 0,    0]
 + Doc3 = [0,    0,    0.50, 0,    0.50, 0.50, 0.50, 0,    0,    0,    0.50]

Ưu điểm của TF‑IDF là dễ triển khai, không cần huấn luyện mô hình phức tạp, lại rất hiệu quả trong các bài toán tìm kiếm thông tin hay phân loại văn bản cơ bản, nhất là khi nguồn lực tính toán hạn chế. Tuy nhiên, vì chỉ dựa vào tần suất từ mà không xét đến ngữ cảnh hay thứ tự từ, TF‑IDF không thể phân biệt được những khác biệt về ý nghĩa hay mối quan hệ ngữ pháp giữa các từ; hơn nữa, với kích thước từ điển lớn, vector biểu diễn sẽ rất thưa và chiếm nhiều bộ nhớ.  
<br>

2. Word2Vec

Tiếp theo là Word2Vec, pretrained model, model này mang đến một bước tiến lớn khi chuyển từ sparse vector sang dạng dense vector, chiều không gian ngắn hơn và có ý nghĩa hơn:
Mỗi từ sẽ được plot vào một vector space cỡ vài trăm chiều, trong đó các từ có ngữ nghĩa tương đồng thường nằm gần nhau. Mô hình này được train với một pretraining objective được kết hợp 2 phương pháp là CBOW (dự đoán từ trung tâm từ ngữ cảnh) và Skip‑gram (dự đoán ngữ cảnh từ từ trung tâm), và có khả năng nắm bắt các quan hệ tuyến tính giữa các từ, kiểu “king” - “man” + “woman” =  “queen”. Tham khảo (1). Tuy nhiên, Word2Vec vẫn chỉ cho mỗi từ một vector cố định, nên không thể phân biệt khi một từ xuất hiện trong các ngữ cảnh khác nhau. For instances, “bank” trong “river bank” và “bank account”, 2 từ bank trong 2 câu này sẽ có cùng một vector biểu diễn mặc cho ý nghĩa và ngữ cảnh của chúng là khác nhau.

* Note, các pretrained model thường có pretraining objective giống nhau. Những vector được cho ra từ Word2Vec còn được gọi là static vector, các static vector này cũng tồn tại trong BERT-base model, well thì pretrained model sẽ học để plot từ ngữ vào không gian vector... không gian này còn được gọi là vocabulary của model. Anyways, các vector này được lấy ra bằng cách extract từ layer đầu tiên transformer layer, những vector này trong BERT gọi là first layer embedding hoặc embedding layer's vector.  
<br>
<br>

3. BERT-base model 

Các BERT-based model cũng tương tự như word2vec, sẽ plot những từ vào trong một vector space nhưng số chiều sẽ lớn hơn (300 với Word2Vec, 768 với BERT-base model). Nhưng thay vì dừng lại ở bước gán static cho mỗi từ, các model này sẽ pass những static vector qua transformer layer của nó (một tập hợp gồm 12 attention layer và 12 Multi Layer Perceptron/ Feed Forward layer) để gán trọng số cho từng từ dựa theo những từ còn lại trong câu input, điều này đồng nghĩa với vector của một từ sẽ được tính toán dựa trên toàn bộ câu hoặc đoạn văn chứa nó. Nhờ vậy, cùng một từ trong các bối cảnh khác nhau sẽ có biểu diễn khác nhau, phản ánh chính xác hơn ý nghĩa ngữ cảnh, syntax và mối quan hệ dài hạn (kiểu mối liên hệ của một từ đối với những từ xung quanh nó, nhưng phạm vi xét sẽ rộng hơn, ví dụ như xét 200 từ xung quanh,...) trong câu. Đổi lại, để sử dụng và huấn luyện những mô hình này, người ta cần đầu tư đáng kể về dữ liệu, phần cứng (GPU/TPU) và thời gian tinh chỉnh, đồng thời phải đối mặt với nguy cơ overfit nếu tập dữ liệu downstream quá nhỏ.

<br>

Về mặt căn bản, ta có những phương thức này để biểu diễn vector, ít nhất e nghĩ thế. Thì những phương pháp này đều sở hữu những ưu nhược điểm riêng, và việc chỉ sử dụng một phương pháp là một lựa chọn không mấy tối ưu, trừ khi sử dụng BERT-based model + Deep learning hoặc fine tune hẳn BERT model cho classification problem thì ye, others suck. Thay vì chỉ lựa chọn một giải pháp duy nhất, e đề xuất một hướng tiếp cận kết hợp, đó là tận dụng khả năng plot vector từ vào không gian của các pretrained model để tiết kiệm bộ nhớ, cũng như dynamic hơn trong việc xử lý các nguồn dữ liệu mới, một số văn bản có thể sẽ sử dụng từ ngữ "chưa từng xuất hiện trong các tập văn bản lúc huấn luyện" for example. Tiếp theo, sử dụng TF-IDF để đánh trọng số để xác định những từ ngữ quan trọng trong câu ( ý tưởng chính của tf-idf ) và cuối cùng sẽ lấy mean của toàn bộ token embedding để tạo thành sentence embedding 

* Note: Khi đưa một câu vào model, model sẽ lần lượt lấy từng từ xuất hiện trong câu input để extract embedding vector, các vector này sau cùng sẽ được trả về theo dạng matrix (m,n) với m là số lượng từ trong câu và n là chiều không gian của vector embedding, 300 hoặc 768 tùy loại model. Việc lấy mean, ép các token embedding thành sentence embedding, của toàn bộ token được xem như tổng hợp ý nghĩa của toàn bộ câu, có thể giải thích là do những câu nói về cùng một chủ đề sẽ có xu hướng sử dụng những từ ngữ, hay cách diễn đạt giống nhau, hence trọng số từ tf-idf và các vector embedding sẽ có tương tự nhau do đó khi lấy mean, các câu về cùng chủ đề sẽ có xu hướng clustered hoặc nằm về cùng phía trong vector space. Tham khảo (2). Anyways, xét về thuật toán và các assumption của các ML model, việc này sẽ giúp cho các model tổng quát dữ liệu tốt hơn, hence better performance.


(1)  
+ https://www.youtube.com/watch?v=wjZofJX0v4M&t=747s đoạn nói về word embeddings

(2) 
+ https://datascience.stackexchange.com/questions/107462/why-does-averaging-word-embedding-vectors-exctracted-from-the-nn-embedding-laye
  
+ https://blog.ml6.eu/the-art-of-pooling-embeddings-c56575114cf8

