"""Shared site data: navigation, doctors, services, booking links and news topics."""

HOTDOC = 'https://www.hotdoc.com.au/medical-centres/victoria-point-QLD-4165/sunstate-family-practice/doctors'
PHONE = '(07) 3207 7744'
TEL = 'tel:+61732077744'
LIVE = 'https://sunstatefamilypractice.com.au'

NAV = [
    {'label': 'Services', 'href': '/our-services/', 'children': [
        {'label': 'Skin Cancer Checks', 'href': '/skin-checks/'},
        {'label': 'Total Body Mapping', 'href': '/total-body-mapping-victoria-point/'},
        {'label': 'Skin Checks Redland Bay', 'href': '/skin-checks-redland-bay/'},
        {'label': 'Ear Micro Suction', 'href': '/ear-micro-suction/'},
        {'label': 'Iron Infusions', 'href': '/iron-infusions/'},
        {'label': 'Preventive Health', 'href': '/preventive-health/'},
        {'label': 'Travel Medicine', 'href': '/travel-medicine/'},
        {'label': 'Chronic Disease Management', 'href': '/chronic-disease-management/'},
        {'label': 'All services', 'href': '/our-services/'},
    ]},
    {'label': 'Doctors', 'href': '/our-team/'},
    {'label': 'About', 'href': '/about-us/', 'children': [
        {'label': 'About Us', 'href': '/about-us/'},
        {'label': 'Patient Feedback', 'href': '/patient-feedback-survey/'},
        {'label': 'Careers', 'href': '/careers/'},
        {'label': 'FAQs', 'href': '/faqs/'},
    ]},
    {'label': 'Fees', 'href': '/fees/'},
    {'label': 'News', 'href': '/news/'},
    {'label': 'Contact Us', 'href': '/contact-us/'},
]

# Current doctors, in the order the live team page shows them.
DOCTORS = [
    {'slug': 'dr-andrew-ganter-2', 'name': 'Dr Andrew Ganter', 'photo': 'andrew-ganter', 'quals': 'MBBS, FRACGP', 'role': 'Principal Doctor',
     'interest': 'Travel medicine, children’s health and skin cancer'},
    {'slug': 'dr-randal-johnson', 'name': 'Dr Randal Johnson', 'photo': 'randal-johnson', 'quals': 'BSc, MD, SCHP, FRACGP',
     'interest': 'Skin cancer detection and removal'},
    {'slug': 'dr-lisa-scupham', 'name': 'Dr Lisa Scupham', 'photo': 'lisa-scupham', 'quals': 'BPharm, MBBS (Hons, Qld), GradDipSurgAnat, MS, FRACGP',
     'interest': 'Skin cancer screening and management'},
    {'slug': 'dr-eugenia-haller', 'name': 'Dr Eugenia Haller', 'photo': 'eugenia-haller', 'quals': 'MD, FRACGP',
     'interest': 'Skin cancer medicine and excisions'},
    {'slug': 'dr-chau-vu-2', 'name': 'Dr Chau Vu', 'photo': 'chau-vu', 'quals': 'BSc, MBBS, FRACGP',
     'interest': 'Skin checks and excisions'},
    {'slug': 'dr-tegan-stein', 'name': 'Dr Tegan Stein', 'photo': 'tegan-stein', 'quals': 'BSc, MBBS, FRACGP',
     'interest': 'Paediatrics, adolescent health and antenatal care'},
    {'slug': 'dr-ben-ierna', 'name': 'Dr Ben Ierna', 'photo': 'ben-ierna', 'quals': 'BAppSc, MBBS, FRACGP',
     'interest': 'Skin checks and minor procedures'},
    {'slug': 'dr-jenny-buteri', 'name': 'Dr Jenny Buteri', 'photo': 'jenny-buteri', 'quals': 'BBiomedSc, MD, FRACGP',
     'interest': 'Women’s health and paediatrics', 'note': 'Currently on maternity leave'},
    {'slug': 'dr-willard-jones', 'name': 'Dr James Willard-Jones', 'photo': 'james-willard-jones', 'quals': 'BBiomedSc, MBBS',
     'interest': 'All aspects of general practice'},
    {'slug': 'dr-harriet-ruffin', 'name': 'Dr Harriet Ruffin', 'photo': 'harriet-ruffin', 'quals': 'MD, BSc (Hons)',
     'interest': 'Women’s health, families and preventive health'},
    {'slug': 'dr-makayla-hamilton', 'name': 'Dr Makayla Hamilton', 'photo': 'makayla-hamilton', 'quals': '',
     'interest': 'All aspects of general practice'},
    {'slug': 'dr-hannah-witenden', 'name': 'Dr Hannah Witenden', 'photo': 'hannah-witenden', 'quals': '',
     'interest': 'All aspects of general practice'},
]
for d in DOCTORS:
    d['href'] = f"/our-team/{d['slug']}/"
    d['img'] = f"/assets/img/doctors/{d['photo']}.webp"

