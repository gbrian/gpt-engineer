
SINGLE_LINE_MENTION_START = "@codx:"
MULTI_LINE_MENTION_START = ">> @codx"
MULTI_LINE_MENTION_END = "<< @codx"

class Mention():
    mention: str = None
    start_line: int = None
    end_line: int = None

    def __init__(self, mention, start_line, end_line):
        self.mention = mention
        self.start_line = start_line
        self.end_line = end_line

def extract_mentions(content):
    content_lines = content.split("\n")
    mentions = []
    start_line = None
    end_line = None
    mention = None

    def add_mention(_mention, _start, _end):
        mentions.append(Mention(_mention.strip(), _start, _end))

    for ix, line in enumerate(content_lines):
        if line.strip().startswith(SINGLE_LINE_MENTION_START):
            start_line = ix
            mention = line.replace(SINGLE_LINE_MENTION_START, "")
            add_mention(mention, start_line, None)
            mention = None
            start_line = None
            end_line = None

        elif line.strip().startswith(MULTI_LINE_MENTION_START):
            mention = []
    
        elif line.strip().startswith(MULTI_LINE_MENTION_END):
            add_mention("\n".join(mention), start_line, end_line)
            mention = None
            start_line = None
            end_line = None

        elif mention is not None:
            if not start_line:
                start_line = ix
            end_line = ix
            mention.append(line)
    return mentions