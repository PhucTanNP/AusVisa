// ============================================================
// CYPHER PROMPT - TƯ VẤN DU HỌC, VISA & ĐỊNH CƯ ÚC
// Knowledge Graph Structure: Study + Visa + Settlement + Cross-Relations
// ============================================================

// ============================================================
// PHẦN 1: TƯ VẤN DU HỌC (STUDY)
// ============================================================

-- name: universities_in_australia
// Đếm và liệt kê tất cả trường tại Úc (trực tiếp từ node University)
MATCH (u:University)
WITH count(u) AS total_universities, collect(u.name) AS uni_names
UNWIND uni_names AS university
RETURN 
  total_universities,
  university
ORDER BY university;

-- name: find_programs_by_university_subject_level
// 1.1. TÌM CHƯƠNG TRÌNH HỌC THEO TRƯỜNG, NGÀNH, CẤP ĐỘ
// Use case: "Tìm chương trình Master về Computer Science tại University of Melbourne"
MATCH (u:University {name: $university_name})
MATCH (u)-[:HAS_PROGRAMS]->(pg:ProgramGroup)
      -[:HAS_LEVEL]->(pl:ProgramLevel {name: $level})
      -[:OFFERS]->(p:Program)
WHERE p.program_type = $level
OPTIONAL MATCH (p)-[:FOCUSES_ON]->(subj:Subject)
OPTIONAL MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
WHERE toLower(subj.name) CONTAINS toLower($subject_keyword)
   OR toLower(cat.name) CONTAINS toLower($subject_keyword)
   OR toLower(p.name) CONTAINS toLower($subject_keyword)
RETURN u.name AS university,
       p.name AS program_name,
       p.url AS program_url,
       p.description AS description,
       p.starting_months AS starting_months,
       subj.name AS subject,
       cat.name AS category
LIMIT 20;

-- name: find_programs_by_ielts
// 1.2. TÌM TRƯỜNG THEO YÊU CẦU IELTS/TOEFL
// Use case: "Tìm trường yêu cầu IELTS 6.5 trở xuống"
MATCH (p:Program)-[:HAS_REQUIRED]->(es:ExamScore)
      <-[:HAS_SCORE]-(e:Exam {name: "IELTS"})
WHERE es.value <= $max_score
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)
      <-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
RETURN DISTINCT u.name AS university,
       p.name AS program_name,
       es.value AS ielts_required,
       es.plus AS needs_plus,
       p.url AS url
ORDER BY es.value ASC
LIMIT 20;

-- name: find_programs_by_intake_month
// 1.3. TÌM CHƯƠNG TRÌNH THEO KỲ NHẬP HỌC
// Use case: "Chương trình nào nhập học tháng 2?"
MATCH (p:Program)-[:STARTS_IN]->(m:Month {name: $month})
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
OPTIONAL MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
RETURN u.name AS university,
       p.name AS program_name,
       p.program_type AS level,
       cat.name AS category,
       p.starting_months AS all_start_months,
       p.url AS url
LIMIT 20;

-- name: find_combined_programs
// 1.4. TÌM CHƯƠNG TRÌNH COMBINED (KÉP)
// Use case: "Tìm chương trình kép Bachelor + Master"
MATCH (parent:Program {relation: "combined"})
      -[:HAS_COMPONENT]->(comp:Program)
MATCH (parent)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
RETURN u.name AS university,
       parent.name AS combined_program,
       collect(comp.name) AS components,
       collect(comp.program_type) AS component_levels,
       parent.url AS url
LIMIT 10;

-- name: compare_entry_requirements
// 1.5. SO SÁNH YÊU CẦU ĐẦU VÀO CỦA NHIỀU TRƯỜNG
// Use case: "So sánh yêu cầu IELTS giữa 3 trường"
MATCH (u:University)
WHERE u.name IN $university_list
MATCH (u)-[:HAS_PROGRAMS]->(pg:ProgramGroup)
      -[:HAS_LEVEL]->(pl:ProgramLevel {name: $level})
      -[:OFFERS]->(p:Program)
OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
RETURN u.name AS university,
       p.name AS program,
       collect(DISTINCT {
           exam: e.name,
           score: es.value,
           plus: es.plus
       }) AS entry_requirements
ORDER BY u.name;

-- name: popular_subjects
// 1.6. TÌM NGÀNH HỌC PHỔ BIẾN
// Use case: "Những ngành nào được nhiều trường cung cấp nhất?"
MATCH (p:Program)-[:FOCUSES_ON]->(s:Subject)
WITH s.name AS subject, count(DISTINCT p) AS program_count
ORDER BY program_count DESC
LIMIT 15
MATCH (s:Subject {name: subject})<-[:FOCUSES_ON]-(p:Program)
      <-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
RETURN subject,
       program_count,
       collect(DISTINCT u.name)[..5] AS sample_universities
ORDER BY program_count DESC;

-- name: university_info_pages
// 1.7. TÌM THÔNG TIN TRƯỜNG (Info Pages)
// Use case: "Chi phí sinh hoạt tại UNSW như thế nào?"
MATCH (u:University {name: $university_name})
      -[:HAS_INFO]->(ip:InfoPage)
      -[:HAS_SECTION]->(sec:InfoSection)
WHERE toLower(sec.key) CONTAINS toLower($info_type)
   OR $info_type IN ['cost', 'accommodation', 'food', 'transport']
RETURN u.name AS university,
       sec.key AS info_category,
       sec.content AS information,
       sec.url AS source_url;

-- name: find_programs_by_tuition_in_description
// 1.8. TÌM CHƯƠNG TRÌNH THEO HỌC PHÍ (nếu có trong description)
// Use case: "Tìm chương trình có học phí dưới 30,000 AUD"
MATCH (p:Program)
WHERE p.description CONTAINS '$' OR p.description CONTAINS 'AUD'
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
RETURN u.name AS university,
       p.name AS program,
       p.description AS description,
       p.url AS url
LIMIT 20;

-- name: find_visas_by_type
// 2.1. TÌM VISA THEO LOẠI (Type)
// Use case: "Có những loại visa du học nào?"
MATCH (vt:VisaType {name_display: $visa_type})
      <-[:BELONGS_TO_TYPE]-(v:Visa)
RETURN vt.name_display AS visa_type,
       collect({
           name: v.name_visa,
           subclass: v.subclass,
           url: v.url
       }) AS visas;

// ============================================================
// PHẦN 2: TƯ VẤN VISA
// ============================================================

-- name: visa_about
// 2.2. XEM THÔNG TIN CHI TIẾT VỀ 1 VISA (About)
// Use case: "Visa 500 là gì?"
MATCH (v:Visa {subclass: $subclass})
OPTIONAL MATCH (v)-[:HAS_ABOUT_INFO]->(a:AboutInfo)
RETURN v.name_visa AS visa_name,
       v.subclass AS subclass,
       v.type AS visa_type,
       v.url AS official_url,
       collect({
           field: a.field,
           content: a.content
       }) AS about_information;

-- name: visa_eligibility
// 2.3. XEM ĐIỀU KIỆN ĐỦ ĐIỀU KIỆN (Eligibility)
// Use case: "Điều kiện xin visa 500 là gì?"
MATCH (v:Visa {subclass: $subclass})
      -[:HAS_ELIGIBILITY_GROUP]->(eg:EligibilityGroup)
      -[:HAS_REQUIREMENT]->(er:EligibilityRequirement)
RETURN v.name_visa AS visa_name,
       eg.group_key AS requirement_group,
       collect({
           key: er.key,
           content: er.content
       }) AS requirements
ORDER BY eg.group_key;

-- name: visa_steps
// 2.4. XEM CÁC BƯỚC XIN VISA (Step by Step)
// Use case: "Quy trình xin visa 500 như thế nào?"
MATCH (v:Visa {subclass: $subclass})-[:HAS_STEP]->(s:VisaStep)
RETURN v.name_visa AS visa_name,
       s.step_order AS step_number,
       s.title AS step_title,
       s.code AS step_code,
       s.body AS step_description,
       s.url AS step_url
ORDER BY s.step_order;

-- name: find_visas_by_purpose
// 2.5. TÌM VISA PHÙ HỢP VỚI MỤC ĐÍCH
// Use case: "Tôi muốn du học và sau đó định cư, nên chọn visa nào?"
MATCH (v:Visa)-[:BELONGS_TO_TYPE]->(vt:VisaType)
WHERE vt.name_display CONTAINS $purpose
   OR v.name_visa CONTAINS $purpose
OPTIONAL MATCH (v)-[:HAS_ABOUT_INFO]->(a:AboutInfo)
WHERE a.field CONTAINS 'benefit' OR a.field CONTAINS 'purpose'
RETURN v.name_visa AS visa_name,
       v.subclass AS subclass,
       vt.name_display AS type,
       v.url AS url,
       collect(DISTINCT a.content)[..3] AS key_benefits
LIMIT 10;

-- name: visa_skilled_list
// 2.6. TÌM TẤT CẢ VISA SKILLED (PR)
// Use case: "Có những visa định cư nào?"
MATCH (v:Visa)
WHERE v.subclass IN ["189", "190", "191", "491", "494", "186", "187"]
OPTIONAL MATCH (v)-[:HAS_ABOUT_INFO]->(a:AboutInfo)
RETURN v.name_visa AS visa_name,
       v.subclass AS subclass,
       v.url AS url,
       collect(DISTINCT a.content)[..2] AS description
ORDER BY v.subclass;

// ============================================================
// PHẦN 3: TƯ VẤN ĐỊNH CƯ (SETTLEMENT)
// ============================================================

-- name: find_settlement_by_category
// 3.1. TÌM THÔNG TIN ĐỊNH CƯ THEO DANH MỤC
// Use case: "Làm sao tìm việc tại Úc?"
MATCH (cat:SettlementCategory {name: $category})
      -[:HAS_GROUP]->(tg:SettlementTaskGroup)
      -[:CONTAINS_SETTLEMENT_PAGE]->(sp:SettlementPage)
OPTIONAL MATCH (sp)-[:HAS_SETTLEMENT_SECTION]->(sec)
RETURN cat.name AS category,
       tg.name AS task_group,
       sp.title AS page_title,
       sp.url AS page_url,
       collect({
           section_title: sec.title,
           section_url: sec.url,
           section_path: sec.path
       })[..5] AS sections
LIMIT 10;

-- name: list_settlement_categories
// 3.2. TÌM TẤT CẢ DANH MỤC ĐỊNH CƯ
// Use case: "Có những hỗ trợ gì khi mới đến Úc?"
MATCH (cat:SettlementCategory)-[:HAS_GROUP]->(tg:SettlementTaskGroup)
WITH cat, count(tg) AS task_count
RETURN cat.name AS category,
       task_count AS number_of_task_groups
ORDER BY task_count DESC;

-- name: settlement_page_detail
// 3.3. TÌM THÔNG TIN CHI TIẾT VỀ MỘT TRANG ĐỊNH CƯ
// Use case: "Chi tiết về tìm nhà ở tại Úc"
MATCH (sp:SettlementPage {title: $page_title})
OPTIONAL MATCH (sp)-[:HAS_SETTLEMENT_SECTION]->(sec)
RETURN sp.title AS page_title,
       sp.url AS page_url,
       collect({
           section_title: sec.title,
           section_level: labels(sec)[0],
           section_path: sec.path,
           section_url: sec.url
       }) AS sections;

