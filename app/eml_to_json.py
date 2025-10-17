import sys, os, json, re
from pathlib import Path
from email import policy
from email.parser import BytesParser
from html import unescape

# simple eml file to JSON converter from online sources but adjusted for my use case ;)
# extracts subject, sender, body (text preferred), links, raw headers as JSON

URL_RE = re.compile(r"https?://[^\s>\)\"]+", re.I)

def extract_body(msg):
    if msg.is_multipart():
        # prefer text/plain
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == 'text/plain':
                return part.get_content().strip()
        # fallback to first text/html
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == 'text/html':
                return strip_html(part.get_content())
        return msg.get_body(preferencelist=('plain', 'html')).get_content().strip()
    else:
        ctype = msg.get_content_type()
        if ctype == 'text/plain':
            return msg.get_content().strip()
        elif ctype == 'text/html':
            return strip_html(msg.get_content())
        else:
            return msg.get_content().strip()

def strip_html(html):
    # very simple HTML -> text
    txt = re.sub(r"<\s*br\s*/?>", "\n", html, flags=re.I)
    txt = re.sub(r"<\s*/p\s*>", "\n", txt, flags=re.I)
    txt = re.sub(r"<[^>]+>", "", txt)
    return unescape(txt)

def extract_links(text):
    return list(set(URL_RE.findall(text)))

def eml_to_json(eml_path: Path) -> dict:
    with open(eml_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    subject = msg.get('subject', '') or ''
    sender = msg.get('from', '') or ''
    body = extract_body(msg)

    links = extract_links(body)
    return {
        "subject": subject,
        "sender": sender,
        "body": body,
        "links": links,
        "raw_headers": str(msg.items())
    }

def convert_file(input_path: Path, output_path: Path):
    data = eml_to_json(input_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {output_path}")

def convert_folder(input_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    for eml in input_dir.glob('*.eml'):
        out = output_dir / (eml.stem + '.json')
        convert_file(eml, out)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage:\n  python -m app.eml_to_json input.eml output.json\n  python -m app.eml_to_json input_dir/ output_dir/")
        sys.exit(1)
    inp = Path(sys.argv[1])
    outp = Path(sys.argv[2])
    if inp.is_file():
        convert_file(inp, outp if outp.suffix else outp.with_suffix('.json'))
    elif inp.is_dir():
        convert_folder(inp, outp)
    else:
        print("Input path not found:", inp)
        sys.exit(2)