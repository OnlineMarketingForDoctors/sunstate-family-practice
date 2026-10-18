"""Build the static site.

    python3 tools/build/build.py

Reads content/live.json (content extracted from the live WordPress site) and
content/handmade.json (metadata for the hand-built homepage and fees page), renders
every page through templates/, and writes each one to the same URL path as the live
site (for example /about-us/index.html) so existing links and rankings carry over.
"""
import json
import os
import re
from datetime import datetime

from jinja2 import Environment, FileSystemLoader

import sitedata as S
from render import (Pool, auto_sections, book_buttons, clean_text, contact_form, contact_section, crumbs, doctors_rail, e,
                    final_cta, fix_links, h2, h3_groups, img, local_href, page_hero, prose, pull_images, qa_item, quick_bar,
                    related_services, section_checklist, section_faq, section_split, section_steps, split_sections,
                    strip_booking, video_card, yt_id)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
CONTENT = {x['path']: x for x in json.load(open(os.path.join(HERE, 'content', 'live.json'), encoding='utf-8'))}
HANDMADE = json.load(open(os.path.join(HERE, 'content', 'handmade.json'), encoding='utf-8'))

env = Environment(loader=FileSystemLoader(os.path.join(HERE, 'templates')), autoescape=False, keep_trailing_newline=True)
WRITTEN = []


def title_of(path, fallback):
    t = CONTENT.get(path, {}).get('title') or fallback
    return t.replace('&', '&amp;') if '&amp;' not in t else t


