from lxml import etree
from classes import Work


def parse_mei_xml(xml_path):
    try:
        tree = etree.parse(xml_path)
    except etree.XMLSyntaxError as e:
        return None
    root = tree.getroot()

    ns = {"mei": "http://www.music-encoding.org/ns/mei"}

    title_elem = root.xpath(".//mei:titleStmt/mei:title[1]", namespaces=ns)
    if not title_elem or not title_elem[0].text:
        return None
    work_title = title_elem[0].text.strip()

    term_elems = root.xpath("./mei:meiHead/mei:workList/mei:work/mei:classification/mei:termList/mei:term", namespaces=ns)
    genres = [t.text.strip() for t in term_elems if t.text and t.text.strip()]
    if not genres:
        return None

    creation_elems = root.xpath("./mei:meiHead/mei:workList/mei:work/mei:creation/mei:date[1]", namespaces=ns)
    if not creation_elems:
        return None
    creation_elem = creation_elems[0]

    isodate_attr = creation_elem.get("isodate")
    not_before_attr = creation_elem.get("notbefore")
    creation_year_str = None

    if isodate_attr:
        creation_year_str = isodate_attr
    elif not_before_attr:
        creation_year_str = not_before_attr
    if not creation_year_str:
        return None
    try:
        if '-' in creation_year_str:
            creation_year = int(creation_year_str.split('-')[0])
        else:
            creation_year = int(creation_year_str)
    except ValueError:
        return None

    if not (1800 <= creation_year <= 2000):
        return None

    return Work(
        work_id=-1,
        composer_id=-1,
        title=work_title,
        genre=','.join(genres),
        creation_year=creation_year
    )


def data_clean():
    works = []
    for composer in ['Carl Nielsen', 'Frederick Delius']:
        composer_txt_filename = f'{composer}.txt'
        try:
            with open(composer_txt_filename, 'r', encoding='utf-8') as f:
                works_data = [eval(line.strip()) for line in f if line.strip()]
        except FileNotFoundError:
            continue
        total_count = len(works_data)
        count_after_clean = 0
        for work_data in works_data:
            xml_path = work_data.get('XML Filename')
            detail_url = work_data.get('Detail Page Link')
            if not xml_path:
                continue
            work = parse_mei_xml(xml_path)
            if not work:
                continue
            work.composer = composer
            work.detail_url = detail_url
            work.decade = f'{work.creation_year // 10}0s'
            works.append(work)
            count_after_clean += 1
        print(f'Before clean, Works of {composer}: {total_count}')
        print(f'After clean, Works of {composer}: {count_after_clean}')
    genres = set()
    for work in works:
        genres.update(work.genre.split(','))

    return works, genres


if __name__ == '__main__':
    works, genres = data_clean()
    # for work in works:
    #     print(work.to_dict())
    # print(genres)
    # print(len(genres))