-- name: settlement_search_by_keyword
// 3.4. TÌM THÔNG TIN THEO TỪ KHÓA
// Use case: "Thông tin về học tiếng Anh tại Úc"
MATCH (cat:SettlementCategory)
WHERE toLower(cat.name) CONTAINS toLower($keyword)
MATCH (cat)-[:HAS_GROUP]->(tg:SettlementTaskGroup)
      -[:CONTAINS_SETTLEMENT_PAGE]->(sp:SettlementPage)
RETURN cat.name AS category,
       collect(DISTINCT {
           task_group: tg.name,
           page_title: sp.title,
           page_url: sp.url
       })[..5] AS related_info
LIMIT 5;

-- ============================================================
-- PHẦN 4: QUAN HỆ CHÉO (CROSS-RELATIONS)
-- ============================================================

-- name: visa500_study_relations
// 4.1. VISA 500 → TRƯỜNG & CHƯƠNG TRÌNH HỌC
// Use case: "Với visa 500, tôi có thể học trường nào?"
MATCH (v:Visa {subclass: "500"})
OPTIONAL MATCH (v)-[:RELEVANT_FOR_UNIVERSITY]->(u:University)
OPTIONAL MATCH (v)-[:ALLOWS_STUDY_LEVEL]->(sl:StudyLevel)
OPTIONAL MATCH (v)-[:ALLOWS_PROGRAM_LEVEL]->(pl:ProgramLevel)
RETURN v.name_visa AS visa,
       collect(DISTINCT u.name)[..10] AS universities,
       collect(DISTINCT sl.level) AS study_levels,
       count(DISTINCT pl) AS program_level_count;

-- name: visa500_related_settlement_info
// 4.2. VISA 500 → THÔNG TIN ĐỊNH CƯ LIÊN QUAN
// Use case: "Với visa du học, tôi cần biết gì về định cư?"
MATCH (v:Visa {subclass: "500"})
      -[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
MATCH (sc)-[:HAS_GROUP]->(tg:SettlementTaskGroup)
      -[:CONTAINS_SETTLEMENT_PAGE]->(sp:SettlementPage)
RETURN v.name_visa AS visa,
       sc.name AS settlement_category,
       collect(DISTINCT {
           task_group: tg.name,
           page_title: sp.title,
           page_url: sp.url
       })[..5] AS settlement_info;

-- name: visa_skilled_employment_info
// 4.3. VISA SKILLED → THÔNG TIN ĐỊNH CƯ VIỆC LÀM
// Use case: "Với visa PR, làm sao tìm việc?"
MATCH (v:Visa)
WHERE v.subclass IN ["189", "190", "191", "491", "494", "186", "187"]
MATCH (v)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
MATCH (sc)-[:HAS_GROUP]->(tg:SettlementTaskGroup)
      -[:CONTAINS_SETTLEMENT_PAGE]->(sp:SettlementPage)
WHERE toLower(sc.name) CONTAINS 'employ'
   OR toLower(sc.name) CONTAINS 'work'
   OR toLower(sc.name) CONTAINS 'job'
RETURN v.name_visa AS visa,
       v.subclass AS subclass,
       sc.name AS category,
       collect(DISTINCT {
           task_group: tg.name,
           page: sp.title,
           url: sp.url
       })[..5] AS employment_info;

-- name: university_related_settlement_info
// 4.4. TRƯỜNG → THÔNG TIN ĐỊNH CƯ
// Use case: "Học tại Melbourne thì nên biết gì về định cư?"
MATCH (u:University {name: $university_name})
      -[:HAS_RELEVANT_SETTLEMENT_INFO]->(sp:SettlementPage)
OPTIONAL MATCH (sp)-[:HAS_SETTLEMENT_SECTION]->(sec)
RETURN u.name AS university,
       collect(DISTINCT {
           page_title: sp.title,
           page_url: sp.url,
           sample_sections: collect(sec.title)[..3]
       })[..5] AS settlement_resources;

-- name: studyfield_related_settlement_info
// 4.5. NGÀNH HỌC → THÔNG TIN ĐỊNH CƯ
// Use case: "Học IT thì có thông tin gì về định cư?"
MATCH (sc:StudyCategory)
WHERE toLower(sc.name) CONTAINS toLower($study_field)
MATCH (sc)-[:RELATED_TO_SETTLEMENT_CATEGORY]->(sc2:SettlementCategory)
MATCH (sc2)-[:HAS_GROUP]->(tg:SettlementTaskGroup)
      -[:CONTAINS_SETTLEMENT_PAGE]->(sp:SettlementPage)
RETURN sc.name AS study_category,
       sc2.name AS settlement_category,
       collect(DISTINCT {
           task_group: tg.name,
           page: sp.title,
           url: sp.url
       })[..5] AS related_settlement_info;

-- ============================================================
-- PHẦN 5: TƯ VẤN TỔNG HỢP (COMPREHENSIVE)
-- ============================================================

-- name: comprehensive_pathway_it_to_pr
// 5.1. LỘ TRÌNH DU HỌC → ĐỊNH CƯ HOÀN CHỈNH
// Use case: "Tôi muốn học IT và định cư, hướng dẫn chi tiết"
// Bước 1: Tìm chương trình IT
MATCH (p:Program)-[:FOCUSES_ON]->(subj:Subject)
WHERE toLower(subj.name) CONTAINS 'computer'
   OR toLower(subj.name) CONTAINS 'information technology'
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
WITH u, p, collect({exam: e.name, score: es.value}) AS requirements
LIMIT 5
// Bước 2: Visa du học (500)
MATCH (v:Visa {subclass: "500"})
OPTIONAL MATCH (v)-[:HAS_STEP]->(s:VisaStep)
// Bước 3: Visa PR sau khi tốt nghiệp
MATCH (vpr:Visa)
WHERE vpr.subclass IN ["189", "190", "191"]
OPTIONAL MATCH (vpr)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
RETURN {
    study: {
        university: u.name,
        program: p.name,
        requirements: requirements,
        url: p.url
    },
    student_visa: {
        name: v.name_visa,
        steps: collect(DISTINCT {order: s.step_order, title: s.title})[..3]
    },
    pr_visas: collect(DISTINCT {
        name: vpr.name_visa,
        subclass: vpr.subclass,
        settlement_support: collect(DISTINCT sc.name)[..3]
    })[..3]
} AS complete_pathway;

-- name: compare_universities_full
// 5.2. SO SÁNH ĐẦY ĐỦ GIỮA CÁC TRƯỜNG
// Use case: "So sánh toàn diện giữa UNSW, Uni Melbourne, ANU"
MATCH (u:University)
WHERE u.name IN $university_list
OPTIONAL MATCH (u)-[:HAS_PROGRAMS]->(pg:ProgramGroup)
              -[:HAS_LEVEL]->(pl:ProgramLevel)
              -[:OFFERS]->(p:Program)
OPTIONAL MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
OPTIONAL MATCH (u)-[:HAS_INFO]->(ip:InfoPage)-[:HAS_SECTION]->(sec:InfoSection)
WITH u, 
     count(DISTINCT p) AS total_programs,
     collect(DISTINCT cat.name) AS categories,
     collect(DISTINCT {exam: e.name, min_score: min(es.value)}) AS min_requirements,
     collect(DISTINCT {info: sec.key, content: sec.content})[..3] AS sample_info
RETURN u.name AS university,
       total_programs,
       categories[..5] AS top_categories,
       min_requirements AS entry_requirements,
       sample_info AS additional_info
ORDER BY total_programs DESC;

-- name: ai_ready_smart_search_example
// 5.3. TÌM KIẾM THÔNG MINH (AI-Ready)
// Use case: Chatbot nhận câu hỏi tự do và query linh hoạt
// "Tôi muốn học Master, IELTS 7.0, quan tâm Business, muốn biết về định cư"
MATCH (p:Program {program_type: "Master"})
MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam {name: "IELTS"})
WHERE es.value <= 7.0
MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
WHERE toLower(cat.name) CONTAINS 'business'
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
// Thông tin visa
OPTIONAL MATCH (v:Visa {subclass: "500"})
OPTIONAL MATCH (v)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
OPTIONAL MATCH (sc)-[:HAS_GROUP]->(tg:SettlementTaskGroup)
RETURN {
    programs: collect(DISTINCT {
        university: u.name,
        program: p.name,
        ielts: es.value,
        url: p.url
    })[..5],
    visa_info: {
        student_visa: v.name_visa,
        settlement_support: collect(DISTINCT {
            category: sc.name,
            task_groups: collect(DISTINCT tg.name)[..3]
        })[..3]
    }
} AS comprehensive_result;

-- name: budget_based_search
// 5.4. TÌM KIẾM THEO NGÂN SÁCH
// Use case: "Tôi có 50,000 AUD, giới thiệu trường và chương trình phù hợp"
MATCH (u:University)-[:HAS_INFO]->(ip:InfoPage)
      -[:HAS_SECTION]->(sec:InfoSection)
WHERE sec.key CONTAINS 'Cost'
MATCH (u)-[:HAS_PROGRAMS]->(pg:ProgramGroup)
      -[:HAS_LEVEL]->(pl:ProgramLevel)
      -[:OFFERS]->(p:Program)
RETURN u.name AS university,
       collect(DISTINCT {
           cost_type: sec.key,
           cost_info: sec.content
       }) AS costs,
       count(DISTINCT p) AS available_programs,
       collect(DISTINCT p.name)[..3] AS sample_programs
LIMIT 10;

-- name: system_dashboard_overview
// 5.5. DASHBOARD THỐNG KÊ
// Use case: "Tổng quan về toàn bộ hệ thống"
MATCH (u:University)
WITH count(u) AS total_universities
MATCH (p:Program)
WITH total_universities, count(p) AS total_programs
MATCH (v:Visa)
WITH total_universities, total_programs, count(v) AS total_visas
MATCH (sp:SettlementPage)
WITH total_universities, total_programs, total_visas, count(sp) AS total_settlement_pages
MATCH (cat:StudyCategory)
WITH total_universities, total_programs, total_visas, total_settlement_pages, 
     collect(cat.name) AS all_categories
RETURN {
    statistics: {
        universities: total_universities,
        programs: total_programs,
        visas: total_visas,
        settlement_pages: total_settlement_pages,
        study_categories: size(all_categories)
    },
    top_categories: all_categories[..10]
} AS system_overview;

// ============================================================
// PHẦN 6: QUERY NÂNG CAO
// ============================================================

-- name: shortest_path_study_to_pr
// 6.1. TÌM LỘ TRÌNH TỐI ƯU (Shortest Path)
// Use case: "Con đường ngắn nhất từ du học đến PR"
MATCH path = shortestPath(
    (start:Visa {subclass: "500"})
    -[*..5]-
    (end:Visa {subclass: "189"})
)
RETURN path;

-- name: universities_with_bachelor_and_master_overlap
// 6.2. TÌM TẤT CẢ TRƯỜNG CÓ CHƯƠNG TRÌNH LIÊN QUAN
// Use case: "Trường nào có cả Bachelor và Master về Engineering?"
MATCH (u:University)-[:HAS_PROGRAMS]->(pg:ProgramGroup)
MATCH (pg)-[:HAS_LEVEL]->(pl1:ProgramLevel {name: "Bachelor"})
      -[:OFFERS]->(p1:Program)