def write(path, template, **ctx):
    out = os.path.join(ROOT, path.strip('/'), 'index.html') if path != '/' else os.path.join(ROOT, 'index.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    section = '/' + path.strip('/').split('/')[0] + '/' if path != '/' else '/'
    for item in S.NAV:
        hrefs = [item['href']] + [c['href'] for c in item.get('children', [])]
        if section in hrefs or path in hrefs:
            section = item['href']
            break
    ctx.setdefault('current_section', section)
    html = env.get_template(template).render(site=S, **ctx)
    html = re.sub(r'\n\s*\n+', '\n', html)
    open(out, 'w', encoding='utf-8').write(html)
    WRITTEN.append(path)


def meta(path):
    c = CONTENT[path]
    return {'title': title_of(path, ''), 'description': e(c.get('description') or '')}


def blocks(path):
    return [dict(b) for b in CONTENT[path]['blocks']]


def lead_from(bs, n=1):
    """Take the first n paragraphs as the hero lead; returns (lead_html, remaining_blocks)."""
    lead, rest, taken = [], [], 0
    for b in bs:
        if b['t'] == 'p' and taken < n:
            lead.append(b)
            taken += 1
        else:
            rest.append(b)
    return prose(lead), rest


def p(html):
    return {'t': 'p', 'html': html}


def ul(*items):
    return {'t': 'ul', 'items': list(items)}


def h(text, level='h2'):
    return {'t': level, 'text': text, 'html': text}


# ---------------------------------------------------------------- service pages

# the clinic's own photo of the ATBM screen replaces the live site's FotoFinder stock shot
TBM_SWAP = {'/assets/img/live/2025-10-fotofinder.webp': ('/assets/img/tbm-atbm-nurse.webp', 'Sunstate nurse operating the FotoFinder total body mapping system')}

SERVICE_PAGES = {
    '/skin-checks/': {
        'bg': '/assets/img/hero-skin.webp', 'chip': 'No referral needed', 'stmt_sat': '/assets/img/dermoscopy-mole.webp',
        'pool': ['/assets/img/woman-sun-hat.webp', '/assets/img/video-mosaic-view.webp', '/assets/img/dermatoscope-arm.webp', '/assets/img/freckled-shoulder.webp'],
        'crumb': [('Services', '/our-services/'), ('Skin Cancer Checks', None)],
        'img_swap': {**TBM_SWAP, '/assets/img/live/2026-06-65614.webp': ('/assets/img/skin-check-exam.webp', 'GP examining a patient\'s shoulder with a dermatoscope')},
    },
    '/total-body-mapping-victoria-point/': {
        'bg': '/assets/img/video-body-imaging.webp', 'sat': '/assets/img/dermoscopy-mole.webp', 'chip': 'AI-assisted FotoFinder imaging',
        'pool': ['/assets/img/video-mosaic-view.webp', '/assets/img/clinic-atbm-capture.webp', '/assets/img/gp-reviewing-images.webp', '/assets/img/video-dermatoscope.webp', '/assets/img/man-sailing.webp'],
        'crumb': [('Services', '/our-services/'), ('Total Body Mapping', None)],
    },
    '/skin-checks-redland-bay/': {
        'h1': 'Skin Checks Redland Bay', 'kicker': 'GP skin cancer checks near Redland Bay',
        'bg': '/assets/img/suburb-redland-bay.webp', 'sat': '/assets/img/live/2026-07-skin-checks-redland-bay.webp', 'chip': '10 minutes from Redland Bay',
        'pool': ['/assets/img/woman-sun-hat.webp', '/assets/img/dermatoscope-arm.webp', '/assets/img/man-sailing.webp', '/assets/img/freckled-shoulder.webp', '/assets/img/gp-reviewing-images.webp'],
        'crumb': [('Services', '/our-services/'), ('Skin Checks Redland Bay', None)],
        'img_swap': TBM_SWAP,
    },
    '/ear-micro-suction/': {
        'bg': '/assets/img/hero-ear.webp', 'chip': 'Performed by specially trained GPs', 'stmt_sat': '/assets/img/svc-ear.webp',
        'pool': ['/assets/img/live/2020-07-earwax-removal-is-benificial-for-hearning-health.webp', '/assets/img/visit-nurse.webp', '/assets/img/life-older.webp'],
        'crumb': [('Services', '/our-services/'), ('Ear Micro Suction', None)],
        'extra': [
            h('Signs of a wax build-up'),
            p('Ear wax protects the ear canal and usually clears on its own. Sometimes it builds up and causes symptoms such as:'),
            ul('A blocked or full feeling in the ear', 'Muffled or reduced hearing', 'Ringing in the ear', 'Ear discomfort or itching', 'Feeling slightly off balance'),
            p('If you have ear pain, discharge or sudden hearing loss, let reception know when you book so your GP can assess you first.'),
            h('What happens during ear micro suction'),
            p('1'), h('A look inside your ear', 'h3'), p('Your GP examines your ear canal with a microscope to see the wax and the eardrum clearly.'),
            p('2'), h('Gentle suction', 'h3'), p('A fine suction tube removes the wax under direct vision, without flushing water into the ear.'),
            p('3'), h('A final check', 'h3'), p('Your GP checks the ear canal and eardrum again and talks you through any follow-up you need.'),
        ],
    },
    '/iron-infusions/': {
        'bg': '/assets/img/hero-iron.webp', 'sat': '/assets/img/live/2026-06-2149261069.webp', 'chip': 'Experienced GPs and nurses',
        'pool': ['/assets/img/live/2026-06-2149261141.webp', '/assets/img/live/2026-06-2148973461.webp', '/assets/img/visit-nurse.webp'],
        'crumb': [('Services', '/our-services/'), ('Iron Infusions', None)],
        'extra': [
            h('Signs your iron may be low'),
            p('Low iron develops slowly, so many people get used to the symptoms. Common signs include:'),
            ul('Tiredness and lack of energy', 'Shortness of breath with everyday activity', 'Pale skin', 'Headaches or dizziness', 'Trouble concentrating'),
            p('A simple blood test ordered by your GP can check your iron levels. Read more in our article <a href="/feeling-tired-and-you-dont-know-why-it-could-be-iron-deficiency/">Feeling tired and you don’t know why? It could be iron deficiency</a>.'),
        ],
    },
    '/preventive-health/': {
        'bg': '/assets/img/hero-preventive.webp', 'chip': 'Health assessments are bulk billed', 'stmt_sat': '/assets/img/svc-preventive.webp',
        'pool': ['/assets/img/life-midlife.webp', '/assets/img/news-40s.webp', '/assets/img/life-older.webp', '/assets/img/visit-nurse.webp'],
        'crumb': [('Services', '/our-services/'), ('Preventive Health', None)],
        'extra': [
            h('Preventive care at Sunstate'),
            p('Our GPs and nurses offer a range of checks and screening to pick up risks early:'),
            ul('Free Health Screening for 45-49 year olds', 'Free annual Health checks for over 75 year olds', 'Screening for early risk of Vascular/ Heart disease with Arterial Brachial Index',
               'Spirometry', 'ECG’s', 'Skin cancer screening', 'Lifestyle modification', 'Weight loss advice'),
            p('Care plans and health assessments are bulk billed Monday to Friday, 8am to 5pm. <a href="/fees/">See our fees</a>.'),
            h('Make a plan with your GP'),
            p('Book a longer appointment for a health assessment so your GP has time to review your history, check your blood pressure, weight and blood tests, and agree on the screening that suits your age and risk.'),
            p('Our article <a href="/preventive-healthcare-checklist-2021/">Preventive healthcare checklist</a> is a good place to start.'),
        ],
    },
    '/travel-medicine/': {
        'bg': '/assets/img/svc-travel.webp', 'sat': '/assets/img/live/2026-06-1746.webp', 'chip': 'Book 6–8 weeks before you fly',
        'pool': ['/assets/img/svc-immunisation.webp', '/assets/img/family-beach.webp', '/assets/img/visit-nurse.webp'],
        'crumb': [('Services', '/our-services/'), ('Travel Medicine', None)],
        'extra': [
            h('Plan your travel appointment'),
            p('See a GP 6–8 weeks before you fly, as some vaccines need time to work or need more than one dose.'),
            p('Bring along:'),
            ul('Your travel itinerary, including the countries and regions you are visiting', 'Your vaccination history, if you have it', 'A list of your current medications', 'Details of any health conditions you are managing'),
            p('Your GP can talk you through vaccinations, medications to take with you and how to stay well while you are away.'),
        ],
    },
    '/chronic-disease-management/': {
        'h1': 'Chronic Disease Management',
        'bg': '/assets/img/svc-chronic.webp', 'sat': '/assets/img/live/2026-03-people-managing-chronic-illness.webp', 'chip': 'Care plans are bulk billed',
        'pool': ['/assets/img/life-older.webp', '/assets/img/news-chronic.webp', '/assets/img/hands.webp'],
        'crumb': [('Services', '/our-services/'), ('Chronic Disease Management', None)],
        'extra': [
            h('How we help you manage a chronic condition'),
            p('1'), h('A GP management plan', 'h3'), p('Your GP works with you to set goals for your condition and the care you need to reach them.'),
            p('2'), h('Team care arrangements', 'h3'), p('Our nurses coordinate your care with allied health professionals and specialists, including Medicare rebateable referrals where you are eligible.'),
            p('3'), h('Regular reviews', 'h3'), p('We review your plan regularly so your care keeps up with your health.'),
            p('Care plans and health assessments are bulk billed Monday to Friday, 8am to 5pm. <a href="/fees/">See our fees</a>.'),
        ],
    },
}


def short_p_list(bs):
    """Turn a run of short paragraphs (the live site's ✔ lists) into a list."""
    out, run = [], []

    def flush():
        if len(run) >= 3:
            out.append({'t': 'ul', 'items': [re.sub(r'^✔\s*', '', b['html']) for b in run]})
        else:
            out.extend(run)
        run.clear()
    for b in bs:
        text = re.sub(r'<[^>]+>', '', b.get('html', '')) if b['t'] == 'p' else ''
        if b['t'] == 'p' and (text.startswith('✔') or (len(text) < 140 and not re.fullmatch(r'\d', text.strip()) and not text.endswith(':'))):
            run.append(b)
        else:
            flush()
            out.append(b)
    flush()
    return out


def videos_section(pairs, title='Questions answered on camera'):
    first_id, first_title = pairs[0]
    items = ''.join(f'<li><button type="button"{" class=\"is-active\"" if i == 0 else ""} data-video="{vid}"><img src="https://i.ytimg.com/vi/{vid}/mqdefault.jpg" alt="" loading="lazy"><span>{e(t)}</span></button></li>'
                    for i, (vid, t) in enumerate(pairs))
    return f'''
<section class="videos" aria-labelledby="videos-title">
  <div class="wrap">
    <div class="videos__head">
      <div>
        <h2 id="videos-title" class="h2 h2--light">{e(title)}</h2>
        <p class="lead--light">Short videos from our team, filmed at the practice.</p>
      </div>
      <a class="videos__channel" href="https://www.youtube.com/@SunstateFamilyPracticeandSkinC" target="_blank" rel="noopener">More on our YouTube channel</a>
    </div>
    <div class="videos__grid">
      <div class="videos__player">
        <div class="yt" data-yt data-id="{first_id}">
          <img src="https://i.ytimg.com/vi/{first_id}/hqdefault.jpg" alt="" data-yt-thumb loading="lazy">
          <button class="yt__play" type="button" data-yt-play aria-label="Play video: {e(first_title)}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg></button>
        </div>
        <p class="videos__now" data-yt-title>{e(first_title)}</p>
      </div>
      <div class="videos__list"><ol class="playlist">{items}</ol></div>
    </div>
  </div>
</section>'''


def statement(lead_blocks, image, sat=None):
    """Opening statement: large text beside a layered photo pair."""
    imgs, bs = pull_images(strip_booking(lead_blocks))
    pic = imgs[0]['src'] if imgs else image
    sat_html = f'<figure class="stmt__sat reveal-img">{img(sat)}</figure>' if sat else ''
    return f'''
<section class="stmt">
  <div class="wrap stmt__grid">
    <div class="stmt__copy">{prose(bs)}</div>
    <div class="stmt__media">
      <figure class="stmt__img reveal-img">{img(pic)}</figure>
      {sat_html}
    </div>
  </div>
</section>'''


def build_service(path, cfg):
    c = CONTENT[path]
    bs = blocks(path)
    # drop the live page's own H1 and "On this page" contents list
    bs = [b for b in bs if not (b['t'] == 'h1' and clean_text(b['text']) == clean_text(c.get('h1') or ''))]
    bs = [b for b in bs if not (b['t'] == 'p' and re.sub(r'<[^>]+>', '', b['html']).startswith(('On this page', 'What Is a Skin Check?Who', 'Skin Monitoring TechnologyWhy')))]
    bs += cfg.get('extra', [])
    for b in bs:
        if b['t'] == 'img' and b['src'] in cfg.get('img_swap', {}):
            b['src'], b['alt'] = cfg['img_swap'][b['src']]
    h1 = cfg.get('h1') or clean_text(c.get('h1') or '')
    intro, sections = split_sections(bs)
    kicker = cfg.get('kicker')
    # "At Sunstate Family Practice" opens most service pages: it becomes the hero kicker and lead
    if sections and sections[0]['title'] == 'At Sunstate Family Practice':
        kicker = 'At Sunstate Family Practice'
        intro = intro + sections.pop(0)['blocks']
    if not intro and sections and path == '/total-body-mapping-victoria-point/':
        kicker = sections[0]['title']
        intro = sections.pop(0)['blocks']
    intro = strip_booking(intro)
    lead_html, rest = lead_from(intro, 1)
    body = [page_hero(h1, lead_html, cfg['bg'], cfg['crumb'], chip=cfg.get('chip'), kicker=kicker), quick_bar()]
    pool = Pool(cfg['pool'])
    rest_imgs, rest_text = pull_images(rest)
    if any(b['t'] in ('p', 'ul', 'ol') for b in rest_text):
        body.append(statement(rest, pool.next(), sat=cfg.get('stmt_sat') or pool.next()))
    # pull video playlists and the closing "Ready to get started" block out of the flow
    closing = None
    flow = []
    for sec in sections:
        title = sec['title'] if isinstance(sec['title'], str) else sec['title'][1]
        vids = []
        kept = []
        pending = None
        for b in sec['blocks']:
            if b['t'] == 'ul' and len(b['items']) == 1:
                pending = re.sub(r'<[^>]+>', '', b['items'][0]).strip()
                continue
            if b['t'] == 'video' and yt_id(b.get('src')):
                vids.append((yt_id(b['src']), pending or 'Watch the video'))
                pending = None
                continue
            kept.append(b)
        if title.lower().startswith('ready to get started'):
            closing = (title, re.sub(r'<[^>]+>', '', next((b['html'] for b in kept if b['t'] == 'p'), '')))
            continue
        sec['blocks'] = short_p_list(kept) if title.lower().startswith(('before you come in', 'why people choose')) else kept
        flow.append(sec)
        if vids:
            flow.append({'videos': vids})
    chunk = []
    for sec in flow:
        if 'videos' in sec:
            body.append(auto_sections(chunk, pool))
            chunk = []
            body.append(videos_section(sec['videos']))
        else:
            chunk.append(sec)
    body.append(auto_sections(chunk, pool))
    body.append(related_services(path))
    if closing:
        body.append(final_cta(closing[0], closing[1]))
    else:
        body.append(final_cta())
    write(path, 'page.html', body='\n'.join(body), preload=cfg['bg'], **meta(path))


# ---------------------------------------------------------------- suburb pages

TRANSPORT_ICONS = {
    'driving': '<path d="M5 11l1.5-4.5A2 2 0 0 1 8.4 5h7.2a2 2 0 0 1 1.9 1.5L19 11v6a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1v-1H8v1a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-6zm2.2-1h9.6l-1-3H8.2l-1 3zM7.5 14a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zm9 0a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z"/>',
    'bus': '<path d="M6 3h12a2 2 0 0 1 2 2v11a2 2 0 0 1-1 1.7V20a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1v-1H9v1a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1v-2.3A2 2 0 0 1 4 16V5a2 2 0 0 1 2-2zm0 3v5h12V6H6zm1.5 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3zm9 0a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z"/>',
    'taxi': '<path d="M9 3h6l1 2h1.6a2 2 0 0 1 1.9 1.5L21 11v6a1 1 0 0 1-1 1h-1a1 1 0 0 1-1-1v-1H6v1a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-6l1.5-4.5A2 2 0 0 1 6.4 5H8l1-2zM6.2 10h11.6l-1-3H7.2l-1 3z"/>',
    'cycling': '<path d="M15.5 5.5a2 2 0 1 0 0-4 2 2 0 0 0 0 4zM5 12a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 8.5a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7zm5.8-10.4L13.3 8l.8.8A6.9 6.9 0 0 0 19 11V9a5 5 0 0 1-3.6-1.5l-1.9-1.9a2 2 0 0 0-2.8 0L7.4 8.9a2 2 0 0 0 0 2.8L10 14v5h2v-6.2l-2.2-2.7zM19 12a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 8.5a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7z"/>',
}


def transport_icon(title):
    t = title.lower()
    key = 'bus' if ('bus' in t or 'shopper' in t) else 'taxi' if ('taxi' in t or 'rideshare' in t) else 'cycling' if 'cycl' in t else 'driving'
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{TRANSPORT_ICONS[key]}</svg>'


# the five services the live suburb pages list, skin checks first as the large card
SUBURB_SERVICES = [next(x for x in S.SERVICES if x['href'] == h) for h in ('/skin-checks/', '/ear-micro-suction/', '/iron-infusions/', '/preventive-health/', '/travel-medicine/')]


def build_suburb(path):
    slug = path.strip('/')
    sub = S.SUBURBS[slug]
    bs = blocks(path)
    _, sections = split_sections(bs)
    by = {(s['title'] if isinstance(s['title'], str) else s['title'][1]): s for s in sections}
    access = sections[0]
    services = next(s for s in sections if s['title'] == 'Our Services')
    getting = next(s for s in sections if str(s['title']).startswith('Getting here') or (isinstance(s['title'], tuple) and s['title'][1].startswith('Getting here')))
    getting_title = getting['title'] if isinstance(getting['title'], str) else getting['title'][1]
    lead_html, rest = lead_from(access['blocks'], 1)
    body = [page_hero(f'Doctors near {sub["name"]}', lead_html, sub['img'], [(f'{sub["name"]} doctors', None)],
                      chip=f'Patients from {sub["name"]} welcome', kicker=access['title'] if isinstance(access['title'], str) else access['title'][1]),
            quick_bar()]
    if rest:
        body.append(statement(rest, '/assets/img/reception.webp'))
    # services: the live copy plus links to each service page
    svc_lead = prose([b for b in services['blocks'] if b['t'] == 'p'])
    cards = ''.join(f'<li class="rel"><a href="{s["href"]}">{img(s["img"])}<span class="rel__body"><strong>{e(s["name"])}</strong><span>{e(s["summary"])}</span></span></a></li>' for s in SUBURB_SERVICES)
    body.append(f'''
<section class="ps svc-grid">
  <div class="wrap">
    <div class="ps-head">{h2(services['title'])}<div class="ps-head__lead">{svc_lead}</div></div>
    <ul class="svc-grid__list">{cards}</ul>
    <p class="ps-after"><a class="textlink" href="/our-services/">See all services</a></p>
  </div>
</section>''')
    body.append(doctors_rail())
    # getting here: each h3 transport option becomes a card
    lead, groups = h3_groups(getting['blocks'])
    tail = []
    if groups:
        last = groups[-1][1]
        # paragraphs after the last option that are not about it (journey planner, booking line) move below the cards
        while last and last[-1]['t'] == 'p' and re.search(r'Journey Planner|make an appointment', last[-1]['html'], re.I):
            tail.insert(0, last.pop())
    tail = [b for b in strip_booking(tail) if 'make an appointment' not in b['html'].lower()]
    cards = ''.join(f'<article class="tcard"><span class="tcard__icon">{transport_icon(t)}</span><h3>{e(t)}</h3>{prose(bl)}</article>' for t, bl in groups)
    origin = sub['name'].replace(' ', '+') + '+QLD'
    body.append(f'''
<section class="ps getting">
  <div class="wrap">
    <div class="getting__top">
      <div class="ps-head">{h2(getting_title)}<div class="ps-head__lead">{prose(lead)}</div>
        <a class="btn btn--plum" href="https://www.google.com/maps/dir/?api=1&amp;origin={origin}&amp;destination=127+Link+Road+Victoria+Point+QLD+4165" target="_blank" rel="noopener">Directions from {e(sub["name"])}</a>
      </div>
      <figure class="getting__map"><iframe title="Map of Sunstate Family Practice, 127 Link Road, Victoria Point" src="https://maps.google.com/maps?q=127%20Link%20Road%2C%20Victoria%20Point%20QLD%204165&amp;z=14&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></figure>
    </div>
    <div class="tcards">{cards}</div>
    {f'<div class="ps-after">{prose(tail)}</div>' if tail else ''}
  </div>
</section>''')
    body.append(final_cta(f'See a GP close to {sub["name"]}', 'To make an appointment call the clinic or Book Online.', image=sub['img']))
    write(path, 'page.html', body='\n'.join(body), preload=sub['img'], **meta(path))


# ---------------------------------------------------------------- doctors

def build_doctor(d):
    path = d['href']
    bs = blocks(path)
    bs = [b for b in bs if b['t'] != 'button']
    vids = [yt_id(b['src']) for b in bs if b['t'] == 'video' and yt_id(b.get('src'))]
    quals_block = next((b for b in bs if b['t'] in ('h4', 'p') and re.fullmatch(r'\(.*\)', re.sub(r'<[^>]+>', '', b.get('html', '')).strip())), None)
    bio = [b for b in bs if b is not quals_block and b['t'] not in ('video', 'h4')]
    quals = re.sub(r'<[^>]+>', '', quals_block['html']).strip('() ') if quals_block else d['quals']
    first = d['name'].split()[-1]
    video_html = f'<div class="doc-video">{video_card(vids[0], f"Meet {d["name"]}")}</div>' if vids else ''
    others = [x for x in S.DOCTORS if x is not d]
    note = f'<p class="doc-hero__note">{e(d["note"])}</p>' if d.get('note') else ''
    body = f'''
<section class="doc-hero">
  <div class="wrap doc-hero__grid">
    <div class="doc-hero__copy">
      {crumbs([('Doctors', '/our-team/'), (d['name'], None)])}
      <h1 class="phero__title">{e(d['name'])}</h1>
      {f'<p class="doc-hero__quals">{e(quals)}</p>' if quals else ''}
      {f'<p class="doc-hero__role">{e(d["role"])}</p>' if d.get('role') else ''}
      <p class="doc-hero__interest"><span>Interests</span>{e(d['interest'])}</p>
      {note}
      {book_buttons(book_label=f'Book with Dr {first}')}
    </div>
    <figure class="doc-hero__photo">{img(d['img'], d['name'], lazy=False)}</figure>
  </div>
</section>
<section class="ps doc-bio">
  <div class="wrap doc-bio__grid">
    <div class="doc-bio__text">
      <h2 class="h2">About {e(d['name'])}</h2>
      {prose(bio) if bio else '<p>' + e(d['name']) + ' enjoys all aspects of general practice at Sunstate Family Practice. Book online to see ' + e(d['name']) + '.</p>'}
    </div>
    <aside class="doc-bio__side">
      {video_html}
      <div class="doc-card">
        <h3>Book with {e(d['name'])}</h3>
        <p>Choose {e(d['name'])} when you book online with HotDoc, or call reception.</p>
        <a class="btn btn--green" href="{S.HOTDOC}" target="_blank" rel="noopener">Book online</a>
        <a class="textlink" href="{S.TEL}">Call {S.PHONE}</a>
      </div>
    </aside>
  </div>
</section>
{doctors_rail('Meet the rest of the team', 'Every doctor at Sunstate shares our passion for long term preventative health care.', others)}
{final_cta()}'''
    m = meta(path)
    write(path, 'page.html', body=body, current_section='/our-team/', **m)


def build_team():
    path = '/our-team/'
    bs = blocks(path)
    h2b = next(b for b in bs if b['t'] == 'h2')
    intro = next(b for b in bs if b['t'] == 'p')
    principal = S.DOCTORS[0]
    cards = ''.join(f'''<li class="mate"><a class="mate__link" href="{d["href"]}">{img(d["img"], "")}<div><h3>{e(d["name"])}</h3>{f'<p class="mate__quals">{e(d["quals"])}</p>' if d["quals"] else ''}<p>{e(d["interest"])}</p>{f'<p class="mate__note">{e(d["note"])}</p>' if d.get("note") else ''}</div></a></li>''' for d in S.DOCTORS)
    body = f'''
{page_hero('Doctors', prose([intro]), '/assets/img/team.webp', [('Doctors', None)], chip='A GP training practice since 2009')}
<section class="ps team-page">
  <div class="wrap">
    <div class="ps-head">
      <h2 class="h2">{e(clean_text(h2b['text']))}</h2>
      <div class="ps-head__lead"><p>Choose your doctor when you book online. Every GP at Sunstate shares our passion for long term preventative health care, and many trained here under Dr Ganter before returning to the practice.</p></div>
    </div>
    <ul class="team team--page">{cards}</ul>
  </div>
</section>
<section class="ps ps--band">
  <div class="ps-band__bg" aria-hidden="true">{img('/assets/img/clinic-hallway.webp')}</div>
  <div class="wrap"><div class="ps-band__card">
    <h2 class="h2">RACGP GP registrar training practice</h2>
    <p>Sunstate Family practice &amp; Skin Cancer Clinic is proud to be a GP training practice, supporting young doctors in the ways of being a good doctor.</p>
    <a class="textlink" href="/about-us/">About Sunstate</a>
  </div></div>
</section>
{final_cta()}'''
    write(path, 'page.html', body=body, preload='/assets/img/team.webp', **meta(path))


# ---------------------------------------------------------------- about

def caps_sections(bs):
    """The live About and booking pages use ALL-CAPS paragraphs as headings."""
    intro, secs, cur = [], [], None
    for b in bs:
        text = re.sub(r'<[^>]+>', '', b.get('html', '')).strip() if b['t'] == 'p' else ''
        if b['t'] == 'p' and text and text.upper() == text and len(text) < 60 and re.search('[A-Z]', text):
            title = text.title().replace('Racgp', 'RACGP').replace('Gp ', 'GP ').replace('&', '&')
            cur = {'title': title, 'blocks': []}
            secs.append(cur)
        elif cur is None:
            intro.append(b)
        else:
            cur['blocks'].append(b)
    return intro, secs


def build_about():
    path = '/about-us/'
    bs = [b for b in blocks(path) if b['t'] != 'img']
    intro, secs = caps_sections(bs)
    lead_html, rest = lead_from(intro, 1)
    suburbs_i = next(i for i, b in enumerate(rest) if b['t'] == 'p' and 'surrounding communities' in b['html'])
    before, area = rest[:suburbs_i], rest[suburbs_i:]
    pool = Pool(['/assets/img/clinic-hallway.webp', '/assets/img/visit-nurse.webp', '/assets/img/team.webp', '/assets/img/reception-question.webp', '/assets/img/hands.webp'])
    timeline = '''
<section class="ps timeline-sec ps--mist">
  <div class="wrap">
    <div class="ps-head"><h2 class="h2">Our story</h2><div class="ps-head__lead"><p>From one doctor to a team of GPs caring for multi-generational Redlands families.</p></div></div>
    <ol class="timeline">
      <li><span class="timeline__year">1993</span><div><h3>Dr Ganter graduates</h3><p>After graduating from the University of Queensland, Dr Andrew Ganter works at Greenslopes and Gold Coast Hospitals, then runs his own practice in Gladstone for 10 years.</p></div></li>
      <li><span class="timeline__year">2009</span><div><h3>Sunstate opens</h3><p>Dr Andrew and Helen Ganter establish Sunstate Family Practice on 1 September 2009, offering quality GP care to patients and a supportive practice for other GPs.</p></div></li>
      <li><span class="timeline__year">Today</span><div><h3>A training practice</h3><p>Many of the registrars Dr Ganter has supervised have returned to work at Sunstate as part of our growing team.</p></div></li>
      <li><span class="timeline__year">2024</span><div><h3>A renovated home</h3><p>In November 2024 we moved into a renovated building with more consulting rooms and treatment areas.</p></div></li>
    </ol>
  </div>
</section>'''
    area_list = next(b for b in area if b['t'] == 'ul')
    links = {'Thornlands': 'thornlands-doctors', 'Cleveland': 'cleveland-doctors', 'Redland Bay': 'redland-bay-doctors', 'Sheldon': 'sheldon-doctors',
             'Capalaba': 'capalaba-doctors', 'Alexandra Hills': 'alexandra-hills-doctors', 'Wellington Point': 'wellington-point-doctors'}
    chips = ''.join(f'<li><a href="/{links[re.sub("<[^>]+>", "", i).strip()]}/">{i}</a></li>' if re.sub('<[^>]+>', '', i).strip() in links else f'<li><span>{i}</span></li>' for i in area_list['items'])
    body = [page_hero('About Sunstate Family Practice', lead_html, '/assets/img/clinic-hallway.webp', [('About Us', None)], chip='AGPAL accredited'),
            quick_bar(),
            statement(before, '/assets/img/reception.webp', sat='/assets/img/visit-nurse.webp'),
            timeline,
            f'''
<section class="local" aria-labelledby="local-title">
  <div class="local__bg" aria-hidden="true">{img('/assets/img/coochiemudlo-aerial.webp')}</div>
  <div class="wrap local__inner">
    <div class="local__copy">
      <h2 id="local-title" class="h2 h2--light local__title">Caring for the Redlands</h2>
      {prose([b for b in area if b['t'] == 'p'])}
      <ul class="suburb-chips">{chips}</ul>
    </div>
    <figure class="local__sat">{img('/assets/img/jetty-victoria-point.webp', 'Victoria Point jetty at sunrise')}<figcaption><strong>From the mainland to the bay islands</strong><span class="suburbs">Patients also join us from Mount Cotton, Ormiston, Birkdale, Cornubia, Carbrook, and Coochiemudlo, Macleay, Karragarra, Lamb and Russell Islands.</span></figcaption></figure>
  </div>
</section>''']
    body.append(auto_sections(secs, pool, start_flip=True))
    body.append(doctors_rail())
    body.append(final_cta())
    write(path, 'page.html', body='\n'.join(body), preload='/assets/img/clinic-hallway.webp', **meta(path))


# ---------------------------------------------------------------- services hub

def build_services_hub():
    path = '/our-services/'
    bs = blocks(path)
    title = clean_text(next(b for b in bs if b['t'] == 'h2')['text'])
    intro = [b for b in bs if b['t'] == 'p'][0]
    items = next(b for b in bs if b['t'] == 'ul')['items']
    feature = ''.join(f'''<li class="hubcard"><a href="{s["href"]}"><figure>{img(s["img"])}</figure><div><h3>{e(s["name"])}</h3><p>{e(s["summary"])}</p><span class="hubcard__go" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M7 17L17 7M9 7h8v8" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg></span></div></a></li>''' for s in S.SERVICES)
    linkmap = {'Total Body Mapping (TBM)': '/total-body-mapping-victoria-point/', 'Skin cancer screening': '/skin-checks/', 'Iron Infusion': '/iron-infusions/',
               'Microscopic ear suction': '/ear-micro-suction/', 'Management of chronic disease': '/chronic-disease-management/', 'Preventative Health': '/preventive-health/',
               'Travel health & Immunisations': '/travel-medicine/', 'Skin cancer treatments': '/skin-checks/'}
    def chip(i):
        text = re.sub('<[^>]+>', '', i).strip()
        if text in linkmap:
            return f'<li><a href="{linkmap[text]}">{e(text)}</a></li>'
        return f'<li><span>{fix_links(i)}</span></li>'
    chips = ''.join(chip(i) for i in items)
    body = f'''
{page_hero('Our Services', prose([intro]), '/assets/img/hero-children.webp', [('Our Services', None)], chip='Care for every stage of life', kicker=title)}
{quick_bar()}
<section class="ps hub">
  <div class="wrap">
    <div class="ps-head"><h2 class="h2">Featured services</h2><div class="ps-head__lead"><p>Learn more about the services our patients ask about most.</p></div></div>
    <ul class="hub__grid">{feature}</ul>
  </div>
</section>
<section class="ps ps--mist allsvc">
  <div class="wrap allsvc__grid">
    <div>
      <h2 class="h2">{e(title)}</h2>
      <p>We provide all General Medical advice and treatment, including:</p>
      <figure class="allsvc__img reveal-img">{img('/assets/img/life-baby.webp')}</figure>
    </div>
    <ul class="allsvc__list">{chips}</ul>
  </div>
</section>
{doctors_rail()}
{final_cta('Book an appointment', 'To make an appointment call the clinic or Book Online.')}'''
    write(path, 'page.html', body=body, **meta(path))


# ---------------------------------------------------------------- FAQs

def build_faqs():
    path = '/faqs/'
    bs = blocks(path)
    ps = [b for b in bs if b['t'] == 'p']
    qas = [b for b in bs if b['t'] == 'qa' and b['a']]
    anchors = {'What are the practice fees?': 'bulkbill'}
    items = []
    for i, q in enumerate(qas):
        aid = anchors.get(clean_text(q['q']), '')
        items.append(qa_item(q, i == 0).replace('<details', f'<details data-faq{f" id={chr(34)}{aid}{chr(34)}" if aid else ""}', 1))
    extra = [
        {'t': 'qa', 'q': 'Do you have female doctors?', 'a': [p('Yes. Many of our GPs are women, including doctors with interests in women’s health, antenatal care and children’s health. You can choose your doctor when you book online.')]},
        {'t': 'qa', 'q': 'Do you bulk bill?', 'a': [p('Sunstate Family Practice is a private billing practice. Children 12 years and under are bulk billed for standard GP consultations between 8am and 5pm Monday to Friday. DVA Gold and White card holders are bulk billed for eligible conditions, and care plans, health assessments, home medication reviews, heart health assessments and immunisations are bulk billed. <a href="/fees/">See our fees</a>.')]},
    ]
    items.append(qa_item(extra[0]).replace('<details', '<details data-faq id="femaledoctors"', 1))
    items.insert(1, qa_item(extra[1]).replace('<details', '<details data-faq', 1))
    body = f'''
{page_hero('Frequently Asked Questions', prose(ps[:1]), '/assets/img/reception-question.webp', [('FAQs', None)], chip='Call us on (07) 3207 7744')}
<section class="faq ps faq--page">
  <div class="wrap faq__grid">
    <div class="faq__list">
      <div class="faq-search">
        <label for="faq-q" class="sr-only">Search the questions</label>
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 2a8 8 0 0 1 6.3 12.9l5.4 5.4-1.4 1.4-5.4-5.4A8 8 0 1 1 10 2zm0 2a6 6 0 1 0 0 12 6 6 0 0 0 0-12z"/></svg>
        <input id="faq-q" type="search" placeholder="Search the questions, for example fees or results" data-faq-search autocomplete="off">
      </div>
      <p class="faq-empty" data-faq-empty hidden>No questions match your search. Call us on <a href="{S.TEL}">{S.PHONE}</a> and we’ll help.</p>
      {''.join(items)}
      {prose(ps[1:])}
    </div>
    <div class="faq__media" aria-hidden="true">
      <img class="faq__img faq__img--a" src="/assets/img/reception-question.webp" alt="" loading="lazy">
      <img class="faq__img faq__img--b" src="/assets/img/life-older.webp" alt="" loading="lazy">
    </div>
  </div>
</section>
{final_cta()}'''
    jsonld = json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': clean_text(q['q']), 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub(r'<[^>]+>', '', prose(q['a']))}} for q in qas + extra]},
        ensure_ascii=False, indent=1)
    write(path, 'page.html', body=body, jsonld=jsonld, **meta(path))


