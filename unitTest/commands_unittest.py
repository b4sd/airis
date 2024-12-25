testlist = [
    {
        "Query": "Tôi cần bạn tóm tắt nội dung từ trang mười đến năm mười lăm của cuốn sách lịch sử thế giới.",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "lịch sử thế giới", 
                "trang bắt đầu": "10", 
                "trang kết thúc": "55"
            }   
        }
    },
    {
        "Query": "Hãy giúp tôi tổng hợp ý chính từ trang mười lăm đến bảy mươi của Tư duy nhanh và chậm.",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "Tư duy nhanh và chậm", 
                "trang bắt đầu": "15", 
                "trang kết thúc": "70"
            }
        }
    },
    {
        "Query": "Tóm lược nội dung từ trang mười một đến bốn mươi chín của sách Tư duy nhanh và chậm giúp tôi.",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "Tư duy nhanh và chậm", 
                "trang bắt đầu": "11", 
                "trang kết thúc": "49"
            }
        }
    },
    {
        "Query": "Làm ơn phân tích nội dung từ đầu đến trang ba mươi của Tư duy nhanh và chậm.",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "Tư duy nhanh và chậm", 
                "trang bắt đầu": "STARTPAGE", 
                "trang kết thúc": "30"
            }
        }
    },
    {
        "Query": "Bạn có thể cô đọng thông tin cả cuốn hạt giống tâm hồn không?",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "Tư duy nhanh và chậm", 
                "trang bắt đầu": "STARTPAGE", 
                "trang kết thúc": "ENDPAGE"
            }
        }
    },
    {
        "Query": "Tôi muốn nội dung từ trang 50 trở đi của sách Cây cam ngọt của tôi được tóm gọn.",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "Cây cam ngọt của tôi", 
                "trang bắt đầu": "50", 
                "trang kết thúc": "ENDPAGE"
            }
        }
    },
    {
        "Query": "Hãy cho tôi một bản tóm tắt về các trang bảy đến mười lăm của sách không gia đình.",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "không gia đình", 
                "trang bắt đầu": "7", 
                "trang kết thúc": "15"
            }
        }
    },
    {
        "Query": "Bạn có thể tóm tắt thông tin quan trọng từ các trang ba đến trang ba bảy trong tết ở làng địa ngục?",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "tết ở làng địa ngục", 
                "trang bắt đầu": "3", 
                "trang kết thúc": "37"
            }
        }
    },
    {
        "Query": "Tóm tắt những ý chính trong chương một trong cuốn hai số phận.",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "hai số phận", 
                "trang bắt đầu": "STARTPAGE", 
                "trang kết thúc": "50"
            }
        }
    },
    {
        "Query": "Giải thích ngắn gọn nội dung các trang mười bốn đến hết của chí phèo.",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "chí phèo", 
                "trang bắt đầu": "14", 
                "trang kết thúc": "ENDPAGE"
            }
        }
    },
    {
        "Query": "Hãy cho tôi biết nội dung chính từ trang mười đến năm mươi của số đỏ.",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "số đỏ", 
                "trang bắt đầu": "10", 
                "trang kết thúc": "50"
            }
        }
    },
    {
        "Query": "Hãy tóm tắt chương cuối của Nhà Giả Kim.",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "Nhà Giả Kim", 
                "trang bắt đầu": "10", 
                "trang kết thúc": "50"
            }
        }
    },
    {
        "Query": "Tóm gọn nội dung từ trang 10-50 của sách Tư duy nhanh và chậm.",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "Tư duy nhanh và chậm", 
                "trang bắt đầu": "10", 
                "trang kết thúc": "50"
            }
        }
    },
    {
        "Query": "Làm ơn giúp tôi tóm lược các trang hai đến năm mươi trong Tư duy nhanh và chậm.",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "Tư duy nhanh và chậm", 
                "trang bắt đầu": "2", 
                "trang kết thúc": "50"
            }
        }
    },
    {
        "Query": "Hãy tổng hợp nội dung sách Hai Số Phận từ trang đầu đến ba mươi.",
        "Output": {
            "command": "tóm tắt", 
            "parameters": {
                "tên sách": "Hai Số Phận", 
                "trang bắt đầu": "STARTPAGE", 
                "trang kết thúc": "30"
            }
        }
    },
    {
        "Query": "Đọc cho tôi cuốn Nhà giả kim từ trang 15 đến 30.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Nhà giả kim", 
                "trang bắt đầu": "15", 
                "trang kết thúc": "30",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Bắt đầu đọc sách Sapiens từ trang 50 đến trang 80 nhé.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Sapiens", 
                "trang bắt đầu": "50", 
                "trang kết thúc": "80",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Tôi muốn nghe nội dung sách Lược sử loài người từ trang 10 tới 40.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Lược sử loài người", 
                "trang bắt đầu": "10", 
                "trang kết thúc": "40",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Đọc tiếp cuốn Hoàng tử bé từ trang 5 đến 20.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Hoàng tử bé", 
                "trang bắt đầu": "5", 
                "trang kết thúc": "20",
                "start_from_previous": "True"
            }
        }
    },
    {
        "Query": "Hãy đọc sách Tư duy nhanh và chậm từ trang 25 đến 50.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Tư duy nhanh và chậm", 
                "trang bắt đầu": "25", 
                "trang kết thúc": "50",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Mở sách Chiến binh cầu vồng, đọc từ trang 100 đến 120.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Chiến binh cầu vồng", 
                "trang bắt đầu": "100", 
                "trang kết thúc": "120",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Tôi muốn nghe cuốn Sherlock Holmes từ trang 1 đến trang 25.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Sherlock Holmes", 
                "trang bắt đầu": "1", 
                "trang kết thúc": "25",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Đọc sách Đắc nhân tâm từ trang 30 đến 60 giúp tôi.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Đắc nhân tâm", 
                "trang bắt đầu": "30", 
                "trang kết thúc": "60",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Đọc cuốn Giấc mơ Mỹ từ trang 70 đến 90.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Giấc mơ Mỹ", 
                "trang bắt đầu": "70", 
                "trang kết thúc": "90",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Bắt đầu đọc cuốn Người bán hàng vĩ đại nhất từ trang 15 đến 35.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Người bán hàng vĩ đại nhất", 
                "trang bắt đầu": "15", 
                "trang kết thúc": "35",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Hãy mở sách Cuộc sống của Pi và đọc từ trang 5 đến 50.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Cuộc sống của Pi", 
                "trang bắt đầu": "5", 
                "trang kết thúc": "50",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Đọc cuốn Vượt lên chính mình từ trang 20 đến 40.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Vượt lên chính mình", 
                "trang bắt đầu": "20", 
                "trang kết thúc": "40",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Tôi muốn nghe nội dung cuốn Bố già từ trang 60 đến 100.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Bố già", 
                "trang bắt đầu": "60", 
                "trang kết thúc": "100",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Bắt đầu đọc cuốn Đại dịch từ trang 50 tới 90 giúp tôi.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Đại dịch", 
                "trang bắt đầu": "50", 
                "trang kết thúc": "90",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Đọc sách Mật mã Da Vinci từ trang 10 đến 30.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "Mật mã Da Vinci", 
                "trang bắt đầu": "10", 
                "trang kết thúc": "30",
                "start_from_previous": "False"
            }
        }
    },
    {
        "Query": "Tiếp tục đi nào.",
        "Output": {
            "command": "tiếp tục", 
            "parameters": {}
        }
    },
    {
        "Query": "Hãy tiếp tục.",
        "Output": {
            "command": "tiếp tục", 
            "parameters": {}
        }
    },
    {
        "Query": "Hãy đọc sách tiếp đi.",
        "Output": {
            "command": "tiếp tục", 
            "parameters": {}
        }
    },
    {
        "Query": "Tiếp tục đọc sách.",
        "Output": {
            "command": "tiếp tục", 
            "parameters": {}
        }
    },
    {
        "Query": "Tiếp tục đọc sách đi.",
        "Output": {
            "command": "tiếp tục", 
            "parameters": {}
        }
    },
    {
        "Query": "Tiếp tục với việc đọc sách.",
        "Output": {
            "command": "tiếp tục", 
            "parameters": {}
        }
    },
    {
        "Query": "Hãy tiếp tục đọc nhé.",
        "Output": {
            "command": "tiếp tục", 
            "parameters": {}
        }
    },
    {
        "Query": "Cứ tiếp tục đọc đi.",
        "Output": {
            "command": "tiếp tục", 
            "parameters": {}
        }
    },
    {
        "Query": "Đọc tiếp từ đoạn trước.",
        "Output": {
            "command": "đọc sách", 
            "parameters": {
                "tên sách": "?", 
                "trang bắt đầu": "PREVIOUS_STOPPAGE", 
            }
        }
    },
    {
        "Query": "Làm tiếp đọc sách đi.",
        "Output": {
            "command": "tiếp tục", 
            "parameters": {}
        }
    },
    {
        "Query": "Hãy giải thích định lý Pitago?", 
        "Output": {
            "command": "hỏi đáp", 
            "parameters": {
                "câu hỏi": "'Định lý Pitago là gì?'"
            }
        }
    },
    {
        "Query": "Hãy chỉ cho tôi cách nấu món phở bò chuẩn vị?", "Output": {
            "command": "hỏi đáp", 
            "parameters": {
                "câu hỏi": "'Làm sao để nấu món phở bò đúng vị?'"
            }
        }
    },
    {
        "Query": "Cho tôi hỏi tại sao bầu trời có màu xanh?", "Output": {
            "command": "hỏi đáp", 
            "parameters": {
                "câu hỏi": "'Nguyên nhân khiến bầu trời màu xanh là gì?'"
            }
        }
    },
    {
        "Query": "Hãy cho biết ý nghĩa của cuộc sống?", 
        "Output": {
            "command": "hỏi đáp", 
            "parameters": {
                "câu hỏi": "'Ý nghĩa của cuộc sống là gì?'"
            }
        }
    },
    {
        "Query": "Cách học lập trình hiệu quả?", 
        "Output": {
            "command": "hỏi đáp", 
            "parameters": {
                "câu hỏi": "'Làm thế nào để học lập trình một cách hiệu quả?'"
            }
        }
    },
    {
        "Query": "Làm thế nào để tập trung hơn khi học?", 
        "Output": {
            "command": "hỏi đáp", 
            "parameters": {
                "câu hỏi": "'Cách để tăng sự tập trung trong học tập?'"
            }
        }
    },
    {
        "Query": "Hãy nêu các bước giải một bài toán đố?", 
        "Output": {
            "command": "hỏi đáp", 
            "parameters": {
                "câu hỏi": "'Làm sao để giải bài toán đố?'"
            }
        }
    },
    {
        "Query": "Tại sao nước biển lại mặn?", 
        "Output": {
            "command": "hỏi đáp", 
            "parameters": {
                "câu hỏi": "'Nguyên nhân khiến nước biển mặn?'"
            }
        }
    },
    {
        "Query": "Cách để giảm cân nhanh và an toàn?", 
        "Output": {
            "command": "hỏi đáp", 
            "parameters": {
                "câu hỏi": "'Làm sao để giảm cân một cách an toàn?'"
            }
        }
    },
    {
        "Query": "Hãy cho tôi biết về vũ trụ?", 
        "Output": {
            "command": "hỏi đáp", 
            "parameters": {
                "câu hỏi": "'Vũ trụ là gì và có những đặc điểm nào?'"
            }
        }
    },
    {"Query": "Hãy thoát khỏi chương trình ngay lập tức.", "Output": {"command": "thoát chương trình", "parameters": {}}},
    {"Query": "Cách để dừng chương trình này?", "Output": {"command": "thoát chương trình", "parameters": {}}},
    {"Query": "Tôi muốn thoát khỏi ứng dụng này.", "Output": {"command": "thoát chương trình", "parameters": {}}},
    {"Query": "Làm sao để kết thúc chương trình một cách an toàn?", "Output": {"command": "thoát chương trình", "parameters": {}}},
    {"Query": "Hãy kết thúc hoạt động của phần mềm ngay.", "Output": {"command": "thoát chương trình", "parameters": {}}},
    {"Query": "Dừng tất cả các tiến trình và thoát chương trình.", "Output": {"command": "thoát chương trình", "parameters": {}}},
    {"Query": "Tôi muốn đóng ứng dụng này.", "Output": {"command": "thoát chương trình", "parameters": {}}},
    {"Query": "Làm sao để tắt chương trình một cách nhanh chóng?", "Output": {"command": "thoát chương trình", "parameters": {}}},
    {"Query": "Hãy tắt chương trình giúp tôi.", "Output": {"command": "thoát chương trình", "parameters": {}}},
    {"Query": "Thoát chương trình ngay và dừng mọi hoạt động.", "Output": {"command": "thoát chương trình", "parameters": {}}}

]