MATCH (pg)-[:HAS_LEVEL]->(pl2:ProgramLevel {name: "Master"})
      -[:OFFERS]->(p2:Program)
WHERE (p1)-[:FOCUSES_ON]->(:Subject)<-[:FOCUSES_ON]-(p2)
   OR (p1)-[:IN_STUDY_CATEGORY]->(:StudyCategory)<-[:IN_STUDY_CATEGORY]-(p2)
RETURN DISTINCT u.name AS university,
       count(DISTINCT p1) AS bachelor_programs,
       count(DISTINCT p2) AS master_programs;

-- name: visa_settlement_connectivity_top
// 6.3. PHÂN TÍCH MẠNG QUAN HỆ
// Use case: "Visa nào có nhiều kết nối nhất với các dịch vụ định cư?"
MATCH (v:Visa)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
WITH v, count(sc) AS connection_count
ORDER BY connection_count DESC
LIMIT 10
MATCH (v)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
RETURN v.name_visa AS visa,
       v.subclass AS subclass,
       connection_count,
       collect(sc.name) AS connected_categories;

// ============================================================
// PHẦN 7: PHÂN TÍCH HỌC SINH (STUDENT ANALYSIS)
// ============================================================

-- name: programs_by_student_profile
// 7.1. TÌM CHƯƠNG TRÌNH PHÙ HỢP THEO PROFILE HỌC SINH
// Use case: "IELTS 6.5, muốn học IT, ngân sách 40k, bắt đầu tháng 7"
MATCH (p:Program)-[:STARTS_IN]->(m:Month {name: $start_month})
MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam {name: $exam_type})
WHERE es.value <= $student_score
MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
WHERE toLower(cat.name) CONTAINS toLower($interest)
   OR toLower(p.name) CONTAINS toLower($interest)
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
OPTIONAL MATCH (u)-[:HAS_INFO]->(ip:InfoPage)
              -[:HAS_SECTION]->(cost:InfoSection)
WHERE cost.key CONTAINS 'Cost'
RETURN u.name AS university,
       p.name AS program,
       p.program_type AS level,
       es.value AS required_score,
       p.starting_months AS available_starts,
       p.url AS program_url,
       collect(DISTINCT cost.content)[0] AS cost_info
ORDER BY es.value ASC
LIMIT 10;

-- name: master_recommendations_from_bachelor_field
// 7.2. GỢI Ý CHƯƠNG TRÌNH DỰA TRÊN LỘ TRÌNH HỌC TẬP
// Use case: "Tôi học Bachelor IT xong, muốn tiếp tục Master"
MATCH (bachelor:Program {program_type: "Bachelor"})
WHERE toLower(bachelor.name) CONTAINS toLower($current_field)
MATCH (bachelor)-[:FOCUSES_ON]->(subj:Subject)
MATCH (master:Program {program_type: "Master"})-[:FOCUSES_ON]->(subj)
MATCH (master)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
OPTIONAL MATCH (master)-[:HAS_REQUIRED]->(es:ExamScore)
              <-[:HAS_SCORE]-(e:Exam)
RETURN u.name AS university,
       master.name AS master_program,
       subj.name AS subject_continuity,
       collect(DISTINCT {exam: e.name, score: es.value}) AS requirements,
       master.url AS url
LIMIT 15;

-- name: entry_difficulty_ranking_by_level
// 7.3. PHÂN TÍCH ĐỘ KHÓ NHẬP HỌC (Entry Difficulty)
// Use case: "Xếp hạng trường theo độ khó nhập học"
MATCH (u:University)-[:HAS_PROGRAMS]->(pg:ProgramGroup)
      -[:HAS_LEVEL]->(pl:ProgramLevel {name: $level})
      -[:OFFERS]->(p:Program)
MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam {name: "IELTS"})
WITH u, 
     avg(es.value) AS avg_ielts,
     min(es.value) AS min_ielts,
     max(es.value) AS max_ielts,
     count(DISTINCT p) AS program_count
ORDER BY avg_ielts DESC
RETURN u.name AS university,
       round(avg_ielts * 10) / 10 AS average_ielts,
       min_ielts AS easiest_entry,
       max_ielts AS hardest_entry,
       program_count AS total_programs,
       CASE 
           WHEN avg_ielts >= 7.5 THEN "Very High"
           WHEN avg_ielts >= 7.0 THEN "High"
           WHEN avg_ielts >= 6.5 THEN "Medium"
           ELSE "Accessible"
       END AS difficulty_level
LIMIT 20;

-- name: flexible_entry_requirements_by_field_and_level
// 7.4. TÌM CHƯƠNG TRÌNH CÓ YÊU CẦU LINH HOẠT
// Use case: "Trường nào dễ nhập học nhất cho Master Business?"
MATCH (p:Program {program_type: $level})
MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
WHERE toLower(cat.name) CONTAINS toLower($field)
MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
WITH u, p, 
     collect({exam: e.name, score: es.value, plus: es.plus}) AS all_requirements,
     min(es.value) AS lowest_requirement
ORDER BY lowest_requirement ASC
RETURN u.name AS university,
       p.name AS program,
       all_requirements AS entry_requirements,
       lowest_requirement AS minimum_score,
       p.url AS url
LIMIT 10;

// ============================================================
// PHẦN 8: PHÂN TÍCH VISA CHI TIẾT (VISA DEEP DIVE)
// ============================================================

-- name: compare_two_visas
// 8.1. SO SÁNH VISA DU HỌC VÀ VISA SKILLED
// Use case: "Khác biệt giữa visa 500 và visa 189?"
MATCH (v1:Visa {subclass: $visa1})
MATCH (v2:Visa {subclass: $visa2})
OPTIONAL MATCH (v1)-[:HAS_ABOUT_INFO]->(a1:AboutInfo)
OPTIONAL MATCH (v2)-[:HAS_ABOUT_INFO]->(a2:AboutInfo)
OPTIONAL MATCH (v1)-[:HAS_ELIGIBILITY_REQUIREMENT]->(e1:EligibilityRequirement)
OPTIONAL MATCH (v2)-[:HAS_ELIGIBILITY_REQUIREMENT]->(e2:EligibilityRequirement)
RETURN {
    visa_1: {
        name: v1.name_visa,
        subclass: v1.subclass,
        type: v1.type,
        about: collect(DISTINCT a1.content)[..3],
        requirements_count: count(DISTINCT e1)
    },
    visa_2: {
        name: v2.name_visa,
        subclass: v2.subclass,
        type: v2.type,
        about: collect(DISTINCT a2.content)[..3],
        requirements_count: count(DISTINCT e2)
    }
} AS comparison;

-- name: visas_by_complexity
// 8.2. TÌM VISA THEO ĐỘ PHỨC TẠP
// Use case: "Visa nào có ít yêu cầu nhất / dễ xin nhất?"
MATCH (v:Visa)-[:HAS_ELIGIBILITY_REQUIREMENT]->(er:EligibilityRequirement)
WITH v, count(er) AS requirement_count
ORDER BY requirement_count ASC
OPTIONAL MATCH (v)-[:HAS_STEP]->(s:VisaStep)
WITH v, requirement_count, count(s) AS step_count
RETURN v.name_visa AS visa_name,
       v.subclass AS subclass,
       v.type AS visa_type,
       requirement_count AS total_requirements,
       step_count AS total_steps,
       v.url AS url,
       CASE 
           WHEN requirement_count <= 5 THEN "Simple"
           WHEN requirement_count <= 10 THEN "Moderate"
           ELSE "Complex"
       END AS complexity_level
ORDER BY requirement_count ASC
LIMIT 15;

-- name: visa_pathway_study_work_pr
// 8.3. TÌM VISA PHÙ HỢP CHO TỪNG GIAI ĐOẠN
// Use case: "Lộ trình visa từ du học → làm việc → định cư"
MATCH (student:Visa {subclass: "500"})
MATCH (work:Visa)
WHERE work.subclass IN ["485", "482", "186"]
MATCH (pr:Visa)
WHERE pr.subclass IN ["189", "190", "191"]
OPTIONAL MATCH (student)-[:HAS_ABOUT_INFO]->(a1:AboutInfo)
OPTIONAL MATCH (work)-[:HAS_ABOUT_INFO]->(a2:AboutInfo)
OPTIONAL MATCH (pr)-[:HAS_ABOUT_INFO]->(a3:AboutInfo)
RETURN {
    stage_1_study: {
        visa: student.name_visa,
        subclass: student.subclass,
        purpose: collect(DISTINCT a1.content)[0]
    },
    stage_2_work: collect(DISTINCT {
        visa: work.name_visa,
        subclass: work.subclass,
        purpose: a2.content
    })[..3],
    stage_3_pr: collect(DISTINCT {
        visa: pr.name_visa,
        subclass: pr.subclass,
        purpose: a3.content
    })[..3]
} AS visa_pathway;

-- name: visa_eligibility_groups_analysis
// 8.4. PHÂN TÍCH ĐIỀU KIỆN VISA THEO NHÓM
// Use case: "Nhóm điều kiện nào khó nhất của visa 189?"
MATCH (v:Visa {subclass: $subclass})
      -[:HAS_ELIGIBILITY_GROUP]->(eg:EligibilityGroup)
      -[:HAS_REQUIREMENT]->(er:EligibilityRequirement)
WITH eg.group_key AS group_name, 
     collect(er.content) AS requirements,
     count(er) AS requirement_count
ORDER BY requirement_count DESC
RETURN group_name,
       requirement_count,
       requirements[..3] AS sample_requirements
LIMIT 10;

-- name: integration_full_roadmap
// 9.1. LỘ TRÌNH HỘI NHẬP ĐẦY ĐỦ
// Use case: "Mới đến Úc cần làm gì theo thứ tự?"
MATCH (cat:SettlementCategory)-[:HAS_GROUP]->(tg:SettlementTaskGroup)
      -[:CONTAINS_SETTLEMENT_PAGE]->(sp:SettlementPage)
WHERE toLower(cat.name) IN ['health', 'accommodation', 'employment', 'education']
WITH cat, tg, sp
ORDER BY cat.name
RETURN cat.name AS priority_category,
       collect(DISTINCT {
           task_group: tg.name,
           pages: collect(DISTINCT sp.title)
       }) AS action_items
LIMIT 4;

// ============================================================
// PHẦN 9: ĐỊNH CƯ VÀ HỘI NHẬP (SETTLEMENT & INTEGRATION)
// ============================================================

-- name: family_support_resources
// 9.2. TÌM HỖ TRỢ CHO GIA ĐÌNH
// Use case: "Tôi có vợ và con nhỏ, cần hỗ trợ gì?"
MATCH (cat:SettlementCategory)-[:HAS_GROUP]->(tg:SettlementTaskGroup)
      -[:CONTAINS_SETTLEMENT_PAGE]->(sp:SettlementPage)
WHERE toLower(cat.name) CONTAINS 'family'
   OR toLower(tg.name) CONTAINS 'family'
   OR toLower(tg.name) CONTAINS 'child'
   OR toLower(sp.title) CONTAINS 'family'
   OR toLower(sp.title) CONTAINS 'child'