# ---------------------------------------------------------------- news

def posts():
    out = []
    for x in CONTENT.values():
        if x['kind'] != 'post':
            continue
        slug = x['path'].strip('/')
        text = ' '.join(re.sub(r'<[^>]+>', '', b.get('html', '')) for b in x['blocks'] if b['t'] == 'p')
        excerpt = text[:170].rsplit(' ', 1)[0] + '…' if len(text) > 170 else text
        out.append({**x, 'slug': slug, 'topic': S.POST_TOPIC.get(slug, 'clinic'), 'excerpt': excerpt.strip(),
                    'date': datetime.fromisoformat(x['published'].replace('Z', '+00:00')) if x.get('published') else datetime(2020, 1, 1),
                    'h1': x.get('h1') or x['title'].split('|')[0].strip()})
    out.sort(key=lambda p_: p_['date'], reverse=True)
    return out


def date_label(d):
    return f'{d.strftime("%B")} {d.day}, {d.year}'


def news_card(post, lead=False):
    pic = post.get('featured') or '/assets/img/family-beach.webp'
    return f'''<article class="ncard{' ncard--lead' if lead else ''}" data-topic="{post['topic']}" data-search="{e((post['h1'] + ' ' + post['excerpt']).lower())}">
  <a href="{post['path']}">
    <figure>{img(pic)}</figure>
    <div class="ncard__body">
      <p class="ncard__meta"><span class="ncard__topic">{e(S.TOPICS[post['topic']])}</span><time datetime="{post['date'].date().isoformat()}">{date_label(post['date'])}</time></p>
      <h3>{e(post['h1'])}</h3>
      <p>{e(post['excerpt'])}</p>
    </div>
  </a>
</article>'''


