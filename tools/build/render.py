"""HTML building blocks shared by every generated page.

Content comes from the live WordPress site (content/live.json) as a flat list of blocks.
These helpers turn those blocks into the editorial section layouts of the design system.
"""
import html
import itertools
import re

import sitedata as S

LIVE_RE = re.compile(r'https?://(?:www\.)?sunstatefamilypractice\.com\.au(?!/wp-content)(/[^"\s]*)?')
# Old URLs the live site redirects (kept in step with vercel.json)
REDIRECTS = {
    '/mole-mapping-victoria-point/': '/total-body-mapping-victoria-point/',
    '/total-body-photography-victoria-point/': '/total-body-mapping-victoria-point/',
    '/total-body-mapping/': '/total-body-mapping-victoria-point/',
    '/skin-cancer-checks-update/': '/skin-checks/',
}


def e(s):
    return html.escape(s or '', quote=True)


def local_href(href):
    """Point links at the new pages; keep uploads (PDFs, forms) on the live server."""
    if not href:
        return href
    href = href.replace('\u200b', '').replace('%e2%80%8b', '').replace('%E2%80%8B', '')
    m = LIVE_RE.match(href)
    if m:
        path = m.group(1) or '/'
        if not path.endswith('/') and '.' not in path.split('/')[-1] and '#' not in path and '?' not in path:
            path += '/'
        return REDIRECTS.get(path, path)
    if href.startswith('/'):
        return REDIRECTS.get(href, href)
    if href.startswith('tel:'):
        digits = re.sub(r'\D', '', href)
        if digits.endswith('732077744'):
            return S.TEL
    return href


def fix_links(h):
    def sub(m):
        href = local_href(m.group(1))
        ext = href.startswith('http') and 'sunstatefamilypractice.com.au/wp-content' not in href
        pdf = href.lower().endswith('.pdf')
        attrs = ' target="_blank" rel="noopener"' if (ext or pdf) else ''
        return f'<a href="{e(href)}"{attrs}>'
    h = re.sub(r'<a href="([^"]*)">', sub, h)
    return h.replace('​', '').replace('&nbsp;', ' ')


def clean_text(s):
    return (s or '').replace('​', '').strip()


def yt_id(url):
    m = re.search(r'(?:v=|youtu\.be/|embed/)([\w-]{11})', url or '')
    return m.group(1) if m else None


def img(src, alt='', cls='', lazy=True, w=None, h=None):
    dims = f' width="{w}" height="{h}"' if w and h else ''
    return f'<img src="{e(src)}" alt="{e(alt)}"{dims}{" loading=\"lazy\"" if lazy else ""}{f" class=\"{cls}\"" if cls else ""}>'


BOOKING_TEXT = re.compile(r'book|ph:|call|\(07\)', re.I)


def is_booking_button(b):
    href = b.get('href') or ''
    return 'make-an-appointment' in href or href.startswith('tel:') or 'hotdoc' in href


def prose(blocks, light=False):
    """Render a run of blocks as flowing text."""
    out = []
    tick = 'ticks ticks--light' if light else 'ticks'
    prev = None
    for b in blocks:
        t = b['t']
        # the live posts sometimes repeat an image straight after itself
        if t == 'img' and prev and prev['t'] == 'img' and prev.get('src') == b.get('src'):
            continue
        prev = b
        if t == 'p':
            h = fix_links(b['html'])
            if h.strip():
                out.append(f'<p>{h}</p>')
        elif t in ('h3', 'h4', 'h5', 'h6'):
            tag = 'h3' if t == 'h3' else 'h4'
            out.append(f'<{tag}>{fix_links(b["html"])}</{tag}>')
        elif t == 'ul':
            out.append(f'<ul class="{tick}">' + ''.join(f'<li>{fix_links(i)}</li>' for i in b['items']) + '</ul>')
        elif t == 'ol':
            out.append('<ol class="numlist">' + ''.join(f'<li>{fix_links(i)}</li>' for i in b['items']) + '</ol>')
        elif t == 'img':
            out.append(f'<figure class="prose-img">{img(b["src"], b.get("alt", ""))}</figure>')
        elif t == 'qa':
            out.append(qa_item(b))
        elif t == 'table':
            rows = b['rows']
            body = ''.join('<tr>' + ''.join(f'<td>{fix_links(c)}</td>' for c in r) + '</tr>' for r in rows)
            out.append(f'<div class="table-wrap"><table class="prose-table">{body}</table></div>')
        elif t == 'video':
            vid = yt_id(b.get('src'))
            if vid:
                out.append(video_card(vid, 'Watch the video'))
        elif t == 'button':
            if not is_booking_button(b):
                out.append(f'<p><a class="textlink" href="{e(local_href(b["href"]))}">{e(clean_text(b["text"]))}</a></p>')
        elif t == 'quote':
            out.append(f'<blockquote>{fix_links(b["html"])}</blockquote>')
    return '\n'.join(out)