OPTIONAL MATCH (sp)-[:HAS_SETTLEMENT_SECTION]->(sec)
RETURN cat.name AS category,
       tg.name AS task_group,
       sp.title AS page_title,
       sp.url AS url,
       collect(sec.title)[..5] AS section_topics
LIMIT 10;

-- name: settlement_info_by_city
// 9.3. TÌM THÔNG TIN THEO THÀNH PHỐ (nếu có trong data)
// Use case: "Thông tin định cư tại Melbourne"
MATCH (sp:SettlementPage)
WHERE toLower(sp.title) CONTAINS toLower($city)
   OR toLower(sp.url) CONTAINS toLower($city)
OPTIONAL MATCH (sp)<-[:CONTAINS_SETTLEMENT_PAGE]-(tg:SettlementTaskGroup)
              <-[:HAS_GROUP]-(cat:SettlementCategory)
OPTIONAL MATCH (sp)-[:HAS_SETTLEMENT_SECTION]->(sec)
RETURN sp.title AS page_title,
       sp.url AS url,
       cat.name AS category,
       tg.name AS task_group,
       collect(DISTINCT sec.title)[..5] AS topics
LIMIT 10;

-- name: settlement_support_by_profession
// 9.4. MAPPING HỖ TRỢ THEO NGÀNH NGHỀ
// Use case: "Tôi làm IT, cần hỗ trợ gì khi mới đến?"
MATCH (sc:StudyCategory)
WHERE toLower(sc.name) CONTAINS toLower($profession)
MATCH (sc)-[:RELATED_TO_SETTLEMENT_CATEGORY]->(sc2:SettlementCategory)
      -[:HAS_GROUP]->(tg:SettlementTaskGroup)
      -[:CONTAINS_SETTLEMENT_PAGE]->(sp:SettlementPage)
RETURN sc.name AS your_field,
       sc2.name AS settlement_category,
       collect(DISTINCT {
           task: tg.name,
           resource: sp.title,
           url: sp.url
       })[..5] AS relevant_resources;

// ============================================================
// PHẦN 10: QUAN HỆ ĐA CHIỀU (MULTI-DIMENSIONAL)
// ============================================================

-- name: university_complete_profile
// 10.1. TÌM TẤT CẢ KẾT NỐI CỦA MỘT TRƯỜNG
// Use case: "Tất cả thông tin liên quan đến UNSW"
MATCH (u:University {name: $university_name})
OPTIONAL MATCH (u)-[:HAS_PROGRAMS]->(pg:ProgramGroup)
              -[:HAS_LEVEL]->(pl:ProgramLevel)
              -[:OFFERS]->(p:Program)
OPTIONAL MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
OPTIONAL MATCH (p)-[:FOCUSES_ON]->(subj:Subject)
OPTIONAL MATCH (u)-[:HAS_INFO]->(ip:InfoPage)
              -[:HAS_SECTION]->(sec:InfoSection)
OPTIONAL MATCH (u)-[:HAS_RELEVANT_SETTLEMENT_INFO]->(sp:SettlementPage)
WITH u,
     count(DISTINCT p) AS total_programs,
     collect(DISTINCT cat.name) AS categories,
     collect(DISTINCT subj.name) AS subjects,
     collect(DISTINCT sec.key) AS info_sections,
     count(DISTINCT sp) AS settlement_resources
RETURN {
    university: u.name,
    programs: {
        total: total_programs,
        categories: categories[..10],
        subjects: subjects[..10]
    },
    information: {
        sections: info_sections,
        settlement_links: settlement_resources
    }
} AS complete_profile;

-- name: visa_ecosystem_overview
// 10.2. PHÂN TÍCH MỐI QUAN HỆ VISA-STUDY-SETTLEMENT
// Use case: "Visa 500 kết nối với những gì?"
MATCH (v:Visa {subclass: $subclass})
OPTIONAL MATCH (v)-[:RELEVANT_FOR_UNIVERSITY]->(u:University)
OPTIONAL MATCH (v)-[:ALLOWS_STUDY_LEVEL]->(sl:StudyLevel)
OPTIONAL MATCH (v)-[:ALLOWS_PROGRAM_LEVEL]->(pl:ProgramLevel)
OPTIONAL MATCH (v)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
WITH v,
     count(DISTINCT u) AS uni_count,
     collect(DISTINCT sl.level) AS study_levels,
     count(DISTINCT pl) AS program_levels,
     collect(DISTINCT sc.name) AS settlement_cats
RETURN {
    visa: v.name_visa,
    connections: {
        universities: uni_count,
        study_levels: study_levels,
        program_levels: program_levels,
        settlement_support: settlement_cats
    }
} AS visa_ecosystem;

-- name: complete_program_info
// 10.3. TÌM CHƯƠNG TRÌNH VỚI ĐẦY ĐỦ THÔNG TIN
// Use case: "Tôi muốn biết mọi thứ về chương trình X"
MATCH (p:Program {name: $program_name})
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
OPTIONAL MATCH (p)-[:STUDY_LEVEL]->(sl:StudyLevel)
OPTIONAL MATCH (p)-[:STUDY_MODE]->(sm:StudyMode)
OPTIONAL MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
OPTIONAL MATCH (p)-[:FOCUSES_ON]->(subj:Subject)
OPTIONAL MATCH (p)-[:AWARDS]->(deg:Degree)
OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
OPTIONAL MATCH (p)-[:STARTS_IN]->(m:Month)
OPTIONAL MATCH (p)-[:HAS_MAJOR]->(maj:Major)
OPTIONAL MATCH (p)-[:HAS_COMPONENT]->(comp:Program)
OPTIONAL MATCH (cat)-[:RELATED_TO_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
RETURN {
    basic_info: {
        university: u.name,
        program: p.name,
        type: p.program_type,
        url: p.url,
        description: p.description
    },
    academic_details: {
        study_level: sl.level,
        study_mode: sm.mode,
        category: cat.name,
        subject: subj.name,
        degree: deg.code
    },
    requirements: collect(DISTINCT {
        exam: e.name,
        score: es.value,
        plus_required: es.plus
    }),
    schedule: {
        starting_months: p.starting_months,
        available_intakes: collect(DISTINCT m.name)
    },
    specializations: collect(DISTINCT maj.name),
    components: collect(DISTINCT {
        name: comp.name,
        level: comp.program_type
    }),
    settlement_support: collect(DISTINCT sc.name)[..5]
} AS complete_program_info;

// ============================================================
// PHẦN 11: THỐNG KÊ VÀ BÁO CÁO (STATISTICS & REPORTS)
// ============================================================

-- name: university_statistics_report
// 11.1. BÁO CÁO THỐNG KÊ THEO TRƯỜNG
MATCH (u:University)
OPTIONAL MATCH (u)-[:HAS_PROGRAMS]->(pg:ProgramGroup)
              -[:HAS_LEVEL]->(pl:ProgramLevel)
              -[:OFFERS]->(p:Program)
OPTIONAL MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam {name: "IELTS"})
WITH u,
     count(DISTINCT p) AS total_programs,
     count(DISTINCT CASE WHEN p.program_type = 'Bachelor' THEN p END) AS bachelor_count,
     count(DISTINCT CASE WHEN p.program_type = 'Master' THEN p END) AS master_count,
     count(DISTINCT CASE WHEN p.program_type = 'Doctor' THEN p END) AS doctor_count,
     collect(DISTINCT cat.name) AS categories,
     avg(es.value) AS avg_ielts
RETURN u.name AS university,
       total_programs,
       bachelor_count,
       master_count,
       doctor_count,
       size(categories) AS category_diversity,
       round(avg_ielts * 10) / 10 AS average_ielts_requirement
ORDER BY total_programs DESC;

-- name: program_distribution_by_category
// 11.2. PHÂN TÍCH PHÂN BỐ CHƯƠNG TRÌNH
MATCH (cat:StudyCategory)<-[:IN_STUDY_CATEGORY]-(p:Program)
WITH cat, count(p) AS program_count
ORDER BY program_count DESC
LIMIT 15
MATCH (cat)<-[:IN_STUDY_CATEGORY]-(p:Program)
      <-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
RETURN cat.name AS category,
       program_count,
       count(DISTINCT u) AS universities_offering,
       count(DISTINCT CASE WHEN p.program_type = 'Bachelor' THEN p END) AS bachelor_programs,
       count(DISTINCT CASE WHEN p.program_type = 'Master' THEN p END) AS master_programs,
       count(DISTINCT CASE WHEN p.program_type = 'Doctor' THEN p END) AS doctor_programs
ORDER BY program_count DESC;

-- name: ielts_stats_by_category
// 11.3. THỐNG KÊ YÊU CẦU IELTS THEO NGÀNH
MATCH (cat:StudyCategory)<-[:IN_STUDY_CATEGORY]-(p:Program)
MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam {name: "IELTS"})
WITH cat,
     avg(es.value) AS avg_ielts,
     min(es.value) AS min_ielts,
     max(es.value) AS max_ielts,
     count(p) AS program_count
WHERE program_count >= 5
RETURN cat.name AS category,
       round(avg_ielts * 10) / 10 AS average_ielts,
       min_ielts AS minimum_ielts,
       max_ielts AS maximum_ielts,
       program_count AS total_programs
ORDER BY avg_ielts DESC
LIMIT 20;

-- name: intake_popularity_report
// 11.4. BÁO CÁO KỲ NHẬP HỌC PHỔ BIẾN
MATCH (m:Month)<-[:STARTS_IN]-(p:Program)
WITH m.name AS month,
     count(p) AS program_count,
     collect(DISTINCT p.program_type) AS levels
ORDER BY 
    CASE month
        WHEN 'Feb' THEN 1
        WHEN 'Mar' THEN 2
        WHEN 'Apr' THEN 3
        WHEN 'May' THEN 4
        WHEN 'Jun' THEN 5
        WHEN 'Jul' THEN 6
        WHEN 'Aug' THEN 7
        WHEN 'Sep' THEN 8
        WHEN 'Oct' THEN 9
        WHEN 'Nov' THEN 10
        WHEN 'Dec' THEN 11
        WHEN 'Jan' THEN 12
    END
RETURN month,
       program_count,
       levels AS available_levels;

-- name: visa_coverage_analysis
// 11.5. PHÂN TÍCH ĐỘ PHỦ CỦA VISA
MATCH (v:Visa)
OPTIONAL MATCH (v)-[:HAS_ABOUT_INFO]->(a:AboutInfo)
OPTIONAL MATCH (v)-[:HAS_ELIGIBILITY_REQUIREMENT]->(er:EligibilityRequirement)
OPTIONAL MATCH (v)-[:HAS_STEP]->(s:VisaStep)
OPTIONAL MATCH (v)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
OPTIONAL MATCH (v)-[:RELEVANT_FOR_UNIVERSITY]->(u:University)
WITH v,
     count(DISTINCT a) AS about_count,
     count(DISTINCT er) AS requirement_count,
     count(DISTINCT s) AS step_count,
     count(DISTINCT sc) AS settlement_count,
     count(DISTINCT u) AS university_count