SERVICES = [
    {'name': 'Skin Cancer Checks', 'href': '/skin-checks/', 'img': '/assets/img/woman-sun-hat.webp',
     'summary': 'Yearly skin checks are essential as Queensland has one of the highest skin cancer rates in the world.'},
    {'name': 'Total Body Mapping', 'href': '/total-body-mapping-victoria-point/', 'img': '/assets/img/video-body-imaging.webp',
     'summary': 'Mole mapping and advanced total body photography that tracks your skin over time.'},
    {'name': 'Ear Micro Suction', 'href': '/ear-micro-suction/', 'img': '/assets/img/svc-ear.webp',
     'summary': 'Microscopic ear suction is the safest way to remove a buildup of wax or other objects from your ear canal.'},
    {'name': 'Iron Infusions', 'href': '/iron-infusions/', 'img': '/assets/img/svc-iron.webp',
     'summary': 'We have doctors who are experienced in performing Iron Infusions at our practice.'},
    {'name': 'Preventive Health', 'href': '/preventive-health/', 'img': '/assets/img/svc-preventive.webp',
     'summary': 'A proactive, collaborative, patient centered approach to health care.'},
    {'name': 'Travel Medicine', 'href': '/travel-medicine/', 'img': '/assets/img/svc-travel.webp',
     'summary': 'Protect yourself and your family from disease and infection before you travel.'},
    {'name': 'Chronic Disease Management', 'href': '/chronic-disease-management/', 'img': '/assets/img/svc-chronic.webp',
     'summary': 'Care plans and team care coordinated by our nurses with your GP and allied health.'},
    {'name': 'Skin Checks Redland Bay', 'href': '/skin-checks-redland-bay/', 'img': '/assets/img/live/2026-07-skin-checks-redland-bay.webp',
     'summary': 'Comprehensive skin checks for patients from Redland Bay, minutes from the practice.'},
]

SUBURBS = {
    'thornlands-doctors': {'name': 'Thornlands', 'img': '/assets/img/suburb-thornlands.webp'},
    'cleveland-doctors': {'name': 'Cleveland', 'img': '/assets/img/suburb-cleveland.webp'},
    'redland-bay-doctors': {'name': 'Redland Bay', 'img': '/assets/img/suburb-redland-bay.webp'},
    'capalaba-doctors': {'name': 'Capalaba', 'img': '/assets/img/suburb-capalaba.webp'},
    'alexandra-hills-doctors': {'name': 'Alexandra Hills', 'img': '/assets/img/suburb-alexandra-hills.webp'},
    'wellington-point-doctors': {'name': 'Wellington Point', 'img': '/assets/img/suburb-wellington-point.webp'},
    'sheldon-doctors': {'name': 'Sheldon', 'img': '/assets/img/suburb-sheldon.webp'},
}

# News topics for filtering (the live site files almost every post under one category).
TOPICS = {
    'skin': 'Skin health',
    'women': 'Women’s health',
    'living': 'Healthy living',
    'conditions': 'Conditions',
    'clinic': 'Clinic news',
    'covid': 'COVID-19',
}
POST_TOPIC = {
    'what-is-a-sunstate-skin-check': 'skin', 'a-simple-skin-check-could-save-you-big-time': 'skin',
    'skin-changes-with-age-whats-normal-and-what-needs-checking': 'skin', 'what-happens-when-your-gp-finds-a-suspicious-spot': 'skin',
    'skin-checks-and-total-body-mapping-do-you-need-both': 'skin', 'skin-cancer-prevention-take-a-skin-cancer-screening-with-us': 'skin',
    'cancer-awareness-and-early-detection-whats-changed-and-what-to-watch': 'conditions',
    'womens-health-week-2020': 'women', 'ready-to-take-control-of-your-menopause-journey': 'women', 'top-10-reasons-of-pelvic-pain-in-women': 'women',
    'beat-anxiety-and-improve-your-sleep': 'living', 'how-to-not-get-food-poisoning-during-christmas': 'living', 'the-essential-holiday-season-guide': 'living',
    '5-food-groups-variety-is-the-key': 'living', '10-healthy-ways-to-boost-your-immune-system': 'living', 'how-food-impacts-heart-health': 'living',
    'healthy-bones-action-week-2020-healthy-bones-for-a-better-life': 'living', 'preventive-healthcare-checklist-2021': 'living',
    'common-health-changes-many-people-notice-in-their-40s': 'living', 'why-vaccines-still-matter-for-you-and-your-family': 'living',
    'why-continuity-of-care-matters-seeing-the-same-gp-over-time': 'living',
    'thyroid-health-the-often-overlooked-gland': 'conditions', 'the-month-of-may-for-matters-of-the-heart': 'conditions',
    'breathe-better-asthma-action-plan': 'conditions', 'difference-between-coeliac-disease-and-gluten-intolerance-why-diagnosis-is-important': 'conditions',
    'feeling-tired-and-you-dont-know-why-it-could-be-iron-deficiency': 'conditions', 'hearing-health-matters-earwax-removal': 'conditions',
    'the-dos-and-donts-for-healthy-kidneys': 'conditions', 'kidney-health-how-to-prevent-kidney-stones': 'conditions',
    'facts-and-risks-of-bowel-cancer-explained': 'conditions', 'asthma-and-bronchiectasis-are-overlapping-lung-diseases': 'conditions',
    'chronic-disease-management-how-your-gp-helps-you-stay-independent': 'conditions',
    'welcome-to-sunstate-dr-ben-ierna': 'clinic', 'were-moving': 'clinic', 'welcome-back-to-sunstate-dr-johnson': 'clinic',
    'introducing-dr-jenny-buteri': 'clinic', 'sunstate-family-practice-welcomes-dr-eugenia-haller': 'clinic', 'exciting-news': 'clinic',
    'new-website-clinic-news': 'clinic', 'introducing-dr-tegan-stein': 'clinic', 'pathology': 'clinic',
    'patient-action-plan-covid-19': 'covid', 'corona-virus-update': 'covid', 'coronavirus-outbreak': 'covid', 'coronavirus-latest': 'covid',
    'coronavirus-covid-19-isolation-guidance': 'covid', 'coronavirus-covid-19-information-for-international-travellers': 'covid',
    'being-a-gp-in-the-current-coronavirus-world-dr-amy-heales': 'covid', 'covid-19-preparedness-and-importance-of-self-isolation': 'covid',
}