def qa_item(b, open_=False):
    return (f'<details{" open" if open_ else ""}><summary>{e(clean_text(b["q"]))}</summary>'
            f'<div class="acc__body">{prose(b["a"])}</div></details>')


def video_card(vid, label):
    return (f'<button class="vcard" type="button" data-lightbox-open data-video-id="{vid}" aria-haspopup="dialog">'
            f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" loading="lazy">'
            f'<span class="vcard__play" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span>'
            f'<span class="vcard__label">{e(label)}</span></button>')


def crumbs(items):
    parts = ['<a href="/">Home</a>']
    for label, href in items:
        parts.append('<span aria-hidden="true">/</span>')
        parts.append(f'<a href="{href}">{e(label)}</a>' if href else f'<span aria-current="page">{e(label)}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + ''.join(parts) + '</nav>'


def book_buttons(light=True, book_label='Book online'):
    ghost = 'btn--glass' if light else 'btn--ghost'
    return (f'<div class="hero__actions"><a class="btn btn--green btn--lg" href="{S.HOTDOC}" target="_blank" rel="noopener">{e(book_label)}</a>'
            f'<a class="btn {ghost} btn--lg" href="{S.TEL}">Call {S.PHONE}</a></div>')


def page_hero(title, lead_html, bg, trail, chip=None, kicker=None, variant=''):
    """Full-bleed photo hero with breadcrumb, an optional pill, H1, lead and booking buttons.

    Nothing is layered over the photo, so the people in it stay visible."""
    pill = f'<p class="hero__welcome"><span class="pulse-dot" aria-hidden="true"></span>{e(chip)}</p>' if chip else ''
    k = f'<p class="phero__kicker">{e(kicker)}</p>' if kicker else ''
    return f'''
<section class="phero{' phero--right' if '/hero-' in bg else ''} {variant}">
  <div class="phero__bg" aria-hidden="true">{img(bg, "", lazy=False)}</div>
  <div class="wrap phero__inner">
    <div class="phero__copy">
      {crumbs(trail)}
      {pill}
      {k}
      <h1 class="phero__title">{e(title)}</h1>
      <div class="phero__lead">{lead_html}</div>
      {book_buttons()}
    </div>
  </div>
</section>'''


def quick_bar():
    return f'''
<div class="quick quick--page">
  <div class="wrap">
    <ul class="quick__bar">
      <li><a href="{S.HOTDOC}" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 2v2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2h-2V2h-2v2H9V2H7zm-2 8h14v10H5V10zm2 2v2h2v-2H7zm4 0v2h2v-2h-2z"/></svg><span><strong>Make an online booking</strong>No referral needed</span></a></li>
      <li><a href="{S.TEL}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1L6.6 10.8z"/></svg><span><strong>{S.PHONE}</strong>After hours: 134 100</span></a></li>
      <li><a href="https://maps.google.com/?cid=17006677294030981847" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 5.2 7 13 7 13s7-7.8 7-13a7 7 0 0 0-7-7zm0 9.5A2.5 2.5 0 1 1 12 6.5a2.5 2.5 0 0 1 0 5z"/></svg><span><strong>127 Link Road, Victoria Point</strong>Get directions</span></a></li>
      <li><a href="/fees/"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm1 15.9V19h-2v-1.1c-1.6-.3-2.9-1.3-3-2.9h2c.1.8.9 1.4 2 1.4 1.3 0 2-.6 2-1.3 0-.8-.6-1.1-2.3-1.5-2-.5-3.4-1.2-3.4-3 0-1.4 1.1-2.4 2.7-2.7V6.8h2v1.1c1.5.3 2.5 1.4 2.6 2.7h-2c-.1-.7-.7-1.2-1.7-1.2-1.1 0-1.7.5-1.7 1.2s.6 1 2.3 1.4c2 .5 3.4 1.3 3.4 3.1 0 1.5-1.2 2.5-2.9 2.8z"/></svg><span><strong>Fees &amp; bulk billing</strong>Know the cost before you book</span></a></li>
    </ul>
  </div>
</div>'''


# ---------------------------------------------------------------- sections

def h2(title, cls='h2'):
    """Section heading; title may be (kicker, heading) when the live page put a short line above it."""
    if isinstance(title, tuple):
        return f'<p class="ps-kicker">{e(title[0])}</p><h2 class="{cls}">{e(title[1])}</h2>'
    return f'<h2 class="{cls}">{e(title)}</h2>'


def split_sections(blocks):
    """Group blocks into (intro, [ {title, blocks} ]) using h2 (and stray h1) as section breaks."""
    intro, sections, cur = [], [], None
    for b in blocks:
        if b['t'] in ('h1', 'h2'):
            title = clean_text(b['text'])
            prev = cur['blocks'] if cur else intro
            if prev and prev[-1]['t'] in ('h3', 'h4') and len(prev[-1]['text']) < 60:
                title = (clean_text(prev.pop()['text']), title)
            cur = {'title': title, 'blocks': []}
            sections.append(cur)
        elif cur is None:
            intro.append(b)
        else:
            cur['blocks'].append(b)
    return intro, sections


def pull_images(blocks):
    imgs = [b for b in blocks if b['t'] == 'img']
    rest = [b for b in blocks if b['t'] != 'img']
    return imgs, rest


def strip_booking(blocks):
    return [b for b in blocks if not (b['t'] == 'button' and is_booking_button(b))]


def h3_groups(blocks):
    """Split blocks into [(lead_blocks), [(h3_text, [blocks])...]]."""
    lead, groups, cur = [], [], None
    for b in blocks:
        if b['t'] == 'h3':
            cur = (clean_text(b['text']), [])
            groups.append(cur)
        elif cur is None:
            lead.append(b)
        else:
            cur[1].append(b)
    return lead, groups


def numbered_steps(blocks):
    """Detect the live site's '1' / heading / text step pattern."""
    steps, cur = [], None
    for b in blocks:
        if b['t'] == 'p' and re.fullmatch(r'\d', re.sub(r'<[^>]+>', '', b['html']).strip()):
            cur = {'title': None, 'blocks': []}
            steps.append(cur)
        elif cur is not None:
            if b['t'] == 'h3' and cur['title'] is None:
                cur['title'] = clean_text(b['text'])
            else:
                cur['blocks'].append(b)
    return steps if len(steps) >= 2 else None


class Pool:
    """Cycles through a page's image pool so every section gets a photo."""

    def __init__(self, images):
        self.images = [i for i in images if i]
        self.it = itertools.cycle(self.images) if self.images else None

    def next(self):
        return next(self.it) if self.it else '/assets/img/family-beach.webp'


def section_split(title, body, image, sat, flip=False, tone=''):
    sat_html = f'<figure class="ps-sat reveal-img">{img(sat)}</figure>' if sat else ''
    return f'''
<section class="ps ps--split{" ps--flip" if flip else ""} {tone}">
  <div class="wrap ps-split">
    <div class="ps-split__media">
      <figure class="ps-img reveal-img">{img(image)}</figure>
      {sat_html}
    </div>
    <div class="ps-split__copy">
      {h2(title)}
      {body}
    </div>
  </div>
</section>'''


def section_band(title, body, image, right=False):
    return f'''
<section class="ps ps--band{" ps--band-right" if right else ""}">
  <div class="ps-band__bg" aria-hidden="true">{img(image)}</div>
  <div class="wrap">
    <div class="ps-band__card">
      {h2(title)}
      {body}
    </div>
  </div>
</section>'''


def section_checklist(title, lead_html, lists_html, after_html, image, tone=''):
    return f'''
<section class="ps ps--check {tone}">
  <div class="wrap ps-check">
    <div class="ps-check__copy">
      {h2(title)}
      {lead_html}
    </div>
    <div class="ps-check__media">
      <figure class="ps-check__img reveal-img">{img(image)}</figure>
      <div class="ps-check__card">{lists_html}</div>
    </div>
    {f'<div class="ps-check__after">{after_html}</div>' if after_html else ''}
  </div>
</section>'''


def section_cards(title, lead_html, cards, after_html='', tone='ps--mist', images=None):
    items = []
    for i, (h, body) in enumerate(cards):
        pic = ''
        if images and i < len(images) and images[i]:
            pic = f'<figure class="pcard__img">{img(images[i])}</figure>'
        items.append(f'<article class="pcard">{pic}<div class="pcard__body"><h3>{e(h)}</h3>{body}</div></article>')
    cols = 'pcards--2' if len(cards) in (2, 4) else ''
    return f'''
<section class="ps ps--cards {tone}">
  <div class="wrap">
    <div class="ps-head">
      {h2(title)}
      {f'<div class="ps-head__lead">{lead_html}</div>' if lead_html else ''}
    </div>
    <div class="pcards {cols}">{''.join(items)}</div>
    {f'<div class="ps-after">{after_html}</div>' if after_html else ''}
  </div>
</section>'''


def section_compare(title, lead_html, a, b, after_html='', image=None):
    (ha, ba), (hb, bb) = a, b
    return f'''
<section class="ps ps--compare">
  <div class="wrap">
    <div class="ps-head ps-head--center">
      {h2(title)}
      {f'<div class="ps-head__lead">{lead_html}</div>' if lead_html else ''}
    </div>
    <div class="pcompare">
      <article class="pcompare__card"><h3>{e(ha)}</h3>{ba}</article>
      {f'<figure class="pcompare__img reveal-img">{img(image)}</figure>' if image else ''}
      <article class="pcompare__card pcompare__card--plum"><h3>{e(hb)}</h3>{bb}</article>
    </div>
    {f'<div class="ps-after ps-after--center">{after_html}</div>' if after_html else ''}
  </div>
</section>'''


def section_steps(title, lead_html, steps, image=None, tone='ps--mist'):
    lis = ''.join(f'<li class="pstep"><span class="pstep__n">{i + 1}</span><div>{f"<h3>{e(s[0])}</h3>" if s[0] else ""}{s[1]}</div></li>'
                  for i, s in enumerate(steps))
    media = f'<figure class="psteps__img reveal-img">{img(image)}</figure>' if image else ''
    return f'''
<section class="ps ps--steps {tone}">
  <div class="wrap psteps">
    <div class="psteps__head">
      {h2(title)}
      {lead_html}
      {media}
    </div>
    <ol class="psteps__list">{lis}</ol>
  </div>
</section>'''


def section_faq(title, lead_html, qas_html, after_html, img_a, img_b, sid=''):
    return f'''
<section class="faq ps"{f' id="{sid}"' if sid else ''}>
  <div class="wrap faq__grid">
    <div class="faq__list">
      {h2(title)}
      {lead_html}
      {qas_html}
      {after_html}
    </div>
    <div class="faq__media" aria-hidden="true">
      <img class="faq__img faq__img--a" src="{img_a}" alt="" loading="lazy">
      <img class="faq__img faq__img--b" src="{img_b}" alt="" loading="lazy">
    </div>
  </div>
</section>'''


def auto_sections(sections, pool, start_flip=False):
    """Pick a layout for each h2 section from the shape of its content."""
    out = []
    flip = start_flip
    tones = itertools.cycle(['', 'ps--mist'])
    split_count = 0
    for sec in sections:
        title = sec['title']
        own_imgs, blocks = pull_images(strip_booking(sec['blocks']))
        image = own_imgs[0]['src'] if own_imgs else pool.next()
        lead, groups = h3_groups(blocks)
        qas = [b for b in blocks if b['t'] == 'qa']
        steps = numbered_steps(blocks)
        lists = [b for b in blocks if b['t'] == 'ul']
        if not blocks:
            continue
        if qas:
            others = [b for b in blocks if b['t'] != 'qa']
            out.append(section_faq(title, prose(others), ''.join(qa_item(q, i == 0) for i, q in enumerate(qas)), '', image, pool.next()))
        elif steps:
            pre = blocks[:next(i for i, b in enumerate(blocks) if b['t'] == 'p' and re.fullmatch(r'\d', re.sub(r'<[^>]+>', '', b['html']).strip()))]
            out.append(section_steps(title, prose(pre), [(s['title'], prose(s['blocks'])) for s in steps], image, tone=next(tones)))
        elif len(groups) == 2 and all(any(x['t'] == 'ul' for x in g[1]) for g in groups):
            out.append(section_compare(title, prose(lead), (groups[0][0], prose(groups[0][1])), (groups[1][0], prose(groups[1][1], light=True)), image=image))
        elif len(groups) >= 3 and all(len(g[1]) <= 3 for g in groups):
            out.append(section_cards(title, prose(lead), [(g[0], prose(g[1])) for g in groups], tone=next(tones)))
        elif len(groups) >= 2:
            cards = [(g[0], prose(g[1])) for g in groups]
            out.append(section_cards(title, prose(lead), cards, tone=next(tones)))
        elif lists and sum(len(l['items']) for l in lists) >= 4 and len([b for b in blocks if b['t'] == 'p']) <= 4:
            i = blocks.index(lists[0])
            before, after = blocks[:i], [b for b in blocks[i:] if b['t'] != 'ul']
            lists_html = ''.join(prose([l], light=True) for l in lists)
            out.append(section_checklist(title, prose(before), lists_html, prose(after), image, tone=next(tones)))
        else:
            split_count += 1
            if split_count % 3 == 0:
                out.append(section_band(title, prose(blocks), image, right=flip))
            else:
                sat = own_imgs[1]['src'] if len(own_imgs) > 1 else (pool.next() if split_count % 2 else None)
                out.append(section_split(title, prose(blocks), image, sat, flip=flip, tone=next(tones)))
            flip = not flip
    return '\n'.join(out)


# ---------------------------------------------------------------- shared closing sections

def related_services(current):
    cards = [s for s in S.SERVICES if s['href'] != current][:6]
    items = ''.join(f'''<li class="rel"><a href="{s["href"]}">{img(s["img"])}<span class="rel__body"><strong>{e(s["name"])}</strong><span>{e(s["summary"])}</span></span></a></li>''' for s in cards)
    return f'''
<section class="related" aria-labelledby="related-title">
  <div class="wrap">
    <div class="related__head">
      <h2 id="related-title" class="h2">More ways we can help</h2>
      <div class="rail-ctrl">
        <button class="rail-btn" type="button" data-rail-prev="related" aria-label="Previous service"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.4 7.4L14 6l-6 6 6 6 1.4-1.4L10.8 12z"/></svg></button>
        <button class="rail-btn" type="button" data-rail-next="related" aria-label="Next service"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8.6 16.6L10 18l6-6-6-6-1.4 1.4 4.6 4.6z"/></svg></button>
        <span class="rail-progress" aria-hidden="true"><span data-rail-bar="related"></span></span>
      </div>
    </div>
    <ul class="related__rail" data-rail="related">{items}</ul>
  </div>
</section>'''


def doctors_rail(title='Meet our doctors', lead='An experienced and caring team of doctors who put your health and wellbeing first.', doctors=None):
    docs = doctors or S.DOCTORS
    items = ''.join(f'''<li class="mate"><a class="mate__link" href="{d["href"]}">{img(d["img"])}<div><h3>{e(d["name"])}</h3><p>{e(d["interest"])}</p></div></a></li>''' for d in docs)
    return f'''
<section class="drail ps ps--mist" aria-labelledby="drail-title">
  <div class="wrap">
    <div class="related__head">
      <div>
        <h2 id="drail-title" class="h2">{e(title)}</h2>
        <p class="ps-head__lead">{e(lead)}</p>
      </div>
      <div class="rail-ctrl">
        <button class="rail-btn" type="button" data-rail-prev="docs" aria-label="Previous doctor"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15.4 7.4L14 6l-6 6 6 6 1.4-1.4L10.8 12z"/></svg></button>
        <button class="rail-btn" type="button" data-rail-next="docs" aria-label="Next doctor"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8.6 16.6L10 18l6-6-6-6-1.4 1.4 4.6 4.6z"/></svg></button>
        <span class="rail-progress" aria-hidden="true"><span data-rail-bar="docs"></span></span>
      </div>
    </div>
    <ul class="drail__rail" data-rail="docs">{items}</ul>
  </div>
</section>'''


def final_cta(title='Book your appointment', text='Book online or call our friendly reception team.', image='/assets/img/family-beach.webp'):
    return f'''
<section class="final" aria-labelledby="final-title">
  <div class="final__bg" aria-hidden="true">{img(image)}</div>
  <div class="wrap final__inner final__inner--solo">
    <div class="final__card">
      <h2 id="final-title" class="h2">{e(title)}</h2>
      <p>{e(text)}</p>
      <div class="final__actions">
        <a class="btn btn--green btn--lg" href="{S.HOTDOC}" target="_blank" rel="noopener">Book online</a>
        <a class="btn btn--ghost btn--lg" href="{S.TEL}">Call {S.PHONE}</a>
      </div>
      <div class="final__info">
        <div>
          <h3>Consulting hours</h3>
          <table class="hours" data-hours>
            <tr data-days="1,2,3,4"><th scope="row">Mon to Thurs</th><td>7.30am to 6.30pm</td></tr>
            <tr data-days="5"><th scope="row">Fri</th><td>7.30am to 5pm</td></tr>
            <tr data-days="6"><th scope="row">Saturday</th><td>8am to 1pm</td></tr>
            <tr data-days="0"><th scope="row">Sundays</th><td>Opening soon</td></tr>
          </table>
          <p class="small">All by Appointment.</p>
        </div>
        <div>
          <h3>Location</h3>
          <p>127 Link Road<br>Victoria Point, QLD 4165</p>
          <a class="textlink" href="https://maps.google.com/?cid=17006677294030981847" target="_blank" rel="noopener">Get directions</a>
        </div>
      </div>
    </div>
  </div>
</section>'''


def contact_form():
    opts = ['Search Engines (Google, Bing, Yahoo)', 'Social media (Facebook, Instagram, TikTok)', 'From a friend or family member',
            'From another doctor', 'Newsletter', 'Text message', 'Influencer', 'Radio (incl. podcasts)', 'AI chats (ChatGPT, Gemini, Perplexity)', 'Other']
    options = ''.join(f'<option>{e(o)}</option>' for o in opts)
    return f'''
    <form class="contact__form" data-contact-form data-endpoint="" novalidate>
      <div class="field-row">
        <div class="field"><label for="cf-first">First name</label><input id="cf-first" name="first_name" type="text" autocomplete="given-name" required><p class="field__error" id="cf-first-err">Enter your first name.</p></div>
        <div class="field"><label for="cf-last">Last name</label><input id="cf-last" name="last_name" type="text" autocomplete="family-name" required><p class="field__error" id="cf-last-err">Enter your last name.</p></div>
      </div>
      <div class="field-row">
        <div class="field"><label for="cf-email">Email</label><input id="cf-email" name="email" type="email" autocomplete="email" required><p class="field__error" id="cf-email-err">Enter an email address like name@example.com.</p></div>
        <div class="field"><label for="cf-phone">Phone</label><input id="cf-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required><p class="field__error" id="cf-phone-err">Enter a phone number we can call you on.</p></div>
      </div>
      <div class="field"><label for="cf-message">Message</label><textarea id="cf-message" name="message" rows="5" required></textarea><p class="field__error" id="cf-message-err">Enter your question or message.</p></div>
      <div class="field"><label for="cf-source">How did you hear about us?</label><select id="cf-source" name="heard_about_us" required><option value="" selected disabled>Choose one</option>{options}</select><p class="field__error" id="cf-source-err">Choose how you heard about us.</p></div>
      <input class="hp" type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">
      <p class="contact__privacy">By sending this form you agree to us using your details to respond to your enquiry, in line with our <a href="https://sunstatefamilypractice.com.au/wp-content/uploads/2025/08/Privacy-Policy-incl-AI.pdf" target="_blank" rel="noopener">privacy policy</a>.</p>
      <button class="btn btn--green btn--lg contact__submit" type="submit">Send message</button>
      <div class="contact__status" role="status" aria-live="polite" data-form-status></div>
    </form>'''


def contact_section(title='Have a question? Send us a message'):
    return f'''
<section class="contact" id="contact" aria-labelledby="contact-title">
  <div class="wrap contact__grid">
    <div class="contact__intro">
      <h2 id="contact-title" class="h2 h2--light">{e(title)}</h2>
      <p>Not ready to book, or just want to ask something first? Our reception team will get back to you during opening hours.</p>
      <ul class="contact__details">
        <li><span>Phone</span><a href="{S.TEL}">{S.PHONE}</a></li>
        <li><span>Email</span><a href="mailto:reception@sunstatefamilypractice.com.au">reception@sunstatefamilypractice.com.au</a></li>
        <li><span>Visit</span>127 Link Road, Victoria Point QLD 4165</li>
      </ul>
      <p class="contact__urgent">This form is for general enquiries only. Please don’t include detailed medical information. For medical advice, book an appointment. In an emergency, call 000.</p>
    </div>
    {contact_form()}
  </div>
</section>'''
