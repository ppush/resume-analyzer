#!/usr/bin/env python3
"""
Final comparison between DOCX and PDF versions after all fixes
"""

import json

def compare_final_results():
    print('🔍 ФИНАЛЬНОЕ СРАВНЕНИЕ DOCX vs PDF (ПОСЛЕ ВСЕХ ИСПРАВЛЕНИЙ)')
    print('=' * 70)
    
    # Load results
    with open('vahan_avagyan_docx_final_result.json', 'r', encoding='utf-8') as f:
        docx_result = json.load(f)
    
    with open('vahan_avagyan_pdf_final_result.json', 'r', encoding='utf-8') as f:
        pdf_result = json.load(f)
    
    print('📊 ОСНОВНЫЕ МЕТРИКИ:')
    print('-' * 50)
    print(f'{"Метрика":<25} {"DOCX":<10} {"PDF":<10} {"Разница":<10}')
    print('-' * 50)
    
    # Skills count
    docx_skills = len(docx_result['skills'])
    pdf_skills = len(pdf_result['skills'])
    skills_diff = docx_skills - pdf_skills
    print(f'{"Навыки":<25} {docx_skills:<10} {pdf_skills:<10} {skills_diff:+d}')
    
    # Roles count
    docx_roles = len(docx_result['roles'])
    pdf_roles = len(pdf_result['roles'])
    roles_diff = docx_roles - pdf_roles
    print(f'{"Роли":<25} {docx_roles:<10} {pdf_roles:<10} {roles_diff:+d}')
    
    # Languages count
    docx_langs = len(docx_result['languages'])
    pdf_langs = len(pdf_result['languages'])
    langs_diff = docx_langs - pdf_langs
    print(f'{"Языки":<25} {docx_langs:<10} {pdf_langs:<10} {langs_diff:+d}')
    
    # Recommendations count
    docx_recs = len(docx_result['recommendations'])
    pdf_recs = len(pdf_result['recommendations'])
    recs_diff = docx_recs - pdf_recs
    print(f'{"Рекомендации":<25} {docx_recs:<10} {pdf_recs:<10} {recs_diff:+d}')
    
    # Location
    docx_loc = docx_result['location']
    pdf_loc = pdf_result['location']
    loc_match = "✅" if docx_loc == pdf_loc else "❌"
    print(f'{"Локация":<25} {docx_loc:<10} {pdf_loc:<10} {loc_match}')
    
    # Experience
    docx_exp = docx_result['experience']
    pdf_exp = pdf_result['experience']
    exp_match = "✅" if docx_exp == pdf_exp else "❌"
    print(f'{"Опыт":<25} {docx_exp:<10} {pdf_exp:<10} {exp_match}')
    
    print()
    print('🎯 ТОП-5 НАВЫКОВ (DOCX):')
    print('-' * 50)
    for i, skill in enumerate(docx_result['skills'][:5], 1):
        print(f'{i}. {skill["name"]} (score: {skill["score"]})')
    
    print()
    print('🎯 ТОП-5 НАВЫКОВ (PDF):')
    print('-' * 50)
    for i, skill in enumerate(pdf_result['skills'][:5], 1):
        print(f'{i}. {skill["name"]} (score: {skill["score"]})')
    
    print()
    print('💻 ЯЗЫКИ ПРОГРАММИРОВАНИЯ:')
    print('-' * 50)
    
    # Find programming languages in both results
    docx_prog_langs = [s for s in docx_result['skills'] if any(lang in s['name'].lower() for lang in ['java', 'python', 'javascript', 'php', 'delphi'])]
    pdf_prog_langs = [s for s in pdf_result['skills'] if any(lang in s['name'].lower() for lang in ['java', 'python', 'javascript', 'php', 'delphi'])]
    
    print('DOCX версия:')
    for skill in docx_prog_langs:
        print(f'  • {skill["name"]} (score: {skill["score"]})')
        if skill.get('merged_names'):
            print(f'    Объединенные: {skill["merged_names"]}')
    
    print()
    print('PDF версия:')
    for skill in pdf_prog_langs:
        print(f'  • {skill["name"]} (score: {skill["score"]})')
        if skill.get('merged_names'):
            print(f'    Объединенные: {skill["merged_names"]}')
    
    print()
    print('💼 РОЛИ (DOCX):')
    print('-' * 50)
    for role in docx_result['roles']:
        print(f'• {role["title"]} - {role["project"]} ({role["duration"]})')
    
    print()
    print('💼 РОЛИ (PDF):')
    print('-' * 50)
    for role in pdf_result['roles']:
        print(f'• {role["title"]} - {role["project"]} ({role["duration"]})')
    
    print()
    print('📈 АНАЛИЗ РАЗЛИЧИЙ:')
    print('-' * 50)
    
    if skills_diff > 0:
        print(f'✅ DOCX извлек больше навыков (+{skills_diff})')
    elif skills_diff < 0:
        print(f'✅ PDF извлек больше навыков ({skills_diff})')
    else:
        print('✅ Количество навыков одинаково')
    
    if roles_diff > 0:
        print(f'✅ DOCX извлек больше ролей (+{roles_diff})')
    elif roles_diff < 0:
        print(f'✅ PDF извлек больше ролей ({roles_diff})')
    else:
        print('✅ Количество ролей одинаково')
    
    # Check for unique roles
    docx_role_titles = {role['title'] for role in docx_result['roles']}
    pdf_role_titles = {role['title'] for role in pdf_result['roles']}
    
    unique_to_docx = docx_role_titles - pdf_role_titles
    unique_to_pdf = pdf_role_titles - docx_role_titles
    
    if unique_to_docx:
        print(f'📋 Уникальные роли в DOCX: {", ".join(unique_to_docx)}')
    if unique_to_pdf:
        print(f'📋 Уникальные роли в PDF: {", ".join(unique_to_pdf)}')
    
    # Check programming languages separation
    docx_merged_prog = any('&' in skill['merged_names'] and any(lang in skill['name'].lower() for lang in ['java', 'python', 'javascript', 'php', 'delphi']) for skill in docx_result['skills'])
    pdf_merged_prog = any('&' in skill['merged_names'] and any(lang in skill['name'].lower() for lang in ['java', 'python', 'javascript', 'php', 'delphi']) for skill in pdf_result['skills'])
    
    print()
    print('🔧 КАЧЕСТВО ОБРАБОТКИ:')
    print('-' * 50)
    
    if not docx_merged_prog and not pdf_merged_prog:
        print('✅ Языки программирования правильно разделены в обеих версиях')
    else:
        if docx_merged_prog:
            print('⚠️ DOCX: некоторые языки программирования объединены')
        if pdf_merged_prog:
            print('⚠️ PDF: некоторые языки программирования объединены')
    
    # Check for strange merged_names patterns
    docx_strange = [s for s in docx_result['skills'] if '(' in s['merged_names'] and ')' in s['merged_names'] and any(char.isdigit() for char in s['merged_names'])]
    pdf_strange = [s for s in pdf_result['skills'] if '(' in s['merged_names'] and ')' in s['merged_names'] and any(char.isdigit() for char in s['merged_names'])]
    
    if docx_strange:
        print('⚠️ DOCX: найдены странные merged_names:')
        for skill in docx_strange:
            print(f'  - {skill["name"]}: {skill["merged_names"]}')
    
    if pdf_strange:
        print('⚠️ PDF: найдены странные merged_names:')
        for skill in pdf_strange:
            print(f'  - {skill["name"]}: {skill["merged_names"]}')
    
    print()
    print('🏆 ИТОГОВЫЙ ВЫВОД:')
    print('-' * 50)
    
    if abs(skills_diff) <= 10 and abs(roles_diff) <= 3:
        print('✅ Результаты достаточно похожи - система работает стабильно')
    else:
        print('⚠️ Есть заметные различия между форматами')
    
    if docx_loc == pdf_loc and docx_exp == pdf_exp:
        print('✅ Ключевая информация (локация, опыт) извлекается одинаково')
    else:
        print('❌ Есть различия в ключевой информации')
    
    if not docx_merged_prog and not pdf_merged_prog and not docx_strange and not pdf_strange:
        print('✅ Алгоритм объединения навыков работает корректно')
    else:
        print('⚠️ Есть проблемы с алгоритмом объединения навыков')

if __name__ == '__main__':
    compare_final_results()