def build_news(path='/news/', heading='Health News & Advice', crumb='News', only=None):
    ps_ = [x for x in posts() if (only is None or only(x))]
    lead, rest = ps_[0], ps_[1:]
    counts = {k: sum(1 for x in ps_ if x['topic'] == k) for k in S.TOPICS}
    chips = '<button type="button" class="chip is-active" data-topic-filter="all" aria-pressed="true">All <span>' + str(len(ps_)) + '</span></button>' + ''.join(
        f'<button type="button" class="chip" data-topic-filter="{k}" aria-pressed="false">{e(v)} <span>{counts[k]}</span></button>' for k, v in S.TOPICS.items() if counts[k])
    body = f'''
<section class="news-hero">
  <div class="wrap">
    {crumbs([(crumb, None)])}
    <h1 class="phero__title">{e(heading)}</h1>
    <p class="news-hero__lead">Health advice from our Victoria Point GPs, plus the latest clinic news.</p>
  </div>
  <div class="wrap news-hero__lead-card">{news_card(lead, lead=True)}</div>
</section>
<section class="ps news-list">
  <div class="wrap">
    <div class="news-tools">
      <div class="chips" role="group" aria-label="Filter by topic">{chips}</div>
      <div class="faq-search news-search">
        <label for="news-q" class="sr-only">Search articles</label>
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 2a8 8 0 0 1 6.3 12.9l5.4 5.4-1.4 1.4-5.4-5.4A8 8 0 1 1 10 2zm0 2a6 6 0 1 0 0 12 6 6 0 0 0 0-12z"/></svg>
        <input id="news-q" type="search" placeholder="Search articles" data-news-search autocomplete="off">
      </div>
    </div>
    <p class="faq-empty" data-news-empty hidden>No articles match. Try another topic or search term.</p>
    <div class="ngrid" data-news-grid>{''.join(news_card(x) for x in rest)}</div>
    <div class="news-more"><button class="btn btn--plum" type="button" data-news-more>Show more articles</button></div>
  </div>
</section>
{final_cta()}'''
    m = meta('/news/') if path == '/news/' else {'title': f'{heading} | Sunstate Family Practice', 'description': e('Clinic news and health advice from Sunstate Family Practice, Victoria Point.')}
    write(path, 'page.html', body=body, current_section='/news/', **m)


