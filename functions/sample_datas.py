import pandas as pd

def sample_data(sample_name):
    # Define sample data based on the requested sample
    if sample_name == 'inc_prev_month':
        data = {
            "보험사+업적월+상품군 key": ["이관계약", "보험사명/202307", "보험사명/202307", "보험사명/202307"],
            "마감월": ["-", 202406, 202406, 202406],
            "보험사": ["-", "보험사명", "보험사명", "보험사명"],
            "업적월": ["-", 202307, 202307, 202307],
            "당기해당회차": [None, 12, 12, 12],
            "수익비용인식회차": [None, 24, 36, 36],
            "환수율적용회차": [None, 15, 18, 24],
            "환수율": ["-", "20.00%", "65.00%", "8.33%"],
            "유지율": ["-", "86.60%", "86.60%", "86.60%"],
            "성과(당월)": ["-", -4102955, None, -1050218],
            "계약관리(당월)": ["-", 30785119, None, None],
            "수금(당월)": ["-", None, None, None],
            "운영(당월)": ["-", None, None, None],
            "기타(당월)": ["-", None, None, None],
            "성과(누적)": ["-", 975102199, 1093299, 640091742],
            "계약관리(누적)": ["-", 74087294, 1460611, None],
            "수금(누적)": ["-", None, None, None],
            "운영(누적)": ["-", None, None, None],
            "기타(누적)": ["-", None, None, None],
            "기초선수수익": ["-", 530402792, 759235, 445237472],
            "당월정액상각대상수령액": ["-", -4102955, None, -1050218],
            "당월누적수익인식액": ["-", 487551100, 364433, 213363914],
            "전월누적수익인식액": ["-", 448802362, 334064, 195904488],
            "당월수익인식액": ["-", 38748737, 30369, 17459426],
            "기타조정액": ["-", None, None, None],
            "기말선수수익": ["-", 487551100, 728866, 426727828],
            "기초환수부채": ["-", 30079252, 96722, 13129745],
            "당기환수수익조정": ["-", -3938262, -1465, -5979797],
            "기말환수부채": ["-", 26140990, 95256, 7149948]
        }
    elif sample_name == 'inc_data_case':
        data = {
            "마감월": ["202406", "202406", "202406"],
            "보험사": ["보험사명", "보험사명", "보험사명"],
            "모집인코드": [1234, 1234, 1234],
            "증권번호": [1234, 1234, 1234],
            "계약일": ["2024-03-29", "2024-03-29", "2024-06-29"],
            "처리납입방법": ["월납", "월납", "월납"],
            "처리계약상태": ["정상", "정상", "정상"],
            "처리납입회차": [4, 4, 1],
            "계산방식": ["유지", "유지", "신계약"],
            "보험료": [255976, 85776, 350178],
            "월납화 보험료": [255976, 85776, 350178],
            "정산성적": [0, 0, 632158],
            "환산성적1": [303667, 140683, 632158],
            "환산성적2": [0, 0, 632158],
            "환산성적3": [0, 0, 632158],
            "성과": [0, 0, 2844711],
            "계약관리": [0, 0, 0],
            "수금": [0, 0, 0],
            "운영": [0, 0, 0],
            "기타": [0, 0, 0],
            "합계": [0, 0, 2844711],
            "납입기간": [0, 0, 0],
            "상품군": ["", "", "보장성"],
            "상품코드": [1234, 1234, 1234],
            "상품명": ["", "", "상품명"],
            "계약자": ["", "", "주식회사 금송산업개"],
            "피보험자": ["abc", "abc", "천순희"],
            "태아회차": ["", "", ""],
            "태아여부": ["", "", ""],
            "ERP사번": [1234, 1234, 1234],
            "사원명": ["사원명", "사원명", "사원명"],
            "모집인 소속경로_사업단": ["", "", ""],
            "모집인 소속경로_지점/팀": ["", "", ""]
        }
    elif sample_name == 'inc_main':
        data = {
            "보험사+업적월+상품군 key": ["보험사명/202307", "보험사명/202307", "보험사명/202307"],
            "마감월": [202406, 202406, 202406],
            "보험사": ["보험사명", "보험사명", "보험사명"]
        }

    elif sample_name == 'exp_main':
        data = {
            "보험사+업적월+상품군 key": ["이관계약", "DB손보/202307", "DB손보/202308", "DB손보/202309"],
            "마감월": [None, 202406, 202406, 202406],  # Assuming 'None' where data is not provided
            "보험사": [None, "DB손보", "DB손보", "DB손보"]  # Assuming 'None' where data is not provided
            }
    elif sample_name == 'exp_security':
            data = {
            "마감월": [202406, 202406, 202406],
            "지급사원번호": ["0020000001", "0020000001", "0020000001"],
            "지급사원명": ["박경은", "박경은", "박경은"],
            "부지급여부": ["지급", "지급", "지급"],
            "직급": ["위임직", "위임직", "위임직"],
            "보험사": ["흥국생명", "삼성화재", "KB손보"],
            "증권번호": ["3434737200001", "52339200770000", "20236770018"],
            "계약일": ["9/24/2023", "12/15/2023", "11/13/2023"],
            "처리계약상태": ["정상", "정상", "정상"],
            "처리납입회차": [10, 7, 8],
            "지급로직": ["유지", "유지", "유지"],
            "납입방법": ["월납", "월납", "월납"],
            "선지급/분급": ["선지급", "선지급", "선지급"],
            "규정": ["환산형", "환산형", "환산형"],
            "쉐어율": ["100.00%", "100.00%", "100.00%"],
            "보험료": [89913, 58000, 38592],
            "보험사환산": [179826, 43505, 92620],
            "통합환산성적1": [224782, 30453, 92620],
            "통합환산성적2": [224782, 30453, 92620],
            "통합환산성적3": [224782, 30453, 92620],
            "신계약지급률": [0.00, 0.00, 0.00],
            "유지관리지급률": [0.00, 0.00, 0.00],
            "유지성과지급률": [0.00, 0.00, 0.00],
            "추가가감율": [100.00, 100.00, 100.00],
            "환수율": [0, 0, 0],
            "감액율": [0.00, 0.00, 0.00],
            "[지급수수료] 신계약성과": [0, 0, 0],
            "[지급수수료] 유지관리": [0, 0, 0],
            "[지급수수료] 유지성과": [0, 0, 0],
            "[지급수수료] 자동차": [0, 0, 0],
            "[지급수수료] 일반": [0, 0, 0],
            "[지급수수료] 합계": [0, 0, 0],
            "[수입수수료] 성과": [17982, 11311, 17597],
            "[수입수수료] 계약관리": [0, 0, 0],
            "[수입수수료] 수금": [0, 0, 0],
            "[수입수수료] 운영(OA)": [0, 0, 0],
            "[수입수수료] 자동차": [0, 0, 0],
            "[수입수수료] 일반": [0, 0, 0],
            "[수입수수료] 합계": [17982, 11311, 17597],
            "상품군1": ["보장성", "장기", "장기"],
            "상품군2": ["건강", "재물", "건강"],
            "상품명": ["(무)흥국생명다(多)사랑OK355간편건강보험", "무배당 삼성화재 재물보험 수퍼비즈니스(BOP)(2304.20)", "KB 금쪽같은 희망플러스 건강보험(무배당)(23.11)_2종_무해지"],
            "계약자": ["고석주", "김지혜", "김지혜"],
            "피보험자": ["고석주", "김지혜", ""],
            "교차판매": ["N", "N", "N"],
            "본인/가족 계약": [None, None, None],
            "소속": ["본사 > 영업본부 > 조직영업팀", "본사 > 영업본부 > 조직영업팀", "본사 > 영업본부 > 조직영업팀"],
            "데이터형태": ["시스템", "시스템", "시스템"],
            "사업단": [None, None, None],
            "지점/팀": [None, None, None]
        }
        
        
    elif sample_name == 'exp_override':
        data = {
            "마감월": [202406, 202406, 202406],
            "[오버라이드] 종류": ["사업단", "지점/팀", "사업단"],
            "[오버라이드] 대상자사번": ["0020000014", "1020230207", "0020000014"],
            "[오버라이드] 대상자": ["이준서", "김정순", "이준서"],
            "[오버라이드] 규정": ["환산형_OVR", "환산형_OVR", "환산형_OVR"],
            "[오버라이드] 재직여부": ["위촉", "위촉", "위촉"],
            "[FC] 대상자사번": ["1020230210", "1020230210", "1020230210"],
            "[FC] 대상자": ["이수진", "이수진", "이수진"],
            "[FC] 입사차월": [12, 12, 12],
            "[FC] 규정": ["환산형", "환산형", "환산형"],
            "[FC] 재직여부": ["위촉", "위촉", "위촉"],
            "보험사": ["흥국생명", "흥국생명", "흥국생명"],
            "증권번호": ["0000960490079", "0000960490079", "0001077650269"],
            "계약일": ["2024-06-29", "2024-06-29", "2024-06-17"],
            "처리계약상태": ["정상", "정상", "정상"],
            "처리납입회차": [1, 1, 1],
            "계산방식": ["신계약", "신계약", "신계약"],
            "납입방법": ["월납", "월납", "월납"],
            "지급유형": ["선지급", "선지급", "선지급"],
            "쉐어율": ["100.00%", "100.00%", "100.00%"],
            "보험료": [350178, 350178, 62028],
            "보험사환산": [632158, 632158, 123164],
            "통합환산성적": [948237, 948237, 184746],
            "FC수수료": [2528632, 2528632, 492656],
            "지급율": [15.00, 3.00, 15.00],
            "가삭감률": [100.00, 100.00, 100.00],
            "환수율": [0, 0, 0],
            "감액율": [0.00, 0.00, 0.00],
            "[지급수수료] 성과": [379294, 75858, 73898],
            "[지급수수료] 육성": [0, 0, 0],
            "[지급수수료] 합계": [379294, 75858, 73898],
            "[수입수수료] 성과": [2844711, 2844711, 554238],
            "[수입수수료] 계약관리": [0, 0, 0],
            "[수입수수료] 수금": [0, 0, 0],
            "[수입수수료] 운영(OA)": [0, 0, 0],
            "[수입수수료] 합계": [2844711, 2844711, 554238],
            "상품군1": ["보장성", "보장성", "보장성"],
            "상품군2": ["건강", "건강", "건강"],
            "상품명": ["(무)흥국생명다(多)사랑OK355간편건강보험", "(무)흥국생명다(多)사랑OK355간편건강보험", "(무)흥국생명다(多)사랑통합보험"],
            "계약자": ["주식회사 금송산업개", "주식회사 금송산업개", "스토케코리아 유한회"],
            "피보험자": ["천순희", "천순희", "채민재"],
            "본인/가족계약": ["N", "N", "N"],
            "데이터형태": ["시스템", "시스템", "시스템"]
        }
    elif sample_name == 'exp_retirement':
         data = {
            "마감월": [202406, 202406, 202406],
            "지급사원번호": [1020230239, 1020230239, 1020231042],
            "지급사원명": ["김난희", "김난희", "서승남"],
            "부지급여부": ["부지급", "부지급", "부지급"],
            "직급": ["설계사", "설계사", "설계사"],
            "보험사": ["흥국생명", "흥국생명", "흥국생명"],
            "증권번호": ["1219652200025", "2149547200009", "3578157200001"],
            "계약일": ["2023-07-06", "2023-07-17", "2023-08-31"],
            "처리계약상태": ["정상", "정상", "정상"],
            "처리납입회차": [12, 12, 11],
            "계산방식": ["유지", "유지", "유지"],
            "납입방법": ["월납", "월납", "월납"],
            "지급유형": ["분급", "분급", "분급"],
            "규정": ["환산형", "환산형", "환산형"],
            "쉐어율": ["100.00%", "100.00%", "100.00%"],
            "보험료": [56024, 63811, 48734],
            "보험사환산": [93132, 120718, 97468],
            "통합환산성적": [116415, 150897, 121835],
            "신계약지급률": [260.00, 260.00, 260.00],
            "유지관리지급률": [10.00, 10.00, 10.00],
            "유지성과지급률": [0.00, 0.00, 0.00],
            "[지급수수료] 신계약성과": [12611, 16347, 13198],
            "[지급수수료] 유지관리": [0, 0, 0],
            "[지급수수료] 유지성과": [0, 0, 0],
            "[지급수수료] 합계": [12611, 16347, 13198],
            "[수입수수료] 성과": [0, 0, 0],
            "[수입수수료] 유지": [13969, 18107, 9746],
            "[수입수수료] 수금": [0, 0, 0],
            "[수입수수료] 운영(OA)": [0, 0, 0],
            "[수입수수료] 합계": [13969, 18107, 9746],
            "상품군1": ["보장성", "보장성", "보장성"],
            "상품군2": ["건강", "건강", "건강"],
            "상품명": ["(무)흥국생명암만보는다사랑건강보험", "(무)흥국생명다(多)사랑통합보험", "(무)흥국생명더블페이암보험"],
            "계약자": ["이옥선", "김지은", "장성수"],
            "피보험자": ["이옥선", "김지은", "장성수"],
            "교차판매": ["N", "N", "N"],
            "본인/가족 계약": [None, None, None],
            "소속": ["전속채널 > FC사업부 > 1총괄본부 > 서울본부 > 을지로사업단 > 을지로[00]지점", "전속채널 > FC사업부 > 1총괄본부 > 서울본부 > 을지로사업단 > 을지로[00]지점", "전속채널 > FC사업부 > 1총괄본부 > 충청본부 > 괴산사업단 > 괴산[01]지점"],
            "데이터형태": ["시스템", "시스템", "시스템"],
            "사업단": ["을지로사업단", "을지로사업단", "괴산사업단"],
            "지점/팀": ["을지로[00]지점", "을지로[00]지점", "괴산[01]지점"]
        }
    elif sample_name == 'exp_prev_month':
         data = {
            "보험사+업적월+상품군 key": ["이관계약", "DB손보/202307", "DB손보/202308"],
            "마감월": [None, 202405, 202405],
            "보험사": [None, "DB손보", "DB손보"],
            "업적월": [None, 202307, 202308],
            "당기해당회차": [None, 11, 10],
            "수익비용인식회차": [None, 18, 18],
            "환수율적용회차": [None, 18, 18],
            "환수율(성과수수료)": [None, 0.6, 0.65],
            "환수율(유지성과수수료)": [0, 0, 0],
            "유지율": [None, 0.87465024, 0.886045673],
            "[지급수수료] 신계약성과(당월)": [56900, 17870, 0],
            "[지급수수료] 유지관리(당월)": [36598842, 87970, 200566],
            "[지급수수료] 유지성과(당월)": [0, 0, 0],
            "[지급수수료] 자동차(당월)": [-81740, 0, 0],
            "[지급수수료] 일반(당월)": [0, 0, 0],
            "[지급수수료] 오버라이드성과(당월)": [0, 0, 0],
            "[지급수수료] 오버라이드육성(당월)": [0, 0, 0],
            "[지급수수료] 신계약성과(누적)": [-3157578, 2771313, 6369948],
            "[지급수수료] 유지관리(누적)": [345005511, 201796, 253915],
            "[지급수수료] 유지성과(누적)": [0, 0, 0],
            "[지급수수료] 자동차(누적)": [-1005540, 102670, 1494326],
            "[지급수수료] 일반(누적)": [5325, 13455, 0],
            "[지급수수료] 오버라이드성과(누적)": [0, 739873, 1329181],
            "[지급수수료] 오버라이드육성(누적)": [0, 0, 0],
            "기초선급비용": [0, 1552584.889, 3849564.5],
            "당월정액상각대상수지급액": [17870, 2145724.778, 427729.3889],
            "당월누적비용인식액": [1940731.111, 204993.6667, 3421835.111],
            "전월누적비용인식액": [264075.7926, 0, 552729.9097],
            "당월비용인식액": [427729.3889, 0, 570276.891],
            "기타조정액": [0, 0, 17546.98126],
            "기말선급비용": [3421835.111, 1365461.222, 570276.891],
            "기초환수자산": [258751.0078, 5324.784858, 17546.98126],
            "당기환수비용조정": [5325, 0, 0],
            "기말환수자산": [0, 0, 0]
        }
    else:
        return None

    # Create a DataFrame
    df = pd.DataFrame(data)
    return df

# Do not call the function here, just define it