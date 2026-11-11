# 08_publish: Console: xuất bản return_policy v2 → nạp lại tài liệu, xoá cache entry liên quan

113 lời gọi hàm.

```text
▶ auth.current_user   [0.8 ms]   (thread: AnyIO worker thread, dòng 35)
│    in  request = <Request>
│  ▶ auth.decode   [0.6 ms]   (thread: AnyIO worker thread, dòng 23)
│  │    in  token = 'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJxZFpSVW9sZEF4eWlsdldiRkh1N3dOVVJtVllaZEVQMmxkVEFnd084eGtNIn0.eyJleHAiOjE3OTQzNzI3MzgsImlhdCI6MTc5NDM3MTgzOCwianRpIjoiZGU1ODRiZGQtOTA3OS00NTQ1LTkwZWQtZmE1MGNjYjAyNzA3Iiwi…(+1219 ký tự)'
│  │    out = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')
│    out = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')

▶ auth.console_user   [0.0 ms]   (thread: AnyIO worker thread, dòng 42)
│    in  user = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')
│    out = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')

▶ main.admin_publish   [977.2 ms]   (thread: AnyIO worker thread, dòng 262)
│    in  doc_id = 'return_policy'
│    in  body = PublishIn({version: 2})
│    in  actor = UserContext(user_id='5b7a9394-f2ca-44a8-acb5-37953e298ad1', username='admin_ops', roles=('default-roles-semcache', 'offline_access', 'uma_authorization', 'ops_admin', 'employee'), display_name='Quản trị vận hành')
│  ▶ documents.available_versions   [20.0 ms]   (thread: AnyIO worker thread, dòng 30)
│  │  ▶ documents.docs_dir   [0.1 ms]   (thread: AnyIO worker thread, dòng 19)
│  │  │    out = <PosixPath>
│  │  ▶ documents.parse_file   [2.6 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    in  path = <PosixPath>
│  │  │    out = ({doc_id: 'complaint_handling', title: 'Kịch bản xử lý khiếu nại khách hàng', collection: 'cskh', version: 1}, '# Kịch bản xử lý khiếu nại khách hàng⏎⏎## Thời gian phản hồi⏎Mọi khiếu nại phải được phản hồi lần đầu trong vòng **24 gi…(+494 ký tự)')
│  │  ▶ documents.parse_file   [2.3 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    in  path = <PosixPath>
│  │  │    out = ({doc_id: 'dealer_discount_north', title: 'Bảng chiết khấu đại lý miền Bắc', collection: 'sales_north', version: 1}, '# Bảng chiết khấu đại lý miền Bắc⏎⏎## Mức chiết khấu theo cấp đại lý⏎| Cấp đại lý | Doanh số tháng tối thiểu | Chiết khấ…(+327 ký tự)')
│  │  ▶ documents.parse_file   [2.2 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    in  path = <PosixPath>
│  │  │    out = ({doc_id: 'dealer_discount_south', title: 'Bảng chiết khấu đại lý miền Nam', collection: 'sales_south', version: 1}, '# Bảng chiết khấu đại lý miền Nam⏎⏎## Mức chiết khấu theo cấp đại lý⏎| Cấp đại lý | Doanh số tháng tối thiểu | Chiết khấ…(+321 ký tự)')
│  │  ▶ documents.parse_file   [2.5 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    in  path = <PosixPath>
│  │  │    out = ({doc_id: 'leave_policy', title: 'Nội quy nghỉ phép', collection: 'internal_all', version: 1}, '# Nội quy nghỉ phép⏎⏎## Số ngày phép năm⏎Nhân viên chính thức được **12 ngày phép năm**. Cứ đủ 5 năm làm việc được cộng …(+363 ký tự)')
│  │  ▶ documents.parse_file   [2.3 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    in  path = <PosixPath>
│  │  │    out = ({doc_id: 'membership_faq', title: 'Câu hỏi thường gặp về hạng thành viên', collection: 'public', version: 1}, '# Câu hỏi thường gặp về hạng thành viên⏎⏎## Có những hạng thành viên nào?⏎Có 3 hạng: **Thường**, **Bạc** và **VIP**. Hạn…(+457 ký tự)')
│  │  ▶ documents.parse_file   [1.5 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    in  path = <PosixPath>
│  │  │    out = ({doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', collection: 'public', version: 1}, '# Chính sách đổi trả hàng⏎⏎## Phạm vi áp dụng⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Đ…(+892 ký tự)')
│  │  ▶ documents.parse_file   [1.2 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    in  path = <PosixPath>
│  │  │    out = ({doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', collection: 'public', version: 2}, '# Chính sách đổi trả hàng⏎⏎## Phạm vi áp dụng⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Đ…(+908 ký tự)')
│  │  ▶ documents.parse_file   [1.1 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    in  path = <PosixPath>
│  │  │    out = ({doc_id: 'salary_bonus', title: 'Quy chế lương thưởng (MẬT)', collection: 'hr_confidential', version: 1}, '# Quy chế lương thưởng (MẬT)⏎⏎## Thưởng Tết⏎Thưởng Tết năm nay bằng **1,7 tháng lương** cơ bản cho nhân viên có thời gia…(+335 ký tự)')
│  │  ▶ documents.parse_file   [1.0 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    in  path = <PosixPath>
│  │  │    out = ({doc_id: 'shipping_policy', title: 'Chính sách giao hàng và lắp đặt', collection: 'public', version: 1}, '# Chính sách giao hàng và lắp đặt⏎⏎## Thời gian giao hàng⏎- Nội thành Hà Nội và TP. Hồ Chí Minh: giao trong **2 giờ** vớ…(+572 ký tự)')
│  │  ▶ documents.parse_file   [1.0 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    in  path = <PosixPath>
│  │  │    out = ({doc_id: 'vip_return_exception', title: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', collection: 'cskh', version: 1}, '# Hướng dẫn nội bộ CSKH: Ngoại lệ đổi trả cho khách VIP⏎⏎## Thời hạn đổi trả của khách VIP⏎Khách hàng hạng VIP được đổi …(+541 ký tự)')
│  │  ▶ documents.parse_file   [1.0 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    in  path = <PosixPath>
│  │  │    out = ({doc_id: 'warranty_policy', title: 'Chính sách bảo hành và gói bảo hành mở rộng', collection: 'public', version: 1}, '# Chính sách bảo hành và gói bảo hành mở rộng⏎⏎## Bảo hành tiêu chuẩn⏎Tất cả sản phẩm điện máy được bảo hành tiêu chuẩn …(+736 ký tự)')
│  │    out = {complaint_handling: {title: 'Kịch bản xử lý khiếu nại khách hàng', collection: 'cskh', versions: [1]}, dealer_discount_north: {title: 'Bảng chiết khấu đại lý miền Bắc', collection: 'sales_north', versions: [1]}, dealer_discount_south: {title: 'Bảng chiết khấu đại lý miền Nam', collection: 'sales_south', versions: [1]}, leave_policy: {title: 'Nội quy nghỉ phép', collection: 'internal_all', versions: [1]}, membership_faq: {title: 'Câu hỏi thường gặp về hạng thành viên', collection: 'public', versions: [1]}, return_policy: {title: 'Chính sách đổi trả hàng', collection: 'public', versions: [1, 2]}, salary_bonus: {title: 'Quy chế lương thưởng (MẬT)', collection: 'hr_confidential', versions: [1]}, shipping_policy: {title: 'Chính sách giao hàng và lắp đặt', collection: 'public', versions: [1]}, vip_return_exception: {title: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', collection: 'cskh', versions: [1]}, warranty_policy: {title: 'Chính sách bảo hành và gói bảo hành mở rộng', collection: 'public', versions: [1]}}
│  ▶ sync.publish_document_version   [957.1 ms]   (thread: AnyIO worker thread, dòng 94)
│  │    in  doc_id = 'return_policy'
│  │    in  version = 2
│  │    in  actor = 'admin_ops'
│  │  ▶ sync._now   [0.0 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    out = <datetime>
│  │  ▶ documents.current_version   [1.8 ms]   (thread: AnyIO worker thread, dòng 52)
│  │  │    in  doc_id = 'return_policy'
│  │  │    out = 1
│  │  ▶ documents.ingest   [903.9 ms]   (thread: AnyIO worker thread, dòng 70)
│  │  │    in  doc_id = 'return_policy'
│  │  │    in  version = 2
│  │  │  ▶ documents.file_for   [0.1 ms]   (thread: AnyIO worker thread, dòng 40)
│  │  │  │    in  doc_id = 'return_policy'
│  │  │  │    in  version = 2
│  │  │  │  ▶ documents.docs_dir   [0.0 ms]   (thread: AnyIO worker thread, dòng 19)
│  │  │  │  │    out = <PosixPath>
│  │  │  │    out = <PosixPath>
│  │  │  ▶ documents.parse_file   [1.9 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  path = <PosixPath>
│  │  │  │    out = ({doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', collection: 'public', version: 2}, '# Chính sách đổi trả hàng⏎⏎## Phạm vi áp dụng⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Đ…(+908 ký tự)')
│  │  │  ▶ chunking.chunk_document   [490.3 ms]   (thread: AnyIO worker thread, dòng 107)
│  │  │  │    in  doc_id = 'return_policy'
│  │  │  │    in  version = 2
│  │  │  │    in  collection = 'public'
│  │  │  │    in  title = 'Chính sách đổi trả hàng'
│  │  │  │    in  md = '# Chính sách đổi trả hàng⏎⏎## Phạm vi áp dụng⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎## Thời hạn đổi trả⏎Từ ngày…(+808 ký tự)'
│  │  │  │    in  max_tokens = 400
│  │  │  │    in  min_tokens = 80
│  │  │  │    in  overlap = 50
│  │  │  │  ▶ chunking._sections   [0.1 ms]   (thread: AnyIO worker thread, dòng 54)
│  │  │  │  │    in  md = '# Chính sách đổi trả hàng⏎⏎## Phạm vi áp dụng⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎## Thời hạn đổi trả⏎Từ ngày…(+808 ký tự)'
│  │  │  │  │    in  title = 'Chính sách đổi trả hàng'
│  │  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │  │    out = ''
│  │  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │  │    out = ''
│  │  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │  │    out = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.'
│  │  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │  │    out = 'Từ ngày 01/12, khách hàng được đổi trả sản phẩm trong vòng **15 ngày** kể từ ngày nhận hàng. Sau thời hạn này, sản phẩm chỉ được hỗ trợ theo chính sách bảo hành.'
│  │  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │  │    out = '- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.'
│  │  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │  │    out = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.'
│  │  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │  │    out = 'Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh toán ban đầu. Đơn thanh toán tiền mặt được hoàn bằng chuyển khoản.'
│  │  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │  │    out = 'Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi xả kho có ghi chú "không đổi trả".'
│  │  │  │  │    out = [_Section(path=['Chính sách đổi trả hàng', 'Phạm vi áp dụng'], lines=['Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh m…(+25 ký tự)', '']), _Section(path=['Chính sách đổi trả hàng', 'Thời hạn đổi trả'], lines=['Từ ngày 01/12, khách hàng được đổi trả sản phẩm trong vòng **15 ngày** kể từ ngày nhận hàng. Sau thời hạn này, sản phẩm …(+41 ký tự)', '']), _Section(path=['Chính sách đổi trả hàng', 'Điều kiện đổi trả'], lines=['- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.', '- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.', '- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.', '']), _Section(path=['Chính sách đổi trả hàng', 'Hàng điện tử và điện thoại'], lines=['Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâ…(+20 ký tự)', '']), _Section(path=['Chính sách đổi trả hàng', 'Hoàn tiền'], lines=['Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh toán ban đầu. Đơn thanh toán tiền mặt được hoàn bằng chuyển…(+7 ký tự)', '']), _Section(path=['Chính sách đổi trả hàng', 'Sản phẩm không áp dụng đổi trả'], lines=['Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi xả kho có ghi chú "không đổi trả".'])]
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.'
│  │  │  │  ▶ chunking.ntokens   [489.2 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.'
│  │  │  │  │    out = 60
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.'
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Từ ngày 01/12, khách hàng được đổi trả sản phẩm trong vòng **15 ngày** kể từ ngày nhận hàng. Sau thời hạn này, sản phẩm chỉ được hỗ trợ theo chính sách bảo hành.'
│  │  │  │  ▶ chunking.ntokens   [0.1 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.Từ ngày 01/12, khách hàng được đổi trả sản phẩm trong vòng **15 ngày** kể t…(+86 ký tự)'
│  │  │  │  │    out = 124
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎⏎**Thời hạn đổi trả**⏎Từ ngày 01/12, khách hàng được đổi trả sản phẩm tro…(+110 ký tự)'
│  │  │  │  ▶ chunking.ntokens   [0.1 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎⏎**Thời hạn đổi trả**⏎Từ ngày 01/12, khách hàng được đổi trả sản phẩm tro…(+110 ký tự)'
│  │  │  │  │    out = 136
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = '- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.'
│  │  │  │  ▶ chunking.ntokens   [0.1 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = '- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.'
│  │  │  │  │    out = 91
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.'
│  │  │  │  ▶ chunking.ntokens   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.'
│  │  │  │  │    out = 61
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.'
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh toán ban đầu. Đơn thanh toán tiền mặt được hoàn bằng chuyển khoản.'
│  │  │  │  ▶ chunking.ntokens   [0.1 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh toán ban đầu. Đơn t…(+47 ký tự)'
│  │  │  │  │    out = 115
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.⏎⏎⏎**Hoàn tiền**⏎Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh to…(+64 ký tự)'
│  │  │  │  ▶ chunking.ntokens   [0.1 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.⏎⏎⏎**Hoàn tiền**⏎Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh to…(+64 ký tự)'
│  │  │  │  │    out = 121
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎⏎**Thời hạn đổi trả**⏎Từ ngày 01/12, khách hàng được đổi trả sản phẩm tro…(+110 ký tự)'
│  │  │  │  ▶ chunking.ntokens   [0.1 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎⏎**Thời hạn đổi trả**⏎Từ ngày 01/12, khách hàng được đổi trả sản phẩm tro…(+110 ký tự)'
│  │  │  │  │    out = 136
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh mục không áp dụng đổi trả.⏎⏎⏎**Thời hạn đổi trả**⏎Từ ngày 01/12, khách hàng được đổi trả sản phẩm tro…(+110 ký tự)'
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = '- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.'
│  │  │  │  ▶ chunking.ntokens   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = '- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.'
│  │  │  │  │    out = 91
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = '- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎- Sản phẩm không có dấu hiệu va đập, vào nước hoặc tự ý sửa chữa.'
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.⏎⏎⏎**Hoàn tiền**⏎Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh to…(+64 ký tự)'
│  │  │  │  ▶ chunking.ntokens   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.⏎⏎⏎**Hoàn tiền**⏎Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh to…(+64 ký tự)'
│  │  │  │  │    out = 121
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâm bảo hành xác nhận.⏎⏎⏎**Hoàn tiền**⏎Tiền được hoàn trong 3–5 ngày làm việc qua phương thức thanh to…(+64 ký tự)'
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi xả kho có ghi chú "không đổi trả".'
│  │  │  │  ▶ chunking.ntokens   [0.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │  │  │    in  text = 'Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi xả kho có ghi chú "không đổi trả".'
│  │  │  │  │    out = 48
│  │  │  │  ▶ chunking._Section.body   [0.0 ms]   (thread: AnyIO worker thread, dòng 49)
│  │  │  │  │    out = 'Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi xả kho có ghi chú "không đổi trả".'
│  │  │  │    out = [Chunk(chunk_id='0a1ca18b30d10659', doc_id='return_policy', version=2, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng', text='Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điện Máy Sao Mai, trừ các sản phẩm thuộc danh m…(+210 ký tự)', embed_text='[Chính sách đổi trả hàng > Phạm vi áp dụng]⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điệ…(+254 ký tự)', index=0), Chunk(chunk_id='772a89c5b6f4c616', doc_id='return_policy', version=2, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Điều kiện đổi trả', text='- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá đơn mua hàng hoặc mã đơn hàng trên hệ thống.⏎-…(+64 ký tự)', embed_text='[Chính sách đổi trả hàng > Điều kiện đổi trả]⏎- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá …(+110 ký tự)', index=1), Chunk(chunk_id='d61fcdd6987e3134', doc_id='return_policy', version=2, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Hàng điện tử và điện thoại', text='Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử chỉ được đổi khi có lỗi do nhà sản xuất, được trung tâ…(+164 ký tự)', embed_text='[Chính sách đổi trả hàng > Hàng điện tử và điện thoại]⏎Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử…(+219 ký tự)', index=2), Chunk(chunk_id='619b0692d2b149ce', doc_id='return_policy', version=2, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Sản phẩm không áp dụng đổi trả', text='Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi xả kho có ghi chú "không đổi trả".', embed_text='[Chính sách đổi trả hàng > Sản phẩm không áp dụng đổi trả]⏎Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi…(+35 ký tự)', index=3)]
│  │  │  ▶ embeddings.embed   [366.3 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │  │    in  texts = ['[Chính sách đổi trả hàng > Phạm vi áp dụng]⏎Chính sách áp dụng cho mọi đơn hàng mua tại cửa hàng và trên website của Điệ…(+254 ký tự)', '[Chính sách đổi trả hàng > Điều kiện đổi trả]⏎- Sản phẩm còn nguyên tem, hộp và đầy đủ phụ kiện, quà tặng kèm.⏎- Có hoá …(+110 ký tự)', '[Chính sách đổi trả hàng > Hàng điện tử và điện thoại]⏎Điện thoại, máy tính bảng và laptop đã kích hoạt bảo hành điện tử…(+219 ký tự)', '[Chính sách đổi trả hàng > Sản phẩm không áp dụng đổi trả]⏎Thẻ cào, phần mềm bản quyền đã kích hoạt, sản phẩm khuyến mãi…(+35 ký tự)']
│  │  │  │    out = ([<vector 1536 số: [0.0091, 0.0230, -0.0536, …]>, <vector 1536 số: [0.0212, 0.0231, -0.0797, …]>, <vector 1536 số: [-0.0054, 0.0251, -0.0288, …]>, <vector 1536 số: [-0.0192, 0.0438, -0.0110, …]>], 487, False)
│  │  │  ▶ documents.ensure_collection   [9.4 ms]   (thread: AnyIO worker thread, dòng 44)
│  │  │  │    out = None
│  │  │  ▶ db.execute   [4.6 ms]   (thread: AnyIO worker thread, dòng 109)
│  │  │  │    in  sql = 'INSERT INTO documents(doc_id,title,collection,version,updated_at) VALUES (%s,%s,%s,%s,now())⏎                  ON CONFLICT (doc_id) DO UPDATE SET title=EXCLUDED.title, collection=EXCLUDED.collection,⏎                  ve…(+40 ký tự)'
│  │  │  │    in  params = ('return_policy', 'Chính sách đổi trả hàng', 'public', 2)
│  │  │  │    out = None
│  │  │    out = 4
│  │  ▶ cache.invalidate_doc   [47.2 ms]   (thread: AnyIO worker thread, dòng 209)
│  │  │    in  doc_id = 'return_policy'
│  │  │  ▶ cache.delete   [8.7 ms]   (thread: AnyIO worker thread, dòng 196)
│  │  │  │    in  entry_id = '89b29268-88ac-4d02-aa9f-213ed5d83917'
│  │  │  │  ▶ cache.get_entry   [0.9 ms]   (thread: AnyIO worker thread, dòng 104)
│  │  │  │  │    in  entry_id = '89b29268-88ac-4d02-aa9f-213ed5d83917'
│  │  │  │  │  ▶ cache.CacheEntry.from_json   [0.1 ms]   (thread: AnyIO worker thread, dòng 68)
│  │  │  │  │  │    in  s = '{"entry_id": "89b29268-88ac-4d02-aa9f-213ed5d83917", "partition": "3963a48f4b463545", "question": "Khách VIP được đổi trả trong bao lâu?", "answer": "Khách hàng được đổi trả sản phẩm trong vòng 7 ngày kể từ ngày nhận hàn…(+1593 ký tự)'
│  │  │  │  │  │    out = CacheEntry(entry_id='89b29268-88ac-4d02-aa9f-213ed5d83917', partition='3963a48f4b463545', question='Khách VIP được đổi trả trong bao lâu?', answer='Khách hàng được đổi trả sản phẩm trong vòng 7 ngày kể từ ngày nhận hàng [c2].', citations=[{label: 'c2', doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', section: 'Chính sách đổi trả hàng > Phạm vi áp dụng', collection: 'public', version: 1}], provenance=[Provenance(chunk_id='7f3df74338ef5336', doc_id='membership_faq', version=1, collection='public', title='Câu hỏi thường gặp về hạng thành viên', section_path='Câu hỏi thường gặp về hạng thành viên > Quyền lợi chung'), Provenance(chunk_id='232c157bca68b49d', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng'), Provenance(chunk_id='2bca42c3afd3fc40', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Hàng điện tử và điện thoại'), Provenance(chunk_id='0d3884b099feeb56', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Sản phẩm không áp dụng đổi trả'), Provenance(chunk_id='5f795b0c2ed5e7a5', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Điều kiện đổi trả')], intent='return_policy', entities={tier: 'vip'}, policy='NORMAL', prompt_version='v1-8cc4d02d', model='gemini-3.5-flash-lite', created_at=1.794e+09, ttl=604800, gen_tokens_in=605, gen_tokens_out=22, gen_cost_usd=0.0001, gen_latency_ms=1958.8714, hits=0, last_hit=None)
│  │  │  │  │    out = CacheEntry(entry_id='89b29268-88ac-4d02-aa9f-213ed5d83917', partition='3963a48f4b463545', question='Khách VIP được đổi trả trong bao lâu?', answer='Khách hàng được đổi trả sản phẩm trong vòng 7 ngày kể từ ngày nhận hàng [c2].', citations=[{label: 'c2', doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', section: 'Chính sách đổi trả hàng > Phạm vi áp dụng', collection: 'public', version: 1}], provenance=[Provenance(chunk_id='7f3df74338ef5336', doc_id='membership_faq', version=1, collection='public', title='Câu hỏi thường gặp về hạng thành viên', section_path='Câu hỏi thường gặp về hạng thành viên > Quyền lợi chung'), Provenance(chunk_id='232c157bca68b49d', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng'), Provenance(chunk_id='2bca42c3afd3fc40', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Hàng điện tử và điện thoại'), Provenance(chunk_id='0d3884b099feeb56', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Sản phẩm không áp dụng đổi trả'), Provenance(chunk_id='5f795b0c2ed5e7a5', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Điều kiện đổi trả')], intent='return_policy', entities={tier: 'vip'}, policy='NORMAL', prompt_version='v1-8cc4d02d', model='gemini-3.5-flash-lite', created_at=1.794e+09, ttl=604800, gen_tokens_in=605, gen_tokens_out=22, gen_cost_usd=0.0001, gen_latency_ms=1958.8714, hits=0, last_hit=None)
│  │  │  │  ▶ cache._delete_vector   [6.8 ms]   (thread: AnyIO worker thread, dòng 192)
│  │  │  │  │    in  entry_id = '89b29268-88ac-4d02-aa9f-213ed5d83917'
│  │  │  │  │    out = None
│  │  │  │    out = None
│  │  │  ▶ cache.delete   [7.4 ms]   (thread: AnyIO worker thread, dòng 196)
│  │  │  │    in  entry_id = '13c22a20-a6b2-4a03-9448-46772e13273d'
│  │  │  │  ▶ cache.get_entry   [0.8 ms]   (thread: AnyIO worker thread, dòng 104)
│  │  │  │  │    in  entry_id = '13c22a20-a6b2-4a03-9448-46772e13273d'
│  │  │  │  │  ▶ cache.CacheEntry.from_json   [0.1 ms]   (thread: AnyIO worker thread, dòng 68)
│  │  │  │  │  │    in  s = '{"entry_id": "13c22a20-a6b2-4a03-9448-46772e13273d", "partition": "95503c7831d2f7ed", "question": "Khách VIP được đổi trả trong bao lâu?", "answer": "Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hà…(+1886 ký tự)'
│  │  │  │  │  │    out = CacheEntry(entry_id='13c22a20-a6b2-4a03-9448-46772e13273d', partition='95503c7831d2f7ed', question='Khách VIP được đổi trả trong bao lâu?', answer='Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hàng [c2]. Trưởng ca CSKH có thể duyệt kéo dài đến t…(+19 ký tự)', citations=[{label: 'c2', doc_id: 'vip_return_exception', title: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Thời hạn đổi trả của khách VIP', collection: 'cskh', version: 1}], provenance=[Provenance(chunk_id='6d104000587bf29f', doc_id='vip_return_exception', version=1, collection='cskh', title='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section_path='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Khách hạng Bạc'), Provenance(chunk_id='9037da49391df36c', doc_id='vip_return_exception', version=1, collection='cskh', title='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section_path='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Thời hạn đổi trả của khách VIP'), Provenance(chunk_id='7f3df74338ef5336', doc_id='membership_faq', version=1, collection='public', title='Câu hỏi thường gặp về hạng thành viên', section_path='Câu hỏi thường gặp về hạng thành viên > Quyền lợi chung'), Provenance(chunk_id='232c157bca68b49d', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng'), Provenance(chunk_id='267228f9c1321d68', doc_id='complaint_handling', version=1, collection='cskh', title='Kịch bản xử lý khiếu nại khách hàng', section_path='Kịch bản xử lý khiếu nại khách hàng > Thời gian phản hồi')], intent='return_policy', entities={tier: 'vip'}, policy='NORMAL', prompt_version='v1-8cc4d02d', model='gemini-3.5-flash-lite', created_at=1.794e+09, ttl=604800, gen_tokens_in=725, gen_tokens_out=44, gen_cost_usd=0.0001, gen_latency_ms=3056.1994, hits=1, last_hit=1.794e+09)
│  │  │  │  │    out = CacheEntry(entry_id='13c22a20-a6b2-4a03-9448-46772e13273d', partition='95503c7831d2f7ed', question='Khách VIP được đổi trả trong bao lâu?', answer='Khách hàng hạng VIP được đổi trả trong vòng 33 ngày kể từ ngày nhận hàng [c2]. Trưởng ca CSKH có thể duyệt kéo dài đến t…(+19 ký tự)', citations=[{label: 'c2', doc_id: 'vip_return_exception', title: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section: 'Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Thời hạn đổi trả của khách VIP', collection: 'cskh', version: 1}], provenance=[Provenance(chunk_id='6d104000587bf29f', doc_id='vip_return_exception', version=1, collection='cskh', title='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section_path='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Khách hạng Bạc'), Provenance(chunk_id='9037da49391df36c', doc_id='vip_return_exception', version=1, collection='cskh', title='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP', section_path='Hướng dẫn nội bộ CSKH - Ngoại lệ đổi trả cho khách VIP > Thời hạn đổi trả của khách VIP'), Provenance(chunk_id='7f3df74338ef5336', doc_id='membership_faq', version=1, collection='public', title='Câu hỏi thường gặp về hạng thành viên', section_path='Câu hỏi thường gặp về hạng thành viên > Quyền lợi chung'), Provenance(chunk_id='232c157bca68b49d', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng'), Provenance(chunk_id='267228f9c1321d68', doc_id='complaint_handling', version=1, collection='cskh', title='Kịch bản xử lý khiếu nại khách hàng', section_path='Kịch bản xử lý khiếu nại khách hàng > Thời gian phản hồi')], intent='return_policy', entities={tier: 'vip'}, policy='NORMAL', prompt_version='v1-8cc4d02d', model='gemini-3.5-flash-lite', created_at=1.794e+09, ttl=604800, gen_tokens_in=725, gen_tokens_out=44, gen_cost_usd=0.0001, gen_latency_ms=3056.1994, hits=1, last_hit=1.794e+09)
│  │  │  │  ▶ cache._delete_vector   [5.6 ms]   (thread: AnyIO worker thread, dòng 192)
│  │  │  │  │    in  entry_id = '13c22a20-a6b2-4a03-9448-46772e13273d'
│  │  │  │  │    out = None
│  │  │  │    out = None
│  │  │  ▶ cache.delete   [8.3 ms]   (thread: AnyIO worker thread, dòng 196)
│  │  │  │    in  entry_id = '58268469-9c80-4a96-a8d5-fe6ff9944f8b'
│  │  │  │  ▶ cache.get_entry   [0.7 ms]   (thread: AnyIO worker thread, dòng 104)
│  │  │  │  │    in  entry_id = '58268469-9c80-4a96-a8d5-fe6ff9944f8b'
│  │  │  │  │  ▶ cache.CacheEntry.from_json   [0.0 ms]   (thread: AnyIO worker thread, dòng 68)
│  │  │  │  │  │    in  s = '{"entry_id": "58268469-9c80-4a96-a8d5-fe6ff9944f8b", "partition": "1fb84ec24c927b56", "question": "Thời hạn đổi trả hàng cho khách VIP là bao lâu?", "answer": "Khách hàng được đổi trả sản phẩm trong vòng 7 ngày kể từ ngà…(+1913 ký tự)'
│  │  │  │  │  │    out = CacheEntry(entry_id='58268469-9c80-4a96-a8d5-fe6ff9944f8b', partition='1fb84ec24c927b56', question='Thời hạn đổi trả hàng cho khách VIP là bao lâu?', answer='Khách hàng được đổi trả sản phẩm trong vòng 7 ngày kể từ ngày nhận hàng [c1]. Thành viên VIP được hỗ trợ đổi trả linh ho…(+65 ký tự)', citations=[{label: 'c1', doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', section: 'Chính sách đổi trả hàng > Phạm vi áp dụng', collection: 'public', version: 1}, {label: 'c2', doc_id: 'membership_faq', title: 'Câu hỏi thường gặp về hạng thành viên', section: 'Câu hỏi thường gặp về hạng thành viên > Quyền lợi chung', collection: 'public', version: 1}], provenance=[Provenance(chunk_id='232c157bca68b49d', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng'), Provenance(chunk_id='7f3df74338ef5336', doc_id='membership_faq', version=1, collection='public', title='Câu hỏi thường gặp về hạng thành viên', section_path='Câu hỏi thường gặp về hạng thành viên > Quyền lợi chung'), Provenance(chunk_id='5f795b0c2ed5e7a5', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Điều kiện đổi trả'), Provenance(chunk_id='0d3884b099feeb56', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Sản phẩm không áp dụng đổi trả'), Provenance(chunk_id='2bca42c3afd3fc40', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Hàng điện tử và điện thoại')], intent='return_policy', entities={tier: 'vip'}, policy='NORMAL', prompt_version='v1-8cc4d02d', model='gemini-3.5-flash-lite', created_at=1.794e+09, ttl=604800, gen_tokens_in=607, gen_tokens_out=49, gen_cost_usd=0.0001, gen_latency_ms=7305.2847, hits=0, last_hit=None)
│  │  │  │  │    out = CacheEntry(entry_id='58268469-9c80-4a96-a8d5-fe6ff9944f8b', partition='1fb84ec24c927b56', question='Thời hạn đổi trả hàng cho khách VIP là bao lâu?', answer='Khách hàng được đổi trả sản phẩm trong vòng 7 ngày kể từ ngày nhận hàng [c1]. Thành viên VIP được hỗ trợ đổi trả linh ho…(+65 ký tự)', citations=[{label: 'c1', doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', section: 'Chính sách đổi trả hàng > Phạm vi áp dụng', collection: 'public', version: 1}, {label: 'c2', doc_id: 'membership_faq', title: 'Câu hỏi thường gặp về hạng thành viên', section: 'Câu hỏi thường gặp về hạng thành viên > Quyền lợi chung', collection: 'public', version: 1}], provenance=[Provenance(chunk_id='232c157bca68b49d', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng'), Provenance(chunk_id='7f3df74338ef5336', doc_id='membership_faq', version=1, collection='public', title='Câu hỏi thường gặp về hạng thành viên', section_path='Câu hỏi thường gặp về hạng thành viên > Quyền lợi chung'), Provenance(chunk_id='5f795b0c2ed5e7a5', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Điều kiện đổi trả'), Provenance(chunk_id='0d3884b099feeb56', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Sản phẩm không áp dụng đổi trả'), Provenance(chunk_id='2bca42c3afd3fc40', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Hàng điện tử và điện thoại')], intent='return_policy', entities={tier: 'vip'}, policy='NORMAL', prompt_version='v1-8cc4d02d', model='gemini-3.5-flash-lite', created_at=1.794e+09, ttl=604800, gen_tokens_in=607, gen_tokens_out=49, gen_cost_usd=0.0001, gen_latency_ms=7305.2847, hits=0, last_hit=None)
│  │  │  │  ▶ cache._delete_vector   [6.8 ms]   (thread: AnyIO worker thread, dòng 192)
│  │  │  │  │    in  entry_id = '58268469-9c80-4a96-a8d5-fe6ff9944f8b'
│  │  │  │  │    out = None
│  │  │  │    out = None
│  │  │  ▶ cache.delete   [19.3 ms]   (thread: AnyIO worker thread, dòng 196)
│  │  │  │    in  entry_id = '09176751-c2c5-46a1-abf9-9cb46fbb0af4'
│  │  │  │  ▶ cache.get_entry   [0.8 ms]   (thread: AnyIO worker thread, dòng 104)
│  │  │  │  │    in  entry_id = '09176751-c2c5-46a1-abf9-9cb46fbb0af4'
│  │  │  │  │  ▶ cache.CacheEntry.from_json   [0.0 ms]   (thread: AnyIO worker thread, dòng 68)
│  │  │  │  │  │    in  s = '{"entry_id": "09176751-c2c5-46a1-abf9-9cb46fbb0af4", "partition": "3963a48f4b463545", "question": "Chính sách đổi trả cho phép trả hàng trong bao nhiêu ngày?", "answer": "Khách hàng được đổi trả sản phẩm trong vòng 7 ngà…(+1579 ký tự)'
│  │  │  │  │  │    out = CacheEntry(entry_id='09176751-c2c5-46a1-abf9-9cb46fbb0af4', partition='3963a48f4b463545', question='Chính sách đổi trả cho phép trả hàng trong bao nhiêu ngày?', answer='Khách hàng được đổi trả sản phẩm trong vòng 7 ngày kể từ ngày nhận hàng [c1].', citations=[{label: 'c1', doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', section: 'Chính sách đổi trả hàng > Phạm vi áp dụng', collection: 'public', version: 1}], provenance=[Provenance(chunk_id='232c157bca68b49d', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng'), Provenance(chunk_id='2bca42c3afd3fc40', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Hàng điện tử và điện thoại'), Provenance(chunk_id='0d3884b099feeb56', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Sản phẩm không áp dụng đổi trả'), Provenance(chunk_id='5f795b0c2ed5e7a5', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Điều kiện đổi trả'), Provenance(chunk_id='508f6d007ba2eeee', doc_id='shipping_policy', version=1, collection='public', title='Chính sách giao hàng và lắp đặt', section_path='Chính sách giao hàng và lắp đặt > Thời gian giao hàng')], intent='return_policy', entities={}, policy='NORMAL', prompt_version='v1-8cc4d02d', model='gemini-3.5-flash-lite', created_at=1.794e+09, ttl=604800, gen_tokens_in=660, gen_tokens_out=22, gen_cost_usd=0.0001, gen_latency_ms=778.8788, hits=0, last_hit=None)
│  │  │  │  │    out = CacheEntry(entry_id='09176751-c2c5-46a1-abf9-9cb46fbb0af4', partition='3963a48f4b463545', question='Chính sách đổi trả cho phép trả hàng trong bao nhiêu ngày?', answer='Khách hàng được đổi trả sản phẩm trong vòng 7 ngày kể từ ngày nhận hàng [c1].', citations=[{label: 'c1', doc_id: 'return_policy', title: 'Chính sách đổi trả hàng', section: 'Chính sách đổi trả hàng > Phạm vi áp dụng', collection: 'public', version: 1}], provenance=[Provenance(chunk_id='232c157bca68b49d', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Phạm vi áp dụng'), Provenance(chunk_id='2bca42c3afd3fc40', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Hàng điện tử và điện thoại'), Provenance(chunk_id='0d3884b099feeb56', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Sản phẩm không áp dụng đổi trả'), Provenance(chunk_id='5f795b0c2ed5e7a5', doc_id='return_policy', version=1, collection='public', title='Chính sách đổi trả hàng', section_path='Chính sách đổi trả hàng > Điều kiện đổi trả'), Provenance(chunk_id='508f6d007ba2eeee', doc_id='shipping_policy', version=1, collection='public', title='Chính sách giao hàng và lắp đặt', section_path='Chính sách giao hàng và lắp đặt > Thời gian giao hàng')], intent='return_policy', entities={}, policy='NORMAL', prompt_version='v1-8cc4d02d', model='gemini-3.5-flash-lite', created_at=1.794e+09, ttl=604800, gen_tokens_in=660, gen_tokens_out=22, gen_cost_usd=0.0001, gen_latency_ms=778.8788, hits=0, last_hit=None)
│  │  │  │  ▶ cache._delete_vector   [17.7 ms]   (thread: AnyIO worker thread, dòng 192)
│  │  │  │  │    in  entry_id = '09176751-c2c5-46a1-abf9-9cb46fbb0af4'
│  │  │  │  │    out = None
│  │  │  │    out = None
│  │  │    out = ['89b29268-88ac-4d02-aa9f-213ed5d83917', '13c22a20-a6b2-4a03-9448-46772e13273d', '58268469-9c80-4a96-a8d5-fe6ff9944f8b', '09176751-c2c5-46a1-abf9-9cb46fbb0af4']
│  │  ▶ sync._now   [0.0 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    out = <datetime>
│  │  ▶ sync._now   [0.0 ms]   (thread: AnyIO worker thread, dòng 23)
│  │  │    out = <datetime>
│  │  ▶ sync.record_event   [4.0 ms]   (thread: AnyIO worker thread, dòng 27)
│  │  │    in  kind = 'doc_update'
│  │  │    in  source = 'admin_api'
│  │  │    in  occurred_at = <datetime>
│  │  │    in  detected_at = <datetime>
│  │  │    in  effective_at = <datetime>
│  │  │    in  summary = 'return_policy: v1 -> v2 (4 chunk), xoá 4 cache entry'
│  │  │    in  details = {doc_id: 'return_policy', from_version: 1, to_version: 2, chunks: 4, invalidated_entries: ['89b29268-88ac-4d02-aa9f-213ed5d83917', '13c22a20-a6b2-4a03-9448-46772e13273d', '58268469-9c80-4a96-a8d5-fe6ff9944f8b', '09176751-c2c5-46a1-abf9-9cb46fbb0af4'], actor: 'admin_ops'}
│  │  │  ▶ db.fetch_one   [3.2 ms]   (thread: AnyIO worker thread, dòng 104)
│  │  │  │    in  sql = 'INSERT INTO security_events(kind,source,occurred_at,detected_at,effective_at,summary,details)⏎           VALUES (%s,%s,%s,%s,%s,%s,%s) RETURNING *'
│  │  │  │    in  params = ('doc_update', 'admin_api', <datetime>, <datetime>, <datetime>, 'return_policy: v1 -> v2 (4 chunk), xoá 4 cache entry', …(+1))
│  │  │  │    out = {id: 23, kind: 'doc_update', source: 'admin_api', occurred_at: <datetime>, detected_at: <datetime>, effective_at: <datetime>, summary: 'return_policy: v1 -> v2 (4 chunk), xoá 4 cache entry', details: {actor: 'admin_ops', chunks: 4, doc_id: 'return_policy', to_version: 2, from_version: 1, invalidated_entries: ['89b29268-88ac-4d02-aa9f-213ed5d83917', '13c22a20-a6b2-4a03-9448-46772e13273d', '58268469-9c80-4a96-a8d5-fe6ff9944f8b', '09176751-c2c5-46a1-abf9-9cb46fbb0af4']}}
│  │  │  ▶ tracing.publish   [0.6 ms]   (thread: AnyIO worker thread, dòng 85)
│  │  │  │    in  kind = 'security'
│  │  │  │    in  data = {id: 23, kind: 'doc_update', source: 'admin_api', occurred_at: '2026-11-11T04:37:58.351167+00:00', detected_at: '2026-11-11T04:37:58.276886+00:00', effective_at: '2026-11-11T04:37:58.276901+00:00', summary: 'return_policy: v1 -> v2 (4 chunk), xoá 4 cache entry', details: {actor: 'admin_ops', chunks: 4, doc_id: 'return_policy', to_version: 2, from_version: 1, invalidated_entries: ['89b29268-88ac-4d02-aa9f-213ed5d83917', '13c22a20-a6b2-4a03-9448-46772e13273d', '58268469-9c80-4a96-a8d5-fe6ff9944f8b', '09176751-c2c5-46a1-abf9-9cb46fbb0af4']}}
│  │  │  │    out = None
│  │  │    out = {id: 23, kind: 'doc_update', source: 'admin_api', occurred_at: '2026-11-11T04:37:58.351167+00:00', detected_at: '2026-11-11T04:37:58.276886+00:00', effective_at: '2026-11-11T04:37:58.276901+00:00', summary: 'return_policy: v1 -> v2 (4 chunk), xoá 4 cache entry', details: {actor: 'admin_ops', chunks: 4, doc_id: 'return_policy', to_version: 2, from_version: 1, invalidated_entries: ['89b29268-88ac-4d02-aa9f-213ed5d83917', '13c22a20-a6b2-4a03-9448-46772e13273d', '58268469-9c80-4a96-a8d5-fe6ff9944f8b', '09176751-c2c5-46a1-abf9-9cb46fbb0af4']}}
│  │    out = {id: 23, kind: 'doc_update', source: 'admin_api', occurred_at: '2026-11-11T04:37:58.351167+00:00', detected_at: '2026-11-11T04:37:58.276886+00:00', effective_at: '2026-11-11T04:37:58.276901+00:00', summary: 'return_policy: v1 -> v2 (4 chunk), xoá 4 cache entry', details: {actor: 'admin_ops', chunks: 4, doc_id: 'return_policy', to_version: 2, from_version: 1, invalidated_entries: ['89b29268-88ac-4d02-aa9f-213ed5d83917', '13c22a20-a6b2-4a03-9448-46772e13273d', '58268469-9c80-4a96-a8d5-fe6ff9944f8b', '09176751-c2c5-46a1-abf9-9cb46fbb0af4']}}
│    out = {id: 23, kind: 'doc_update', source: 'admin_api', occurred_at: '2026-11-11T04:37:58.351167+00:00', detected_at: '2026-11-11T04:37:58.276886+00:00', effective_at: '2026-11-11T04:37:58.276901+00:00', summary: 'return_policy: v1 -> v2 (4 chunk), xoá 4 cache entry', details: {actor: 'admin_ops', chunks: 4, doc_id: 'return_policy', to_version: 2, from_version: 1, invalidated_entries: ['89b29268-88ac-4d02-aa9f-213ed5d83917', '13c22a20-a6b2-4a03-9448-46772e13273d', '58268469-9c80-4a96-a8d5-fe6ff9944f8b', '09176751-c2c5-46a1-abf9-9cb46fbb0af4']}}

```