def build_post(post, all_posts):
    path = post['path']
    bs = [dict(b) for b in post['blocks']]
    # the live template repeats the title as a heading inside the post body
    if bs and bs[0]['t'] in ('h1', 'h2', 'h3') and clean_text(bs[0]['text']).lower() == post['h1'].lower():
        bs = bs[1:]
    feat = post.get('featured')
    same = [x for x in all_posts if x['topic'] == post['topic'] and x['path'] != path][:3]
    if len(same) < 3:
        same += [x for x in all_posts if x['path'] != path and x not in same][:3 - len(same)]
    body_html = prose(bs)
    if not body_html.strip():
        body_html = '<p>This announcement was shared as an image.</p>'
    body = f'''
<article class="article">
  <header class="article__hero">
    <div class="wrap article__hero-grid">
      <div class="article__head">
        {crumbs([('News', '/news/'), (S.TOPICS[post['topic']], None)])}
        <p class="ncard__meta"><span class="ncard__topic">{e(S.TOPICS[post['topic']])}</span><time datetime="{post['date'].date().isoformat()}">{date_label(post['date'])}</time></p>
        <h1 class="article__title">{e(post['h1'])}</h1>
      </div>
      {f'<figure class="article__feat">{img(feat, "", lazy=False)}</figure>' if feat else ''}
    </div>
  </header>
  <div class="wrap article__grid">
    <div class="article__body prose">{body_html}</div>
    <aside class="article__side">
      <div class="doc-card">
        <h3>Talk to a Sunstate GP</h3>
        <p>General information can’t replace advice about your own health. Book an appointment to discuss it with your doctor.</p>
        <a class="btn btn--green" href="{S.HOTDOC}" target="_blank" rel="noopener">Book online</a>
        <a class="textlink" href="{S.TEL}">Call {S.PHONE}</a>
      </div>
    </aside>
  </div>
</article>
<section class="ps ps--mist more-news">
  <div class="wrap">
    <div class="news__head"><h2 class="h2">Keep reading</h2><a class="textlink" href="/news/">All news</a></div>
    <div class="ngrid ngrid--3">{''.join(news_card(x) for x in same)}</div>
  </div>
</section>
{final_cta()}'''
    jsonld = json.dumps({'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': post['h1'], 'datePublished': post.get('published'),
                         'dateModified': post.get('modified'), 'author': {'@type': 'Organization', 'name': 'Sunstate Family Practice & Skin Cancer Clinic'}}, ensure_ascii=False)
    write(path, 'page.html', body=body, jsonld=jsonld, current_section='/news/', preload=feat, **meta(path))