RETURN v.name_visa AS visa,
       v.subclass AS subclass,
       v.type AS type,
       about_count AS information_sections,
       requirement_count AS eligibility_criteria,
       step_count AS application_steps,
       settlement_count AS settlement_resources,
       university_count AS linked_universities
ORDER BY (about_count + requirement_count + step_count + settlement_count) DESC;

// ============================================================
// PHẦN 12: QUERY THỰC CHIẾN CHO CHATBOT
// ============================================================

-- name: open_question_aggregate
// 12.1. QUERY TỔNG HỢP CHO CÂU HỎI MỞ
// Use case: "Tôi muốn học Master IT, IELTS 7.0, có visa gì?"
MATCH (p:Program {program_type: $level})
WHERE toLower(p.name) CONTAINS toLower($keyword)
   OR exists((p)-[:IN_STUDY_CATEGORY]->(:StudyCategory))
MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam {name: $exam})
WHERE es.value <= $score
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
WITH u, p, es, 
     [(v:Visa)-[:ALLOWS_PROGRAM_LEVEL]->(pl) | v.name_visa][0] AS student_visa
OPTIONAL MATCH (cat:StudyCategory)<-[:IN_STUDY_CATEGORY]-(p)
              -[:RELATED_TO_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
RETURN {
    recommendation: {
        university: u.name,
        program: p.name,
        required_score: es.value,
        url: p.url
    },
    visa_info: {
        visa_name: student_visa,
        subclass: "500"
    },
    settlement_support: collect(DISTINCT sc.name)[..3]
} AS complete_answer
LIMIT 5;

-- name: fallback_search_programs_by_keyword
// 12.2. FALLBACK QUERY (Khi không tìm thấy kết quả chính xác)
MATCH (p:Program)
WHERE toLower(p.name) CONTAINS toLower($keyword)
   OR toLower(p.description) CONTAINS toLower($keyword)
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
OPTIONAL MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
OPTIONAL MATCH (p)-[:FOCUSES_ON]->(subj:Subject)
RETURN u.name AS university,
       p.name AS program,
        p.program_type AS level,
       cat.name AS category,
       subj.name AS subject,
       p.url AS url
LIMIT 10;

-- name: intent_classification_query
// 12.3. INTENT CLASSIFICATION QUERY
// Use case: "Phát hiện ý định người dùng để route đúng query"
MATCH (v:Visa)
WHERE toLower(v.name_visa) CONTAINS toLower($user_query)
   OR toString(v.subclass) CONTAINS $user_query
RETURN 'visa' AS intent, 
       collect(v.name_visa)[0] AS detected_entity
UNION
MATCH (u:University)
WHERE toLower(u.name) CONTAINS toLower($user_query)
RETURN 'university' AS intent,
       u.name AS detected_entity
UNION
MATCH (cat:StudyCategory)
WHERE toLower(cat.name) CONTAINS toLower($user_query)
RETURN 'study_category' AS intent,
       cat.name AS detected_entity
UNION
MATCH (sc:SettlementCategory)
WHERE toLower(sc.name) CONTAINS toLower($user_query)
RETURN 'settlement' AS intent,
       sc.name AS detected_entity
LIMIT 1;

-- name: context_aware_more_programs
// 12.4. CONTEXT-AWARE QUERY (Dựa trên lịch sử hội thoại)
MATCH (u:University {name: $previous_university})
      -[:HAS_PROGRAMS]->(pg:ProgramGroup)
      -[:HAS_LEVEL]->(pl:ProgramLevel {name: $previous_level})
      -[:OFFERS]->(p:Program)
WHERE NOT p.name = $previous_program
OPTIONAL MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
RETURN p.name AS program,
       p.program_type AS level,
       cat.name AS category,
       collect({exam: e.name, score: es.value}) AS requirements,
       p.url AS url
LIMIT 5;

-- name: recommendation_engine_query
// 12.5. RECOMMENDATION ENGINE QUERY
// Use case: "Gợi ý thông minh dựa trên profile"
MATCH (p:Program {program_type: $user_level})
MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
WHERE cat.name IN $user_interests
MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
WHERE es.value <= $user_max_score
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
RETURN u.name AS university,
       p.name AS program,
       p.program_type AS level,
       collect(DISTINCT {exam: e.name, score: es.value, plus: es.plus}) AS requirements,
       p.url AS url
ORDER BY min(es.value) ASC
LIMIT 10;


// ============================================================
// PHẦN 13: OPTIMIZATION QUERIES (Tối ưu hiệu suất)
// ============================================================

-- name: visa_indexed_lookup_by_subclass
// 13.1. INDEXED LOOKUP (Sử dụng index hiệu quả)
// Use case: "Tìm nhanh theo subclass visa"
MATCH (v:Visa)
USING INDEX v:Visa(subclass)
WHERE v.subclass = $subclass
RETURN v;

-- name: batch_universities_program_counts
// 13.2. BATCH PROCESSING QUERY
// Use case: "Lấy thông tin nhiều trường cùng lúc"
UNWIND $university_names AS uni_name
MATCH (u:University {name: uni_name})
OPTIONAL MATCH (u)-[:HAS_PROGRAMS]->(pg:ProgramGroup)
              -[:HAS_LEVEL]->(pl:ProgramLevel)
              -[:OFFERS]->(p:Program)
WITH u, count(p) AS program_count
RETURN u.name AS university,
       program_count
ORDER BY program_count DESC;

-- name: program_existence_for_university
// 13.3. EXISTENCE CHECK (Kiểm tra tồn tại nhanh)
// Use case: "Trường có chương trình này không?"
MATCH (u:University {name: $university_name})
RETURN exists((u)-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->()
              -[:OFFERS]->(:Program {name: $program_name})) 
       AS program_exists;

-- name: count_programs_by_university
// 13.4. COUNT OPTIMIZATION
// Use case: "Đếm nhanh số lượng"
MATCH (u:University {name: $university_name})
      -[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->()-[:OFFERS]->(p:Program)
RETURN count(p) AS total_programs;

-- name: universities_program_count_top20
// 13.5. EFFICIENT AGGREGATION
// Use case: "Thống kê nhanh theo trường"
MATCH (u:University)
OPTIONAL MATCH (u)-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->()-[:OFFERS]->(p:Program)
WITH u, count(p) AS program_count
WHERE program_count > 0
RETURN u.name AS university,
       program_count
ORDER BY program_count DESC
LIMIT 20;

-- name: apoc_batch_fill_program_urls
// 13.6. USING APOC FOR PERFORMANCE (nếu có APOC plugin)
// Use case: "Batch update với APOC"
CALL apoc.periodic.iterate(
  "MATCH (p:Program) WHERE p.url IS NULL RETURN p",
  "SET p.url = 'https://example.com'",
  {batchSize: 1000, parallel: false}
);

-- name: profile_slow_queries_example
// 13.7. PROFILE SLOW QUERIES
// Use case: "Tìm và tối ưu query chậm"
PROFILE
MATCH (u:University)-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->()-[:OFFERS]->(p:Program)
MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
WHERE es.value >= 6.5
RETURN u.name, count(p)
ORDER BY count(p) DESC;

-- name: limit_early_programs_by_university
// 13.8. LIMIT EARLY (Giảm tải xử lý)
MATCH (u:University)
WITH u LIMIT 10
MATCH (u)-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->()-[:OFFERS]->(p:Program)
RETURN u.name, count(p);

-- name: avoid_cartesian_example
// 13.9. AVOID CARTESIAN PRODUCTS
// ❌ BAD: MATCH (u:University), (v:Visa)
// ✅ GOOD:
MATCH (u:University)
MATCH (v:Visa)-[:RELEVANT_FOR_UNIVERSITY]->(u)
RETURN u.name, v.name_visa;

-- name: optional_match_scores_by_level
// 13.10. USE OPTIONAL MATCH WISELY
MATCH (p:Program)
WHERE p.program_type = $level
OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)
RETURN p.name, collect(es.value) AS scores
LIMIT 20;

// ============================================================
// PHẦN 14: VALIDATION QUERIES (Kiểm tra dữ liệu)
// ============================================================

-- name: programs_without_requirements
// 14.1. KIỂM TRA DATA INTEGRITY
MATCH (p:Program)
WHERE NOT exists((p)-[:HAS_REQUIRED]->())
RETURN p.name AS program_without_requirements,
       p.university_name AS university,
       p.url AS url
LIMIT 20;

-- name: orphan_settlement_pages
// 14.2. TÌM ORPHAN NODES
MATCH (sp:SettlementPage)
WHERE NOT exists((sp)<-[:CONTAINS_SETTLEMENT_PAGE]-())
RETURN sp.title AS orphan_page,
       sp.url AS url
LIMIT 10;

-- name: duplicate_universities
// 14.3. KIỂM TRA DUPLICATE DATA
MATCH (u:University)
WITH u.name AS uni_name, count(*) AS cnt
WHERE cnt > 1
RETURN uni_name, cnt;

-- name: incomplete_program_relationships
// 14.4. VALIDATE RELATIONSHIPS
MATCH (p:Program)
WHERE NOT exists((p)<-[:OFFERS]-())
   OR NOT exists((p)-[:STUDY_LEVEL]->())
RETURN p.name AS incomplete_program,
       p.uid AS uid,
       exists((p)<-[:OFFERS]-()) AS has_university,
       exists((p)-[:STUDY_LEVEL]->()) AS has_level
LIMIT 20;

-- name: program_null_fields
// 14.5. CHECK NULL VALUES
MATCH (p:Program)
WHERE p.name IS NULL 
   OR p.university_name IS NULL
   OR p.program_type IS NULL
RETURN p.uid AS program_id,
       p.name IS NULL AS missing_name,
       p.university_name IS NULL AS missing_university,
       p.program_type IS NULL AS missing_type
LIMIT 20;

-- name: incomplete_visa_info
// 14.6. VALIDATE VISA STRUCTURE
MATCH (v:Visa)
WHERE NOT exists((v)-[:HAS_ABOUT_INFO]->())
   OR NOT exists((v)-[:HAS_ELIGIBILITY_REQUIREMENT]->())
   OR NOT exists((v)-[:HAS_STEP]->())
RETURN v.name_visa AS incomplete_visa,
       v.subclass AS subclass,
       exists((v)-[:HAS_ABOUT_INFO]->()) AS has_about,
       exists((v)-[:HAS_ELIGIBILITY_REQUIREMENT]->()) AS has_eligibility,
       exists((v)-[:HAS_STEP]->()) AS has_steps
LIMIT 10;

-- name: visa500_study_links_exists
// 14.7. CHECK CROSS-RELATIONS
MATCH (v:Visa {subclass: "500"})
RETURN v.name_visa AS visa,
       exists((v)-[:RELEVANT_FOR_UNIVERSITY]->()) AS linked_to_universities,
       exists((v)-[:ALLOWS_STUDY_LEVEL]->()) AS linked_to_study_levels,
       exists((v)-[:ALLOWS_PROGRAM_LEVEL]->()) AS linked_to_program_levels,
       exists((v)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->()) AS linked_to_settlement;

-- name: abnormal_exam_scores
// 14.8. VALIDATE EXAM SCORES
MATCH (es:ExamScore)
WHERE es.value < 0 OR es.value > 9
RETURN es.exam AS exam_name,
       es.value AS invalid_score,
       es.raw AS raw_value
LIMIT 20;

-- name: settlement_categories_without_groups
// 14.9. CHECK SETTLEMENT HIERARCHY
MATCH (cat:SettlementCategory)
WHERE NOT exists((cat)-[:HAS_GROUP]->())
RETURN cat.name AS category_without_groups
LIMIT 10;

-- name: broken_urls_in_entities
// 14.10. FIND BROKEN URLS
MATCH (n)
WHERE (n:Program OR n:Visa OR n:SettlementPage)
  AND (n.url IS NULL OR n.url = '' OR NOT n.url STARTS WITH 'http')
RETURN labels(n)[0] AS node_type,
       CASE 
         WHEN n:Program THEN n.name
         WHEN n:Visa THEN n.name_visa
         WHEN n:SettlementPage THEN n.title
       END AS name,
       n.url AS invalid_url
LIMIT 20;

// ============================================================
// PHẦN 15: EXPORT & REPORTING QUERIES
// ============================================================

-- name: export_programs_by_university
// 15.1. EXPORT DANH SÁCH ĐẦY ĐỦ
MATCH (u:University {name: $university_name})
      -[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->(pl:ProgramLevel)
      -[:OFFERS]->(p:Program)
OPTIONAL MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
RETURN u.name AS University,
       pl.name AS Level,
       p.name AS Program,
       cat.name AS Category,
       p.starting_months AS StartingMonths,
       collect(DISTINCT e.name + ': ' + toString(es.value)) AS Requirements,
       p.url AS URL
ORDER BY pl.name, p.name;

-- name: system_summary_report
// 15.2. SUMMARY REPORT
MATCH (u:University)
WITH count(u) AS uni_count
MATCH (p:Program)
WITH uni_count, count(p) AS prog_count
MATCH (v:Visa)
WITH uni_count, prog_count, count(v) AS visa_count
MATCH (sp:SettlementPage)
WITH uni_count, prog_count, visa_count, count(sp) AS settlement_count
MATCH (cat:StudyCategory)
RETURN {
    universities: uni_count,
    programs: prog_count,
    visas: visa_count,
    settlement_pages: settlement_count,
    study_categories: count(cat),
    generated_at: toString(datetime())
} AS system_summary;

-- name: export_all_visa_info
// 15.3. EXPORT VISA INFORMATION
MATCH (v:Visa)
OPTIONAL MATCH (v)-[:HAS_ABOUT_INFO]->(a:AboutInfo)
OPTIONAL MATCH (v)-[:HAS_ELIGIBILITY_REQUIREMENT]->(er:EligibilityRequirement)
OPTIONAL MATCH (v)-[:HAS_STEP]->(s:VisaStep)
RETURN v.name_visa AS VisaName,
       v.subclass AS Subclass,
       v.type AS Type,
       v.url AS URL,
       collect(DISTINCT a.field + ': ' + a.content)[..3] AS AboutInfo,
       count(DISTINCT er) AS TotalRequirements,
       count(DISTINCT s) AS TotalSteps
ORDER BY v.subclass;

-- name: export_settlement_structure
// 15.4. EXPORT SETTLEMENT STRUCTURE
MATCH (cat:SettlementCategory)-[:HAS_GROUP]->(tg:SettlementTaskGroup)
      -[:CONTAINS_SETTLEMENT_PAGE]->(sp:SettlementPage)
RETURN cat.name AS Category,
       tg.name AS TaskGroup,
       sp.title AS PageTitle,
       sp.url AS URL
ORDER BY cat.name, tg.name, sp.title;

-- name: export_university_profiles
// 15.5. EXPORT UNIVERSITY PROFILES
MATCH (u:University)
OPTIONAL MATCH (u)-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->(pl:ProgramLevel)
              -[:OFFERS]->(p:Program)
OPTIONAL MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
OPTIONAL MATCH (u)-[:HAS_INFO]->()-[:HAS_SECTION]->(sec:InfoSection)
WITH u,
     count(DISTINCT p) AS total_programs,
     collect(DISTINCT cat.name) AS categories,
     collect(DISTINCT sec.key) AS info_sections
RETURN u.name AS University,
       total_programs AS TotalPrograms,
       categories[..10] AS TopCategories,
       info_sections AS AvailableInfo
ORDER BY total_programs DESC;

-- name: export_student_visa_cross_relations
// 15.6. EXPORT CROSS-RELATIONS MAPPING
MATCH (v:Visa {subclass: "500"})
OPTIONAL MATCH (v)-[:RELEVANT_FOR_UNIVERSITY]->(u:University)
OPTIONAL MATCH (v)-[:ALLOWS_STUDY_LEVEL]->(sl:StudyLevel)
OPTIONAL MATCH (v)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
RETURN v.name_visa AS StudentVisa,
       collect(DISTINCT u.name) AS LinkedUniversities,
       collect(DISTINCT sl.level) AS AllowedStudyLevels,
       collect(DISTINCT sc.name) AS SettlementSupport;

-- name: export_statistics_by_category
// 15.7. EXPORT STATISTICS BY CATEGORY
MATCH (cat:StudyCategory)<-[:IN_STUDY_CATEGORY]-(p:Program)
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
WITH cat.name AS Category,
     count(DISTINCT p) AS ProgramCount,
     count(DISTINCT u) AS UniversityCount,
     collect(DISTINCT pl.name) AS Levels
RETURN Category,
       ProgramCount,
       UniversityCount,
       Levels
ORDER BY ProgramCount DESC;

-- name: export_requirements_matrix
// 15.8. EXPORT REQUIREMENTS MATRIX
MATCH (e:Exam)<-[:HAS_SCORE]-(es:ExamScore)<-[:HAS_REQUIRED]-(p:Program)
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
WITH u.name AS University,
     p.name AS Program,
     e.name AS Exam,
     min(es.value) AS MinScore,
     max(es.value) AS MaxScore
RETURN University,
       Program,
       collect({
           exam: Exam,
           min: MinScore,
           max: MaxScore
       }) AS Requirements
ORDER BY University, Program
LIMIT 100;

-- name: export_timeline_data
// 15.9. EXPORT TIMELINE DATA
MATCH (m:Month)<-[:STARTS_IN]-(p:Program)
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
RETURN m.name AS Month,
       count(DISTINCT p) AS ProgramsAvailable,
       collect(DISTINCT u.name)[..5] AS SampleUniversities,
       collect(DISTINCT pl.name) AS AvailableLevels
ORDER BY 
    CASE m.name
        WHEN 'Jan' THEN 1 WHEN 'Feb' THEN 2 WHEN 'Mar' THEN 3
        WHEN 'Apr' THEN 4 WHEN 'May' THEN 5 WHEN 'Jun' THEN 6
        WHEN 'Jul' THEN 7 WHEN 'Aug' THEN 8 WHEN 'Sep' THEN 9
        WHEN 'Oct' THEN 10 WHEN 'Nov' THEN 11 WHEN 'Dec' THEN 12
    END;

-- name: export_graph_structure_sample
// 15.10. EXPORT COMPLETE GRAPH STRUCTURE (Small subset)
MATCH path = (u:University)-[*1..3]-(related)
WHERE u.name = $sample_university
RETURN path
LIMIT 100;

-- name: apoc_export_programs_csv
// 15.11. EXPORT TO CSV FORMAT (Using APOC)
CALL apoc.export.csv.query(
    "MATCH (u:University)-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->()-[:OFFERS]->(p:Program)
     RETURN u.name AS University, p.name AS Program, p.url AS URL",
    "programs_export.csv",
    {}
);

-- name: apoc_export_university_json
// 15.12. EXPORT JSON FORMAT
MATCH (u:University {name: $university_name})
OPTIONAL MATCH (u)-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->(pl:ProgramLevel)
              -[:OFFERS]->(p:Program)
OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
RETURN {
    university: u.name,
    programs: collect(DISTINCT {
        name: p.name,
        level: pl.name,
        url: p.url,
        requirements: collect({
            exam: e.name,
            score: es.value
        })
    })
} AS json_export;

// ============================================================
// PHẦN 16: TIME-BASED & PLANNING QUERIES
// ============================================================

-- name: timeline_preparation_plan
// 16.1. KẾ HOẠCH THEO TIMELINE
MATCH (p:Program)-[:STARTS_IN]->(m:Month {name: $target_month})
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
MATCH (v:Visa {subclass: "500"})-[:HAS_STEP]->(s:VisaStep)
OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
RETURN {
    timeline: {
        target_start: $target_month,
        months_to_prepare: $months_until
    },
    programs_available: collect(DISTINCT {
        university: u.name,
        program: p.name,
        url: p.url
    })[..5],
    preparation_steps: [
        {
            deadline: "Now - Month " + toString($months_until - 4),
            action: "Prepare English exam",
            required_scores: collect(DISTINCT {exam: e.name, score: es.value})
        },
        {
            deadline: "Month " + toString($months_until - 3),
            action: "Submit applications to universities"
        },
        {
            deadline: "Month " + toString($months_until - 2),
            action: "Apply for student visa (500)",
            steps: collect(DISTINCT {order: s.step_order, title: s.title})[..3]
        }
    ]
} AS preparation_plan
LIMIT 1;

-- name: programs_open_in_upcoming_months
// 16.2. LỌC THEO HẠN DEADLINE
MATCH (p:Program)-[:STARTS_IN]->(m:Month)
WHERE m.name IN $upcoming_months
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
RETURN u.name AS university,
       p.name AS program,
       p.program_type AS level,
       collect(DISTINCT m.name) AS intakes,
       p.url AS apply_url,
       "Apply now - deadline approaching!" AS urgency
ORDER BY size(collect(DISTINCT m.name)) DESC
LIMIT 15;

-- name: programs_open_in_upcoming_months_with_field
// 16.2b. Chương trình còn nhận trong N tháng tới + lọc ngành (IT, Business,...)
MATCH (p:Program)-[:STARTS_IN]->(m:Month)
WHERE m.name IN $upcoming_months
OPTIONAL MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
OPTIONAL MATCH (p)-[:FOCUSES_ON]->(subj:Subject)
WITH p, m, cat, subj,
     toLower($interest) AS kw
WHERE kw IS NULL OR kw = "" 
   OR toLower(p.name) CONTAINS kw
   OR toLower(cat.name) CONTAINS kw
   OR toLower(subj.name) CONTAINS kw
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
RETURN u.name AS university,
       p.name AS program,
       p.program_type AS level,
       collect(DISTINCT m.name) AS intakes,
       p.url AS apply_url,
       "Apply now - deadline approaching!" AS urgency
ORDER BY size(collect(DISTINCT m.name)) DESC
LIMIT 20;

-- name: long_term_bachelor_master_pr_pathway
// 16.3. LỘ TRÌNH DÀI HẠN (3-5 NĂM)
MATCH (bachelor:Program {program_type: "Bachelor"})
WHERE toLower(bachelor.name) CONTAINS toLower($field)
MATCH (bachelor)-[:FOCUSES_ON]->(subj:Subject)
MATCH (master:Program {program_type: "Master"})-[:FOCUSES_ON]->(subj)
MATCH (bachelor)<-[:OFFERS]-(pl1:ProgramLevel)
      <-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
MATCH (master)<-[:OFFERS]-(pl2:ProgramLevel)
      <-[:HAS_LEVEL]-(pg)
MATCH (visa_student:Visa {subclass: "500"})
MATCH (visa_graduate:Visa {subclass: "485"})
MATCH (visa_pr:Visa)
WHERE visa_pr.subclass IN ["189", "190"]
RETURN {
    year_1_to_3: {
        stage: "Bachelor Study",
        program: bachelor.name,
        university: u.name,
        visa: visa_student.name_visa,
        url: bachelor.url
    },
    year_4_to_5: {
        stage: "Master Study",
        program: master.name,
        university: u.name,
        visa: visa_student.name_visa,
        url: master.url
    },
    year_5_plus: {
        stage: "Work & Permanent Residency",
        visa_options: collect(DISTINCT {name: visa_pr.name_visa, subclass: visa_pr.subclass}),
        graduate_visa: {name: visa_graduate.name_visa, duration: "2-4 years work rights"}
    },
    subject_continuity: subj.name
} AS five_year_pathway
LIMIT 3;

// ============================================================
// PHẦN 17: FINANCIAL ANALYSIS QUERIES
// ============================================================

-- name: university_cost_estimation_by_level
// 17.1. PHÂN TÍCH CHI PHÍ TỔNG HỢP
MATCH (u:University {name: $university_name})
      -[:HAS_INFO]->(ip:InfoPage)
      -[:HAS_SECTION]->(cost:InfoSection)
WHERE cost.key CONTAINS 'Cost'
WITH u, collect({type: cost.key, amount: cost.content}) AS all_costs
MATCH (u)-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->(pl:ProgramLevel {name: $level})
      -[:OFFERS]->(p:Program)
WITH u, all_costs, avg(CASE 
    WHEN p.description CONTAINS '$' 
    THEN toFloat(substring(p.description, apoc.text.indexOf(p.description, '$') + 1, 5))
    ELSE 0 
END) AS estimated_tuition
RETURN {
    university: u.name,
    estimated_costs: {
        tuition_per_year: coalesce(estimated_tuition, 25000),
        living_costs: all_costs,
        total_estimate_3_years: coalesce(estimated_tuition * 3, 75000) + 60000
    }
} AS cost_breakdown;

-- name: compare_costs_across_universities
// 17.2. SO SÁNH CHI PHÍ GIỮA CÁC TRƯỜNG
MATCH (p:Program {program_type: $level})
MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
WHERE toLower(cat.name) CONTAINS toLower($field)
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
OPTIONAL MATCH (u)-[:HAS_INFO]->()-[:HAS_SECTION]->(cost:InfoSection)
WHERE cost.key = 'Cost Accommodation'
WITH u, p, cost.content AS accommodation_cost
ORDER BY accommodation_cost ASC
RETURN u.name AS university,
       p.name AS program,
       accommodation_cost AS living_cost_info,
       p.url AS url,
       CASE WHEN accommodation_cost IS NOT NULL THEN "Cost info available"
            ELSE "Contact university for costs" END AS cost_status
LIMIT 10;

-- name: programs_with_scholarships
// 17.3. TÌM HỌC BỔNG (nếu có trong description)
MATCH (p:Program)
WHERE toLower(p.description) CONTAINS 'scholarship'
   OR toLower(p.description) CONTAINS 'funding'
   OR toLower(p.description) CONTAINS 'financial aid'
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)
      <-[:HAS_PROGRAMS]-(u:University)
RETURN u.name AS university,
       p.name AS program,
       p.program_type AS level,
       p.description AS scholarship_info,
       p.url AS url
LIMIT 15;

// ============================================================
// PHẦN 18: GEOGRAPHIC & LOCATION QUERIES
// ============================================================

-- name: universities_by_city_with_local_settlement
// 18.1. TÌM TRƯỜNG THEO KHU VỰC (dựa vào tên)
MATCH (u:University)
WHERE toLower(u.name) CONTAINS toLower($city)
OPTIONAL MATCH (u)-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->()-[:OFFERS]->(p:Program)
OPTIONAL MATCH (u)-[:HAS_RELEVANT_SETTLEMENT_INFO]->(sp:SettlementPage)
WHERE toLower(sp.title) CONTAINS toLower($city)
   OR toLower(sp.url) CONTAINS toLower($city)
RETURN {
    university: u.name,
    location: $city,
    programs_available: count(DISTINCT p),
    local_settlement_info: collect(DISTINCT {title: sp.title, url: sp.url})[..3]
} AS location_based_info
ORDER BY count(DISTINCT p) DESC
LIMIT 10;

-- name: universities_by_state_distribution
// 18.2. BẢN ĐỒ CÁC TRƯỜNG (Geographic Distribution)
MATCH (u:University)
WITH u,
     CASE 
         WHEN u.name CONTAINS 'Sydney' OR u.name CONTAINS 'NSW' THEN 'New South Wales'
         WHEN u.name CONTAINS 'Melbourne' OR u.name CONTAINS 'Victoria' THEN 'Victoria'
         WHEN u.name CONTAINS 'Queensland' OR u.name CONTAINS 'Brisbane' THEN 'Queensland'
         WHEN u.name CONTAINS 'Adelaide' OR u.name CONTAINS 'South Australia' THEN 'South Australia'
         WHEN u.name CONTAINS 'Perth' OR u.name CONTAINS 'Western Australia' THEN 'Western Australia'
         WHEN u.name CONTAINS 'Tasmania' THEN 'Tasmania'
         WHEN u.name CONTAINS 'Canberra' OR u.name CONTAINS 'ACT' THEN 'Australian Capital Territory'
         WHEN u.name CONTAINS 'Darwin' OR u.name CONTAINS 'Northern Territory' THEN 'Northern Territory'
         ELSE 'Other'
     END AS state
MATCH (u)-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->()-[:OFFERS]->(p:Program)
RETURN state,
       collect(DISTINCT u.name) AS universities,
       count(DISTINCT u) AS university_count,
       count(DISTINCT p) AS total_programs
ORDER BY university_count DESC;

-- name: settlement_info_by_state
// 18.3. ĐỊNH CƯ THEO VÙNG
MATCH (sp:SettlementPage)
WHERE toLower(sp.title) CONTAINS toLower($state)
   OR toLower(sp.url) CONTAINS toLower($state)
OPTIONAL MATCH (sp)<-[:CONTAINS_SETTLEMENT_PAGE]-(tg:SettlementTaskGroup)
              <-[:HAS_GROUP]-(cat:SettlementCategory)
OPTIONAL MATCH (sp)-[:HAS_SETTLEMENT_SECTION]->(sec)
RETURN sp.title AS page_title,
       sp.url AS url,
       cat.name AS category,
       tg.name AS task_group,
       collect(DISTINCT sec.title)[..5] AS sections
LIMIT 10;

// ============================================================
// PHẦN 19: CAREER & EMPLOYMENT QUERIES
// ============================================================

-- name: career_resources_by_field
// 19.1. TÌM NGÀNH NGHỀ TIỀM NĂNG
MATCH (cat:StudyCategory)
WHERE toLower(cat.name) CONTAINS toLower($field)
MATCH (cat)-[:RELATED_TO_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
WHERE toLower(sc.name) CONTAINS 'employ'
   OR toLower(sc.name) CONTAINS 'work'
   OR toLower(sc.name) CONTAINS 'career'
MATCH (sc)-[:HAS_GROUP]->(tg:SettlementTaskGroup)
      -[:CONTAINS_SETTLEMENT_PAGE]->(sp:SettlementPage)
OPTIONAL MATCH (sp)-[:HAS_SETTLEMENT_SECTION]->(sec)
WHERE toLower(sec.title) CONTAINS 'job'
   OR toLower(sec.title) CONTAINS 'career'
   OR toLower(sec.title) CONTAINS 'industry'
RETURN {
    study_field: cat.name,
    career_resources: collect(DISTINCT {
        category: sc.name,
        resource: sp.title,
        url: sp.url,
        sections: collect(DISTINCT sec.title)[..3]
    })[..5]
} AS career_info;

-- name: skills_demand_overview
// 19.2. SKILLS GAP ANALYSIS
MATCH (sc:SettlementCategory)
WHERE toLower(sc.name) CONTAINS 'skill'
   OR toLower(sc.name) CONTAINS 'demand'
   OR toLower(sc.name) CONTAINS 'shortage'
MATCH (sc)-[:HAS_GROUP]->(tg:SettlementTaskGroup)
      -[:CONTAINS_SETTLEMENT_PAGE]->(sp:SettlementPage)
OPTIONAL MATCH (cat:StudyCategory)
              -[:RELATED_TO_SETTLEMENT_CATEGORY]->(sc)
RETURN {
    in_demand_category: sc.name,
    related_study_fields: collect(DISTINCT cat.name),
    resources: collect(DISTINCT {title: sp.title, url: sp.url})[..3]
} AS skills_demand
LIMIT 5;

-- name: post_graduation_career_pathway
// 19.3. LỘ TRÌNH NGHỀ NGHIỆP SAU TỐT NGHIỆP
MATCH (p:Program {program_type: $level})
WHERE toLower(p.name) CONTAINS toLower($field)
MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
MATCH (cat)-[:RELATED_TO_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
MATCH (sc)-[:HAS_GROUP]->(tg:SettlementTaskGroup)
MATCH (visa_grad:Visa {subclass: "485"})
MATCH (visa_pr:Visa)
WHERE visa_pr.subclass IN ["189", "190", "186"]
OPTIONAL MATCH (visa_pr)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(sc2:SettlementCategory)
RETURN {
    your_degree: { program: p.name, category: cat.name },
    immediate_steps: { visa: visa_grad.name_visa, purpose: "2-4 years work rights after graduation" },
    career_resources: collect(DISTINCT { category: sc.name, task_group: tg.name })[..3],
    long_term: {
        pr_visa_options: collect(DISTINCT visa_pr.name_visa),
        settlement_support: collect(DISTINCT sc2.name)[..3]
    }
} AS career_pathway
LIMIT 1;

// ============================================================
// PHẦN 20: COMPARATIVE ANALYSIS (So sánh nâng cao)
// ============================================================

-- name: university_comparison_matrix
// 20.1. MA TRẬN SO SÁNH TRƯỜNG
MATCH (u:University)
WHERE u.name IN $university_list
OPTIONAL MATCH (u)-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->(pl:ProgramLevel)-[:OFFERS]->(p:Program)
OPTIONAL MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam {name: "IELTS"})
OPTIONAL MATCH (u)-[:HAS_INFO]->()-[:HAS_SECTION]->(sec:InfoSection)
WITH u,
     count(DISTINCT p) AS total_programs,
     count(DISTINCT CASE WHEN p.program_type = 'Bachelor' THEN p END) AS bachelor,
     count(DISTINCT CASE WHEN p.program_type = 'Master' THEN p END) AS master,
     count(DISTINCT CASE WHEN p.program_type = 'Doctor' THEN p END) AS doctor,
     collect(DISTINCT cat.name)[..5] AS top_categories,
     avg(es.value) AS avg_ielts,
     min(es.value) AS min_ielts,
     collect(DISTINCT sec.key)[..3] AS info_available
RETURN u.name AS University,
       total_programs AS `Total Programs`,
       bachelor AS `Bachelor`,
       master AS `Master`,
       doctor AS `PhD`,
       top_categories AS `Top Categories`,
       round(avg_ielts * 10) / 10 AS `Avg IELTS`,
       min_ielts AS `Min IELTS`,
       info_available AS `Info Available`
ORDER BY total_programs DESC;

-- name: visa_pathway_comparison
// 20.2. SO SÁNH VISA PATHWAY
UNWIND $visa_subclasses AS subclass
MATCH (v:Visa {subclass: subclass})
OPTIONAL MATCH (v)-[:HAS_ABOUT_INFO]->(a:AboutInfo)
OPTIONAL MATCH (v)-[:HAS_ELIGIBILITY_REQUIREMENT]->(er:EligibilityRequirement)
OPTIONAL MATCH (v)-[:HAS_RELEVANT_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
WITH v,
     collect(DISTINCT a.content)[..2] AS about,
     count(DISTINCT er) AS requirements,
     collect(DISTINCT sc.name)[..3] AS settlement
RETURN {
    visa_name: v.name_visa,
    subclass: v.subclass,
    description: about,
    requirement_complexity: CASE 
        WHEN requirements <= 5 THEN "Low"
        WHEN requirements <= 10 THEN "Medium"
        ELSE "High"
    END,
    settlement_support: settlement,
    url: v.url
} AS visa_comparison
ORDER BY v.subclass;

-- name: benchmark_field_across_universities
// 20.3. BENCHMARK NGÀNH HỌC
MATCH (cat:StudyCategory)
WHERE toLower(cat.name) CONTAINS toLower($field)
MATCH (p:Program)-[:IN_STUDY_CATEGORY]->(cat)
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)<-[:HAS_PROGRAMS]-(u:University)
OPTIONAL MATCH (p)-[:HAS_REQUIRED]->(es:ExamScore)<-[:HAS_SCORE]-(e:Exam)
WITH u, cat, count(DISTINCT p) AS programs, collect(DISTINCT p.program_type) AS levels, avg(es.value) AS avg_requirement
RETURN u.name AS university,
       cat.name AS category,
       programs AS total_programs,
       levels AS available_levels,
       round(avg_requirement * 10) / 10 AS avg_entry_score
ORDER BY programs DESC
LIMIT 10;

// ============================================================
// PHẦN 21: FUZZY MATCHING & SEARCH (Tìm kiếm mờ)
// ============================================================

-- name: fuzzy_university_search
// 21.1. TÌM KIẾM GẦN ĐÚNG TRƯỜNG
MATCH (u:University)
WHERE toLower(u.name) CONTAINS toLower($search_term)
   OR apoc.text.levenshteinDistance(toLower(u.name), toLower($search_term)) <= 3
RETURN u.name AS university,
       apoc.text.levenshteinDistance(toLower(u.name), toLower($search_term)) AS distance
ORDER BY distance ASC
LIMIT 5;

-- name: programs_multi_keyword_search
// 21.2. MULTI-KEYWORD SEARCH
MATCH (p:Program)
WHERE ANY(keyword IN $keywords 
    WHERE toLower(p.name) CONTAINS toLower(keyword)
       OR toLower(p.description) CONTAINS toLower(keyword))
MATCH (p)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)<-[:HAS_PROGRAMS]-(u:University)
OPTIONAL MATCH (p)-[:FOCUSES_ON]->(subj:Subject)
OPTIONAL MATCH (p)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
WITH u, p, subj, cat,
     size([keyword IN $keywords WHERE toLower(p.name) CONTAINS toLower(keyword)]) AS match_count
WHERE match_count > 0
RETURN u.name AS university,
       p.name AS program,
       match_count AS relevance_score,
       subj.name AS subject,
       cat.name AS category,
       p.url AS url
ORDER BY match_count DESC, u.name ASC
LIMIT 15;

-- name: semantic_similar_programs
// 21.3. SEMANTIC SEARCH
MATCH (reference:Program {name: $reference_program})
MATCH (reference)-[:FOCUSES_ON]->(subj:Subject)
MATCH (reference)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
MATCH (similar:Program)-[:FOCUSES_ON]->(subj)
WHERE similar <> reference
OPTIONAL MATCH (similar)-[:IN_STUDY_CATEGORY]->(cat)
MATCH (similar)<-[:OFFERS]-(pl:ProgramLevel)<-[:HAS_LEVEL]-(pg:ProgramGroup)<-[:HAS_PROGRAMS]-(u:University)
WITH u, similar, CASE WHEN exists((similar)-[:IN_STUDY_CATEGORY]->(cat)) THEN 2 ELSE 1 END AS similarity_score
RETURN u.name AS university,
       similar.name AS similar_program,
       similarity_score,
       similar.url AS url
ORDER BY similarity_score DESC, u.name ASC
LIMIT 10;

// ============================================================
// PHẦN 22: GRAPH ANALYTICS (Phân tích đồ thị)
// ============================================================

-- name: studycategory_centrality_overview
// 22.1. CENTRALITY ANALYSIS
MATCH (cat:StudyCategory)
OPTIONAL MATCH (cat)<-[:IN_STUDY_CATEGORY]-(p:Program)
OPTIONAL MATCH (cat)-[:RELATED_TO_SETTLEMENT_CATEGORY]->(sc:SettlementCategory)
WITH cat,
     count(DISTINCT p) AS program_connections,
     count(DISTINCT sc) AS settlement_connections,
     (count(DISTINCT p) + count(DISTINCT sc)) AS total_connections
ORDER BY total_connections DESC
LIMIT 10
RETURN cat.name AS category,
       program_connections,
       settlement_connections,
       total_connections AS centrality_score;

-- name: university_community_detection_by_categories
// 22.2. COMMUNITY DETECTION
MATCH (u1:University)-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->()-[:OFFERS]->(p1:Program)
MATCH (p1)-[:IN_STUDY_CATEGORY]->(cat:StudyCategory)
MATCH (p2:Program)-[:IN_STUDY_CATEGORY]->(cat)
MATCH (u2:University)-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->()-[:OFFERS]->(p2)
WHERE u1 <> u2
WITH u1, u2, count(DISTINCT cat) AS shared_categories
WHERE shared_categories >= 3
RETURN u1.name AS university_1,
       u2.name AS university_2,
       shared_categories AS similarity_index
ORDER BY shared_categories DESC
LIMIT 20;

-- name: path_analysis_bachelor_it_to_pr
// 22.3. PATH ANALYSIS
MATCH path = shortestPath(
    (start:Program {program_type: "Bachelor"})-[:FOCUSES_ON]->(:Subject)
    -[*..8]-
    (end:Visa)
)
WHERE toLower(start.name) CONTAINS 'computer'
  AND end.subclass IN ["189", "190"]
RETURN path,
       length(path) AS path_length,
       [n IN nodes(path) | labels(n)[0]] AS node_types,
       [r IN relationships(path) | type(r)] AS relationship_types
LIMIT 3;

// ============================================================
// PHẦN 23: ADMIN & MAINTENANCE QUERIES
// ============================================================

-- name: data_quality_check_summary
// 23.1. DATA QUALITY CHECK
MATCH (p:Program)
WHERE p.name IS NULL OR p.name = '' OR NOT exists((p)<-[:OFFERS]-())
RETURN 'Incomplete Program' AS issue, count(p) AS count, collect(p.uid)[..5] AS examples
UNION
MATCH (v:Visa)
WHERE v.subclass IS NULL OR v.subclass = ''
RETURN 'Incomplete Visa' AS issue, count(v) AS count, collect(v.name_visa)[..5] AS examples
UNION
MATCH (u:University)
WHERE NOT exists((u)-[:HAS_PROGRAMS]->())
RETURN 'University without programs' AS issue, count(u) AS count, collect(u.name)[..5] AS examples;

-- name: relationship_audit_counts
// 23.2. RELATIONSHIP AUDIT
MATCH ()-[r]->()
WITH type(r) AS rel_type, count(r) AS rel_count
RETURN rel_type, rel_count
ORDER BY rel_count DESC;

-- name: node_count_by_label
// 23.3. NODE COUNT BY LABEL
CALL db.labels() YIELD label
CALL apoc.cypher.run('MATCH (n:`' + label + '`) RETURN count(n) AS cnt', {}) YIELD value
RETURN label, value.cnt AS count
ORDER BY value.cnt DESC;

// ============================================================
// PHẦN 24: PERFORMANCE OPTIMIZATION
// ============================================================

-- name: create_core_indexes
// 24.1. CREATE INDEXES (DDL)
CREATE INDEX university_name IF NOT EXISTS FOR (u:University) ON (u.name);
CREATE INDEX program_uid IF NOT EXISTS FOR (p:Program) ON (p.uid);
CREATE INDEX program_type IF NOT EXISTS FOR (p:Program) ON (p.program_type);
CREATE INDEX visa_subclass IF NOT EXISTS FOR (v:Visa) ON (v.subclass);
CREATE INDEX category_name IF NOT EXISTS FOR (c:StudyCategory) ON (c.name);
CREATE INDEX settlement_title IF NOT EXISTS FOR (sp:SettlementPage) ON (sp.title);

-- name: profile_program_count_by_university
// 24.2. QUERY PROFILING
PROFILE
MATCH (u:University {name: $university_name})-[:HAS_PROGRAMS]->()-[:HAS_LEVEL]->()-[:OFFERS]->(p:Program)
RETURN count(p);

-- name: explain_visa_about_query
// 24.3. EXPLAIN PLAN
EXPLAIN
MATCH (v:Visa {subclass: $subclass})-[:HAS_ABOUT_INFO]->(a:AboutInfo)
RETURN v, collect(a);

// ============================================================
// KẾT THÚC - GHI CHÚ BỔ SUNG
// ============================================================

/*
ADVANCED TIPS:

1. CACHING STRATEGIES:
   - Cache kết quả thường dùng: danh sách trường, visa types
   - Invalidate cache khi có update data
   - Redis/Memcached cho production

2. PAGINATION:
   - Luôn dùng SKIP/LIMIT cho large results
   - Frontend: implement infinite scroll
   
3. ERROR HANDLING:
   - Check empty results
   - Provide fallback queries
   - Log failed queries for analysis

4. MONITORING:
   - Track query performance
   - Monitor slow queries (>1s)
   - Set up alerts for timeouts

5. SECURITY:
   - Parameterize ALL user inputs
   - Never concatenate strings in queries
   - Limit query complexity (max depth)

6. SCALABILITY:
   - Use batch operations for imports
   - Implement read replicas
   - Consider sharding for >100M nodes

TESTING CHECKLIST:
□ Test with NULL values
□ Test with special characters
□ Test with very long inputs
□ Test with multiple concurrent requests
□ Test edge cases (0 results, 1000+ results)
*/

// ============================================================
// LƯU Ý SỬ DỤNG:
// ============================================================
// - Thay $parameter bằng giá trị thực tế khi chạy query
// - Adjust LIMIT theo nhu cầu hiển thị
// - Combine nhiều query để tạo kết quả phức tạp hơn
// - Sử dụng OPTIONAL MATCH để tránh missing data
// - Với chatbot: parse user intent → chọn query template → fill parameters
// ============================================================






