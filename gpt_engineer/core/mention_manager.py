
SINGLE_LINE_MENTION_START = "@codx:"
MULTI_LINE_MENTION_START = ">> @codx"
MULTI_LINE_MENTION_END = "<< @codx"

class Mention():
    mention: str = None
    start_line: int = None
    end_line: int = None
    respone: str = None

    def __init__(self, mention, start_line, end_line=None, respone=None):
        self.mention = mention
        self.start_line = start_line
        self.end_line = end_line
        self.respone = respone

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
            start_line = ix
    
        elif line.strip().startswith(MULTI_LINE_MENTION_END):
            end_line = ix
            add_mention("\n".join(mention), start_line, end_line)
            mention = None
            start_line = None
            end_line = None

        elif mention is not None:
            mention.append(line)
    return mentions

def replace_mentions(content, mentions):
    content_lines = content.split("\n")
    new_content = []
    last_index = 0
    for mention in mentions:
        new_content = new_content + content_lines[last_index:mention.start_line]
        new_content = new_content + mention.respone.split("\n")
        last_index = (mention.end_line if mention.end_line else mention.start_line) + 1
    if last_index < len(content) - 1:
        new_content = new_content + content_lines[last_index:]
    return "\n".join(new_content)