# ---------------------------------------------------------------- contact, booking, careers, feedback, legal

def build_contact():
    path = '/contact-us/'
    bs = blocks(path)
    # Christmas 2020 holiday hours are out of date and are left out
    bs = [b for b in bs if not (b['t'] == 'ul' and re.search(r'December|January', ' '.join(b['items'])))]
    rights_i = next(i for i, b in enumerate(bs) if b['t'] == 'p' and 'Your Rights' in b['html'])
    head_ps = [b for b in bs[:rights_i] if b['t'] == 'p']
    rights = [b for b in bs[rights_i:] if b['t'] in ('p', 'ul')]
    h2_book = next(b for b in bs if b['t'] == 'h2')
    body = f'''
{page_hero('Contact Us', fix_links(h2_book['html']).replace('<strong>', '<p>').replace('</strong>', '</p>'), '/assets/img/reception-question.webp', [('Contact Us', None)], chip='Book online any time')}
{quick_bar()}
<section class="ps contact-cards">
  <div class="wrap cc-grid">
    <article class="cc"><h2>Call or visit</h2>{prose(head_ps)}</article>
    <article class="cc cc--plum"><h2>Consulting hours</h2>
      <table class="hours hours--light" data-hours>
        <tr data-days="1,2,3,4"><th scope="row">Mon to Thurs</th><td>7.30am to 6.30pm</td></tr>
        <tr data-days="5"><th scope="row">Fri</th><td>7.30am to 5pm</td></tr>
        <tr data-days="6"><th scope="row">Saturday</th><td>8am to 1pm</td></tr>
        <tr data-days="0"><th scope="row">Sundays</th><td>Opening soon</td></tr>
      </table>
      <p>All by Appointment. Some days, we will close earlier, depending on last patient, to support the well being of our staff.</p>
    </article>
    <figure class="cc cc--map"><iframe title="Map of Sunstate Family Practice, 127 Link Road, Victoria Point" src="https://maps.google.com/maps?q=127%20Link%20Road%2C%20Victoria%20Point%20QLD%204165&amp;z=15&amp;output=embed" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></figure>
  </div>
</section>
{contact_section('Send us a message')}
<section class="ps rights">
  <div class="wrap rights__grid">
    <figure class="rights__img reveal-img">{img('/assets/img/hands.webp')}</figure>
    <div class="rights__copy"><h2 class="h2">Your Rights</h2>{prose(rights).replace('<strong>Your Rights</strong><br>', '')}</div>
  </div>
</section>'''
    write(path, 'page.html', body=body, **meta(path))


def build_appointment():
    path = '/make-an-appointment/'
    bs = blocks(path)
    h2b = next(b for b in bs if b['t'] == 'h2')
    ps_ = [b for b in bs if b['t'] == 'p']
    links = next(b for b in bs if b['t'] == 'ul')
    after_links = bs[bs.index(links) + 1:]
    intro, secs = caps_sections(after_links)
    pool = Pool(['/assets/img/visit-frontdesk.webp', '/assets/img/clinic-hallway.webp', '/assets/img/life-older.webp', '/assets/img/reception.webp', '/assets/img/team.webp'])
    body = f'''
{page_hero(clean_text(h2b['text']), prose(ps_[:1]), '/assets/img/booking-phone.webp', [('Book an Appointment', None)], chip='New patients welcome')}
<section class="ps booking">
  <div class="wrap booking__grid">
    <div class="booking__widget">
      {prose(ps_[1:2])}
      <iframe title="Book an appointment with Sunstate Family Practice on HotDoc" src="{S.HOTDOC}" width="100%" height="800" loading="lazy" data-hotdoc-widget="iframe"></iframe>
    </div>
    <aside class="booking__side">
      <div class="doc-card">
        <h3>Useful links</h3>
        {prose([links])}
      </div>
      <div class="doc-card doc-card--plum">
        <h3>Prefer to call?</h3>
        <p>Our reception team can book you in on <a href="{S.TEL}">{S.PHONE}</a>.</p>
      </div>
    </aside>
  </div>
</section>
{auto_sections(secs, pool)}
{final_cta()}'''
    write(path, 'page.html', body=body, **meta(path))


def build_careers():
    path = '/careers/'
    bs = blocks(path)
    jobs, cur = [], None
    for b in bs:
        if b['t'] == 'h3':
            cur = {'title': clean_text(b['text']), 'blocks': []}
            jobs.append(cur)
        elif cur and b['t'] != 'img':
            cur['blocks'].append(b)
    cards = ''.join(f'''<article class="job"><div class="job__head"><span class="job__tag">Now hiring</span><h3>{e(j["title"].title() if j["title"].isupper() else j["title"])}</h3></div>
<details><summary>Read the role description</summary><div class="acc__body">{prose(j["blocks"])}</div></details>
<a class="btn btn--green" href="mailto:manager@sunstatefamilypractice.com.au?subject={e(j["title"])}%20application">Apply by email</a></article>''' for j in jobs)
    body = f'''
{page_hero('Careers', '<p>Join a supportive GP training practice in Victoria Point. View current opportunities for doctors, nurses and reception staff at Sunstate Family Practice.</p>', '/assets/img/careers-nurse.webp', [('Careers', None)], chip='RACGP training practice')}
<section class="ps jobs">
  <div class="wrap">
    <div class="ps-head"><h2 class="h2">Current opportunities</h2><div class="ps-head__lead"><p>Sunstate was established in 2009 and has grown into a thriving general practice. We are committed to nurturing a friendly, relaxed and professional team culture.</p></div></div>
    <div class="jobs__grid">{cards}</div>
  </div>
</section>
<section class="ps ps--band">
  <div class="ps-band__bg" aria-hidden="true">{img('/assets/img/team.webp')}</div>
  <div class="wrap"><div class="ps-band__card">
    <h2 class="h2">Don’t see your role?</h2>
    <p>We’re always happy to hear from doctors, nurses and administration staff who share our values. Send your CV to our Practice Manager.</p>
    <a class="btn btn--plum" href="mailto:manager@sunstatefamilypractice.com.au">Email the Practice Manager</a>
  </div></div>
</section>'''
    write(path, 'page.html', body=body, **meta(path))


def build_feedback():
    path = '/patient-feedback-survey/'
    bs = blocks(path)
    title = clean_text(next(b for b in bs if b['t'] == 'h2')['text'])
    intro = [b for b in bs if b['t'] == 'p'][0]
    # split by h3, and the improve section by h4
    parts, cur = [], None
    for b in bs:
        if b['t'] == 'h3':
            cur = {'title': clean_text(b['text']), 'blocks': []}
            parts.append(cur)
        elif cur:
            cur['blocks'].append(b)
    improve, well, welcome = parts[0], parts[1], parts[2]
    areas, a = [], None
    lead_imp = []
    for b in improve['blocks']:
        if b['t'] == 'h4':
            a = {'title': clean_text(b['text']), 'blocks': []}
            areas.append(a)
        elif a:
            a['blocks'].append(b)
        else:
            lead_imp.append(b)
    icons = ['/assets/img/doctors/chau-vu.webp', '/assets/img/visit-frontdesk.webp', '/assets/img/reception.webp']
    area_html = ''.join(f'<article class="fb-area"><figure>{img(icons[i % 3])}</figure><div><h4>{e(x["title"])}</h4>{prose(x["blocks"])}</div></article>' for i, x in enumerate(areas))
    body = f'''
{page_hero(title, prose([intro]), '/assets/img/reception-question.webp', [('About', '/about-us/'), ('Patient Feedback', None)], chip='Thank you for your feedback')}
<section class="ps fb-well">
  <div class="wrap fb-well__grid">
    <div><h2 class="h2">{e(well['title'])}</h2>{prose([b for b in well['blocks'] if b['t'] == 'p'][:1])}</div>
    <div class="fb-well__card">{prose([b for b in well['blocks'] if b['t'] == 'ul'], light=True)}{prose([b for b in well['blocks'] if b['t'] == 'p'][1:])}</div>
  </div>
</section>
<section class="ps ps--mist">
  <div class="wrap">
    <div class="ps-head"><h2 class="h2">{e(improve['title'])}</h2>{prose(lead_imp)}</div>
    <div class="fb-areas">{area_html}</div>
  </div>
</section>
{section_checklist(welcome['title'], prose([b for b in welcome['blocks'] if b['t'] == 'p'][:2]), prose([b for b in welcome['blocks'] if b['t'] == 'ul'], light=True), prose([b for b in welcome['blocks'] if b['t'] == 'p'][2:]), '/assets/img/hands.webp')}
{final_cta()}'''
    write(path, 'page.html', body=body, current_section='/about-us/', **meta(path))


def build_legal(path, h1):
    bs = blocks(path)
    if bs and bs[0]['t'] == 'h2':
        bs = bs[1:]
    body = f'''
<section class="news-hero legal-hero">
  <div class="wrap">
    {crumbs([(h1, None)])}
    <h1 class="phero__title">{e(h1)}</h1>
  </div>
</section>
<section class="ps legal">
  <div class="wrap"><div class="legal__body prose">{prose(bs)}</div></div>
</section>'''
    write(path, 'page.html', body=body, **meta(path))


# ---------------------------------------------------------------- run

def main():
    write('/', 'home.html', **HANDMADE['home'])
    write('/fees/', 'fees.html', **HANDMADE['fees'])
    for path, cfg in SERVICE_PAGES.items():
        build_service(path, cfg)
    for slug in S.SUBURBS:
        build_suburb(f'/{slug}/')
    for d in S.DOCTORS:
        build_doctor(d)
    build_team()
    build_about()
    build_services_hub()
    build_faqs()
    all_posts = posts()
    build_news()
    build_news('/category/clinic-news/', 'Clinic News', 'Clinic News')
    build_news('/category/doctors/', 'Doctors', 'Doctors', only=lambda x: x['topic'] == 'clinic')
    build_news('/category/uncategorised/', 'Uncategorised', 'Uncategorised')
    for post in all_posts:
        build_post(post, all_posts)
    build_contact()
    build_appointment()
    build_careers()
    build_feedback()
    build_legal('/terms/', 'Terms of Use')
    build_legal('/privacy-policy/', 'Website Privacy Policy')
    print(f'{len(WRITTEN)} pages written')


if __name__ == '__main__':
    main()
